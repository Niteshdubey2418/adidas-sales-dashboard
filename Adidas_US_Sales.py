import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
st.set_page_config(
    page_title="Adidas US Sales Dashboard",
    layout="wide")

st.title("👟 Adidas US Sales Dashboard")
st.caption("Built using Streamlit | Data Source: Adidas US Sales | Designed for Business Intelligence Insights")
st.subheader("Overview")
st.markdown("This dashboard shows sales insights.")


# Load Data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "Adidas US Sales Dashboard.xlsx")
    return pd.read_excel(file_path)

df = load_data()

def format_millions(value):
    return f"${value/1_000_000:,.2f}M"

def format_thousands(value):
    return f"{value/1_000:,.1f}K"

def format_number(value):
    return f"{value:,.0f}"
    

# Convert Invoice Date to datetime
df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])

df["Year"] = df["Invoice Date"].dt.year
df["Quarter"] = "Q" + df["Invoice Date"].dt.quarter.astype(str)

#   SIDEBARS
st.sidebar.title("🔍 Dashboard Filters")
st.sidebar.markdown("Use filters to explore sales performance")

st.sidebar.header("🔍 Filters")

region = st.sidebar.multiselect( "Select Region",
                                 options=df["Region"].unique(),
                                 default=df["Region"].unique() )



product = st.sidebar.multiselect(
    "Select Product",
    options=df["Product"].unique(),
    default=df["Product"].unique())

year = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique()))
filtered_year_df = df[df["Year"].isin(year)]


quarter = st.sidebar.multiselect(
    "Select Quarter",
    options=sorted(df["Quarter"].unique()),
    default=sorted(df["Quarter"].unique()))
filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Product"].isin(product)) &
    (df["Year"].isin(year)) &
    (df["Quarter"].isin(quarter))]



# KPI CARDS

# KPI CARDS
col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Total Sales"].sum()
units_sold = filtered_df["Units Sold"].sum()
total_profit = filtered_df["Operating Profit"].sum()

col1.metric("💰 Total Sales", format_millions(total_sales))
col2.metric("📦 Units Sold", format_thousands(units_sold))
col3.metric("📈 Operating Profit", format_millions(total_profit))

weighted_margin = total_profit / total_sales if total_sales != 0 else 0
col4.metric("📊 Weighted Profit Margin", f"{weighted_margin:.2%}")




# TOP PERFORMING PRODUCTS
product_sales = (
    filtered_df
    .groupby("Product")["Total Sales"]
    .sum()
    .sort_values(ascending=False)   # 👈 This is the important line
    .reset_index())

if not product_sales.empty:
    best_product = product_sales.iloc[0]
    worst_product = product_sales.iloc[-1]

    st.markdown("### 🏅 Performance Highlights")
    st.write(f"Top Performing Product: **{best_product['Product']}** (${best_product['Total Sales']:,.0f})")
    st.write(f"Lowest Performing Product: **{worst_product['Product']}** (${worst_product['Total Sales']:,.0f})")



# MONTH OVER MONTH SALES TREND
monthly_sales = (
    filtered_df
    .resample("M", on="Invoice Date")["Total Sales"]
    .sum()
    .reset_index())

fig_mom = px.line(
    monthly_sales,
    x="Invoice Date",
    y="Total Sales",
    markers=True,
    title="📅 Monthly Sales Trend")
st.plotly_chart(fig_mom, use_container_width=True)


# SALES BY PRODUCTS
product_sales = (
    filtered_df
    .groupby("Product")["Total Sales"]
    .sum()
    .sort_values(ascending=False)   # 👈 This is the important line
    .reset_index())

fig_product = px.bar(
    product_sales,
    x="Product",
    y="Total Sales",
    title="🧾 Sales by Product",
    text_auto=True)

st.plotly_chart(fig_product, use_container_width=True)
product_sales["Revenue %"] = (
    product_sales["Total Sales"] /
    product_sales["Total Sales"].sum()) * 100
st.dataframe(product_sales)


# PROFIT MARGIN
product_margin = (
    filtered_df.groupby("Product")
    .agg({
        "Total Sales": "sum",
        "Operating Profit": "sum"})
    .reset_index())

product_margin["Profit Margin %"] = (
    product_margin["Operating Profit"] / product_margin["Total Sales"]) * 100

fig_margin = px.bar(
    product_margin.sort_values("Profit Margin %", ascending=False),
    x="Product",
    y="Profit Margin %",
    title="📈 Profit Margin % by Product",
    text_auto=True)

st.plotly_chart(fig_margin, use_container_width=True)



# SALES BY REGION AND PROFIT BY RETAILER
col1, col2 = st.columns(2)

region_sales = filtered_df.groupby("Region")["Total Sales"].sum().reset_index()
fig_region = px.pie(region_sales, names="Region", values="Total Sales", title="🌎 Sales by Region")


top_region = region_sales.sort_values("Total Sales", ascending=False).iloc[0]
bottom_region = region_sales.sort_values("Total Sales", ascending=True).iloc[0]

st.markdown("### 🌎 Regional Performance Summary")
st.write(f"Top Region: **{top_region['Region']}** (${top_region['Total Sales']:,.0f})")
st.write(f"Lowest Region: **{bottom_region['Region']}** (${bottom_region['Total Sales']:,.0f})")



retailer_profit = (
    filtered_df
    .groupby("Retailer")["Operating Profit"]
    .sum()
    .sort_values(ascending=False)  # 👈 Important line
    .reset_index())
fig_retailer = px.bar(retailer_profit, x="Retailer", y="Operating Profit", title="🏪 Profit by Retailer")

col1.plotly_chart(fig_region, use_container_width=True)
col2.plotly_chart(fig_retailer, use_container_width=True)

# FILTERED DATA TABLE
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df)

# DOWNLOAD THE DATA
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name='filtered_sales.csv',
    mime='text/csv')


# WHICH STATE CONTRIBUTE THE MOST REVENUE
top_states = (
    filtered_df.groupby("State")["Total Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index())

fig_states = px.bar(
    top_states,
    x="State",
    y="Total Sales",
    title="🏆 Top 5 States by Sales",
    text_auto=True)

st.plotly_chart(fig_states, use_container_width=True)


# TOP 5 PRODUCTS BY UNITS SOLD

top_products = (
    filtered_df.groupby("Product")["Units Sold"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index())

fig_products = px.bar(
    top_products,
    x="Product",
    y="Units Sold",
    title="📦 Top 5 Products by Units Sold",
    text_auto=True)

st.plotly_chart(fig_products, use_container_width=True)



# Where do customers buy more — Online, Outlet, or In-Store?
sales_method = (
    filtered_df.groupby("Sales Method")["Total Sales"]
    .sum()
    .reset_index())

fig_method = px.pie(
    sales_method,
    names="Sales Method",
    values="Total Sales",
    title="🛒 Sales by Method")

st.plotly_chart(fig_method, use_container_width=True)


# UNITS SOLD VS PROFIT

scatter_df = (
    filtered_df.groupby("Product")
    .agg({
        "Units Sold": "sum",
        "Operating Profit": "sum"
    })
    .reset_index())

fig_scatter = px.scatter(
    scatter_df,
    x="Units Sold",
    y="Operating Profit",
    size="Operating Profit",
    color="Product",
    title="📦 Units Sold vs Operating Profit",
    hover_name="Product")

st.plotly_chart(fig_scatter, use_container_width=True)

profit_units = (
    filtered_df.groupby("Product")
    .agg({
        "Units Sold": "sum",
        "Operating Profit": "sum"
    })
    .reset_index())
correlation_profit_units = profit_units["Units Sold"].corr(
    profit_units["Operating Profit"]
)
st.write(
    f"📊 Correlation between Units Sold and Operating Profit: "
    f"**{correlation_profit_units:.2f}**"
)
if correlation_profit_units > 0.7:
    st.success("Strong positive relationship: Higher sales volume drives higher profit.")
elif correlation_profit_units > 0.3:
    st.info("Moderate positive relationship between units sold and profit.")
elif correlation_profit_units > 0:
    st.warning("Weak positive relationship: High volume does not strongly translate to profit.")
else:
    st.error("Negative relationship detected: High sales volume may not be profitable.")




# Are higher-priced products selling less?
price_units = (
    filtered_df.groupby("Product")
    .agg({
        "Price per Unit": "mean",
        "Units Sold": "sum"
    })
    .reset_index())

fig_price = px.scatter(
    price_units,
    x="Price per Unit",
    y="Units Sold",
    size="Units Sold",
    title="💲 Price vs Units Sold",
    hover_name="Product")

st.plotly_chart(fig_price, use_container_width=True)
# st.write("Higher prices do impact the sale")
correlation = price_units["Price per Unit"].corr(price_units["Units Sold"])
st.write(f"📊 Correlation between Price and Units Sold: **{correlation:.2f}**")




# SALES CONCENTRATION
pareto_df = (
    filtered_df.groupby("State")["Total Sales"]
    .sum()
    .sort_values(ascending=False)
    .reset_index())

pareto_df["Cumulative %"] = pareto_df["Total Sales"].cumsum() / pareto_df["Total Sales"].sum()

fig_pareto = px.line(
    pareto_df,
    x="State",
    y="Cumulative %",
    title="📊 Sales Concentration by State (Pareto Analysis)")

st.plotly_chart(fig_pareto, use_container_width=True)

top_20_states = pareto_df[pareto_df["Cumulative %"] <= 0.8]
st.write(f"📌 {len(top_20_states)} states contribute to 80% of revenue.")

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()
    
top_region = region_sales.sort_values("Total Sales", ascending=False).iloc[0]["Region"]




st.markdown("## 🧠 Key Insights")

st.write("""
• The West region contributes the highest revenue.\n
• Online sales show higher margins than in-store.\n
• A few states account for the majority of sales (Pareto effect).
""")





