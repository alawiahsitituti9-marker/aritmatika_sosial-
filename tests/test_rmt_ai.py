import json
import random
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ai_tutor  # noqa: E402
import rmt  # noqa: E402
import web_api  # noqa: E402
from permainan import Permainan  # noqa: E402
from soal import misi_acak, misi_kisi_kisi  # noqa: E402


def kunci(t):
    return t.kunci_pilihan if t.jenis == "pilihan" else [str(i.jawaban) for i in t.isian]


def salah(t):
    return (t.kunci_pilihan + 1) % 4 if t.jenis == "pilihan" else ["1"] * len(t.isian)


class TestRMT(unittest.TestCase):
    def test_data_rmt_lengkap_untuk_setiap_tahap(self):
        for kumpulan in (misi_kisi_kisi(random.Random(1)), misi_acak(random.Random(2))):
            for m in kumpulan:
                info = rmt.info_misi(m.nomor)
                for k in ("tujuan", "makna", "sehari_hari", "analisis", "transendensi"):
                    self.assertTrue(info[k], k)
                self.assertEqual(len(rmt.TAHAP[m.nomor]), len(m.tahapan), m.judul)
                for j in range(len(m.tahapan)):
                    t = rmt.info_tahap(m.nomor, j)
                    self.assertIn(t["fase"], rmt.FASE)
                    self.assertGreaterEqual(len(t["mediasi"]), 2)

    def test_mediasi_tidak_membocorkan_kunci_isian(self):
        for m in misi_kisi_kisi(random.Random(0)):
            for j, t in enumerate(m.tahapan):
                teks = " ".join(rmt.info_tahap(m.nomor, j)["mediasi"])
                for s in t.isian:
                    self.assertNotIn(s.kunci(), teks, f"{m.judul} / {t.judul}")

    def test_setiap_misi_punya_ketiga_fase(self):
        for nomor, daftar in rmt.TAHAP.items():
            self.assertEqual(daftar[0]["fase"], "input", nomor)
            self.assertEqual(daftar[-1]["fase"], "output", nomor)
            self.assertIn("elaborasi", [t["fase"] for t in daftar])

    def test_profil_dan_fase_terlemah(self):
        p = Permainan("kisi", random.Random(1))
        while not p.selesai:
            t = p.tahap_sekarang
            fase = rmt.info_tahap(p.misi_sekarang.nomor, p.i_tahap)["fase"]
            p.jawab(salah(t) if fase == "output" else kunci(t))
            p.maju()
        profil = rmt.profil_fase(p)
        self.assertEqual(profil["output"], (0, 4))
        self.assertEqual(profil["input"], (4, 4))
        self.assertEqual(rmt.fase_terlemah(profil), "output")
        self.assertEqual(sum(d for d, _ in profil.values()), p.skor)


class TestAsesmenDinamis(unittest.TestCase):
    def test_uji_ulang_setelah_mediasi(self):
        p = Permainan("kisi", random.Random(1))
        t = p.tahap_sekarang
        self.assertFalse(p.boleh_ulang)          # belum menjawab
        self.assertEqual(p.jawab(salah(t)).skor, 0)
        self.assertTrue(p.boleh_ulang)
        self.assertEqual(p.jawab_ulang(kunci(t)).skor, t.skor)
        self.assertFalse(p.boleh_ulang)          # hanya sekali
        with self.assertRaises(RuntimeError):
            p.jawab_ulang(kunci(t))
        self.assertEqual(p.skor, 0)              # skor resmi tetap (sesuai kisi-kisi)
        self.assertEqual(p.skor_setelah_mediasi, t.skor)
        self.assertEqual(p.jumlah_mediasi, 1)

    def test_tidak_boleh_ulang_jika_benar(self):
        p = Permainan("kisi", random.Random(1))
        p.jawab(kunci(p.tahap_sekarang))
        self.assertFalse(p.boleh_ulang)

    def test_refleksi_tersimpan(self):
        p = Permainan("kisi", random.Random(1))
        p.simpan_refleksi("input", "Menyusun data dalam tabel")
        self.assertEqual(p.refleksi[0]["fase"], "input")


class _ServerTiruan(BaseHTTPRequestHandler):
    """Meniru endpoint Gemini yang kompatibel OpenAI."""
    diterima = {}
    model_dicoba = []
    gagal_dulu = 0  # jumlah respons 503 sebelum berhasil

    def do_POST(self):
        panjang = int(self.headers["Content-Length"])
        _ServerTiruan.diterima = {"auth": self.headers.get("Authorization"),
                                  "body": json.loads(self.rfile.read(panjang))}
        _ServerTiruan.model_dicoba.append(_ServerTiruan.diterima["body"]["model"])
        kode_sibuk = {"sibuk-503": 503, "habis-429": 429}.get(_ServerTiruan.diterima["body"]["model"])
        if kode_sibuk or (_ServerTiruan.gagal_dulu > 0):
            _ServerTiruan.gagal_dulu -= 1
            self.send_response(kode_sibuk or 503)
            self.end_headers()
            self.wfile.write(b'{"error": {"code": 503, "message": "The model is overloaded."}}')
            return
        if self.headers.get("Authorization") == "Bearer salah":
            isi = b'[{"error": {"code": 400, "message": "API key not valid. Please pass a valid API key.", "status": "INVALID_ARGUMENT", "details": [{"reason": "API_KEY_INVALID"}]}}]'
            self.send_response(400)
            self.end_headers()
            self.wfile.write(isi)
            return
        data = {"choices": [{"message": {"role": "assistant", "content": " Coba susun tabel. "}}]}
        isi = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(isi)))
        self.end_headers()
        self.wfile.write(isi)

    def log_message(self, *a):
        pass


class TestAITutor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _ServerTiruan)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/chat/completions"
        cls.jeda_asli, ai_tutor.JEDA_COBA_ULANG = ai_tutor.JEDA_COBA_ULANG, 0
        cls.asli = ai_tutor.PENYEDIA["gemini"]["url"]
        ai_tutor.PENYEDIA["gemini"]["url"] = cls.url

    @classmethod
    def tearDownClass(cls):
        ai_tutor.PENYEDIA["gemini"]["url"] = cls.asli
        ai_tutor.JEDA_COBA_ULANG = cls.jeda_asli
        cls.server.shutdown()

    def setUp(self):
        self.misi = misi_kisi_kisi(random.Random(0))

    def test_panggil_berhasil(self):
        cfg = {"penyedia": "gemini", "api_key": "kunci-uji", "model": ""}
        pesan = ai_tutor.pesan_petunjuk(self.misi[0], self.misi[0].tahapan[2])
        self.assertEqual(ai_tutor.panggil(cfg, pesan), "Coba susun tabel.")
        self.assertEqual(_ServerTiruan.diterima["auth"], "Bearer kunci-uji")
        body = _ServerTiruan.diterima["body"]
        self.assertEqual(body["model"], "gemini-flash-latest")
        self.assertIn("generativelanguage.googleapis.com", self.asli)
        self.assertEqual(body["messages"][0]["role"], "system")

    def test_coba_ulang_saat_server_sibuk(self):
        cfg = {"penyedia": "gemini", "api_key": "kunci-uji", "model": ""}
        _ServerTiruan.model_dicoba, _ServerTiruan.gagal_dulu = [], 1
        self.assertEqual(ai_tutor.panggil(cfg, []), "Coba susun tabel.")
        self.assertEqual(_ServerTiruan.model_dicoba, ["gemini-flash-latest"] * 2)

    def test_pindah_ke_model_cadangan(self):
        for model, kode in (("sibuk-503", 503), ("habis-429", 429)):
            _ServerTiruan.model_dicoba, _ServerTiruan.gagal_dulu = [], 0
            cfg = {"penyedia": "gemini", "api_key": "kunci-uji", "model": model}
            self.assertEqual(ai_tutor.panggil(cfg, []), "Coba susun tabel.")
            self.assertEqual(_ServerTiruan.model_dicoba[-1], "gemini-flash-lite-latest")
            percobaan = ai_tutor.JUMLAH_COBA_ULANG + 1 if kode == 503 else 1
            self.assertEqual(_ServerTiruan.model_dicoba.count(model), percobaan)

    def test_cadangan_tidak_ada_tetap_laporkan_server_sibuk(self):
        asli = ai_tutor.PENYEDIA["gemini"]["cadangan"]
        ai_tutor.PENYEDIA["gemini"]["cadangan"] = "sibuk-503"
        try:
            # cadangan juga sibuk -> pesan tetap "server sibuk"
            with self.assertRaisesRegex(ai_tutor.AIError, "sedang sibuk"):
                ai_tutor.panggil({"penyedia": "gemini", "api_key": "kunci-uji", "model": "habis-429"}, [])
        finally:
            ai_tutor.PENYEDIA["gemini"]["cadangan"] = asli

    def test_key_salah_tidak_dicoba_ulang(self):
        _ServerTiruan.model_dicoba, _ServerTiruan.gagal_dulu = [], 0
        with self.assertRaises(ai_tutor.AIError):
            ai_tutor.panggil({"penyedia": "gemini", "api_key": "salah"}, [])
        self.assertEqual(len(_ServerTiruan.model_dicoba), 1)

    def test_key_salah_dan_key_kosong(self):
        with self.assertRaisesRegex(ai_tutor.AIError, "API key Gemini tidak valid.*diawali 'AIza'"):
            ai_tutor.panggil({"penyedia": "gemini", "api_key": "salah"}, [])
        with self.assertRaisesRegex(ai_tutor.AIError, "belum diisi"):
            ai_tutor.panggil({"penyedia": "gemini", "api_key": ""}, [])
        with self.assertRaisesRegex(ai_tutor.AIError, "tidak memberi jawaban"):
            ai_tutor.ambil_teks({"choices": [{"message": {"content": ""}}]})

    def test_key_dibersihkan_dan_dicek(self):
        asli = "AIza" + "x" * 35
        for salinan in (f"  {asli}\n", f'"{asli}"', f"Bearer {asli}", f"GEMINI_API_KEY={asli}",
                        asli[:20] + "\n" + asli[20:]):
            self.assertEqual(ai_tutor.bersihkan_key(salinan), asli, repr(salinan))
        self.assertIsNone(ai_tutor.cek_format_key(asli))
        self.assertIn("AIza", ai_tutor.cek_format_key("project-123456"))
        self.assertIn("tidak tersalin lengkap", ai_tutor.cek_format_key("AIzaSyABC"))
        cfg = {"penyedia": "gemini", "api_key": f"  '{asli}' ", "model": ""}
        _, headers, _ = ai_tutor.buat_permintaan(cfg, [])
        self.assertEqual(headers["Authorization"], f"Bearer {asli}")

    def test_prompt_rmt(self):
        m, t = self.misi[3], self.misi[3].tahapan[2]
        petunjuk = ai_tutor.pesan_petunjuk(m, t)[1]["content"]
        self.assertIn("Fase kognitif RMT", petunjuk)
        self.assertIn("JANGAN", petunjuk)
        self.assertIn("Rigorous Mathematical Thinking", ai_tutor.SISTEM)
        jelas = ai_tutor.pesan_penjelasan(m, t, "A. salah", False)[1]["content"]
        self.assertIn("DIAGNOSIS RMT", jelas)
        self.assertIn("TRANSENDENSI", jelas)
        refl = ai_tutor.pesan_refleksi(m, "Input", "Menyusun data dalam tabel")[1]["content"]
        self.assertIn("metakognisi", refl)

    def test_config_tidak_bocor_dan_tersimpan(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config_ai.json"
            self.assertEqual(ai_tutor.muat_config(path)["penyedia"], "gemini")
            ai_tutor.simpan_config({"penyedia": "gemini", "api_key": "abc", "model": ""}, path)
            cfg = ai_tutor.muat_config(path)
            self.assertEqual((cfg["penyedia"], cfg["api_key"]), ("gemini", "abc"))
            # konfigurasi lama DeepSeek otomatis beralih ke Gemini
            ai_tutor.simpan_config({"penyedia": "deepseek", "api_key": "x", "model": ""}, path)
            self.assertEqual(ai_tutor.muat_config(path)["penyedia"], "gemini")
        gitignore = (Path(__file__).resolve().parent.parent / ".gitignore").read_text()
        self.assertIn("config_ai.json", gitignore)

    def test_web_api_tidak_mengirim_key(self):
        web_api.mulai("kisi")
        req = json.loads(web_api.permintaan_ai("petunjuk", "-1", "gemini", ""))
        self.assertNotIn("Authorization", req["headers"])
        self.assertTrue(req["body"]["model"].startswith("gemini"))
        self.assertEqual(req["url"], ai_tutor.PENYEDIA["gemini"]["url"])
        teks = json.loads(web_api.ambil_teks_ai(json.dumps(
            {"choices": [{"message": {"content": "Halo"}}]})))
        self.assertEqual(teks["teks"], "Halo")


if __name__ == "__main__":
    unittest.main()
