"""Penyimpanan papan skor tertinggi ke file JSON lokal."""

import json
from datetime import date
from pathlib import Path

FILE_SKOR = Path(__file__).with_name("skor_tertinggi.json")
MAKS_ENTRI = 10


def muat_skor(path: Path = FILE_SKOR) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def tambah_skor(nama: str, nilai: int, skor: int, mode: str,
                path: Path = FILE_SKOR) -> int | None:
    """Simpan hasil; kembalikan peringkat (1-based) jika masuk papan skor."""
    entri = {"nama": nama, "nilai": nilai, "skor": skor, "mode": mode,
             "tanggal": date.today().isoformat()}
    daftar = muat_skor(path) + [entri]
    daftar.sort(key=lambda e: (e.get("nilai", 0), e.get("skor", 0)), reverse=True)
    daftar = daftar[:MAKS_ENTRI]
    try:
        path.write_text(json.dumps(daftar, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    for i, e in enumerate(daftar):
        if e is entri:
            return i + 1
    return None
