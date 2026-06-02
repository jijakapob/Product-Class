\# Product Class SKU Rationalization Dashboard Instructions



\## Project Context



This project is a Streamlit dashboard for SKU portfolio review and SKU rationalization.



The dashboard currently uses:



\* 177 SKUs

\* 19 dynamic categories

\* Default dataset: `data/default\_sales\_gp.csv`

\* Main app file: `app.py`



The dashboard is used for FMCG beverage portfolio analysis in Thailand.



The main business objective is to help management review portfolio patterns using neutral clusters:



\* Top Quartile

\* Upper-Middle Quartile

\* Lower-Middle Quartile

\* Bottom Quartile



Do not treat cluster output as an automatic action decision. It is a decision-support tool only.



\---



\## Critical Business Definitions



\### Sales



Use:



`Net Value 6M`



This represents 6-month sales value.



Higher sales is better.



\---



\### GP%



GP% is SKU margin percentage.



Use GP% for display, scatter charts, tooltips, and SKU-level interpretation.



Do not use simple average GP% for portfolio-level profitability.



\---



\### Weighted GP%



Portfolio GP% must be calculated as:



`SUM(GP amount) / SUM(Net Value 6M)`



Never calculate portfolio GP% using:



`average(GP%)`



This is wrong because it ignores SKU sales weight.



\---



\### GP Amount



Use:



`GP amount`



This represents actual profit contribution.



For rationalization scoring, use GP Amount, not GP%.



Reason:



GP Amount reflects real business profit contribution.



\---



\### CVM



CVM means stock cover in months.



CVM is not cost.



Examples:



\* CVM 0.2 = around 6 days stock cover

\* CVM 0.5 = around 15 days stock cover

\* CVM 1.0 = around 30 days stock cover



Lower CVM is better.



Higher CVM means longer stock cover.



Do not create unnecessary interpretation labels unless requested.



Use plain quadrant descriptions such as:



\* Low Sales / High Stock Cover

\* High Sales / High Stock Cover

\* Low Sales / Low Stock Cover

\* High Sales / Low Stock Cover



Avoid recommendation-style labels unless explicitly requested.



\---



\## Rationalization Scoring Logic



Default scoring weights:



\* Sales Score = 40%

\* GP Amount Score = 40%

\* CVM Efficiency Score = 20%



Formula:



`Rationalization Score = Sales Score \* 0.40 + GP Amount Score \* 0.40 + CVM Efficiency Score \* 0.20`



Scoring direction:



\* Sales: higher is better

\* GP Amount: higher is better

\* CVM: lower is better



CVM score must be inverted before weighting.



\---



\## Score Quartile



Classify SKUs dynamically by score percentile:



\* Top 25% = Top Quartile

\* 25% to 50% = Upper-Middle Quartile

\* 50% to 75% = Lower-Middle Quartile

\* Bottom 25% = Bottom Quartile



Use neutral cluster and quartile language only. Do not use recommendation-style status labels for these score bands.



\---



\## Chart Rules



\### Sales vs GP%



Use for profitability analysis.



\* X-axis = Net Value 6M

\* Y-axis = GP%

\* Reference line should use weighted GP%, not average GP%



\---



\### Sales vs CVM



Use for inventory efficiency analysis.



\* X-axis = Net Value 6M

\* Y-axis = CVM stock cover months



Important:



Do not auto-scale Y-axis to extreme CVM outliers.



Recommended visual Y-axis:



\* Fixed range: 0 to 3

\* If CVM > 3, cap plotting position at 3

\* Keep actual CVM value visible in tooltip and export



Quadrant labels should be plain descriptions:



\* Top Left: Low Sales / High Stock Cover

\* Top Right: High Sales / High Stock Cover

\* Bottom Left: Low Sales / Low Stock Cover

\* Bottom Right: High Sales / Low Stock Cover



\---



\### GP% vs CVM



Use for profitability plus inventory efficiency.



\* X-axis = GP%

\* Y-axis = CVM

\* Bubble size = Net Value 6M



Apply the same CVM axis rule:



\* Visual Y-axis range 0 to 3

\* CVM values above 3 are visually capped at 3

\* Actual CVM remains in tooltip and table



\---



\## Data Handling Rules



Required fields:



\* Flavor Description

\* Size

\* Category

\* Net Value 6M

\* GP%

\* GP amount

\* CVM



The app should handle monthly updates with the same structure.



Dynamic category loading is required.



Do not hard-code included or excluded categories.



Do not remove categories such as:



\* Aura

\* Aquare

\* Canned Fruit

\* CEREAL BEVERAGE

\* Gift set

\* Herb Product

\* Less Sweet

\* Tipco Chewy

\* Tipco Play

\* White Tea

\* VEGE \& FRUIT



unless explicitly requested.



\---



\## UI Rules



Preserve the current premium executive dashboard look.



Do not redesign the app unless explicitly requested.



Keep:



\* Current header style

\* Current filter flow

\* Current category and size chip style

\* Current ranking chart

\* Current export function

\* Current mobile responsiveness



When fixing charts, prioritize readability and business interpretation.



\---



\## Validation Checklist



Before committing changes, validate:



\* App loads without Streamlit error

\* 177 SKUs loaded

\* 19 categories loaded

\* Weighted GP% uses GP amount / Net Value 6M

\* Category filter works

\* Size filter works

\* Sales vs GP% works

\* Sales vs CVM works

\* GP% vs CVM works

\* Ranking chart works

\* Export includes rationalization fields

\* Mobile view does not overflow badly



After changes, provide:



\* Summary of what changed

\* Validation results

\* Git commit ID

\* Confirmation that push to GitHub main succeeded

\* Confirmation that Streamlit Cloud redeployed or is reachable



