import os
import re
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Lumen Financial Risk Agent",
    layout="wide"
)

st.markdown("""
<style>
.block-container { padding-top: 2rem; }

.main-title {
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #667085;
    font-size: 1.05rem;
    margin-bottom: 1.5rem;
}

[data-testid="stMetric"] {
    background: #ffffff;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e6e8eb;
    box-shadow: 0 1px 6px rgba(16, 24, 40, 0.04);
}

.insight-box {
    background: #f8fafc;
    border-left: 5px solid #344054;
    border-radius: 14px;
    padding: 1.2rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

mark {
    background-color: #fff3b0;
    padding: 2px 4px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="main-title">Lumen Financial Risk Agent</div>
    <div class="subtitle">
    AI-powered analysis of narrative risk signals across SEC 10-K and 10-Q filings,
    enabling structured comparison, trend detection, and evidence-based insights.
    </div>
    """,
    unsafe_allow_html=True
)

portfolio_df = pd.read_csv("portfolio_risk_comparison.csv")

risk_columns = ["regulation", "financial", "market", "operations", "technology"]

keyword_map = {
    "regulation": ["regulation", "regulatory", "compliance", "legal", "sanctions"],
    "financial": ["liquidity", "debt", "cash flow", "revenue", "costs"],
    "market": ["competition", "demand", "decline", "market"],
    "operations": ["supply chain", "disruption", "operations", "shortage"],
    "technology": ["cybersecurity", "data breach", "system failure", "technology"]
}

def build_risk_dict(row):
    return {col: int(row[col]) for col in risk_columns}

def risk_level(value):
    value = abs(int(value))
    if value >= 50:
        return "High"
    elif value >= 15:
        return "Medium"
    elif value > 0:
        return "Low"
    return "No material change"

def filing_folder(filing_type):
    return filing_type.replace("-", "")

def extract_text_from_file(file_path):
    if not os.path.exists(file_path):
        return ""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "ix:nonfraction", "ix:nonnumeric"]):
        tag.extract()

    text = soup.get_text(separator=" ")
    text = " ".join(text.split())
    return text

def get_positions(lower_text):
    positions = []
    start = 0

    while True:
        position = lower_text.find("risk factors", start)
        if position == -1:
            break
        positions.append(position)
        start = position + 1

    return positions

def extract_risk_factors_section(clean_text):
    lower_text = clean_text.lower()
    positions = get_positions(lower_text)

    if len(positions) >= 3:
        start = positions[1]
        end = positions[2]
    elif len(positions) >= 2:
        start = positions[1]
        end = start + 50000
    elif len(positions) == 1:
        start = positions[0]
        end = start + 50000
    else:
        return ""

    return clean_text[start:end]

def extract_evidence_snippets(file_name, filing_type, risk_category, max_paragraphs=8):
    folder = filing_folder(filing_type)
    file_path = os.path.join("data", folder, file_name)

    clean_text = extract_text_from_file(file_path)
    risk_text = extract_risk_factors_section(clean_text)

    if not risk_text:
        return ["No Risk Factors section found for this filing."]

    paragraphs = re.split(r"(?<=[.!?])\s+", risk_text)
    keywords = keyword_map.get(risk_category, [risk_category])

    results = []

    for paragraph in paragraphs:
        paragraph_lower = paragraph.lower()

        if any(keyword.lower() in paragraph_lower for keyword in keywords):
            results.append(paragraph.strip())

        if len(results) >= max_paragraphs:
            break

    return results if results else ["No direct evidence snippet found for this risk category."]

def highlight_keywords(text, risk_category):
    keywords = keyword_map.get(risk_category, [risk_category])
    highlighted_text = text

    for keyword in keywords:
        highlighted_text = re.sub(
            f"({re.escape(keyword)})",
            r"<mark>\1</mark>",
            highlighted_text,
            flags=re.IGNORECASE
        )

    return highlighted_text

def build_single_insight(company, row, risk_change):
    top_increase = row["top_increase"]
    top_decrease = row["top_decrease"]

    increase_value = risk_change[top_increase]
    decrease_value = risk_change[top_decrease]

    filing_context = (
        "annual structural disclosure shift"
        if row["filing_type"] == "10-K"
        else "quarterly short-term disclosure shift"
    )

    return f"""
<div class="insight-box">

### Agent Insight

**Key finding:**  
For **{company}**, this {filing_context} shows the strongest increase in **{top_increase} risk** from **{row['older_year']} to {row['newer_year']}**.

**Risk interpretation:**  
The **{top_increase}** category changed by **{increase_value}** keyword references. This may reflect greater disclosure emphasis, external pressure, company-specific exposure, or more cautious filing language.

**Largest decrease:**  
The largest decline is in **{top_decrease} risk**, changing by **{decrease_value}** keyword references.

**Signal strength:**  
**{risk_level(increase_value)}**

**Recommended human review:**  
1. Review the evidence snippets below.  
2. Compare wording with the prior filing.  
3. Validate the signal with financial metrics, market context, and external news.

</div>
"""

def build_comparison_insight(company_a, row_a, risk_a, company_b, row_b, risk_b):
    top_a = row_a["top_increase"]
    top_b = row_b["top_increase"]

    value_a = risk_a[top_a]
    value_b = risk_b[top_b]

    stronger_company = company_a if value_a >= value_b else company_b
    stronger_risk = top_a if value_a >= value_b else top_b
    stronger_value = max(value_a, value_b)

    return f"""
<div class="insight-box">

### Agent Insight

**Key finding:**  
The stronger upward narrative signal appears in **{stronger_company}**, led by **{stronger_risk} risk** with a change of **{stronger_value}** keyword references.

**Company A — {company_a}:**  
From **{row_a['older_year']} to {row_a['newer_year']}** in **{row_a['filing_type']}**, the largest increase is **{top_a} risk**.

**Company B — {company_b}:**  
From **{row_b['older_year']} to {row_b['newer_year']}** in **{row_b['filing_type']}**, the largest increase is **{top_b} risk**.

**Interpretation:**  
This does not prove one company is objectively riskier. It identifies where each company’s risk narrative changed most strongly.

**Recommended human review:**  
Review the evidence snippets and determine whether the changes reflect company-specific exposure, industry-wide pressure, or filing-period changes.

</div>
"""

def make_single_report_text(company, row, risk_change):
    return f"""
Lumen Credit Risk Agent Report

Company: {company}
Filing Type: {row['filing_type']}
Period: {row['older_year']} → {row['newer_year']}

Risk Change:
{risk_change}

Top Increase: {row['top_increase']}
Top Decrease: {row['top_decrease']}
Signal Strength: {risk_level(risk_change[row['top_increase']])}

Agent Interpretation:
The strongest narrative increase is in {row['top_increase']} risk. This should be treated as an early screening signal and validated through human review.
"""

def make_comparison_report_text(company_a, row_a, risk_a, company_b, row_b, risk_b):
    return f"""
Lumen Company Comparison Report

Company A: {company_a}
Filing Type A: {row_a['filing_type']}
Period A: {row_a['older_year']} → {row_a['newer_year']}
Risk Change A:
{risk_a}

Top Increase A: {row_a['top_increase']}
Top Decrease A: {row_a['top_decrease']}

Company B: {company_b}
Filing Type B: {row_b['filing_type']}
Period B: {row_b['older_year']} → {row_b['newer_year']}
Risk Change B:
{risk_b}

Top Increase B: {row_b['top_increase']}
Top Decrease B: {row_b['top_decrease']}

Agent Interpretation:
This comparison highlights narrative risk changes across two selected company-period pairs. It should be used as a screening signal before deeper human review.
"""

st.sidebar.title("Control Panel")

filing_type_filter = st.sidebar.selectbox(
    "Filing Type",
    sorted(portfolio_df["filing_type"].unique())
)

selected_signal = st.sidebar.selectbox(
    "Focus Risk Category",
    risk_columns
)

min_year = int(portfolio_df["older_year"].min())
max_year = int(portfolio_df["newer_year"].max())

year_range = st.sidebar.slider(
    "Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

filtered_df = portfolio_df[
    (portfolio_df["filing_type"] == filing_type_filter) &
    (portfolio_df["older_year"] >= year_range[0]) &
    (portfolio_df["newer_year"] <= year_range[1])
]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Filing Type", filing_type_filter)
col2.metric("Companies Covered", filtered_df["company"].nunique())
col3.metric("Total Comparisons", len(filtered_df))
col4.metric(
    f"Largest {selected_signal} Increase",
    int(filtered_df[selected_signal].max()) if not filtered_df.empty else 0
)

tab1, tab2, tab3 = st.tabs([
    "Portfolio Dashboard",
    "Single Filing Review",
    "Company Comparison"
])

with tab1:
    st.subheader("Portfolio-Level Signal Summary")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("#### Risk Signal Distribution")
            st.bar_chart(filtered_df["top_increase"].value_counts())

        with right:
            st.markdown(f"#### Top {selected_signal.title()} Risk Increases")
            st.dataframe(
                filtered_df.sort_values(selected_signal, ascending=False).head(10),
                use_container_width=True
            )

        st.markdown("#### Full Portfolio Table")
        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            label="Export Portfolio CSV",
            data=filtered_df.to_csv(index=False),
            file_name=f"lumen_{filing_type_filter}_portfolio_risk_summary.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("Single Company Report")

    if filtered_df.empty:
        st.warning("No data available.")
    else:
        companies = sorted(filtered_df["company"].unique())

        selected_company = st.selectbox(
            "Select Company",
            companies,
            key="single_company"
        )

        company_df = filtered_df[filtered_df["company"] == selected_company]

        selected_row = st.selectbox(
            "Select Period",
            company_df.index,
            format_func=lambda i: f"{company_df.loc[i, 'older_year']} → {company_df.loc[i, 'newer_year']}",
            key="single_period"
        )

        row = filtered_df.loc[selected_row]
        risk_change = build_risk_dict(row)

        c1, c2, c3 = st.columns(3)
        c1.metric("Top Increase", row["top_increase"], risk_change[row["top_increase"]])
        c2.metric("Top Decrease", row["top_decrease"], risk_change[row["top_decrease"]])
        c3.metric("Signal Strength", risk_level(risk_change[row["top_increase"]]))

        st.markdown("#### Risk Change Chart")
        st.bar_chart(risk_change)

        st.markdown(build_single_insight(selected_company, row, risk_change), unsafe_allow_html=True)

        st.markdown("#### Evidence View")
        snippets = extract_evidence_snippets(
            row["newer_file"],
            row["filing_type"],
            row["top_increase"]
        )

        for i, snippet in enumerate(snippets, 1):
            with st.expander(f"Evidence Snippet {i} — {row['top_increase']} risk"):
                st.markdown(
                    highlight_keywords(snippet, row["top_increase"]),
                    unsafe_allow_html=True
                )

        report_text = make_single_report_text(selected_company, row, risk_change)

        st.markdown("#### Exportable Report")
        st.text(report_text)

        st.download_button(
            label="Export Single Company Report",
            data=report_text,
            file_name=f"{selected_company}_{filing_type_filter}_risk_report.txt",
            mime="text/plain"
        )

with tab3:
    st.subheader("Company A vs Company B")

    if filtered_df.empty:
        st.warning("No data available.")
    else:
        companies = sorted(filtered_df["company"].unique())

        left, right = st.columns(2)

        with left:
            company_a = st.selectbox("Company A", companies, key="company_a")
            company_a_df = filtered_df[filtered_df["company"] == company_a]

            row_a_index = st.selectbox(
                "Company A Period",
                company_a_df.index,
                format_func=lambda i: f"{company_a_df.loc[i, 'older_year']} → {company_a_df.loc[i, 'newer_year']}",
                key="period_a"
            )

        with right:
            company_b = st.selectbox("Company B", companies, key="company_b")
            company_b_df = filtered_df[filtered_df["company"] == company_b]

            row_b_index = st.selectbox(
                "Company B Period",
                company_b_df.index,
                format_func=lambda i: f"{company_b_df.loc[i, 'older_year']} → {company_b_df.loc[i, 'newer_year']}",
                key="period_b"
            )

        row_a = filtered_df.loc[row_a_index]
        row_b = filtered_df.loc[row_b_index]

        risk_a = build_risk_dict(row_a)
        risk_b = build_risk_dict(row_b)

        c1, c2, c3 = st.columns(3)
        c1.metric(f"{company_a} Top Increase", row_a["top_increase"], risk_a[row_a["top_increase"]])
        c2.metric(f"{company_b} Top Increase", row_b["top_increase"], risk_b[row_b["top_increase"]])
        c3.metric(
            "Stronger Signal",
            company_a if risk_a[row_a["top_increase"]] >= risk_b[row_b["top_increase"]] else company_b
        )

        comparison_chart_df = pd.DataFrame({
            f"{company_a} {row_a['older_year']}→{row_a['newer_year']}": risk_a,
            f"{company_b} {row_b['older_year']}→{row_b['newer_year']}": risk_b
        })

        st.markdown("#### Side-by-Side Risk Change")
        st.bar_chart(comparison_chart_df)

        st.markdown(
            build_comparison_insight(company_a, row_a, risk_a, company_b, row_b, risk_b),
            unsafe_allow_html=True
        )

        st.markdown("#### Evidence View")

        ev1, ev2 = st.columns(2)

        with ev1:
            st.markdown(f"**{company_a} evidence — {row_a['top_increase']} risk**")
            snippets_a = extract_evidence_snippets(
                row_a["newer_file"],
                row_a["filing_type"],
                row_a["top_increase"]
            )

            for i, snippet in enumerate(snippets_a, 1):
                with st.expander(f"{company_a} Evidence {i}"):
                    st.markdown(
                        highlight_keywords(snippet, row_a["top_increase"]),
                        unsafe_allow_html=True
                    )

        with ev2:
            st.markdown(f"**{company_b} evidence — {row_b['top_increase']} risk**")
            snippets_b = extract_evidence_snippets(
                row_b["newer_file"],
                row_b["filing_type"],
                row_b["top_increase"]
            )

            for i, snippet in enumerate(snippets_b, 1):
                with st.expander(f"{company_b} Evidence {i}"):
                    st.markdown(
                        highlight_keywords(snippet, row_b["top_increase"]),
                        unsafe_allow_html=True
                    )

        report_text = make_comparison_report_text(company_a, row_a, risk_a, company_b, row_b, risk_b)

        st.markdown("#### Exportable Comparison Report")
        st.text(report_text)

        st.download_button(
            label="Export Comparison Report",
            data=report_text,
            file_name=f"{company_a}_vs_{company_b}_{filing_type_filter}_comparison_report.txt",
            mime="text/plain"
        )