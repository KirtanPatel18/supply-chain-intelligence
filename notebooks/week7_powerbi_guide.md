# Week 7 — Power BI Dashboard Guide
## Supply Chain Intelligence Project

---

## Prerequisites
- Download **Power BI Desktop** (free): https://powerbi.microsoft.com/desktop
- All CSV files from `data/processed/` must exist (Weeks 1–6 complete)

---

## Files to Load into Power BI

| File | Used For |
|---|---|
| `cleaned_supply_chain.csv` | Main data source |
| `supplier_risk_scores.csv` | Supplier risk page |
| `supplier_tier_summary.csv` | Supplier tier KPIs |
| `forecast_6month_summary.csv` | Forecast page |
| `business_impact_report.csv` | Business impact page |
| `executive_summary.csv` | Overview page |

---

## Step 1 — Load Data into Power BI

1. Open Power BI Desktop
2. Click **Home → Get Data → Text/CSV**
3. Load `cleaned_supply_chain.csv` first
4. Click **Transform Data** to open Power Query
5. Verify columns look correct → Click **Close & Apply**
6. Repeat for all 6 CSV files above

---

## Step 2 — Data Types to Fix in Power Query

For `cleaned_supply_chain.csv`:

| Column | Set Type To |
|---|---|
| Order Date | Date |
| Ship Date | Date |
| Revenue | Decimal Number |
| Is_Late | Whole Number |
| Is_Cancelled | Whole Number |
| Delivery_Delay_Days | Decimal Number |
| Order Profit Per Order | Decimal Number |

---

## Step 3 — Create These 5 Dashboard Pages

---

### PAGE 1 — Overview (Executive Summary)

**KPI Cards (top row):**
- Total Revenue → `SUM(cleaned_supply_chain[Revenue])`
- Total Orders → `COUNT(cleaned_supply_chain[Invoice])`
- Late Delivery Rate → `AVERAGE(cleaned_supply_chain[Is_Late])`
- Revenue at Risk → `SUM(cleaned_supply_chain[Revenue_At_Risk])`
- Avg Delay Days → `AVERAGE(cleaned_supply_chain[Delivery_Delay_Days])`

**Visuals:**
1. Line Chart — Monthly Revenue Trend
   - X-axis: Order_YearMonth
   - Y-axis: SUM(Revenue)

2. Bar Chart — Revenue by Market
   - X-axis: Market
   - Y-axis: SUM(Revenue)
   - Color: Market

3. Donut Chart — On Time vs Late Orders
   - Values: COUNT of orders
   - Legend: Is_Late (rename 0=On Time, 1=Late)

4. Bar Chart — Top 10 Categories by Revenue
   - X-axis: Category Name
   - Y-axis: SUM(Revenue)
   - Filter: Top 10 by Revenue

---

### PAGE 2 — Late Delivery Analysis

**KPI Cards:**
- Late Rate % → `AVERAGE(Is_Late) * 100`
- Total Late Orders → `SUM(Is_Late)`
- Avg Delay → `AVERAGE(Delivery_Delay_Days)`
- Revenue At Risk → `SUM(Revenue_At_Risk)`

**Visuals:**
1. Bar Chart — Late Rate by Shipping Mode
   - X-axis: Shipping Mode
   - Y-axis: AVERAGE(Is_Late)
   - Sort descending

2. Bar Chart — Late Rate by Order Region (Top 10)
   - X-axis: Order Region
   - Y-axis: AVERAGE(Is_Late)
   - Filter: Top 10 by late rate

3. Line Chart — Monthly Late Rate Trend
   - X-axis: Order_YearMonth
   - Y-axis: AVERAGE(Is_Late)
   - Add constant line at 0.5 (50% benchmark)

4. Matrix Table — Late Rate by Market × Shipping Mode
   - Rows: Market
   - Columns: Shipping Mode
   - Values: AVERAGE(Is_Late)
   - Conditional formatting: Red=high, Green=low

---

### PAGE 3 — Supplier Risk

**Data source:** `supplier_risk_scores.csv`

**KPI Cards:**
- High Risk Regions → COUNT where Risk_Tier = "High Risk"
- Avg Risk Score → AVERAGE(Risk_Score)
- High Risk Revenue → SUM(Total_Revenue) filtered to High Risk
- High Risk Revenue at Risk → SUM(Revenue_At_Risk) filtered to High Risk

**Visuals:**
1. Bar Chart — Risk Score by Region
   - X-axis: Order Region
   - Y-axis: Risk_Score
   - Color: Risk_Tier (Red/Yellow/Green)
   - Sort descending

2. Scatter Chart — Late Rate vs Avg Delay
   - X-axis: Late_Rate
   - Y-axis: Avg_Delay_Days
   - Size: Total_Revenue
   - Color: Risk_Tier
   - Details: Order Region

3. Stacked Bar — Revenue Safe vs At Risk by Tier
   - X-axis: Risk_Tier
   - Y-axis: Total_Revenue (Safe) + Revenue_At_Risk
   - Colors: Green=Safe, Red=At Risk

4. Table — Full Supplier Risk Scorecard
   - Columns: Order Region, Risk_Tier, Risk_Score, Late_Rate, Avg_Delay_Days, Total_Revenue, Revenue_At_Risk
   - Conditional formatting on Risk_Score

---

### PAGE 4 — Demand Forecast

**Data source:** `forecast_6month_summary.csv`

**KPI Cards:**
- Total Forecasted Orders → SUM(Forecast_Orders)
- Peak Month → Month with MAX(Forecast_Orders)
- Avg Monthly Forecast → AVERAGE(Forecast_Orders)
- Forecast Growth % → from business_impact_report.csv

**Visuals:**
1. Bar Chart with Error Bars — 6-Month Forecast
   - X-axis: Month
   - Y-axis: Forecast_Orders
   - Error bars: Lower_Bound to Upper_Bound
   - Color: steelblue

2. Line Chart — Historical + Forecast (use cleaned_supply_chain for historical)
   - Group monthly orders from main data
   - Overlay forecast from forecast_6month_summary

3. KPI Gauge — Forecast Accuracy
   - Value: 92.8
   - Min: 0, Max: 100
   - Target: 85

4. Table — Monthly Forecast Detail
   - Columns: Month, Forecast_Orders, Lower_Bound, Upper_Bound
   - Conditional formatting on Forecast_Orders

---

### PAGE 5 — Business Impact & ROI

**Data source:** `business_impact_report.csv`

**KPI Cards:**
- Total Cost of Delays → Total_Cost_Late
- Orders Preventable → Orders_Preventable
- Total Savings → Total_Savings
- Net ROI % → Net_ROI_Pct

**Visuals:**
1. Waterfall Chart — Revenue Impact
   - Categories: Total Revenue → Revenue At Risk → Costs → Net Revenue
   - Colors: Green=positive, Red=negative

2. Bar Chart — Before vs After ML Intervention
   - Side by side: Current Late Rate vs Projected Late Rate
   - Side by side: Current Rev at Risk vs Projected Rev at Risk

3. Donut Chart — Cost Breakdown
   - Retention Loss / Expediting / Customer Service / Brand Damage

4. Card Visual — ROI Highlight
   - Large number showing Net ROI %
   - Subtitle: "Return on ML Investment"

---

## Step 4 — Formatting & Design Tips

**Colors to use (consistent with project):**
- Primary Blue: `#3B8BD4`
- Success Green: `#1D9E75`
- Risk Red: `#E24B4A`
- Warning Amber: `#F5A623`
- Background: White `#FFFFFF`
- Text: Dark `#2C3E50`

**Apply to every page:**
- Page background: White
- All chart backgrounds: White
- Font: Segoe UI (Power BI default)
- Add company logo placeholder top-left
- Add page title top-center (bold, size 18)
- Add "Supply Chain Intelligence | Kirtan Patel" footer

**Slicers to add on every page:**
- Market slicer (dropdown)
- Year slicer (2015 / 2016 / 2017 / 2018)
- Shipping Mode slicer (dropdown)

---

## Step 5 — DAX Measures to Create

In Power BI, go to **Home → New Measure** and create these:

```dax
-- Late Delivery Rate %
Late Rate % = AVERAGE(cleaned_supply_chain[Is_Late]) * 100

-- Revenue at Risk
Revenue At Risk = SUM(cleaned_supply_chain[Revenue_At_Risk])

-- On Time Orders
On Time Orders = COUNTROWS(FILTER(cleaned_supply_chain, cleaned_supply_chain[Is_Late] = 0))

-- Late Orders
Late Orders = SUM(cleaned_supply_chain[Is_Late])

-- Avg Delay Days
Avg Delay = AVERAGE(cleaned_supply_chain[Delivery_Delay_Days])

-- Profit Margin %
Profit Margin % = 
    DIVIDE(
        SUM(cleaned_supply_chain[Order Profit Per Order]),
        SUM(cleaned_supply_chain[Revenue])
    ) * 100

-- Monthly Revenue
Monthly Revenue = 
    CALCULATE(
        SUM(cleaned_supply_chain[Revenue]),
        DATESMTD(cleaned_supply_chain[Order Date])
    )
```

---

## Step 6 — Export & Save

1. Save file as `supply_chain_dashboard.pbix` in `dashboard/` folder
2. Export each page as PNG:
   - File → Export → Export to PDF
   - Or: Print each page → Save as PNG
3. Save screenshots to `dashboard/screenshots/` folder
4. These screenshots go into your GitHub README

---

## Final Checklist

- [ ] All 5 pages created
- [ ] Slicers on every page
- [ ] Consistent colors applied
- [ ] DAX measures created
- [ ] KPI cards on every page
- [ ] File saved as .pbix
- [ ] Screenshots exported
- [ ] Screenshots added to GitHub README

---

## Next Step → Week 8: Streamlit App
