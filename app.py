import os
from pathlib import Path
import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="FinanceHub + AI Guide", page_icon="💳", layout="wide")

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "show_ai" not in st.session_state:
    st.session_state.show_ai = False
if "chat" not in st.session_state:
    st.session_state.chat = []

# --------------------------------------------------
# OpenAI Setup
# --------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# Choose model (you can override via Streamlit Secrets: OPENAI_CHAT_MODEL)
MODEL = st.secrets.get("OPENAI_CHAT_MODEL", os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"))

# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
<style>
  .topbar {
    background:#201535;
    padding:14px 18px;
    border-radius:12px;
    color:white;
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:18px;
  }
  .brand {font-weight:800;font-size:18px;display:flex;gap:10px;align-items:center;}
  .badge {
    width:26px;height:26px;border-radius:6px;
    background:#2dd4bf;color:#0b1020;
    display:flex;align-items:center;justify-content:center;
    font-weight:900;
  }
  .nav {font-size:14px; opacity:.9; display:flex; gap:14px; align-items:center;}
  .pill {background:#2f2350;padding:6px 12px;border-radius:999px}

  .hero {
    padding:24px;
    border-radius:18px;
    background:linear-gradient(180deg,#ffffff,#f6f7fb);
    border:1px solid #e5e7eb;
  }
  .hero-title {font-size:56px;font-weight:900;line-height:1;margin:0;}
  .hero-sub {font-size:16px;color:#475569;max-width:560px;margin-top:10px}
  .cta {margin-top:16px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;}
  .small {font-size:12px;color:#64748b;margin-top:8px;}

  .video-card {
    background:linear-gradient(135deg,#6366f1,#3b82f6);
    border-radius:18px;
    height:210px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-size:26px;
    font-weight:800;
    border:1px solid rgba(0,0,0,0.05);
  }

  .section {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:18px;
    margin-top:16px;
  }
  .section-title {font-size:42px;font-weight:900;white-space:pre-line;margin:6px 0 0 0;}
  .kicker {font-size:12px;letter-spacing:.12em;color:#64748b;font-weight:800}
  .feature {margin-top:10px}
  .feature b {font-size:16px}
  .muted {color:#475569}
  .link {color:#2563eb;font-weight:700;margin-top:12px}

  /* AI card with multiple colors */
  .ai-card {
    background:linear-gradient(135deg,#eef2ff 0%, #f0fdf4 50%, #fff7ed 100%);
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:14px;
    margin-bottom:12px;
  }
  .ai-title {font-size:20px;font-weight:900;color:#0f172a;margin:0 0 6px 0;}
  .ai-desc {font-size:13px;color:#334155;line-height:1.45;margin:0;}
  .ai-highlight {color:#2563eb;font-weight:800;}
  .ai-note {font-size:12px;color:#64748b;margin-top:8px;}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# AI Logic
# --------------------------------------------------
def ask_ai(user_question: str) -> str:
    app_context = """
This is a public finance onboarding UI with these main sections:
- Budgeting & Spending: Budgeting Tool, Spending Tracker, Subscription Manager, WalletScore
- Credit: Credit Scores & Reports, Credit Builder, Credit Report Monitoring, Credit Lock, Credit Improvement Plan, Debt Payoff Plan
- Offers: Personalized Credit Card Offers, Pre-qualified Personal Loans, Savings Opportunities
- Investments: Investment Monitoring, News Feed, Retirement Planning, Net Worth
- Identity: Dark Web Monitoring, Identity Theft Insurance, Identity Monitoring

Rules:
- You cannot access any private user credit report or account.
- If the user asks "why my score dropped", explain common reasons and offer optional high-level questions (utilization range, recent application yes/no, missed payment yes/no).
- Provide clear “Where to click next” suggestions.
- Keep answers concise, friendly, and beginner-friendly.
"""
    prompt = f"""You are an onboarding assistant for this finance app UI.
Use only the provided app context to describe features/navigation.
Do not claim access to private data.

APP CONTEXT:
{app_context}

User question: {user_question}

Answer with:
1) Direct answer (2-6 sentences)
2) 1-3 "Next clicks" suggestions (bullets)
3) If it’s a score-drop question, add a short safe checklist (utilization / inquiry / payment / age / derogatory)
"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful, safe onboarding assistant for a finance app."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry — I hit an error calling the model: {e}"


def push_chat(q: str):
    st.session_state.chat.append(("You", q))
    st.session_state.chat.append(("AI", ask_ai(q)))


# --------------------------------------------------
# Sidebar: AI Assistant (ONLY when activated)
# --------------------------------------------------
if st.session_state.show_ai:
    with st.sidebar:
        # Your AI image in repo root: picture.png (recommended)
        img_candidates = ["picture.png", "picture.jpg", "picture.jpeg", "picture.webp"]
        img_path = next((p for p in img_candidates if Path(p).exists()), None)
        if img_path:
            st.image(img_path, use_container_width=True)

        st.markdown(
            """
<div class="ai-card">
  <div class="ai-title">AI Assistant</div>
  <div class="ai-desc">
    Hi! I’m your <span class="ai-highlight">AI Assistant</span>.<br/>
    You can ask me questions about this app, explore features, and get simple explanations in plain English.
  </div>
  <div class="ai-note">
    No login • No private data • You decide when to use AI
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("Close AI Assistant", use_container_width=True):
            st.session_state.show_ai = False
            st.rerun()

        st.divider()
        st.caption("Example prompts (click to try):")

        if st.button("60-sec tour", use_container_width=True):
            push_chat("Give me a 60-second tour of this app. Where should a new user start?")
        if st.button("Where should I start?", use_container_width=True):
            push_chat("Where should a new user start, and what is the first best section to explore?")
        if st.button("Why can a credit score drop?", use_container_width=True):
            push_chat("Why can a credit score drop? Explain in plain English.")
        if st.button("What is credit utilization?", use_container_width=True):
            push_chat("What is credit utilization and why does it matter?")
        if st.button("Help me find the right section", use_container_width=True):
            push_chat("I want to save money and improve my credit. Which sections should I use and what should I click next?")

        st.divider()

        # Show recent chat
        for role, msg in st.session_state.chat[-10:]:
            st.markdown(f"**{role}:** {msg}")

        user_q = st.text_input("Ask a question", placeholder="Type your question here…")
        if st.button("Send", type="primary", use_container_width=True) and user_q.strip():
            push_chat(user_q.strip())

# --------------------------------------------------
# Top Bar
# --------------------------------------------------
st.markdown(
    """
<div class="topbar">
  <div class="brand"><div class="badge">W</div> FinanceHub</div>
  <div class="nav">
    <span>MyHub</span>
    <span>Credit Cards</span>
    <span>Loans</span>
    <span>Banking</span>
    <span>Pros</span>
    <span class="pill">Login</span>
    <span class="pill">Sign Up</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Hero Section
# --------------------------------------------------
left, right = st.columns([1.2, 1])
with left:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Supercharge<br/>Your Finances</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">A single place to learn, explore, and navigate key finance tools: budgeting, credit, offers, investments, and identity protection.</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cta">', unsafe_allow_html=True)
    st.button("Get Started for Free", type="primary")

    ai_label = "Ask AI Assistant" if not st.session_state.show_ai else "AI Assistant Active"
    if st.button(ai_label):
        st.session_state.show_ai = True
        st.rerun()

    st.markdown(
        '<div class="small">AI is optional: it explains features and suggests where to click next (no login, no private data).</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="video-card">Meet FinanceHub ▶</div>', unsafe_allow_html=True)
    st.caption("Placeholder for an intro video (optional).")

# --------------------------------------------------
# Section Builder
# --------------------------------------------------
def section(kicker, title, features, footer_link="View all features →"):
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(f'<div class="kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    for name, desc in features:
        st.markdown(f'<div class="feature"><b>＋ {name}</b><div class="muted">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="link">{footer_link}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Main Sections (important only)
# --------------------------------------------------
section(
    "BUDGETING & SPENDING",
    "Make your money\nwork for you",
    [
        ("Budgeting Tool", "Create a budget and take control of your spending."),
        ("Spending Tracker", "Monitor spending habits and identify potential savings."),
        ("Subscription Manager", "Manage subscriptions in one place and spot the ones you no longer need."),
        ("WalletScore", "A simple score to summarize your financial habits (high-level)."),
    ],
)

section(
    "CREDIT",
    "Improve your\ncredit & save",
    [
        ("Credit Scores & Reports", "Understand your score and how it changes over time."),
        ("Credit Builder", "Steps and tools to help strengthen credit history."),
        ("Credit Report Monitoring", "Alerts for important changes and potential issues."),
        ("Credit Lock", "Reduce the risk of new credit being opened without you."),
        ("Credit Improvement Plan", "A guided checklist to improve score drivers."),
        ("Debt Payoff Plan", "A plan to reduce debt with clear milestones."),
    ],
)

section(
    "OFFERS",
    "Personalized offers\nfor your credit",
    [
        ("Personalized Credit Card Offers", "Find cards that fit common goals like cash back or low APR."),
        ("Pre-qualified Personal Loans", "Explore loan options without heavy searching."),
        ("Savings Opportunities", "Discover ways to lower interest, fees, or recurring costs."),
    ],
)

section(
    "INVESTMENTS",
    "Monitor and track\nyour investments",
    [
        ("Investment Monitoring", "Track investment performance and changes over time."),
        ("News Feed", "A focused feed that highlights what matters."),
        ("Retirement Planning", "Plan savings targets based on timeline and lifestyle goals."),
        ("Net Worth", "Track assets and liabilities over time."),
    ],
)

section(
    "IDENTITY",
    "Protect your\nidentity",
    [
        ("Dark Web Monitoring", "Get notified if your information appears in common leak sources."),
        ("Identity Theft Insurance", "Coverage support if identity theft occurs (summary)."),
        ("Identity Monitoring", "Alerts for suspicious activity involving identity and accounts."),
    ],
)

st.caption("Demo UI + optional onboarding AI. No login and no private user data.")
