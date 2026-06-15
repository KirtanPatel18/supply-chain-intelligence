import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import os
import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F9FA; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1F2E 0%, #2C3E50 100%);
    }
    [data-testid="stSidebar"] * { color: #ECF0F1 !important; }
    .kpi-card {
        background: white; border-radius: 12px; padding: 20px;
        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #3B8BD4;
    }
    .kpi-card-red   { border-left-color: #E24B4A !important; }
    .kpi-card-green { border-left-color: #1D9E75 !important; }
    .kpi-card-amber { border-left-color: #F5A623 !important; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #2C3E50; margin: 8px 0; }
    .kpi-label { font-size: 13px; color: #7F8C8D; font-weight: 500;
                 text-transform: uppercase; letter-spacing: 0.5px; }
    .section-header {
        font-size: 20px; font-weight: 700; color: #2C3E50;
        margin: 24px 0 16px 0; padding-bottom: 8px;
        border-bottom: 2px solid #3B8BD4;
    }
    .page-title { font-size: 32px; font-weight: 800; color: #1A1F2E; margin-bottom: 4px; }
    .page-subtitle { font-size: 15px; color: #7F8C8D; margin-bottom: 24px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── PATHS ─────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR    = os.path.join(PROJECT_DIR, 'data', 'processed')
MODEL_DIR   = os.path.join(PROJECT_DIR, 'models')

def data_path(f): return os.path.join(DATA_DIR, f)
def model_path(f): return os.path.join(MODEL_DIR, f)

# ─── COLORS ────────────────────────────────────────────────────
BLUE   = '#3B8BD4'
GREEN  = '#1D9E75'
RED    = '#E24B4A'
AMBER  = '#F5A623'
PURPLE = '#9B59B6'
RISK_COLORS = {'High Risk': RED, 'Medium Risk': AMBER, 'Low Risk': GREEN}

# ─── HELPERS ───────────────────────────────────────────────────
def kpi_card(label, value, card_class=''):
    st.markdown(f"""
    <div class="kpi-card {card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>""", unsafe_allow_html=True)

def section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

# ─── LOAD DATA ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df           = pd.read_csv(data_path('cleaned_supply_chain.csv'),
                               parse_dates=['Order Date', 'Ship Date'])
    supplier     = pd.read_csv(data_path('supplier_risk_scores.csv'))
    tier_summary = pd.read_csv(data_path('supplier_tier_summary.csv'))
    forecast_6m  = pd.read_csv(data_path('forecast_6month_summary.csv'))
    impact       = pd.read_csv(data_path('business_impact_report.csv'))
    exec_summary = pd.read_csv(data_path('executive_summary.csv'))
    forecast_full= pd.read_csv(data_path('forecast_results.csv'), parse_dates=['ds'])
    return df, supplier, tier_summary, forecast_6m, impact, exec_summary, forecast_full

@st.cache_resource
def load_models():
    models = {}
    try:
        with open(model_path('late_delivery_model.pkl'), 'rb') as f:
            models['late_model'] = pickle.load(f)
        with open(model_path('label_encoders.pkl'), 'rb') as f:
            models['encoders'] = pickle.load(f)
        with open(model_path('feature_config.pkl'), 'rb') as f:
            models['feature_config'] = pickle.load(f)
        with open(model_path('late_delivery_scaler.pkl'), 'rb') as f:
            models['scaler'] = pickle.load(f)
    except Exception as e:
        st.warning(f"Some models could not be loaded: {e}")
    return models

df, supplier, tier_summary, forecast_6m, impact, exec_summary, forecast_full = load_data()
models = load_models()

# ─── SIDEBAR ───────────────────────────────────────────────────
st.sidebar.markdown("## 📦 Supply Chain\nIntelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "📊 Overview",
    "🚚 Late Delivery Analysis",
    "⚠️ Supplier Risk",
    "📈 Demand Forecast",
    "💰 Business Impact",
    "🔮 Late Delivery Predictor"
])
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
markets = ['All Markets'] + sorted(df['Market'].dropna().unique().tolist())
selected_market = st.sidebar.selectbox("Market", markets)
years = ['All Years'] + sorted(df['Order_Year'].dropna().unique().astype(str).tolist())
selected_year = st.sidebar.selectbox("Year", years)

df_f = df.copy()
if selected_market != 'All Markets':
    df_f = df_f[df_f['Market'] == selected_market]
if selected_year != 'All Years':
    df_f = df_f[df_f['Order_Year'] == int(selected_year)]

st.sidebar.markdown("---")
st.sidebar.caption(f"📁 {len(df_f):,} orders | Python · Streamlit")

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown('<div class="page-title">📊 Supply Chain Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">End-to-end performance summary across all markets and regions</div>', unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi_card("Total Revenue",     f"${df_f['Revenue'].sum():,.0f}", 'kpi-card-green')
    with c2: kpi_card("Total Orders",      f"{len(df_f):,}")
    with c3: kpi_card("Late Delivery Rate",f"{df_f['Is_Late'].mean():.1%}", 'kpi-card-red')
    with c4: kpi_card("Revenue at Risk",   f"${df_f['Revenue_At_Risk'].sum():,.0f}", 'kpi-card-red')
    with c5: kpi_card("Avg Delay",         f"{df_f['Delivery_Delay_Days'].mean():.2f} days", 'kpi-card-amber')

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📈 Monthly Revenue & Order Volume")

    monthly = df_f.groupby('Order_YearMonth').agg(
        Revenue=('Revenue','sum'), Orders=('Revenue','count')).reset_index()
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=monthly['Order_YearMonth'], y=monthly['Revenue'],
        name='Revenue ($)', marker_color=BLUE, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly['Order_YearMonth'], y=monthly['Orders'],
        name='Order Count', line=dict(color=RED, width=2), mode='lines+markers'), secondary_y=True)
    fig.update_layout(plot_bgcolor='white', height=380, legend=dict(x=0.01, y=0.99))
    fig.update_yaxes(title_text='Revenue ($)', secondary_y=False)
    fig.update_yaxes(title_text='Order Count', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("🌍 Revenue by Market")
        mrev = df_f.groupby('Market')['Revenue'].sum().sort_values(ascending=True).reset_index()
        fig2 = px.bar(mrev, x='Revenue', y='Market', orientation='h',
            color='Revenue', color_continuous_scale='Blues', labels={'Revenue':'Revenue ($)'})
        fig2.update_layout(plot_bgcolor='white', height=320, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        section_header("🔄 On-Time vs Late")
        fig3 = go.Figure(go.Pie(
            labels=['On Time','Late'],
            values=[(df_f['Is_Late']==0).sum(),(df_f['Is_Late']==1).sum()],
            marker_colors=[GREEN, RED], hole=0.5, textinfo='label+percent'))
        fig3.update_layout(height=320)
        st.plotly_chart(fig3, use_container_width=True)

    section_header("📦 Top 10 Categories by Revenue")
    top_cats = df_f.groupby('Category Name')['Revenue'].sum()\
        .sort_values(ascending=False).head(10).reset_index()
    fig4 = px.bar(top_cats.sort_values('Revenue', ascending=True),
        x='Revenue', y='Category Name', orientation='h',
        color='Revenue', color_continuous_scale='Teal',
        labels={'Revenue':'Revenue ($)','Category Name':'Category'})
    fig4.update_layout(plot_bgcolor='white', height=400, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 2 — LATE DELIVERY ANALYSIS
# ═══════════════════════════════════════════════════════════════
elif page == "🚚 Late Delivery Analysis":
    st.markdown('<div class="page-title">🚚 Late Delivery Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Identifying where, when and why deliveries are late</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Late Rate",       f"{df_f['Is_Late'].mean():.1%}", 'kpi-card-red')
    with c2: kpi_card("Late Orders",     f"{df_f['Is_Late'].sum():,}", 'kpi-card-red')
    with c3: kpi_card("Avg Delay",       f"{df_f['Delivery_Delay_Days'].mean():.2f} days", 'kpi-card-amber')
    with c4: kpi_card("Revenue at Risk", f"${df_f['Revenue_At_Risk'].sum():,.0f}", 'kpi-card-red')

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        section_header("📦 Late Rate by Shipping Mode")
        ship = df_f.groupby('Shipping Mode')['Is_Late'].mean().sort_values(ascending=True).reset_index()
        ship['Pct'] = ship['Is_Late'] * 100
        fig = px.bar(ship, x='Pct', y='Shipping Mode', orientation='h',
            color='Pct', color_continuous_scale='RdYlGn_r', text='Pct',
            labels={'Pct':'Late Rate (%)'})
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(plot_bgcolor='white', height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("🌍 Late Rate by Market")
        mkt = df_f.groupby('Market')['Is_Late'].mean().sort_values(ascending=True).reset_index()
        mkt['Pct'] = mkt['Is_Late'] * 100
        fig2 = px.bar(mkt, x='Pct', y='Market', orientation='h',
            color='Pct', color_continuous_scale='RdYlGn_r', text='Pct',
            labels={'Pct':'Late Rate (%)'})
        fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig2.update_layout(plot_bgcolor='white', height=320, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    section_header("📅 Monthly Late Rate Trend")
    ml = df_f.groupby('Order_YearMonth')['Is_Late'].mean().reset_index()
    ml['Pct'] = ml['Is_Late'] * 100
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=ml['Order_YearMonth'], y=ml['Pct'],
        mode='lines+markers', line=dict(color=RED, width=2.5),
        fill='tozeroy', fillcolor='rgba(226,75,74,0.1)', name='Late Rate %'))
    fig3.add_hline(y=50, line_dash='dash', line_color='gray', annotation_text='50% Benchmark')
    fig3.update_layout(xaxis_title='Month', yaxis_title='Late Rate (%)',
        plot_bgcolor='white', height=360)
    st.plotly_chart(fig3, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("📊 Delay Distribution")
        fig4 = px.histogram(df_f, x='Delivery_Delay_Days', nbins=30,
            color_discrete_sequence=[BLUE],
            labels={'Delivery_Delay_Days':'Delay (days)'})
        fig4.add_vline(x=0, line_dash='dash', line_color=RED)
        fig4.update_layout(plot_bgcolor='white', height=320)
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        section_header("📦 Top 10 Categories by Late Rate")
        cat_late = df_f.groupby('Category Name')['Is_Late'].mean()\
            .sort_values(ascending=False).head(10).reset_index()
        cat_late['Pct'] = cat_late['Is_Late'] * 100
        fig5 = px.bar(cat_late.sort_values('Pct', ascending=True),
            x='Pct', y='Category Name', orientation='h',
            color='Pct', color_continuous_scale='Reds',
            labels={'Pct':'Late Rate (%)','Category Name':'Category'})
        fig5.update_layout(plot_bgcolor='white', height=320, coloraxis_showscale=False)
        st.plotly_chart(fig5, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 3 — SUPPLIER RISK
# ═══════════════════════════════════════════════════════════════
elif page == "⚠️ Supplier Risk":
    st.markdown('<div class="page-title">⚠️ Supplier Risk Segmentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">K-Means clustering of 23 supply regions into Low / Medium / High risk tiers</div>', unsafe_allow_html=True)

    high = supplier[supplier['Risk_Tier']=='High Risk']
    low  = supplier[supplier['Risk_Tier']=='Low Risk']

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("High Risk Regions",      f"{len(high)} / {len(supplier)}", 'kpi-card-red')
    with c2: kpi_card("High Risk Rev at Risk",  f"${high['Revenue_At_Risk'].sum():,.0f}", 'kpi-card-red')
    with c3: kpi_card("Avg Risk Score",         f"{supplier['Risk_Score'].mean():.1f}/100", 'kpi-card-amber')
    with c4: kpi_card("Low Risk Regions",       f"{len(low)} / {len(supplier)}", 'kpi-card-green')

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📊 Risk Score by Region")
    fig = px.bar(supplier.sort_values('Risk_Score', ascending=True),
        x='Risk_Score', y='Order Region', orientation='h',
        color='Risk_Tier', color_discrete_map=RISK_COLORS,
        text='Risk_Score', labels={'Risk_Score':'Risk Score (0–100)','Order Region':'Region'})
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(plot_bgcolor='white', height=580)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("🔵 Risk Landscape Bubble Chart")
        fig2 = px.scatter(supplier, x='Late_Rate', y='Avg_Delay_Days',
            size='Total_Revenue', color='Risk_Tier',
            color_discrete_map=RISK_COLORS, text='Order Region',
            title='Late Rate vs Avg Delay (bubble = revenue)',
            labels={'Late_Rate':'Late Rate','Avg_Delay_Days':'Avg Delay (days)'},
            hover_data=['Risk_Score','Total_Orders'])
        fig2.update_traces(textposition='top center')
        fig2.update_layout(plot_bgcolor='white', height=420)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        section_header("💰 Revenue at Risk by Tier")
        tr = supplier.groupby('Risk_Tier').agg(
            Safe=('Total_Revenue','sum'), Risk=('Revenue_At_Risk','sum')).reset_index()
        tr['Safe'] = tr['Safe'] - tr['Risk']
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=tr['Risk_Tier'], y=tr['Safe'],
            name='Safe Revenue', marker_color=GREEN))
        fig3.add_trace(go.Bar(x=tr['Risk_Tier'], y=tr['Risk'],
            name='At Risk', marker_color=RED))
        fig3.update_layout(barmode='stack', plot_bgcolor='white', height=420)
        st.plotly_chart(fig3, use_container_width=True)

    section_header("📋 Full Supplier Risk Scorecard")
    cols = ['Order Region','Risk_Tier','Risk_Score','Late_Rate',
            'Avg_Delay_Days','Cancel_Rate','Total_Orders','Total_Revenue','Revenue_At_Risk']
    cols = [c for c in cols if c in supplier.columns]
    s = supplier[cols].sort_values('Risk_Score', ascending=False).copy()
    s['Late_Rate']       = s['Late_Rate'].apply(lambda x: f'{x:.1%}')
    s['Cancel_Rate']     = s['Cancel_Rate'].apply(lambda x: f'{x:.1%}')
    s['Total_Revenue']   = s['Total_Revenue'].apply(lambda x: f'${x:,.0f}')
    s['Revenue_At_Risk'] = s['Revenue_At_Risk'].apply(lambda x: f'${x:,.0f}')
    s['Risk_Score']      = s['Risk_Score'].apply(lambda x: f'{x:.1f}')
    s['Avg_Delay_Days']  = s['Avg_Delay_Days'].apply(lambda x: f'{x:.2f}')
    st.dataframe(s, use_container_width=True, height=420)

# ═══════════════════════════════════════════════════════════════
# PAGE 4 — DEMAND FORECAST
# ═══════════════════════════════════════════════════════════════
elif page == "📈 Demand Forecast":
    st.markdown('<div class="page-title">📈 Demand Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Facebook Prophet model — 92.8% accuracy | 6-month forward forecast</div>', unsafe_allow_html=True)

    peak_month  = forecast_6m.loc[forecast_6m['Forecast_Orders'].idxmax(), 'Month']
    total_fc    = forecast_6m['Forecast_Orders'].sum()
    avg_fc      = forecast_6m['Forecast_Orders'].mean()

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Forecast Accuracy",    "92.8%", 'kpi-card-green')
    with c2: kpi_card("6-Month Total Orders", f"{total_fc:,.0f}")
    with c3: kpi_card("Peak Demand Month",    peak_month, 'kpi-card-amber')
    with c4: kpi_card("Avg Monthly Forecast", f"{avg_fc:,.0f} orders")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📊 Full Forecast with Confidence Interval")

    daily_hist = df.groupby(df['Order Date'].dt.date).size().reset_index()
    daily_hist.columns = ['ds','y']
    daily_hist['ds'] = pd.to_datetime(daily_hist['ds'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_full['ds'], forecast_full['ds'][::-1]]),
        y=pd.concat([forecast_full['yhat_upper'], forecast_full['yhat_lower'][::-1]]),
        fill='toself', fillcolor='rgba(59,139,212,0.12)',
        line=dict(color='rgba(255,255,255,0)'), name='Confidence Interval'))
    fig.add_trace(go.Scatter(x=daily_hist['ds'], y=daily_hist['y'],
        mode='lines', name='Actual Orders',
        line=dict(color=BLUE, width=1), opacity=0.7))
    fig.add_trace(go.Scatter(x=forecast_full['ds'], y=forecast_full['yhat'],
        mode='lines', name='Forecast',
        line=dict(color=RED, width=2, dash='dash')))
    fig.update_layout(xaxis_title='Date', yaxis_title='Daily Orders',
        plot_bgcolor='white', height=440)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("📅 6-Month Forecast Summary")
        fig2 = go.Figure(go.Bar(
            x=forecast_6m['Month'], y=forecast_6m['Forecast_Orders'],
            marker_color=BLUE,
            text=forecast_6m['Forecast_Orders'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            error_y=dict(type='data', symmetric=False,
                array=forecast_6m['Upper_Bound']-forecast_6m['Forecast_Orders'],
                arrayminus=forecast_6m['Forecast_Orders']-forecast_6m['Lower_Bound'],
                color='gray')))
        fig2.update_layout(plot_bgcolor='white', height=380)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        section_header("📋 Forecast Detail")
        fd = forecast_6m.copy()
        fd['Forecast_Orders'] = fd['Forecast_Orders'].apply(lambda x: f'{x:,.0f}')
        fd['Lower_Bound']     = fd['Lower_Bound'].apply(lambda x: f'{x:,.0f}')
        fd['Upper_Bound']     = fd['Upper_Bound'].apply(lambda x: f'{x:,.0f}')
        st.dataframe(fd, use_container_width=True, height=380)

# ═══════════════════════════════════════════════════════════════
# PAGE 5 — BUSINESS IMPACT
# ═══════════════════════════════════════════════════════════════
elif page == "💰 Business Impact":
    st.markdown('<div class="page-title">💰 Business Impact & ROI</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Financial quantification of supply chain inefficiencies and ML intervention value</div>', unsafe_allow_html=True)

    row = impact.iloc[0]
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Total Cost of Delays", f"${row['Total_Cost_Late']:,.0f}", 'kpi-card-red')
    with c2: kpi_card("Orders Preventable",   f"{row['Orders_Preventable']:,.0f}", 'kpi-card-green')
    with c3: kpi_card("Total Savings",        f"${row['Total_Savings']:,.0f}", 'kpi-card-green')
    with c4: kpi_card("Net ROI",              f"{row['Net_ROI_Pct']:.0f}%", 'kpi-card-green')

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        section_header("💸 Cost Breakdown")
        rev_at_risk = row['Revenue_At_Risk']
        late_orders = row['Late_Orders']
        retention   = rev_at_risk * 0.05
        expediting  = late_orders * 15
        cs_cost     = late_orders * 8
        brand       = rev_at_risk * 0.02
        fig = px.pie(
            names=['Retention Loss','Expediting','Customer Service','Brand Damage'],
            values=[retention, expediting, cs_cost, brand],
            color_discrete_sequence=[RED, AMBER, BLUE, PURPLE], hole=0.45)
        fig.update_traces(textinfo='label+percent')
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("📈 ROI Analysis")
        impl      = row['Impl_Cost']
        savings   = row['Total_Savings']
        net       = savings - impl
        fig2 = go.Figure(go.Bar(
            x=['Implementation Cost','Total Savings','Net Benefit'],
            y=[impl, savings, net],
            marker_color=[RED, GREEN, BLUE],
            text=[f'${v:,.0f}' for v in [impl, savings, net]],
            textposition='outside'))
        fig2.update_layout(yaxis_title='Amount ($)',
            plot_bgcolor='white', height=380,
            title=f'ROI: {row["Net_ROI_Pct"]:.0f}%')
        st.plotly_chart(fig2, use_container_width=True)

    section_header("📋 Executive Summary")
    st.dataframe(exec_summary, use_container_width=True, height=520)

# ═══════════════════════════════════════════════════════════════
# PAGE 6 — LATE DELIVERY PREDICTOR
# ═══════════════════════════════════════════════════════════════
elif page == "🔮 Late Delivery Predictor":
    st.markdown('<div class="page-title">🔮 Late Delivery Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enter order details to predict delivery risk — Random Forest (ROC-AUC: 0.741)</div>', unsafe_allow_html=True)

    if not models:
        st.error("Models not loaded. Ensure all .pkl files exist in models/ folder.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📦 Order Details")
            shipping_mode    = st.selectbox("Shipping Mode",
                ['Standard Class','Second Class','First Class','Same Day'])
            order_qty        = st.number_input("Order Quantity", min_value=1, max_value=100, value=5)
            order_total      = st.number_input("Order Total ($)", min_value=0.0, value=150.0, step=10.0)
            product_price    = st.number_input("Product Price ($)", min_value=0.0, value=50.0, step=5.0)

        with col2:
            st.markdown("#### 🌍 Location & Category")
            market           = st.selectbox("Market",
                sorted(df['Market'].dropna().unique().tolist()))
            order_region     = st.selectbox("Order Region",
                sorted(df['Order Region'].dropna().unique().tolist()))
            category         = st.selectbox("Category",
                sorted(df['Category Name'].dropna().unique().tolist()))
            customer_segment = st.selectbox("Customer Segment",
                sorted(df['Customer Segment'].dropna().unique().tolist()))

        with col3:
            st.markdown("#### 📅 Order Date")
            order_date       = st.date_input("Order Date", value=datetime.date.today())
            scheduled_days   = st.number_input("Scheduled Shipping Days", min_value=1, max_value=10, value=4)
            department       = st.selectbox("Department",
                sorted(df['Department Name'].dropna().unique().tolist()))

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔮 Predict Delivery Risk", type="primary", use_container_width=True):
            try:
                feature_config = models.get('feature_config', {})
                encoders       = models.get('encoders', {})
                late_model     = models.get('late_model')
                order_dt       = pd.Timestamp(order_date)

                input_data = {
                    'Shipping Mode'                 : shipping_mode,
                    'Market'                        : market,
                    'Order Region'                  : order_region,
                    'Category Name'                 : category,
                    'Customer Segment'              : customer_segment,
                    'Department Name'               : department,
                    'Days for shipment (scheduled)' : scheduled_days,
                    'Order Item Quantity'            : order_qty,
                    'Order Item Total'              : order_total,
                    'Order Profit Per Order'        : order_total * 0.1,
                    'Product Price'                 : product_price,
                    'Order_Month'                   : order_dt.month,
                    'Order_Quarter'                 : order_dt.quarter,
                    'Order_DayOfWeek'               : order_dt.dayofweek,
                    'Is_Weekend'                    : int(order_dt.dayofweek >= 5),
                }

                input_df = pd.DataFrame([input_data])
                cat_features = feature_config.get('categorical_features', [])
                for col in cat_features:
                    if col in encoders and col in input_df.columns:
                        le  = encoders[col]
                        val = input_df[col].astype(str).iloc[0]
                        input_df[col] = le.transform([val]) if val in le.classes_ else 0

                all_features = [f for f in feature_config.get('all_features', [])
                                if f in input_df.columns]
                prob       = late_model.predict_proba(input_df[all_features])[0][1]
                prediction = late_model.predict(input_df[all_features])[0]

                st.markdown("---")
                r1, r2, r3 = st.columns(3)

                with r1:
                    if prediction == 1:
                        st.error(f"### 🔴 HIGH RISK — LIKELY LATE\nProbability: **{prob:.1%}**")
                    elif prob > 0.35:
                        st.warning(f"### 🟡 MEDIUM RISK\nProbability: **{prob:.1%}**")
                    else:
                        st.success(f"### 🟢 LOW RISK — ON TIME\nProbability: **{prob:.1%}**")

                with r2:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=prob * 100,
                        title={'text': "Late Delivery Risk %"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': RED if prob > 0.5 else (AMBER if prob > 0.35 else GREEN)},
                            'steps': [
                                {'range': [0, 35],  'color': '#D4EDDA'},
                                {'range': [35, 50], 'color': '#FFF3CD'},
                                {'range': [50, 100],'color': '#FFE5E5'}
                            ],
                            'threshold': {'line': {'color': 'black', 'width': 3},
                                          'thickness': 0.75, 'value': 50}
                        }
                    ))
                    fig_gauge.update_layout(height=280)
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with r3:
                    st.markdown("#### 💡 Recommendations")
                    if prediction == 1:
                        st.markdown("""
                        - 🚨 Flag for priority routing
                        - 📞 Alert supplier immediately
                        - 📦 Upgrade shipping mode
                        - 📧 Proactively notify customer
                        - 🔄 Prepare backup inventory
                        """)
                    elif prob > 0.35:
                        st.markdown("""
                        - ⚠️ Monitor order closely
                        - 📊 Check supplier capacity
                        - 📋 Add to watchlist
                        - 📅 Confirm shipping schedule
                        """)
                    else:
                        st.markdown("""
                        - ✅ Order looks good
                        - 📦 Standard processing
                        - 📧 Send confirmation to customer
                        """)

            except Exception as e:
                st.error(f"Prediction error: {e}")
                st.info("Make sure all model .pkl files exist in the models/ folder.")
