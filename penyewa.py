class Penyewa:
    def __init__(self, id_penyewa, nama, no_telepon):
        self.id_penyewa = id_penyewa
        self.nama = nama
        self.no_telepon = no_telepon

    def sewa_kamar(self, kamar):
        print(f"-> {self.nama} memilih Kamar {kamar.nomor_kamar} ({kamar.tipe}).")

    def akhiri_sewa(self, sewa):
        print(f"-> {self.nama} mengakhiri sewa kamar.")
        sewa.proses_pengakhiran()

    def info(self):
        return f"ID: {self.id_penyewa} | Nama: {self.nama} | Telp: {self.no_telepon}"