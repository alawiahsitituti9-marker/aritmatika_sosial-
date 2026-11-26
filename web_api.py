"""Jembatan antara tampilan web (index.html) dan logika game Python.

Versi web menjalankan file Python yang sama (soal.py, permainan.py, materi.py)
langsung di browser menggunakan Pyodide. Semua fungsi di sini mengembalikan
teks JSON agar mudah dibaca oleh JavaScript.
"""

import json

from materi import MATERI
from permainan import MODE, Permainan, bintang, predikat
from soal import parse_angka

_game: Permainan | None = None


def mulai(mode: str) -> str:
    global _game
    _game = Permainan(mode)
    return status()


def status() -> str:
    p = _game
    if p.selesai:
        return json.dumps({
            "selesai": True,
            "mode": MODE[p.mode],
            "skor": p.skor,
            "maks": p.skor_maks,
            "nilai": p.nilai,
            "predikat": predikat(p.nilai),
            "misi": [{
                "nomor": m.nomor,
                "indikator": m.indikator,
                "judul": m.judul,
                "skor": p.skor_misi(i),
                "maks": m.skor_maks,
                "bintang": bintang(p.skor_misi(i), m.skor_maks),
            } for i, m in enumerate(p.misi)],
        })
    m, t = p.misi_sekarang, p.tahap_sekarang
    return json.dumps({
        "selesai": False,
        "mode": MODE[p.mode],
        "skor": p.skor,
        "maks": p.skor_maks,
        "i_misi": p.i_misi,
        "jumlah_misi": len(p.misi),
        "i_tahap": p.i_tahap,
        "tahap_terakhir": p.tahap_terakhir,
        "misi_terakhir": p.misi_terakhir,
        "misi": {
            "nomor": m.nomor,
            "indikator": m.indikator,
            "deskripsi": m.deskripsi_indikator,
            "judul": m.judul,
            "soal": m.soal,
            "tahapan": [{"judul": x.judul, "skor": x.skor,
                         "hasil": p.skor_tahap[p.i_misi][i]}
                        for i, x in enumerate(m.tahapan)],
        },
        "tahap": {
            "judul": t.judul,
            "perintah": t.perintah,
            "skor": t.skor,
            "jenis": t.jenis,
            "pilihan": t.pilihan,
            "isian": [{"label": s.label, "satuan": s.satuan} for s in t.isian],
        },
    })


def jawab(jawaban_json: str) -> str:
    jawaban = json.loads(jawaban_json)
    t = _game.tahap_sekarang
    if t.jenis == "isian":
        if any(parse_angka(x) is None for x in jawaban):
            return json.dumps({"error": "Isi semua kotak dengan angka terlebih dahulu."})
    elif not isinstance(jawaban, int) or jawaban < 0:
        return json.dumps({"error": "Pilih salah satu jawaban terlebih dahulu."})
    h = _game.jawab(jawaban)
    return json.dumps({
        "benar": h.benar,
        "skor": h.skor,
        "per_butir": h.per_butir,
        "kunci_pilihan": t.kunci_pilihan,
        "kunci_isian": [s.kunci() for s in t.isian],
        "penjelasan": t.penjelasan,
        "status": json.loads(status()),
    })


def maju() -> str:
    _game.maju()
    return status()


def materi() -> str:
    return json.dumps([{"judul": j, "isi": i} for j, i in MATERI])
