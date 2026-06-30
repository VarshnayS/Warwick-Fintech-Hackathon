# Warwick-Fintech-Hackathon

## Vercel

This repository now includes a Vercel-compatible Python entrypoint:

- `app.py` exports a Flask `app` object.
- `pyproject.toml` points Vercel at `app:app`.
- `vercel.json` configures the Python function.

Deploy from the Vercel dashboard by importing this GitHub repo, or from the CLI:

```bash
vercel deploy
```

For local Vercel-style development:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8000`.

## Original Streamlit App

The original Streamlit version is still available in `main.py`. Install its full dependencies with:

```bash
pip install -r requirements-streamlit.txt
streamlit run main.py
```
