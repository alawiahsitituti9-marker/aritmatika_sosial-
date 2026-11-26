"""Logika permainan (terpisah dari tampilan agar mudah diuji)."""

import random
from dataclasses import dataclass

from soal import Misi, Tahap, misi_acak, misi_kisi_kisi

MODE = {
    "kisi": "Soal Kisi-kisi",
    "acak": "Latihan Soal Acak",
}


@dataclass
class Hasil:
    per_butir: list  # benar/salah tiap butir isian/pilihan
    skor: int

    @property
    def benar(self) -> bool:
        return all(self.per_butir)


def predikat(nilai: float) -> str:
    if nilai >= 90:
        return "A — Sangat Baik"
    if nilai >= 75:
        return "B — Baik"
    if nilai >= 60:
        return "C — Cukup"
    return "D — Perlu Bimbingan"


def bintang(skor: int, maks: int) -> int:
    if maks == 0:
        return 0
    r = skor / maks
    return 3 if r == 1 else 2 if r >= 2 / 3 else 1 if r >= 1 / 3 else 0


class Permainan:
    def __init__(self, mode: str = "kisi", rng: random.Random | None = None):
        if mode not in MODE:
            raise ValueError(f"Mode tidak dikenal: {mode}")
        self.mode = mode
        self.misi: list[Misi] = misi_kisi_kisi(rng) if mode == "kisi" else misi_acak(rng)
        self.i_misi = 0
        self.i_tahap = 0
        # skor tiap tahap; None = belum dijawab
        self.skor_tahap = [[None] * len(m.tahapan) for m in self.misi]

    # ---------------------------------------------------------------- posisi
    @property
    def selesai(self) -> bool:
        return self.i_misi >= len(self.misi)

    @property
    def misi_sekarang(self) -> Misi:
        return self.misi[self.i_misi]

    @property
    def tahap_sekarang(self) -> Tahap:
        return self.misi_sekarang.tahapan[self.i_tahap]

    @property
    def tahap_terakhir(self) -> bool:
        return self.i_tahap == len(self.misi_sekarang.tahapan) - 1

    @property
    def misi_terakhir(self) -> bool:
        return self.i_misi == len(self.misi) - 1

    # ---------------------------------------------------------------- aksi
    def jawab(self, jawaban) -> Hasil:
        if self.skor_tahap[self.i_misi][self.i_tahap] is not None:
            raise RuntimeError("Tahap ini sudah dijawab")
        t = self.tahap_sekarang
        per_butir = t.periksa(jawaban)
        skor = t.skor if all(per_butir) else 0
        self.skor_tahap[self.i_misi][self.i_tahap] = skor
        return Hasil(per_butir, skor)

    def maju(self):
        self.i_tahap += 1
        if self.i_tahap >= len(self.misi_sekarang.tahapan):
            self.i_misi += 1
            self.i_tahap = 0

    # ---------------------------------------------------------------- skor
    def skor_misi(self, i: int) -> int:
        return sum(s or 0 for s in self.skor_tahap[i])

    @property
    def skor(self) -> int:
        return sum(self.skor_misi(i) for i in range(len(self.misi)))

    @property
    def skor_maks(self) -> int:
        return sum(m.skor_maks for m in self.misi)

    @property
    def nilai(self) -> int:
        return round(self.skor * 100 / self.skor_maks)
