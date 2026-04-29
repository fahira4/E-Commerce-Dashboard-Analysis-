import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style="darkgrid")

@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()
st.title("E-Commerce Public Data Dashboard 🛒")
st.markdown("Dashboard ini menampilkan performa penjualan, segmentasi pelanggan, dan logistik tahun 2018.")

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

main_df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
             (df['order_purchase_timestamp'].dt.date <= end_date)]

st.subheader("Ringkasan Pendapatan")
col1, col2 = st.columns(2)
col1.metric("Total Order", value=main_df['order_id'].nunique())
col2.metric("Total Revenue", value=f"BRL {main_df['price'].sum():,.2f}")

st.markdown("---")

st.subheader("Top & Bottom Kategori Produk Berdasarkan Pendapatan")
category_revenue = main_df.groupby('product_category_name_english')['price'].sum().reset_index()
category_revenue = category_revenue.sort_values(by='price', ascending=False)
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10)) 
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="price", y="product_category_name_english", data=category_revenue.head(5), palette=colors, ax=ax[0])
ax[0].set_title("Top 5 Kategori", loc="center", fontsize=18)
ax[0].set_xlabel("Total Revenue (BRL)")

sns.barplot(x="price", y="product_category_name_english", data=category_revenue.tail(5), palette=colors, ax=ax[1])
ax[1].set_title("Bottom 5 Kategori", loc="center", fontsize=18)
ax[1].set_xlabel("Total Revenue (BRL)")
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()

st.pyplot(fig)

st.markdown("---")

st.subheader("Distribusi Pelanggan (Recency, Frequency, Monetary)")

recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
rfm_df = main_df.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
    'order_id': 'nunique',
    'price': 'sum'
}).reset_index()
rfm_df.columns = ['customer_unique_id', 'recency', 'frequency', 'monetary']
fig_rfm, ax_rfm = plt.subplots(nrows=1, ncols=3, figsize=(26, 8))

sns.histplot(rfm_df['recency'], bins=50, kde=True, color="#72BCD4", ax=ax_rfm[0])
ax_rfm[0].set_title("Recency (Hari)", fontsize=16)

sns.histplot(rfm_df[rfm_df['frequency'] < 10]['frequency'], bins=10, kde=False, color="#72BCD4", ax=ax_rfm[1])
ax_rfm[1].set_title("Frequency (Jumlah Order)", fontsize=16)

sns.histplot(rfm_df[rfm_df['monetary'] < 2000]['monetary'], bins=50, kde=True, color="#72BCD4", ax=ax_rfm[2])
ax_rfm[2].set_title("Monetary (Total Pengeluaran BRL)", fontsize=16)

st.pyplot(fig_rfm)
with st.expander("Lihat Insight RFM"):
    st.write("Distribusi menunjukkan sebagian besar pelanggan melakukan pembelian sekali (Frequency = 1). Fokus marketing harus diarahkan pada kampanye retensi untuk mengubah pelanggan satu kali menjadi pelanggan setia.")

st.markdown("---")

st.subheader("Korelasi Harga Produk vs Ongkos Kirim")
fig_corr, ax_corr = plt.subplots(figsize=(16, 8))
sample_df = main_df.sample(1000, random_state=42) if len(main_df) > 1000 else main_df
sns.regplot(x='price', y='freight_value', data=sample_df, line_kws={"color": "red"}, scatter_kws={'alpha': 0.5}, ax=ax_corr)
ax_corr.set_title("Scatter Plot: Harga vs Ongkos Kirim (Sample)", fontsize=18)
ax_corr.set_xlabel("Harga Produk (BRL)", fontsize=14)
ax_corr.set_ylabel("Ongkos Kirim (BRL)", fontsize=14)
st.pyplot(fig_corr)

st.caption("Copyright © Dicoding Submission - Nurul Fakhira 2026")