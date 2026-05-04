import streamlit as st
from openai import OpenAI
import pandas as pd
import altair as alt

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Category Strategy Builder", layout="wide")

# ---------------- INIT ----------------
def init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

init("step", 1)
init("category_name","")
init("category_desc","")
init("category_type","Product")
init("category_level","L1")
init("cost_components",[])
init("market","")
init("countries","")

init("strength","")
init("weakness","")
init("opportunities_box","")
init("threats_box","")

init("targets",{})
init("strategy","")

if "risks" not in st.session_state:
    st.session_state.risks = [{"name":"", "impact":3, "prob":3}]

if "stakeholders" not in st.session_state:
    st.session_state.stakeholders = [{"group":"", "role":"", "power":3, "impact":3}]

# ---------------- SIDEBAR ----------------
steps = [
    "Category","Cost","Market","SWOT",
    "Risk","Stakeholders","Targets",
    "Summary","Strategy","Executive"
]

st.sidebar.title("Progress")

for i, s in enumerate(steps, start=1):
    if i == st.session_state.step:
        st.sidebar.markdown(f"➡️ **{s}**")
    elif i < st.session_state.step:
        st.sidebar.markdown(f"✅ {s}")
    else:
        st.sidebar.markdown(f"⬜ {s}")

# ---------------- NAV ----------------
def nav(next_step):
    col1, col2 = st.columns([1,3])

    with col1:
        if st.session_state.step > 1:
            if st.button("⬅️ Back"):
                st.session_state.step -= 1
                st.rerun()

    with col2:
        if st.button("Continue ➡️"):
            st.session_state.step = next_step
            st.rerun()

# ---------------- HEADER ----------------
st.title("🧠 Category Strategy Builder")
st.subheader(f"Step {st.session_state.step}: {steps[st.session_state.step-1]}")

# =========================================================
# STEP 1 — CATEGORY
# =========================================================
if st.session_state.step == 1:

    st.session_state.category_name = st.text_input("Category Name")
    st.session_state.category_desc = st.text_area("Describe your category")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.category_type = st.selectbox(
            "Category Type",
            ["Product","Service","Commodity","Project"]
        )

    with col2:
        st.session_state.category_level = st.selectbox(
            "Category Level (L1–L4)",
            ["L1","L2","L3","L4"]
        )

    nav(2)

# =========================================================
# STEP 2 — COST
# =========================================================
elif st.session_state.step == 2:

    defaults = [
        "Direct Material","Indirect Material",
        "Manufacturing Overhead","GSA","EBIT"
    ]

    selected = []
    for d in defaults:
        if st.checkbox(d, value=True):
            selected.append(d)

    st.session_state.cost_components = selected

    nav(3)

# =========================================================
# STEP 3 — MARKET
# =========================================================
elif st.session_state.step == 3:

    st.session_state.countries = st.text_input(
        "Where are your key suppliers located? (up to 3 countries)"
    )

    if st.button("Generate PESTLE"):
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{
                "role":"user",
                "content":f"PESTLE for {st.session_state.category_name}, countries {st.session_state.countries}, bullet points only"
            }]
        )
        st.session_state.market = res.choices[0].message.content

    st.session_state.market = st.text_area(
        "Market Analysis",
        value=st.session_state.market
    )

    nav(4)

# =========================================================
# STEP 4 — SWOT
# =========================================================
elif st.session_state.step == 4:

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.session_state.strength = st.text_area("Strengths")

    with col2:
        st.session_state.weakness = st.text_area("Weaknesses")

    with col3:
        st.markdown("### Opportunities")

        if st.button("Generate Opportunities"):
            res = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{
                    "role":"user",
                    "content":f"4 opportunities for {st.session_state.category_name}, bullet points only"
                }]
            )
            st.session_state.opportunities_box = res.choices[0].message.content

        st.text_area("Opportunities", key="opportunities_box")

    with col4:
        st.markdown("### Threats")

        if st.button("Generate Threats"):
            res = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{
                    "role":"user",
                    "content":f"4 threats for {st.session_state.category_name}, bullet points only"
                }]
            )
            st.session_state.threats_box = res.choices[0].message.content

        st.text_area("Threats", key="threats_box")

    nav(5)

# =========================================================
# STEP 5 — RISK
# =========================================================
elif st.session_state.step == 5:

    if st.button("Add Risk"):
        st.session_state.risks.append({"name":"","impact":3,"prob":3})
        st.rerun()

    for i, r in enumerate(st.session_state.risks):

        col1, col2, col3, col4 = st.columns([3,1,1,1])

        with col1:
            r["name"] = st.text_input(f"Risk {i+1}", value=r["name"], key=f"r{i}")

        with col2:
            r["impact"] = st.slider(f"Impact {i+1}",1,5,r["impact"],key=f"ri{i}")

        with col3:
            r["prob"] = st.slider(f"Probability {i+1}",1,5,r["prob"],key=f"rp{i}")

        if i > 0:
            with col4:
                if st.button("❌", key=f"del_r{i}"):
                    st.session_state.risks.pop(i)
                    st.rerun()

    nav(6)

# =========================================================
# STEP 6 — STAKEHOLDERS
# =========================================================
elif st.session_state.step == 6:

    if st.button("Add Stakeholder"):
        st.session_state.stakeholders.append({
            "group":"","role":"","power":3,"impact":3
        })
        st.rerun()

    for i, s in enumerate(st.session_state.stakeholders):

        col1, col2, col3, col4, col5 = st.columns([2,2,1,1,1])

        with col1:
            s["group"] = st.text_input(f"Group {i+1}", value=s["group"], key=f"g{i}")

        with col2:
            s["role"] = st.text_input(f"Role {i+1}", value=s["role"], key=f"ro{i}")

        with col3:
            s["power"] = st.slider(f"Power {i+1}",1,5,s["power"],key=f"p{i}")

        with col4:
            s["impact"] = st.slider(f"Impact {i+1}",1,5,s["impact"],key=f"i{i}")

        if i > 0:
            with col5:
                if st.button("❌", key=f"del_s{i}"):
                    st.session_state.stakeholders.pop(i)
                    st.rerun()

    nav(7)

# =========================================================
# STEP 7 — TARGETS
# =========================================================
elif st.session_state.step == 7:

    targets = {}
    for t in ["Availability","Cost","Innovation","Quality","Risk","Sustainability"]:
        targets[t] = st.slider(t,1,5,3)

    st.session_state.targets = targets

    nav(8)

# =========================================================
# STEP 8 — SUMMARY
# =========================================================
elif st.session_state.step == 8:

    st.header("Summary")

    st.write(f"**{st.session_state.category_name}** ({st.session_state.category_type}, {st.session_state.category_level})")
    st.write(st.session_state.category_desc)

    st.subheader("Cost")
    st.write(", ".join(st.session_state.cost_components))

    st.subheader("Market")
    st.write(st.session_state.market)

    st.subheader("SWOT")
    st.write(st.session_state.strength)
    st.write(st.session_state.weakness)
    st.write(st.session_state.opportunities_box)
    st.write(st.session_state.threats_box)

    # -------- RISK MAP --------
    st.subheader("Risk Map")

    df = pd.DataFrame(st.session_state.risks)

    if not df.empty:
        chart = alt.Chart(df).mark_circle(size=120).encode(
            x=alt.X(
                "prob",
                scale=alt.Scale(domain=[0, 5]),
                axis=alt.Axis(values=[0, 1, 2, 3, 4, 5], title="Probability")
            ),
            y=alt.Y(
                "impact",
                scale=alt.Scale(domain=[0, 5]),
                axis=alt.Axis(values=[0, 1, 2, 3, 4, 5], title="Impact")
            ),
            tooltip=["name", "impact", "prob"]
        )

        text = alt.Chart(df).mark_text(dy=-10).encode(
            x="prob",
            y="impact",
            text="name"
        )

        st.altair_chart(chart + text, use_container_width=True)

    # -------- STAKEHOLDER MAP --------
    st.subheader("Stakeholder Map")

    df2 = pd.DataFrame(st.session_state.stakeholders)

    if not df2.empty:
        chart2 = alt.Chart(df2).mark_circle(size=120).encode(
            x=alt.X(
                "power",
                scale=alt.Scale(domain=[0, 5]),
                axis=alt.Axis(values=[0, 1, 2, 3, 4, 5], title="Power")
            ),
            y=alt.Y(
                "impact",
                scale=alt.Scale(domain=[0, 5]),
                axis=alt.Axis(values=[0, 1, 2, 3, 4, 5], title="Impact")
            ),
            tooltip=["group", "power", "impact"]
        )

        text2 = alt.Chart(df2).mark_text(dy=-10).encode(
            x="power",
            y="impact",
            text="group"
        )

        st.altair_chart(chart2 + text2, use_container_width=True)

    # -------- TARGETS --------
    st.subheader("Value Contribution Priorities")

    targets = st.session_state.targets

    if targets:

        # Sort highest → lowest
        sorted_targets = sorted(
            targets.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Top 3 priorities
        top = [t[0] for t in sorted_targets[:3]]

        st.markdown(f"""
**Primary focus areas:** {", ".join(top)}

These priorities indicate where the category strategy should concentrate its efforts to maximize value creation.
""")

        # Visual bars
        for k, v in sorted_targets:
            st.markdown(f"**{k}**")
            st.progress(v / 5)

    nav(9)
# =========================================================
# STEP 9 — STRATEGY
# =========================================================
elif st.session_state.step == 9:

    if st.button("Generate Strategy"):

        # Convert risk + stakeholder to readable text
        risks_text = "\n".join([
            f"- {r['name']} (Impact {r['impact']}, Probability {r['prob']})"
            for r in st.session_state.risks if r["name"]
        ])

        stakeholders_text = "\n".join([
            f"- {s['group']} ({s['role']}) - Power {s['power']}, Impact {s['impact']}"
            for s in st.session_state.stakeholders if s["group"]
        ])

        targets_text = ", ".join([
            f"{k}: {v}" for k, v in st.session_state.targets.items()
        ])

        prompt = f"""
Build a category strategy using ALL the inputs below.

Category: {st.session_state.category_name}
Type: {st.session_state.category_type}
Level: {st.session_state.category_level}

Description:
{st.session_state.category_desc}

Cost Components:
{", ".join(st.session_state.cost_components)}

Market (PESTLE):
{st.session_state.market}

SWOT:
Strengths: {st.session_state.strength}
Weaknesses: {st.session_state.weakness}
Opportunities: {st.session_state.opportunities_box}
Threats: {st.session_state.threats_box}

Risks:
{risks_text}

Stakeholders:
{stakeholders_text}

Value Priorities:
{targets_text}

Output:
1. Strategic levers (max 6 bullets)
2. Key actions (top 5)

Rules:
- bullet points only
- no intro text
- use risk + stakeholder + priorities explicitly
"""

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.6
        )

        st.session_state.strategy = res.choices[0].message.content

    st.write(st.session_state.strategy)

    nav(10)

# =========================================================
# STEP 10 — EXEC SUMMARY
# =========================================================
elif st.session_state.step == 10:

    if st.button("Generate Executive Summary"):

        risks_text = "\n".join([
            f"- {r['name']} (Impact {r['impact']}, Probability {r['prob']})"
            for r in st.session_state.risks if r["name"]
        ])

        stakeholders_text = "\n".join([
            f"- {s['group']} ({s['role']}) - Power {s['power']}, Impact {s['impact']}"
            for s in st.session_state.stakeholders if s["group"]
        ])

        targets_text = ", ".join([
            f"{k}: {v}" for k, v in st.session_state.targets.items()
        ])

        prompt = f"""
Create a professional executive summary.

Category: {st.session_state.category_name}
Type: {st.session_state.category_type}
Level: {st.session_state.category_level}

Description:
{st.session_state.category_desc}

Market:
{st.session_state.market}

SWOT:
Strengths: {st.session_state.strength}
Weaknesses: {st.session_state.weakness}
Opportunities: {st.session_state.opportunities_box}
Threats: {st.session_state.threats_box}

Risks:
{risks_text}

Stakeholders:
{stakeholders_text}

Value Priorities:
{targets_text}

Strategy:
{st.session_state.strategy}

Instructions:
- concise and structured
- no fluff
- business tone
- max 3–4 short paragraphs
"""

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.5
        )

        st.write(res.choices[0].message.content)

    # -------- NAVIGATION --------
    col1, col2 = st.columns([1,3])

    with col1:
        if st.button("⬅️ Back"):
            st.session_state.step = 9
            st.rerun()