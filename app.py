"""LearnMate AI - Personal AI Study Tutor (Streamlit + Google Gemini). Single-file app."""

import json

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="LearnMate AI", page_icon="🎓", layout="wide")

MODEL = "gemini-2.5-flash"
SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science",
    "History", "Geography", "Economics", "Literature", "Languages",
    "Other (type your own)",
]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
LEVEL_GUIDE = {
    "Beginner": "Assume no prior knowledge. Use very simple words, short sentences and "
                "everyday analogies. Avoid jargon, or explain it right away.",
    "Intermediate": "Assume the student knows the basics. Use correct terminology and "
                    "explain the reasoning.",
    "Advanced": "Assume a strong foundation. Go deep, with nuance, edge cases and technical detail.",
}

# ---------------------------------------------------------------- Styling

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700&display=swap');
html, body, [class*="st-"], button, input, textarea { font-family: 'Lexend', sans-serif; }
.block-container { padding-top: 2rem; max-width: 1000px; }
.hero { background: linear-gradient(120deg, #312E81 0%, #4338CA 55%, #0EA5A4 100%);
        padding: 2rem 2.2rem; border-radius: 20px; margin-bottom: 1.5rem; }
.hero h1 { color: #fff; font-size: 2.2rem; margin: 0 0 .3rem 0; padding: 0; }
.hero p { color: #E0E7FF; font-size: 1.05rem; margin: 0; }
.chip { display: inline-block; background: #EEF0FF; color: #312E81; border-radius: 999px;
        padding: .25rem .85rem; margin: 0 .4rem 1rem 0; font-size: .85rem; font-weight: 500; }
.card { background: #fff; color: #1B1F3B; border: 1px solid #E3E6F5;
        border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
.card h2, .card h3 { color: #312E81; }
.stTabs [data-baseweb="tab"] { padding: .6rem 1.1rem; font-weight: 500; }
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button
    { border-radius: 10px; font-weight: 500; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🎓 LearnMate AI</h1>
  <p>Your personal AI study tutor. Pick a topic and learn it at your own pace.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- Gemini helpers

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

if not API_KEY:
    st.error("Gemini API key not found.")
    st.info("Add `GEMINI_API_KEY` in Streamlit **Settings → Secrets** (deployed) "
            "or `.streamlit/secrets.toml` (local). See the README.")
    st.stop()

client = genai.Client(api_key=API_KEY)


def system_prompt(subject, topic, level):
    return (f"You are LearnMate AI, a friendly and patient study tutor.\n"
            f"Subject: {subject}\nTopic: {topic}\nStudent level: {level}\n{LEVEL_GUIDE[level]}\n"
            "Be accurate and encouraging. Use Markdown. If unsure, say so instead of guessing.")


def ask_gemini(contents, system, as_json=False):
    """Send a prompt to Gemini. Returns text, or None after showing a friendly error."""
    try:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json" if as_json else "text/plain",
        )
        response = client.models.generate_content(model=MODEL, contents=contents, config=config)
        if response.text:
            return response.text
        st.error("Gemini returned an empty answer. Please try again.")
    except Exception as e:
        msg = str(e).lower()
        if "api key" in msg or "403" in msg or "401" in msg:
            st.error("The Gemini API key looks invalid. Check your secrets.")
        elif "429" in msg or "quota" in msg:
            st.error("Too many requests right now. Wait a minute and try again.")
        else:
            st.error("Could not reach Gemini. Please try again.")
    return None


def ask_json(prompt, system):
    text = ask_gemini(prompt, system, as_json=True)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        st.error("Gemini answered in the wrong format. Please try again.")
        return None


def clean_quiz(data):
    quiz = []
    for q in data if isinstance(data, list) else []:
        try:
            if len(q["options"]) == 4 and 0 <= int(q["answer_index"]) <= 3:
                quiz.append({"question": q["question"], "options": q["options"],
                             "answer_index": int(q["answer_index"]),
                             "explanation": q.get("explanation", "")})
        except (KeyError, TypeError, ValueError):
            continue
    return quiz


# ---------------------------------------------------------------- Sidebar

with st.sidebar:
    st.header("What do you want to learn?")
    subject = st.selectbox("Subject", SUBJECTS)
    if subject.startswith("Other"):
        subject = st.text_input("Your subject", placeholder="e.g. Psychology").strip()
    topic = st.text_input("Topic", placeholder="e.g. Photosynthesis").strip()
    level = st.radio("Learning level", LEVELS,
                     captions=["New to this", "Know the basics", "Want to go deep"])
    st.divider()
    st.caption("Powered by Google Gemini")

if not subject or not topic:
    st.markdown("""
### Get started in 3 steps
1. Choose a **subject** in the sidebar.
2. Type the **topic** you want to learn.
3. Pick your **level**, then explore the tabs.
""")
    st.stop()

sig = (subject, topic, level)
SYSTEM = system_prompt(subject, topic, level)


def save(name, data):
    st.session_state[name] = {"sig": sig, "data": data}


def load(name):
    """Saved results only show up for the current subject, topic and level."""
    item = st.session_state.get(name)
    return item["data"] if item and item["sig"] == sig else None


def card(text):
    st.markdown(f'<div class="card">\n\n{text}\n\n</div>', unsafe_allow_html=True)


st.markdown(f'<span class="chip">{subject}</span><span class="chip">{topic}</span>'
            f'<span class="chip">{level}</span>', unsafe_allow_html=True)

tab_learn, tab_chat, tab_quiz, tab_notes = st.tabs(
    ["📖 Learn", "💬 Ask Tutor", "📝 Quiz & Practice", "🗒️ Notes & Summary"])

# ---------------------------------------------------------------- Learn

with tab_learn:
    if st.button("Explain this topic", type="primary"):
        with st.spinner("Preparing your lesson..."):
            text = ask_gemini(f'''Teach me "{topic}". Use these Markdown sections:
## In simple words
A short, clear explanation.
## Step-by-step
Numbered steps that build understanding from the ground up.
## Real-life examples
2-3 relatable everyday examples.
## Key takeaways
3-5 bullet points to remember.''', SYSTEM)
        if text:
            save("lesson", text)
    lesson = load("lesson")
    if lesson:
        card(lesson)
    else:
        st.info("Click **Explain this topic** for a step-by-step lesson with real-life examples.")

# ---------------------------------------------------------------- Chat

with tab_chat:
    if st.session_state.get("chat_sig") != sig:  # new topic or level = new chat
        st.session_state.chat_sig = sig
        st.session_state.chat = []

    left, right = st.columns([4, 1])
    left.caption("Ask anything about this topic, including follow-up questions.")
    if right.button("Clear chat"):
        st.session_state.chat = []
        st.rerun()

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])

    question = st.chat_input(f"Ask a question about {topic}...")
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        contents = [{"role": "user" if m["role"] == "user" else "model",
                     "parts": [{"text": m["text"]}]} for m in st.session_state.chat]
        contents.append({"role": "user", "parts": [{"text": question}]})
        with st.spinner("Thinking..."):
            reply = ask_gemini(contents, SYSTEM + "\nThis is a chat: answer clearly and briefly, "
                               "and end with a short question to check understanding when helpful.")
        if reply:
            st.session_state.chat += [{"role": "user", "text": question},
                                      {"role": "assistant", "text": reply}]
            with st.chat_message("assistant"):
                st.markdown(reply)

# ---------------------------------------------------------------- Quiz & practice

with tab_quiz:
    mode = st.radio("Choose a mode", ["Multiple-choice quiz", "Practice questions"], horizontal=True)
    count = st.slider("Number of questions", 3, 10, 5)

    if mode == "Multiple-choice quiz":
        if st.button("Generate quiz", type="primary"):
            with st.spinner("Writing your quiz..."):
                data = ask_json(f'''Create a {count}-question multiple-choice quiz on "{topic}" for a {level} student.
Return ONLY a JSON list. Each item looks exactly like:
{{"question": "...", "options": ["text 1", "text 2", "text 3", "text 4"], "answer_index": 0, "explanation": "why it is correct"}}
Rules: exactly 4 options, answer_index is 0-3, one correct option, no "A)" prefixes.''', SYSTEM)
            quiz = clean_quiz(data) if data is not None else []
            if quiz:
                save("quiz", quiz)
                st.session_state.quiz_id = st.session_state.get("quiz_id", 0) + 1
                st.session_state.quiz_checked = False
            elif data is not None:
                st.error("Could not build the quiz. Please try again.")

        quiz = load("quiz")
        if quiz:
            qid = st.session_state.quiz_id
            with st.form(f"quiz_form_{qid}"):
                for i, q in enumerate(quiz):
                    st.markdown(f"**Q{i + 1}. {q['question']}**")
                    st.radio("Your answer", q["options"], index=None,
                             key=f"q_{qid}_{i}", label_visibility="collapsed")
                if st.form_submit_button("Check my answers", type="primary"):
                    st.session_state.quiz_checked = True

            if st.session_state.get("quiz_checked"):
                score = 0
                for i, q in enumerate(quiz):
                    correct = q["options"][q["answer_index"]]
                    if st.session_state.get(f"q_{qid}_{i}") == correct:
                        score += 1
                        st.success(f"Q{i + 1}: Correct! {q['explanation']}")
                    else:
                        st.error(f"Q{i + 1}: The answer is **{correct}**. {q['explanation']}")
                st.metric("Your score", f"{score} / {len(quiz)}")
        else:
            st.info("Click **Generate quiz** to test what you know.")

    else:
        if st.button("Generate practice questions", type="primary"):
            with st.spinner("Writing practice questions..."):
                data = ask_json(f'''Write {count} practice questions on "{topic}" for a {level} student.
Mix short-answer, problem-solving and "explain why" questions.
Return ONLY a JSON list. Each item: {{"question": "...", "answer": "a clear model answer"}}''', SYSTEM)
            items = [q for q in data if isinstance(q, dict) and "question" in q and "answer" in q] \
                if isinstance(data, list) else []
            if items:
                save("practice", items)
            elif data is not None:
                st.error("Could not build practice questions. Please try again.")

        items = load("practice")
        if items:
            for i, item in enumerate(items):
                st.markdown(f"**{i + 1}. {item['question']}**")
                with st.expander("Show model answer"):
                    st.markdown(item["answer"])
        else:
            st.info("Try answering on paper first, then open each model answer to check yourself.")

# ---------------------------------------------------------------- Notes & summary

with tab_notes:
    c1, c2 = st.columns(2)
    if c1.button("Create study notes", type="primary", use_container_width=True):
        with st.spinner("Writing your notes..."):
            text = ask_gemini(f'''Write well-organized study notes on "{topic}". Include: key definitions,
main concepts (bullets), important formulas or rules (if any), common mistakes,
and 3 quick revision questions at the end.''', SYSTEM)
        if text:
            save("notes", text)
    if c2.button("Quick summary", use_container_width=True):
        with st.spinner("Summarizing..."):
            text = ask_gemini(f'Summarize "{topic}" in under 150 words, then add a one-line '
                              '"If you remember only one thing" takeaway.', SYSTEM)
        if text:
            save("summary", text)

    summary, notes = load("summary"), load("notes")
    if summary:
        st.markdown("### Quick summary")
        card(summary)
    if notes:
        st.markdown("### Study notes")
        card(notes)
        st.download_button("Download notes (.md)", notes,
                           file_name=f"{topic.replace(' ', '_')}_notes.md")
    if not summary and not notes:
        st.info("Create study notes or a quick summary to revise from later.")
