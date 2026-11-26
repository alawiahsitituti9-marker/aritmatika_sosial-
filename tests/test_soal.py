import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from permainan import Permainan  # noqa: E402
from skor import muat_skor, tambah_skor  # noqa: E402
from soal import GENERATOR_PER_LEVEL, buat_soal, parse_jawaban, rupiah  # noqa: E402


class TestSoal(unittest.TestCase):
    def test_semua_generator_menghasilkan_jawaban_bulat_positif(self):
        rng = random.Random(42)
        for level, generators in GENERATOR_PER_LEVEL.items():
            for gen in generators:
                for _ in range(500):
                    s = gen(rng)
                    self.assertIsInstance(s.jawaban, int, gen.__name__)
                    self.assertGreater(s.jawaban, 0, gen.__name__)
                    self.assertTrue(s.pertanyaan and s.pembahasan)

    def test_buat_soal_tiap_level(self):
        for level in (1, 2, 3):
            self.assertIsNotNone(buat_soal(level, random.Random(1)))

    def test_rupiah(self):
        self.assertEqual(rupiah(1500000), "Rp1.500.000")
        self.assertEqual(rupiah(500), "Rp500")

    def test_parse_jawaban(self):
        self.assertEqual(parse_jawaban("15000"), 15000)
        self.assertEqual(parse_jawaban("Rp 15.000"), 15000)
        self.assertEqual(parse_jawaban("15.000,00"), 15000)
        self.assertEqual(parse_jawaban("25%"), 25)
        self.assertEqual(parse_jawaban("40 kg"), 40)
        self.assertIsNone(parse_jawaban(""))
        self.assertIsNone(parse_jawaban("abc"))
        self.assertIsNone(parse_jawaban("12,5"))
        self.assertIsNone(parse_jawaban(None))


class TestPermainan(unittest.TestCase):
    def test_jawaban_benar_menambah_skor(self):
        p = Permainan(1, rng=random.Random(3))
        s = p.soal_berikutnya()
        h = p.jawab(str(s.jawaban), sisa_waktu=60)
        self.assertTrue(h.benar)
        self.assertEqual(p.skor, 10 + 10)
        self.assertEqual(p.nyawa, 3)

    def test_jawaban_salah_dan_waktu_habis_mengurangi_nyawa(self):
        p = Permainan(2, rng=random.Random(3))
        s = p.soal_berikutnya()
        self.assertFalse(p.jawab(str(s.jawaban + 1)).benar)
        p.soal_berikutnya()
        self.assertFalse(p.jawab(None).benar)
        self.assertEqual(p.nyawa, 1)

    def test_permainan_selesai(self):
        p = Permainan(3, jumlah_soal=3, rng=random.Random(5))
        while not p.selesai:
            s = p.soal_berikutnya()
            p.jawab(str(s.jawaban))
        self.assertEqual(p.jumlah_benar, 3)
        self.assertEqual(p.nomor, 3)


class TestSkor(unittest.TestCase):
    def test_simpan_dan_urutkan(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "skor.json"
            self.assertEqual(muat_skor(path), [])
            self.assertEqual(tambah_skor("A", 50, 1, 5, path), 1)
            self.assertEqual(tambah_skor("B", 90, 2, 8, path), 1)
            self.assertEqual(tambah_skor("C", 70, 1, 7, path), 2)
            self.assertEqual([e["nama"] for e in muat_skor(path)], ["B", "C", "A"])


if __name__ == "__main__":
    unittest.main()
