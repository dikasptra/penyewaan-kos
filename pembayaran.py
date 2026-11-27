class Pembayaran:
    def __init__(self, sewa, jumlah, tanggal_bayar, id_pembayaran=None, total_dibayar=None):
        if not isinstance(jumlah, int) or jumlah <= 0:
            raise ValueError("Jumlah pembayaran harus lebih dari 0.")

        self.id_pembayaran = id_pembayaran
        self.sewa = sewa
        self.jumlah = jumlah
        self.tanggal_bayar = tanggal_bayar
        self.total_dibayar = jumlah if total_dibayar is None else total_dibayar

    def catat_pembayaran(self):
        status = "Lunas" if self.cek_lunas() else "Belum Lunas"
        print(f"-> Hasil: Pembayaran Rp{self.jumlah:,} pada {self.tanggal_bayar} berhasil dicatat | Status: {status}")

    def cek_lunas(self):
        return self.total_dibayar >= self.sewa.hitung_total()