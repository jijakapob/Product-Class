from pathlib import Path
import base64
import html
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


APP_TITLE = "Sales vs GP% Portfolio Dashboard"
DEFAULT_DATA_FILE = Path("data/default_sales_gp.csv")
PROFILE_IMAGE_FILE = Path("assets/profile_ji.jpg")

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

BASE_COLOR_MAP = {
    "FJ 100%": "#27496d",
    "VJ 100%": "#2f7d73",
    "Cool 40%": "#9b7a3c",
    "Super Kid": "#6f638f",
    "Squeeze": "#9a5f5a",
    "Aura": "#3f6f99",
    "Aquare": "#40878d",
    "OEM": "#6f7d86",
    "OEM - S&P": "#46566f",
    "Essence": "#8a5a68",
    "FOOD SERVICE TRADE": "#5b6d8b",
    "Consumer product - Food": "#7d735d",
}

PREMIUM_COLOR_SEQUENCE = [
    "#27496d",
    "#2f7d73",
    "#9b7a3c",
    "#6f638f",
    "#9a5f5a",
    "#3f6f99",
    "#40878d",
    "#6f7d86",
    "#46566f",
    "#8a5a68",
    "#5b6d8b",
    "#7d735d",
    "#38556f",
    "#55706d",
    "#756c8b",
    "#8a6f55",
    "#637487",
    "#53616f",
    "#7a6872",
]


st.set_page_config(page_title=APP_TITLE, layout="wide")


def local_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --navy: #10233f;
            --navy-2: #18385d;
            --steel: #52677f;
            --brand-blue: #12355b;
            --brand-blue-soft: #e8f0f8;
            --ink: #17202a;
            --muted: #667085;
            --line: #d9e0ea;
            --soft: #f4f7fb;
            --surface: #fbfcfe;
            --card-shadow: 0 18px 42px rgba(19, 36, 61, 0.08), 0 2px 8px rgba(19, 36, 61, 0.04);
        }
        .stApp {
            background:
                radial-gradient(circle at 14% 8%, rgba(77, 105, 137, 0.13), transparent 32%),
                radial-gradient(circle at 88% 4%, rgba(35, 67, 103, 0.10), transparent 30%),
                linear-gradient(180deg, #eef3f8 0%, #f7f9fc 38%, #f3f6fa 100%);
        }
        .main .block-container {
            padding-top: 1.15rem;
            padding-bottom: 2.5rem;
            max-width: 1240px;
        }
        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: 0;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
            border-right: 1px solid rgba(166, 181, 199, 0.45);
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
            padding-top: 1.25rem;
        }
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--navy);
            font-weight: 760;
            letter-spacing: 0;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"],
        section[data-testid="stSidebar"] [data-testid="stTextInput"],
        section[data-testid="stSidebar"] [data-testid="stDownloadButton"] {
            background: rgba(251, 252, 254, 0.76);
            border: 1px solid rgba(206, 216, 228, 0.88);
            border-radius: 16px;
            padding: 0.72rem;
            box-shadow: 0 10px 24px rgba(26, 44, 69, 0.05);
        }
        .dashboard-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1.4rem;
            margin-bottom: 1.25rem;
            padding: 1.35rem 1.45rem;
            border: 1px solid rgba(200, 211, 225, 0.88);
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(251, 252, 254, 0.96), rgba(238, 243, 249, 0.90)),
                radial-gradient(circle at 88% 12%, rgba(18, 53, 91, 0.10), transparent 28%);
            box-shadow: var(--card-shadow);
            position: relative;
            overflow: hidden;
        }
        .dashboard-header::after {
            content: "";
            position: absolute;
            inset: auto -8% -46% 52%;
            height: 180px;
            background: linear-gradient(115deg, rgba(18, 53, 91, 0.08), rgba(82, 103, 127, 0.02));
            transform: skewX(-18deg);
            pointer-events: none;
        }
        .dashboard-title-block {
            min-width: 0;
            flex: 1 1 auto;
            position: relative;
            z-index: 1;
        }
        .dashboard-title-block h1 {
            margin: 0 0 0.35rem 0;
            font-size: clamp(2.15rem, 3vw, 3.05rem);
            line-height: 1.02;
            font-weight: 780;
            letter-spacing: -0.01em;
            color: var(--navy);
        }
        .designer-profile {
            flex: 0 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.34rem;
            padding: 0.35rem 0.2rem;
            min-width: 120px;
            position: relative;
            z-index: 1;
            transition: transform 180ms ease, filter 180ms ease;
        }
        .designer-profile:hover {
            transform: translateY(-1px) scale(1.015);
            filter: drop-shadow(0 9px 18px rgba(18, 53, 91, 0.13));
        }
        .designer-photo {
            width: clamp(72px, 7vw, 92px);
            height: clamp(72px, 7vw, 92px);
            border-radius: 999px;
            object-fit: cover;
            border: 3px solid rgba(251, 252, 254, 0.95);
            box-shadow: 0 10px 22px rgba(18, 53, 91, 0.16), 0 0 0 1px rgba(139, 156, 178, 0.28);
            background: #e8eef6;
        }
        .designer-name {
            color: #203a57;
            font-size: 0.88rem;
            font-weight: 720;
            line-height: 1.15;
            white-space: nowrap;
        }
        .designer-subtitle {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 560;
            line-height: 1.1;
            white-space: nowrap;
        }
        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: var(--card-shadow);
        }
        div[data-testid="stMetricLabel"] {
            color: var(--muted);
        }
        div.stButton > button {
            border-radius: 10px;
            border: 1px solid rgba(190, 202, 217, 0.95);
            background: linear-gradient(180deg, #ffffff, #f6f8fb);
            color: var(--navy);
            font-weight: 600;
            min-height: 34px;
            white-space: normal;
            line-height: 1.15;
            box-shadow: 0 6px 14px rgba(26, 44, 69, 0.04);
        }
        div.stButton > button:hover {
            border-color: var(--navy-2);
            color: var(--navy);
            background: #f2f6fb;
            box-shadow: 0 10px 20px rgba(26, 44, 69, 0.08);
        }
        .stButton button[kind="secondary"] {
            padding: 0.2rem 0.65rem;
            min-height: 32px;
            font-size: 0.84rem;
            border-radius: 999px;
        }
        .section-caption, .source-note, .filter-summary {
            color: var(--muted);
            font-size: 0.92rem;
        }
        .section-caption {
            margin-top: 0;
            margin-bottom: 0;
            max-width: 62rem;
            font-weight: 390;
            line-height: 1.55;
        }
        .filter-summary {
            background: linear-gradient(135deg, rgba(251, 252, 254, 0.94), rgba(239, 244, 250, 0.88));
            border: 1px solid rgba(200, 211, 225, 0.92);
            border-radius: 18px;
            padding: 0.86rem 1rem;
            margin: 1rem 0 1.1rem 0;
            box-shadow: 0 12px 28px rgba(26, 44, 69, 0.06);
        }
        .filter-summary b {
            color: var(--ink);
        }
        .source-note {
            margin: 0.4rem 0 1rem 0;
            color: var(--steel);
            font-weight: 560;
        }
        .filter-heading {
            color: var(--navy);
            font-size: 0.88rem;
            font-weight: 820;
            letter-spacing: 0;
            margin: 1.35rem 0 0.24rem 0;
            text-transform: uppercase;
        }
        .filter-help {
            color: var(--muted);
            font-size: 0.8rem;
            margin: -0.1rem 0 0.46rem 0;
        }
        .filter-disabled {
            color: #8a97a8;
            background: rgba(238, 243, 248, 0.74);
            border: 1px dashed #cbd5e1;
            border-radius: 16px;
            padding: 0.86rem 1rem;
            font-size: 0.9rem;
            margin-top: 0.35rem;
        }
        .instruction-card {
            background: linear-gradient(135deg, rgba(251, 252, 254, 0.96), rgba(241, 245, 250, 0.88));
            border: 1px solid rgba(200, 211, 225, 0.92);
            border-radius: 20px;
            padding: 1.08rem 1.2rem;
            color: var(--navy);
            font-weight: 650;
            margin-top: 0.9rem;
            box-shadow: var(--card-shadow);
        }
        div[data-testid="stElementToolbar"] {
            display: none;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.75rem;
        }
        div[data-testid="stPlotlyChart"],
        iframe {
            max-width: 100% !important;
            border: 1px solid rgba(200, 211, 225, 0.92) !important;
            border-radius: 22px !important;
            box-shadow: var(--card-shadow) !important;
            background: #fbfcfe !important;
        }
        .chart-section-title {
            color: var(--navy);
            font-size: 1.18rem;
            font-weight: 780;
            letter-spacing: 0;
            margin: 1.55rem 0 0.15rem 0;
            padding-top: 0.35rem;
        }
        .chart-section-title::before {
            content: "";
            display: inline-block;
            width: 34px;
            height: 2px;
            margin-right: 10px;
            vertical-align: middle;
            background: linear-gradient(90deg, var(--navy), rgba(82, 103, 127, 0.22));
            border-radius: 999px;
        }
        .chart-section-note {
            color: var(--muted);
            font-size: 0.86rem;
            margin-bottom: 0.62rem;
            line-height: 1.45;
        }
        .kpi-card {
            position: relative;
            overflow: hidden;
            min-height: 126px;
            padding: 1rem 1.05rem 1rem 1.05rem;
            border-radius: 20px;
            background:
                linear-gradient(180deg, rgba(251, 252, 254, 0.98), rgba(245, 248, 252, 0.92));
            border: 1px solid rgba(200, 211, 225, 0.92);
            box-shadow: var(--card-shadow);
        }
        .kpi-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 3px;
            background: linear-gradient(90deg, #10233f, #52677f 55%, rgba(82, 103, 127, 0.1));
        }
        .kpi-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 680;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }
        .kpi-value {
            color: var(--navy);
            font-size: clamp(1.35rem, 2.2vw, 2rem);
            line-height: 1.06;
            font-weight: 780;
            letter-spacing: -0.01em;
            overflow-wrap: anywhere;
        }
        .kpi-subtext {
            color: var(--steel);
            font-size: 0.76rem;
            font-weight: 520;
            margin-top: 0.5rem;
        }
        div[data-baseweb="button-group"] {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.34rem !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100% !important;
        }
        div[data-baseweb="button-group"] > button,
        [data-testid="stBaseButton-pills"],
        [data-testid="stBaseButton-pillsActive"] {
            min-height: 32px !important;
            height: 32px !important;
            border-radius: 999px !important;
            white-space: nowrap !important;
            line-height: 1.15;
            padding: 0.20rem 0.72rem !important;
            font-size: 0.82rem !important;
            font-weight: 680 !important;
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: 13rem !important;
            box-shadow: none !important;
        }
        div[data-baseweb="button-group"] > button p,
        [data-testid="stBaseButton-pills"] p,
        [data-testid="stBaseButton-pillsActive"] p {
            margin: 0 !important;
            line-height: 1.1 !important;
        }
        div[data-baseweb="button-group"] > button[kind="pills"],
        [data-testid="stBaseButton-pills"] {
            background: rgba(251, 252, 254, 0.86) !important;
            border: 1px solid rgba(199, 211, 225, 0.96) !important;
            color: #344054 !important;
        }
        div[data-baseweb="button-group"] > button[kind="pills"]:hover,
        [data-testid="stBaseButton-pills"]:hover {
            background: #eef4fa !important;
            border-color: #7f96b2 !important;
            color: var(--brand-blue) !important;
            box-shadow: 0 8px 16px rgba(18, 53, 91, 0.07) !important;
        }
        div[data-baseweb="button-group"] > button[kind="pillsActive"],
        div[data-baseweb="button-group"] > button[aria-pressed="true"],
        [data-testid="stBaseButton-pills"][aria-pressed="true"],
        [data-testid="stBaseButton-pillsActive"],
        button[aria-pressed="true"] {
            background: linear-gradient(180deg, #18385d, #10233f) !important;
            border-color: rgba(16, 35, 63, 0.85) !important;
            color: #f8fafc !important;
            box-shadow: 0 10px 20px rgba(18, 53, 91, 0.18) !important;
        }
        .stButton button[kind="secondary"] {
            min-height: 30px !important;
            height: 30px !important;
            padding: 0.16rem 0.62rem !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            border-radius: 999px !important;
            background: #ffffff !important;
            color: #475467 !important;
            border-color: #d7dee8 !important;
            width: auto !important;
        }
        @media (max-width: 700px) {
            .main .block-container {
                padding: 0.85rem 0.65rem 1.4rem 0.65rem;
            }
            .dashboard-header {
                align-items: center;
                flex-direction: column;
                gap: 0.72rem;
                text-align: center;
                margin-bottom: 0.85rem;
                padding: 1rem 0.9rem;
                border-radius: 20px;
            }
            .dashboard-title-block h1 {
                font-size: 1.65rem;
                line-height: 1.15;
            }
            .designer-profile {
                min-width: 0;
                gap: 0.24rem;
            }
            .designer-photo {
                width: 64px;
                height: 64px;
                border-width: 2px;
                box-shadow: 0 7px 16px rgba(18, 53, 91, 0.14), 0 0 0 1px rgba(139, 156, 178, 0.25);
            }
            .designer-name {
                font-size: 0.82rem;
            }
            .designer-subtitle {
                font-size: 0.68rem;
            }
            .section-caption, .filter-summary {
                font-size: 0.82rem;
            }
            .filter-heading {
                font-size: 0.94rem;
                margin-top: 1.1rem;
            }
            [data-testid="stBaseButton-pills"],
            [data-testid="stBaseButton-pillsActive"],
            div[data-baseweb="button-group"] > button {
                min-height: 38px !important;
                height: 38px !important;
                font-size: 0.84rem !important;
                padding-left: 0.72rem !important;
                padding-right: 0.72rem !important;
            }
            div[data-testid="stMetric"] {
                padding: 10px 12px;
            }
            div[data-testid="stMetricValue"] {
                font-size: 1.25rem !important;
                line-height: 1.18 !important;
            }
            .chart-section-title {
                font-size: 1rem;
                margin-top: 0.9rem;
            }
            .chart-section-title::before {
                width: 24px;
                margin-right: 8px;
            }
            .chart-section-note {
                font-size: 0.78rem;
            }
            .kpi-card {
                min-height: 104px;
                padding: 0.86rem 0.92rem;
                border-radius: 18px;
            }
            .kpi-label {
                font-size: 0.68rem;
            }
            .kpi-value {
                font-size: 1.28rem;
            }
            .kpi-subtext {
                font-size: 0.7rem;
            }
        }
        @media (max-width: 430px) {
            iframe[title="st.iframe"] {
                height: 320px !important;
            }
        }
        @media (min-width: 431px) and (max-width: 900px) {
            iframe[title="st.iframe"] {
                height: 430px !important;
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
    sales_text = data["Net Value 6M"].astype(str).str.strip()
    data["Net Value 6M"] = to_number(data["Net Value 6M"])
    data.loc[sales_text.eq("-"), "Net Value 6M"] = 0
    data["GP%"] = to_percentage(data["GP%"])

    data = data.dropna(subset=REQUIRED_COLUMNS)
    data = data[data["Flavor Description"].ne("")]
    data = data.drop_duplicates()

    return data.sort_values(["Category", "Net Value 6M"], ascending=[True, False]).reset_index(drop=True)


def build_color_map(categories: list[str]) -> dict[str, str]:
    return {
        category: BASE_COLOR_MAP.get(
            category,
            PREMIUM_COLOR_SEQUENCE[index % len(PREMIUM_COLOR_SEQUENCE)],
        )
        for index, category in enumerate(categories)
    }


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


def best_csv_table(file_obj) -> pd.DataFrame:
    raw = pd.read_csv(file_obj, header=None, dtype=object, encoding="utf-8-sig")
    scores = raw.apply(header_score, axis=1)
    best_header = int(scores.idxmax())
    table = raw.iloc[best_header + 1 :].copy()
    table.columns = raw.iloc[best_header].astype(str).str.strip().tolist()
    return table


def read_raw_upload(uploaded_file) -> pd.DataFrame:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".csv":
        return best_csv_table(uploaded_file)
    return best_excel_table(uploaded_file)


def load_default_data(path_text: str) -> pd.DataFrame:
    return clean_data(best_csv_table(path_text))


def format_money(value: float) -> str:
    if pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:,.1f}K"
    return f"{value:,.0f}"


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def render_kpi_card(label: str, value: str, subtext: str = "") -> None:
    subtext_markup = f'<div class="kpi-subtext">{html.escape(subtext)}</div>' if subtext else ""
    st.markdown(
        (
            '<div class="kpi-card">'
            f'<div class="kpi-label">{html.escape(label)}</div>'
            f'<div class="kpi-value">{html.escape(value)}</div>'
            f"{subtext_markup}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


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
    st.session_state["selected_sizes"] = []


def set_items(state_key: str, items: list[str]) -> None:
    st.session_state[state_key] = items.copy()


def shorten_label(value: object, max_chars: int = 20) -> str:
    text = " ".join(str(value).split())
    text = re.sub(r"\band\b", "&", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3].rstrip()}..."


def render_pill_selector(
    title: str,
    help_text: str,
    options: list[str],
    state_key: str,
    key_prefix: str,
) -> None:
    st.markdown(f'<div class="filter-heading">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="filter-help">{help_text}</div>', unsafe_allow_html=True)
    control_left, control_right, _ = st.columns([0.16, 0.16, 0.68])
    control_left.button(
        "Select All",
        key=f"{key_prefix}_all",
        width="content",
        on_click=set_items,
        args=(state_key, options),
    )
    control_right.button(
        "Clear All",
        key=f"{key_prefix}_clear",
        width="content",
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


def render_disabled_step(title: str, message: str) -> None:
    st.markdown(f'<div class="filter-heading">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="filter-disabled">{message}</div>', unsafe_allow_html=True)


def render_responsive_plotly_chart(
    fig: go.Figure,
    chart_id: str,
    desktop_height: int,
    tablet_height: int,
    mobile_height: int,
) -> None:
    html = fig.to_html(
        include_plotlyjs=True,
        full_html=False,
        config={"displaylogo": False, "scrollZoom": True, "responsive": True},
        div_id=chart_id,
    )
    st.iframe(
        f"""
        <style>
          html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #fbfcfe;
          }}
          .plotly-responsive-frame {{
            width: 100%;
            overflow: hidden;
          }}
        </style>
        <div class="plotly-responsive-frame">
          {html}
        </div>
        <script>
          const chart = document.getElementById("{chart_id}");
          const heights = {{
            desktop: {desktop_height},
            tablet: {tablet_height},
            mobile: {mobile_height}
          }};

          function targetHeight() {{
            const width = window.innerWidth || document.documentElement.clientWidth || 390;
            if (width <= 430) return heights.mobile;
            if (width <= 900) return heights.tablet;
            return heights.desktop;
          }}

          function resizeChart() {{
            if (!chart || !window.Plotly) return;
            const width = Math.max(300, document.documentElement.clientWidth || window.innerWidth || 390);
            const height = targetHeight();
            const isMobile = width <= 430;
            const isTablet = width > 430 && width <= 900;
            const isRank = "{chart_id}".includes("rank");
            const margin = isRank
              ? (isMobile ? {{ l: 48, r: 42, t: 22, b: 92 }} : isTablet ? {{ l: 68, r: 58, t: 28, b: 120 }} : {{ l: 86, r: 74, t: 34, b: 142 }})
              : (isMobile ? {{ l: 44, r: 12, t: 42, b: 42 }} : isTablet ? {{ l: 52, r: 18, t: 50, b: 52 }} : {{ l: 58, r: 22, t: 56, b: 58 }});
            const baseFont = isMobile ? 9 : isTablet ? 10 : 11;
            const titleFont = isMobile ? 12 : isTablet ? 15 : 18;
            const tickFont = isMobile ? 8 : isTablet ? 9 : 10;
            const axisTitleFont = isMobile ? 9 : isTablet ? 10 : 11;
            window.Plotly.relayout(chart, {{
              width,
              height,
              margin,
              "font.size": baseFont,
              "title.font.size": titleFont,
              "legend.font.size": isMobile ? 8 : 10,
              "legend.title.font.size": isMobile ? 8 : 10,
              "xaxis.tickfont.size": tickFont,
              "yaxis.tickfont.size": tickFont,
              "yaxis2.tickfont.size": tickFont,
              "xaxis.title.font.size": axisTitleFont,
              "yaxis.title.font.size": axisTitleFont,
              "yaxis2.title.font.size": axisTitleFont,
              "xaxis.tickangle": isRank ? (isMobile ? -55 : -45) : 0
            }});
            window.parent.postMessage(
              {{ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: height + 12 }},
              "*"
            );
          }}

          window.addEventListener("resize", resizeChart);
          window.addEventListener("load", resizeChart);
          requestAnimationFrame(resizeChart);
          setTimeout(resizeChart, 250);
        </script>
        """,
        width="stretch",
        height="content",
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

profile_src = image_data_uri(PROFILE_IMAGE_FILE)
profile_markup = ""
if profile_src:
    profile_markup = (
        f'<div class="designer-profile" aria-label="Dashboard designer profile">'
        f'<img class="designer-photo" src="{profile_src}" alt="Ji profile photo" loading="eager" decoding="async" />'
        '<div class="designer-name">Designed by Ji</div>'
        '<div class="designer-subtitle">Commercial Portfolio Analytics</div>'
        "</div>"
    )

st.markdown(
    f"""
<div class="dashboard-header">
    <div class="dashboard-title-block">
        <h1>Sales vs GP% Portfolio Dashboard</h1>
        <div class="section-caption">FMCG beverage SKU portfolio view for commercial review, margin strategy, and category prioritization.</div>
    </div>
    {profile_markup}
</div>
""",
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

category_options = sorted(df["Category"].dropna().unique().tolist())
color_map = build_color_map(category_options)
category_options_signature = "|".join(category_options)
if st.session_state["last_category_options_signature"] != category_options_signature:
    st.session_state["selected_categories"] = []
    st.session_state["selected_sizes"] = []
    st.session_state["last_category_options_signature"] = category_options_signature
    st.session_state["last_category_signature"] = ""

st.session_state["selected_categories"] = [
    category for category in st.session_state["selected_categories"] if category in category_options
]

render_pill_selector(
    "STEP 1 — Choose Category",
    "Select one or more portfolio categories.",
    category_options,
    "selected_categories",
    "cat",
)

selected_categories = st.session_state["selected_categories"]
if not selected_categories:
    st.session_state["selected_sizes"] = []
    st.session_state["last_category_signature"] = ""
    render_disabled_step("STEP 2 — Choose Size", "Choose at least one category first. Size options will appear here.")
    st.markdown(
        '<div class="instruction-card">Select a category to begin analysis.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

category_df = df[df["Category"].isin(selected_categories)]

available_sizes = sorted(category_df["Size"].dropna().unique().tolist())
category_signature = "|".join(selected_categories) + "::" + "|".join(available_sizes)

if st.session_state["last_category_signature"] != category_signature:
    reset_size_state(available_sizes)
    st.session_state["last_category_signature"] = category_signature
st.session_state["selected_sizes"] = [
    size for size in st.session_state["selected_sizes"] if size in available_sizes
]

render_pill_selector(
    "STEP 2 — Choose Size",
    "Only sizes available in the selected categories are shown.",
    available_sizes,
    "selected_sizes",
    "size",
)
selected_sizes = st.session_state["selected_sizes"]

if not selected_sizes:
    selected_category_label = summarize_categories(selected_categories, category_options)
    st.markdown(
        (
            '<div class="filter-summary">'
            f"<b>Selected:</b> {selected_category_label} &nbsp;&nbsp; "
            "<b>Sizes:</b> None &nbsp;&nbsp; "
            "<b>SKU Count:</b> 0"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="instruction-card">Please choose at least one Size to display the chart.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

filtered = category_df.copy()
filtered = filtered[filtered["Size"].isin(selected_sizes)]
if search_term:
    filtered = filtered[
        filtered["Flavor Description"].str.contains(search_term, case=False, na=False)
    ]

with st.sidebar:
    st.caption(f"Selected SKU count: {len(filtered):,}")
    if not filtered.empty:
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

if filtered.empty:
    st.info("No SKUs match the current category, size, and search filters.")
    st.stop()

total_sales = filtered["Net Value 6M"].sum() if not filtered.empty else 0
average_gp = filtered["GP%"].mean() if not filtered.empty else pd.NA
sku_count = len(filtered)

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
with kpi_1:
    render_kpi_card("Total Sales Value", format_money(total_sales), "Filtered portfolio revenue")
with kpi_2:
    render_kpi_card("Average GP%", "-" if pd.isna(average_gp) else f"{average_gp:.1%}", "Weighted view by SKU mix")
with kpi_3:
    render_kpi_card("Number of SKUs", f"{sku_count:,}", "Active filtered items")
with kpi_4:
    render_kpi_card("Selected Category", selected_category_label, "Current strategic lens")

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
    color_discrete_map=color_map,
    size="Net Value 6M",
    size_max=22,
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
    marker=dict(opacity=0.80, line=dict(width=0.9, color="#fbfcfe")),
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
    autosize=True,
    height=560,
    margin=dict(l=58, r=22, t=56, b=58),
    legend_title_text="Category",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(size=10, color="#4b5563"),
        title_font=dict(size=10),
    ),
    plot_bgcolor="#f8fafc",
    paper_bgcolor="#fbfcfe",
    hovermode="closest",
    title=dict(font=dict(size=18, color="#17202a")),
    font=dict(size=11, color="#4b5563"),
    hoverlabel=dict(bgcolor="#10233f", bordercolor="#10233f", font=dict(color="#f8fafc", size=12)),
)
fig.update_xaxes(
    title="Sales Value / Net Value 6M",
    tickformat=",.0f",
    showgrid=True,
    gridcolor="#e8edf4",
    zeroline=False,
)
fig.update_yaxes(
    title="GP%",
    tickformat=".0%",
    showgrid=True,
    gridcolor="#e8edf4",
    zeroline=False,
    range=[max(y_min - y_padding, -1), min(y_max + y_padding, 1.5)],
)

st.markdown('<div class="chart-section-title">Sales vs GP% Portfolio Map</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="chart-section-note">Bubble view for quadrant review: sales scale, margin quality, and category mix.</div>',
    unsafe_allow_html=True,
)
render_responsive_plotly_chart(
    fig,
    "sales_gp_scatter",
    desktop_height=560,
    tablet_height=420,
    mobile_height=308,
)

st.markdown('<div class="chart-section-title">Sales Rank vs GP%</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="chart-section-note">Ranked bar and margin marker view. Choose how many SKUs to show, or scroll horizontally for the full portfolio.</div>',
    unsafe_allow_html=True,
)

rank_view = st.pills(
    "Ranked SKU count",
    ["Top 10", "Top 20", "Top 30", "All"],
    default="Top 10",
    selection_mode="single",
    label_visibility="collapsed",
    width="content",
)
rank_view = rank_view or "Top 10"
rank_limits = {"Top 10": 10, "Top 20": 20, "Top 30": 30}
rank_limit = rank_limits.get(rank_view)

ranked = filtered.sort_values("Net Value 6M", ascending=False).reset_index(drop=True).copy()
if rank_limit is not None:
    ranked = ranked.head(rank_limit).copy()
ranked["Display Label"] = [
    f"{index + 1}. {shorten_label(name)}"
    for index, name in enumerate(ranked["Flavor Description"].astype(str).tolist())
]
ranked["Bar Width"] = 0.24

rank_fig = make_subplots(specs=[[{"secondary_y": True}]])
rank_fig.add_trace(
    go.Bar(
        x=ranked["Display Label"],
        y=ranked["Net Value 6M"],
        name="Sales",
        width=ranked["Bar Width"],
        marker=dict(color="#9bbbd6", line=dict(color="rgba(66, 105, 143, 0.12)", width=0.4)),
        opacity=0.72,
        customdata=ranked[["Flavor Description", "Size", "Category", "Net Value 6M", "GP%"]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Size: %{customdata[1]}<br>"
            "Category: %{customdata[2]}<br>"
            "Sales: %{customdata[3]:,.0f}<br>"
            "GP%: %{customdata[4]:.1%}<extra></extra>"
        ),
    ),
    secondary_y=False,
)
rank_fig.add_trace(
    go.Scatter(
        x=ranked["Display Label"],
        y=ranked["GP%"],
        name="GP%",
        mode="lines+markers",
        line=dict(color="#238f7d", width=1.9),
        marker=dict(size=6.5, color="#238f7d", line=dict(color="#fbfcfe", width=1.2)),
        customdata=ranked[["Flavor Description", "Size", "Category", "Net Value 6M", "GP%"]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Size: %{customdata[1]}<br>"
            "Category: %{customdata[2]}<br>"
            "Sales: %{customdata[3]:,.0f}<br>"
            "GP%: %{customdata[4]:.1%}<extra></extra>"
        ),
    ),
    secondary_y=True,
)
rank_fig.update_layout(
    autosize=True,
    height=480,
    margin=dict(l=86, r=74, t=34, b=142),
    plot_bgcolor="#f8fafc",
    paper_bgcolor="#fbfcfe",
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#10233f", bordercolor="#10233f", font=dict(color="#f8fafc", size=12)),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=10, color="#4b5563"),
        bgcolor="rgba(251,252,254,0)",
    ),
    bargap=0.72,
    bargroupgap=0.30,
)
rank_fig.update_xaxes(
    title="SKU rank, sales high to low",
    tickangle=-45,
    tickfont=dict(size=9, color="#4b5563"),
    showgrid=False,
    automargin=True,
    title_standoff=34,
)
rank_fig.update_yaxes(
    title_text="Sales Value",
    tickformat=",.0f",
    showgrid=True,
    gridcolor="#e8edf4",
    zeroline=False,
    title_standoff=14,
    tickfont=dict(color="#4b5563"),
    secondary_y=False,
)
rank_fig.update_yaxes(
    title_text="GP%",
    tickformat=".0%",
    showgrid=False,
    zeroline=False,
    title_standoff=12,
    tickfont=dict(color="#4b5563"),
    secondary_y=True,
)
render_responsive_plotly_chart(
    rank_fig,
    "sales_gp_rank",
    desktop_height=480,
    tablet_height=360,
    mobile_height=300,
)

with st.expander("Filtered SKU data", expanded=False):
    display = filtered.copy()
    display["GP%"] = display["GP%"].map(lambda value: f"{value:.1%}")
    display["Net Value 6M"] = display["Net Value 6M"].map(lambda value: f"{value:,.0f}")
    st.dataframe(display, width="stretch", hide_index=True)
