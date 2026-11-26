"""Soal Mathematical Literacy — Persentase Menghitung Untung dan Rugi.

Struktur soal mengikuti kisi-kisi:
  1. Mathematical Reasoning                                      (skor maks 6)
  2. Formulating Situations Mathematically                       (skor maks 6)
  3. Employing Mathematical Concepts, Facts, and Procedures       (skor maks 6)
  4. Interpreting, Applying, and Evaluating Mathematical Outcomes (skor maks 6)

Setiap soal (misi) dikerjakan per tahapan penyelesaian. Setiap tahap punya
skor sendiri, persis seperti kolom "Skor per Tahapan" pada kisi-kisi.
Tersedia soal asli kisi-kisi (misi_kisi_kisi) dan variasi acak (misi_acak)
dengan struktur tahapan yang sama.
"""

import random
import re
from dataclasses import dataclass, field
from itertools import permutations

TOLERANSI = 0.01

INDIKATOR = [
    ("Mathematical Reasoning",
     "Siswa mampu mengidentifikasi hubungan matematis, membandingkan alternatif, "
     "memberikan alasan, dan menentukan keputusan yang dapat dipertanggungjawabkan."),
    ("Formulating Situations Mathematically",
     "Siswa mampu mengidentifikasi informasi relevan, menentukan besaran, dan "
     "menerjemahkan situasi nyata menjadi model matematika."),
    ("Employing Mathematical Concepts, Facts, and Procedures",
     "Siswa mampu memilih serta menggunakan konsep, operasi, prosedur, dan strategi "
     "matematika untuk memperoleh solusi."),
    ("Interpreting, Applying, and Evaluating Mathematical Outcomes",
     "Siswa mampu menafsirkan hasil matematika dalam konteks, menilai kewajaran hasil, "
     "dan mengambil keputusan berdasarkan hasil perhitungan."),
]


# ------------------------------------------------------------ format angka --

def angka(n) -> str:
    """15000 -> '15.000'"""
    return f"{round(n):,}".replace(",", ".")


def rupiah(n) -> str:
    """15000 -> 'Rp15.000'"""
    return "Rp" + angka(n)


def desimal(x, digit=2) -> str:
    """0.15 -> '0,15'; 17.647 -> '17,65'; 25.0 -> '25'"""
    s = f"{x:.{digit}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def persen(x) -> str:
    return desimal(x) + "%"


def parse_angka(teks):
    """Ubah teks jawaban siswa menjadi angka. None jika tidak valid.

    Menerima: '15000', '15.000', 'Rp 15.000', '15.000,00', '25', '25%', '17,65'.
    Titik dianggap pemisah ribuan bila polanya 1.234.567; koma = desimal.
    """
    if teks is None:
        return None
    t = teks.strip().lower()
    for kata in ("rp", "%", " "):
        t = t.replace(kata, "")
    if not t:
        return None
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", t, flags=re.ASCII):
        t = t.replace(".", "")
    t = t.replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d+)?", t, flags=re.ASCII):
        return None
    nilai = float(t)
    return int(nilai) if nilai.is_integer() else nilai


# ---------------------------------------------------------------- struktur --

@dataclass
class Isian:
    """Satu kotak isian angka."""
    label: str
    jawaban: float
    satuan: str  # "Rp" atau "%"

    def cocok(self, teks) -> bool:
        v = parse_angka(teks)
        return v is not None and abs(v - self.jawaban) <= TOLERANSI

    def kunci(self) -> str:
        return rupiah(self.jawaban) if self.satuan == "Rp" else persen(self.jawaban)


@dataclass
class Tahap:
    judul: str
    perintah: str
    skor: int
    penjelasan: str
    isian: list = field(default_factory=list)      # list[Isian]
    pilihan: list = field(default_factory=list)    # list[str]
    kunci_pilihan: int = -1

    @property
    def jenis(self) -> str:
        return "pilihan" if self.pilihan else "isian"

    def periksa(self, jawaban) -> list:
        """jawaban = indeks pilihan (int) atau list teks isian.
        Mengembalikan list benar/salah per butir."""
        if self.pilihan:
            return [jawaban == self.kunci_pilihan]
        if not isinstance(jawaban, (list, tuple)) or len(jawaban) != len(self.isian):
            return [False] * len(self.isian)
        return [i.cocok(t) for i, t in zip(self.isian, jawaban)]


@dataclass
class Misi:
    nomor: int
    judul: str
    soal: str
    tahapan: list  # list[Tahap]

    @property
    def indikator(self) -> str:
        return INDIKATOR[self.nomor - 1][0]

    @property
    def deskripsi_indikator(self) -> str:
        return INDIKATOR[self.nomor - 1][1]

    @property
    def skor_maks(self) -> int:
        return sum(t.skor for t in self.tahapan)


def _tahap_pilihan(rng, judul, perintah, skor, penjelasan, benar, salah) -> Tahap:
    opsi = [benar]
    for s in salah:
        if s not in opsi:
            opsi.append(s)
        if len(opsi) == 4:
            break
    rng.shuffle(opsi)
    return Tahap(judul, perintah, skor, penjelasan, pilihan=opsi, kunci_pilihan=opsi.index(benar))


def _kapital(s: str) -> str:
    return s[:1].upper() + s[1:]


def _gabung_toko(nama: list) -> str:
    t = [f"Toko {n}" for n in nama]
    if len(t) == 1:
        return t[0]
    return ", ".join(t[:-1]) + (", dan " if len(t) > 2 else " dan ") + t[-1]


def _urutan(nilai: dict, nama: list) -> str:
    urut = sorted(nama, key=lambda n: -nilai[n])
    s = f"Toko {urut[0]}"
    for a, b in zip(urut, urut[1:]):
        s += (" = " if abs(nilai[a] - nilai[b]) < 1e-9 else " > ") + f"Toko {b}"
    return s


# ------------------------------------------- Soal 1: Mathematical Reasoning --

def misi_penalaran(barang: str, toko: list, rng: random.Random) -> Misi:
    """toko = [(nama, harga_beli, harga_jual), ...]"""
    nama = [t[0] for t in toko]
    beli = {n: b for n, b, _ in toko}
    jual = {n: j for n, _, j in toko}
    untung = {n: jual[n] - beli[n] for n in nama}
    pct = {n: untung[n] * 100 / beli[n] for n in nama}
    maks = max(pct.values())
    pemenang = [n for n in nama if abs(pct[n] - maks) < 1e-9]
    n_rp = max(nama, key=lambda n: untung[n])
    n_jual = max(nama, key=lambda n: jual[n])
    n_murah = min(nama, key=lambda n: beli[n])
    n_kalah = min(nama, key=lambda n: pct[n])

    kalimat = []
    for i, n in enumerate(nama):
        objek = f"sebuah {barang}" if i == 0 else (f"{barang} sejenis" if i == 1 else barang)
        kalimat.append(f"Toko {n} membeli {objek} seharga {rupiah(beli[n])} "
                       f"dan menjualnya seharga {rupiah(jual[n])}.")
    soal = (" ".join(kalimat) + " Toko manakah yang memperoleh persentase keuntungan "
            "paling besar? Tunjukkan perhitungan dan alasanmu.")

    def data(b, j):
        return "\n".join(f"Toko {n}: harga beli {rupiah(b[n])}, harga jual {rupiah(j[n])}"
                         for n in nama)

    tukar_satu = dict(beli), dict(jual)
    tukar_satu[0][nama[1]], tukar_satu[1][nama[1]] = jual[nama[1]], beli[nama[1]]
    geser = {n: jual[nama[(i + 1) % len(nama)]] for i, n in enumerate(nama)}
    t1 = _tahap_pilihan(
        rng, "Tahap 1: Mengidentifikasi harga beli dan harga jual setiap toko",
        "Pilih data harga beli dan harga jual yang benar untuk setiap toko.", 1,
        "Harga beli = harga saat toko membeli tas; harga jual = harga saat toko menjualnya.\n"
        + data(beli, jual),
        data(beli, jual), [data(jual, beli), data(*tukar_satu), data(beli, geser)])

    t2 = Tahap(
        "Tahap 2: Menghitung keuntungan masing-masing",
        "Hitung besar keuntungan setiap toko (harga jual − harga beli).", 1,
        "\n".join(f"Toko {n} = {rupiah(jual[n])} − {rupiah(beli[n])} = {rupiah(untung[n])}."
                  for n in nama),
        isian=[Isian(f"Keuntungan Toko {n}", untung[n], "Rp") for n in nama])

    t3 = Tahap(
        "Tahap 3: Menghitung persentase keuntungan",
        "Hitung persentase keuntungan setiap toko dengan rumus\n"
        "(keuntungan ÷ harga beli) × 100%.", 2,
        "\n".join(f"Toko {n} = ({angka(untung[n])} ÷ {angka(beli[n])}) × 100% = {persen(pct[n])}."
                  for n in nama),
        isian=[Isian(f"Persentase Toko {n}", pct[n], "%") for n in nama])

    benar_urut = _urutan(pct, nama)
    salah_urut = [_urutan(untung, nama), _urutan(jual, nama)]
    perm = [" > ".join(f"Toko {n}" for n in p) for p in permutations(nama)]
    rng.shuffle(perm)
    t4 = _tahap_pilihan(
        rng, "Tahap 4: Membandingkan hasil",
        "Bandingkan persentase keuntungan ketiga toko. Urutan mana yang benar "
        "(dari yang terbesar)?", 1,
        "Persentase keuntungan: " + ", ".join(persen(pct[n]) for n in nama)
        + f".\nJadi urutannya: {benar_urut}.",
        benar_urut, salah_urut + perm)

    benar_simpul = (f"{_gabung_toko(pemenang)} memperoleh persentase keuntungan terbesar, "
                    f"yaitu {'sama-sama ' if len(pemenang) > 1 else ''}{persen(maks)}.")
    salah_simpul = []
    if pemenang != [n_rp]:
        salah_simpul.append(f"Hanya Toko {n_rp}, karena besar keuntungannya paling banyak "
                            f"({rupiah(untung[n_rp])}).")
    if pemenang != [n_jual]:
        salah_simpul.append(f"Hanya Toko {n_jual}, karena harga jualnya paling tinggi "
                            f"({rupiah(jual[n_jual])}).")
    if pemenang != [n_murah]:
        salah_simpul.append(f"Hanya Toko {n_murah}, karena harga belinya paling murah.")
    salah_simpul.append("Semua toko memperoleh persentase keuntungan yang sama.")
    salah_simpul.append(f"Hanya Toko {n_kalah}, karena persentase keuntungannya paling besar.")
    catatan = (f"Perhatikan: keuntungan rupiah terbesar dimiliki Toko {n_rp} "
               f"({rupiah(untung[n_rp])}), tetapi yang dibandingkan adalah PERSENTASE "
               f"terhadap harga beli, bukan besar rupiahnya.")
    t5 = _tahap_pilihan(
        rng, "Tahap 5: Menyimpulkan",
        "Pilih kesimpulan dan alasan yang tepat.", 1,
        f"{benar_simpul}\n{catatan}", benar_simpul, salah_simpul)

    return Misi(1, "Memilih Penawaran dengan Keuntungan Terbesar", soal, [t1, t2, t3, t4, t5])


# ---------------------------- Soal 2: Formulating Situations Mathematically --

def misi_formulasi(nama: str, barang: str, beli: int, p: int, rng: random.Random) -> Misi:
    untung = beli * p // 100
    jual = beli + untung
    soal = (f"{nama} membeli sebuah {barang} dengan harga {rupiah(beli)}. {nama} ingin "
            f"menjual {barang} tersebut dengan memperoleh keuntungan sebesar {p}% dari "
            f"harga beli. Berapakah harga jual {barang} yang harus ditetapkan? Tuliskan "
            f"model matematika dan langkah penyelesaiannya.")

    t1 = _tahap_pilihan(
        rng, "Tahap 1: Mengidentifikasi informasi",
        "Apa yang diketahui dan apa yang ditanyakan?", 1,
        f"Diketahui: harga beli = {rupiah(beli)} dan persentase keuntungan = {p}%.\n"
        f"Ditanya: harga jual.",
        f"Diketahui: harga beli = {rupiah(beli)} dan persentase keuntungan = {p}%.\n"
        f"Ditanya: harga jual.",
        [f"Diketahui: harga jual = {rupiah(beli)} dan persentase keuntungan = {p}%.\n"
         f"Ditanya: harga beli.",
         f"Diketahui: harga beli = {rupiah(beli)} dan keuntungan = {rupiah(p)}.\n"
         f"Ditanya: harga jual.",
         f"Diketahui: harga beli = {rupiah(beli)} dan persentase keuntungan = {p}%.\n"
         f"Ditanya: persentase kerugian."])

    t2 = Tahap(
        "Tahap 2: Menentukan besar keuntungan",
        f"Hitung besar keuntungan = {p}% × harga beli.", 1,
        f"Keuntungan = {p}% × {rupiah(beli)} = {rupiah(untung)}.",
        isian=[Isian("Besar keuntungan", untung, "Rp")])

    t3 = _tahap_pilihan(
        rng, "Tahap 3: Menentukan model matematika",
        "Model matematika mana yang tepat untuk mencari harga jual?", 1,
        "Model matematika: Harga jual = harga beli + keuntungan.",
        "Harga jual = harga beli + keuntungan",
        ["Harga jual = harga beli − keuntungan",
         "Harga jual = keuntungan − harga beli",
         "Harga jual = harga beli × keuntungan"])

    t4 = _tahap_pilihan(
        rng, "Tahap 4: Memasukkan nilai yang diketahui",
        "Substitusikan nilai yang diketahui ke dalam model.", 1,
        f"Harga jual = {rupiah(beli)} + {rupiah(untung)}.",
        f"Harga jual = {rupiah(beli)} + {rupiah(untung)}",
        [f"Harga jual = {rupiah(beli)} − {rupiah(untung)}",
         f"Harga jual = {rupiah(beli)} + {p}",
         f"Harga jual = {rupiah(beli)} × {p}%"])

    t5 = Tahap(
        "Tahap 5: Menghitung harga jual",
        "Hitung harga jualnya.", 1,
        f"Harga jual = {rupiah(beli)} + {rupiah(untung)} = {rupiah(jual)}.",
        isian=[Isian("Harga jual", jual, "Rp")])

    def simpul(x):
        return f"{_kapital(barang)} harus dijual seharga {rupiah(x)} agar memperoleh keuntungan {p}%."
    t6 = _tahap_pilihan(
        rng, "Tahap 6: Menyimpulkan",
        "Pilih kesimpulan yang tepat.", 1, simpul(jual),
        simpul(jual), [simpul(beli - untung), simpul(beli + p), simpul(untung)])

    return Misi(2, "Menentukan Harga Jual dengan Persentase Keuntungan", soal,
                [t1, t2, t3, t4, t5, t6])


# ------------------- Soal 3: Employing Mathematical Concepts and Procedures --

def misi_prosedur(nama: str, barang_untung: tuple, barang_rugi: tuple,
                  rng: random.Random) -> Misi:
    """barang_untung / barang_rugi = (nama_barang, harga_beli, harga_jual)"""
    b1, beli1, jual1 = barang_untung
    b2, beli2, jual2 = barang_rugi
    u1, r2 = jual1 - beli1, beli2 - jual2
    p1, p2 = u1 * 100 / beli1, r2 * 100 / beli2
    soal = (f"{nama} membeli sebuah {b1} seharga {rupiah(beli1)}. {_kapital(b1)} tersebut "
            f"kemudian dijual seharga {rupiah(jual1)}. Pada kesempatan lain, ia membeli "
            f"sebuah {b2} seharga {rupiah(beli2)}, tetapi hanya terjual seharga "
            f"{rupiah(jual2)}. Hitunglah besar keuntungan atau kerugian serta persentasenya "
            f"untuk masing-masing barang. Tunjukkan langkah perhitunganmu.")

    def data(bl1, jl1, bl2, jl2):
        return (f"{_kapital(b1)}: harga beli {rupiah(bl1)}; harga jual {rupiah(jl1)}.\n"
                f"{_kapital(b2)}: harga beli {rupiah(bl2)}; harga jual {rupiah(jl2)}.")
    benar = data(beli1, jual1, beli2, jual2)
    t1 = _tahap_pilihan(
        rng, "Tahap 1: Mengidentifikasi harga beli dan harga jual kedua barang",
        "Pilih data yang benar untuk kedua barang.", 1, benar, benar,
        [data(jual1, beli1, jual2, beli2), data(beli1, jual1, jual2, beli2),
         data(jual1, beli1, beli2, jual2)])

    t2 = Tahap(f"Tahap 2: Menghitung keuntungan {b1}",
               f"Hitung keuntungan {b1}.", 1,
               f"{rupiah(jual1)} − {rupiah(beli1)} = {rupiah(u1)}.",
               isian=[Isian(f"Keuntungan {b1}", u1, "Rp")])
    t3 = Tahap(f"Tahap 3: Menghitung persentase keuntungan {b1}",
               "Gunakan rumus (keuntungan ÷ harga beli) × 100%.", 1,
               f"({angka(u1)} ÷ {angka(beli1)}) × 100% = {persen(p1)}.",
               isian=[Isian(f"Persentase keuntungan {b1}", p1, "%")])
    t4 = Tahap(f"Tahap 4: Menghitung kerugian {b2}",
               f"Hitung kerugian {b2}.", 1,
               f"{rupiah(beli2)} − {rupiah(jual2)} = {rupiah(r2)}.",
               isian=[Isian(f"Kerugian {b2}", r2, "Rp")])
    t5 = Tahap(f"Tahap 5: Menghitung persentase kerugian {b2}",
               "Gunakan rumus (kerugian ÷ harga beli) × 100%.", 1,
               f"({angka(r2)} ÷ {angka(beli2)}) × 100% = {persen(p2)}.",
               isian=[Isian(f"Persentase kerugian {b2}", p2, "%")])

    benar_s = (f"{_kapital(b1)} menghasilkan keuntungan {rupiah(u1)} ({persen(p1)}), "
               f"sedangkan {b2} mengalami kerugian {rupiah(r2)} ({persen(p2)}).")
    t6 = _tahap_pilihan(
        rng, "Tahap 6: Menyimpulkan", "Pilih kesimpulan yang tepat.", 1, benar_s, benar_s,
        [f"{_kapital(b1)} mengalami kerugian {rupiah(u1)} ({persen(p1)}), "
         f"sedangkan {b2} menghasilkan keuntungan {rupiah(r2)} ({persen(p2)}).",
         f"{_kapital(b1)} menghasilkan keuntungan {rupiah(u1)} ({persen(u1 * 100 / jual1)}), "
         f"sedangkan {b2} mengalami kerugian {rupiah(r2)} ({persen(r2 * 100 / jual2)}).",
         f"Kedua barang menghasilkan keuntungan, yaitu {rupiah(u1)} dan {rupiah(r2)}."])

    return Misi(3, "Menghitung Persentase Untung dan Rugi", soal, [t1, t2, t3, t4, t5, t6])


# ------------- Soal 4: Interpreting, Applying, and Evaluating the Outcomes --

def misi_evaluasi(nama: str, barang: str, beli: int, jual: int, rng: random.Random) -> Misi:
    rugi = beli - jual
    p = rugi * 100 / beli
    klaim = rugi * 100 / jual
    soal = (f"{nama} membeli sebuah {barang} seharga {rupiah(beli)}. Karena sedang "
            f"membutuhkan uang, {barang} tersebut dijual kembali seharga {rupiah(jual)}. "
            f"Teman {nama} menyatakan bahwa persentase kerugian yang dialami {nama} adalah "
            f"{persen(klaim)} karena kerugian {rupiah(rugi)} dibagi dengan harga jual "
            f"{rupiah(jual)}. Apakah pernyataan teman {nama} benar? Evaluasilah dengan "
            f"perhitungan matematika dan jelaskan alasanmu.")

    benar1 = f"Harga beli = {rupiah(beli)} dan harga jual = {rupiah(jual)}."
    t1 = _tahap_pilihan(
        rng, "Tahap 1: Mengidentifikasi harga beli dan harga jual",
        "Pilih informasi yang benar.", 1, benar1, benar1,
        [f"Harga beli = {rupiah(jual)} dan harga jual = {rupiah(beli)}.",
         f"Harga beli = {rupiah(jual)} dan kerugian = {rupiah(beli)}.",
         f"Harga jual = {rupiah(beli)} dan kerugian = {rupiah(rugi)}."])

    t2 = Tahap("Tahap 2: Menentukan besar kerugian",
               "Hitung besar kerugian (harga beli − harga jual).", 1,
               f"{rupiah(beli)} − {rupiah(jual)} = {rupiah(rugi)}.",
               isian=[Isian("Besar kerugian", rugi, "Rp")])

    t3 = _tahap_pilihan(
        rng, "Tahap 3: Menentukan rumus persentase kerugian",
        "Rumus mana yang benar?", 1,
        "Persentase kerugian = (kerugian ÷ harga beli) × 100%.",
        "Persentase kerugian = (kerugian ÷ harga beli) × 100%",
        ["Persentase kerugian = (kerugian ÷ harga jual) × 100%",
         "Persentase kerugian = (harga beli ÷ kerugian) × 100%",
         "Persentase kerugian = (harga jual ÷ harga beli) × 100%"])

    t4 = _tahap_pilihan(
        rng, "Tahap 4: Memasukkan nilai yang diketahui",
        "Substitusikan nilai ke dalam rumus.", 1,
        f"({angka(rugi)} ÷ {angka(beli)}) × 100%.",
        f"({angka(rugi)} ÷ {angka(beli)}) × 100%",
        [f"({angka(rugi)} ÷ {angka(jual)}) × 100%",
         f"({angka(beli)} ÷ {angka(rugi)}) × 100%",
         f"({angka(jual)} ÷ {angka(beli)}) × 100%"])

    t5 = Tahap("Tahap 5: Menghitung persentase kerugian",
               "Hitung persentase kerugiannya.", 1,
               f"= {desimal(rugi / beli, 4)} × 100% = {persen(p)}.",
               isian=[Isian("Persentase kerugian", p, "%")])

    benar6 = (f"Pernyataan teman {nama} tidak benar. Persentase kerugian dihitung berdasarkan "
              f"harga beli, sehingga kerugian {nama} adalah {persen(p)}, bukan {persen(klaim)}.")
    t6 = _tahap_pilihan(
        rng, "Tahap 6: Menyimpulkan", "Apakah pernyataan teman tersebut benar?", 1,
        benar6, benar6,
        [f"Pernyataan teman {nama} benar, karena kerugian harus dibagi harga jual "
         f"sehingga hasilnya {persen(klaim)}.",
         f"Pernyataan teman {nama} tidak benar, seharusnya persentase kerugiannya "
         f"{persen(jual * 100 / beli)}.",
         f"Pernyataan teman {nama} benar, karena harga jual adalah uang yang "
         f"benar-benar diterima {nama}."])

    return Misi(4, "Mengevaluasi Pernyataan tentang Persentase Kerugian", soal,
                [t1, t2, t3, t4, t5, t6])


# ---------------------------------------------------------- kumpulan soal --

def misi_kisi_kisi(rng: random.Random | None = None) -> list:
    """Empat soal persis seperti pada dokumen kisi-kisi."""
    rng = rng or random.Random()
    return [
        misi_penalaran("tas", [("A", 120000, 150000), ("B", 140000, 175000),
                               ("C", 160000, 192000)], rng),
        misi_formulasi("Ibu", "blender", 250000, 20, rng),
        misi_prosedur("Pak Rudi", ("sepeda", 800000, 920000),
                      ("kipas angin", 500000, 425000), rng),
        misi_evaluasi("Dina", "jaket", 400000, 340000, rng),
    ]


NAMA = ["Pak Budi", "Bu Sari", "Kak Rina", "Pak Joko", "Andi", "Putri", "Bayu", "Dewi"]
BARANG = ["tas", "sepatu", "jaket", "helm", "jam tangan", "kemeja batik", "topi", "payung"]
BARANG_RUMAH = ["blender", "rice cooker", "kipas angin", "setrika", "dispenser",
                "kompor gas", "sepeda", "lemari kecil", "televisi", "gitar"]
PERSEN = [10, 15, 20, 25, 30, 40]


def _penalaran_acak(rng):
    barang = rng.choice(BARANG)
    while True:
        if rng.random() < 0.5:  # ada dua toko dengan persentase sama
            a, b = sorted(rng.sample(PERSEN, 2))
            ps = [b, b, a]
        else:
            ps = rng.sample(PERSEN, 3)
        rng.shuffle(ps)
        belis = [x * 10000 for x in rng.sample(range(8, 31), 3)]
        toko = [(n, b, b + b * p // 100) for n, b, p in zip("ABC", belis, ps)]
        untung = [j - b for _, b, j in toko]
        if untung.count(max(untung)) > 1:
            continue
        n_rp = toko[untung.index(max(untung))][0]
        terbesar = [t[0] for t, p in zip(toko, ps) if p == max(ps)]
        if terbesar != [n_rp]:  # supaya untung-rupiah-terbesar menjadi pengecoh
            return misi_penalaran(barang, toko, rng)


def _formulasi_acak(rng):
    return misi_formulasi(rng.choice(NAMA), rng.choice(BARANG_RUMAH),
                          rng.randrange(2, 21) * 50000, rng.choice(PERSEN), rng)


def _prosedur_acak(rng):
    b1, b2 = rng.sample(BARANG_RUMAH, 2)
    beli1 = rng.randrange(3, 16) * 100000
    beli2 = rng.randrange(2, 11) * 100000
    p1, p2 = rng.choice([5, 10, 15, 20, 25]), rng.choice([5, 10, 15, 20, 25])
    return misi_prosedur(rng.choice(NAMA), (b1, beli1, beli1 + beli1 * p1 // 100),
                         (b2, beli2, beli2 - beli2 * p2 // 100), rng)


def _evaluasi_acak(rng):
    beli = rng.randrange(2, 11) * 100000
    p = rng.choice([5, 10, 15, 20, 25, 30])
    nama = rng.choice(["Dina", "Raka", "Salsa", "Fajar", "Nisa", "Bima"])
    return misi_evaluasi(nama, rng.choice(BARANG), beli, beli - beli * p // 100, rng)


def misi_acak(rng: random.Random | None = None) -> list:
    """Empat soal baru dengan struktur & indikator yang sama, angka acak."""
    rng = rng or random.Random()
    return [_penalaran_acak(rng), _formulasi_acak(rng), _prosedur_acak(rng), _evaluasi_acak(rng)]
