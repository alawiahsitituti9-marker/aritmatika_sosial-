"""Generator soal Aritmatika Sosial.

Setiap soal dibuat secara acak, tetapi angkanya dipilih sedemikian rupa
sehingga jawabannya selalu bilangan bulat (mudah dihitung siswa).
"""

import random
import re
from dataclasses import dataclass


@dataclass
class Soal:
    topik: str
    pertanyaan: str
    jawaban: int
    satuan: str  # "Rp", "%", "kg", atau "bulan"
    pembahasan: str


NAMA = ["Budi", "Siti", "Andi", "Rina", "Dewi", "Joko", "Putri", "Rudi", "Ayu", "Bayu"]
BARANG = ["sepeda", "tas sekolah", "sepatu", "jam tangan", "kipas angin",
          "rice cooker", "lemari kecil", "gitar", "helm", "ponsel bekas"]
KARUNG = ["beras", "gula", "tepung terigu", "jagung", "kacang tanah", "kopi"]


def rupiah(n: int) -> str:
    """Format angka menjadi rupiah, contoh: 15000 -> 'Rp15.000'."""
    return "Rp" + f"{n:,}".replace(",", ".")


def format_jawaban(n: int, satuan: str) -> str:
    if satuan == "Rp":
        return rupiah(n)
    if satuan == "%":
        return f"{n}%"
    return f"{n} {satuan}"


def parse_jawaban(teks: str):
    """Ubah teks jawaban siswa menjadi int. Kembalikan None jika tidak valid.

    Menerima variasi seperti '15000', '15.000', 'Rp 15.000', '25%', '40 kg', '15.000,00'.
    """
    if teks is None:
        return None
    t = teks.strip().lower()
    for kata in ("rp", "%", "kg", "bulan", " "):
        t = t.replace(kata, "")
    t = t.replace(".", "")
    t = re.sub(r",0+$", "", t)  # buang desimal nol di belakang koma
    if not re.fullmatch(r"\d+", t, flags=re.ASCII):
        return None
    return int(t)


# ---------------------------------------------------------------- Level 1 ---

def soal_untung_rugi(rng: random.Random) -> Soal:
    nama, barang = rng.choice(NAMA), rng.choice(BARANG)
    beli = rng.randrange(20, 200) * 1000
    selisih = rng.randrange(1, 30) * 500
    untung = rng.random() < 0.5
    jual = beli + selisih if untung else beli - selisih
    jenis = "untung" if untung else "rugi"
    rumus = (f"Untung = Harga jual − Harga beli = {rupiah(jual)} − {rupiah(beli)}"
             if untung else
             f"Rugi = Harga beli − Harga jual = {rupiah(beli)} − {rupiah(jual)}")
    return Soal(
        topik="Untung dan Rugi",
        pertanyaan=(f"{nama} membeli {barang} seharga {rupiah(beli)}, lalu menjualnya "
                    f"seharga {rupiah(jual)}.\nBerapa besar {jenis} yang diperoleh {nama}?"),
        jawaban=selisih,
        satuan="Rp",
        pembahasan=(f"Harga jual {'lebih besar' if untung else 'lebih kecil'} dari harga beli, "
                    f"jadi {nama} {jenis}.\n{rumus} = {rupiah(selisih)}"),
    )


def soal_diskon(rng: random.Random) -> Soal:
    barang = rng.choice(BARANG)
    harga = rng.randrange(5, 101) * 5000
    d = rng.choice([5, 10, 15, 20, 25, 30, 40, 50])
    potongan = harga * d // 100
    bayar = harga - potongan
    return Soal(
        topik="Diskon",
        pertanyaan=(f"Sebuah {barang} dijual dengan harga {rupiah(harga)}. Toko memberi "
                    f"diskon {d}%.\nBerapa harga yang harus dibayar?"),
        jawaban=bayar,
        satuan="Rp",
        pembahasan=(f"Potongan = {d}% × {rupiah(harga)} = {rupiah(potongan)}\n"
                    f"Harga bayar = {rupiah(harga)} − {rupiah(potongan)} = {rupiah(bayar)}"),
    )


def soal_bruto_neto(rng: random.Random) -> Soal:
    isi = rng.choice(KARUNG)
    bruto = rng.randrange(20, 101)
    tara = rng.randrange(1, 6)
    neto = bruto - tara
    return Soal(
        topik="Bruto, Tara, Neto",
        pertanyaan=(f"Sebuah karung {isi} memiliki bruto {bruto} kg dan tara {tara} kg.\n"
                    f"Berapa neto (berat bersih) {isi} tersebut?"),
        jawaban=neto,
        satuan="kg",
        pembahasan=f"Neto = Bruto − Tara = {bruto} kg − {tara} kg = {neto} kg",
    )


# ---------------------------------------------------------------- Level 2 ---

def _beli_dan_persen(rng: random.Random):
    beli = rng.randrange(2, 41) * 5000
    p = rng.choice([5, 10, 12, 15, 20, 25, 30, 40])
    untung = rng.random() < 0.6
    besar = beli * p // 100
    jual = beli + besar if untung else beli - besar
    return beli, p, untung, besar, jual


def soal_persen_untung(rng: random.Random) -> Soal:
    nama, barang = rng.choice(NAMA), rng.choice(BARANG)
    beli, p, untung, besar, jual = _beli_dan_persen(rng)
    jenis = "untung" if untung else "rugi"
    return Soal(
        topik=f"Persentase {jenis.capitalize()}",
        pertanyaan=(f"{nama} membeli {barang} seharga {rupiah(beli)} dan menjualnya "
                    f"seharga {rupiah(jual)}.\nBerapa persen {jenis} yang dialami {nama}?"),
        jawaban=p,
        satuan="%",
        pembahasan=(f"Besar {jenis} = {rupiah(besar)}\n"
                    f"% {jenis} = ({rupiah(besar)} ÷ {rupiah(beli)}) × 100% = {p}%"),
    )


def soal_harga_jual(rng: random.Random) -> Soal:
    nama, barang = rng.choice(NAMA), rng.choice(BARANG)
    beli, p, untung, besar, jual = _beli_dan_persen(rng)
    jenis = "untung" if untung else "rugi"
    tanda = "+" if untung else "−"
    return Soal(
        topik="Menentukan Harga Jual",
        pertanyaan=(f"{nama} membeli {barang} seharga {rupiah(beli)}. Ia menjualnya dan "
                    f"mengalami {jenis} {p}%.\nBerapa harga jual {barang} tersebut?"),
        jawaban=jual,
        satuan="Rp",
        pembahasan=(f"Besar {jenis} = {p}% × {rupiah(beli)} = {rupiah(besar)}\n"
                    f"Harga jual = {rupiah(beli)} {tanda} {rupiah(besar)} = {rupiah(jual)}"),
    )


def soal_ppn(rng: random.Random) -> Soal:
    barang = rng.choice(BARANG)
    harga = rng.randrange(1, 100) * 10000
    pajak = harga * 11 // 100
    total = harga + pajak
    return Soal(
        topik="Pajak (PPN 11%)",
        pertanyaan=(f"Harga sebuah {barang} sebelum pajak adalah {rupiah(harga)}. "
                    f"Pembeli dikenakan PPN 11%.\nBerapa total yang harus dibayar?"),
        jawaban=total,
        satuan="Rp",
        pembahasan=(f"PPN = 11% × {rupiah(harga)} = {rupiah(pajak)}\n"
                    f"Total bayar = {rupiah(harga)} + {rupiah(pajak)} = {rupiah(total)}"),
    )


def soal_tara_persen(rng: random.Random) -> Soal:
    isi = rng.choice(KARUNG)
    bruto = rng.randrange(1, 11) * 100
    t = rng.choice([1, 2, 3, 4, 5, 10])
    tara = bruto * t // 100
    neto = bruto - tara
    return Soal(
        topik="Persentase Tara",
        pertanyaan=(f"Sebuah truk mengangkut {isi} dengan bruto {bruto} kg. "
                    f"Taranya {t}% dari bruto.\nBerapa neto {isi} tersebut?"),
        jawaban=neto,
        satuan="kg",
        pembahasan=(f"Tara = {t}% × {bruto} kg = {tara} kg\n"
                    f"Neto = {bruto} kg − {tara} kg = {neto} kg"),
    )


# ---------------------------------------------------------------- Level 3 ---

def soal_harga_beli(rng: random.Random) -> Soal:
    nama, barang = rng.choice(NAMA), rng.choice(BARANG)
    beli, p, untung, besar, jual = _beli_dan_persen(rng)
    jenis = "untung" if untung else "rugi"
    persen_jual = 100 + p if untung else 100 - p
    return Soal(
        topik="Menentukan Harga Beli",
        pertanyaan=(f"{nama} menjual {barang} seharga {rupiah(jual)} dan mengalami "
                    f"{jenis} {p}%.\nBerapa harga beli {barang} tersebut?"),
        jawaban=beli,
        satuan="Rp",
        pembahasan=(f"Harga jual = (100% {'+' if untung else '−'} {p}%) × harga beli "
                    f"= {persen_jual}% × harga beli\n"
                    f"Harga beli = (100 ÷ {persen_jual}) × {rupiah(jual)} = {rupiah(beli)}"),
    )


def soal_diskon_ganda(rng: random.Random) -> Soal:
    barang = rng.choice(BARANG)
    harga = rng.randrange(2, 31) * 50000
    d1 = rng.choice([10, 20, 25, 30, 40, 50])
    d2 = rng.choice([5, 10, 20])
    h1 = harga * (100 - d1) // 100
    h2 = h1 * (100 - d2) // 100
    return Soal(
        topik="Diskon Bertingkat",
        pertanyaan=(f"Sebuah {barang} seharga {rupiah(harga)} mendapat diskon {d1}% + {d2}%.\n"
                    f"(Diskon kedua dihitung dari harga setelah diskon pertama.)\n"
                    f"Berapa harga yang harus dibayar?"),
        jawaban=h2,
        satuan="Rp",
        pembahasan=(f"Setelah diskon {d1}%: {100 - d1}% × {rupiah(harga)} = {rupiah(h1)}\n"
                    f"Setelah diskon {d2}%: {100 - d2}% × {rupiah(h1)} = {rupiah(h2)}\n"
                    f"Ingat: diskon {d1}% + {d2}% BUKAN berarti diskon {d1 + d2}%!"),
    )


def _tabungan(rng: random.Random):
    modal = rng.randrange(1, 21) * 600000
    b = rng.choice([3, 4, 5, 6, 8, 10, 12])
    n = rng.choice([3, 4, 6, 8, 9, 12, 18, 24])
    bunga = modal * b * n // 1200
    return modal, b, n, bunga


def soal_bunga_tunggal(rng: random.Random) -> Soal:
    nama = rng.choice(NAMA)
    modal, b, n, bunga = _tabungan(rng)
    akhir = modal + bunga
    return Soal(
        topik="Bunga Tunggal",
        pertanyaan=(f"{nama} menabung {rupiah(modal)} di bank dengan bunga tunggal {b}% per tahun.\n"
                    f"Berapa jumlah tabungan {nama} setelah {n} bulan?"),
        jawaban=akhir,
        satuan="Rp",
        pembahasan=(f"Bunga = (n/12) × b% × M = ({n}/12) × {b}% × {rupiah(modal)} = {rupiah(bunga)}\n"
                    f"Tabungan akhir = {rupiah(modal)} + {rupiah(bunga)} = {rupiah(akhir)}"),
    )


def soal_lama_menabung(rng: random.Random) -> Soal:
    nama = rng.choice(NAMA)
    modal, b, n, bunga = _tabungan(rng)
    akhir = modal + bunga
    bunga_setahun = modal * b // 100
    return Soal(
        topik="Lama Menabung",
        pertanyaan=(f"{nama} menabung {rupiah(modal)} dengan bunga tunggal {b}% per tahun. "
                    f"Kini tabungannya menjadi {rupiah(akhir)}.\n"
                    f"Sudah berapa bulan {nama} menabung?"),
        jawaban=n,
        satuan="bulan",
        pembahasan=(f"Bunga yang diperoleh = {rupiah(akhir)} − {rupiah(modal)} = {rupiah(bunga)}\n"
                    f"Bunga setahun = {b}% × {rupiah(modal)} = {rupiah(bunga_setahun)}\n"
                    f"n = ({rupiah(bunga)} ÷ {rupiah(bunga_setahun)}) × 12 = {n} bulan"),
    )


GENERATOR_PER_LEVEL = {
    1: [soal_untung_rugi, soal_diskon, soal_bruto_neto],
    2: [soal_persen_untung, soal_harga_jual, soal_ppn, soal_tara_persen],
    3: [soal_harga_beli, soal_diskon_ganda, soal_bunga_tunggal, soal_lama_menabung],
}


def buat_soal(level: int, rng: random.Random | None = None) -> Soal:
    rng = rng or random.Random()
    return rng.choice(GENERATOR_PER_LEVEL[level])(rng)
