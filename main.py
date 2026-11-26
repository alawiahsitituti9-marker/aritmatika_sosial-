"""Pasar Pintar — Game Literasi Matematika: Persentase Untung dan Rugi.

Jalankan dengan:  python main.py
"""

import tkinter as tk
from tkinter import messagebox

from materi import MATERI
from permainan import MODE, Permainan, bintang, predikat
from skor import muat_skor, tambah_skor
from soal import parse_angka

BG = "#FFF8EC"
KARTU = "#FFFFFF"
LEMBUT = "#FFF1DC"
GARIS = "#E8DCC8"
TEKS = "#2D2A26"
REDUP = "#7A7268"
UTAMA = "#E07A1F"
HIJAU = "#2E9E5B"
MERAH = "#D64545"
BIRU = "#2F6FB3"
UNGU = "#7A4FB5"
WARNA_INDIKATOR = [BIRU, UNGU, HIJAU, MERAH]

FONT = "Segoe UI"


class AreaGulir(tk.Frame):
    """Frame yang bisa di-scroll secara vertikal."""

    def __init__(self, parent, bg=KARTU, **kw):
        super().__init__(parent, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        bar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.isi = tk.Frame(self.canvas, bg=bg)
        self.isi.bind("<Configure>",
                      lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self._win = self.canvas.create_window((0, 0), window=self.isi, anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        self.bind_all("<MouseWheel>", self._roda, add="+")

    def _roda(self, e):
        try:
            if self.winfo_exists() and str(e.widget).startswith(str(self)):
                self.canvas.yview_scroll(int(-e.delta / 120), "units")
        except tk.TclError:
            pass

    def ke_atas(self):
        self.canvas.yview_moveto(0)


class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pasar Pintar — Literasi Matematika Untung & Rugi")
        # Sesuaikan ukuran dengan skala layar (mis. Windows 125%/150%)
        self.skala = max(1.0, self.winfo_fpixels("1i") / 96)
        lebar_layar, tinggi_layar = self.winfo_screenwidth(), self.winfo_screenheight()
        w = min(self.px(1080), lebar_layar - 40)
        h = min(self.px(720), tinggi_layar - 80)
        self.geometry(f"{w}x{h}")
        self.minsize(min(self.px(900), w), min(self.px(600), h))
        if w < self.px(1080) or h < self.px(720):
            try:
                self.state("zoomed")  # layar kecil: maksimalkan jendela
            except tk.TclError:
                pass
        self.configure(bg=BG)

        self.nama = tk.StringVar(value="Pemain")
        self.permainan: Permainan | None = None
        self.layar: tk.Frame | None = None
        self.sudah_dijawab = False

        self.tampil_menu()

    # ------------------------------------------------------------ helper UI --

    def px(self, n: int) -> int:
        """Ubah ukuran piksel desain (skala 100%) ke piksel layar sebenarnya."""
        return int(n * getattr(self, "skala", 1.0))

    def ganti_layar(self) -> tk.Frame:
        self.unbind("<Return>")
        if self.layar is not None:
            self.layar.destroy()
        self.layar = tk.Frame(self, bg=BG)
        self.layar.pack(fill="both", expand=True, padx=24, pady=18)
        return self.layar

    @staticmethod
    def label(parent, text, size=12, bold=False, fg=TEKS, bg=BG, **kw):
        return tk.Label(parent, text=text, fg=fg, bg=bg,
                        font=(FONT, size, "bold" if bold else "normal"), **kw)

    @staticmethod
    def tombol(parent, text, command, warna=UTAMA, size=13, width=None):
        return tk.Button(parent, text=text, command=command, bg=warna, fg="white",
                         activebackground=TEKS, activeforeground="white",
                         disabledforeground="#EEEEEE",
                         relief="flat", bd=0, cursor="hand2", padx=18, pady=8,
                         width=width, font=(FONT, size, "bold"))

    # ----------------------------------------------------------------- menu --

    def tampil_menu(self):
        f = self.ganti_layar()
        self.label(f, "🛒", size=46).pack(pady=(6, 0))
        self.label(f, "Pasar Pintar", size=32, bold=True, fg=UTAMA).pack()
        self.label(f, "Game Literasi Matematika — Persentase Untung dan Rugi",
                   size=14, fg=REDUP).pack(pady=(0, 20))

        baris = tk.Frame(f, bg=BG)
        baris.pack(pady=(0, 16))
        self.label(baris, "Nama pemain:", size=12).pack(side="left", padx=(0, 8))
        tk.Entry(baris, textvariable=self.nama, font=(FONT, 12), width=22,
                 relief="solid", bd=1).pack(side="left")

        for teks, cmd, warna in [
            ("📝  Soal Kisi-kisi (4 Misi)", lambda: self.mulai("kisi"), UTAMA),
            ("🎲  Latihan Soal Acak", lambda: self.mulai("acak"), HIJAU),
            ("📖  Pelajari Materi", self.tampil_materi, BIRU),
            ("🏆  Papan Skor", self.tampil_papan_skor, UNGU),
            ("✖  Keluar", self.destroy, REDUP),
        ]:
            self.tombol(f, teks, cmd, warna, width=24).pack(pady=5)

        self.label(f, "4 misi sesuai indikator Mathematical Literacy • dikerjakan per tahap • "
                      "skor maksimum 6 per misi", size=10, fg=REDUP).pack(pady=(16, 0))

    # ---------------------------------------------------------------- game --

    def mulai(self, mode: str):
        if not self.nama.get().strip():
            self.nama.set("Pemain")
        self.permainan = Permainan(mode)
        self.bangun_layar_misi()

    def bangun_layar_misi(self):
        p = self.permainan
        m = p.misi_sekarang
        warna = WARNA_INDIKATOR[(m.nomor - 1) % len(WARNA_INDIKATOR)]
        f = self.ganti_layar()

        # bar atas
        atas = tk.Frame(f, bg=BG)
        atas.pack(fill="x")
        self.label(atas, f"Misi {p.i_misi + 1} dari {len(p.misi)}  •  {MODE[p.mode]}",
                   size=12, bold=True).pack(side="left")
        self.tombol(atas, "Menu", self.konfirmasi_keluar, REDUP, size=10).pack(side="right")
        self.lbl_skor = self.label(atas, "", size=12, bold=True, fg=UTAMA)
        self.lbl_skor.pack(side="right", padx=16)

        badan = tk.Frame(f, bg=BG)
        badan.pack(fill="both", expand=True, pady=(12, 0))

        # panel kiri: indikator, soal, daftar tahapan
        kiri = tk.Frame(badan, bg=KARTU, highlightbackground=GARIS, highlightthickness=1,
                        width=self.px(400))
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        dalam = tk.Frame(kiri, bg=KARTU)
        dalam.pack(fill="both", expand=True, padx=16, pady=14)
        tk.Label(dalam, text=f"INDIKATOR {m.nomor}: {m.indikator.upper()}", bg=warna,
                 fg="white", font=(FONT, 9, "bold"), padx=8, pady=3, wraplength=self.px(350),
                 justify="left").pack(anchor="w")
        self.label(dalam, m.deskripsi_indikator, size=9, fg=REDUP, bg=KARTU,
                   wraplength=self.px(360), justify="left").pack(anchor="w", pady=(4, 10))
        self.label(dalam, m.judul, size=14, bold=True, bg=KARTU, wraplength=self.px(360),
                   justify="left").pack(anchor="w")
        self.label(dalam, m.soal, size=11, bg=KARTU, wraplength=self.px(360),
                   justify="left").pack(anchor="w", pady=(6, 12))

        self.label(dalam, "Tahapan Penyelesaian", size=10, bold=True, fg=REDUP,
                   bg=KARTU).pack(anchor="w")
        self.lbl_tahapan = []
        for t in m.tahapan:
            lbl = self.label(dalam, "", size=10, bg=KARTU, anchor="w", justify="left",
                             wraplength=self.px(360))
            lbl.pack(fill="x")
            self.lbl_tahapan.append(lbl)

        # panel kanan: pengerjaan tahap
        self.gulir = AreaGulir(badan)
        self.gulir.pack(side="left", fill="both", expand=True, padx=(14, 0))
        self.gulir.configure(highlightbackground=GARIS, highlightthickness=1)

        bawah = tk.Frame(f, bg=BG)
        bawah.pack(fill="x", pady=(12, 0))
        self.btn_periksa = self.tombol(bawah, "Periksa Jawaban", self.periksa, HIJAU, size=12)
        self.btn_periksa.pack(side="left")
        self.btn_lanjut = self.tombol(bawah, "Lanjut →", self.lanjut, UTAMA, size=12)
        self.btn_lanjut.pack(side="right")

        self.bind("<Return>", lambda _e: self.lanjut() if self.sudah_dijawab else self.periksa())
        self.tampil_tahap()

    def perbarui_status(self):
        p = self.permainan
        self.lbl_skor.config(text=f"⭐ Skor: {p.skor} / {p.skor_maks}")
        m = p.misi_sekarang
        for i, (t, lbl) in enumerate(zip(m.tahapan, self.lbl_tahapan)):
            s = p.skor_tahap[p.i_misi][i]
            judul = t.judul.split(":", 1)[0]
            if s is None:
                tanda, warna = ("▶" if i == p.i_tahap else "○"), (UTAMA if i == p.i_tahap else REDUP)
                teks = f"{tanda} {judul} — skor {t.skor}"
            else:
                tanda, warna = ("✔", HIJAU) if s == t.skor else ("✘", MERAH)
                teks = f"{tanda} {judul} — {s}/{t.skor}"
            lbl.config(text=teks, fg=warna,
                       font=(FONT, 10, "bold" if i == p.i_tahap else "normal"))

    def tampil_tahap(self):
        p = self.permainan
        t = p.tahap_sekarang
        self.sudah_dijawab = False
        isi = self.gulir.isi
        for w in isi.winfo_children():
            w.destroy()
        self.gulir.ke_atas()

        wadah = tk.Frame(isi, bg=KARTU)
        wadah.pack(fill="both", expand=True, padx=22, pady=18)
        self.label(wadah, t.judul, size=15, bold=True, fg=UTAMA, bg=KARTU, wraplength=self.px(560),
                   justify="left").pack(anchor="w")
        self.label(wadah, f"Skor tahap ini: {t.skor}", size=10, fg=REDUP,
                   bg=KARTU).pack(anchor="w")
        self.label(wadah, t.perintah, size=12, bg=KARTU, wraplength=self.px(560),
                   justify="left").pack(anchor="w", pady=(10, 12))

        self.entri, self.lbl_butir, self.radio = [], [], []
        if t.jenis == "isian":
            for i, s in enumerate(t.isian):
                baris = tk.Frame(wadah, bg=KARTU)
                baris.pack(fill="x", pady=4)
                self.label(baris, s.label, size=11, bg=KARTU, width=28,
                           anchor="w").pack(side="left")
                if s.satuan == "Rp":
                    self.label(baris, "Rp", size=11, fg=REDUP, bg=KARTU).pack(side="left")
                e = tk.Entry(baris, font=(FONT, 13), width=14, relief="solid", bd=1)
                e.pack(side="left", padx=6)
                if s.satuan == "%":
                    self.label(baris, "%", size=11, fg=REDUP, bg=KARTU).pack(side="left")
                hasil = self.label(baris, "", size=11, bold=True, bg=KARTU)
                hasil.pack(side="left", padx=8)
                self.entri.append(e)
                self.lbl_butir.append(hasil)
            self.entri[0].focus_set()
            self.label(wadah, "Tulis angka saja, misal 30000 atau 30.000; desimal pakai koma "
                              "(17,65).", size=9, fg=REDUP, bg=KARTU).pack(anchor="w", pady=(4, 0))
        else:
            self.pilih = tk.IntVar(value=-1)
            for i, teks in enumerate(t.pilihan):
                rb = tk.Radiobutton(wadah, text=f"{'ABCD'[i]}.  {teks}", variable=self.pilih,
                                    value=i, bg=LEMBUT, fg=TEKS, activebackground=LEMBUT,
                                    selectcolor=KARTU, anchor="w", justify="left",
                                    wraplength=self.px(540), font=(FONT, 11), padx=10, pady=6,
                                    relief="flat", cursor="hand2")
                rb.pack(fill="x", pady=3)
                self.radio.append(rb)
            self.focus_set()

        self.lbl_hasil = self.label(wadah, "", size=13, bold=True, bg=KARTU, anchor="w")
        self.lbl_hasil.pack(fill="x", pady=(14, 4))
        self.lbl_bahas = tk.Label(wadah, text="", bg=KARTU, fg=TEKS, font=(FONT, 11),
                                  justify="left", anchor="w", wraplength=self.px(560))
        self.lbl_bahas.pack(fill="x")

        self.btn_periksa.config(state="normal")
        self.btn_lanjut.config(state="disabled", text="Lanjut →")
        self.perbarui_status()

    def periksa(self):
        if self.sudah_dijawab:
            return
        p = self.permainan
        t = p.tahap_sekarang
        if t.jenis == "isian":
            jawaban = [e.get() for e in self.entri]
            if any(parse_angka(j) is None for j in jawaban):
                self.lbl_hasil.config(text="Isi semua kotak dengan angka terlebih dahulu.",
                                      fg=REDUP)
                return
        else:
            jawaban = self.pilih.get()
            if jawaban < 0:
                self.lbl_hasil.config(text="Pilih salah satu jawaban terlebih dahulu.", fg=REDUP)
                return

        hasil = p.jawab(jawaban)
        self.sudah_dijawab = True

        if t.jenis == "isian":
            for e, lbl, ok, s in zip(self.entri, self.lbl_butir, hasil.per_butir, t.isian):
                e.config(state="disabled")
                lbl.config(text="✔" if ok else f"✘  {s.kunci()}", fg=HIJAU if ok else MERAH)
        else:
            for i, rb in enumerate(self.radio):
                rb.config(state="disabled")
                if i == t.kunci_pilihan:
                    rb.config(bg="#DFF3E6", disabledforeground=HIJAU)
                elif i == jawaban:
                    rb.config(bg="#FBE3E3", disabledforeground=MERAH)
                else:
                    rb.config(disabledforeground=REDUP)

        if hasil.benar:
            self.lbl_hasil.config(text=f"✔ Tepat! +{hasil.skor} skor", fg=HIJAU)
        else:
            self.lbl_hasil.config(text=f"✘ Belum tepat (0/{t.skor}). Pelajari pembahasannya:",
                                  fg=MERAH)
        self.lbl_bahas.config(text="Pembahasan:\n" + t.penjelasan)

        self.btn_periksa.config(state="disabled")
        if p.tahap_terakhir:
            teks = "Lihat Hasil Akhir →" if p.misi_terakhir else "Misi Berikutnya →"
        else:
            teks = "Tahap Berikutnya →"
        self.btn_lanjut.config(state="normal", text=teks)
        self.btn_lanjut.focus_set()
        self.perbarui_status()

    def lanjut(self):
        if not self.sudah_dijawab:
            return
        p = self.permainan
        akhir_misi = p.tahap_terakhir
        p.maju()
        if p.selesai:
            self.tampil_hasil_akhir()
        elif akhir_misi:
            self.bangun_layar_misi()
        else:
            self.tampil_tahap()

    def konfirmasi_keluar(self):
        if messagebox.askyesno("Keluar", "Akhiri permainan dan kembali ke menu?"):
            self.tampil_menu()

    # ---------------------------------------------------------- hasil akhir --

    def tampil_hasil_akhir(self):
        p = self.permainan
        nama = self.nama.get().strip() or "Pemain"
        peringkat = tambah_skor(nama, p.nilai, p.skor, MODE[p.mode])

        f = self.ganti_layar()
        self.label(f, "🏆" if p.nilai >= 75 else "📚", size=44).pack(pady=(4, 0))
        self.label(f, "Semua Misi Selesai!", size=24, bold=True, fg=UTAMA).pack()
        self.label(f, f"Nilai {nama}: {p.nilai}", size=28, bold=True).pack(pady=(6, 0))
        self.label(f, f"Skor {p.skor} dari {p.skor_maks}  •  Predikat {predikat(p.nilai)}",
                   size=13, fg=REDUP).pack(pady=(0, 14))

        tabel = tk.Frame(f, bg=KARTU, highlightbackground=GARIS, highlightthickness=1)
        tabel.pack(fill="x", padx=80)
        for c, k in enumerate(["No", "Indikator", "Soal", "Skor", "Capaian"]):
            self.label(tabel, k, size=10, bold=True, fg=REDUP, bg=KARTU).grid(
                row=0, column=c, padx=10, pady=6, sticky="w")
        tabel.grid_columnconfigure(1, weight=1)
        for r, m in enumerate(p.misi, start=1):
            s = p.skor_misi(r - 1)
            b = bintang(s, m.skor_maks)
            nilai = [m.nomor, m.indikator, m.judul, f"{s} / {m.skor_maks}",
                     "★" * b + "☆" * (3 - b)]
            for c, v in enumerate(nilai):
                self.label(tabel, str(v), size=10, bg=KARTU, wraplength=self.px(330) if c in (1, 2) else 0,
                           justify="left", fg=UTAMA if c == 4 else TEKS).grid(
                    row=r, column=c, padx=10, pady=4, sticky="w")

        lemah = [m.indikator for i, m in enumerate(p.misi) if p.skor_misi(i) < m.skor_maks]
        saran = ("Sempurna! Semua indikator literasi matematika tercapai."
                 if not lemah else
                 "Perlu latihan lagi pada: " + "; ".join(lemah) + ".")
        self.label(f, saran, size=11, fg=TEKS, wraplength=self.px(820)).pack(pady=(12, 2))
        if peringkat:
            self.label(f, f"Kamu masuk papan skor di peringkat #{peringkat}!",
                       size=11, bold=True, fg=UNGU).pack()

        tombol = tk.Frame(f, bg=BG)
        tombol.pack(pady=14)
        self.tombol(tombol, "Ulangi", lambda: self.mulai(p.mode), HIJAU).pack(side="left", padx=6)
        self.tombol(tombol, "Latihan Acak", lambda: self.mulai("acak"), BIRU).pack(side="left", padx=6)
        self.tombol(tombol, "Menu", self.tampil_menu, REDUP).pack(side="left", padx=6)

    # --------------------------------------------------------------- materi --

    def tampil_materi(self):
        f = self.ganti_layar()
        self.label(f, "📖 Materi: Persentase Untung dan Rugi", size=22, bold=True,
                   fg=BIRU).pack(anchor="w")

        badan = tk.Frame(f, bg=BG)
        badan.pack(fill="both", expand=True, pady=12)
        daftar = tk.Frame(badan, bg=BG)
        daftar.pack(side="left", fill="y", padx=(0, 14))

        teks = tk.Text(badan, wrap="word", font=("Consolas", 12), bg=KARTU, fg=TEKS,
                       relief="flat", padx=18, pady=14, highlightthickness=1,
                       highlightbackground=GARIS)
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
                      bg=KARTU, fg=TEKS, relief="flat", cursor="hand2", width=26,
                      font=(FONT, 11), padx=10, pady=6).pack(fill="x", pady=2)
        tampilkan(0)

        self.tombol(f, "← Kembali", self.tampil_menu, REDUP, size=11).pack(anchor="w")

    # ----------------------------------------------------------- papan skor --

    def tampil_papan_skor(self):
        f = self.ganti_layar()
        self.label(f, "🏆 Papan Skor", size=22, bold=True, fg=UNGU).pack(pady=(10, 16))

        tabel = tk.Frame(f, bg=KARTU, highlightbackground=GARIS, highlightthickness=1)
        tabel.pack(fill="x", padx=60)
        kolom = ["#", "Nama", "Nilai", "Skor", "Mode", "Tanggal"]
        for c, k in enumerate(kolom):
            self.label(tabel, k, size=11, bold=True, fg=REDUP, bg=KARTU).grid(
                row=0, column=c, padx=12, pady=8, sticky="w")
            tabel.grid_columnconfigure(c, weight=1)

        data = muat_skor()
        if not data:
            self.label(tabel, "Belum ada skor. Ayo main!", bg=KARTU, fg=REDUP).grid(
                row=1, column=0, columnspan=len(kolom), pady=16)
        for r, e in enumerate(data, start=1):
            nilai = [r, e.get("nama", "-"), e.get("nilai", "-"), f"{e.get('skor', '-')}/24",
                     e.get("mode", "-"), e.get("tanggal", "-")]
            for c, v in enumerate(nilai):
                self.label(tabel, str(v), size=11, bg=KARTU, bold=(c == 2)).grid(
                    row=r, column=c, padx=12, pady=4, sticky="w")

        self.tombol(f, "← Kembali", self.tampil_menu, REDUP, size=11).pack(pady=20)


if __name__ == "__main__":
    Aplikasi().mainloop()
