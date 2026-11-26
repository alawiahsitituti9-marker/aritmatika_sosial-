"""Tutor AI UntungCerdas (Google Gemini).

Menghubungkan aplikasi ke model AI Google Gemini agar aplikasi bisa berperan
sebagai MEDIATOR RMT:
  • memberi pertanyaan terpimpin (mediasi) tanpa membocorkan jawaban,
  • mendiagnosis fase kognitif yang menyulitkan siswa, dan
  • menanggapi refleksi metakognisi siswa.

Aplikasi memakai endpoint Gemini yang kompatibel dengan format OpenAI:
  https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
API key Gemini GRATIS dibuat di Google AI Studio: https://aistudio.google.com/apikey

API key TIDAK disimpan di kode. Key dibaca dari file config_ai.json
(sudah masuk .gitignore sehingga tidak ikut terunggah ke GitHub) atau dari
variabel lingkungan GEMINI_API_KEY.
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import rmt

FILE_CONFIG = Path(__file__).with_name("config_ai.json")

PENYEDIA = {
    "gemini": {
        "nama": "Google Gemini (aistudio.google.com)",
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-flash-latest",
        # dipakai otomatis jika model utama sibuk (503) atau kuotanya habis (429)
        "cadangan": "gemini-flash-lite-latest",
        "env": "GEMINI_API_KEY",
    },
}
PENYEDIA_BAWAAN = "gemini"

# Kode HTTP "server sibuk/sementara" yang layak dicoba ulang otomatis.
KODE_COBA_ULANG = (500, 502, 503, 504)
JUMLAH_COBA_ULANG = 2      # percobaan ulang per model
JEDA_COBA_ULANG = 2.0      # detik (dikalikan nomor percobaan)

SISTEM = """Kamu adalah "Tutor UntungCerdas", MEDIATOR kognitif untuk siswa SMP kelas VII yang
belajar persentase untung dan rugi dengan model Rigorous Mathematical Thinking (RMT, Kinard & Kozulin).

Prinsip RMT yang wajib kamu terapkan:
- Mediated Learning Experience (Feuerstein):
  • Intensionalitas & resiprositas: arahkan perhatian siswa pada tujuan tahap ini dan ajak ia merespons.
  • Makna: jelaskan mengapa langkah ini penting.
  • Transendensi: kaitkan dengan prinsip umum yang berlaku di luar soal ini.
- Gunakan pertanyaan terpimpin (mediated questioning), bukan langsung memberi jawaban.
- Fungsi kognitif dibagi tiga fase: INPUT (mengumpulkan informasi dengan teliti),
  ELABORASI (mengolah: rumus, hubungan bagian-keseluruhan, membandingkan),
  OUTPUT (menyimpulkan dan mengomunikasikan dengan tepat, tanpa coba-coba).
- Dorong penggunaan alat psikologis matematika: tabel, rumus/persamaan, simbol %, garis bilangan,
  skema bagian-keseluruhan (harga jual = harga beli + untung), dan bahasa matematika yang tepat.
- Jembatani konsep sehari-hari ("untung banyak") ke konsep ilmiah (persentase terhadap harga beli).
- Dorong metakognisi: ajak siswa memeriksa dan merefleksikan strateginya sendiri.

Aturan penulisan:
- Bahasa Indonesia yang sederhana, ramah, dan singkat.
- Persentase untung/rugi SELALU dihitung terhadap harga beli.
- Tulis uang dengan format Rp (contoh Rp150.000) dan persen dengan koma desimal (17,65%).
- Jangan memakai LaTeX, markdown tebal, atau tabel; gunakan teks biasa."""


class AIError(Exception):
    """Kesalahan saat menghubungi AI, dengan pesan yang ramah untuk siswa."""


# ------------------------------------------------------------- konfigurasi --

def muat_config(path: Path = FILE_CONFIG) -> dict:
    cfg = {"penyedia": PENYEDIA_BAWAAN, "api_key": "", "model": ""}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            cfg.update({k: str(v) for k, v in data.items() if k in cfg})
    except (OSError, ValueError):
        pass
    if cfg["penyedia"] not in PENYEDIA:  # mis. konfigurasi lama (DeepSeek)
        cfg["penyedia"] = PENYEDIA_BAWAAN
    if not cfg["api_key"]:
        cfg["api_key"] = os.environ.get(PENYEDIA[cfg["penyedia"]]["env"], "")
    return cfg


def simpan_config(cfg: dict, path: Path = FILE_CONFIG) -> None:
    data = {k: cfg.get(k, "") for k in ("penyedia", "api_key", "model")}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def bersihkan_key(key: str) -> str:
    """Rapikan key hasil salin: buang spasi, enter, tanda kutip, dan awalan seperti 'Bearer '."""
    k = (key or "").strip().strip("\"'").strip()
    for awalan in ("Bearer ", "bearer ", "GEMINI_API_KEY=", "GOOGLE_API_KEY=", "API_KEY=", "key="):
        if k.startswith(awalan):
            k = k[len(awalan):].strip().strip("\"'")
    return "".join(k.split())


def cek_format_key(key: str):
    """Kembalikan peringatan jika key tidak tampak seperti API key Gemini, atau None."""
    k = bersihkan_key(key)
    if not k:
        return "API key masih kosong."
    if not k.startswith("AIza"):
        return ("Key Gemini dari Google AI Studio biasanya diawali 'AIza'. Pastikan yang disalin "
                "adalah API key itu sendiri, bukan nama/ID project atau potongan kode.")
    if len(k) < 35:
        return (f"Key hanya {len(k)} karakter, kemungkinan tidak tersalin lengkap "
                "(key Gemini biasanya 39 karakter). Gunakan tombol salin di Google AI Studio.")
    return None


def siap(cfg: dict) -> bool:
    return bool(bersihkan_key(cfg.get("api_key", "")))


# ------------------------------------------------------------------ prompt --

def _info_rmt(misi, tahap) -> dict:
    try:
        return rmt.info_tahap(misi.nomor, misi.tahapan.index(tahap))
    except (KeyError, ValueError, IndexError):
        return {}


def _konteks(misi, tahap) -> str:
    baris = [
        f"Indikator literasi: {misi.indikator}",
        f"Soal: {misi.soal}",
        f"Tahap yang sedang dikerjakan: {tahap.judul}",
        f"Perintah tahap: {tahap.perintah}",
    ]
    info = _info_rmt(misi, tahap)
    if info:
        baris += [
            f"Fase kognitif RMT: {rmt.FASE[info['fase']]}",
            f"Operasi mental: {info['operasi']}",
            f"Alat psikologis yang dipakai: {info['alat']}",
            f"Fungsi kognitif yang dilatih: {info['fungsi']}",
        ]
    if tahap.jenis == "pilihan":
        baris.append("Pilihan jawaban:")
        baris += [f"  {'ABCD'[i]}. {p}" for i, p in enumerate(tahap.pilihan)]
    else:
        baris.append("Yang harus diisi: " + ", ".join(s.label for s in tahap.isian))
    return "\n".join(baris)


def _kunci(tahap) -> str:
    if tahap.jenis == "pilihan":
        return f"{'ABCD'[tahap.kunci_pilihan]}. {tahap.pilihan[tahap.kunci_pilihan]}"
    return ", ".join(f"{s.label} = {s.kunci()}" for s in tahap.isian)


def teks_jawaban(tahap, jawaban) -> str:
    """Ubah jawaban mentah siswa menjadi teks yang mudah dibaca AI."""
    if tahap.jenis == "pilihan":
        if isinstance(jawaban, int) and 0 <= jawaban < len(tahap.pilihan):
            return f"{'ABCD'[jawaban]}. {tahap.pilihan[jawaban]}"
        return "(belum memilih)"
    isi = [f"{s.label} = {j.strip() or '(kosong)'}" for s, j in zip(tahap.isian, jawaban or [])]
    return ", ".join(isi) if isi else "(belum mengisi)"


def pesan_petunjuk(misi, tahap, jawaban_sementara: str = "") -> list:
    """Petunjuk bertahap: menuntun tanpa memberi jawaban akhir."""
    tambahan = (f"\nJawaban sementara siswa: {jawaban_sementara}"
                if jawaban_sementara and "belum" not in jawaban_sementara else "")
    return [
        {"role": "system", "content": SISTEM},
        {"role": "user", "content": (
            f"{_konteks(misi, tahap)}{tambahan}\n\n"
            "Siswa meminta MEDIASI untuk tahap ini. JANGAN sebutkan jawaban akhir, angka hasil, "
            "atau huruf pilihan yang benar. Berikan 2–3 pertanyaan terpimpin yang melatih fungsi "
            "kognitif fase ini dan sarankan alat psikologis yang tepat (misalnya tabel atau rumus). "
            "Maksimal 80 kata.")},
    ]


def pesan_penjelasan(misi, tahap, jawaban_siswa: str, benar: bool) -> list:
    """Penjelasan personal setelah siswa menjawab."""
    status = "BENAR" if benar else "SALAH"
    return [
        {"role": "system", "content": SISTEM},
        {"role": "user", "content": (
            f"{_konteks(misi, tahap)}\n\n"
            f"Jawaban siswa: {jawaban_siswa}\n"
            f"Kunci jawaban: {_kunci(tahap)}\n"
            f"Status: jawaban siswa {status}.\n"
            f"Pembahasan resmi: {tahap.penjelasan}\n\n"
            + ("Lakukan DIAGNOSIS RMT: sebutkan pada fase mana kesulitan siswa kemungkinan terjadi "
               "(Input, Elaborasi, atau Output) dan miskonsepsi apa yang terlihat dari jawabannya. "
               "Lalu mediasi cara berpikir yang benar langkah demi langkah. "
               if not benar else
               "Beri penguatan singkat, jelaskan fungsi kognitif yang sudah ia gunakan dengan baik, "
               "dan ajak siswa merefleksikan strateginya. ")
            + "Tutup dengan satu kalimat TRANSENDENSI (prinsip umum yang berlaku di situasi lain). "
            "Maksimal 130 kata.")},
    ]


def pesan_tanya(pertanyaan: str, misi=None, tahap=None) -> list:
    """Pertanyaan bebas siswa tentang materi."""
    konteks = f"Konteks soal yang sedang dikerjakan:\n{_konteks(misi, tahap)}\n\n" if misi and tahap else ""
    return [
        {"role": "system", "content": SISTEM},
        {"role": "user", "content": (
            f"{konteks}Pertanyaan siswa: {pertanyaan}\n\n"
            "Jawab dengan jelas dan singkat (maksimal 120 kata). Jika pertanyaan di luar materi "
            "matematika, arahkan kembali dengan sopan ke materi untung dan rugi.")},
    ]


# ------------------------------------------------------------ panggil API --

def buat_permintaan(cfg: dict, pesan: list, maks_token: int = 400):
    """Kembalikan (url, headers, body) untuk API chat completions."""
    p = PENYEDIA.get(cfg.get("penyedia"), PENYEDIA[PENYEDIA_BAWAAN])
    body = {
        "model": cfg.get("model") or p["model"],
        "messages": pesan,
        "temperature": 0.4,
        # Model Gemini terbaru "berpikir" dulu dan token berpikir ikut dihitung,
        # jadi diberi ruang tambahan agar jawabannya tidak terpotong/kosong.
        "max_tokens": maks_token + 2048,
        "stream": False,
    }
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {bersihkan_key(cfg.get('api_key', ''))}"}
    return p["url"], headers, body


def ambil_teks(data: dict) -> str:
    try:
        teks = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pesan = (data.get("error") or {}).get("message") if isinstance(data, dict) else None
        raise AIError(f"Respons AI tidak dikenali{': ' + pesan if pesan else '.'}")
    teks = (teks or "").strip()
    if not teks:
        raise AIError("AI tidak memberi jawaban. Coba klik tombol AI sekali lagi.")
    return teks


def pesan_galat_http(kode: int, isi: str = "") -> str:
    """Pesan ramah untuk kode galat HTTP. Gemini memakai kode 400 untuk API key salah."""
    if any(k in isi for k in ("API_KEY_INVALID", "API key not valid", "API key expired",
                              "valid API key")):
        return "API key Gemini tidak valid. Salin ulang key dari Google AI Studio."
    if "location is not supported" in isi.lower():
        return "Layanan Gemini belum tersedia di lokasi/jaringan ini."
    return {
        400: "Permintaan ditolak server AI (periksa API key dan nama model di Pengaturan AI).",
        401: "API key tidak valid. Periksa kembali API key di Pengaturan AI.",
        402: "Kuota akun AI habis. Coba lagi nanti atau periksa akun Google AI Studio.",
        403: "Akses ditolak oleh server AI. Periksa API key dan izin akun.",
        404: "Model AI tidak ditemukan. Periksa nama model di Pengaturan AI.",
        429: "Batas kuota gratis Gemini tercapai. Tunggu sekitar 1 menit, lalu coba lagi.",
        500: "Server AI sedang mengalami gangguan. Tunggu 1–2 menit, lalu klik tombol AI lagi.",
        503: "Server Gemini sedang sibuk karena banyak pengguna. Aplikasi sudah mencoba ulang "
             "otomatis — tunggu 1–2 menit, lalu klik tombol AI lagi.",
    }.get(kode, f"Server AI sedang bermasalah (kode {kode}). Coba lagi nanti.")


class _GagalHTTP(Exception):
    def __init__(self, kode: int, isi: str):
        super().__init__(kode)
        self.kode, self.isi = kode, isi


def _kirim(url, headers, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            isi = e.read().decode("utf-8", "replace")
        except OSError:
            isi = ""
        raise _GagalHTTP(e.code, isi) from None


def daftar_model(cfg: dict) -> list:
    """Model yang dicoba berurutan: model pilihan/bawaan, lalu model cadangan."""
    p = PENYEDIA.get(cfg.get("penyedia"), PENYEDIA[PENYEDIA_BAWAAN])
    utama = cfg.get("model") or p["model"]
    return [utama] + ([p["cadangan"]] if p.get("cadangan") and p["cadangan"] != utama else [])


def panggil(cfg: dict, pesan: list, timeout: int = 60, maks_token: int = 400) -> str:
    """Kirim pesan ke AI dan kembalikan teks jawabannya (dipakai versi desktop).

    Jika server sibuk (5xx), dicoba ulang otomatis beberapa kali; jika tetap
    sibuk atau kuota habis (429), beralih ke model cadangan.
    """
    if not siap(cfg):
        raise AIError("API key belum diisi. Buka menu ⚙️ Pengaturan AI terlebih dahulu.")
    url, headers, body = buat_permintaan(cfg, pesan, maks_token)
    galat = galat_utama = None
    for model in daftar_model(cfg):
        body["model"] = model
        for percobaan in range(JUMLAH_COBA_ULANG + 1):
            try:
                return ambil_teks(_kirim(url, headers, body, timeout))
            except _GagalHTTP as e:
                galat = e
                if e.kode in KODE_COBA_ULANG and percobaan < JUMLAH_COBA_ULANG:
                    time.sleep(JEDA_COBA_ULANG * (percobaan + 1))
                    continue
                break  # ke model cadangan (atau berhenti)
            except (urllib.error.URLError, TimeoutError, OSError):
                raise AIError("Tidak dapat terhubung ke server AI. Periksa koneksi internet.") from None
            except ValueError:
                raise AIError("Respons AI tidak dapat dibaca.") from None
        if galat_utama is None:
            galat_utama = galat
        if galat.kode not in KODE_COBA_ULANG + (429,):
            break  # galat lain (mis. key salah) tidak perlu dicoba dengan model cadangan
    if galat.kode in (400, 404) and galat is not galat_utama:
        galat = galat_utama  # model cadangan tidak tersedia: laporkan masalah model utama
    pesan_galat = pesan_galat_http(galat.kode, galat.isi)
    saran = cek_format_key(cfg.get("api_key", ""))
    if "tidak valid" in pesan_galat and saran:
        pesan_galat += " " + saran
    raise AIError(pesan_galat)


def pesan_refleksi(misi, fase_sulit: str, strategi: str) -> list:
    """Tanggapan AI atas refleksi metakognitif siswa di akhir misi."""
    return [
        {"role": "system", "content": SISTEM},
        {"role": "user", "content": (
            f"Siswa baru menyelesaikan misi \"{misi.judul}\" (indikator {misi.indikator}).\n"
            f"Refleksi siswa — fase yang paling menantang: {fase_sulit}; strategi yang paling "
            f"membantu: {strategi}.\n\n"
            "Berikan tanggapan reflektif (metakognisi): hargai refleksinya, beri satu saran "
            "konkret untuk melatih fase yang menantang itu, dan satu pertanyaan reflektif "
            "untuk dipikirkan. Maksimal 90 kata.")},
    ]