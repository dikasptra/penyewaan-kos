from flask import Flask, render_template, request, redirect, url_for
from kamar import Kamar
from penyewa import Penyewa
from sewa import Sewa
from pembayaran import Pembayaran
import database

app = Flask(__name__)

database.buat_tabel()
pesan_hasil = ""

@app.route("/")
def index():
    global pesan_hasil
    pesan = pesan_hasil
    pesan_hasil = ""
    daftar_sewa = database.ambil_semua_sewa()
    return render_template(
        "index.html",
        daftar_kamar=database.ambil_semua_kamar(),
        daftar_penyewa=database.ambil_semua_penyewa(),
        daftar_sewa=daftar_sewa,
        daftar_sewa_aktif=[sewa for sewa in daftar_sewa if sewa.aktif],
        daftar_pembayaran=database.ambil_semua_pembayaran(),
        pesan=pesan
    )

# KAMAR
@app.route("/kamar", methods=["POST"])
def tambah_kamar():
    global pesan_hasil
    nomor_kamar = request.form["nomor_kamar"]
    tipe = request.form["tipe"]

    try:
        harga = int(request.form["harga_per_bulan"])
        kamar_baru = Kamar(nomor_kamar, tipe, harga)
    except ValueError as e:
        pesan_hasil = str(e)
        return redirect(url_for("index"))

    if database.simpan_kamar(kamar_baru):
        pesan_hasil = f"Kamar {nomor_kamar} berhasil ditambahkan."
    else:
        pesan_hasil = f"Nomor kamar {nomor_kamar} sudah ada."
    return redirect(url_for("index"))

@app.route("/kamar/edit/<nomor_kamar>", methods=["GET", "POST"])
def edit_kamar(nomor_kamar):
    global pesan_hasil
    kamar = database.cari_kamar(nomor_kamar)

    if not kamar:
        pesan_hasil = f"Kamar dengan nomor '{nomor_kamar}' tidak ditemukan."
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            kamar.tipe = request.form["tipe"]
            kamar.harga_per_bulan = int(request.form["harga_per_bulan"])
            database.update_kamar(kamar)
            pesan_hasil = f"Data Kamar {nomor_kamar} berhasil diubah."
        except ValueError as e:
            pesan_hasil = str(e)
        return redirect(url_for("index"))

    return render_template("edit_kamar.html", kamar=kamar)

@app.route("/kamar/hapus/<nomor_kamar>", methods=["POST"])
def hapus_kamar(nomor_kamar):
    global pesan_hasil

    if database.kamar_punya_sewa(nomor_kamar):
        pesan_hasil = f"Kamar {nomor_kamar} tidak bisa dihapus karena sudah punya data sewa. Hapus data sewanya dulu."
    else:
        database.hapus_kamar(nomor_kamar)
        pesan_hasil = f"Kamar {nomor_kamar} berhasil dihapus."
    return redirect(url_for("index"))

# PENYEWA
@app.route("/penyewa", methods=["POST"])
def input_penyewa():
    global pesan_hasil
    id_penyewa = request.form["id_penyewa"]
    nama = request.form["nama"]
    no_telepon = request.form["no_telepon"]

    penyewa_baru = Penyewa(id_penyewa, nama, no_telepon)

    if database.simpan_penyewa(penyewa_baru):
        pesan_hasil = f"Data penyewa tersimpan ({penyewa_baru.info()})"
    else:
        pesan_hasil = f"ID penyewa {id_penyewa} sudah dipakai."
    return redirect(url_for("index"))

@app.route("/penyewa/edit/<id_penyewa>", methods=["GET", "POST"])
def edit_penyewa(id_penyewa):
    global pesan_hasil
    penyewa = database.cari_penyewa(id_penyewa)

    if not penyewa:
        pesan_hasil = f"Penyewa dengan ID '{id_penyewa}' tidak ditemukan."
        return redirect(url_for("index"))

    if request.method == "POST":
        penyewa.nama = request.form["nama"]
        penyewa.no_telepon = request.form["no_telepon"]
        database.update_penyewa(penyewa)
        pesan_hasil = f"Data penyewa berhasil diubah ({penyewa.info()})"
        return redirect(url_for("index"))

    return render_template("edit_penyewa.html", penyewa=penyewa)

@app.route("/penyewa/hapus/<id_penyewa>", methods=["POST"])
def hapus_penyewa(id_penyewa):
    global pesan_hasil
    penyewa = database.cari_penyewa(id_penyewa)

    if not penyewa:
        pesan_hasil = f"Penyewa dengan ID '{id_penyewa}' tidak ditemukan."
    elif database.penyewa_punya_sewa(id_penyewa):
        pesan_hasil = f"{penyewa.nama} tidak bisa dihapus karena masih punya data sewa. Hapus data sewanya dulu."
    else:
        database.hapus_penyewa(id_penyewa)
        pesan_hasil = f"Data penyewa {penyewa.nama} berhasil dihapus."
    return redirect(url_for("index"))

# SEWA
@app.route("/sewa", methods=["POST"])
def sewa_kamar():
    global pesan_hasil
    id_penyewa = request.form["id_penyewa"]
    nomor_kamar = request.form["nomor_kamar"]
    tanggal_mulai = request.form["tanggal_mulai"]
    try:
        durasi_bulan = int(request.form.get("durasi_bulan", ""))
        if durasi_bulan <= 0:
            raise ValueError
    except (TypeError, ValueError):
        pesan_hasil = "Durasi sewa harus berupa angka bulat lebih dari 0."
        return redirect(url_for("index"))

    penyewa_dipilih = database.cari_penyewa(id_penyewa)
    kamar_ditemukan = database.cari_kamar(nomor_kamar)

    if not penyewa_dipilih:
        pesan_hasil = f"Penyewa dengan ID '{id_penyewa}' tidak ditemukan."
        return redirect(url_for("index"))

    if not kamar_ditemukan:
        pesan_hasil = f"Kamar dengan nomor '{nomor_kamar}' tidak ditemukan."
        return redirect(url_for("index"))

    penyewa_dipilih.sewa_kamar(kamar_ditemukan)
    sewa_baru = Sewa(penyewa_dipilih, kamar_ditemukan, tanggal_mulai, durasi_bulan)

    if sewa_baru.proses_sewa():
        database.update_kamar(kamar_ditemukan)
        database.simpan_sewa(sewa_baru)
        pesan_hasil = f"{penyewa_dipilih.nama} berhasil menyewa Kamar {nomor_kamar}. Total: Rp{sewa_baru.hitung_total():,}"
    else:
        pesan_hasil = f"Maaf, Kamar {nomor_kamar} tidak tersedia."

    return redirect(url_for("index"))

@app.route("/checkout/<int:id_sewa>", methods=["POST"])
def checkout(id_sewa):
    global pesan_hasil
    sewa_dipilih = database.cari_sewa(id_sewa)

    if not sewa_dipilih:
        pesan_hasil = "Data sewa tidak ditemukan."
    elif not sewa_dipilih.aktif:
        pesan_hasil = "Sewa ini sudah selesai."
    else:
        sewa_dipilih.penyewa.akhiri_sewa(sewa_dipilih)
        database.update_kamar(sewa_dipilih.kamar)
        database.update_status_sewa(sewa_dipilih)
        pesan_hasil = f"Sewa selesai, Kamar {sewa_dipilih.kamar.nomor_kamar} kembali tersedia."
    return redirect(url_for("index"))

@app.route("/sewa/hapus/<int:id_sewa>", methods=["POST"])
def hapus_sewa(id_sewa):
    global pesan_hasil
    sewa_dipilih = database.cari_sewa(id_sewa)

    if not sewa_dipilih:
        pesan_hasil = "Data sewa tidak ditemukan."
    elif sewa_dipilih.aktif:
        pesan_hasil = "Sewa yang masih aktif tidak bisa dihapus. Akhiri sewa terlebih dahulu."
    else:
        database.hapus_sewa(id_sewa)
        pesan_hasil = "Data sewa beserta pembayarannya berhasil dihapus."
    return redirect(url_for("index"))

# PEMBAYARAN
@app.route("/bayar", methods=["POST"])
def bayar_sewa():
    global pesan_hasil
    try:
        id_sewa = int(request.form.get("id_sewa", ""))
        jumlah = int(request.form.get("jumlah", ""))
    except (TypeError, ValueError):
        pesan_hasil = "ID sewa dan jumlah pembayaran harus berupa angka yang valid."
        return redirect(url_for("index"))

    if jumlah <= 0:
        pesan_hasil = "Jumlah pembayaran harus lebih dari 0."
        return redirect(url_for("index"))

    tanggal_bayar = request.form["tanggal_bayar"]

    sewa_dipilih = database.cari_sewa(id_sewa)

    if not sewa_dipilih:
        pesan_hasil = "Data sewa tidak ditemukan."
        return redirect(url_for("index"))

    if not sewa_dipilih.aktif:
        pesan_hasil = "Pembayaran hanya dapat dicatat untuk sewa yang masih aktif."
        return redirect(url_for("index"))

    try:
        pembayaran_baru = Pembayaran(sewa_dipilih, jumlah, tanggal_bayar)
    except ValueError as e:
        pesan_hasil = str(e)
        return redirect(url_for("index"))

    database.simpan_pembayaran(pembayaran_baru)
    pembayaran_baru.total_dibayar = database.total_pembayaran(id_sewa)
    pembayaran_baru.catat_pembayaran()

    status = "Lunas" if pembayaran_baru.cek_lunas() else "Belum Lunas"
    pesan_hasil = f"Pembayaran {sewa_dipilih.penyewa.nama} sebesar Rp{jumlah:,} dicatat ({status})."
    return redirect(url_for("index"))

@app.route("/pembayaran/hapus/<int:id_pembayaran>", methods=["POST"])
def hapus_pembayaran(id_pembayaran):
    global pesan_hasil
    database.hapus_pembayaran(id_pembayaran)
    pesan_hasil = "Data pembayaran berhasil dihapus."
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)