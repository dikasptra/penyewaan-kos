class Sewa:
    def __init__(self, penyewa, kamar, tanggal_mulai, durasi_bulan):
        self.penyewa = penyewa
        self.kamar = kamar
        self.tanggal_mulai = tanggal_mulai
        self.durasi_bulan = durasi_bulan
        self.aktif = False

    def proses_sewa(self):
        if not self.kamar.tersedia():
            print(f"-> Hasil: Maaf, Kamar {self.kamar.nomor_kamar} tidak tersedia.")
            return False

        self.kamar.sewakan()
        self.aktif = True
        print(f"-> Hasil: {self.penyewa.nama} berhasil menyewa Kamar {self.kamar.nomor_kamar} selama {self.durasi_bulan} bulan.")
        print(f"-> Total biaya sewa: Rp{self.hitung_total():,}")
        return True

    def hitung_total(self):
        return self.kamar.harga_per_bulan * self.durasi_bulan

    def proses_pengakhiran(self):
        self.kamar.kosongkan()
        self.aktif = False
        print(f"-> Hasil: Sewa selesai, Kamar {self.kamar.nomor_kamar} kembali tersedia.")