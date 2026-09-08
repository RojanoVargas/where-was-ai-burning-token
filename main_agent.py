import config
from dotenv import load_dotenv
from langchain.agents import create_agent
from sql_agent import SQL_TOOLS, sql_llm
from rag_agent import RAG_TOOLS, search_episodes
from model_config import AI_PROVIDER

load_dotenv()

main_llm = sql_llm  # reuse the same LLM defined in sql_agent.py

tools = SQL_TOOLS + RAG_TOOLS

def get_system_prompt(current_episode_id: int = None) -> str:
    ep_id = current_episode_id if current_episode_id is not None else config.CURRENT_EPISODE_ID
    return f"""
You are an agent that answers questions about Sex and the City using:
- A SQL database with tables: characters, episodes, appearances
- A vector store with episode summaries (what happens in each episode)

Current user progress:
- Only episodes with id <= {ep_id} are known to the user.
- You MUST NOT reveal or imply any information from episodes with id > {ep_id}.
- If a question would require knowing about later episodes (e.g., characters that first appear later, plot after episode {ep_id}), say you cannot answer without spoiling and stop.

Rules:
- For structured facts (counts, which characters, which episodes, who appears where), use the SQL tools.
  - When querying episodes or appearances, restrict to episodes.id <= {ep_id} if needed.
- For plot/summary questions ("What happens in episode X?", "How do they meet?", "Summarize episode 2"), use search_episodes.
- Always double-check SQL queries with sql_db_query_checker before executing.
- Use the minimum number of tools needed. After a tool returns the requested information, answer the user directly and do not call that tool again.
- Do not make up details; rely only on the database and retrieved summaries.
- If you are unsure whether something is a spoiler, assume it is and refuse to answer.

Output formatting:
- NEVER reveal raw SQL code, queries (such as SELECT ..., WHERE ...), database schemas, or internal tool names to the user.
- Always reply in clean, conversational, natural language with friendly formatting (bullet points, bold text).

Always start by deciding whether the question is about:
- Structure/metadata → SQL
- Plot/summary → search_episodes
"""

_agents = {}

def get_agent(current_episode_id: int = None):
    ep_id = current_episode_id if current_episode_id is not None else config.CURRENT_EPISODE_ID
    if ep_id not in _agents:
        _agents[ep_id] = create_agent(
            main_llm,
            tools,
            system_prompt=get_system_prompt(ep_id),
        )
    return _agents[ep_id]

# Default agent instance
agent = get_agent(config.CURRENT_EPISODE_ID)

def get_response_stream(messages, current_episode_id: int = None):
    if current_episode_id is not None:
        config.CURRENT_EPISODE_ID = current_episode_id
    active_agent = get_agent(config.CURRENT_EPISODE_ID)

    latest_prompt = messages[-1].get("content", "") if messages else ""
    is_plot_question = any(
        marker in latest_prompt.lower()
        for marker in ("what happens", "summarize", "summary", "plot", "episode ")
    )

    # Keep the primary episode experience deterministic: retrieve the allowed
    # episode context once, then ask Nebius to write the answer without another
    # tool round. This also makes the RAG evidence easy to demonstrate.
    if AI_PROVIDER == "nebius" and is_plot_question:
        retrieved = search_episodes.invoke({"query": latest_prompt, "k": 3})
        response = main_llm.invoke(
            [
                {
                    "role": "system",
                    "content": get_system_prompt(config.CURRENT_EPISODE_ID)
                    + f"\n\nRetrieved episode context:\n{retrieved}",
                },
                *messages,
            ]
        )
        content = response.content
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        yield "token", content
        return

    # Nebius tool-calling responses are reliable in regular completions but
    # can stall when LangGraph streams the second model turn after a tool.
    # Invoke the agent normally for Nebius, then yield the completed answer so
    # the Streamlit UI keeps its existing response interface.
    if AI_PROVIDER == "nebius":
        result = active_agent.invoke(
            {"messages": messages},
            config={"recursion_limit": 8},
        )
        final_message = result["messages"][-1]
        content = final_message.content
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        yield "token", content
        return

    stream = active_agent.stream_events(
        {"messages": messages},
        version="v3",
    )

    for kind, item in stream.interleave("messages", "tool_calls"):
        if kind == "messages":
            # Only stream tokens from the assistant model node, not intermediate tool messages
            if getattr(item, "node", None) == "model":
                for token in item.text:
                    yield "token", token
        elif kind == "tool_calls":
            yield "tool_start", (item.tool_name, item.input)
            for delta in item.output_deltas:
                yield "tool_delta", delta
            yield "tool_end", item.output

if __name__ == "__main__":
    question = "What happens in episode 3?"

    for event_type, data in get_response_stream([{"role": "user", "content": question}]):
        if event_type == "token":
            print(data, end="", flush=True)
        elif event_type == "tool_start":
            print(f"\nTool call: {data[0]}({data[1]})")
        elif event_type == "tool_delta":
            print(data, end="", flush=True)
        elif event_type == "tool_end":
            print(f"\nTool result: {data}")
