import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set page config
st.set_page_config(page_title="Finwise Dashboard", page_icon="💰", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data_v8.csv")
    df['date'] = pd.to_datetime(df['date'])
    # Standardisasi teks kolom kategorikal
    for col in ['type', 'category', 'subcategory', 'payment_method']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df

try:
    all_df = load_data()
except FileNotFoundError:
    # Fallback dummy data jika file tidak ditemukan saat inisialisasi awal
    st.error("File 'cleaned_data_v8.csv' tidak ditemukan. Harap pastikan file berada di direktori yang sama.")
    st.stop()

# Sidebar untuk Filter
min_date = all_df["date"].min()
max_date = all_df["date"].max()

with st.sidebar:
    st.title("Navigasi Finewise")
    st.markdown("Gunakan filter di bawah ini untuk mengatur rentang waktu data yang ingin ditampilkan.")
    
    # Date Input
    date_range = st.date_input(
        label='Rentang Waktu Analisis',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Pastikan input rentang waktu valid sebelum memproses data
if isinstance(date_range, list) or isinstance(date_range, tuple):
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = date_range[0]
        end_date = max_date
else:
    start_date = date_range
    end_date = max_date

# Filter DataFrame berdasarkan pilihan user
main_df = all_df[(all_df["date"] >= pd.to_datetime(start_date)) & 
                (all_df["date"] <= pd.to_datetime(end_date))].copy()

# Pisahkan data Income (Pemasukan) dan Expense (Pengeluaran)
expense_df = main_df[main_df['type'].str.lower() == 'expense'].copy()
income_df = main_df[main_df['type'].str.lower() == 'income'].copy()

# --- HEADER SECTION ---
st.title('📊 Finwise Personal Finance Dashboard')
st.markdown(f"Menampilkan analisis data dari periode **{start_date}** sampai **{end_date}**.")
st.markdown("---")

# --- KPI METRICS SECTION ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_income = income_df['amount'].sum()
    st.metric("Total Pemasukan", value=f"Rp {total_income:,.0f}")
with col2:
    total_expense = expense_df['amount'].sum()
    st.metric("Total Pengeluaran", value=f"Rp {total_expense:,.0f}")
with col3:
    net_balance = total_income - total_expense
    color_delta = "normal" if net_balance >= 0 else "inverse"
    st.metric("Saldo Bersih (Net)", value=f"Rp {net_balance:,.0f}")
with col4:
    avg_expense = expense_df['amount'].mean() if len(expense_df) > 0 else 0
    st.metric("Rata-rata per Pengeluaran", value=f"Rp {avg_expense:,.0f}")

st.markdown("---")

# --- MAIN DASHBOARD TABS ---
tab1, tab2, tab3 = st.tabs(["📈 Tren & Pola Waktu", "🗂️ Analisis Kategori & Subkategori", "💳 Pola Metode Pembayaran"])

# TAB 1: TREN WAKTU
with tab1:
    st.subheader("Tren Finansial Bulanan")
    if not main_df.empty:
        main_df['month_year'] = main_df['date'].dt.to_period('M')
        trend_df = main_df.groupby(['month_year', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
        trend_df['month_year'] = trend_df['month_year'].astype(str)
        
        fig, ax = plt.subplots(figsize=(14, 5))
        if 'income' in trend_df.columns:
            ax.plot(trend_df['month_year'], trend_df['income'], marker='o', color='#2ECC71', label='Pemasukan (Income)', linewidth=2.5)
        if 'expense' in trend_df.columns:
            ax.plot(trend_df['month_year'], trend_df['expense'], marker='o', color='#E74C3C', label='Pengeluaran (Expense)', linewidth=2.5)
        
        ax.set_title("Perbandingan Tren Bulanan Pemasukan vs Pengeluaran", fontsize=14, fontweight='bold', pad=15)
        
        ax.set_xlabel("Bulan", fontsize=12, labelpad=15) 
        ax.set_ylabel("Total Jumlah (Rupiah)", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        ax.legend(fontsize=11)
        
        plt.tight_layout() 
        
        st.pyplot(fig)
    else:
        st.info("Tidak ada data pada rentang waktu terpilih.")

# TAB 2: ANALISIS KATEGORI
with tab2:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Proporsi Pengeluaran per Kategori")
        if not expense_df.empty:
            cat_expense = expense_df.groupby('category')['amount'].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(8, 8))
            # Menampilkan pie/donut chart untuk porsi pengeluaran
            wedges, texts, autotexts = ax.pie(
                cat_expense['amount'], 
                labels=cat_expense['category'], 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=sns.color_palette('pastel'),
                textprops=dict(color="black")
            )
            plt.setp(autotexts, size=11, weight="bold")
            plt.setp(texts, size=11)
            ax.set_title("Persentase Pengeluaran Berdasarkan Kategori", fontsize=13, fontweight='bold')
            st.pyplot(fig)
        else:
            st.info("Tidak ada data pengeluaran pada rentang waktu ini.")
            
    with col_right:
        st.subheader("Top 5 Subkategori Pengeluaran Terbesar")
        if not expense_df.empty:
            subcat_expense = expense_df.groupby('subcategory')['amount'].sum().reset_index()
            subcat_expense = subcat_expense.sort_values(by='amount', ascending=False).head(5)
            
            fig, ax = plt.subplots(figsize=(9, 6.5))
            sns.barplot(data=subcat_expense, x='amount', y='subcategory', palette='Reds_r', ax=ax)
            ax.set_title("5 Subkategori dengan Pengeluaran Tertinggi", fontsize=13, fontweight='bold', pad=10)
            ax.set_xlabel("Total Pengeluaran (Rp)", fontsize=11)
            ax.set_ylabel("Subkategori", fontsize=11)
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            st.pyplot(fig)
        else:
            st.info("Tidak ada data pengeluaran pada rentang waktu ini.")

# TAB 3: METODE PEMBAYARAN
with tab3:
    st.subheader("Analisis Perilaku Metode Pembayaran (Khusus Pengeluaran)")
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("**Rata-rata Nominal Transaksi per Metode Pembayaran**")
        if not expense_df.empty:
            pay_mean = expense_df.groupby('payment_method')['amount'].mean().reset_index().sort_values(by='amount', ascending=False)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(data=pay_mean, x='payment_method', y='amount', palette='Blues_r', ax=ax)
            ax.set_ylabel("Rata-rata Nominal (Rp)", fontsize=11)
            ax.set_xlabel("Metode Pembayaran", fontsize=11)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)
        else:
            st.info("Tidak ada data pengeluaran.")
            
    with col_p2:
        st.markdown("**Total Frekuensi Pemakaian Metode Pembayaran**")
        if not expense_df.empty:
            pay_count = expense_df['payment_method'].value_counts().reset_index()
            pay_count.columns = ['payment_method', 'count']
            
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(data=pay_count, x='payment_method', y='count', palette='GnBu_r', ax=ax)
            ax.set_ylabel("Jumlah Transaksi (Frekuensi)", fontsize=11)
            ax.set_xlabel("Metode Pembayaran", fontsize=11)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)
        else:
            st.info("Tidak ada data pengeluaran.")

# --- FOOTER ---
st.markdown("---")
st.caption('Copyright © Finwise 2026. All rights reserved.')