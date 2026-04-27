import os
import re
import html
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Lumen Financial Risk Agent", layout="wide")

theme_options = {
    "White": {
        "accent": "#111827",
        "background": "#ffffff",
        "card": "#ffffff",
        "text": "#111827",
    },
    "Navy": {
        "accent": "#1F4E79",
        "background": "#eef5fb",
        "card": "#ffffff",
        "text": "#111827",
    },
    "Green": {
        "accent": "#047857",
        "background": "#ecfdf5",
        "card": "#ffffff",
        "text": "#111827",
    },
    "Purple": {
        "accent": "#6D28D9",
        "background": "#f5f3ff",
        "card": "#ffffff",
        "text": "#111827",
    },
    "Burgundy": {
        "accent": "#9F1239",
        "background": "#fff1f2",
        "card": "#ffffff",
        "text": "#111827",
    },
    "Gold": {
        "accent": "#B7791F",
        "background": "#fffbeb",
        "card": "#ffffff",
        "text": "#111827",
    },
    "Dark": {
        "accent": "#60A5FA",
        "background": "#0f172a",
        "card": "#1e293b",
        "text": "#f1f5f9",
    },
}

selected_theme = st.sidebar.selectbox("Choose Theme", list(theme_options.keys()))

theme = theme_options[selected_theme]
theme_color = theme["accent"]
page_background = theme["background"]
card_background = theme["card"]
text_color = theme["text"]
secondary_chart_color = "#64748b" if selected_theme == "Dark" else "#9ca3af"
grid_color = "#334155" if selected_theme == "Dark" else "#e5e7eb"
legend_bg = "#0f172a" if selected_theme == "Dark" else "#ffffff"

st.markdown(
    f"""
<style>
.stApp {{
    background-color: {page_background};
    color: {text_color};
}}

header[data-testid="stHeader"] {{
    background-color: {page_background} !important;
}}

section[data-testid="stSidebar"] {{
    background-color: {page_background} !important;
}}

section[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: {card_background} !important;
    color: {text_color} !important;
    border: 1px solid {"#334155" if selected_theme == "Dark" else "#d1d5db"} !important;
}}

.block-container {{
    padding-top: 2rem;
}}

.main-title {{
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
    color: {"#f8fafc" if selected_theme == "Dark" else theme_color};
}}

.subtitle {{
    color: {"#cbd5e1" if selected_theme == "Dark" else "#667085"};
    font-size: 1.05rem;
    margin-bottom: 1.5rem;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {"#f8fafc" if selected_theme == "Dark" else "#111827"} !important;
}}

p, div, span, label {{
    color: {"#e5e7eb" if selected_theme == "Dark" else "#111827"};
}}

[data-testid="stMarkdownContainer"] {{
    color: {"#e5e7eb" if selected_theme == "Dark" else "#111827"} !important;
}}

[data-testid="stMetric"] {{
    background: {card_background};
    padding: 18px;
    border-radius: 14px;
    border: 1px solid {"#334155" if selected_theme == "Dark" else "#e6e8eb"};
    box-shadow: 0 1px 6px rgba(16, 24, 40, 0.04);
}}

[data-testid="stMetric"] label {{
    color: {"#cbd5e1" if selected_theme == "Dark" else "#667085"} !important;
}}

[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {"#f8fafc" if selected_theme == "Dark" else "#111827"} !important;
}}

.insight-box {{
    background: {card_background};
    color: {"#e5e7eb" if selected_theme == "Dark" else "#111827"};
    border-left: 5px solid {theme_color};
    border-radius: 14px;
    padding: 1.2rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 6px rgba(16, 24, 40, 0.04);
}}

.stTabs [data-baseweb="tab"] {{
    color: {"#cbd5e1" if selected_theme == "Dark" else "#667085"} !important;
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    color: {theme_color} !important;
    border-bottom: 3px solid {theme_color};
}}

.stDownloadButton button {{
    background-color: {card_background} !important;
    border-color: {theme_color} !important;
    color: {theme_color} !important;
    border-radius: 10px;
    font-weight: 600;
}}

div[data-baseweb="select"] > div {{
    background-color: {card_background} !important;
    color: {text_color} !important;
    border: 1px solid {"#334155" if selected_theme == "Dark" else "#d1d5db"} !important;
}}

div[data-baseweb="select"] span {{
    color: {text_color} !important;
}}

div[data-baseweb="popover"], div[data-baseweb="popover"] * {{
    background-color: {card_background} !important;
    color: {text_color} !important;
}}

ul[role="listbox"], ul[role="listbox"] li {{
    background-color: {card_background} !important;
    color: {text_color} !important;
}}

ul[role="listbox"] li:hover {{
    background-color: {theme_color} !important;
    color: {"#0f172a" if selected_theme == "Dark" else "#ffffff"} !important;
}}

mark {{
    background-color: #fff3b0;
    color: #111827;
    padding: 2px 4px;
    border-radius: 4px;
}}

.report-box {{
    background-color: {card_background};
    color: {text_color};
    border: 1px solid {"#334155" if selected_theme == "Dark" else "#d1d5db"};
    border-radius: 14px;
    padding: 22px;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1rem;
    line-height: 1.7;
    white-space: pre-wrap;
}}

div[data-baseweb="select"] input {{
    color: {text_color} !important;
    -webkit-text-fill-color: {text_color} !important;
}}

div[data-baseweb="select"] input::placeholder {{
    color: {"#94a3b8" if selected_theme == "Dark" else "#6b7280"} !important;
}}

details[data-testid="stExpander"] summary {{
    background-color: {card_background} !important;
    color: {text_color} !important;
}}

details[data-testid="stExpander"] summary:hover {{
    background-color: {"#1e293b" if selected_theme == "Dark" else "#f8fafc"} !important;
    color: {text_color} !important;
}}

details[data-testid="stExpander"] summary * {{
    color: {text_color} !important;
}}


div[data-testid="stExpander"] details {{
    background-color: {card_background} !important;
    border: 1px solid {"#334155" if selected_theme == "Dark" else "#d1d5db"} !important;
    border-radius: 12px !important;
}}

div[data-testid="stExpander"] summary {{
    background-color: {card_background} !important;
    color: {text_color} !important;
    border-radius: 12px 12px 0 0 !important;
}}

div[data-testid="stExpander"] summary:hover {{
    background-color: {"#1e293b" if selected_theme == "Dark" else "#f3f4f6"} !important;
    color: {text_color} !important;
}}

div[data-testid="stExpander"] summary * {{
    color: {text_color} !important;
}}

div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] {{
    color: {text_color} !important;
}}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-title">Lumen Financial Risk Agent</div>
    <div class="subtitle">
    AI-powered analysis of narrative risk signals across SEC 10-K and 10-Q filings,
    enabling structured comparison, trend detection, and evidence-based insights.
    </div>
    """,
    unsafe_allow_html=True,
)

df_10k = pd.read_csv("portfolio_10k.csv")
df_10q = pd.read_csv("portfolio_10q.csv")

risk_columns = ["regulation", "financial", "market", "operations", "technology"]

keyword_map = {
    "regulation": ["regulation", "regulatory", "compliance", "legal", "sanctions"],
    "financial": ["liquidity", "debt", "cash flow", "revenue", "costs"],
    "market": ["competition", "demand", "decline", "market"],
    "operations": ["supply chain", "disruption", "operations", "shortage"],
    "technology": ["cybersecurity", "data breach", "system failure", "technology"],
}


def update_chart_layout(fig, title, df, y_col):
    fig.update_layout(
        title=dict(text=title, font=dict(color=text_color, size=20)),
        plot_bgcolor=page_background,
        paper_bgcolor=page_background,
        font=dict(color=text_color),
        xaxis=dict(color=text_color, gridcolor=grid_color, zerolinecolor=grid_color),
        yaxis=dict(color=text_color, gridcolor=grid_color, zerolinecolor=grid_color),
        legend=dict(
            font=dict(color=text_color),
            bgcolor=legend_bg,
            bordercolor=grid_color,
            borderwidth=1,
        ),
    )

    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8")

    fig.update_yaxes(range=[min(df[y_col].min(), -1), max(df[y_col].max(), 1)])

    return fig


def themed_risk_chart(data_dict, title="Risk Change", chart_type="Bar Chart"):
    chart_df = pd.DataFrame(
        {"Risk Category": list(data_dict.keys()), "Change": list(data_dict.values())}
    )

    if chart_type == "Line Chart":
        fig = px.line(chart_df, x="Risk Category", y="Change", markers=True)
        fig.update_traces(
            line_color=theme_color,
            marker_color=theme_color,
            text=chart_df["Change"],
            textposition="top center",
        )
    else:
        fig = px.bar(
            chart_df,
            x="Risk Category",
            y="Change",
            text="Change",
            color="Risk Category",
            color_discrete_sequence=[theme_color] * len(chart_df),
        )
        fig.update_traces(textposition="outside", cliponaxis=False)

    fig = update_chart_layout(fig, title, chart_df, "Change")
    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)
    st.caption("A value of 0 means no detected change, not missing data.")


def themed_count_chart(series, title="Risk Signal Distribution"):
    chart_df = series.reset_index()
    chart_df.columns = ["Risk Category", "Count"]

    fig = px.bar(
        chart_df,
        x="Risk Category",
        y="Count",
        text="Count",
        color="Risk Category",
        color_discrete_sequence=[theme_color] * len(chart_df),
    )

    fig.update_traces(textposition="outside", cliponaxis=False)

    fig.update_layout(
        title=title,
        plot_bgcolor=page_background,
        paper_bgcolor=page_background,
        font_color=text_color,
        xaxis=dict(color=text_color),
        yaxis=dict(color=text_color),
        showlegend=False,
    )

    fig.update_yaxes(
        range=[min(chart_df["Count"].min(), 0), max(chart_df["Count"].max(), 1)]
    )

    st.plotly_chart(fig, use_container_width=True)


def themed_comparison_chart(comparison_chart_df, chart_type="Bar Chart"):
    df = (
        comparison_chart_df.reset_index()
        .melt(id_vars="index", var_name="Company Period", value_name="Change")
        .rename(columns={"index": "Risk Category"})
    )

    if chart_type == "Line Chart":
        fig = px.line(
            df,
            x="Risk Category",
            y="Change",
            color="Company Period",
            markers=True,
            color_discrete_sequence=[theme_color, secondary_chart_color],
        )
    else:
        fig = px.bar(
            df,
            x="Risk Category",
            y="Change",
            color="Company Period",
            barmode="group",
            text="Change",
            color_discrete_sequence=[theme_color, secondary_chart_color],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)

    fig = update_chart_layout(fig, "Side-by-Side Risk Change", df, "Change")

    st.plotly_chart(fig, use_container_width=True)
    st.caption("A value of 0 means no detected change, not missing data.")


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


def extract_date(file_name):
    parts = file_name.split("_")
    for part in parts:
        if part.startswith("20"):
            return part[:10]
    return "Unknown"


def display_period_label(row):
    return f"{extract_date(row['older_file'])} → {extract_date(row['newer_file'])}"


def extract_text_from_file(file_path):
    if not os.path.exists(file_path):
        return ""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html_text = f.read()

    soup = BeautifulSoup(html_text, "html.parser")

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

    return (
        results
        if results
        else ["No direct evidence snippet found for this risk category."]
    )


def highlight_keywords(text, risk_category):
    keywords = keyword_map.get(risk_category, [risk_category])
    highlighted_text = text

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"

        highlighted_text = re.sub(
            pattern, r"<mark>\g<0></mark>", highlighted_text, flags=re.IGNORECASE
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
Lumen Financial Risk Agent Report

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
Lumen Financial Risk Agent Comparison Report

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

filing_type_filter = st.sidebar.selectbox("Filing Type", ["10-K", "10-Q"])

if filing_type_filter == "10-K":
    portfolio_df = df_10k
else:
    portfolio_df = df_10q

selected_signal = st.sidebar.selectbox("Focus Risk Category", risk_columns)

min_year = int(portfolio_df["older_year"].min())
max_year = int(portfolio_df["newer_year"].max())

year_range = st.sidebar.slider("Year Range", min_year, max_year, (min_year, max_year))

filtered_df = portfolio_df[
    (portfolio_df["filing_type"] == filing_type_filter)
    & (portfolio_df["older_year"] >= year_range[0])
    & (portfolio_df["newer_year"] <= year_range[1])
]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Filing Type", filing_type_filter)
col2.metric("Companies Covered", filtered_df["company"].nunique())
col3.metric("Total Comparisons", len(filtered_df))
col4.metric(
    f"Largest {selected_signal} Increase",
    int(filtered_df[selected_signal].max()) if not filtered_df.empty else 0,
)

tab1, tab2, tab3 = st.tabs(
    ["Portfolio Dashboard", "Single Filing Review", "Company Comparison"]
)

with tab1:
    st.subheader("Portfolio-Level Signal Summary")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("#### Risk Signal Distribution")
            themed_count_chart(filtered_df["top_increase"].value_counts())

        with right:
            st.markdown(f"#### Top {selected_signal.title()} Risk Increases")
            st.dataframe(
                filtered_df.sort_values(selected_signal, ascending=False).head(10),
                use_container_width=True,
            )

        st.markdown("#### Full Portfolio Table")
        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            label="Export Portfolio CSV",
            data=filtered_df.to_csv(index=False),
            file_name=f"lumen_{filing_type_filter}_portfolio_risk_summary.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("Single Company Report")

    if filtered_df.empty:
        st.warning("No data available.")
    else:
        companies = sorted(filtered_df["company"].unique())

        selected_company = st.selectbox(
            "Select Company (type to search)", companies, key="single_company"
        )

        company_df = filtered_df[filtered_df["company"] == selected_company]
        period_options = list(company_df.index)

        from_row = st.selectbox(
            "From Period",
            period_options,
            format_func=lambda i: display_period_label(company_df.loc[i]),
            key="tab2_from_period",
        )

        to_row = st.selectbox(
            "To Period",
            period_options,
            index=len(period_options) - 1,
            format_func=lambda i: display_period_label(company_df.loc[i]),
            key="tab2_to_period",
        )

        start_pos = period_options.index(from_row)
        end_pos = period_options.index(to_row)

        if start_pos > end_pos:
            st.warning("From Period should be earlier than To Period.")
            st.stop()

        selected_rows = company_df.loc[period_options[start_pos : end_pos + 1]]
        risk_change = {col: int(selected_rows[col].sum()) for col in risk_columns}
        row = selected_rows.iloc[-1]

        c1, c2, c3 = st.columns(3)
        c1.metric("Top Increase", row["top_increase"], risk_change[row["top_increase"]])
        c2.metric("Top Decrease", row["top_decrease"], risk_change[row["top_decrease"]])
        c3.metric("Signal Strength", risk_level(risk_change[row["top_increase"]]))

        st.markdown("#### Risk Change Chart")

        single_chart_type = st.radio(
            "Choose Chart Type",
            ["Bar Chart", "Line Chart"],
            horizontal=True,
            key="tab2_chart_type",
        )

        if len(selected_rows) == 1:
            themed_risk_chart(risk_change, "Risk Change Chart", single_chart_type)
        else:
            multi_period_df = selected_rows[
                ["older_year", "newer_year"] + risk_columns
            ].copy()

            multi_period_df["Period"] = (
                multi_period_df["older_year"].astype(str)
                + " → "
                + multi_period_df["newer_year"].astype(str)
            )

            chart_df = multi_period_df.melt(
                id_vars="Period",
                value_vars=risk_columns,
                var_name="Risk Category",
                value_name="Change",
            )

            if single_chart_type == "Line Chart":
                fig = px.line(
                    chart_df,
                    x="Period",
                    y="Change",
                    color="Risk Category",
                    markers=True,
                )
            else:
                fig = px.bar(
                    chart_df,
                    x="Risk Category",
                    y="Change",
                    color="Period",
                    barmode="group",
                    text="Change",
                )
                fig.update_traces(textposition="outside", cliponaxis=False)

            fig = update_chart_layout(
                fig, "Multi-Period Risk Change", chart_df, "Change"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("A value of 0 means no detected change, not missing data.")

        st.markdown(
            build_single_insight(selected_company, row, risk_change),
            unsafe_allow_html=True,
        )

        st.markdown("#### Evidence View")
        snippets = extract_evidence_snippets(
            row["newer_file"], row["filing_type"], row["top_increase"]
        )

        for i, snippet in enumerate(snippets, 1):
            with st.expander(f"Evidence Snippet {i} — {row['top_increase']} risk"):
                st.markdown(
                    highlight_keywords(snippet, row["top_increase"]),
                    unsafe_allow_html=True,
                )

        report_text = make_single_report_text(selected_company, row, risk_change)

        st.markdown("#### Exportable Report")
        report_class = "report-box"

        st.markdown(
            f'<div class="{report_class}">{report_text}</div>', unsafe_allow_html=True
        )

        st.download_button(
            label="Export Single Company Report",
            data=report_text,
            file_name=f"{selected_company}_{filing_type_filter}_risk_report.txt",
            mime="text/plain",
        )


with tab3:
    st.subheader("Company A vs Company B")

    if filtered_df.empty:
        st.warning("No data available.")
    else:
        companies = sorted(filtered_df["company"].unique())

        left, right = st.columns(2)

        with left:
            company_a = st.selectbox(
                "Company A (type to search)", companies, key="company_a"
            )

            company_a_df = filtered_df[filtered_df["company"] == company_a]

            row_a_index = st.selectbox(
                "Company A Period",
                company_a_df.index,
                format_func=lambda i: display_period_label(company_a_df.loc[i]),
                key="period_a",
            )

        with right:
            company_b = st.selectbox(
                "Company B (type to search)", companies, key="company_b"
            )

            company_b_df = filtered_df[filtered_df["company"] == company_b]

            row_b_index = st.selectbox(
                "Company B Period",
                company_b_df.index,
                format_func=lambda i: display_period_label(company_b_df.loc[i]),
                key="period_b",
            )

        row_a = company_a_df.loc[row_a_index]
        row_b = company_b_df.loc[row_b_index]

        risk_a = build_risk_dict(row_a)
        risk_b = build_risk_dict(row_b)

        c1, c2, c3 = st.columns(3)
        c1.metric(
            f"{company_a} Top Increase",
            row_a["top_increase"],
            risk_a[row_a["top_increase"]],
        )
        c2.metric(
            f"{company_b} Top Increase",
            row_b["top_increase"],
            risk_b[row_b["top_increase"]],
        )
        c3.metric(
            "Stronger Signal",
            (
                company_a
                if risk_a[row_a["top_increase"]] >= risk_b[row_b["top_increase"]]
                else company_b
            ),
        )

        comparison_chart_df = pd.DataFrame(
            {
                f"{company_a} {display_period_label(row_a)}": risk_a,
                f"{company_b} {display_period_label(row_b)}": risk_b,
            }
        )

        st.markdown("#### Side-by-Side Risk Change")

        comparison_chart_type = st.radio(
            "Choose Comparison Chart Type",
            ["Bar Chart", "Radar Chart", "Difference Chart", "Heatmap"],
            horizontal=True,
            key="comparison_chart_type",
        )

        if comparison_chart_type == "Bar Chart":
            themed_comparison_chart(comparison_chart_df, "Bar Chart")

        elif comparison_chart_type == "Radar Chart":
            categories = risk_columns

            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=[risk_a[col] for col in categories],
                    theta=categories,
                    fill="toself",
                    name=f"{company_a} {display_period_label(row_a)}",
                    line=dict(color=theme_color, width=3),
                    marker=dict(color=theme_color),
                )
            )

            fig.add_trace(
                go.Scatterpolar(
                    r=[risk_b[col] for col in categories],
                    theta=categories,
                    fill="toself",
                    name=f"{company_b} {display_period_label(row_b)}",
                    line=dict(color=secondary_chart_color, width=3),
                    marker=dict(color=secondary_chart_color),
                )
            )

            fig.update_layout(
                title=dict(
                    text="Risk Structure Radar View",
                    font=dict(color=text_color, size=20),
                ),
                paper_bgcolor=page_background,
                plot_bgcolor=page_background,
                font=dict(color=text_color),
                polar=dict(
                    bgcolor=page_background,
                    radialaxis=dict(
                        visible=True,
                        color=text_color,
                        gridcolor=grid_color,
                        tickfont=dict(color=text_color),
                    ),
                    angularaxis=dict(
                        color=text_color,
                        gridcolor=grid_color,
                        tickfont=dict(color=text_color),
                    ),
                ),
                legend=dict(
                    font=dict(color=text_color),
                    bgcolor=legend_bg,
                    bordercolor=grid_color,
                    borderwidth=1,
                ),
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

        elif comparison_chart_type == "Difference Chart":
            diff = {col: risk_a[col] - risk_b[col] for col in risk_columns}

            diff_df = pd.DataFrame(
                {
                    "Risk Category": list(diff.keys()),
                    "Difference": list(diff.values()),
                }
            )

            fig = px.bar(
                diff_df,
                x="Risk Category",
                y="Difference",
                text="Difference",
                color="Difference",
                color_continuous_scale="RdBu",
            )

            fig.update_traces(textposition="outside", cliponaxis=False)

            fig.update_layout(
                title=dict(
                    text=f"Difference Chart: {company_a} minus {company_b}",
                    font=dict(color=text_color, size=20),
                ),
                plot_bgcolor=page_background,
                paper_bgcolor=page_background,
                font=dict(color=text_color),
                xaxis=dict(
                    color=text_color,
                    gridcolor=grid_color,
                    zerolinecolor=grid_color,
                ),
                yaxis=dict(
                    color=text_color,
                    gridcolor=grid_color,
                    zerolinecolor=grid_color,
                ),
                coloraxis_colorbar=dict(
                    tickfont=dict(color=text_color),
                    title=dict(font=dict(color=text_color)),
                ),
                showlegend=False,
            )

            fig.add_hline(
                y=0,
                line_dash="dash",
                line_color="#94a3b8",
            )

            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                f"Positive values mean {company_a} is higher. Negative values mean {company_b} is higher."
            )

        elif comparison_chart_type == "Heatmap":
            heatmap_df = pd.DataFrame(
                {
                    company_a: risk_a,
                    company_b: risk_b,
                }
            )

            fig = px.imshow(
                heatmap_df,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
            )

            fig.update_layout(
                title=dict(
                    text="Risk Signal Heatmap",
                    font=dict(color=text_color, size=20),
                ),
                paper_bgcolor=page_background,
                plot_bgcolor=page_background,
                font=dict(color=text_color),
                xaxis=dict(
                    color=text_color,
                    tickfont=dict(color=text_color),
                ),
                yaxis=dict(
                    color=text_color,
                    tickfont=dict(color=text_color),
                ),
                coloraxis_colorbar=dict(
                    tickfont=dict(color=text_color),
                    title=dict(font=dict(color=text_color)),
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            build_comparison_insight(
                company_a, row_a, risk_a, company_b, row_b, risk_b
            ),
            unsafe_allow_html=True,
        )

        st.markdown("#### Evidence View")

        ev1, ev2 = st.columns(2)

        with ev1:
            st.markdown(f"**{company_a} evidence — {row_a['top_increase']} risk**")
            snippets_a = extract_evidence_snippets(
                row_a["newer_file"],
                row_a["filing_type"],
                row_a["top_increase"],
            )

            for i, snippet in enumerate(snippets_a, 1):
                with st.expander(f"{company_a} Evidence {i}"):
                    st.markdown(
                        highlight_keywords(snippet, row_a["top_increase"]),
                        unsafe_allow_html=True,
                    )

        with ev2:
            st.markdown(f"**{company_b} evidence — {row_b['top_increase']} risk**")
            snippets_b = extract_evidence_snippets(
                row_b["newer_file"],
                row_b["filing_type"],
                row_b["top_increase"],
            )

            for i, snippet in enumerate(snippets_b, 1):
                with st.expander(f"{company_b} Evidence {i}"):
                    st.markdown(
                        highlight_keywords(snippet, row_b["top_increase"]),
                        unsafe_allow_html=True,
                    )

        report_text = make_comparison_report_text(
            company_a, row_a, risk_a, company_b, row_b, risk_b
        )

        st.markdown("#### Exportable Comparison Report")
        report_class = "report-box"

        st.markdown(
            f'<div class="{report_class}">{report_text}</div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            label="Export Comparison Report",
            data=report_text,
            file_name=f"{company_a}_vs_{company_b}_{filing_type_filter}_comparison_report.txt",
            mime="text/plain",
        )
