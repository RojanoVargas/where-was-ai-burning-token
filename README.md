# Where Was (A)I?

A spoiler-free chatbot to help you refresh your point in a series.
[Live version](https://where-was-ai-burning-token.onrender.com/)

## Run locally

Install the dependencies and add the required values to `.env`:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app uses Nebius Token Factory for both AI responses and vector embeddings. Its OpenAI-compatible endpoint is configured with `NEBIUS_BASE_URL`, `NEBIUS_MODEL`, `NEBIUS_EMBEDDING_MODEL`, and `NEBIUS_API_KEY`. Embedding generation is handled with `EMBEDDING_PROVIDER=nebius` using 4,096-dimensional embeddings in Supabase.

## Evaluation

Run the repeatable smoke evaluation with:

```bash
python evaluate.py
```

It checks grounded answers for Episodes 1 and 2, verifies that Episode 3 is blocked when the user is on Episode 2, and reports pass rate and response time.
