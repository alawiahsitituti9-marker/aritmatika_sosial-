"""Jembatan antara tampilan web (index.html) dan logika game Python.

Versi web menjalankan file Python yang sama (soal.py, permainan.py, materi.py)
langsung di browser menggunakan Pyodide. Semua fungsi di sini mengembalikan
teks JSON agar mudah dibaca oleh JavaScript.
"""

import json

import ai_tutor
import rmt
from materi import MATERI
from permainan import MODE, Permainan, bintang, predikat
from soal import parse_angka

_game: Permainan | None = None
_terakhir = {"jawaban": "", "benar": False}  # jawaban terakhir siswa, untuk penjelasan AI


def mulai(mode: str) -> str:
    global _game
    _game = Permainan(mode)
    return status()


def status() -> str:
    p = _game
    if p.selesai:
        profil = rmt.profil_fase(p)
        lemah = rmt.fase_terlemah(profil)
        return json.dumps({
            "selesai": True,
            "mode": MODE[p.mode],
            "skor": p.skor,
            "maks": p.skor_maks,
            "nilai": p.nilai,
            "predikat": predikat(p.nilai),
            "profil": [{"fase": rmt.FASE[f], "dapat": d, "maks": mk} for f, (d, mk) in profil.items()],
            "skor_mediasi": p.skor_setelah_mediasi,
            "jumlah_mediasi": p.jumlah_mediasi,
            "fase_lemah": rmt.FASE[lemah] if lemah else None,
            "rekomendasi": rmt.REKOMENDASI_FASE[lemah] if lemah else None,
            "refleksi": [dict(rmt.REFLEKSI_FASE)[r["fase"]].split(" —")[0] if r else None
                         for r in p.refleksi],
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
    info = rmt.info_tahap(m.nomor, p.i_tahap)
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
        "boleh_ulang": p.boleh_ulang,
        "skor_misi": p.skor_misi(p.i_misi),
        "rmt_misi": rmt.info_misi(m.nomor),
        "langkah_la": [n for n, _ in rmt.LANGKAH_LA],
        "rmt_tahap": {**info, "fase_label": rmt.FASE[info["fase"]]},
        "opsi_refleksi_fase": rmt.REFLEKSI_FASE,
        "opsi_refleksi_strategi": rmt.REFLEKSI_STRATEGI,
        "misi": {
            "nomor": m.nomor,
            "indikator": m.indikator,
            "deskripsi": m.deskripsi_indikator,
            "judul": m.judul,
            "soal": m.soal,
            "tahapan": [{"judul": x.judul, "skor": x.skor,
                         "hasil": p.skor_tahap[p.i_misi][i],
                         "ulang": p.skor_ulang[p.i_misi][i],
                         "fase": rmt.info_tahap(m.nomor, i)["fase"]}
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


def jawab(jawaban_json: str, ulang: bool = False) -> str:
    """Periksa jawaban. ulang=True berarti uji ulang setelah mediasi (asesmen dinamis)."""
    jawaban = json.loads(jawaban_json)
    t = _game.tahap_sekarang
    if t.jenis == "isian":
        if any(parse_angka(x) is None for x in jawaban):
            return json.dumps({"error": "Isi semua kotak dengan angka terlebih dahulu."})
    elif not isinstance(jawaban, int) or jawaban < 0:
        return json.dumps({"error": "Pilih salah satu jawaban terlebih dahulu."})
    h = _game.jawab_ulang(jawaban) if ulang else _game.jawab(jawaban)
    _terakhir.update(jawaban=ai_tutor.teks_jawaban(t, jawaban), benar=h.benar)
    return json.dumps({
        "benar": h.benar,
        "skor": h.skor,
        "per_butir": h.per_butir,
        "kunci_pilihan": t.kunci_pilihan,
        "kunci_isian": [s.kunci() for s in t.isian],
        "penjelasan": t.penjelasan,
        "status": json.loads(status()),
    })


def simpan_refleksi(fase: str, strategi: str) -> str:
    _game.simpan_refleksi(fase, strategi)
    return status()


def maju() -> str:
    _game.maju()
    return status()


def materi() -> str:
    return json.dumps([{"judul": j, "isi": i} for j, i in MATERI])


# ------------------------------------------------------------------ tutor AI
# API key tidak pernah masuk ke Python: JavaScript yang menambahkan header
# Authorization dari key yang disimpan di browser siswa.

def permintaan_ai(jenis: str, sementara_json: str, penyedia: str, model: str) -> str:
    """Susun permintaan ke AI. jenis = 'petunjuk' (sebelum menjawab) atau 'penjelasan'."""
    m, t = _game.misi_sekarang, _game.tahap_sekarang
    if jenis == "refleksi":
        r = json.loads(sementara_json)
        pesan = ai_tutor.pesan_refleksi(m, dict(rmt.REFLEKSI_FASE).get(r.get("fase"), "-"),
                                        r.get("strategi", "-"))
    elif jenis == "penjelasan":
        pesan = ai_tutor.pesan_penjelasan(m, t, _terakhir["jawaban"], _terakhir["benar"])
    else:
        sementara = ai_tutor.teks_jawaban(t, json.loads(sementara_json))
        pesan = ai_tutor.pesan_petunjuk(m, t, sementara)
    return _permintaan(penyedia, model, pesan)


def permintaan_tes(penyedia: str, model: str) -> str:
    pesan = [{"role": "user", "content": "Jawab singkat: 20% dari Rp50.000 berapa?"}]
    return _permintaan(penyedia, model, pesan, maks_token=60)


def _permintaan(penyedia, model, pesan, maks_token=400) -> str:
    url, headers, body = ai_tutor.buat_permintaan(
        {"penyedia": penyedia, "api_key": "", "model": model}, pesan, maks_token)
    headers.pop("Authorization", None)
    return json.dumps({"url": url, "headers": headers, "body": body})


def ambil_teks_ai(data_json: str) -> str:
    try:
        return json.dumps({"teks": ai_tutor.ambil_teks(json.loads(data_json))})
    except (ai_tutor.AIError, ValueError) as e:
        return json.dumps({"error": str(e) or "Respons AI tidak dapat dibaca."})


def galat_http(kode: int, isi: str = "") -> str:
    return ai_tutor.pesan_galat_http(int(kode), isi or "")


def daftar_penyedia() -> str:
    return json.dumps({k: {"nama": v["nama"], "model": v["model"]}
                       for k, v in ai_tutor.PENYEDIA.items()})

def bersihkan_key(key: str) -> str:
    return ai_tutor.bersihkan_key(key)


def cek_format_key(key: str) -> str:
    return ai_tutor.cek_format_key(key) or ""
