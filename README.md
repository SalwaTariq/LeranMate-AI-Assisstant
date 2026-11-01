# 🎓 LearnMate AI – Personal AI Study Tutor

A simple AI study tutor built with **Python**, **Streamlit** and the **Google Gemini API**.

## Features

- Subject and topic selection
- Three learning levels: Beginner, Intermediate, Advanced
- Simple AI explanations, step by step, with real-life examples
- Chatbot for questions and follow-ups
- AI-generated quizzes (with scoring) and practice questions
- Study notes (downloadable) and quick summaries

## Files

| File | Purpose |
|------|---------|
| `app.py` | The whole app |
| `requirements.txt` | Python packages |
| `README.md` | This guide |

## Step 1: Get a Gemini API key

Create a free key at https://aistudio.google.com/apikey

## Step 2: Upload to GitHub

1. Create a new **public** repository on github.com (for example `learnmate-ai`).
2. Click **Add file → Upload files** and upload `app.py`, `requirements.txt` and `README.md`.
3. Click **Commit changes**.

Do **not** upload your API key. It goes into Streamlit Secrets (Step 3).

## Step 3: Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app** and pick your repository, the `main` branch, and `app.py`.
3. Open **Advanced settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
4. Click **Deploy**. Your app gets a public link in a minute or two.

## Run locally (optional)

```bash
pip install -r requirements.txt
mkdir .streamlit
echo 'GEMINI_API_KEY = "your-key-here"' > .streamlit/secrets.toml
streamlit run app.py
```

Never upload the `.streamlit` folder to GitHub.

## Troubleshooting

- **"API key not found"**: the secret must be named exactly `GEMINI_API_KEY`.
- **"Too many requests"**: the free tier has limits. Wait a minute and retry.
- **Quiz fails to build**: click Generate again. AI answers vary.
- **Model error**: change `MODEL = "gemini-2.5-flash"` near the top of `app.py` to a current Gemini model name.
