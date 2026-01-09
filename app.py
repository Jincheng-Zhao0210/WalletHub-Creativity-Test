import os
import streamlit as st
from openai import OpenAI

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="FinanceHub + AI Guide", page_icon="💳", layout="wide")

# Read key safely (Streamlit secrets first, then env)
api_key = None
if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it to Streamlit Secrets or your environment variables.")
    st.stop()

client = OpenAI(api_key=api_key)

# Model (keep it flexible)
CHAT_MODEL = (
    (st.secrets.get("OPENAI_CHAT_MODEL") if hasattr(st, "secrets") else None)
    or os.getenv("OPENAI_CHAT_MODEL")
    or "gpt-4o-mini"
)

# ----------------------------
# Styling (simple, similar feel)
# ----------------------------
st.markdown(
    """
<style>
  .topbar {
    background: #201535;
    padding: 14px 18px;
    border-radius: 12px;
    color: white;
    display:flex;
    justify-content: space-between;
    align-items:center;
    margin-bottom: 18px;
  }
  .brand { font-weight: 700; font-size: 18px; display:flex; gap:10px; align-items:center; }
  .brand-badge {
    width: 26px; height: 26px; border-radius: 6px;
    background: #2dd4bf; display:inline-flex; align-items:center; justify-content:center;
    font-weight:800; color:#0b1020;
  }
  .nav { font-size: 14px; opacity: 0.9; display:flex; gap:16px; align-items:center; }
  .pill {
    background:#2f2350; padding:7px 12px; border-radius: 999px; display:inline-block;
  }
  .hero {
    padding: 22px 22px;
    border-radius: 18px;
    background: linear-gradient(180deg, #ffffff 0%, #f7f7fb 100%);
    border: 1px solid #ececf3;
  }
  .hero-title { font-size: 56px; font-weight: 800; line-height: 1.0; margin:0; }
  .hero-sub { font-size: 16px; opacity: 0.85; margin-top: 10px; max-width: 560px;}
  .cta { margin-top: 16px; }
  .video-card {
    background: #5b77f4;
    border-radius: 18px;
    height: 210px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-size: 26px;
    font-weight: 700;
    border: 1px solid rgba(0,0,0,0.05);
  }
  .section-card {
    background: white;
    border: 1px solid #ececf3;
    border-radius: 18px;
    padding: 18px 18px;
    margin-top: 16px;
  }
  .section-title { font-size: 44px; font-weight: 800; line-height:1.0; margin:0; white-space: pre-line; }
  .section-kicker { font-size: 13px; letter-spacing: 0.12em; opacity: 0.6; font-weight: 700; }
  .feature { margin-top: 10px; }
  .feature b { font-size: 16px; }
  .muted { opacity: 0.75; }
  .linkish { color: #2563eb; font-weight: 600; }
  .small { font-size: 13px; opacity: 0.75;}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Helper: call model (Chat Completions)
# ----------------------------
def ask_ai(user_question: str) -> str:
    # Context: Only YOUR app's public sections (safe)
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
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful, safe onboarding assistant for a finance app."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry — I hit an error calling the model: {e}"


# ----------------------------
# Sidebar: AI Assistant
# ----------------------------
with st.sidebar:
    st.markdown("## 🤖 AI Assistant")
    st.caption("Public onboarding guide (no login, no private data).")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    # quick prompts
    cols = st.columns(2)
    if cols[0].button("60-sec tour"):
        st.session_state.chat.append(("user", "Give me a 60-second tour of this app. Where should a new user start?"))
        st.session_state.chat.append(("assistant", ask_ai("Give me a 60-second tour of this app. Where should a new user start?")))
    if cols[1].button("Why score drops?"):
        st.session_state.chat.append(("user", "Why can a credit score drop? Explain in plain English."))
        st.session_state.chat.append(("assistant", ask_ai("Why can a credit score drop? Explain in plain English.")))

    st.divider()

    # show chat history
    for role, msg in st.session_state.chat[-10:]:
        if role == "user":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**AI:** {msg}")

    user_q = st.text_input("Ask a question", placeholder="e.g., What is credit utilization?")
    if st.button("Send", type="primary", use_container_width=True) and user_q.strip():
        st.session_state.chat.append(("user", user_q.strip()))
        st.session_state.chat.append(("assistant", ask_ai(user_q.strip())))

# ----------------------------
# Top bar (similar)
# ----------------------------
st.markdown(
    """
<div class="topbar">
  <div class="brand"><span class="brand-badge">W</span> FinanceHub</div>
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

# ----------------------------
# Hero section (important only)
# ----------------------------
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
    st.markdown('<p class="small">Tip: open the AI Assistant on the left to ask “Where do I start?”</p>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="video-card">Meet FinanceHub ▶</div>', unsafe_allow_html=True)
    st.caption("Placeholder for an intro video (optional).")

# ----------------------------
# Section builder
# ----------------------------
def section(kicker, title, features, footer_link="View all features →"):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)
    for name, desc in features:
        st.markdown(
            f'<div class="feature"><b>＋ {name}</b><div class="muted">{desc}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown(f'<div class="linkish" style="margin-top:12px;">{footer_link}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Main important sections (simplified)
# ----------------------------
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

st.caption("This is a demo UI + onboarding AI. It does not use private user data and is intended for navigation + education.")
