import streamlit as st
from openai import OpenAI
import pandas as pd
import altair as alt

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="Category Strategy Builder",
    layout="wide"
)

# =========================================================
# INIT
# =========================================================
def init(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

init("step", 1)

init("category_name", "")
init("category_desc", "")
init("category_type", "Product")
init("category_level", "L1")

init("countries", "")
init("market", "")

init("strength", "")
init("weakness", "")

init("opportunities_box", "")
init("threats_box", "")

init("targets", {})
init("levers", "")

if "risks" not in st.session_state:
    st.session_state.risks = [{
        "name":"",
        "impact":3,
        "prob":3
    }]

if "stakeholders" not in st.session_state:
    st.session_state.stakeholders = [{
        "group":"",
        "role":"",
        "power":3,
        "interest":3
    }]

# =========================================================
# SIDEBAR
# =========================================================
steps = [
    "Category",
    "Market",
    "SWOT",
    "Risk",
    "Stakeholders",
    "Targets",
    "Summary",
    "Strategic Levers",
    "Executive"
]

st.sidebar.title("Progress")

for i, s in enumerate(steps, start=1):

    if i == st.session_state.step:
        st.sidebar.markdown(f"➡️ **{s}**")

    elif i < st.session_state.step:
        st.sidebar.markdown(f"✅ {s}")

    else:
        st.sidebar.markdown(f"⬜ {s}")

# =========================================================
# NAVIGATION
# =========================================================
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

# =========================================================
# HEADER
# =========================================================
st.title("🧠 Category Strategy Builder")

st.subheader(
    f"Step {st.session_state.step}: "
    f"{steps[st.session_state.step-1]}"
)

# =========================================================
# STEP 1 — CATEGORY
# =========================================================
if st.session_state.step == 1:

    st.session_state.category_name = st.text_input(
        "Category Name"
    )

    st.session_state.category_desc = st.text_area(
        "Describe your category / industry"
    )

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
# STEP 2 — MARKET
# =========================================================
elif st.session_state.step == 2:

    st.session_state.countries = st.text_input(
        "Where are your key suppliers located? (up to 3 countries)"
    )

    if st.button("Generate PESTLE"):

        prompt = f"""
Create a concise PESTLE analysis.

Category:
{st.session_state.category_name}

Industry:
{st.session_state.category_desc}

Supplier Countries:
{st.session_state.countries}

Rules:
- concise
- business tone
- bullet points only
"""

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{
                "role":"user",
                "content":prompt
            }]
        )

        st.session_state.market = (
            res.choices[0].message.content
        )

    st.session_state.market = st.text_area(
        "Market Analysis",
        value=st.session_state.market
    )

    nav(3)

# =========================================================
# STEP 3 — SWOT
# =========================================================
elif st.session_state.step == 3:

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:

        st.session_state.strength = st.text_area(
            "Strengths"
        )

    with col2:

        st.session_state.weakness = st.text_area(
            "Weaknesses"
        )

    with col3:

        st.markdown("### Opportunities")

        if st.button("Generate Opportunities"):

            prompt = f"""
Generate opportunities.

Category:
{st.session_state.category_name}

Industry:
{st.session_state.category_desc}

Supplier Countries:
{st.session_state.countries}

Rules:
- do not separate by country
- one consolidated list
- concise
- bullet points only
"""

            res = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{
                    "role":"user",
                    "content":prompt
                }]
            )

            st.session_state.opportunities_box = (
                res.choices[0].message.content
            )

        st.session_state.opportunities_box = st.text_area(
            "Opportunities",
            value=st.session_state.opportunities_box,
            key="opp_box"
        )

    with col4:

        st.markdown("### Threats")

        if st.button("Generate Threats"):

            prompt = f"""
Generate threats.

Category:
{st.session_state.category_name}

Industry:
{st.session_state.category_desc}

Supplier Countries:
{st.session_state.countries}

Rules:
- do not separate by country
- one consolidated list
- concise
- bullet points only
"""

            res = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{
                    "role":"user",
                    "content":prompt
                }]
            )

            st.session_state.threats_box = (
                res.choices[0].message.content
            )

        st.session_state.threats_box = st.text_area(
            "Threats",
            value=st.session_state.threats_box,
            key="threat_box"
        )

    nav(4)

# =========================================================
# STEP 4 — RISK
# =========================================================
elif st.session_state.step == 4:

    st.header("Risk Assessment")

    if st.button("Add Risk"):

        st.session_state.risks.append({
            "name":"",
            "impact":3,
            "prob":3
        })

        st.rerun()

    for i, r in enumerate(st.session_state.risks):

        col1, col2, col3, col4 = st.columns([3,1,1,1])

        with col1:

            r["name"] = st.text_input(
                f"Risk {i+1}",
                value=r["name"],
                key=f"r{i}"
            )

        with col2:

            r["impact"] = st.slider(
                f"Impact {i+1}",
                1,5,r["impact"],
                key=f"ri{i}"
            )

        with col3:

            r["prob"] = st.slider(
                f"Probability {i+1}",
                1,5,r["prob"],
                key=f"rp{i}"
            )

        if i > 0:

            with col4:

                if st.button("❌", key=f"del_r{i}"):

                    st.session_state.risks.pop(i)
                    st.rerun()

    nav(5)

# =========================================================
# STEP 5 — STAKEHOLDERS
# =========================================================
elif st.session_state.step == 5:

    st.header("Stakeholder Management")

    if st.button("Add Stakeholder"):

        st.session_state.stakeholders.append({
            "group":"",
            "role":"",
            "power":3,
            "interest":3
        })

        st.rerun()

    for i, s in enumerate(st.session_state.stakeholders):

        col1, col2, col3, col4, col5 = st.columns(
            [2,2,1,1,1]
        )

        with col1:

            s["group"] = st.text_input(
                f"Group {i+1}",
                value=s["group"],
                key=f"g{i}"
            )

        with col2:

            s["role"] = st.text_input(
                f"Role {i+1}",
                value=s["role"],
                key=f"ro{i}"
            )

        with col3:

            s["power"] = st.slider(
                f"Power {i+1}",
                1,5,s["power"],
                key=f"p{i}"
            )

        with col4:

            s["interest"] = st.slider(
                f"Interest {i+1}",
                1,5,s["interest"],
                key=f"in{i}"
            )

        if i > 0:

            with col5:

                if st.button("❌", key=f"del_s{i}"):

                    st.session_state.stakeholders.pop(i)
                    st.rerun()

    nav(6)

# =========================================================
# STEP 6 — TARGETS
# =========================================================
elif st.session_state.step == 6:

    targets = {}

    for t in [
        "Availability",
        "Cost",
        "Innovation",
        "Quality",
        "Risk",
        "Sustainability"
    ]:

        targets[t] = st.slider(
            t,
            1,
            5,
            3
        )

    st.session_state.targets = targets

    nav(7)

# =========================================================
# STEP 7 — SUMMARY
# =========================================================
elif st.session_state.step == 7:

    st.header("Summary")

    st.write(
        f"**{st.session_state.category_name}** "
        f"({st.session_state.category_type}, "
        f"{st.session_state.category_level})"
    )

    st.write(st.session_state.category_desc)

    # ---------------- MARKET ----------------
    st.subheader("Market")

    st.write(st.session_state.market)

    # ---------------- SWOT ----------------
    st.subheader("SWOT")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:

        st.markdown("### Strengths")
        st.write(st.session_state.strength)

    with col2:

        st.markdown("### Weaknesses")
        st.write(st.session_state.weakness)

    with col3:

        st.markdown("### Opportunities")
        st.write(st.session_state.opportunities_box)

    with col4:

        st.markdown("### Threats")
        st.write(st.session_state.threats_box)

    # ---------------- RISK MAP ----------------
    st.subheader("Risk Map")

    df = pd.DataFrame(st.session_state.risks)

    if not df.empty:

        chart = alt.Chart(df).mark_circle(
            size=120
        ).encode(

            x=alt.X(
                "prob",
                scale=alt.Scale(domain=[0,5]),
                axis=alt.Axis(
                    values=[0,1,2,3,4,5],
                    title="Probability"
                )
            ),

            y=alt.Y(
                "impact",
                scale=alt.Scale(domain=[0,5]),
                axis=alt.Axis(
                    values=[0,1,2,3,4,5],
                    title="Impact"
                )
            ),

            tooltip=[
                "name",
                "impact",
                "prob"
            ]
        )

        text = alt.Chart(df).mark_text(
            dy=-10,
            color="white"
        ).encode(
            x="prob",
            y="impact",
            text="name"
        )

        st.altair_chart(
            chart + text,
            use_container_width=True
        )

    # ---------------- STAKEHOLDER MAP ----------------
    st.subheader("Stakeholder Map")

    df2 = pd.DataFrame(st.session_state.stakeholders)

    if not df2.empty:

        chart2 = alt.Chart(df2).mark_circle(
            size=120
        ).encode(

            x=alt.X(
                "power",
                scale=alt.Scale(domain=[0,5]),
                axis=alt.Axis(
                    values=[0,1,2,3,4,5],
                    title="Power"
                )
            ),

            y=alt.Y(
                "interest",
                scale=alt.Scale(domain=[0,5]),
                axis=alt.Axis(
                    values=[0,1,2,3,4,5],
                    title="Interest"
                )
            ),

            tooltip=[
                "group",
                "power",
                "interest"
            ]
        )

        text2 = alt.Chart(df2).mark_text(
            dy=-10,
            color="white"
        ).encode(
            x="power",
            y="interest",
            text="group"
        )

        st.altair_chart(
            chart2 + text2,
            use_container_width=True
        )

    # ---------------- TARGETS ----------------
    st.subheader(
        "Value Contribution Priorities"
    )

    targets = st.session_state.targets

    if targets:

        sorted_targets = sorted(
            targets.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top = [
            t[0]
            for t in sorted_targets[:3]
        ]

        st.markdown(f"""
**Primary focus areas:** {", ".join(top)}

These priorities indicate where the category strategy should concentrate its efforts to maximize value creation.
""")

        for k, v in sorted_targets:

            st.markdown(f"**{k}**")
            st.progress(v / 5)

    nav(8)

# =========================================================
# STEP 8 — STRATEGIC LEVERS
# =========================================================
elif st.session_state.step == 8:

    if st.button(
        "Generate Strategic Levers"
    ):

        risks_text = "\n".join([
            f"- {r['name']} "
            f"(Impact {r['impact']}, "
            f"Probability {r['prob']})"
            for r in st.session_state.risks
            if r["name"]
        ])

        stakeholders_text = "\n".join([
            f"- {s['group']} "
            f"({s['role']}) "
            f"- Power {s['power']}, "
            f"Interest {s['interest']}"
            for s in st.session_state.stakeholders
            if s["group"]
        ])

        targets_text = ", ".join([
            f"{k}: {v}"
            for k, v in st.session_state.targets.items()
        ])

        prompt = f"""
Generate strategic levers.

Category:
{st.session_state.category_name}

Industry:
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

Rules:
- max 8 bullets
- actionable
- business tone
- explicitly consider risks, stakeholders, and priorities
"""

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{
                "role":"user",
                "content":prompt
            }],
            temperature=0.6
        )

        st.session_state.levers = (
            res.choices[0].message.content
        )

    st.write(st.session_state.levers)

    nav(9)

# =========================================================
# STEP 9 — EXEC SUMMARY
# =========================================================
elif st.session_state.step == 9:

    if st.button(
        "Generate Executive Summary"
    ):

        risks_text = "\n".join([
            f"- {r['name']} "
            f"(Impact {r['impact']}, "
            f"Probability {r['prob']})"
            for r in st.session_state.risks
            if r["name"]
        ])

        stakeholders_text = "\n".join([
            f"- {s['group']} "
            f"({s['role']}) "
            f"- Power {s['power']}, "
            f"Interest {s['interest']}"
            for s in st.session_state.stakeholders
            if s["group"]
        ])

        targets_text = ", ".join([
            f"{k}: {v}"
            for k, v in st.session_state.targets.items()
        ])

        prompt = f"""
Create a professional executive summary.

Category:
{st.session_state.category_name}

Industry:
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

Strategic Levers:
{st.session_state.levers}

Instructions:
- concise and structured
- business tone
- no fluff
- max 4 short paragraphs
"""

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{
                "role":"user",
                "content":prompt
            }],
            temperature=0.5
        )

        st.write(
            res.choices[0].message.content
        )

    col1, col2 = st.columns([1,3])

    with col1:

        if st.button("⬅️ Back"):

            st.session_state.step = 8
            st.rerun()
