import streamlit as st
from config import CURRENT_EPISODE_ID
from main_agent import get_response_stream

# Known available episodes in the database
AVAILABLE_EPISODES = {
    1: "Episode 1: Pilot",
    2: "Episode 2: Models and Mortals",
    3: "Episode 3: Bay of Married Pigs",
}

EPISODE_IMAGES = {
    1: (
        "https://pixel.disco.nowtv.com/uuid/26289333-e9a3-3631-85b1-ccc6efe96831/LAND_16_9?language=en-GB&proposition=NOWOTT&version=09d81fd5-6e28-358e-975d-e632dd43d838",
        "Episode 1 · Carrie meets Mr. Big",
    ),
    2: (
        "https://is1-ssl.mzstatic.com/image/thumb/xnuq_-wVOphziIDabn-uvw/1200x675.jpg",
        "Episode 2 · Models and Mortals",
    ),
    3: (
        "https://is1-ssl.mzstatic.com/image/thumb/8-ehCbrX_xkFwiFKI2ijaw/1200x675.jpg",
        "Episode 3 · Bay of Married Pigs",
    ),
}

# Page Configuration
st.set_page_config(
    page_title="Where Was AI? - Sex and the City Guide",
    page_icon="🍸",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');

    :root {
        --ink: #30202b;
        --muted: #816875;
        --rose: #d45178;
        --rose-dark: #9d3157;
        --champagne: #f8e8d1;
        --plum: #4a2942;
    }

    .stApp {
        background: radial-gradient(circle at 92% 4%, rgba(248, 232, 209, 0.85), transparent 23rem),
            linear-gradient(135deg, #fffaf8 0%, #fff5f6 48%, #fdf0f3 100%);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4a2942 0%, #321e32 100%);
        border-right: 1px solid rgba(248, 232, 209, 0.25);
    }

    [data-testid="stSidebar"] * { color: #fff8f5; }
    [data-testid="stSidebar"] hr { border-color: rgba(248, 232, 209, 0.25); }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
        color: #f8e8d1 !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #f7e6ec !important;
        border-color: #d989a2 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"] * {
        background: #f7e6ec !important;
        color: #30202b !important;
        -webkit-text-fill-color: #30202b !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] {
        position: relative;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        opacity: 0 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"]::after {
        color: #4a2942;
        content: "⌄";
        font-family: Georgia, serif;
        font-size: 1.45rem;
        font-weight: 700;
        line-height: 1;
        pointer-events: none;
        position: absolute;
        right: 0.8rem;
        top: 50%;
        transform: translateY(-56%);
        z-index: 5;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 0.45rem;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255, 248, 245, 0.1);
        border: 1px solid rgba(248, 232, 209, 0.25);
        border-radius: 0.55rem;
        padding: 0.4rem 0.55rem;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #d45178;
        border-color: #f8e8d1;
    }

    [data-testid="stSidebar"] [data-baseweb="popover"] [role="option"] {
        background: #fff8f5 !important;
        color: #30202b !important;
    }

    [data-testid="stSidebar"] [data-baseweb="popover"] [role="option"]:hover,
    [data-testid="stSidebar"] [data-baseweb="popover"] [aria-selected="true"] {
        background: #f7e6ec !important;
        color: #9d3157 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(248, 232, 209, 0.28);
        color: #fff8f5;
        text-align: left;
        transition: all 160ms ease;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--rose);
        border-color: var(--rose);
        color: white;
        transform: translateX(3px);
    }

    .main-header {
        color: var(--plum);
        font-family: 'Playfair Display', Georgia, serif;
        font-size: clamp(2.7rem, 6vw, 4.4rem);
        font-weight: 800;
        letter-spacing: -0.055em;
        line-height: 1;
        margin: 1.8rem 0 0.45rem;
        text-shadow: 2px 2px 0 rgba(248, 232, 209, 0.75);
    }

    .sub-header {
        color: var(--muted);
        font-size: 1.04rem;
        line-height: 1.6;
        margin-bottom: 1.35rem;
        max-width: 42rem;
    }

    .badge-pill {
        display: inline-block;
        padding: 0.5rem 0.95rem;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.72);
        color: var(--rose-dark);
        margin-bottom: 1.8rem;
        border: 1px solid rgba(212, 81, 120, 0.26);
        box-shadow: 0 5px 20px rgba(157, 49, 87, 0.07);
    }

    [data-testid="stChatMessage"] {
        border: 0;
        border-radius: 1.1rem;
        margin: 0.85rem 0;
        padding: 0.8rem 1rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: rgba(255, 255, 255, 0.66);
        border: 1px solid rgba(212, 81, 120, 0.14);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: rgba(248, 232, 209, 0.34);
        border-left: 3px solid var(--rose);
    }

    .archive-status {
        color: var(--rose-dark);
        font-size: 0.88rem;
        font-style: italic;
        padding: 0.35rem 0;
    }

    [data-testid="stChatInput"] {
        background: transparent;
        border: 1px solid rgba(157, 49, 87, 0.25);
        border-radius: 25px;
        box-shadow: 0 8px 28px rgba(74, 41, 66, 0.1);
    }

    [data-testid="stChatInput"] > div {
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] > div:focus-within {
        border-color: rgb(255, 75, 75);
        border-radius: 25px;
    }

    [data-testid="stChatInput"] textarea { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif; color: var(--plum); }

    /* Keep episode artwork clean: hide Streamlit's hover expand toolbar. */
    [data-testid="stElementToolbar"],
    [data-testid="stElementToolbar"] *,
    [title="View fullscreen"],
    [aria-label="View fullscreen"] {
        display: none !important;
    }

    /* Replace Streamlit's running-man execution icon with a cocktail. */
    [data-testid="stStatusWidgetRunningIcon"] svg {
        display: none !important;
    }

    [data-testid="stStatusWidgetRunningIcon"]::before {
        content: "🍸";
        font-size: 1.25rem;
        line-height: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_episode" not in st.session_state:
    st.session_state.current_episode = CURRENT_EPISODE_ID

# Sidebar Controls & Configuration
with st.sidebar:
    st.title("🍸 Where Was AI?")
    st.caption("A very New York spoiler-free companion, darling")

    st.markdown("---")
    st.markdown("### 📺 Watch Progress")
    
    # Episode Selector (1 to 3)
    selected_ep = st.radio(
        "Select your current episode:",
        options=list(AVAILABLE_EPISODES.keys()),
        format_func=lambda ep: AVAILABLE_EPISODES[ep],
        index=st.session_state.current_episode - 1,
        help="Choose the episode you have watched up to. Future episodes are strictly blocked.",
    )

    # If the episode changed, update session state
    if selected_ep != st.session_state.current_episode:
        st.session_state.current_episode = selected_ep
        st.rerun()

    image_url, image_caption = EPISODE_IMAGES[st.session_state.current_episode]
    st.image(image_url, caption=image_caption, width="stretch")

    st.markdown("---")
    st.markdown("### 🛡️ Anti-Spoiler Shield")
    st.info(
        f"**Active Checkpoint:** {AVAILABLE_EPISODES[st.session_state.current_episode]}\n\n"
        f"The assistant only accesses data and summaries up to **Episode {st.session_state.current_episode}**. "
        "Any question revealing later plots will be refused."
    )

    st.markdown("### 💡 Try Asking")
    
    # Dynamic queries based on current episode selection
    if st.session_state.current_episode == 1:
        sample_queries = [
            "What happens in Episode 1?",
            "Who is Mr. Big and how did Carrie meet him?",
            "Which characters have appeared so far?",
            "What happens in Episode 2? (Spoiler test)",
        ]
    elif st.session_state.current_episode == 2:
        sample_queries = [
            "What happens in Episode 2 (Models and Mortals)?",
            "What is a 'modelizer' and who are they?",
            "Who is Derek 'The Bone'?",
            "What happens in Episode 3? (Spoiler test)",
        ]
    else:  # Episode 3
        sample_queries = [
            "Summarize Episode 3: Bay of Married Pigs",
            "Why does Miranda pretend to be in a relationship with Syd?",
            "What happened with Carrie and Peter in the Hamptons?",
            "What happens in Episode 4? (Spoiler test)",
        ]

    for q in sample_queries:
        if st.button(q, width="stretch", key=f"btn_{st.session_state.current_episode}_{q}"):
            st.session_state.pending_prompt = q
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", width="stretch", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    with st.expander("ℹ️ How it works", expanded=False):
        st.markdown(
            """
            - **SQL Database**: Queries characters, appearances, and metadata filtered up to your active episode.
            - **RAG Vector Store**: Retrieves episode summaries with semantic search, protected by episode filters.
            - **Anti-Spoiler Guardrails**: LLM is instructed to halt if an answer requires knowledge of unreached episodes.
            """
        )

# Header Section
st.markdown('<div class="main-header">🍸 Where Was AI?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Your spoiler-free <i>Sex and the City</i> companion. '
    'A little archive of characters, relationships, and Manhattan misadventures — '
    'with absolutely no spoilers past your current episode. Because knowledge is power, '
    'but spoilers are a friendship-ending offense.</div>',
    unsafe_allow_html=True,
)

current_ep_title = AVAILABLE_EPISODES[st.session_state.current_episode]
st.markdown(
    f'<div class="badge-pill">🛡️ Watching checkpoint: {current_ep_title} (Episodes > {st.session_state.current_episode} blocked)</div>',
    unsafe_allow_html=True,
)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check for pending prompt from quick buttons or chat input
pending_prompt = st.session_state.pop("pending_prompt", None)
user_prompt = st.chat_input("Ask the archive a question, darling...")

prompt_to_process = pending_prompt or user_prompt

if prompt_to_process:
    # Append & render user message
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    # Render assistant response with streaming
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        response_placeholder = st.empty()
        full_response = ""
        tool_logs = []

        try:
            status_placeholder.markdown(
                f'<div class="archive-status">🍸 Let me consult the archives, darling '
                f'(up to Episode {st.session_state.current_episode})...</div>',
                unsafe_allow_html=True,
            )

            # Prepare conversation messages for the agent
            conversation_payload = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages
            ]

            # Stream response events with selected episode checkpoint
            for event_type, data in get_response_stream(
                conversation_payload,
                current_episode_id=st.session_state.current_episode,
            ):
                if event_type == "token":
                    full_response += data
                    response_placeholder.markdown(full_response + "▌")
                elif event_type == "tool_start":
                    tool_name, tool_input = data
                    readable_name = tool_name.replace("_", " ").title()
                    status_placeholder.markdown(
                        f'<div class="archive-status">🔍 Consulting {readable_name}...</div>',
                        unsafe_allow_html=True,
                    )
                    tool_logs.append(readable_name)
                elif event_type == "tool_delta":
                    pass
                elif event_type == "tool_end":
                    pass

            if tool_logs:
                unique_tools = list(dict.fromkeys(tool_logs))
                status_placeholder.markdown(
                    f'<div class="archive-status">✨ The archives have spoken '
                    f'({", ".join(unique_tools)})</div>',
                    unsafe_allow_html=True,
                )
            else:
                status_placeholder.markdown(
                    '<div class="archive-status">✨ The gossip is ready</div>',
                    unsafe_allow_html=True,
                )

            # Finalize output display without the cursor
            if full_response:
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                fallback_msg = "The archive is being dramatic. Try rephrasing your question."
                response_placeholder.markdown(fallback_msg)
                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})

        except Exception as e:
            status_placeholder.empty()
            error_message = f"⚠️ The archive is having a little Manhattan meltdown: {str(e)}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
