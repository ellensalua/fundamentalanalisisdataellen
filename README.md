# 🚲 Bike Sharing Data Analysis

Proyek analisis data end-to-end pada **Bike Sharing Dataset** (2011–2012) untuk menjawab:
1. Tren penyewaan bulanan/musiman 2011 vs 2012 & pengaruh cuaca.
2. Pola per jam hari kerja vs hari libur & komposisi registered vs casual.

## 📁 Struktur Folder
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

## ⚙️ Setup
```bash
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Menjalankan Dashboard
Dari root:
```bash
streamlit run dashboard/dashboard.py
```
Atau dari folder dashboard:
```bash
cd dashboard && streamlit run dashboard.py
```

Akses di `http://localhost:8501`.

**Fitur dashboard:**
- Filter sidebar: tanggal, musim, cuaca, jenis hari
- Metric cards: total, rata-rata harian, registered, casual
- 3 visualisasi: tren bulanan, pola per jam, komposisi user
- Tabel ringkasan data terfilter

## 📓 Menjalankan Notebook
```bash
jupyter notebook notebook.ipynb
```
Kernel → **Restart & Run All**.

## 🔍 Temuan Utama
| Aspek | Temuan |
|---|---|
| Pertumbuhan 2011→2012 | ±65% |
| Musim tertinggi | Gugur |
| Puncak bulanan | Agustus–September |
| Cuaca | Cerah tertinggi; hujan/kabut menekan |
| Puncak hari kerja | 08.00 & 17.00–18.00 |
| Puncak hari libur | 12.00–14.00 |
| Komposisi | registered ≈ 81% |

## 👤 Author
Nama: Ellen Salua — Dicoding ID: DS323B6X0507