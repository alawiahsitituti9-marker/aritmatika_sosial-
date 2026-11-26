"""Ringkasan materi Aritmatika Sosial (SMP kelas VII)."""

MATERI = [
    ("Untung dan Rugi", """\
Harga beli  = harga saat pedagang membeli barang (modal).
Harga jual  = harga saat barang dijual kembali.

• Jika harga jual > harga beli  → UNTUNG
      Untung = Harga jual − Harga beli
• Jika harga jual < harga beli  → RUGI
      Rugi = Harga beli − Harga jual

Contoh:
Beli sepeda Rp500.000, dijual Rp560.000.
Untung = Rp560.000 − Rp500.000 = Rp60.000
"""),
    ("Persentase Untung/Rugi", """\
Persentase selalu dihitung terhadap HARGA BELI.

  % Untung = (Untung ÷ Harga beli) × 100%
  % Rugi   = (Rugi ÷ Harga beli) × 100%

Menentukan harga jual:
  Untung p%  → Harga jual = (100% + p%) × Harga beli
  Rugi p%    → Harga jual = (100% − p%) × Harga beli

Menentukan harga beli:
  Untung p%  → Harga beli = (100 ÷ (100 + p)) × Harga jual
  Rugi p%    → Harga beli = (100 ÷ (100 − p)) × Harga jual

Contoh:
Beli Rp200.000, untung 15%.
Untung = 15% × Rp200.000 = Rp30.000
Harga jual = Rp230.000
"""),
    ("Diskon (Rabat)", """\
Diskon = potongan harga, biasanya dalam persen dari harga awal.

  Potongan    = Diskon% × Harga awal
  Harga bayar = Harga awal − Potongan
              = (100% − Diskon%) × Harga awal

Diskon bertingkat, misal "20% + 10%":
  Diskon kedua dihitung dari harga SETELAH diskon pertama.
  Rp100.000 → diskon 20% → Rp80.000 → diskon 10% → Rp72.000
  (Bukan diskon 30% = Rp70.000!)
"""),
    ("Pajak (PPN)", """\
Pajak Pertambahan Nilai (PPN) ditambahkan ke harga barang.
Tarif PPN di Indonesia saat ini: 11%.

  PPN        = 11% × Harga sebelum pajak
  Total bayar = Harga + PPN = 111% × Harga

Contoh:
Harga Rp200.000 → PPN = Rp22.000 → Total Rp222.000
"""),
    ("Bunga Tunggal", """\
Bunga tunggal: bunga dihitung dari modal awal saja (tidak berbunga lagi).

  Bunga n bulan = (n ÷ 12) × b% × M
     M = modal/tabungan awal
     b = suku bunga per tahun
     n = lama menabung (bulan)

  Tabungan akhir = M + Bunga

Mencari lama menabung:
  n = (Bunga ÷ (b% × M)) × 12

Contoh:
M = Rp1.200.000, bunga 6%/tahun, 8 bulan
Bunga = (8/12) × 6% × Rp1.200.000 = Rp48.000
Tabungan akhir = Rp1.248.000
"""),
    ("Bruto, Tara, Neto", """\
Bruto = berat kotor (barang + wadah)
Tara  = berat wadah/kemasan
Neto  = berat bersih (barang saja)

  Neto  = Bruto − Tara
  Bruto = Neto + Tara
  Tara  = Bruto − Neto

Persentase tara:
  Tara = %Tara × Bruto

Contoh:
Bruto 500 kg, tara 2% → Tara = 10 kg → Neto = 490 kg
"""),
]
