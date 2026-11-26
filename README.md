# 🛒 Pasar Pintar: Game Literasi Matematika Untung dan Rugi

Draft aplikasi/game pembelajaran untuk materi **Persentase Menghitung Untung dan Rugi**,
dibuat dengan **Python** dan **Tkinter**. Soal disusun berdasarkan kisi-kisi
**Mathematical Literacy**, dengan 4 indikator dan penilaian per tahapan penyelesaian.

## Isi Game: 4 Misi sesuai Kisi-kisi

| Misi | Indikator | Soal | Tahapan | Skor Maks |
|---|---|---|---|---|
| 1 | Mathematical Reasoning | Memilih Penawaran dengan Keuntungan Terbesar (Toko A, B, C) | 5 tahap (Tahap 3 bernilai 2) | 6 |
| 2 | Formulating Situations Mathematically | Menentukan Harga Jual dengan Persentase Keuntungan (blender) | 6 tahap | 6 |
| 3 | Employing Mathematical Concepts, Facts, and Procedures | Menghitung Persentase Untung dan Rugi (sepeda & kipas angin) | 6 tahap | 6 |
| 4 | Interpreting, Applying, and Evaluating Mathematical Outcomes | Mengevaluasi Pernyataan tentang Persentase Kerugian (jaket) | 6 tahap | 6 |

**Total skor maksimum 24.** Nilai = skor ÷ 24 × 100, dengan predikat A/B/C/D.

### Cara bermain
- Soal ditampilkan di panel kiri, sedangkan siswa mengerjakannya **tahap demi tahap** di panel kanan,
  mengikuti urutan "Kisi-kisi Jawaban per Tahapan Penyelesaian".
- Tahap perhitungan dijawab dengan **mengisi angka**. Tahap identifikasi, model matematika,
  perbandingan, dan kesimpulan dijawab dengan **pilihan ganda**. Pengecohnya disusun dari
  miskonsepsi umum, misalnya membagi dengan harga jual atau memilih untung rupiah terbesar.
- Setiap tahap langsung dinilai sesuai skor per tahapan, lalu **pembahasannya** ditampilkan.
- Di akhir permainan muncul rekap capaian per indikator (★), nilai, predikat, dan saran indikator yang perlu dilatih.

### Mode
- **Soal Kisi-kisi**: 4 soal persis seperti dokumen kisi-kisi.
- **Latihan Soal Acak**: 4 soal baru dengan indikator dan tahapan yang sama, tetapi angka, nama,
  dan barangnya acak, sehingga bisa dipakai berlatih berulang kali.

Fitur lainnya: menu **Materi** (rumus, contoh, dan kesalahan yang sering terjadi) serta **Papan Skor**.

## Cara Menjalankan

Butuh **Python 3.10+**. Tkinter sudah termasuk dalam instalasi Python untuk Windows/macOS.

```bash
python main.py
```

Menjalankan unit test (termasuk pengecekan bahwa kunci jawaban sama dengan kisi-kisi):

```bash
python -m unittest discover -s tests -v
```

## Struktur Kode

```
main.py        # Tampilan (GUI Tkinter): menu, misi per tahap, hasil, materi, papan skor
soal.py        # 4 misi sesuai kisi-kisi + generator soal acak + pembahasan per tahap
permainan.py   # Logika permainan: alur misi/tahap, skor per tahap, nilai & predikat
materi.py      # Ringkasan materi persentase untung dan rugi
skor.py        # Simpan/muat papan skor (JSON)
tests/         # Unit test
```

---
Dibuat dengan bantuan VS Code + Claude Code.
