import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(page_title="UK MOD Spend Analysis", page_icon="📊", layout="wide")
# 作者信息

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('UK MOD Spend Data - Jan 20XXCO.xlsx')
    df.columns = ['Expense Type (Category)', 'Expense Area (User/BU)', 'Supplier', 'Invoice Value (GBP)']
    return df

df = load_data()

# Title and introduction
st.title("🏛️ UK Ministry of Defence Spend Analysis Dashboard")
st.markdown("""
**Author:** CHEN JUNG-LU  
**Email:** E1582484@u.nus.edu 
""")

st.markdown("""
### Executive Summary
This dashboard provides comprehensive analysis of UK Ministry of Defence procurement spending data. 
Explore spending patterns across different categories, business units, and suppliers to identify 
opportunities for cost optimization and strategic procurement decisions.
""")

# Enhanced Filter Section
with st.expander("🔍 **Data Filters** - Click to customize your analysis", expanded=False):
    st.markdown("**Filter the data to focus on specific areas of interest:**")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("**📂 Expense Categories**")
        filter_method_cat = st.radio(
            "Filter method for categories:",
            ["Top Categories (Default)", "Search & Select", "Select All"],
            key="cat_method",
            help="Choose how to filter expense categories"
        )
        
        if filter_method_cat == "Top Categories (Default)":
            top_n_cat = st.slider("Number of top categories by spend:", 5, 15, 10)
            top_categories = df.groupby('Expense Type (Category)')['Invoice Value (GBP)'].sum().nlargest(top_n_cat).index.tolist()
            selected_categories = st.multiselect(
                "Selected categories:",
                options=top_categories,
                default=top_categories,
                help="Top categories by total spend"
            )
        elif filter_method_cat == "Search & Select":
            search_cat = st.text_input("🔍 Search categories:", placeholder="Type to search...")
            available_cats = df['Expense Type (Category)'].unique()
            if search_cat:
                available_cats = [cat for cat in available_cats if search_cat.lower() in cat.lower()]
            selected_categories = st.multiselect(
                "Select categories:",
                options=available_cats,
                default=available_cats[:5] if len(available_cats) <= 5 else available_cats[:3]
            )
        else:  # Select All for categories
            selected_categories = st.multiselect(
                "Select categories:",
                options=df['Expense Type (Category)'].unique(),
                default=df['Expense Type (Category)'].unique()  # Changed from [:5] to select ALL
            )
    
    with col2:
        st.markdown("**🏢 Expense Areas**")
        filter_method_area = st.radio(
            "Filter method for expense areas:",
            ["Top Areas (Default)", "Search & Select", "Select All"],
            key="area_method",
            help="Choose how to filter expense areas"
        )
        
        if filter_method_area == "Top Areas (Default)":
            top_n_area = st.slider("Number of top areas by spend:", 5, 15, 8)
            top_areas = df.groupby('Expense Area (User/BU)')['Invoice Value (GBP)'].sum().nlargest(top_n_area).index.tolist()
            selected_areas = st.multiselect(
                "Selected areas:",
                options=top_areas,
                default=top_areas,
                help="Top areas by total spend"
            )
        elif filter_method_area == "Search & Select":
            search_area = st.text_input("🔍 Search areas:", placeholder="Type to search...")
            available_areas = df['Expense Area (User/BU)'].unique()
            if search_area:
                available_areas = [area for area in available_areas if search_area.lower() in area.lower()]
            selected_areas = st.multiselect(
                "Select areas:",
                options=available_areas,
                default=available_areas[:5] if len(available_areas) <= 5 else available_areas[:3]
            )
        else:  # Select All for areas
            selected_areas = st.multiselect(
                "Select areas:",
                options=df['Expense Area (User/BU)'].unique(),
                default=df['Expense Area (User/BU)'].unique()  # Changed from [:5] to select ALL
            )
    
    with col3:
        st.markdown("**⚙️ Actions**")
        if st.button("🔄 Reset Filters", help="Reset all filters to default"):
            st.rerun()
        
        st.markdown("**📊 Quick Stats**")
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Categories", len(df['Expense Type (Category)'].unique()))
        st.metric("Areas", len(df['Expense Area (User/BU)'].unique()))

# Apply filters
filtered_df = df[
    (df['Expense Type (Category)'].isin(selected_categories)) &
    (df['Expense Area (User/BU)'].isin(selected_areas))
]

# Data loading status
if len(filtered_df) == 0:
    st.error("⚠️ No data matches your current filters. Please adjust your selection.")
    st.stop()
else:
    st.success(f"✅ Loaded {len(filtered_df):,} records matching your filters ({len(filtered_df)/len(df)*100:.1f}% of total data)")

# Main Dashboard Content
st.markdown("---")

# Key Performance Indicators
st.header("📈 Key Performance Indicators")
st.markdown("""
**Understanding the Numbers:** These KPIs provide a high-level overview of MOD spending patterns. 
Total spend indicates the scale of procurement, while supplier concentration metrics help assess 
market competition and potential risks from over-reliance on specific suppliers.
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_spend = filtered_df['Invoice Value (GBP)'].sum()
    st.metric(
        "💰 Total Spend", 
        f"£{total_spend:,.0f}",
        help="Total procurement spending in the filtered dataset"
    )

with col2:
    unique_suppliers = filtered_df['Supplier'].nunique()
    st.metric(
        "🏭 Unique Suppliers", 
        f"{unique_suppliers:,}",
        help="Number of distinct suppliers in the filtered data"
    )

with col3:
    avg_invoice = filtered_df['Invoice Value (GBP)'].mean()
    st.metric(
        "📄 Average Invoice", 
        f"£{avg_invoice:,.0f}",
        help="Average invoice value across all transactions"
    )

with col4:
    top_supplier_share = (filtered_df.groupby('Supplier')['Invoice Value (GBP)'].sum().max() / total_spend * 100)
    st.metric(
        "🎯 Top Supplier Share", 
        f"{top_supplier_share:.1f}%",
        help="Percentage of total spend from the largest supplier"
    )

# Main visualizations
st.header("📊 Spending Analysis")

# Category Analysis
st.subheader("💼 Spending by Category")
st.markdown("""
**Analysis Insight:** This visualization shows how MOD spending is distributed across different expense categories. 
Large categories may indicate core operational needs, while smaller categories might represent specialized requirements. 
Uneven distribution could suggest opportunities for category management and strategic sourcing.
""")

category_spend = filtered_df.groupby('Expense Type (Category)')['Invoice Value (GBP)'].sum().sort_values(ascending=True)
fig_cat = px.bar(
    x=category_spend.values, 
    y=category_spend.index,
    orientation='h',
    title="Total Spend by Expense Category",
    labels={'x': 'Total Spend (£)', 'y': 'Expense Category'},
    color=category_spend.values,
    color_continuous_scale='Blues'
)
fig_cat.update_layout(height=max(400, len(category_spend) * 30))
st.plotly_chart(fig_cat, use_container_width=True)

# Supplier Analysis
st.subheader("🏭 Top Suppliers Analysis")
st.markdown("""
**Strategic Procurement Insight:** Supplier concentration analysis is crucial for risk management. 
High concentration (few suppliers handling large spend) may indicate dependency risks but could also 
reflect successful strategic partnerships. The Herfindahl-Hirschman Index (HHI) measures market concentration:
- **HHI < 1,500**: Competitive market
- **HHI 1,500-2,500**: Moderately concentrated
- **HHI > 2,500**: Highly concentrated market
""")

col1, col2 = st.columns(2)

with col1:
    # Top suppliers chart
    top_suppliers = filtered_df.groupby('Supplier')['Invoice Value (GBP)'].sum().nlargest(15)
    fig_suppliers = px.bar(
        x=top_suppliers.values,
        y=top_suppliers.index,
        orientation='h',
        title="Top 15 Suppliers by Spend",
        labels={'x': 'Total Spend (£)', 'y': 'Supplier'},
        color=top_suppliers.values,
        color_continuous_scale='Reds'
    )
    fig_suppliers.update_layout(height=500)
    st.plotly_chart(fig_suppliers, use_container_width=True)

with col2:
    # HHI calculation and display
    supplier_spend = filtered_df.groupby('Supplier')['Invoice Value (GBP)'].sum()
    market_shares = (supplier_spend / supplier_spend.sum()) * 100
    hhi = (market_shares ** 2).sum()
    
    # HHI interpretation
    if hhi < 1500:
        hhi_interpretation = "Competitive Market 🟢"
        hhi_color = "green"
        hhi_explanation = "Low concentration indicates a competitive supplier market with good negotiating position for MOD."
    elif hhi < 2500:
        hhi_interpretation = "Moderately Concentrated 🟡"
        hhi_color = "orange"
        hhi_explanation = "Moderate concentration suggests some supplier dominance but still competitive."
    else:
        hhi_interpretation = "Highly Concentrated 🔴"
        hhi_color = "red"
        hhi_explanation = "High concentration indicates potential supplier dependency risks."
    
    st.markdown(f"**Market Concentration Analysis**")
    st.markdown(f"**HHI Score:** {hhi:.0f}")
    st.markdown(f"**Status:** {hhi_interpretation}")
    st.markdown(f"*{hhi_explanation}*")
    
    # Top 5 suppliers market share
    top_5_share = market_shares.nlargest(5).sum()
    st.markdown(f"**Top 5 Suppliers Control:** {top_5_share:.1f}% of market")
    
    # Supplier distribution pie chart
    top_10_suppliers = supplier_spend.nlargest(10)
    others_spend = supplier_spend.sum() - top_10_suppliers.sum()
    
    pie_data = list(top_10_suppliers.values) + [others_spend]
    pie_labels = list(top_10_suppliers.index) + ['Others']
    
    fig_pie = px.pie(
        values=pie_data,
        names=pie_labels,
        title="Supplier Market Share Distribution"
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# Expense Area Analysis
st.subheader("🏢 Spending by Business Unit/Area")
st.markdown("""
**Organizational Insight:** This analysis reveals how different MOD business units and operational areas 
contribute to overall spending. Understanding area-wise spending helps in:
- **Budget allocation** and planning
- **Identifying high-spend areas** for focused cost management
- **Resource optimization** across different operational units
- **Benchmarking** spending efficiency between similar units
""")

area_spend = filtered_df.groupby('Expense Area (User/BU)')['Invoice Value (GBP)'].sum().sort_values(ascending=False)

# Create hierarchical data for treemap
treemap_data = []
for area, spend in area_spend.items():
    treemap_data.append({
        'ids': area,
        'labels': area,
        'parents': '',
        'values': spend
    })

treemap_df = pd.DataFrame(treemap_data)

# Create treemap with go.Treemap for more control
fig_area = go.Figure(go.Treemap(
    ids=treemap_df['ids'],
    labels=treemap_df['labels'],
    parents=treemap_df['parents'],
    values=treemap_df['values'],
    textinfo="label+value+percent parent",
    hovertemplate='<b>%{label}</b><br>Spend: £%{value:,.0f}<br>Percentage: %{percentParent}<extra></extra>'
))

fig_area.update_layout(
    title="Spending Distribution by Business Unit/Area (Treemap)",
    height=500
)
st.plotly_chart(fig_area, use_container_width=True)

# Category vs Area Heatmap
st.subheader("🔥 Category-Area Spending Heatmap")
st.markdown("""
**Cross-Analysis Insight:** This heatmap reveals the intersection of spending categories and business areas. 
Dark areas indicate high spending combinations, helping identify:
- **Strategic focus areas** where specific units have high category spending
- **Potential consolidation opportunities** across similar categories
- **Unusual spending patterns** that may require investigation
- **Category management opportunities** for high-spend intersections
""")

heatmap_data = filtered_df.pivot_table(
    values='Invoice Value (GBP)', 
    index='Expense Type (Category)', 
    columns='Expense Area (User/BU)', 
    aggfunc='sum', 
    fill_value=0
)

fig_heatmap = px.imshow(
    heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    aspect='auto',
    title="Spending Heatmap: Categories vs Business Areas",
    color_continuous_scale='Blues'
)
fig_heatmap.update_layout(height=max(400, len(heatmap_data.index) * 25))
st.plotly_chart(fig_heatmap, use_container_width=True)

# Raw Data Section
st.header("📋 Detailed Data View")
st.markdown("""
**Data Exploration:** Browse the underlying transaction data that powers all visualizations above. 
Use this section to:
- **Verify specific transactions** and their details
- **Export data** for further analysis
- **Investigate outliers** or unusual patterns
- **Validate insights** from the visualizations
""")

# Summary statistics
col1, col2 = st.columns(2)
with col1:
    st.markdown("**📊 Statistical Summary**")
    st.dataframe(filtered_df['Invoice Value (GBP)'].describe().round(2))

with col2:
    st.markdown("**🔍 Data Quality Metrics**")
    quality_metrics = {
        'Total Records': len(filtered_df),
        'Complete Records': len(filtered_df.dropna()),
        'Missing Values': filtered_df.isnull().sum().sum(),
        'Duplicate Records': filtered_df.duplicated().sum()
    }
    for metric, value in quality_metrics.items():
        st.metric(metric, f"{value:,}")

# Display filtered data
st.markdown("**📋 Transaction Details**")
st.dataframe(
    filtered_df.sort_values('Invoice Value (GBP)', ascending=False),
    use_container_width=True,
    height=400
)

# Download option
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='mod_spend_filtered_data.csv',
    mime='text/csv',
    help="Download the currently filtered dataset for external analysis"
)

# Footer
st.markdown("---")
st.markdown("""
**📝 Dashboard Notes:**
- All monetary values are in British Pounds (GBP)
- Data represents MOD procurement spending for January 20XX
- HHI calculations help assess supplier market concentration
- Use filters to focus analysis on specific categories or business areas
- For questions about specific transactions, refer to the detailed data view
""")
