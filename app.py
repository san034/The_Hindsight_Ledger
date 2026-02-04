from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(page_title="The Hindsight Ledger", page_icon="💰", layout="wide")

# Custom CSS for a "CSE Student" vibe
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    </style>
    """,
    unsafe_allow_html=True,
)


# 1. Data Loading Function
@st.cache_data
def load_data():
    # Loading the specific ~ delimited format
    df = pd.read_csv("bitcoin_data.csv", sep="~")
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "CSV file not found! Please ensure 'bitcoin_data.csv' is in the same folder."
    )
    st.stop()

# Title and Description
st.title("💰 The Hindsight Ledger")
st.subheader("What if you hadn't bought that coffee/gadget and bought Bitcoin instead?")

# 2. Sidebar Inputs
st.sidebar.header("Configuration")
invest_amount = st.sidebar.number_input(
    "Amount Spent (USD)", min_value=1.0, value=100.0
)
invest_date = st.sidebar.date_input(
    "Date of Purchase",
    value=datetime(2017, 12, 17),
    min_value=df["DATE"].min(),
    max_value=df["DATE"].max(),
)

# 3. Calculation Logic
# Find the closest price to the selected date
price_row = df.iloc[(df["DATE"] - pd.Timestamp(invest_date)).abs().argsort()[:1]]
buy_price = price_row["CLOSE"].values[0]
actual_date = price_row["DATE"].dt.strftime("%Y-%m-%d").values[0]

# Get the latest "current" price (the last row in your 2026 dataset)
current_price = df["CLOSE"].iloc[-1]
current_date = df["DATE"].iloc[-1].strftime("%Y-%m-%d")

# Calculate Gains
if buy_price > 0:
    btc_owned = invest_amount / buy_price
    current_value = btc_owned * current_price
    roi = ((current_value - invest_amount) / invest_amount) * 100
else:
    btc_owned = 0
    current_value = 0
    roi = 0

# 4. Display Results
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Price on " + actual_date, f"${buy_price:,.2f}")

with col2:
    st.metric("Value in 2026", f"${current_value:,.2f}", f"{roi:,.2f}% ROI")

with col3:
    st.metric("BTC You'd Own", f"₿ {btc_owned:.6f}")

# 5. Visualizations
st.write("---")
st.subheader("Visualizing Your Lost Fortune")

# Filter data for chart starting from investment date
chart_df = df[df["DATE"] >= pd.Timestamp(invest_date)].copy()
chart_df["InvestmentValue"] = (
    (invest_amount / buy_price) * chart_df["CLOSE"] if buy_price > 0 else 0
)

fig = px.line(
    chart_df,
    x="DATE",
    y="InvestmentValue",
    title=f"Growth of ${invest_amount} Investment Over Time",
    labels={"InvestmentValue": "Portfolio Value (USD)", "DATE": "Year"},
)

fig.update_traces(line_color="#f7931a")  # Bitcoin Orange
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# 6. Technical Section (For your Viva/Interviews)
with st.expander("View Raw Data Snippet"):
    st.write(df.tail(10))
    st.info(
        f"Technical Note: This app parses a custom '~' delimited CSV and uses a Closest-Date-Match algorithm to calculate ROI."
    )
