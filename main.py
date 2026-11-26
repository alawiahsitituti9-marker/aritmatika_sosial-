"""Pasar Pintar — Game Edukasi Aritmatika Sosial.

Jalankan dengan:  python main.py
"""

import tkinter as tk
from tkinter import messagebox

from materi import MATERI
from permainan import DESKRIPSI_LEVEL, NAMA_LEVEL, WAKTU_PER_SOAL, Permainan
from skor import muat_skor, tambah_skor
from soal import format_jawaban, parse_jawaban

BG = "#FFF8EC"
KARTU = "#FFFFFF"
TEKS = "#2D2A26"
REDUP = "#7A7268"
UTAMA = "#E07A1F"
HIJAU = "#2E9E5B"
MERAH = "#D64545"
BIRU = "#2F6FB3"
UNGU = "#7A4FB5"

FONT = "Segoe UI"


class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pasar Pintar — Game Aritmatika Sosial")
        self.geometry("860x620")
        self.minsize(760, 560)
        self.configure(bg=BG)

        self.nama = tk.StringVar(value="Pemain")
        self.permainan: Permainan | None = None
        self.layar: tk.Frame | None = None
        self.timer_id = None
        self.sisa_waktu = 0
        self.sudah_dijawab = False

        self.tampil_menu()

    # ------------------------------------------------------------ helper UI --

    def ganti_layar(self) -> tk.Frame:
        self.hentikan_timer()
        self.unbind("<Return>")
        if self.layar is not None:
            self.layar.destroy()
        self.layar = tk.Frame(self, bg=BG)
        self.layar.pack(fill="both", expand=True, padx=28, pady=22)
        return self.layar

    @staticmethod
    def label(parent, text, size=12, bold=False, fg=TEKS, bg=BG, **kw):
        return tk.Label(parent, text=text, fg=fg, bg=bg,
                        font=(FONT, size, "bold" if bold else "normal"), **kw)

    @staticmethod
    def tombol(parent, text, command, warna=UTAMA, size=13, width=None):
        return tk.Button(parent, text=text, command=command, bg=warna, fg="white",
                         activebackground=TEKS, activeforeground="white",
                         relief="flat", bd=0, cursor="hand2", padx=18, pady=8,
                         width=width, font=(FONT, size, "bold"))

    # ----------------------------------------------------------------- menu --

    def tampil_menu(self):
        f = self.ganti_layar()
        self.label(f, "🛒", size=48).pack(pady=(10, 0))
        self.label(f, "Pasar Pintar", size=32, bold=True, fg=UTAMA).pack()
        self.label(f, "Game Edukasi Aritmatika Sosial", size=14, fg=REDUP).pack(pady=(0, 24))

        baris = tk.Frame(f, bg=BG)
        baris.pack(pady=(0, 18))
        self.label(baris, "Nama pemain:", size=12).pack(side="left", padx=(0, 8))
        tk.Entry(baris, textvariable=self.nama, font=(FONT, 12), width=20,
                 relief="solid", bd=1).pack(side="left")

        for teks, cmd, warna in [
            ("▶  Mulai Bermain", self.tampil_pilih_level, UTAMA),
            ("📖  Pelajari Materi", self.tampil_materi, BIRU),
            ("🏆  Papan Skor", self.tampil_papan_skor, UNGU),
            ("✖  Keluar", self.destroy, REDUP),
        ]:
            self.tombol(f, teks, cmd, warna, width=20).pack(pady=6)

    # --------------------------------------------------------- pilih level --

    def tampil_pilih_level(self):
        if not self.nama.get().strip():
            self.nama.set("Pemain")
        f = self.ganti_layar()
        self.label(f, "Pilih Level", size=24, bold=True, fg=UTAMA).pack(pady=(10, 4))
        self.label(f, f"10 soal • 3 nyawa • {WAKTU_PER_SOAL} detik per soal",
                   fg=REDUP).pack(pady=(0, 20))

        for level, warna in [(1, HIJAU), (2, BIRU), (3, MERAH)]:
            kartu = tk.Frame(f, bg=KARTU, highlightbackground="#E8DCC8", highlightthickness=1)
            kartu.pack(fill="x", padx=60, pady=8)
            teks = tk.Frame(kartu, bg=KARTU)
            teks.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            self.label(teks, f"Level {level} — {NAMA_LEVEL[level]}", size=14, bold=True,
                       bg=KARTU, anchor="w").pack(fill="x")
            self.label(teks, DESKRIPSI_LEVEL[level], size=11, fg=REDUP, bg=KARTU,
                       anchor="w").pack(fill="x")
            self.tombol(kartu, "Main", lambda lv=level: self.mulai(lv), warna,
                        size=12).pack(side="right", padx=16)

        self.tombol(f, "← Kembali", self.tampil_menu, REDUP, size=11).pack(pady=20)

    # ---------------------------------------------------------------- game --

    def mulai(self, level: int):
        self.permainan = Permainan(level)
        self.bangun_layar_game()
        self.soal_berikutnya()

    def bangun_layar_game(self):
        f = self.ganti_layar()

        atas = tk.Frame(f, bg=BG)
        atas.pack(fill="x")
        self.lbl_info = self.label(atas, "", size=12, bold=True)
        self.lbl_info.pack(side="left")
        self.lbl_waktu = self.label(atas, "", size=12, bold=True, fg=BIRU)
        self.lbl_waktu.pack(side="right")
        self.lbl_nyawa = self.label(atas, "", size=14, fg=MERAH)
        self.lbl_nyawa.pack(side="right", padx=16)
        self.lbl_skor = self.label(atas, "", size=12, bold=True, fg=UTAMA)
        self.lbl_skor.pack(side="right", padx=16)

        self.progres = tk.Canvas(f, height=8, bg="#EFE4D2", highlightthickness=0)
        self.progres.pack(fill="x", pady=(8, 16))

        kartu = tk.Frame(f, bg=KARTU, highlightbackground="#E8DCC8", highlightthickness=1)
        kartu.pack(fill="both", expand=True)
        isi = tk.Frame(kartu, bg=KARTU)
        isi.pack(fill="both", expand=True, padx=24, pady=18)

        self.lbl_topik = tk.Label(isi, text="", bg=UTAMA, fg="white",
                                  font=(FONT, 10, "bold"), padx=10, pady=2)
        self.lbl_topik.pack(anchor="w")
        self.lbl_soal = self.label(isi, "", size=14, bg=KARTU, justify="left",
                                   anchor="w", wraplength=740)
        self.lbl_soal.pack(fill="x", pady=(12, 16))

        baris = tk.Frame(isi, bg=KARTU)
        baris.pack(fill="x")
        self.label(baris, "Jawaban:", size=12, bg=KARTU).pack(side="left")
        self.entry = tk.Entry(baris, font=(FONT, 14), width=18, relief="solid", bd=1)
        self.entry.pack(side="left", padx=10)
        self.lbl_satuan = self.label(baris, "", size=12, fg=REDUP, bg=KARTU)
        self.lbl_satuan.pack(side="left")
        self.btn_jawab = self.tombol(baris, "Jawab", self.periksa, HIJAU, size=12)
        self.btn_jawab.pack(side="left", padx=14)

        self.lbl_hasil = self.label(isi, "", size=14, bold=True, bg=KARTU, anchor="w")
        self.lbl_hasil.pack(fill="x", pady=(16, 4))
        self.lbl_bahas = self.label(isi, "", size=12, fg=TEKS, bg=KARTU, justify="left",
                                    anchor="w", wraplength=740)
        self.lbl_bahas.pack(fill="x")

        bawah = tk.Frame(f, bg=BG)
        bawah.pack(fill="x", pady=(14, 0))
        self.tombol(bawah, "Menyerah & ke Menu", self.konfirmasi_keluar, REDUP,
                    size=10).pack(side="left")
        self.btn_lanjut = self.tombol(bawah, "Soal Berikutnya →", self.lanjut, UTAMA, size=12)
        self.btn_lanjut.pack(side="right")

        self.bind("<Return>", lambda _e: self.lanjut() if self.sudah_dijawab else self.periksa())

    def perbarui_status(self):
        p = self.permainan
        self.lbl_info.config(text=f"Level {p.level} • Soal {p.nomor}/{p.jumlah_soal}")
        self.lbl_skor.config(text=f"⭐ {p.skor}")
        self.lbl_nyawa.config(text="♥" * p.nyawa + "♡" * (3 - p.nyawa))
        self.progres.update_idletasks()
        lebar = self.progres.winfo_width()
        self.progres.delete("all")
        self.progres.create_rectangle(0, 0, lebar * p.nomor / p.jumlah_soal, 8,
                                      fill=UTAMA, width=0)

    def soal_berikutnya(self):
        soal = self.permainan.soal_berikutnya()
        self.sudah_dijawab = False
        self.lbl_topik.config(text=soal.topik.upper())
        self.lbl_soal.config(text=soal.pertanyaan)
        satuan = {"Rp": "(rupiah)", "%": "(persen)", "kg": "kg", "bulan": "bulan"}
        self.lbl_satuan.config(text=satuan.get(soal.satuan, soal.satuan))
        self.lbl_hasil.config(text="")
        self.lbl_bahas.config(text="")
        self.entry.config(state="normal")
        self.entry.delete(0, "end")
        self.entry.focus_set()
        self.btn_jawab.config(state="normal")
        self.btn_lanjut.config(state="disabled")
        self.perbarui_status()
        self.sisa_waktu = WAKTU_PER_SOAL
        self.detik()

    def detik(self):
        self.lbl_waktu.config(text=f"⏱ {self.sisa_waktu} dtk",
                              fg=MERAH if self.sisa_waktu <= 10 else BIRU)
        if self.sisa_waktu <= 0:
            self.timer_id = None
            self.tampilkan_hasil(None)
            return
        self.sisa_waktu -= 1
        self.timer_id = self.after(1000, self.detik)

    def hentikan_timer(self):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def periksa(self):
        if self.sudah_dijawab:
            return
        teks = self.entry.get()
        if parse_jawaban(teks) is None:
            self.lbl_hasil.config(text="Masukkan jawaban berupa angka, misal 15000 atau 15.000",
                                  fg=REDUP)
            return
        self.tampilkan_hasil(teks)

    def tampilkan_hasil(self, teks):
        self.hentikan_timer()
        self.sudah_dijawab = True
        p = self.permainan
        soal = p.soal
        hasil = p.jawab(teks, self.sisa_waktu)
        kunci = format_jawaban(soal.jawaban, soal.satuan)

        if hasil.benar:
            bonus = f"  (beruntun {p.beruntun}x 🔥)" if p.beruntun >= 2 else ""
            self.lbl_hasil.config(text=f"✔ Benar! +{hasil.poin} poin{bonus}", fg=HIJAU)
        elif teks is None:
            self.lbl_hasil.config(text=f"⏰ Waktu habis! Jawaban: {kunci}", fg=MERAH)
        else:
            self.lbl_hasil.config(text=f"✘ Kurang tepat. Jawaban yang benar: {kunci}", fg=MERAH)

        self.lbl_bahas.config(text="Pembahasan:\n" + soal.pembahasan)
        self.entry.config(state="disabled")
        self.btn_jawab.config(state="disabled")
        self.btn_lanjut.config(state="normal",
                               text="Lihat Hasil →" if p.selesai else "Soal Berikutnya →")
        self.btn_lanjut.focus_set()
        self.perbarui_status()

    def lanjut(self):
        if not self.sudah_dijawab:
            return
        if self.permainan.selesai:
            self.tampil_hasil_akhir()
        else:
            self.soal_berikutnya()

    def konfirmasi_keluar(self):
        if messagebox.askyesno("Keluar", "Akhiri permainan dan kembali ke menu?"):
            self.tampil_menu()

    # ---------------------------------------------------------- hasil akhir --

    def tampil_hasil_akhir(self):
        p = self.permainan
        nama = self.nama.get().strip() or "Pemain"
        peringkat = tambah_skor(nama, p.skor, p.level, p.jumlah_benar)

        f = self.ganti_layar()
        rasio = p.jumlah_benar / p.nomor if p.nomor else 0
        if rasio >= 0.9:
            emoji, pesan = "🏆", "Luar biasa! Kamu siap jadi juragan pasar!"
        elif rasio >= 0.7:
            emoji, pesan = "🎉", "Hebat! Pemahamanmu sudah bagus."
        elif rasio >= 0.5:
            emoji, pesan = "👍", "Lumayan! Terus berlatih, ya."
        else:
            emoji, pesan = "📚", "Yuk, baca materi dulu lalu coba lagi!"

        self.label(f, emoji, size=56).pack(pady=(20, 0))
        judul = "Permainan Selesai!" if p.nyawa > 0 else "Nyawa Habis!"
        self.label(f, judul, size=26, bold=True, fg=UTAMA).pack()
        self.label(f, pesan, size=13, fg=REDUP).pack(pady=(4, 20))
        self.label(f, f"Skor: {p.skor}", size=30, bold=True).pack()
        self.label(f, f"Benar {p.jumlah_benar} dari {p.nomor} soal • "
                      f"Level {p.level} ({NAMA_LEVEL[p.level]})", size=12).pack(pady=4)
        if peringkat:
            self.label(f, f"Kamu masuk papan skor di peringkat #{peringkat}!",
                       size=12, bold=True, fg=UNGU).pack(pady=4)

        tombol = tk.Frame(f, bg=BG)
        tombol.pack(pady=24)
        self.tombol(tombol, "Main Lagi", lambda: self.mulai(p.level), HIJAU).pack(side="left", padx=6)
        self.tombol(tombol, "Pilih Level", self.tampil_pilih_level, BIRU).pack(side="left", padx=6)
        self.tombol(tombol, "Menu", self.tampil_menu, REDUP).pack(side="left", padx=6)

    # --------------------------------------------------------------- materi --

    def tampil_materi(self):
        f = self.ganti_layar()
        self.label(f, "📖 Materi Aritmatika Sosial", size=22, bold=True, fg=BIRU).pack(anchor="w")

        badan = tk.Frame(f, bg=BG)
        badan.pack(fill="both", expand=True, pady=12)
        daftar = tk.Frame(badan, bg=BG)
        daftar.pack(side="left", fill="y", padx=(0, 14))

        teks = tk.Text(badan, wrap="word", font=("Consolas", 12), bg=KARTU, fg=TEKS,
                       relief="flat", padx=18, pady=14, highlightthickness=1,
                       highlightbackground="#E8DCC8")
        teks.pack(side="left", fill="both", expand=True)

        def tampilkan(i):
            judul, isi = MATERI[i]
            teks.config(state="normal")
            teks.delete("1.0", "end")
            teks.insert("end", judul + "\n\n", "judul")
            teks.insert("end", isi)
            teks.tag_config("judul", font=(FONT, 16, "bold"), foreground=BIRU)
            teks.config(state="disabled")

        for i, (judul, _) in enumerate(MATERI):
            tk.Button(daftar, text=judul, command=lambda i=i: tampilkan(i), anchor="w",
                      bg=KARTU, fg=TEKS, relief="flat", cursor="hand2", width=22,
                      font=(FONT, 11), padx=10, pady=6).pack(fill="x", pady=2)
        tampilkan(0)

        self.tombol(f, "← Kembali", self.tampil_menu, REDUP, size=11).pack(anchor="w")

    # ----------------------------------------------------------- papan skor --

    def tampil_papan_skor(self):
        f = self.ganti_layar()
        self.label(f, "🏆 Papan Skor", size=22, bold=True, fg=UNGU).pack(pady=(10, 16))

        tabel = tk.Frame(f, bg=KARTU, highlightbackground="#E8DCC8", highlightthickness=1)
        tabel.pack(fill="x", padx=60)
        kolom = ["#", "Nama", "Skor", "Level", "Benar", "Tanggal"]
        for c, k in enumerate(kolom):
            self.label(tabel, k, size=11, bold=True, fg=REDUP, bg=KARTU).grid(
                row=0, column=c, padx=12, pady=8, sticky="w")
            tabel.grid_columnconfigure(c, weight=1)

        data = muat_skor()
        if not data:
            self.label(tabel, "Belum ada skor. Ayo main!", bg=KARTU, fg=REDUP).grid(
                row=1, column=0, columnspan=len(kolom), pady=16)
        for r, e in enumerate(data, start=1):
            nilai = [r, e.get("nama", "-"), e.get("skor", 0), e.get("level", "-"),
                     e.get("benar", "-"), e.get("tanggal", "-")]
            for c, v in enumerate(nilai):
                self.label(tabel, str(v), size=11, bg=KARTU, bold=(c == 2)).grid(
                    row=r, column=c, padx=12, pady=4, sticky="w")

        self.tombol(f, "← Kembali", self.tampil_menu, REDUP, size=11).pack(pady=20)


if __name__ == "__main__":
    Aplikasi().mainloop()
