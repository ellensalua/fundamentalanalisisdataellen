from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Dashboard Penyewaan Sepeda", layout="wide",
                   initial_sidebar_state="expanded")

sns.set_theme(style="whitegrid")

# ---------------------------------------------------------------- Konstanta
BASE_DIR = Path(__file__).resolve().parent
URUTAN_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
URUTAN_MUSIM = ["Semi", "Panas", "Gugur", "Dingin"]
URUTAN_CUACA = ["Cerah", "Berkabut", "Hujan Ringan", "Hujan Lebat"]
WARNA_TAHUN = {2011: "#A6B1BD", 2012: "#2A9D8F"}
WARNA_HARI = {"Hari Kerja": "#2E5C8A", "Hari Libur": "#E07B39"}
WARNA_REGISTERED, WARNA_CASUAL = "#6A4C93", "#C9B6E4"
WARNA_PUNCAK = "#C0392B"


# ---------------------------------------------------------------- Fungsi bantu
def fmt(angka, desimal=0):
    """Format angka dengan pemisah ribuan titik dan desimal koma (gaya Indonesia)."""
    teks = f"{angka:,.{desimal}f}"
    return teks.replace(",", "X").replace(".", ",").replace("X", ".")


def resolve_data_path() -> Path:
    for p in [BASE_DIR / "main_data.csv",
              BASE_DIR.parent / "dashboard" / "main_data.csv",
              Path.cwd() / "dashboard" / "main_data.csv",
              Path.cwd() / "main_data.csv"]:
        if p.exists():
            return p
    raise FileNotFoundError("main_data.csv tidak ditemukan pada folder dashboard.")


@st.cache_data
def load_data(path_str: str) -> pd.DataFrame:
    data = pd.read_csv(path_str)
    data["dteday"] = pd.to_datetime(data["dteday"])
    return data


df = load_data(str(resolve_data_path()))

# ---------------------------------------------------------------- Sidebar
st.sidebar.title("Filter Data")
min_date, max_date = df["dteday"].min().date(), df["dteday"].max().date()

rentang = st.sidebar.date_input("Rentang tanggal", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)
if isinstance(rentang, (tuple, list)):
    start_date = rentang[0]
    end_date = rentang[1] if len(rentang) == 2 else rentang[0]
else:
    start_date = end_date = rentang

semua_musim = [m for m in URUTAN_MUSIM if m in df["season"].unique()]
pilih_musim = st.sidebar.multiselect("Musim", semua_musim, default=semua_musim)

semua_cuaca = [c for c in URUTAN_CUACA if c in df["cuaca_harian"].unique()]
pilih_cuaca = st.sidebar.multiselect(
    "Kondisi cuaca harian", semua_cuaca, default=semua_cuaca,
    help="Kondisi cuaca mengikuti data harian (day.csv), sama seperti analisis pada notebook.")

pilih_hari = st.sidebar.radio("Jenis hari", ["Semua", "Hari Kerja", "Hari Libur"], index=0)

st.sidebar.markdown("---")
st.sidebar.caption(f"Periode data: **{min_date}** sampai **{max_date}**")
st.sidebar.caption("Seluruh filter bekerja pada tingkat hari, sehingga setiap hari yang terpilih "
                   "disertakan secara utuh (24 jam).")

# ---------------------------------------------------------------- Penyaringan data
mask = ((df["dteday"].dt.date >= start_date) & (df["dteday"].dt.date <= end_date)
        & df["season"].isin(pilih_musim) & df["cuaca_harian"].isin(pilih_cuaca))
if pilih_hari != "Semua":
    mask &= df["day_type"] == pilih_hari
main_df = df.loc[mask].copy()

# ---------------------------------------------------------------- Header
st.title("Dashboard Analisis Penyewaan Sepeda (Bike Sharing)")
st.markdown(
    "Dashboard ini menyajikan analisis penyewaan sepeda pada tahun **2011 hingga 2012** untuk "
    "menjawab dua pertanyaan bisnis: **(1)** bagaimana tren penyewaan per bulan dan per musim "
    "pada tahun 2011 dibandingkan dengan 2012 serta kondisi cuaca yang paling menurunkan "
    "penyewaan harian, dan **(2)** pada jam berapa permintaan mencapai puncak pada hari kerja "
    "dibandingkan dengan hari libur serta bagaimana komposisi pengguna *registered* dan *casual*."
)

if main_df.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Ubah filter pada sidebar.")
    st.stop()

# ---------------------------------------------------------------- Agregasi harian
# Setiap hari terpilih utuh, sehingga agregasi harian dari data per jam
# identik dengan data harian (day.csv) pada notebook.
harian = (main_df.groupby(["dteday", "year", "month_num", "season", "cuaca_harian", "day_type"],
                          as_index=False, observed=True)
          .agg(cnt=("cnt", "sum"), casual=("casual", "sum"), registered=("registered", "sum")))

# ---------------------------------------------------------------- Metrik
total = int(main_df["cnt"].sum())
rata_harian = harian["cnt"].mean()
total_casual = int(main_df["casual"].sum())
total_registered = int(main_df["registered"].sum())
porsi_registered = total_registered / total * 100 if total else 0
porsi_casual = 100 - porsi_registered

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Penyewaan", fmt(total))
k2.metric("Rata-rata Harian", fmt(rata_harian))
k3.metric("Registered", fmt(total_registered))
k3.caption(f"Porsi terhadap total: {fmt(porsi_registered, 1)}%")
k4.metric("Casual", fmt(total_casual))
k4.caption(f"Porsi terhadap total: {fmt(porsi_casual, 1)}%")

st.caption(f"Jumlah hari terpilih: {fmt(len(harian))} hari.")
st.markdown("---")

# ---------------------------------------------------------------- Grafik 1: tren bulanan
st.subheader("1. Tren Penyewaan Bulanan pada Tahun 2011 dan 2012")
bulanan = (main_df.groupby(["year", "month_num"], as_index=False)["cnt"].sum()
           .sort_values(["year", "month_num"]))

fig1, ax1 = plt.subplots(figsize=(11, 4.8))
for tahun, grp in bulanan.groupby("year"):
    ax1.plot(grp["month_num"], grp["cnt"], marker="o", linewidth=2.5,
             color=WARNA_TAHUN.get(tahun, "#4C72B0"), label=str(tahun))
    idx = grp["cnt"].idxmax()
    ax1.scatter(grp.loc[idx, "month_num"], grp.loc[idx, "cnt"], s=150, color=WARNA_PUNCAK,
                zorder=5, edgecolor="white", linewidth=1.5)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(URUTAN_BULAN)
ax1.set_xlabel("Bulan")
ax1.set_ylabel("Total Penyewaan (unit)")
ax1.set_title("Total Penyewaan per Bulan (titik merah menandai puncak setiap tahun)",
              fontweight="bold")
ax1.set_ylim(bottom=0)
ax1.legend(title="Tahun")
sns.despine(ax=ax1)
st.pyplot(fig1)
plt.close(fig1)

teks = []
for tahun, grp in bulanan.groupby("year"):
    puncak = grp.loc[grp["cnt"].idxmax()]
    terendah = grp.loc[grp["cnt"].idxmin()]
    teks.append(f"{tahun}: puncak pada **{URUTAN_BULAN[int(puncak['month_num']) - 1]}** "
                f"({fmt(puncak['cnt'])}), terendah pada **{URUTAN_BULAN[int(terendah['month_num']) - 1]}** "
                f"({fmt(terendah['cnt'])})")
total_tahun = main_df.groupby("year")["cnt"].sum()
if {2011, 2012}.issubset(total_tahun.index):
    rasio = total_tahun[2012] / total_tahun[2011]
    teks.append(f"total 2012 adalah {fmt(rasio, 2)} kali total 2011 "
                f"(pertumbuhan {fmt((rasio - 1) * 100, 2)}%)")
st.markdown("**Insight** (dihitung dari data terfilter): " + "; ".join(teks) + ".")
st.caption("Total bulanan mengikuti filter yang aktif. Bulan yang hanya terisi sebagian "
           "akibat filter tanggal akan tampak lebih rendah.")
st.markdown("---")

# ---------------------------------------------------------------- Grafik 2 dan 3: musim dan cuaca
st.subheader("2. Rata-rata Penyewaan Harian menurut Musim dan Kondisi Cuaca")
col_a, col_b = st.columns(2)

with col_a:
    musim_tahun = (harian.pivot_table(index="season", columns="year", values="cnt",
                                      aggfunc="mean", observed=True)
                   .reindex([m for m in URUTAN_MUSIM if m in harian["season"].unique()]))
    fig2, ax2 = plt.subplots(figsize=(6.2, 4.6))
    tahun_ada = list(musim_tahun.columns)
    lebar = 0.8 / max(len(tahun_ada), 1)
    for i, tahun in enumerate(tahun_ada):
        geser = (i - (len(tahun_ada) - 1) / 2) * lebar
        batang = ax2.bar([p + geser for p in range(len(musim_tahun))], musim_tahun[tahun],
                         lebar, color=WARNA_TAHUN.get(tahun, "#4C72B0"), label=str(tahun))
        for b in batang:
            if pd.notna(b.get_height()):
                ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 60,
                         fmt(b.get_height()), ha="center", va="bottom", fontsize=8,
                         fontweight="bold")
    ax2.set_xticks(range(len(musim_tahun)))
    ax2.set_xticklabels(musim_tahun.index)
    ax2.set_xlabel("Musim")
    ax2.set_ylabel("Rata-rata Penyewaan Harian (unit/hari)")
    ax2.set_title("Rata-rata Harian per Musim", fontweight="bold")
    ax2.set_ylim(0, float(musim_tahun.max().max()) * 1.18)
    ax2.legend(title="Tahun", loc="upper left")
    ax2.grid(axis="x", visible=False)
    sns.despine(ax=ax2)
    st.pyplot(fig2)
    plt.close(fig2)

with col_b:
    cuaca = (harian.groupby("cuaca_harian", observed=True)
             .agg(rata_harian=("cnt", "mean"), hari=("cnt", "count"))
             .reindex([c for c in URUTAN_CUACA if c in harian["cuaca_harian"].unique()]))
    ada_cerah = "Cerah" in cuaca.index
    fig3, ax3 = plt.subplots(figsize=(6.2, 4.6))
    warna = ["#4C72B0" if k == "Cerah" else "#B8C6D9" for k in cuaca.index]
    batang = ax3.bar(cuaca.index, cuaca["rata_harian"], color=warna, edgecolor="white")
    for b, (kondisi, baris) in zip(batang, cuaca.iterrows()):
        label = f"{fmt(baris['rata_harian'])}\n(n={int(baris['hari'])} hari)"
        if ada_cerah and kondisi != "Cerah":
            selisih = (baris["rata_harian"] / cuaca.loc["Cerah", "rata_harian"] - 1) * 100
            label += f"\n{fmt(selisih, 1)}% terhadap Cerah"
        ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + cuaca["rata_harian"].max() * 0.015,
                 label, ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax3.set_xlabel("Kondisi Cuaca Harian")
    ax3.set_ylabel("Rata-rata Penyewaan Harian (unit/hari)")
    ax3.set_title("Rata-rata Harian per Kondisi Cuaca", fontweight="bold")
    ax3.set_ylim(0, cuaca["rata_harian"].max() * 1.4)
    ax3.grid(axis="x", visible=False)
    sns.despine(ax=ax3)
    st.pyplot(fig3)
    plt.close(fig3)

teks = []
if len(musim_tahun) > 0:
    rata_musim = harian.groupby("season", observed=True)["cnt"].mean()
    teks.append(f"musim dengan rata-rata harian tertinggi adalah **{rata_musim.idxmax()}** "
                f"({fmt(rata_musim.max())} per hari) dan terendah **{rata_musim.idxmin()}** "
                f"({fmt(rata_musim.min())} per hari)")
if {2011, 2012}.issubset(musim_tahun.columns):
    kenaikan = (musim_tahun[2012] / musim_tahun[2011] - 1) * 100
    teks.append(f"kenaikan 2012 terhadap 2011 terbesar terjadi pada musim **{kenaikan.idxmax()}** "
                f"({fmt(kenaikan.max())}%)")
if ada_cerah and len(cuaca) > 1:
    lain = cuaca.drop(index="Cerah")
    terendah = lain["rata_harian"].idxmin()
    selisih = (lain.loc[terendah, "rata_harian"] / cuaca.loc["Cerah", "rata_harian"] - 1) * 100
    teks.append(f"kondisi cuaca yang paling menurunkan rata-rata harian adalah **{terendah}** "
                f"({fmt(selisih, 2)}% terhadap Cerah, n={int(lain.loc[terendah, 'hari'])} hari)")
elif not ada_cerah:
    teks.append("kondisi Cerah tidak termasuk filter, sehingga selisih terhadap Cerah tidak dapat dihitung")
st.markdown("**Insight** (dihitung dari data terfilter): " + "; ".join(teks) + ".")
st.caption("Kondisi cuaca memakai data harian (day.csv) seperti pada notebook. Pada data per jam, "
           "cuaca dapat berubah dalam satu hari, sehingga tidak digunakan sebagai dasar filter.")
st.markdown("---")

# ---------------------------------------------------------------- Grafik 4: pola per jam
st.subheader("3. Pola Penyewaan per Jam pada Hari Kerja dan Hari Libur")
pola = (main_df.pivot_table(index="hr", columns="day_type", values="cnt", aggfunc="mean")
        .reindex(range(0, 24)))

fig4, ax4 = plt.subplots(figsize=(11, 4.8))
for jenis in pola.columns:
    ax4.plot(pola.index, pola[jenis], marker="o", linewidth=2.5,
             color=WARNA_HARI.get(jenis, "#4C72B0"), label=jenis)
    seri = pola[jenis].dropna()
    if not seri.empty:
        j = int(seri.idxmax())
        ax4.scatter(j, seri.max(), s=150, color=WARNA_PUNCAK, zorder=5,
                    edgecolor="white", linewidth=1.5)
        ax4.annotate(f"puncak {j:02d}.00", xy=(j, seri.max()),
                     xytext=(j + 0.6, seri.max() * 1.08), fontsize=9,
                     fontweight="bold", color=WARNA_PUNCAK)
ax4.set_xticks(range(0, 24))
ax4.set_xlim(-0.5, 23.5)
ax4.set_xlabel("Jam (0 hingga 23)")
ax4.set_ylabel("Rata-rata Penyewaan per Jam (unit/jam)")
ax4.set_title("Rata-rata Penyewaan per Jam menurut Jenis Hari", fontweight="bold")
ax4.set_ylim(0, float(pola.max().max()) * 1.2)
ax4.legend(title="Jenis Hari")
sns.despine(ax=ax4)
st.pyplot(fig4)
plt.close(fig4)

teks = []
for jenis in pola.columns:
    seri = pola[jenis].dropna()
    teks.append(f"**{jenis}**: jam tertinggi pukul **{int(seri.idxmax()):02d}.00** "
                f"({fmt(seri.max(), 1)} per jam)")
if "Hari Kerja" in pola.columns:
    kerja = pola["Hari Kerja"].dropna()
    if len(kerja) >= 24:
        pagi = kerja.loc[6:10].idxmax()
        sore = kerja.loc[15:20].idxmax()
        teks.append(f"puncak hari kerja pada pagi hari pukul {int(pagi):02d}.00 dan pada sore hari "
                    f"pukul {int(sore):02d}.00")
st.markdown("**Insight** (dihitung dari data terfilter): " + "; ".join(teks) + ".")
st.markdown("---")

# ---------------------------------------------------------------- Grafik 5: komposisi pengguna
st.subheader("4. Komposisi Pengguna Registered dan Casual per Jam")
komp = main_df.groupby(["day_type", "hr"], as_index=False)[["casual", "registered"]].mean()
jenis_list = [j for j in ["Hari Kerja", "Hari Libur"] if j in komp["day_type"].unique()]

fig5, axes = plt.subplots(1, len(jenis_list), figsize=(6.5 * len(jenis_list), 4.4),
                          sharey=True, squeeze=False)
for ax, jenis in zip(axes[0], jenis_list):
    sub = komp[komp["day_type"] == jenis].set_index("hr").reindex(range(0, 24))
    ax.bar(sub.index, sub["registered"], color=WARNA_REGISTERED, label="Registered", width=0.85)
    ax.bar(sub.index, sub["casual"], bottom=sub["registered"], color=WARNA_CASUAL,
           label="Casual", width=0.85)
    ax.set_title(jenis, fontweight="bold")
    ax.set_xlabel("Jam (0 hingga 23)")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="x", visible=False)
    sns.despine(ax=ax)
axes[0][0].set_ylabel("Rata-rata Penyewaan per Jam (unit/jam)")
fig5.suptitle("Komposisi Pengguna di Setiap Jam", fontweight="bold")
plt.tight_layout()
st.pyplot(fig5)
plt.close(fig5)

teks = [f"pengguna *registered* berkontribusi **{fmt(porsi_registered, 1)}%** dan *casual* "
        f"**{fmt(porsi_casual, 1)}%** dari total penyewaan terfilter"]
for jenis in jenis_list:
    sub = komp[komp["day_type"] == jenis].set_index("hr")
    jam_casual = int(sub["casual"].idxmax())
    teks.append(f"pada **{jenis}**, rata-rata pengguna *casual* tertinggi terjadi pukul "
                f"**{jam_casual:02d}.00** ({fmt(sub['casual'].max(), 1)} per jam, dibandingkan dengan "
                f"*registered* {fmt(sub.loc[jam_casual, 'registered'], 1)} per jam)")
st.markdown("**Insight** (dihitung dari data terfilter): " + "; ".join(teks) + ".")
st.markdown("---")

# ---------------------------------------------------------------- Tabel
with st.expander("Tabel ringkasan data terfilter"):
    st.write("**Ringkasan per jenis hari**")
    ringkasan = (main_df.groupby("day_type", as_index=False)
                 .agg(total=("cnt", "sum"), rata_per_jam=("cnt", "mean"),
                      casual=("casual", "sum"), registered=("registered", "sum"))
                 .round(2))
    st.dataframe(ringkasan, width="stretch")
    st.write("**Cuplikan data (100 baris pertama)**")
    st.dataframe(main_df.head(100), width="stretch")

st.caption("Proyek Analisis Data: Bike Sharing Dataset | Ellen Tri Alfiana Salua")
