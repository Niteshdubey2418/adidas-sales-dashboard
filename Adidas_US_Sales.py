import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
st.set_page_config(
    page_title="Adidas US Sales Dashboard",
    layout="wide")

st.title("👟 Adidas US Sales Dashboard")

st.subheader("Overview")
st.markdown("This dashboard shows sales insights.")

# Load Data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "Adidas US Sales Dashboard.xlsx")
    return pd.read_excel(file_path)

df = load_data()


# Convert Invoice Date to datetime
df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])

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

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Invoice Date"].min(), df["Invoice Date"].max()])


filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Product"].isin(product)) &
    (df["Invoice Date"] >= pd.to_datetime(date_range[0])) &
    (df["Invoice Date"] <= pd.to_datetime(date_range[1]))]



# KPI CARDS

def format_millions(value):
    return f"${value/1_000_000:.2f}M"

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰Total Sales ($)",f"{filtered_df['Total Sales'].sum():,.0f}")
col2.metric("📦Units Sold", f"{filtered_df['Units Sold'].sum():,}")
col3.metric("📈Operating Profit ($)", f"{filtered_df['Operating Profit'].sum():,.0f}")
col4.metric("📊Avg Margin", f"{filtered_df['Operating Margin'].mean():.2%}")


# MONTH OVER MONTH SALES TREND
monthly_sales = (
    filtered_df
    .resample("M", on="Invoice Date")["Total Sales"]
    .sum()
    .reset_index()
)

fig_mom = px.line(
    monthly_sales,
    x="Invoice Date",
    y="Total Sales",
    markers=True,
    title="📅 Monthly Sales Trend"
)

st.plotly_chart(fig_mom, use_container_width=True)


# SALES BY PRODUCTS
product_sales = (
    filtered_df
    .groupby("Product")["Total Sales"]
    .sum()
    .sort_values(ascending=False)   # 👈 This is the important line
    .reset_index()
)

fig_product = px.bar(
    product_sales,
    x="Product",
    y="Total Sales",
    title="🧾 Sales by Product",
    text_auto=True)

st.plotly_chart(fig_product, use_container_width=True)




# SALES BY REGION AND PROFIT BY RETAILER
col1, col2 = st.columns(2)

region_sales = filtered_df.groupby("Region")["Total Sales"].sum().reset_index()
fig_region = px.pie(region_sales, names="Region", values="Total Sales", title="🌎 Sales by Region")

retailer_profit = (
    filtered_df
    .groupby("Retailer")["Operating Profit"]
    .sum()
    .sort_values(ascending=False)  # 👈 Important line
    .reset_index()
)
fig_retailer = px.bar(retailer_profit, x="Retailer", y="Operating Profit", title="🏪 Profit by Retailer")

col1.plotly_chart(fig_region, use_container_width=True)
col2.plotly_chart(fig_retailer, use_container_width=True)

# FILTERED DATA TABLE
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df)



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




st.markdown("## 🧠 Key Insights")

st.write("""
• The West region contributes the highest revenue.\n
• Online sales show higher margins than in-store.\n
• A few states account for the majority of sales (Pareto effect).
""")



