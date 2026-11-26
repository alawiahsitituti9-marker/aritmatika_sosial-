"""Logika permainan (terpisah dari tampilan agar mudah diuji)."""

import random
from dataclasses import dataclass

from soal import Soal, buat_soal, parse_jawaban

WAKTU_PER_SOAL = 60  # detik
NAMA_LEVEL = {
    1: "Pedagang Pemula",
    2: "Pedagang Terampil",
    3: "Juragan Pasar",
}
DESKRIPSI_LEVEL = {
    1: "Untung & rugi, diskon, bruto-tara-neto",
    2: "Persentase untung/rugi, harga jual, PPN, persentase tara",
    3: "Harga beli, diskon bertingkat, bunga tunggal tabungan",
}


@dataclass
class Hasil:
    benar: bool
    poin: int
    jawaban_siswa: int | None


class Permainan:
    def __init__(self, level: int, jumlah_soal: int = 10, nyawa: int = 3,
                 rng: random.Random | None = None):
        if level not in NAMA_LEVEL:
            raise ValueError(f"Level tidak dikenal: {level}")
        self.level = level
        self.jumlah_soal = jumlah_soal
        self.nyawa = nyawa
        self.rng = rng or random.Random()
        self.nomor = 0
        self.skor = 0
        self.jumlah_benar = 0
        self.beruntun = 0
        self.soal: Soal | None = None

    def soal_berikutnya(self) -> Soal:
        self.nomor += 1
        self.soal = buat_soal(self.level, self.rng)
        return self.soal

    def jawab(self, teks: str | None, sisa_waktu: int = 0) -> Hasil:
        """Periksa jawaban. teks=None berarti waktu habis."""
        nilai = parse_jawaban(teks)
        if nilai is not None and nilai == self.soal.jawaban:
            self.beruntun += 1
            self.jumlah_benar += 1
            poin = 10 * self.level + max(sisa_waktu, 0) // 6 + 2 * min(self.beruntun - 1, 5)
            self.skor += poin
            return Hasil(True, poin, nilai)
        self.beruntun = 0
        self.nyawa -= 1
        return Hasil(False, 0, nilai)

    @property
    def selesai(self) -> bool:
        return self.nyawa <= 0 or self.nomor >= self.jumlah_soal
