import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lumen Credit Risk Agent", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    font-size: 2.6rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    font-weight: 700 !important;
}

[data-testid="stMetric"] {
    background-color: #f7f8fa;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e6e8eb;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    padding: 12px 20px;
    border-radius: 12px 12px 0 0;
}

.stDownloadButton button {
    border-radius: 10px;
    font-weight: 600;
}

div[data-testid="stMarkdownContainer"] p {
    font-size: 1rem;
    line-height: 1.55;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
# Lumen Credit Risk Agent
AI-powered narrative risk screening for SEC 10-K disclosures.
""")

portfolio_df = pd.read_csv("portfolio_risk_comparison.csv")

risk_columns = ["regulation", "financial", "market", "operations", "technology"]


def build_risk_dict(row):
    return {col: int(row[col]) for col in risk_columns}


def risk_level(value):
    abs_value = abs(value)

    if abs_value >= 50:
        return "High"
    elif abs_value >= 15:
        return "Medium"
    elif abs_value > 0:
        return "Low"
    else:
        return "No material change"


def direction_text(value):
    if value > 0:
        return "increased"
    elif value < 0:
        return "decreased"
    return "remained stable"


def build_single_insight(company, row, risk_change):
    top_increase = row["top_increase"]
    top_decrease = row["top_decrease"]

    top_increase_value = risk_change[top_increase]
    top_decrease_value = risk_change[top_decrease]

    return f"""
### Agent Insight

**Key finding:**  
For **{company}**, the strongest narrative increase from **{row['older_year']} to {row['newer_year']}** is in **{top_increase} risk**.

**Risk interpretation:**  
The **{top_increase}** category {direction_text(top_increase_value)} by **{top_increase_value}** keyword references.  
This suggests that the company may be placing greater disclosure emphasis on this risk area. The change may reflect new external pressure, operational exposure, regulatory developments, or more cautious filing language.

**Largest decrease:**  
The largest decline is in **{top_decrease} risk**, changing by **{top_decrease_value}** keyword references.  
This may indicate reduced emphasis, stabilization, or a shift in management’s disclosure focus.

**Confidence level:**  
**{risk_level(top_increase_value)}**, based on the size of the keyword-count shift.

**Recommended human review:**  
1. Review the full **{top_increase}** risk paragraph in the newer filing.  
2. Compare wording against the prior-year filing.  
3. Check whether financial metrics, news, or industry conditions support the narrative shift.
"""


def build_comparison_insight(company_a, row_a, risk_a, company_b, row_b, risk_b):
    top_a = row_a["top_increase"]
    top_b = row_b["top_increase"]

    max_a_value = risk_a[top_a]
    max_b_value = risk_b[top_b]

    stronger_company = company_a if max_a_value >= max_b_value else company_b
    stronger_risk = top_a if max_a_value >= max_b_value else top_b
    stronger_value = max(max_a_value, max_b_value)

    return f"""
### Agent Insight

**Key finding:**  
The comparison shows that **{stronger_company}** has the stronger upward narrative risk signal, led by **{stronger_risk} risk** with a change of **{stronger_value}** keyword references.

**Company A interpretation — {company_a}:**  
From **{row_a['older_year']} to {row_a['newer_year']}**, the largest increase is **{top_a} risk**.  
This suggests that the filing places more emphasis on **{top_a}**-related exposure than in the prior period.

**Company B interpretation — {company_b}:**  
From **{row_b['older_year']} to {row_b['newer_year']}**, the largest increase is **{top_b} risk**.  
This suggests that the company’s disclosure focus shifted most toward **{top_b}**.

**Cross-company interpretation:**  
This comparison does not prove one company is objectively riskier. It shows where each company’s **risk narrative changed most strongly**.  
A credit analyst should use this as a screening signal before reviewing the original filing language.

**Recommended human review:**  
1. Review the highest-increase category for both companies.  
2. Determine whether the change is company-specific or industry-wide.  
3. Compare the narrative signal with financial metrics and external market conditions.
"""


def build_report_text(company, row, risk_change):
    return f"""
Lumen Credit Risk Agent Report

Company: {company}
Period: {row['older_year']} → {row['newer_year']}

Risk Change:
{risk_change}

Top Increase: {row['top_increase']}
Top Decrease: {row['top_decrease']}

Agent Insight:
For {company}, the strongest narrative increase is in {row['top_increase']} risk. 
The largest narrative decrease is in {row['top_decrease']} risk.

This output should be treated as an early screening signal. A credit analyst should review the original Risk Factors section and validate the signal against financial metrics, industry context, and external news.
"""


def build_comparison_report_text(company_a, row_a, risk_a, company_b, row_b, risk_b):
    return f"""
Lumen Company Comparison Report

Company A: {company_a}
Period A: {row_a['older_year']} → {row_a['newer_year']}
Risk Change A:
{risk_a}

Top Increase A: {row_a['top_increase']}
Top Decrease A: {row_a['top_decrease']}

Company B: {company_b}
Period B: {row_b['older_year']} → {row_b['newer_year']}
Risk Change B:
{risk_b}

Top Increase B: {row_b['top_increase']}
Top Decrease B: {row_b['top_decrease']}

Agent Insight:
This comparison highlights narrative risk changes across two selected company-period pairs. 
It helps analysts identify which risk categories changed most and where deeper review is needed.
"""


tab1, tab2, tab3 = st.tabs([
    "Portfolio Overview",
    "Single Company Report",
    "Company A vs Company B"
])


with tab1:
    st.subheader("Portfolio Risk Comparison")
    st.dataframe(portfolio_df, use_container_width=True)

    st.subheader("Top Regulation Risk Increases")
    st.dataframe(
        portfolio_df.sort_values("regulation", ascending=False).head(10),
        use_container_width=True
    )

    st.subheader("Portfolio-Level Signal Summary")
    signal_counts = portfolio_df["top_increase"].value_counts()
    st.bar_chart(signal_counts)


with tab2:
    companies = sorted(portfolio_df["company"].unique())

    selected_company = st.selectbox("Select Company", companies, key="single_company")
    company_df = portfolio_df[portfolio_df["company"] == selected_company]

    selected_row = st.selectbox(
        "Select Comparison Period",
        company_df.index,
        format_func=lambda i: f"{company_df.loc[i, 'older_year']} → {company_df.loc[i, 'newer_year']}",
        key="single_period"
    )

    row = company_df.loc[selected_row]
    risk_change = build_risk_dict(row)

    st.subheader(f"{selected_company}: {row['older_year']} → {row['newer_year']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Top Increase", row["top_increase"], risk_change[row["top_increase"]])
    col2.metric("Top Decrease", row["top_decrease"], risk_change[row["top_decrease"]])
    col3.metric("Signal Strength", risk_level(risk_change[row["top_increase"]]))

    st.subheader("Risk Change Chart")
    st.bar_chart(risk_change)

    st.markdown(build_single_insight(selected_company, row, risk_change))

    report_text = build_report_text(selected_company, row, risk_change)

    st.subheader("Exportable Report")
    st.text(report_text)

    st.download_button(
        label="Export Report",
        data=report_text,
        file_name=f"{selected_company}_risk_report.txt",
        mime="text/plain"
    )


with tab3:
    companies = sorted(portfolio_df["company"].unique())

    st.subheader("Company A vs Company B Comparison")

    col1, col2 = st.columns(2)

    with col1:
        company_a = st.selectbox("Select Company A", companies, key="company_a")
        company_a_df = portfolio_df[portfolio_df["company"] == company_a]

        row_a_index = st.selectbox(
            "Select Company A Period",
            company_a_df.index,
            format_func=lambda i: f"{company_a_df.loc[i, 'older_year']} → {company_a_df.loc[i, 'newer_year']}",
            key="period_a"
        )

    with col2:
        company_b = st.selectbox("Select Company B", companies, key="company_b")
        company_b_df = portfolio_df[portfolio_df["company"] == company_b]

        row_b_index = st.selectbox(
            "Select Company B Period",
            company_b_df.index,
            format_func=lambda i: f"{company_b_df.loc[i, 'older_year']} → {company_b_df.loc[i, 'newer_year']}",
            key="period_b"
        )

    row_a = portfolio_df.loc[row_a_index]
    row_b = portfolio_df.loc[row_b_index]

    risk_a = build_risk_dict(row_a)
    risk_b = build_risk_dict(row_b)

    st.subheader(f"{company_a} vs {company_b}")

    col1, col2, col3 = st.columns(3)
    col1.metric(f"{company_a} Top Increase", row_a["top_increase"], risk_a[row_a["top_increase"]])
    col2.metric(f"{company_b} Top Increase", row_b["top_increase"], risk_b[row_b["top_increase"]])
    col3.metric(
        "Stronger Signal",
        company_a if risk_a[row_a["top_increase"]] >= risk_b[row_b["top_increase"]] else company_b
    )

    comparison_df = pd.DataFrame({
        f"{company_a} {row_a['older_year']}→{row_a['newer_year']}": risk_a,
        f"{company_b} {row_b['older_year']}→{row_b['newer_year']}": risk_b
    })

    st.subheader("Side-by-Side Risk Change Chart")
    st.bar_chart(comparison_df)

    st.markdown(build_comparison_insight(company_a, row_a, risk_a, company_b, row_b, risk_b))

    report_text = build_comparison_report_text(company_a, row_a, risk_a, company_b, row_b, risk_b)

    st.subheader("Exportable Comparison Report")
    st.text(report_text)

    st.download_button(
        label="Export Comparison Report",
        data=report_text,
        file_name=f"{company_a}_vs_{company_b}_comparison_report.txt",
        mime="text/plain"
    )