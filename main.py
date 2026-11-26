"""UntungCerdas — Game Literasi Matematika: Persentase Untung dan Rugi.

Jalankan dengan:  python main.py
"""

import queue
import threading
import tkinter as tk
from tkinter import messagebox

import ai_tutor
import rmt
from materi import MATERI
from permainan import MODE, Permainan, bintang, predikat
from skor import muat_skor, tambah_skor
from soal import parse_angka

# Tema biru
BG = "#EEF5FD"       # latar biru sangat muda
KARTU = "#FFFFFF"
LEMBUT = "#E3EEFB"   # latar pilihan jawaban
GARIS = "#C9DCF2"
TEKS = "#1C2B3A"
REDUP = "#5B6B7D"
UTAMA = "#1E6FD9"    # biru utama
BIRU = "#0B4F9C"     # biru tua
LANGIT = "#1590C9"   # biru langit
NILA = "#4B63D1"     # biru nila
HIJAU = "#2E9E5B"    # khusus tanda jawaban benar
MERAH = "#D64545"    # khusus tanda jawaban salah
WARNA_INDIKATOR = [UTAMA, NILA, LANGIT, BIRU]

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
        self.title("UntungCerdas — Literasi Matematika Untung & Rugi")
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
        self.keadaan = "jawab"
        self.cfg_ai = ai_tutor.muat_config()
        self._antrian_ai: queue.Queue = queue.Queue()
        self._id_ai = 0  # untuk mengabaikan jawaban AI dari tahap sebelumnya

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
        self.label(f, "UntungCerdas", size=32, bold=True, fg=UTAMA).pack()
        self.label(f, "Game Literasi Matematika — Persentase Untung dan Rugi",
                   size=14, fg=REDUP).pack(pady=(0, 20))

        baris = tk.Frame(f, bg=BG)
        baris.pack(pady=(0, 16))
        self.label(baris, "Nama pemain:", size=12).pack(side="left", padx=(0, 8))
        tk.Entry(baris, textvariable=self.nama, font=(FONT, 12), width=22,
                 relief="solid", bd=1).pack(side="left")

        for teks, cmd, warna in [
            ("📝  Soal Kisi-kisi (4 Misi)", lambda: self.mulai("kisi"), UTAMA),
            ("🎲  Latihan Soal Acak", lambda: self.mulai("acak"), LANGIT),
            ("📖  Pelajari Materi", self.tampil_materi, BIRU),
            ("🏆  Papan Skor", self.tampil_papan_skor, NILA),
            ("⚙️  Pengaturan AI", self.pengaturan_ai, LANGIT),
            ("✖  Keluar", self.destroy, REDUP),
        ]:
            self.tombol(f, teks, cmd, warna, width=24).pack(pady=5)

        status = (f"🤖 Tutor AI aktif ({ai_tutor.PENYEDIA[self.cfg_ai['penyedia']]['nama']})"
                  if ai_tutor.siap(self.cfg_ai) else
                  "🤖 Tutor AI belum aktif — isi API key di ⚙️ Pengaturan AI")
        self.label(f, status, size=10, fg=UTAMA if ai_tutor.siap(self.cfg_ai) else REDUP).pack(pady=(10, 0))

        self.label(f, "Model pembelajaran: Rigorous Mathematical Thinking (RMT) • 4 misi literasi "
                      "matematika • mediasi bertahap", size=10, fg=REDUP).pack(pady=(16, 0))

    # ---------------------------------------------------------------- game --

    def mulai(self, mode: str):
        if not self.nama.get().strip():
            self.nama.set("Pemain")
        self.permainan = Permainan(mode)
        self.tampil_orientasi()

    def _bar_atas(self, f, kanan_skor=False):
        p = self.permainan
        atas = tk.Frame(f, bg=BG)
        atas.pack(fill="x")
        self.label(atas, f"Misi {p.i_misi + 1} dari {len(p.misi)}  •  {MODE[p.mode]}  •  Model RMT",
                   size=12, bold=True).pack(side="left")
        self.tombol(atas, "Menu", self.konfirmasi_keluar, REDUP, size=10).pack(side="right")
        if kanan_skor:
            self.lbl_skor = self.label(atas, "", size=12, bold=True, fg=UTAMA)
            self.lbl_skor.pack(side="right", padx=16)

    def _kartu_gulir(self, f):
        gulir = AreaGulir(f)
        gulir.pack(fill="both", expand=True, pady=(12, 0))
        gulir.configure(highlightbackground=GARIS, highlightthickness=1)
        w = tk.Frame(gulir.isi, bg=KARTU)
        w.pack(fill="both", expand=True, padx=26, pady=20)
        return w

    def _bagian(self, w, judul, isi, warna=BIRU):
        self.label(w, judul, size=12, bold=True, fg=warna, bg=KARTU).pack(anchor="w", pady=(10, 0))
        self.label(w, isi, size=11, bg=KARTU, wraplength=self.px(880),
                   justify="left").pack(anchor="w")

    # ------------------------------------------------- RMT: orientasi misi --

    def tampil_orientasi(self):
        """MLE (intensionalitas & makna) + Learning Activity (analisis tugas)."""
        p = self.permainan
        m = p.misi_sekarang
        info = rmt.info_misi(m.nomor)
        warna = WARNA_INDIKATOR[(m.nomor - 1) % len(WARNA_INDIKATOR)]
        self.keadaan = "orientasi"
        f = self.ganti_layar()
        self._bar_atas(f)
        w = self._kartu_gulir(f)

        tk.Label(w, text=f"INDIKATOR {m.nomor}: {m.indikator.upper()}", bg=warna, fg="white",
                 font=(FONT, 9, "bold"), padx=8, pady=3).pack(anchor="w")
        self.label(w, m.judul, size=18, bold=True, fg=UTAMA, bg=KARTU, wraplength=self.px(880),
                   justify="left").pack(anchor="w", pady=(8, 0))
        self.label(w, "Orientasi Misi — Pengalaman Belajar Ter-mediasi (MLE)", size=10, fg=REDUP,
                   bg=KARTU).pack(anchor="w")
        self._bagian(w, "🎯 Tujuan Belajar (Intensionalitas)", info["tujuan"])
        self._bagian(w, "💡 Mengapa Ini Penting? (Makna)", info["makna"])
        self._bagian(w, "🔄 Dari Konsep Sehari-hari ke Konsep Matematika", info["sehari_hari"])
        self._bagian(w, "🔍 Analisis Tugas", "\n".join("• " + a for a in info["analisis"]))
        self._bagian(w, "🧭 Langkah Belajar (Learning Activity)",
                     "  →  ".join(f"{n}" for n, _ in rmt.LANGKAH_LA)
                     + "\nSetiap tahap diberi label fase kognitif: Input → Elaborasi → Output. "
                       "Jika jawabanmu belum tepat, kamu akan dimediasi lalu boleh mencoba lagi.")

        bawah = tk.Frame(f, bg=BG)
        bawah.pack(fill="x", pady=(12, 0))
        self.tombol(bawah, "Saya Siap — Mulai Misi →", self.bangun_layar_misi, UTAMA,
                    size=12).pack(side="right")
        self.bind("<Return>", lambda _e: self.bangun_layar_misi())

    # ------------------------------------------------------- layar tahapan --

    def bangun_layar_misi(self):
        p = self.permainan
        m = p.misi_sekarang
        warna = WARNA_INDIKATOR[(m.nomor - 1) % len(WARNA_INDIKATOR)]
        f = self.ganti_layar()
        self._bar_atas(f, kanan_skor=True)

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
        self.label(dalam, m.judul, size=14, bold=True, bg=KARTU, wraplength=self.px(360),
                   justify="left").pack(anchor="w", pady=(8, 0))
        self.label(dalam, m.soal, size=11, bg=KARTU, wraplength=self.px(360),
                   justify="left").pack(anchor="w", pady=(6, 12))

        self.label(dalam, "Tahapan Penyelesaian", size=10, bold=True, fg=REDUP,
                   bg=KARTU).pack(anchor="w")
        self.lbl_tahapan = []
        for _ in m.tahapan:
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
        self.btn_periksa = self.tombol(bawah, "Periksa Jawaban", self.periksa, LANGIT, size=12)
        self.btn_periksa.pack(side="left")
        self.btn_mediasi = self.tombol(bawah, "🧭 Mediasi", self.tampil_mediasi, NILA, size=12)
        self.btn_mediasi.pack(side="left", padx=(10, 0))
        self.btn_ai = self.tombol(bawah, "🤖 Mediator AI", self.minta_ai, BIRU, size=12)
        self.btn_ai.pack(side="left", padx=10)
        self.btn_lanjut = self.tombol(bawah, "Lanjut →", self.lanjut, UTAMA, size=12)
        self.btn_lanjut.pack(side="right")

        self.bind("<Return>", lambda _e: self.lanjut() if self.keadaan == "selesai" else self.periksa())
        self.tampil_tahap()

    def perbarui_status(self):
        p = self.permainan
        self.lbl_skor.config(text=f"⭐ Skor: {p.skor} / {p.skor_maks}")
        m = p.misi_sekarang
        for i, (t, lbl) in enumerate(zip(m.tahapan, self.lbl_tahapan)):
            s = p.skor_tahap[p.i_misi][i]
            u = p.skor_ulang[p.i_misi][i]
            fase = rmt.info_tahap(m.nomor, i)["fase"].capitalize()
            judul = f"{t.judul.split(':', 1)[0]} [{fase}]"
            if s is None:
                aktif = i == p.i_tahap
                teks = f"{'▶' if aktif else '○'} {judul} — skor {t.skor}"
                warna = UTAMA if aktif else REDUP
            elif s == t.skor:
                teks, warna = f"✔ {judul} — {s}/{t.skor}", HIJAU
            else:
                tambahan = " (✔ setelah mediasi)" if u else ""
                teks, warna = f"✘ {judul} — {s}/{t.skor}{tambahan}", MERAH
            lbl.config(text=teks, fg=warna,
                       font=(FONT, 10, "bold" if i == p.i_tahap else "normal"))

    def tampil_tahap(self):
        p = self.permainan
        t = p.tahap_sekarang
        info = rmt.info_tahap(p.misi_sekarang.nomor, p.i_tahap)
        self.keadaan = "jawab"  # jawab → (mediasi) → selesai
        self.level_mediasi = 0
        self.salah_dipilih = set()
        self._id_ai += 1
        self.jawaban_terakhir, self.benar_terakhir = "", False
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

        kotak = tk.Frame(wadah, bg=LEMBUT)
        kotak.pack(fill="x", pady=(8, 0))
        self.label(kotak, f"🧠 Fase {rmt.FASE[info['fase']]}", size=10, bold=True, fg=BIRU,
                   bg=LEMBUT).pack(anchor="w", padx=10, pady=(6, 0))
        self.label(kotak, f"Operasi mental: {info['operasi']}  •  Alat psikologis: {info['alat']}\n"
                          f"Fungsi kognitif: {info['fungsi']}", size=9, fg=REDUP, bg=LEMBUT,
                   justify="left", wraplength=self.px(540)).pack(anchor="w", padx=10, pady=(0, 6))

        self.label(wadah, t.perintah, size=12, bg=KARTU, wraplength=self.px(560),
                   justify="left").pack(anchor="w", pady=(10, 12))

        self.entri, self.lbl_butir, self.radio = [], [], []
        if t.jenis == "isian":
            for s in t.isian:
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

        self.lbl_hasil = self.label(wadah, "", size=13, bold=True, bg=KARTU, anchor="w",
                                    justify="left", wraplength=self.px(560))
        self.lbl_hasil.pack(fill="x", pady=(14, 4))
        self.wadah_tahap = wadah
        self.lbl_mediasi = tk.Label(wadah, text="", bg="#EEF0FD", fg=TEKS, font=(FONT, 11),
                                    justify="left", anchor="w", wraplength=self.px(540),
                                    padx=12, pady=10)
        self.lbl_bahas = tk.Label(wadah, text="", bg=KARTU, fg=TEKS, font=(FONT, 11),
                                  justify="left", anchor="w", wraplength=self.px(560))
        self.lbl_bahas.pack(fill="x")
        self.lbl_ai = tk.Label(wadah, text="", bg=LEMBUT, fg=TEKS, font=(FONT, 11),
                               justify="left", anchor="w", wraplength=self.px(540),
                               padx=12, pady=10)

        self.btn_periksa.config(state="normal", text="Periksa Jawaban")
        self.btn_mediasi.config(state="normal")
        self.btn_ai.config(state="normal", text="🤖 Mediator AI")
        self.btn_lanjut.config(state="disabled", text="Lanjut →")
        self.perbarui_status()

    # ------------------------------------------- RMT: mediasi bertingkat --

    def tampil_mediasi(self):
        """Pertanyaan terpimpin bertingkat (mediated questioning), tanpa membocorkan jawaban."""
        if self.keadaan == "selesai":
            return
        p = self.permainan
        daftar = rmt.info_tahap(p.misi_sekarang.nomor, p.i_tahap)["mediasi"]
        self.level_mediasi = min(self.level_mediasi + 1, len(daftar))
        teks = "\n".join(f"🧭 Mediasi {i + 1}: {q}" for i, q in enumerate(daftar[:self.level_mediasi]))
        self.lbl_mediasi.config(text=teks)
        if not self.lbl_mediasi.winfo_ismapped():
            self.lbl_mediasi.pack(fill="x", pady=(4, 6), before=self.lbl_bahas)
        if self.level_mediasi >= len(daftar):
            self.btn_mediasi.config(state="disabled")

    def ambil_jawaban(self, t):
        if t.jenis == "isian":
            jawaban = [e.get() for e in self.entri]
            if any(parse_angka(j) is None for j in jawaban):
                return None, "Isi semua kotak dengan angka terlebih dahulu."
            return jawaban, None
        jawaban = self.pilih.get()
        if jawaban < 0:
            return None, "Pilih salah satu jawaban terlebih dahulu."
        return jawaban, None

    def periksa(self):
        if self.keadaan == "selesai":
            return
        p = self.permainan
        t = p.tahap_sekarang
        jawaban, galat = self.ambil_jawaban(t)
        if galat:
            self.lbl_hasil.config(text=galat, fg=REDUP)
            return

        if self.keadaan == "jawab":
            hasil = p.jawab(jawaban)
        else:  # uji ulang setelah mediasi (asesmen dinamis)
            hasil = p.jawab_ulang(jawaban)
        self.jawaban_terakhir = ai_tutor.teks_jawaban(t, jawaban)
        self.benar_terakhir = hasil.benar
        if t.jenis == "pilihan" and not hasil.benar:
            self.salah_dipilih.add(jawaban)

        if self.keadaan == "jawab" and not hasil.benar:
            self.masuk_mediasi(hasil, jawaban)
            return
        if hasil.benar and self.keadaan == "jawab":
            self.lbl_hasil.config(text=f"✔ Tepat! +{hasil.skor} skor", fg=HIJAU)
        elif hasil.benar:
            self.lbl_hasil.config(text="✔ Tepat setelah mediasi! Kemampuanmu berkembang — "
                                       "dicatat sebagai potensi belajar.", fg=HIJAU)
        else:
            self.lbl_hasil.config(text="✘ Masih belum tepat. Pelajari pembahasannya:", fg=MERAH)
        self.selesaikan_tahap()

    def masuk_mediasi(self, hasil, jawaban):
        """Uji → Mediasi → Uji ulang (LPAD Feuerstein). Kunci belum ditampilkan."""
        self.keadaan = "mediasi"
        t = self.permainan.tahap_sekarang
        if t.jenis == "isian":
            for e, lbl, ok in zip(self.entri, self.lbl_butir, hasil.per_butir):
                if ok:
                    e.config(state="disabled")
                    lbl.config(text="✔", fg=HIJAU)
                else:
                    lbl.config(text="✘ periksa lagi", fg=MERAH)
        else:
            self.radio[jawaban].config(state="disabled", bg="#FBE3E3", disabledforeground=MERAH)
            self.pilih.set(-1)
        self.lbl_hasil.config(text=f"✘ Belum tepat (skor tahap 0/{t.skor}). Jangan menyerah — "
                                   "ikuti mediasi di bawah, lalu coba lagi sekali.", fg=MERAH)
        self.tampil_mediasi()
        self.gulir_ke_bawah()
        self.btn_periksa.config(text="🔁 Coba Lagi")
        self.btn_lanjut.config(state="normal", text="Lihat Pembahasan")
        self.perbarui_status()

    def selesaikan_tahap(self):
        self.keadaan = "selesai"
        p = self.permainan
        t = p.tahap_sekarang
        if t.jenis == "isian":
            per_butir = t.periksa([e.get() for e in self.entri])
            for e, lbl, ok, s in zip(self.entri, self.lbl_butir, per_butir, t.isian):
                e.config(state="disabled")
                lbl.config(text="✔" if ok else f"✘  {s.kunci()}", fg=HIJAU if ok else MERAH)
        else:
            for i, rb in enumerate(self.radio):
                rb.config(state="disabled")
                if i == t.kunci_pilihan:
                    rb.config(bg="#DFF3E6", disabledforeground=HIJAU)
                elif i in self.salah_dipilih:
                    rb.config(bg="#FBE3E3", disabledforeground=MERAH)
                else:
                    rb.config(disabledforeground=REDUP)

        self.lbl_bahas.config(text="Pembahasan:\n" + t.penjelasan)
        self.btn_periksa.config(state="disabled")
        self.btn_mediasi.config(state="disabled")
        self.btn_ai.config(state="normal", text="🤖 Diagnosis AI")
        self.btn_lanjut.config(state="normal", text="Refleksi Misi →" if p.tahap_terakhir
                               else "Tahap Berikutnya →")
        self.btn_lanjut.focus_set()
        self.perbarui_status()
        self.gulir_ke_bawah()

    def gulir_ke_bawah(self):
        """Tampilkan kotak mediasi/pembahasan yang muncul di bawah pilihan jawaban."""
        self.update_idletasks()
        self.gulir.canvas.yview_moveto(1.0)

    def lanjut(self):
        if self.keadaan == "mediasi":  # siswa memilih melihat pembahasan tanpa uji ulang
            self.lbl_hasil.config(text="Pembahasan ditampilkan tanpa uji ulang.", fg=REDUP)
            self.selesaikan_tahap()
            return
        if self.keadaan != "selesai":
            return
        p = self.permainan
        if p.tahap_terakhir:
            self.tampil_refleksi()
        else:
            p.maju()
            self.tampil_tahap()

    # --------------------------------------- RMT: refleksi & transendensi --

    def tampil_refleksi(self):
        p = self.permainan
        m = p.misi_sekarang
        info = rmt.info_misi(m.nomor)
        f = self.ganti_layar()
        self._bar_atas(f)
        w = self._kartu_gulir(f)

        s = p.skor_misi(p.i_misi)
        b = bintang(s, m.skor_maks)
        self.label(w, f"🪞 Refleksi & Transendensi — Misi {m.nomor}", size=18, bold=True,
                   fg=UTAMA, bg=KARTU).pack(anchor="w")
        self.label(w, f"{m.judul}  •  Skor {s}/{m.skor_maks}  {'★' * b}{'☆' * (3 - b)}",
                   size=11, fg=REDUP, bg=KARTU).pack(anchor="w")
        self._bagian(w, "🌉 Transendensi — Prinsip Umum", info["transendensi"])

        self.label(w, "🪞 Refleksi Diri (Metakognisi)", size=12, bold=True, fg=BIRU,
                   bg=KARTU).pack(anchor="w", pady=(14, 0))
        self.label(w, "1. Fase berpikir mana yang paling menantang bagimu pada misi ini?",
                   size=11, bg=KARTU).pack(anchor="w", pady=(4, 0))
        self.var_fase = tk.StringVar(value="")
        for kode, teks in rmt.REFLEKSI_FASE:
            tk.Radiobutton(w, text=teks, variable=self.var_fase, value=kode, bg=KARTU,
                           activebackground=KARTU, font=(FONT, 11), anchor="w").pack(anchor="w")
        self.label(w, "2. Strategi apa yang paling membantumu?", size=11,
                   bg=KARTU).pack(anchor="w", pady=(8, 0))
        self.var_strategi = tk.StringVar(value="")
        for teks in rmt.REFLEKSI_STRATEGI:
            tk.Radiobutton(w, text=teks, variable=self.var_strategi, value=teks, bg=KARTU,
                           activebackground=KARTU, font=(FONT, 11), anchor="w").pack(anchor="w")
        self.lbl_hasil = self.label(w, "", size=11, fg=MERAH, bg=KARTU)
        self.lbl_hasil.pack(anchor="w", pady=(6, 0))
        self.lbl_ai = tk.Label(w, text="", bg=LEMBUT, fg=TEKS, font=(FONT, 11), justify="left",
                               anchor="w", wraplength=self.px(860), padx=12, pady=10)
        self.keadaan = "refleksi"
        self._id_ai += 1

        bawah = tk.Frame(f, bg=BG)
        bawah.pack(fill="x", pady=(12, 0))
        self.btn_ai = self.tombol(bawah, "🤖 Tanggapan AI atas Refleksiku", self.minta_ai, BIRU,
                                  size=12)
        self.btn_ai.pack(side="left")
        teks = "Lihat Hasil Akhir →" if p.misi_terakhir else "Misi Berikutnya →"
        self.tombol(bawah, teks, self.selesai_refleksi, UTAMA, size=12).pack(side="right")

    def _refleksi_terpilih(self):
        fase, strategi = self.var_fase.get(), self.var_strategi.get()
        if not fase or not strategi:
            self.lbl_hasil.config(text="Jawab kedua pertanyaan refleksi terlebih dahulu.")
            return None
        return fase, strategi

    def selesai_refleksi(self):
        pilihan = self._refleksi_terpilih()
        if not pilihan:
            return
        p = self.permainan
        p.simpan_refleksi(*pilihan)
        p.maju()
        if p.selesai:
            self.tampil_hasil_akhir()
        else:
            self.tampil_orientasi()

    # -------------------------------------------------------------- tutor AI --

    def minta_ai(self):
        """Mediasi AI (sebelum/saat mediasi), diagnosis AI (sesudah), atau tanggapan refleksi."""
        if not ai_tutor.siap(self.cfg_ai):
            if messagebox.askyesno("Tutor AI belum aktif",
                                   "API key DeepSeek belum diisi.\nBuka Pengaturan AI sekarang?"):
                self.pengaturan_ai()
            return
        p = self.permainan
        m = p.misi_sekarang
        if self.keadaan == "refleksi":
            pilihan = self._refleksi_terpilih()
            if not pilihan:
                return
            label_fase = dict(rmt.REFLEKSI_FASE)[pilihan[0]]
            pesan = ai_tutor.pesan_refleksi(m, label_fase, pilihan[1])
            judul = "🤖 Tanggapan Mediator AI"
        elif self.keadaan == "selesai":
            t = p.tahap_sekarang
            pesan = ai_tutor.pesan_penjelasan(m, t, self.jawaban_terakhir, self.benar_terakhir)
            judul = "🤖 Diagnosis Mediator AI"
        else:
            t = p.tahap_sekarang
            if t.jenis == "isian":
                sementara = ai_tutor.teks_jawaban(t, [e.get() for e in self.entri])
            else:
                sementara = ai_tutor.teks_jawaban(t, self.pilih.get())
            pesan = ai_tutor.pesan_petunjuk(m, t, sementara)
            judul = "🤖 Mediator AI"
        self.tampilkan_ai(f"{judul}\nSedang berpikir…")
        self.btn_ai.config(state="disabled")
        self._jalankan_ai(pesan, judul, self._id_ai)

    def _jalankan_ai(self, pesan, judul, id_ai):
        cfg = dict(self.cfg_ai)

        def kerja():
            try:
                teks = ai_tutor.panggil(cfg, pesan)
            except ai_tutor.AIError as e:
                teks = f"⚠️ {e}"
            self._antrian_ai.put((id_ai, judul, teks))

        threading.Thread(target=kerja, daemon=True).start()
        self.after(150, self._cek_ai)

    def _cek_ai(self):
        try:
            id_ai, judul, teks = self._antrian_ai.get_nowait()
        except queue.Empty:
            self.after(150, self._cek_ai)
            return
        if id_ai != self._id_ai:
            return  # siswa sudah pindah tahap/layar
        try:
            self.tampilkan_ai(f"{judul}\n{teks}")
            self.btn_ai.config(state="normal")
        except tk.TclError:
            pass

    def tampilkan_ai(self, teks):
        try:
            self.lbl_ai.config(text=teks)
            if not self.lbl_ai.winfo_ismapped():
                self.lbl_ai.pack(fill="x", pady=(12, 0))
        except tk.TclError:
            pass

    def pengaturan_ai(self):
        win = tk.Toplevel(self)
        win.title("Pengaturan Tutor AI (DeepSeek)")
        win.configure(bg=BG)
        win.transient(self)
        win.grab_set()
        f = tk.Frame(win, bg=BG)
        f.pack(fill="both", expand=True, padx=20, pady=16)

        self.label(f, "⚙️ Pengaturan Tutor AI", size=16, bold=True, fg=UTAMA).pack(anchor="w")
        self.label(f, "Masukkan API key DeepSeek agar aplikasi bisa memberi petunjuk dan "
                      "penjelasan cerdas. Key hanya disimpan di komputer ini (config_ai.json) "
                      "dan tidak ikut diunggah ke GitHub.", size=10, fg=REDUP,
                   wraplength=self.px(460), justify="left").pack(anchor="w", pady=(2, 12))

        var_penyedia = tk.StringVar(value=self.cfg_ai["penyedia"])
        self.label(f, "Penyedia:", size=11, bold=True).pack(anchor="w")
        for kode, info in ai_tutor.PENYEDIA.items():
            tk.Radiobutton(f, text=info["nama"], variable=var_penyedia, value=kode, bg=BG,
                           activebackground=BG, font=(FONT, 11), anchor="w").pack(anchor="w")

        self.label(f, "API key:", size=11, bold=True).pack(anchor="w", pady=(10, 0))
        var_key = tk.StringVar(value=self.cfg_ai["api_key"])
        e_key = tk.Entry(f, textvariable=var_key, show="•", font=(FONT, 11), width=46,
                         relief="solid", bd=1)
        e_key.pack(anchor="w", fill="x")
        var_lihat = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Tampilkan key", variable=var_lihat, bg=BG, activebackground=BG,
                       command=lambda: e_key.config(show="" if var_lihat.get() else "•")
                       ).pack(anchor="w")

        self.label(f, "Model (kosongkan untuk bawaan):", size=11, bold=True).pack(anchor="w", pady=(8, 0))
        var_model = tk.StringVar(value=self.cfg_ai["model"])
        tk.Entry(f, textvariable=var_model, font=(FONT, 11), width=46, relief="solid",
                 bd=1).pack(anchor="w", fill="x")
        self.label(f, "Bawaan: " + " • ".join(f"{k} → {v['model']}" for k, v in ai_tutor.PENYEDIA.items()),
                   size=9, fg=REDUP, wraplength=self.px(460), justify="left").pack(anchor="w")

        lbl_status = self.label(f, "", size=10, wraplength=self.px(460), justify="left")
        lbl_status.pack(anchor="w", pady=(10, 0))

        def ambil():
            return {"penyedia": var_penyedia.get(), "api_key": var_key.get().strip(),
                    "model": var_model.get().strip()}

        def simpan():
            self.cfg_ai = ambil()
            try:
                ai_tutor.simpan_config(self.cfg_ai)
            except OSError as e:
                messagebox.showerror("Gagal menyimpan", str(e), parent=win)
                return
            win.destroy()
            if self.permainan is None or self.permainan.selesai:
                self.tampil_menu()

        def tes():
            cfg = ambil()
            if not ai_tutor.siap(cfg):
                lbl_status.config(text="Isi API key terlebih dahulu.", fg=MERAH)
                return
            lbl_status.config(text="Menghubungi AI…", fg=REDUP)
            hasil: queue.Queue = queue.Queue()

            def kerja():
                try:
                    teks = ai_tutor.panggil(cfg, [{"role": "user", "content":
                                                   "Jawab singkat: 20% dari Rp50.000 berapa?"}],
                                            maks_token=60)
                    hasil.put((True, teks))
                except ai_tutor.AIError as e:
                    hasil.put((False, str(e)))

            def cek():
                try:
                    ok, teks = hasil.get_nowait()
                except queue.Empty:
                    win.after(150, cek)
                    return
                if win.winfo_exists():
                    lbl_status.config(text=("✔ Berhasil terhubung! Jawaban AI: " + teks) if ok
                                      else "✘ " + teks, fg=HIJAU if ok else MERAH)

            threading.Thread(target=kerja, daemon=True).start()
            win.after(150, cek)

        tombol = tk.Frame(f, bg=BG)
        tombol.pack(fill="x", pady=(14, 0))
        self.tombol(tombol, "Tes Koneksi", tes, LANGIT, size=11).pack(side="left")
        self.tombol(tombol, "Simpan", simpan, UTAMA, size=11).pack(side="right")
        self.tombol(tombol, "Batal", win.destroy, REDUP, size=11).pack(side="right", padx=8)

    def konfirmasi_keluar(self):
        if messagebox.askyesno("Keluar", "Akhiri permainan dan kembali ke menu?"):
            self.tampil_menu()

    # ---------------------------------------------------------- hasil akhir --

    def tampil_hasil_akhir(self):
        p = self.permainan
        nama = self.nama.get().strip() or "Pemain"
        peringkat = tambah_skor(nama, p.nilai, p.skor, MODE[p.mode])

        f = self.ganti_layar()
        w = self._kartu_gulir(f)
        kepala = tk.Frame(w, bg=KARTU)
        kepala.pack(fill="x")
        self.label(kepala, "🏆" if p.nilai >= 75 else "📚", size=36, bg=KARTU).pack()
        self.label(kepala, "Semua Misi Selesai!", size=22, bold=True, fg=UTAMA, bg=KARTU).pack()
        self.label(kepala, f"Nilai {nama}: {p.nilai}", size=26, bold=True, bg=KARTU).pack(pady=(4, 0))
        self.label(kepala, f"Skor {p.skor} dari {p.skor_maks}  •  Predikat {predikat(p.nilai)}",
                   size=12, fg=REDUP, bg=KARTU).pack(pady=(0, 10))

        # tabel capaian per indikator
        tabel = tk.Frame(w, bg=KARTU, highlightbackground=GARIS, highlightthickness=1)
        tabel.pack(fill="x", padx=20)
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
                self.label(tabel, str(v), size=10, bg=KARTU,
                           wraplength=self.px(300) if c in (1, 2) else 0,
                           justify="left", fg=UTAMA if c == 4 else TEKS).grid(
                    row=r, column=c, padx=10, pady=4, sticky="w")

        # profil fungsi kognitif RMT
        rmt_box = tk.Frame(w, bg=LEMBUT)
        rmt_box.pack(fill="x", padx=20, pady=(14, 0))
        dalam = tk.Frame(rmt_box, bg=LEMBUT)
        dalam.pack(fill="x", padx=14, pady=10)
        self.label(dalam, "🧠 Profil Fungsi Kognitif (Model RMT)", size=13, bold=True, fg=BIRU,
                   bg=LEMBUT).pack(anchor="w")
        profil = rmt.profil_fase(p)
        lebar = self.px(320)
        for kode, (d, mk) in profil.items():
            baris = tk.Frame(dalam, bg=LEMBUT)
            baris.pack(fill="x", pady=3)
            self.label(baris, rmt.FASE[kode], size=10, bg=LEMBUT, width=36,
                       anchor="w").pack(side="left")
            kanvas = tk.Canvas(baris, width=lebar, height=self.px(14), bg="#D5E3F5",
                               highlightthickness=0)
            kanvas.pack(side="left", padx=6)
            if mk:
                kanvas.create_rectangle(0, 0, lebar * d / mk, self.px(14), fill=UTAMA, width=0)
            self.label(baris, f"{d}/{mk} ({round(d * 100 / mk) if mk else 0}%)", size=10,
                       bg=LEMBUT).pack(side="left")

        self.label(dalam, f"📈 Asesmen dinamis (Uji – Mediasi – Uji ulang): skor awal {p.skor}/"
                          f"{p.skor_maks} → setelah mediasi {p.skor_setelah_mediasi}/{p.skor_maks} "
                          f"({p.jumlah_mediasi} kali uji ulang).", size=10, bg=LEMBUT,
                   wraplength=self.px(860), justify="left").pack(anchor="w", pady=(8, 0))
        lemah = rmt.fase_terlemah(profil)
        saran = ("✅ Semua fase kognitif sudah sangat baik. Pertahankan cara berpikir yang teliti!"
                 if lemah is None else
                 f"🎯 Fase yang perlu dilatih: {rmt.FASE[lemah]}.\n{rmt.REKOMENDASI_FASE[lemah]}")
        self.label(dalam, saran, size=10, bg=LEMBUT, wraplength=self.px(860),
                   justify="left").pack(anchor="w", pady=(6, 0))
        refleksi = [r for r in p.refleksi if r]
        if refleksi:
            ringkas = "; ".join(f"Misi {i + 1}: sulit di {dict(rmt.REFLEKSI_FASE)[r['fase']].split(' —')[0]}"
                                for i, r in enumerate(p.refleksi) if r)
            self.label(dalam, f"🪞 Refleksimu — {ringkas}.", size=10, fg=REDUP, bg=LEMBUT,
                       wraplength=self.px(860), justify="left").pack(anchor="w", pady=(6, 0))

        if peringkat:
            self.label(w, f"Kamu masuk papan skor di peringkat #{peringkat}!",
                       size=11, bold=True, fg=NILA, bg=KARTU).pack(pady=(10, 0))

        tombol = tk.Frame(f, bg=BG)
        tombol.pack(pady=(12, 0))
        self.tombol(tombol, "Ulangi", lambda: self.mulai(p.mode), LANGIT).pack(side="left", padx=6)
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
        self.label(f, "🏆 Papan Skor", size=22, bold=True, fg=NILA).pack(pady=(10, 16))

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
