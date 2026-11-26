import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from permainan import Permainan, bintang, predikat  # noqa: E402
from skor import muat_skor, tambah_skor  # noqa: E402
from soal import misi_acak, misi_kisi_kisi, parse_angka, persen, rupiah  # noqa: E402


def jawaban_benar(tahap):
    if tahap.jenis == "pilihan":
        return tahap.kunci_pilihan
    return [str(i.jawaban).replace(".", ",") for i in tahap.isian]


class TestKisiKisi(unittest.TestCase):
    """Jawaban harus sama persis dengan dokumen kisi-kisi."""

    def setUp(self):
        self.misi = misi_kisi_kisi(random.Random(0))

    def kunci(self, m, t):
        return [i.jawaban for i in self.misi[m].tahapan[t].isian]

    def pilihan_benar(self, m, t):
        tahap = self.misi[m].tahapan[t]
        return tahap.pilihan[tahap.kunci_pilihan]

    def test_skor_maksimum_6_per_soal(self):
        self.assertEqual([m.skor_maks for m in self.misi], [6, 6, 6, 6])
        self.assertEqual([len(m.tahapan) for m in self.misi], [5, 6, 6, 6])
        self.assertEqual(self.misi[0].tahapan[2].skor, 2)  # Tahap 3 soal 1 = 2

    def test_soal1_penalaran(self):
        self.assertEqual(self.kunci(0, 1), [30000, 35000, 32000])
        self.assertEqual(self.kunci(0, 2), [25, 25, 20])
        self.assertEqual(self.pilihan_benar(0, 3), "Toko A = Toko B > Toko C")
        self.assertIn("Toko A dan Toko B", self.pilihan_benar(0, 4))
        self.assertIn("sama-sama 25%", self.pilihan_benar(0, 4))

    def test_soal2_formulasi(self):
        self.assertEqual(self.kunci(1, 1), [50000])
        self.assertEqual(self.pilihan_benar(1, 2), "Harga jual = harga beli + keuntungan")
        self.assertEqual(self.pilihan_benar(1, 3), "Harga jual = Rp250.000 + Rp50.000")
        self.assertEqual(self.kunci(1, 4), [300000])
        self.assertIn("Rp300.000", self.pilihan_benar(1, 5))

    def test_soal3_prosedur(self):
        self.assertEqual(self.kunci(2, 1), [120000])
        self.assertEqual(self.kunci(2, 2), [15])
        self.assertEqual(self.kunci(2, 3), [75000])
        self.assertEqual(self.kunci(2, 4), [15])

    def test_soal4_evaluasi(self):
        self.assertIn("17,65%", self.misi[3].soal)
        self.assertEqual(self.kunci(3, 1), [60000])
        self.assertEqual(self.pilihan_benar(3, 3), "(60.000 ÷ 400.000) × 100%")
        self.assertEqual(self.kunci(3, 4), [15])
        self.assertIn("tidak benar", self.pilihan_benar(3, 5))
        self.assertIn("bukan 17,65%", self.pilihan_benar(3, 5))


class TestSoalAcak(unittest.TestCase):
    def test_struktur_valid(self):
        rng = random.Random(7)
        for _ in range(300):
            for m in misi_acak(rng):
                self.assertEqual(m.skor_maks, 6)
                for t in m.tahapan:
                    if t.jenis == "pilihan":
                        self.assertEqual(len(t.pilihan), 4, t.judul)
                        self.assertEqual(len(set(t.pilihan)), 4, t.judul)
                        self.assertIn(t.kunci_pilihan, range(4))
                    else:
                        for i in t.isian:
                            self.assertGreater(i.jawaban, 0)
                            self.assertTrue(t.periksa(jawaban_benar(t)))


class TestFormat(unittest.TestCase):
    def test_format(self):
        self.assertEqual(rupiah(1500000), "Rp1.500.000")
        self.assertEqual(persen(25.0), "25%")
        self.assertEqual(persen(60000 * 100 / 340000), "17,65%")

    def test_parse_angka(self):
        self.assertEqual(parse_angka("15000"), 15000)
        self.assertEqual(parse_angka("Rp 15.000"), 15000)
        self.assertEqual(parse_angka("15.000,00"), 15000)
        self.assertEqual(parse_angka("25%"), 25)
        self.assertEqual(parse_angka("17,65"), 17.65)
        self.assertEqual(parse_angka("0,15"), 0.15)
        self.assertIsNone(parse_angka(""))
        self.assertIsNone(parse_angka("abc"))
        self.assertIsNone(parse_angka(None))


class TestPermainan(unittest.TestCase):
    def test_semua_benar_nilai_100(self):
        p = Permainan("kisi", random.Random(1))
        while not p.selesai:
            self.assertTrue(p.jawab(jawaban_benar(p.tahap_sekarang)).benar)
            p.maju()
        self.assertEqual((p.skor, p.skor_maks, p.nilai), (24, 24, 100))
        self.assertEqual(predikat(p.nilai), "A — Sangat Baik")

    def test_jawaban_salah_skor_nol(self):
        p = Permainan("kisi", random.Random(1))
        t = p.tahap_sekarang  # pilihan ganda
        salah = (t.kunci_pilihan + 1) % 4
        self.assertEqual(p.jawab(salah).skor, 0)
        p.maju()
        h = p.jawab(["30000", "35000", "99"])  # satu isian salah -> skor tahap 0
        self.assertEqual(h.per_butir, [True, True, False])
        self.assertEqual(h.skor, 0)
        with self.assertRaises(RuntimeError):
            p.jawab(["30000", "35000", "32000"])

    def test_bintang(self):
        self.assertEqual([bintang(s, 6) for s in (6, 4, 2, 1)], [3, 2, 1, 0])


class TestSkor(unittest.TestCase):
    def test_simpan_dan_urutkan(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "skor.json"
            self.assertEqual(muat_skor(path), [])
            self.assertEqual(tambah_skor("A", 50, 12, "kisi", path), 1)
            self.assertEqual(tambah_skor("B", 92, 22, "kisi", path), 1)
            self.assertEqual(tambah_skor("C", 75, 18, "acak", path), 2)
            self.assertEqual([e["nama"] for e in muat_skor(path)], ["B", "C", "A"])


if __name__ == "__main__":
    unittest.main()
