from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲",
                   layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).resolve().parent

def resolve_data_path() -> Path:
    for p in [BASE_DIR / "main_data.csv",
              BASE_DIR.parent / "dashboard" / "main_data.csv",
              Path.cwd() / "dashboard" / "main_data.csv",
              Path.cwd() / "main_data.csv"]:
        if p.exists():
            return p
    raise FileNotFoundError("main_data.csv tidak ditemukan di folder dashboard/.")

@st.cache_data
def load_data(path_str: str) -> pd.DataFrame:
    df = pd.read_csv(path_str)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load_data(str(resolve_data_path()))

# ─── Sidebar ───
st.sidebar.title("🚲 Filter Data")
min_date, max_date = df["dteday"].min().date(), df["dteday"].max().date()

rentang = st.sidebar.date_input("Rentang tanggal", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)
if isinstance(rentang, (tuple, list)) and len(rentang) == 2:
    start_date, end_date = rentang
else:
    start_date = end_date = rentang if not isinstance(rentang, (tuple, list)) else rentang[0]

all_season = sorted(df["season"].dropna().unique().tolist())
sel_season = st.sidebar.multiselect("Musim", all_season, default=all_season)
all_weather = sorted(df["weathersit"].dropna().unique().tolist())
sel_weather = st.sidebar.multiselect("Kondisi cuaca", all_weather, default=all_weather)
sel_day = st.sidebar.radio("Jenis hari", ["Semua", "Hari Kerja", "Hari Libur"], index=0)

st.sidebar.markdown("---")
st.sidebar.caption(f"Periode: **{min_date}** s.d. **{max_date}**")

# ─── Filtering ───
mask = ((df["dteday"].dt.date >= start_date) & (df["dteday"].dt.date <= end_date)
        & df["season"].isin(sel_season) & df["weathersit"].isin(sel_weather))
if sel_day != "Semua":
    mask &= df["day_type"] == sel_day
main_df = df.loc[mask].copy()

# ─── Header ───
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis penyewaan sepeda **2011–2012**: tren musiman, pengaruh cuaca, "
            "dan pola permintaan per jam.")

if main_df.empty:
    st.warning("Tidak ada data untuk filter ini. Ubah filter di sidebar.")
    st.stop()

# ─── Metrics ───
harian = main_df.groupby("dteday", as_index=False).agg(cnt=("cnt","sum"))
total = int(main_df["cnt"].sum())
rata = harian["cnt"].mean()
casual_total = int(main_df["casual"].sum())
reg_total = int(main_df["registered"].sum())
pct_reg = reg_total / total * 100 if total else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penyewaan", f"{total:,}")
c2.metric("Rata-rata Harian", f"{rata:,.0f}")
c3.metric("Registered", f"{reg_total:,}", f"{pct_reg:.1f}%")
c4.metric("Casual", f"{casual_total:,}", f"{100-pct_reg:.1f}%")

st.markdown("---")

# ─── Chart 1: Tren bulanan ───
st.subheader("1️⃣ Tren Penyewaan Bulanan per Tahun")
bulanan = (main_df.groupby(["year","month_num"], as_index=False)["cnt"]
           .sum().sort_values(["year","month_num"]))
label_bulan = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
fig1, ax1 = plt.subplots(figsize=(11, 4.6))
warna = {2011: "#8FA9C9", 2012: "#E07B39"}
for tahun, grp in bulanan.groupby("year"):
    ax1.plot(grp["month_num"], grp["cnt"], marker="o", linewidth=2.5,
             color=warna.get(tahun, "#4C72B0"), label=str(tahun))
if not bulanan.empty:
    idx = bulanan["cnt"].idxmax()
    ax1.scatter(bulanan.loc[idx,"month_num"], bulanan.loc[idx,"cnt"],
                s=160, color="#C0392B", zorder=5, edgecolor="white", linewidth=1.5)
ax1.set_xticks(range(1,13)); ax1.set_xticklabels(label_bulan)
ax1.set_xlabel("Bulan"); ax1.set_ylabel("Total Penyewaan (unit)")
ax1.set_title("Total Penyewaan per Bulan", fontweight="bold")
ax1.set_ylim(bottom=0); ax1.legend(title="Tahun")
sns.despine(ax=ax1); st.pyplot(fig1); plt.close(fig1)
st.markdown("**Insight:** 2012 konsisten di atas 2011; puncak Agustus–September.")

st.markdown("---")

# ─── Chart 2: Pola per jam ───
st.subheader("2️⃣ Pola Penyewaan per Jam: Hari Kerja vs Hari Libur")
pola = main_df.pivot_table(index="hr", columns="day_type",
                           values="cnt", aggfunc="mean").reindex(range(0,24))
fig2, ax2 = plt.subplots(figsize=(11, 4.6))
warna_hari = {"Hari Kerja": "#2E5C8A", "Hari Libur": "#E07B39"}
for jenis in pola.columns:
    ax2.plot(pola.index, pola[jenis], marker="o", linewidth=2.5,
             color=warna_hari.get(jenis, "#4C72B0"), label=jenis)
    seri = pola[jenis].dropna()
    if not seri.empty:
        j = seri.idxmax()
        ax2.scatter(j, seri.max(), s=150, color="#C0392B",
                    zorder=5, edgecolor="white", linewidth=1.5)
        ax2.annotate(f"puncak {int(j):02d}.00", xy=(j, seri.max()),
                     xytext=(j+0.6, seri.max()*1.08),
                     fontsize=9, fontweight="bold", color="#C0392B")
ax2.set_xticks(range(0,24)); ax2.set_xlim(-0.5, 23.5)
ax2.set_xlabel("Jam (0–23)"); ax2.set_ylabel("Rata-rata Penyewaan per Jam (unit/jam)")
ax2.set_title("Rata-rata Penyewaan per Jam per Jenis Hari", fontweight="bold")
ax2.set_ylim(bottom=0); ax2.legend(title="Jenis Hari")
sns.despine(ax=ax2); st.pyplot(fig2); plt.close(fig2)
st.markdown("**Insight:** Hari kerja double-peak (08.00 & 17.00–18.00); "
            "hari libur single-peak (12.00–14.00).")

st.markdown("---")

# ─── Chart 3: Komposisi user ───
st.subheader("3️⃣ Komposisi Registered vs Casual per Jam")
komp = main_df.groupby(["day_type","hr"], as_index=False)[["casual","registered"]].mean()
if not komp.empty:
    jenis_list = komp["day_type"].unique().tolist()
    fig3, axes = plt.subplots(1, len(jenis_list), figsize=(6*len(jenis_list), 4.2),
                              sharey=True, squeeze=False)
    for ax, jenis in zip(axes[0], jenis_list):
        sub = komp[komp["day_type"]==jenis].set_index("hr").reindex(range(0,24))
        ax.bar(sub.index, sub["registered"], color="#2E5C8A", label="Registered", width=0.85)
        ax.bar(sub.index, sub["casual"], bottom=sub["registered"],
               color="#E07B39", label="Casual", width=0.85)
        ax.set_title(jenis, fontweight="bold")
        ax.set_xlabel("Jam (0–23)"); ax.set_ylim(bottom=0)
        ax.legend(loc="upper left", fontsize=8); sns.despine(ax=ax)
    axes[0][0].set_ylabel("Rata-rata Penyewaan per Jam (unit/jam)")
    fig3.suptitle("Siapa yang Menyewa di Setiap Jam?", fontweight="bold")
    plt.tight_layout(); st.pyplot(fig3); plt.close(fig3)

st.markdown("**Insight:** `registered` dominan; porsi `casual` naik di siang hari libur.")

st.markdown("---")
with st.expander("📄 Tabel ringkasan data terfilter"):
    st.write("**Ringkasan per jenis hari**")
    ring = main_df.groupby("day_type", as_index=False).agg(
        total=("cnt","sum"), rata_per_jam=("cnt","mean"),
        casual=("casual","sum"), registered=("registered","sum")).round(2)
    st.dataframe(ring, use_container_width=True)
    st.write("**Cuplikan data**")
    st.dataframe(main_df.head(100), use_container_width=True)

st.caption("© 2024 — Bike Sharing Analysis | Dicoding Proyek Analisis Data")