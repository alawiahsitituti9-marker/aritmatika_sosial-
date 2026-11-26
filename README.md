# 🛒 Pasar Pintar — Game Edukasi Aritmatika Sosial

Draft aplikasi/game pembelajaran **Aritmatika Sosial** (Matematika SMP kelas VII)
yang dibuat dengan **Python** dan **Tkinter**. Pemain berperan sebagai pedagang di pasar
dan harus menjawab soal-soal hitungan jual-beli sehari-hari.

## Fitur

- **3 level kesulitan**
  | Level | Nama | Materi |
  |---|---|---|
  | 1 | Pedagang Pemula | Untung & rugi, diskon, bruto–tara–neto |
  | 2 | Pedagang Terampil | Persentase untung/rugi, harga jual, PPN 11%, persentase tara |
  | 3 | Juragan Pasar | Harga beli, diskon bertingkat, bunga tunggal, lama menabung |
- **Soal acak tak terbatas** — angka dibuat otomatis, jawaban selalu bilangan bulat.
- **Pembahasan langkah demi langkah** setelah setiap soal (benar maupun salah).
- **Mekanik game**: 10 soal per sesi, 3 nyawa ♥, timer 60 detik, bonus waktu & bonus jawaban beruntun 🔥.
- **Menu materi** berisi ringkasan rumus dan contoh untuk tiap topik.
- **Papan skor** (10 skor tertinggi) yang tersimpan di `skor_tertinggi.json`.
- Input jawaban fleksibel: `15000`, `15.000`, `Rp 15.000`, `25%`, `40 kg` semuanya diterima.

## Cara Menjalankan

Butuh **Python 3.10+** (Tkinter sudah termasuk di instalasi Python Windows/macOS).

```bash
python main.py
```

Menjalankan unit test:

```bash
python -m unittest discover -s tests -v
```

## Struktur Kode

```
main.py        # Tampilan (GUI Tkinter): menu, level, game, materi, papan skor
permainan.py   # Logika permainan: skor, nyawa, nomor soal, penilaian jawaban
soal.py        # Generator soal acak + pembahasan untuk setiap topik
materi.py      # Ringkasan materi & rumus Aritmatika Sosial
skor.py        # Simpan/muat papan skor (JSON)
tests/         # Unit test
```

Logika (`soal.py`, `permainan.py`) dipisahkan dari tampilan (`main.py`) sehingga
mudah diuji dan dikembangkan, misalnya untuk menambah topik soal baru cukup membuat
fungsi `soal_...()` di `soal.py` lalu mendaftarkannya di `GENERATOR_PER_LEVEL`.

## Ide Pengembangan Selanjutnya

- Mode cerita (pemain membuka "toko" dan modal bertambah dari jawaban benar)
- Soal pilihan ganda untuk siswa yang lebih muda
- Suara & animasi
- Topik tambahan: bunga majemuk, komisi, cicilan

---
Dibuat dengan bantuan VS Code + Claude Code.
