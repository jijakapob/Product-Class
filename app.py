from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import streamlit as st


APP_TITLE = "Sales vs GP% Portfolio Dashboard"
DEFAULT_DATA_FILE = Path("data/default_sales_gp.csv")

REQUIRED_COLUMNS = ["Flavor Description", "Size", "Category", "Net Value 6M", "GP%"]

FIELD_LABELS = {
    "Flavor Description": "SKU / Product Name",
    "Size": "Size",
    "Category": "Category",
    "Net Value 6M": "Sales Value",
    "GP%": "GP%",
}

COLUMN_ALIASES = {
    "Flavor Description": [
        "Flavor Description",
        "SKU",
        "SKU Name",
        "Product Name",
        "Product",
        "Item Name",
        "Flavor",
    ],
    "Size": ["Size", "Pack Size", "SKU Size", "Volume", "Pack"],
    "Category": ["Category", "Product Category", "Class", "Product Class", "Segment"],
    "Net Value 6M": [
        "Net Value 6M",
        "Net Sales",
        "Sales",
        "Sales Value",
        "Revenue",
        "Net Value",
        "Value",
    ],
    "GP%": ["GP%", "Gross Profit %", "GP Percent", "Gross Margin %", "Margin %", "GP"],
}

INCLUDED_CATEGORIES = [
    "FJ 100%",
    "VJ 100%",
    "Cool 40%",
    "Super Kid",
    "Squeeze",
    "Aura",
    "Aquare",
    "OEM",
    "OEM - S&P",
    "Essence",
    "FOOD SERVICE TRADE",
    "Consumer product - Food",
]

EXCLUDED_CATEGORIES = [
    "Tipco Play",
    "Less Sweet",
    "Tipco Chewy",
    "Canned Fruit",
    "CEREAL BEVERAGE",
    "Gift set",
    "Herb Product",
]

COLOR_MAP = {
    "FJ 100%": "#1f77b4",
    "VJ 100%": "#17a589",
    "Cool 40%": "#f39c12",
    "Super Kid": "#8e44ad",
    "Squeeze": "#e74c3c",
    "Aura": "#2e86de",
    "Aquare": "#00a8a8",
    "OEM": "#7f8c8d",
    "OEM - S&P": "#34495e",
    "Essence": "#c0392b",
    "FOOD SERVICE TRADE": "#5d6d7e",
    "Consumer product - Food": "#7d6608",
}


st.set_page_config(page_title=APP_TITLE, layout="wide")


def local_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --brand-blue: #12355b;
            --ink: #17202a;
            --muted: #667085;
            --line: #d7dee8;
            --soft: #f6f8fb;
        }
        .main .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: 0;
        }
        div[data-testid="stMetric"] {
            background: #fbfcfe;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        div[data-testid="stMetricLabel"] {
            color: var(--muted);
        }
        div.stButton > button {
            border-radius: 6px;
            border: 1px solid #c8d2df;
            background: #fbfcfe;
            color: #1f2a37;
            font-weight: 600;
            min-height: 36px;
            white-space: normal;
            line-height: 1.15;
        }
        div.stButton > button:hover {
            border-color: #12355b;
            color: #12355b;
            background: #f2f6fb;
        }
        .section-caption, .source-note, .filter-summary {
            color: var(--muted);
            font-size: 0.92rem;
        }
        .section-caption {
            margin-top: -0.55rem;
            margin-bottom: 1rem;
        }
        .filter-summary {
            background: var(--soft);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.72rem 0.9rem;
            margin-bottom: 1rem;
        }
        .filter-summary b {
            color: var(--ink);
        }
        .source-note {
            margin: 0.4rem 0 1rem 0;
        }
        .filter-heading {
            color: var(--ink);
            font-size: 0.94rem;
            font-weight: 800;
            letter-spacing: 0;
            margin: 1.05rem 0 0.35rem 0;
        }
        .filter-help {
            color: var(--muted);
            font-size: 0.8rem;
            margin: -0.1rem 0 0.45rem 0;
        }
        div[data-testid="stElementToolbar"] {
            display: none;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.75rem;
        }
        [data-testid="stBaseButton-pills"],
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-primary"] {
            min-height: 42px;
            border-radius: 999px;
            white-space: normal;
            line-height: 1.15;
        }
        @media (max-width: 700px) {
            .main .block-container {
                padding: 1rem 0.85rem 1.6rem 0.85rem;
            }
            h1 {
                font-size: 2rem;
                line-height: 1.15;
            }
            .section-caption, .filter-summary {
                font-size: 0.88rem;
            }
            .filter-heading {
                font-size: 1rem;
                margin-top: 1.1rem;
            }
            [data-testid="stBaseButton-pills"],
            [data-testid="stBaseButton-secondary"],
            [data-testid="stBaseButton-primary"] {
                min-height: 44px;
                font-size: 0.92rem;
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }
            div[data-testid="stMetric"] {
                padding: 12px 14px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_text(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def normalize_category(value: object) -> str:
    text = str(value).strip()
    text = " ".join(text.split())
    aliases = {
        "OEM- S&P": "OEM - S&P",
        "OEM -S&P": "OEM - S&P",
        "OEM-S&P": "OEM - S&P",
    }
    return aliases.get(text, text)


def to_number(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("(", "-", regex=False)
        .str.replace(")", "", regex=False)
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "-": pd.NA})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def to_percentage(series: pd.Series) -> pd.Series:
    numeric = to_number(series)
    if numeric.dropna().gt(1).mean() > 0.5:
        numeric = numeric / 100
    return numeric


def detect_mapping(columns: list[object]) -> tuple[dict[str, str | None], dict[str, list[str]]]:
    normalized_columns: dict[str, list[str]] = {}
    for column in columns:
        normalized_columns.setdefault(normalize_text(column), []).append(str(column))

    mapping: dict[str, str | None] = {}
    candidates: dict[str, list[str]] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        matches: list[str] = []
        for alias in aliases:
            matches.extend(normalized_columns.get(normalize_text(alias), []))
        unique_matches = list(dict.fromkeys(matches))
        candidates[canonical] = unique_matches
        mapping[canonical] = unique_matches[0] if len(unique_matches) == 1 else None
    return mapping, candidates


def mapping_is_complete(mapping: dict[str, str | None]) -> bool:
    values = [mapping.get(column) for column in REQUIRED_COLUMNS]
    return all(values) and len(set(values)) == len(values)


def apply_mapping(raw: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    mapped = pd.DataFrame()
    for canonical in REQUIRED_COLUMNS:
        mapped[canonical] = raw[mapping[canonical]]
    return mapped


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    data = data.dropna(how="all")
    data = data[REQUIRED_COLUMNS]
    data["Flavor Description"] = data["Flavor Description"].astype(str).str.strip()
    data["Size"] = data["Size"].astype(str).str.strip()
    data["Category"] = data["Category"].map(normalize_category)
    data["Net Value 6M"] = to_number(data["Net Value 6M"])
    data["GP%"] = to_percentage(data["GP%"])

    data = data[data["Category"].isin(INCLUDED_CATEGORIES)]
    data = data[~data["Category"].isin(EXCLUDED_CATEGORIES)]
    data = data.dropna(subset=REQUIRED_COLUMNS)
    data = data[data["Flavor Description"].ne("")]
    data = data.drop_duplicates()

    return data.sort_values(["Category", "Net Value 6M"], ascending=[True, False]).reset_index(drop=True)


def header_score(row: pd.Series) -> int:
    values = {normalize_text(value) for value in row.dropna().tolist()}
    score = 0
    for aliases in COLUMN_ALIASES.values():
        alias_values = {normalize_text(alias) for alias in aliases}
        if values.intersection(alias_values):
            score += 1
    return score


def best_excel_table(file_obj) -> pd.DataFrame:
    excel = pd.ExcelFile(file_obj)
    best_sheet = excel.sheet_names[0]
    best_header = 0
    best_score = -1

    for sheet in excel.sheet_names:
        preview = pd.read_excel(file_obj, sheet_name=sheet, header=None, nrows=25)
        for index, row in preview.iterrows():
            score = header_score(row)
            if score > best_score:
                best_score = score
                best_sheet = sheet
                best_header = int(index)

    return pd.read_excel(file_obj, sheet_name=best_sheet, header=best_header)


def read_raw_upload(uploaded_file) -> pd.DataFrame:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(uploaded_file)
    return best_excel_table(uploaded_file)


def load_default_data(path_text: str) -> pd.DataFrame:
    return clean_data(pd.read_csv(path_text))


def format_money(value: float) -> str:
    if pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:,.1f}K"
    return f"{value:,.0f}"


def summarize_sizes(selected_sizes: list[str], available_sizes: list[str]) -> str:
    if not selected_sizes:
        return "None"
    if len(selected_sizes) == len(available_sizes):
        return "All sizes"
    if len(selected_sizes) <= 3:
        return " + ".join(selected_sizes)
    return f"{selected_sizes[0]} + {selected_sizes[1]} + {len(selected_sizes) - 2} more"


def summarize_categories(selected_categories: list[str], available_categories: list[str]) -> str:
    if not selected_categories:
        return "None"
    if len(selected_categories) == len(available_categories):
        return "All included categories"
    if len(selected_categories) <= 3:
        return ", ".join(selected_categories)
    return f"{selected_categories[0]}, {selected_categories[1]}, {selected_categories[2]} + {len(selected_categories) - 3} more"


def reset_category_state(available_categories: list[str]) -> None:
    st.session_state["selected_categories"] = available_categories.copy()


def reset_size_state(available_sizes: list[str]) -> None:
    st.session_state["selected_sizes"] = available_sizes.copy()


def set_items(state_key: str, items: list[str]) -> None:
    st.session_state[state_key] = items.copy()


def render_pill_selector(
    title: str,
    help_text: str,
    options: list[str],
    state_key: str,
    key_prefix: str,
) -> None:
    st.markdown(f'<div class="filter-heading">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="filter-help">{help_text}</div>', unsafe_allow_html=True)
    control_left, control_right = st.columns(2)
    control_left.button(
        "Select All",
        key=f"{key_prefix}_all",
        width="stretch",
        on_click=set_items,
        args=(state_key, options),
    )
    control_right.button(
        "Clear All",
        key=f"{key_prefix}_clear",
        width="stretch",
        on_click=set_items,
        args=(state_key, []),
    )
    st.pills(
        f"{title.title()} options",
        options,
        selection_mode="multi",
        key=state_key,
        label_visibility="collapsed",
        width="stretch",
    )


local_css()

if "selected_categories" not in st.session_state:
    st.session_state["selected_categories"] = []
if "selected_sizes" not in st.session_state:
    st.session_state["selected_sizes"] = []
if "last_category_signature" not in st.session_state:
    st.session_state["last_category_signature"] = ""
if "last_category_options_signature" not in st.session_state:
    st.session_state["last_category_options_signature"] = ""

st.title("Sales vs GP% Portfolio Dashboard")
st.markdown(
    '<div class="section-caption">FMCG beverage SKU portfolio view for commercial review, margin strategy, and category prioritization.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Data & Filters")
    uploaded = st.file_uploader("Upload Excel or CSV", type=["xlsx", "xls", "csv"])

raw_upload = None
manual_mapping_needed = False
source_status = "Using default embedded data"

if uploaded is not None:
    try:
        raw_upload = read_raw_upload(uploaded)
        auto_mapping, mapping_candidates = detect_mapping(raw_upload.columns.tolist())
        manual_mapping_needed = not mapping_is_complete(auto_mapping)
    except Exception as exc:
        st.warning(f"The uploaded file could not be read. Using default embedded data. Details: {exc}")
        raw_upload = None

if raw_upload is not None and not manual_mapping_needed:
    mapped_upload = apply_mapping(raw_upload, {key: value for key, value in auto_mapping.items() if value})
    df = clean_data(mapped_upload)
    source_status = f"Using uploaded file: {uploaded.name}"
elif raw_upload is not None and manual_mapping_needed:
    st.warning("Column recognition needs your confirmation. Map the uploaded columns below, then the dashboard will refresh.")
    with st.sidebar:
        st.subheader("Column Mapping")
        upload_columns = raw_upload.columns.astype(str).tolist()
        manual_mapping: dict[str, str] = {}
        used_defaults: set[str] = set()
        for canonical in REQUIRED_COLUMNS:
            options = ["Select column"] + upload_columns
            suggested = mapping_candidates.get(canonical, [])
            default_value = suggested[0] if suggested else "Select column"
            if default_value in used_defaults:
                default_value = "Select column"
            index = options.index(default_value) if default_value in options else 0
            choice = st.selectbox(FIELD_LABELS[canonical], options, index=index, key=f"map_{canonical}")
            if choice != "Select column":
                manual_mapping[canonical] = choice
                used_defaults.add(choice)

    if len(manual_mapping) == len(REQUIRED_COLUMNS) and len(set(manual_mapping.values())) == len(REQUIRED_COLUMNS):
        df = clean_data(apply_mapping(raw_upload, manual_mapping))
        source_status = f"Using uploaded file: {uploaded.name}"
    else:
        df = load_default_data(str(DEFAULT_DATA_FILE))
else:
    df = load_default_data(str(DEFAULT_DATA_FILE))

if df.empty:
    st.warning("No usable rows were found after cleaning. Check that sales and GP% values are populated.")
    st.stop()

with st.sidebar:
    st.markdown(f'<div class="source-note">{source_status}</div>', unsafe_allow_html=True)
    search_term = st.text_input("SKU search", placeholder="Type product or flavor name")

category_options = [
    category for category in INCLUDED_CATEGORIES if category in df["Category"].unique()
]
category_options_signature = "|".join(category_options)
if st.session_state["last_category_options_signature"] != category_options_signature:
    reset_category_state(category_options)
    st.session_state["last_category_options_signature"] = category_options_signature

st.session_state["selected_categories"] = [
    category for category in st.session_state["selected_categories"] if category in category_options
]

render_pill_selector(
    "CHOOSE CATEGORY",
    "Select one or more portfolio categories.",
    category_options,
    "selected_categories",
    "cat",
)

selected_categories = st.session_state["selected_categories"]
if selected_categories:
    category_df = df[df["Category"].isin(selected_categories)]
else:
    category_df = df.iloc[0:0]

available_sizes = sorted(category_df["Size"].dropna().unique().tolist())
category_signature = "|".join(selected_categories) + "::" + "|".join(available_sizes)

if st.session_state["last_category_signature"] != category_signature:
    reset_size_state(available_sizes)
    st.session_state["last_category_signature"] = category_signature
st.session_state["selected_sizes"] = [
    size for size in st.session_state["selected_sizes"] if size in available_sizes
]

render_pill_selector(
    "CHOOSE SIZE",
    "Only sizes available in the selected categories are shown.",
    available_sizes,
    "selected_sizes",
    "size",
)
selected_sizes = st.session_state["selected_sizes"]

filtered = category_df.copy()
if selected_sizes:
    filtered = filtered[filtered["Size"].isin(selected_sizes)]
else:
    filtered = filtered.iloc[0:0]
if search_term:
    filtered = filtered[
        filtered["Flavor Description"].str.contains(search_term, case=False, na=False)
    ]

with st.sidebar:
    st.caption(f"Selected SKU count: {len(filtered):,}")
    export_csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Export filtered data",
        data=export_csv,
        file_name="sales_gp_filtered_data.csv",
        mime="text/csv",
        width="stretch",
    )

selected_category_label = summarize_categories(selected_categories, category_options)
st.markdown(
    (
        '<div class="filter-summary">'
        f"<b>Selected:</b> {selected_category_label} &nbsp;&nbsp; "
        f"<b>Sizes:</b> {summarize_sizes(selected_sizes, available_sizes)} &nbsp;&nbsp; "
        f"<b>SKU Count:</b> {len(filtered):,}"
        "</div>"
    ),
    unsafe_allow_html=True,
)

total_sales = filtered["Net Value 6M"].sum() if not filtered.empty else 0
average_gp = filtered["GP%"].mean() if not filtered.empty else pd.NA
sku_count = len(filtered)

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("Total Sales Value", format_money(total_sales))
kpi_2.metric("Average GP%", "-" if pd.isna(average_gp) else f"{average_gp:.1%}")
kpi_3.metric("Number of SKUs", f"{sku_count:,}")
kpi_4.metric("Selected Category", selected_category_label)

if filtered.empty:
    st.info("No SKUs match the current category, size, and search filters.")
    st.stop()

avg_sales = filtered["Net Value 6M"].mean()
avg_gp = filtered["GP%"].mean()
x_min = filtered["Net Value 6M"].min()
x_max = filtered["Net Value 6M"].max()
y_min = min(filtered["GP%"].min(), avg_gp)
y_max = max(filtered["GP%"].max(), avg_gp)
y_padding = max((y_max - y_min) * 0.12, 0.03)

fig = px.scatter(
    filtered,
    x="Net Value 6M",
    y="GP%",
    color="Category",
    color_discrete_map=COLOR_MAP,
    size="Net Value 6M",
    size_max=26,
    hover_data={
        "Flavor Description": True,
        "Size": True,
        "Category": True,
        "Net Value 6M": ":,.0f",
        "GP%": ":.1%",
    },
    custom_data=["Flavor Description", "Size", "Category", "Net Value 6M", "GP%"],
    title="SKU Sales Value vs Gross Profit %",
)

fig.update_traces(
    marker=dict(opacity=0.84, line=dict(width=0.8, color="#fbfcfe")),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Size: %{customdata[1]}<br>"
        "Category: %{customdata[2]}<br>"
        "Sales Value: %{customdata[3]:,.0f}<br>"
        "GP%: %{customdata[4]:.1%}<extra></extra>"
    ),
)

fig.add_vline(
    x=avg_sales,
    line_width=2,
    line_dash="dash",
    line_color="#6b7280",
    annotation_text=f"Avg Sales {format_money(avg_sales)}",
    annotation_position="top left",
)
fig.add_hline(
    y=avg_gp,
    line_width=2,
    line_dash="dash",
    line_color="#6b7280",
    annotation_text=f"Avg GP {avg_gp:.1%}",
    annotation_position="bottom right",
)

x_span = max(x_max - x_min, 1)
label_x_low = x_min + x_span * 0.08
label_x_high = avg_sales + (x_max - avg_sales) * 0.45 if x_max > avg_sales else x_max
label_y_high = avg_gp + (y_max - avg_gp) * 0.70 if y_max > avg_gp else y_max
label_y_low = y_min + (avg_gp - y_min) * 0.25 if avg_gp > y_min else y_min

for text, x_value, y_value in [
    ("High Sales / High GP", label_x_high, label_y_high),
    ("High Sales / Low GP", label_x_high, label_y_low),
    ("Low Sales / High GP", label_x_low, label_y_high),
    ("Low Sales / Low GP", label_x_low, label_y_low),
]:
    fig.add_annotation(
        x=x_value,
        y=y_value,
        text=text,
        showarrow=False,
        font=dict(size=12, color="#4b5563"),
        bgcolor="rgba(251,252,254,0.80)",
        bordercolor="rgba(215,222,232,0.9)",
        borderwidth=1,
        borderpad=4,
    )

fig.update_layout(
    height=650,
    margin=dict(l=20, r=20, t=70, b=35),
    legend_title_text="Category",
    plot_bgcolor="#fbfcfe",
    paper_bgcolor="#fbfcfe",
    hovermode="closest",
    title=dict(font=dict(size=22, color="#17202a")),
)
fig.update_xaxes(
    title="Sales Value / Net Value 6M",
    tickformat=",.0f",
    showgrid=True,
    gridcolor="#e6ebf2",
    zeroline=False,
)
fig.update_yaxes(
    title="GP%",
    tickformat=".0%",
    showgrid=True,
    gridcolor="#e6ebf2",
    zeroline=False,
    range=[max(y_min - y_padding, -1), min(y_max + y_padding, 1.5)],
)

st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "scrollZoom": True})

with st.expander("Filtered SKU data", expanded=False):
    display = filtered.copy()
    display["GP%"] = display["GP%"].map(lambda value: f"{value:.1%}")
    display["Net Value 6M"] = display["Net Value 6M"].map(lambda value: f"{value:,.0f}")
    st.dataframe(display, width="stretch", hide_index=True)
