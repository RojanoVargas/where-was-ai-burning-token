import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool
from episode_summaries import EPISODE_SUMMARIES
import config
from model_config import chat_model_kwargs, embedding_model_kwargs

load_dotenv()

import re

rag_llm = ChatOpenAI(
    **chat_model_kwargs(),
    temperature=0,
)

# Supabase client (same project, uses documents table for vectors)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = create_client(supabase_url, supabase_key)

# Embeddings
embeddings = OpenAIEmbeddings(**embedding_model_kwargs())

# Prepare documents from your 3 episode summaries
docs = [
    Document(
        page_content=ep["summary"],
        metadata={"episode_id": ep["episode_id"], "title": ep["title"]},
    )
    for ep in EPISODE_SUMMARIES
]

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
)
splits = text_splitter.split_documents(docs)

# Create Supabase vector store
vector_store = SupabaseVectorStore(
    client=supabase_client,
    embedding=embeddings,
    table_name="documents",
    query_name="match_documents",
)

# Run this once to ingest (comment out after first run):
# vector_store.add_documents(splits)

@tool(parse_docstring=True)
def search_episodes(query: str, k: int = 2) -> str:
    """Search episode summaries by meaning and return relevant chunks.

    Args:
        query: Natural language question about what happens in an episode.
    k: Number of chunks to retrieve (default 2).

    Returns:
        Text with episode titles, IDs, and matching summary snippets.
        Only episodes up to the current episode (no spoilers) are included.
    """
    ep_match = re.search(r'episode\s*([0-9]+)|ep\s*([0-9]+)', query, re.IGNORECASE)
    
    if ep_match:
        target_ep = int(ep_match.group(1) or ep_match.group(2))
        if target_ep > config.CURRENT_EPISODE_ID:
            return f"Cannot retrieve Episode {target_ep} because your current progress is Episode {config.CURRENT_EPISODE_ID}. This would contain spoilers."
        results = vector_store.similarity_search(query, k=k, filter={"episode_id": target_ep})
    else:
        allowed_eps = [ep for ep in range(1, config.CURRENT_EPISODE_ID + 1)]
        results = []
        for ep in allowed_eps:
            results.extend(vector_store.similarity_search(query, k=k, filter={"episode_id": ep}))
    
    lines = []
    for doc in results[:k]:
        ep_id = doc.metadata.get("episode_id", "?")
        title = doc.metadata.get("title", "Unknown episode")
        lines.append(f"Episode {ep_id}: {title}\n{doc.page_content}\n")
    return "\n---\n".join(lines)

RAG_TOOLS = [search_episodes]
