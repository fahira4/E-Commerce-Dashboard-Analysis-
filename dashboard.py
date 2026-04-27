import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style="darkgrid")

# Load cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# Header Dashboard
st.title("E-Commerce Public Data Dashboard 🛒")
st.markdown("Dashboard ini menampilkan performa penjualan dan segmentasi pelanggan.")

# Sidebar untuk filter Waktu
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

with st.sidebar:
    st.header("Filter Waktu 📅")
    start_date, end_date = st.date_input(
        "Pilih Rentang Waktu",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Memfilter data berdasarkan input dari sidebar
main_df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
             (df['order_purchase_timestamp'].dt.date <= end_date)]

# Metrik Utama
st.subheader("Ringkasan Pendapatan")
total_orders = main_df['order_id'].nunique()
total_revenue = main_df['price'].sum()

col1, col2 = st.columns(2)
col1.metric("Total Order", value=total_orders)
col2.metric("Total Revenue", value=f"BRL {total_revenue:,.2f}")

st.markdown("---")

# Visualisasi 1: Top Categories
st.subheader("Top & Bottom Kategori Produk Berdasarkan Pendapatan")

category_revenue = main_df.groupby('product_category_name_english')['price'].sum().reset_index()
category_revenue.rename(columns={'price': 'total_revenue'}, inplace=True)
category_revenue = category_revenue.sort_values(by='total_revenue', ascending=False)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Top 5
sns.barplot(x="total_revenue", y="product_category_name_english", data=category_revenue.head(5), palette=colors, ax=ax[0])
ax[0].set_title("Top 5 Kategori", loc="center", fontsize=15)
ax[0].set_xlabel("Total Revenue")
ax[0].set_ylabel(None)

# Bottom 5
sns.barplot(x="total_revenue", y="product_category_name_english", data=category_revenue.tail(5).sort_values(by='total_revenue', ascending=True), palette=colors, ax=ax[1])
ax[1].set_title("Bottom 5 Kategori", loc="center", fontsize=15)
ax[1].set_xlabel("Total Revenue")
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_ylabel(None)

st.pyplot(fig)

st.markdown("---")

# Visualisasi 2: Analisis RFM Sederhana
st.subheader("Distribusi Recency & Frequency Pelanggan (RFM)")

# Kalkulasi RFM Sederhana
recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
rfm_df = main_df.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
    'order_id': 'count',
}).reset_index()
rfm_df.columns = ['customer_unique_id', 'recency', 'frequency']

fig_rfm, ax_rfm = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))

sns.histplot(rfm_df['recency'], bins=50, kde=True, color="#72BCD4", ax=ax_rfm[0])
ax_rfm[0].set_title("Distribusi Recency (Hari)")

sns.histplot(rfm_df[rfm_df['frequency'] < 10]['frequency'], bins=10, kde=False, color="#72BCD4", ax=ax_rfm[1])
ax_rfm[1].set_title("Distribusi Frequency (Jumlah Transaksi)")

st.pyplot(fig_rfm)

st.caption("Copyright © E-Commerce Analysis 2026")