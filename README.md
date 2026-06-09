# Sales vs GP% Portfolio Dashboard

Sharing-ready Streamlit web app for beverage SKU portfolio analysis using Python, Pandas, Plotly, and an embedded default CSV.

## App Files

Deploy these project files:

- `app.py`
- `requirements.txt`
- `README.md`
- `data/default_sales_gp.csv`

The original Excel workbooks are not required for the default dashboard view.

## What It Does

- Shows an executive scatter chart for SKU portfolio review:
  - X-axis: `Sales Value / Net Value 6M`
  - Y-axis: `GP%`
  - One dot per SKU
  - Colors by category
  - Hover tooltip with SKU name, size, category, sales value, and GP%
- Adds average sales and average GP% reference lines to create four quadrants.
- Includes KPI cards for total sales value, average GP%, number of SKUs, and selected category.
- Supports visible category pills, dynamic size pills, SKU search, chart zoom, and CSV export.
- Allows Excel or CSV upload with flexible column recognition and manual mapping when needed.

## Included Categories

The dashboard includes only:

- `FJ 100%`
- `VJ 100%`
- `Cool 40%`
- `Super Kid`
- `Squeeze`
- `Aura`
- `Aquare`
- `OEM`
- `OEM - S&P`
- `Essence`
- `FOOD SERVICE TRADE`
- `Consumer product - Food`

The dashboard excludes Tipco Play, Less Sweet, Tipco Chewy, Canned Fruit, Cereal Beverage, Gift set, and Herb Product.

## Embedded Default Data

The app loads this file automatically when no upload is provided:

```text
data/default_sales_gp.csv
```

This means the app can run on Streamlit Community Cloud or a company server without needing any local Excel path from the original computer.

## Upload Requirements

Uploaded Excel or CSV files should contain these business fields:

- SKU / Product Name
- Size
- Category
- Sales Value
- GP%

The app recognizes common alternatives such as `Flavor Description`, `SKU Name`, `Product Name`, `Pack Size`, `Product Category`, `Net Value 6M`, `Sales`, `Revenue`, `Gross Profit %`, and `Gross Margin %`.

If column recognition is uncertain, the app shows a manual mapping section instead of crashing.

## Option A: Streamlit Community Cloud

Use this when you want one public shareable link.

1. Create a GitHub repository.
2. Add these files and folder to the repository:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `data/default_sales_gp.csv`
3. Commit and push to GitHub:

```bash
git init
git add app.py requirements.txt README.md data/default_sales_gp.csv .gitignore
git commit -m "Add Sales vs GP dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

4. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
5. Choose **New app**.
6. Select your GitHub repository and branch.
7. Set the main file path to:

```text
app.py
```

8. Deploy the app.
9. Copy the public app URL and share it with colleagues.

## Option B: Company Or Internal Server

Use this when the app should stay inside a company network.

1. Ask IT to place the project folder on a server.
2. Install Python and the dependencies:

```bash
pip install -r requirements.txt
```

3. Run Streamlit on a server port:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

4. IT should expose the app through an internal URL, reverse proxy, VPN, or company web server.
5. Colleagues can open the internal URL from a browser if they are on the company network or VPN.

## Option C: Local Use

Use this only for your own computer.

```bash
pip install -r requirements.txt
streamlit run app.py
```

The `localhost:8501` link works only on the computer running Streamlit. It is not a public shareable link.

## Deployment Checklist

- [ ] App runs locally with `streamlit run app.py`
- [ ] Default data loads from `data/default_sales_gp.csv`
- [ ] No local computer path dependency
- [ ] `requirements.txt` is complete
- [ ] Mobile layout checked
- [ ] Ready to upload to GitHub or deploy

## New Features (AI Narrator + Scenario Simulator)

### AI Portfolio Narrator

The AI Portfolio Narrator generates a concise executive summary from the current dashboard selection. It uses the filtered category and size view, summarizes sales, GP amount, weighted GP%, CVM observations, and review-priority watchouts, and avoids final decision wording.

### Delist-Potential Scenario Simulator

The Delist-Potential Scenario Simulator models the impact of simulating removal of the top 10, 20, or 30 Review Delist-Potential SKUs from the current filtered portfolio. It shows SKU count, sales, GP amount, weighted GP%, and stock-cover impacts for discussion only.

### Set GEMINI_API_KEY Locally

```bash
export GEMINI_API_KEY="your-key-here"
```

### Set GEMINI_API_KEY In Streamlit Cloud

1. Go to App Settings -> Secrets.
2. Add:

```toml
GEMINI_API_KEY = "your-key-here"
```

Simulator calculations work fully without an AI key. AI summaries are optional and only narrate already-calculated dashboard data; they do not invent numbers.
