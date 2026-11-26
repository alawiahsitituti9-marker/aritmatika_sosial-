"""Model pembelajaran Rigorous Mathematical Thinking (RMT).

Berdasarkan Kinard & Kozulin, "Rigorous Mathematical Thinking: Conceptual
Formation in the Mathematics Classroom". RMT memadukan:
  • Vygotsky  — alat psikologis (tabel, rumus, simbol, bahasa matematika),
                Learning Activity (analisis tugas, perencanaan, refleksi), ZPD.
  • Feuerstein — Mediated Learning Experience (intensionalitas & resiprositas,
                transendensi, makna), fungsi kognitif fase Input–Elaborasi–Output,
                dan asesmen dinamis (uji – mediasi – uji ulang).

Modul ini berisi data RMT untuk setiap misi dan setiap tahap, serta fungsi
diagnostik untuk profil fungsi kognitif siswa.
"""

FASE = {
    "input": "Input — Mengumpulkan Informasi",
    "elaborasi": "Elaborasi — Mengolah Informasi",
    "output": "Output — Mengekspresikan Hasil",
}

REKOMENDASI_FASE = {
    "input": "Latih membaca soal dengan teliti: garis bawahi data penting dan susun "
             "dalam TABEL (harga beli, harga jual) sebelum mulai menghitung.",
    "elaborasi": "Latih menghubungkan data dengan RUMUS: tulis rumusnya dulu, lalu "
                 "substitusi nilai. Ingat, persentase selalu dibandingkan dengan harga beli.",
    "output": "Latih menuliskan KESIMPULAN lengkap dengan alasan, dan periksa apakah "
              "jawabanmu masuk akal. Hindari menebak (coba-coba).",
}

# Langkah Learning Activity yang sama untuk semua misi (Bab 3).
LANGKAH_LA = [
    ("Analisis Tugas", "Kenali apa yang diketahui dan apa yang ditanyakan."),
    ("Perencanaan Tindakan", "Ikuti tahapan penyelesaian secara sistematis."),
    ("Refleksi", "Evaluasi strategi dan proses berpikirmu sendiri."),
]

REFLEKSI_FASE = [
    ("input", "Input — memahami & mengumpulkan informasi dari soal"),
    ("elaborasi", "Elaborasi — memilih rumus & menghitung"),
    ("output", "Output — menyimpulkan & menuliskan jawaban"),
    ("tidak", "Tidak ada, semuanya lancar"),
]

REFLEKSI_STRATEGI = [
    "Menyusun data dalam tabel",
    "Menuliskan rumus sebelum menghitung",
    "Memeriksa kembali kewajaran jawaban",
    "Menggunakan pertanyaan mediasi/petunjuk",
]

# ----------------------------------------------------------- data per misi --
# Kunci = nomor misi (1–4, sesuai indikator kisi-kisi).

MISI = {
    1: {
        "tujuan": "Kamu akan belajar membandingkan beberapa penawaran dengan ukuran yang "
                  "adil, yaitu PERSENTASE keuntungan.",
        "makna": "Pedagang yang cerdas tidak hanya melihat besar untung dalam rupiah, tetapi "
                 "seberapa besar untung itu dibandingkan modalnya. Dengan begitu ia bisa "
                 "memilih usaha yang paling menguntungkan.",
        "sehari_hari": "Sehari-hari kita bilang \"untungnya banyak\" jika rupiahnya besar. "
                       "Dalam matematika, untung dinilai RELATIF terhadap modal (persentase).",
        "analisis": ["Diketahui: harga beli dan harga jual setiap toko.",
                     "Ditanya: toko dengan persentase keuntungan terbesar.",
                     "Rencana: susun tabel → hitung untung → hitung persentase → "
                     "bandingkan → simpulkan."],
        "transendensi": "Prinsip umum: untuk membandingkan hal-hal yang ukurannya berbeda, "
                        "gunakan perbandingan RELATIF (persentase/rasio). Prinsip ini juga "
                        "dipakai untuk membandingkan nilai ujian dengan jumlah soal berbeda, "
                        "kenaikan harga, atau pertumbuhan tabungan.",
    },
    2: {
        "tujuan": "Kamu akan belajar menerjemahkan situasi nyata menjadi MODEL MATEMATIKA "
                  "untuk menentukan harga jual.",
        "makna": "Menetapkan harga jual yang tepat membuat penjual memperoleh untung sesuai "
                 "rencana, tanpa menebak-nebak harga.",
        "sehari_hari": "Sehari-hari orang sering \"menaikkan harga sedikit\". Dalam matematika, "
                       "kenaikan itu dihitung tepat: p% dari harga beli.",
        "analisis": ["Diketahui: harga beli dan persentase keuntungan yang diinginkan.",
                     "Ditanya: harga jual.",
                     "Rencana: hitung untung → tulis model → substitusi → hitung → simpulkan."],
        "transendensi": "Pola \"nilai akhir = nilai awal + perubahan\" berlaku di banyak situasi: "
                        "harga setelah kenaikan, gaji setelah bonus, atau tabungan setelah "
                        "mendapat bunga.",
    },
    3: {
        "tujuan": "Kamu akan menggunakan KONSEP dan PROSEDUR untung, rugi, dan persentase "
                  "secara tepat pada dua barang yang berbeda.",
        "makna": "Dengan prosedur yang benar, kamu bisa mengetahui transaksi mana yang "
                 "menguntungkan dan mana yang merugikan, serta seberapa besar dampaknya.",
        "sehari_hari": "Sehari-hari \"rugi\" berarti uang berkurang. Dalam matematika, rugi "
                       "dan untung diukur dengan prosedur yang sama terhadap harga beli.",
        "analisis": ["Diketahui: harga beli dan harga jual dua barang.",
                     "Ditanya: besar untung/rugi dan persentasenya untuk tiap barang.",
                     "Rencana: identifikasi → hitung untung & persen → hitung rugi & persen "
                     "→ simpulkan."],
        "transendensi": "Prosedur \"selisih ÷ nilai awal × 100%\" berlaku untuk SEMUA persentase "
                        "kenaikan atau penurunan: berat badan, jumlah penduduk, nilai ulangan.",
    },
    4: {
        "tujuan": "Kamu akan MENILAI kebenaran sebuah pernyataan dengan bukti perhitungan.",
        "makna": "Tidak semua klaim angka itu benar. Pemikir yang teliti memeriksa klaim "
                 "dengan bukti sebelum mempercayainya.",
        "sehari_hari": "Sehari-hari kita sering langsung percaya angka persen. Dalam matematika, "
                       "kita selalu bertanya: \"persen DARI APA?\"",
        "analisis": ["Diketahui: harga beli, harga jual, dan klaim teman.",
                     "Ditanya: apakah klaim teman benar?",
                     "Rencana: hitung rugi → pilih rumus yang benar → hitung → bandingkan "
                     "dengan klaim → simpulkan."],
        "transendensi": "Saat menilai klaim persentase apa pun, periksa PEMBANDINGNYA "
                        "(penyebut). Pembanding yang berbeda menghasilkan makna yang berbeda.",
    },
}

# ---------------------------------------------------------- data per tahap --
# fase, operasi mental, alat psikologis, fungsi kognitif, dan mediasi
# (pertanyaan terpimpin bertingkat, tidak membocorkan jawaban).

def _t(fase, operasi, alat, fungsi, *mediasi):
    return {"fase": fase, "operasi": operasi, "alat": alat, "fungsi": fungsi,
            "mediasi": list(mediasi)}


_IDENTIFIKASI = _t(
    "input", "Identifikasi", "Tabel", "Persepsi yang jelas & pengumpulan data yang akurat",
    "Baca lagi soalnya. Kata kerja mana yang menunjukkan HARGA BELI (membeli) dan mana "
    "yang menunjukkan HARGA JUAL (menjual/terjual)?",
    "Buat tabel kecil: kolom 'harga beli' dan 'harga jual'. Isi dari kalimat soal satu per "
    "satu, lalu cocokkan dengan pilihan.")

TAHAP = {
    1: [
        _IDENTIFIKASI,
        _t("elaborasi", "Menghitung selisih", "Rumus",
           "Hubungan bagian–keseluruhan (harga jual = harga beli + untung)",
           "Harga jual terdiri dari dua bagian: modal (harga beli) dan untung. Bagian mana "
           "yang sedang kamu cari?",
           "Gunakan rumus Untung = Harga jual − Harga beli untuk setiap toko."),
        _t("elaborasi", "Menghubungkan (rasio)", "Rumus & simbol %",
           "Pembandingan relatif terhadap harga beli",
           "Persentase keuntungan membandingkan untung dengan apa: harga beli atau harga jual?",
           "Hitung (untung ÷ harga beli) × 100%. Sederhanakan pecahannya dulu, misalnya "
           "30.000/120.000 = 1/4."),
        _t("elaborasi", "Membandingkan & mengurutkan", "Garis bilangan",
           "Pembandingan yang sistematis",
           "Letakkan ketiga persentase pada garis bilangan. Mana yang paling kanan (terbesar)?",
           "Jika dua nilai sama besar, tuliskan dengan tanda '=', bukan '>'."),
        _t("output", "Menarik kesimpulan logis", "Bahasa matematika",
           "Komunikasi yang jelas dengan bukti logis (bukan coba-coba)",
           "Kesimpulanmu harus didukung hasil perbandingan di Tahap 4. Ukuran apa yang "
           "dibandingkan: rupiah atau persentase?",
           "Hati-hati: untung rupiah terbesar belum tentu persentasenya terbesar, karena "
           "modalnya berbeda."),
    ],
    2: [
        _t("input", "Identifikasi", "Bahasa matematika", "Memilih informasi yang relevan",
           "Garis bawahi angka pada soal. Mana yang merupakan harga beli dan mana persentase?",
           "Kalimat tanya \"Berapakah …?\" menunjukkan apa yang DITANYAKAN."),
        _t("elaborasi", "Mengubah persen ke rupiah", "Simbol %",
           "Memahami makna simbol persen",
           "p% artinya p dari setiap 100. Jadi p% dari harga beli = p/100 × harga beli.",
           "Trik: hitung 10% dulu (bagi 10), lalu kalikan sesuai kebutuhan."),
        _t("elaborasi", "Memodelkan (abstraksi)", "Skema bagian–keseluruhan",
           "Hubungan bagian–keseluruhan",
           "Bayangkan harga jual sebagai satu batang utuh yang terdiri dari dua bagian. "
           "Bagian apa saja?",
           "Jika penjual ingin UNTUNG, harga jual harus lebih besar atau lebih kecil dari "
           "harga beli?"),
        _t("elaborasi", "Menerapkan rumus", "Rumus & persamaan",
           "Kesepadanan ruas kiri dan kanan (satuan harus sama)",
           "Bilangan yang dijumlahkan harus bersatuan sama: rupiah dengan rupiah.",
           "Ganti kata \"keuntungan\" dengan nilai RUPIAH dari Tahap 2, bukan angka persennya."),
        _t("elaborasi", "Menghitung", "Rumus", "Ketepatan dan akurasi perhitungan",
           "Jumlahkan harga beli dengan besar keuntungan dari Tahap 2.",
           "Periksa: hasilnya harus lebih besar dari harga beli."),
        _t("output", "Menyimpulkan dalam konteks", "Bahasa matematika",
           "Menyatakan jawaban dengan jelas sesuai konteks",
           "Apakah jawabanmu masuk akal? Untuk untung, harga jual harus lebih besar dari "
           "harga beli.",
           "Kesimpulan yang lengkap memuat nama barang, harga jual, dan tujuannya."),
    ],
    3: [
        _IDENTIFIKASI,
        _t("elaborasi", "Menghitung selisih", "Rumus", "Hubungan bagian–keseluruhan",
           "Pada barang pertama, mana yang lebih besar: harga jual atau harga beli?",
           "Untung = Harga jual − Harga beli."),
        _t("elaborasi", "Menghubungkan (rasio)", "Rumus & simbol %",
           "Pembandingan relatif terhadap harga beli",
           "Untung dibandingkan dengan harga BELI, bukan harga jual.",
           "Hitung (untung ÷ harga beli) × 100%."),
        _t("elaborasi", "Menghitung selisih", "Rumus", "Hubungan sebab–akibat (mengapa rugi)",
           "Pada barang kedua, harga jual lebih kecil dari harga beli. Apa artinya?",
           "Rugi = Harga beli − Harga jual (yang besar dikurangi yang kecil)."),
        _t("elaborasi", "Menghubungkan (rasio)", "Rumus & simbol %",
           "Pembandingan relatif terhadap harga beli",
           "Rugi juga dibandingkan dengan harga BELI.",
           "Hitung (rugi ÷ harga beli) × 100%."),
        _t("output", "Menyimpulkan", "Bahasa matematika",
           "Komunikasi yang tepat (untung vs rugi tidak tertukar)",
           "Barang mana yang untung dan mana yang rugi? Jangan sampai tertukar.",
           "Periksa apakah persentase dalam kesimpulan dihitung dari harga beli."),
    ],
    4: [
        _IDENTIFIKASI,
        _t("elaborasi", "Menghitung selisih", "Rumus", "Hubungan bagian–keseluruhan",
           "Harga jual lebih kecil dari harga beli, berarti rugi. Berapa selisihnya?",
           "Rugi = Harga beli − Harga jual."),
        _t("elaborasi", "Memilih prinsip yang tepat", "Rumus & persamaan",
           "Penalaran hipotetis (bagaimana jika pembandingnya berbeda?)",
           "Persentase untung dan rugi selalu dibandingkan dengan apa?",
           "Coba pikirkan: jika pembandingnya harga jual, apakah hasilnya adil bagi semua "
           "transaksi?"),
        _t("elaborasi", "Menerapkan rumus", "Rumus & persamaan", "Ketepatan substitusi",
           "Masukkan besar rugi sebagai pembilang dan pembanding yang benar sebagai penyebut.",
           "Penyebutnya harus harga BELI."),
        _t("elaborasi", "Menghitung", "Simbol %", "Ketepatan dan akurasi perhitungan",
           "Bagi rugi dengan harga beli, lalu kalikan 100%.",
           "Sederhanakan dulu pecahannya, misalnya 60.000/400.000 = 6/40."),
        _t("output", "Mengevaluasi klaim", "Bahasa matematika",
           "Menilai kewajaran hasil dengan bukti logis",
           "Bandingkan hasil hitunganmu dengan klaim teman. Sama atau berbeda?",
           "Kesalahan teman ada pada pembandingnya. Pembanding apa yang ia pakai?"),
    ],
}


def info_misi(nomor: int) -> dict:
    return MISI[nomor]


def info_tahap(nomor_misi: int, i_tahap: int) -> dict:
    return TAHAP[nomor_misi][i_tahap]


def profil_fase(permainan) -> dict:
    """Skor per fase kognitif dari percobaan PERTAMA (sebelum mediasi)."""
    hasil = {f: [0, 0] for f in FASE}
    for i, m in enumerate(permainan.misi):
        for j, t in enumerate(m.tahapan):
            f = info_tahap(m.nomor, j)["fase"]
            hasil[f][0] += permainan.skor_tahap[i][j] or 0
            hasil[f][1] += t.skor
    return {f: tuple(v) for f, v in hasil.items()}


def fase_terlemah(profil: dict):
    """Fase dengan persentase capaian terendah; None jika semua sempurna."""
    rasio = {f: (d / m if m else 1) for f, (d, m) in profil.items()}
    f = min(rasio, key=rasio.get)
    return None if rasio[f] >= 1 else f
