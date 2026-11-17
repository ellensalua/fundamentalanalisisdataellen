# Proyek Analisis Data: Bike Sharing Dataset

Proyek analisis data end-to-end pada **Bike Sharing Dataset** (2011 hingga 2012) untuk menjawab dua pertanyaan bisnis:

1. Bagaimana tren total penyewaan sepeda (`cnt`) per bulan dan per musim pada tahun 2011 dibandingkan dengan tahun 2012, dan kondisi cuaca (`weathersit`) mana yang paling menurunkan rata-rata penyewaan harian selama periode 2011 hingga 2012?
2. Pada jam berapa permintaan penyewaan mencapai puncak pada hari kerja dibandingkan dengan hari libur selama 2011 hingga 2012, dan bagaimana perbandingan kontribusi pengguna `registered` terhadap pengguna `casual` pada jam-jam tersebut?

## Struktur Folder

```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment

Gunakan Python 3.11 atau yang lebih baru. Versi pada `requirements.txt` dikunci dari virtual environment bersih yang sudah diuji (pandas 3.1.1, numpy 2.4.6, pyarrow 26.0.1, streamlit 1.67.0), dan versi pandas serta numpy sama dengan yang tercetak pada notebook.

```bash
python -m venv venv
```

Aktifkan virtual environment:

- Windows (Command Prompt): `venv\Scripts\activate`
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- macOS atau Linux: `source venv/bin/activate`

Pasang seluruh library:

```bash
pip install -r requirements.txt
```

## Menjalankan Dashboard

Dari folder utama proyek:

```bash
streamlit run dashboard/dashboard.py
```

Atau dari folder `dashboard`. Pada macOS, Linux, dan PowerShell versi baru:

```bash
cd dashboard && streamlit run dashboard.py
```

Pada Windows PowerShell versi lama (operator `&&` tidak dikenali), jalankan dua perintah secara terpisah:

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard dapat diakses pada `http://localhost:8501`.

**Fitur dashboard:**
- Filter sidebar: rentang tanggal, musim, kondisi cuaca harian, dan jenis hari.
- Empat kartu metrik: total penyewaan, rata-rata harian, pengguna `registered`, dan pengguna `casual`.
- Empat kelompok visualisasi: tren bulanan per tahun, rata-rata harian per musim dan per kondisi cuaca, pola per jam, serta komposisi pengguna.
- Teks insight yang dihitung ulang dari data yang sedang difilter.
- Tabel ringkasan data terfilter.

**Catatan dasar perhitungan:** kondisi cuaca pada dashboard memakai kondisi cuaca harian (`day.csv`), sama seperti notebook. Pada data per jam, kondisi cuaca dapat berubah dalam satu hari (terjadi pada 577 dari 731 hari), sehingga tidak dipakai sebagai dasar filter. Seluruh filter bekerja pada tingkat hari, sehingga angka rata-rata harian pada dashboard sama dengan notebook.

## Menjalankan Notebook

Notebook memerlukan Jupyter yang dipasang terpisah, misalnya `pip install notebook`, atau dapat dijalankan pada Google Colab.

```bash
jupyter notebook notebook.ipynb
```

Pilih menu Kernel, lalu **Restart and Run All**. Sel terakhir pada bagian Cleaning Data akan menghasilkan ulang `dashboard/main_data.csv`.

## Temuan Utama

| Aspek | Temuan |
|---|---|
| Pertumbuhan 2011 ke 2012 | 64,88% (sekitar 1,65 kali) |
| Musim dengan kontribusi tertinggi | Gugur (32,23%) |
| Puncak bulanan | Juni 2011 (143.512) dan September 2012 (218.573) |
| Bulan terendah | Januari pada kedua tahun, disusul Februari |
| Cuaca yang paling menurunkan penyewaan | Hujan Ringan (turun 63,02% terhadap Cerah); Berkabut turun 17,24% |
| Puncak hari kerja | Pukul 08.00 dan 17.00 hingga 18.00 |
| Puncak hari libur | Pukul 12.00 hingga 14.00 |
| Komposisi pengguna | `registered` 81,17% dan `casual` 18,83% |
| Segmen waktu (rata-rata per jam) | Sore 362,5; Siang 239,0; Pagi 177,1; Malam 106,8 |

## Author

Nama: Ellen Tri Alfiana Salua | ID Dicoding: ellen_tri_alfiana_salua_N0og
