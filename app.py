import os
from pathlib import Path
import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="FinanceHub", page_icon="💳", layout="wide")

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "show_ai" not in st.session_state:
    st.session_state.show_ai = False
if "chat" not in st.session_state:
    st.session_state.chat = []

# --------------------------------------------------
# OpenAI config
# --------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)
MODEL = st.secrets.get("OPENAI_CHAT_MODEL", os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"))

# --------------------------------------------------
# Styling (WalletHub-like typography + colors)
# --------------------------------------------------
st.markdown(
    """
<style>
/* --- Page --- */
section.main { background: #f6f7fb; }

/* --- Top nav --- */
.topbar{
  background:#201535; padding:14px 18px; border-radius:12px; color:white;
  display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;
}
.brand{ font-weight:800; font-size:16px; display:flex; gap:10px; align-items:center; }
.brand-badge{
  width:26px; height:26px; border-radius:6px; background:#2dd4bf;
  display:inline-flex; align-items:center; justify-content:center;
  font-weight:900; color:#0b1020;
}
.nav{ font-size:13px; opacity:.95; display:flex; gap:14px; align-items:center; }
.pill{ background:#2f2350; padding:7px 12px; border-radius:999px; display:inline-block; }

/* --- Hero --- */
.hero-wrap{ padding:8px 6px 6px 6px; }
.hero-title{
  font-family:Georgia,"Times New Roman",serif; font-size:72px; font-weight:700;
  line-height:.98; color:#0f172a; margin:0;
}
.hero-sub{ font-size:16px; color:#475569; margin-top:14px; max-width:620px; }
.hero-cta-row{ margin-top:16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
.note{ font-size:12px; color:#64748b; margin-top:10px; }

/* --- Video card --- */
.video-card{
  background:#5b77f4; border-radius:18px; height:240px;
  display:flex; align-items:center; justify-content:center;
  color:white; font-size:26px; font-weight:800;
  border:1px solid rgba(0,0,0,.05);
}

/* --- Sections --- */
.section-card{
  background:white; border:1px solid #ececf3; border-radius:22px;
  padding:22px; margin-top:18px;
}
.section-kicker{
  font-size:12px; letter-spacing:.14em; color:#64748b; font-weight:800;
}
.section-title{
  font-family:Georgia,"Times New Roman",serif; font-size:54px; font-weight:700;
  line-height:1.02; color:#0f172a; margin:8px 0 10px 0; white-space:pre-line;
}
.feature{ margin-top:14px; }
.feature b{ font-size:16px; font-weight:700; color:#0f172a; }
.feature .desc{ margin-left:18px; margin-top:4px; color:#475569; font-size:14px; }
.linkish{ color:#2563eb; font-weight:700; margin-top:14px; }

/* --- AI sidebar card (multi-color) --- */
.ai-card{
  background:linear-gradient(135deg,#eef2ff 0%, #f0fdf4 50%, #fff7ed 100%);
  border:1px solid #e5e7eb; border-radius:16px; padding:14px; margin-bottom:12px;
}
.ai-title{ font-size:18px; font-weight:900; color:#0f172a; margin:0 0 6px 0; }
.ai-desc{ font-size:13px; color:#334155; line-height:1.45; margin:0; }
.ai-highlight{ color:#2563eb; font-weight:900; }
.ai-note{ font-size:12px; color:#64748b; margin-top:8px; }

/* --- End-page deals section (WalletHub-like) --- */
.deals-wrap{ margin-top:34px; padding:10px 0 6px 0; }
.deals-kicker{
  font-size:12px; letter-spacing:.14em; color:#0f172a; font-weight:800; text-align:center;
}
.deals-title{
  font-family:Georgia,"Times New Roman",serif; font-size:64px; font-weight:700;
  line-height:1.03; color:#0f172a; text-align:center; margin-top:8px;
}
.deals-sub{
  font-size:15px; color:#475569; text-align:center;
  max-width:720px; margin:12px auto 0 auto;
}
.deals-grid{
  max-width:980px; margin:24px auto 0 auto;
  display:grid; grid-template-columns:repeat(3, 1fr); gap:18px;
}
@media (max-width:900px){ .deals-grid{ grid-template-columns:repeat(2, 1fr); } }
@media (max-width:600px){ .deals-grid{ grid-template-columns:1fr; } }
.deal-card{
  background:#f3f5f9; border:1px solid #edf0f6; border-radius:22px;
  padding:18px 14px; height:150px;
  display:flex; flex-direction:column; justify-content:center; align-items:center;
}
.deal-icon{
  width:54px; height:54px; border-radius:18px; background:white;
  border:1px solid #e7eaf2;
  display:flex; align-items:center; justify-content:center;
  font-size:28px; margin-bottom:10px;
}
.deal-label{ font-size:20px; color:#0f172a; font-weight:500; }
.deals-cta{ display:flex; justify-content:center; margin-top:22px; }
.wallethub-btn button{
  background:#201535 !important; color:white !important;
  border-radius:999px !important; padding:0.65rem 1.6rem !important;
  font-weight:700 !important; border:none !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# AI (Natural, no rigid format, no forced "next clicks")
# --------------------------------------------------
def ask_ai(question: str) -> str:
    prompt = f"""
You are a friendly AI onboarding assistant for a finance app UI.

Your role:
- Help users understand what this app offers
- Explain financial concepts in plain, simple English
- Gently guide users without giving rigid steps
- Never claim access to personal or private data

Important rules:
- Do NOT use fixed formats, numbered lists, or checklists unless the user asks for them
- Do NOT give compliance-style or scripted answers
- Keep the tone natural, supportive, and conversational
- If helpful, casually mention where in the app a feature lives (e.g., “Credit section”)
- If the question is vague, ask ONE short clarifying question

Context:
This app includes budgeting, credit education, offers comparison, investments tracking, and identity protection.
It is for learning and navigation only (no login, no private data).

User question:
{question}

Respond naturally, like a helpful product guide.
"""
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful, calm onboarding assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return "Sorry — I ran into a temporary issue. Please try again."

def push_chat(q: str):
    st.session_state.chat.append(("You", q))
    st.session_state.chat.append(("AI", ask_ai(q)))

# --------------------------------------------------
# Sidebar: AI Assistant (button-activated)
# --------------------------------------------------
if st.session_state.show_ai:
    with st.sidebar:
        # Use your picture (no robot emoji)
        img_candidates = ["ai_assistant.png", "picture.png", "picture.jpg", "picture.jpeg", "picture.webp"]
        img_path = next((p for p in img_candidates if Path(p).exists()), None)
        if img_path:
            st.image(img_path, use_container_width=True)

        st.markdown(
            """
<div class="ai-card">
  <div class="ai-title">AI Assistant</div>
  <p class="ai-desc">
    Hi! I am your <span class="ai-highlight">AI assistant</span>.<br/>
    You can ask me questions about this app, explore features, and get simple explanations in plain English.
  </p>
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

        c1, c2 = st.columns(2)
        if c1.button("60-sec tour", use_container_width=True):
            push_chat("Give me a 60-second tour of this app. Where should a new user start?")
        if c2.button("Where should I start?", use_container_width=True):
            push_chat("Where should a new user start?")

        if st.button("Explain credit score", use_container_width=True):
            push_chat("Explain what a credit score is in simple English.")

        st.divider()

        for role, msg in st.session_state.chat[-10:]:
            st.markdown(f"**{role}:** {msg}")

        user_q = st.text_input("Ask a question", placeholder="Type your question here…")
        if st.button("Send", type="primary", use_container_width=True) and user_q.strip():
            push_chat(user_q.strip())

# --------------------------------------------------
# Top bar
# --------------------------------------------------
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

# --------------------------------------------------
# Hero
# --------------------------------------------------
left, right = st.columns([1.25, 1])
with left:
    st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Supercharge<br/>Your Finances</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">FinanceHub helps you make the most of your money. '
        'Strengthen your credit, budget better, track offers, monitor investments, and protect your identity — all in one place.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-cta-row">', unsafe_allow_html=True)
    st.button("Get Started for Free", type="primary")
    if st.button("Ask AI Assistant"):
        st.session_state.show_ai = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="note">AI is optional: education + navigation (no login, no private data).</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="video-card">Meet FinanceHub ▶</div>', unsafe_allow_html=True)
    st.caption("Placeholder for an intro video (optional).")

# --------------------------------------------------
# Section builder
# --------------------------------------------------
def section(kicker: str, title: str, features: list, footer: str = "View all features →"):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    for name, desc in features:
        st.markdown(
            f'<div class="feature"><b>＋ {name}</b><div class="desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown(f'<div class="linkish">{footer}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Main sections
# --------------------------------------------------
section(
    "BUDGETING & SPENDING",
    "Make your money\nwork for you",
    [
        ("Budgeting Tool", "Create a budget and take control of your spending."),
        ("Spending Tracker", "Monitor spending habits and identify potential savings."),
        ("Subscription Manager", "Effortlessly manage subscriptions and cancel what you no longer need."),
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
        ("Personalized Credit Card Offers", "Find cards that fit goals like cash back or low APR."),
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
        ("Retirement Planning", "Plan targets based on timeline and lifestyle goals."),
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

# --------------------------------------------------
# End page: "Find the Best Deals"
# --------------------------------------------------
st.markdown('<div class="deals-wrap">', unsafe_allow_html=True)
st.markdown('<div class="deals-kicker">SAVINGS OPPORTUNITIES</div>', unsafe_allow_html=True)
st.markdown('<div class="deals-title">Find the Best Deals</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="deals-sub">People trust FinanceHub because of its user reviews, unbiased recommendations, '
    'and transparent rating logic designed to help you compare options confidently.</div>',
    unsafe_allow_html=True
)

cards = [
    ("💳", "Credit Cards"),
    ("💰", "Personal Loans"),
    ("🚗", "Car Insurance"),
    ("🐷", "Savings Accounts"),
    ("🏦", "Checking Accounts"),
    ("📈", "CDs"),
]

st.markdown('<div class="deals-grid">', unsafe_allow_html=True)
for icon, label in cards:
    st.markdown(
        f"""
        <div class="deal-card">
          <div class="deal-icon">{icon}</div>
          <div class="deal-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="deals-cta wallethub-btn">', unsafe_allow_html=True)
st.button("View All FinanceHub Awards")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.caption("Demo UI + optional onboarding AI. Educational only. No login and no private user data.")
