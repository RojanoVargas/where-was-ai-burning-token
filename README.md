# Where Was AI?

A spoiler-free chatbot to help you refresh your point in a series.

## Run locally

Install the dependencies and add the required values to `.env`:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app uses Nebius Token Factory for AI responses. Its OpenAI-compatible endpoint is configured with `NEBIUS_BASE_URL`, `NEBIUS_MODEL`, and `NEBIUS_API_KEY`. The existing Supabase vector index uses OpenAI embeddings because its stored vectors are 1,536-dimensional; `EMBEDDING_PROVIDER=openai` keeps retrieval compatible with that index.

## Evaluation

Run the repeatable smoke evaluation with:

```bash
python evaluate.py
```

It checks grounded answers for Episodes 1 and 2, verifies that Episode 3 is blocked when the user is on Episode 2, and reports pass rate and response time.
