from flask import Flask, render_template, request, redirect, url_for
from kamar import Kamar
from penyewa import Penyewa
from sewa import Sewa

app = Flask(__name__)

daftar_kamar = [
    Kamar("101", "Reguler", 750_000),
    Kamar("102", "VIP AC", 1_200_000),
    Kamar("103", "Reguler", 750_000)
]
daftar_kamar[2].sewakan()

daftar_penyewa = []
daftar_sewa = []
pesan_hasil = ""


@app.route("/")
def index():
    global pesan_hasil
    pesan = pesan_hasil
    pesan_hasil = ""
    return render_template(
        "index.html",
        daftar_kamar=daftar_kamar,
        daftar_penyewa=daftar_penyewa,
        daftar_sewa=daftar_sewa,
        pesan=pesan
    )


@app.route("/penyewa", methods=["POST"])
def input_penyewa():
    global pesan_hasil
    id_penyewa = request.form["id_penyewa"]
    nama = request.form["nama"]
    no_telepon = request.form["no_telepon"]

    penyewa_baru = Penyewa(id_penyewa, nama, no_telepon)
    daftar_penyewa.append(penyewa_baru)
    pesan_hasil = f"Data penyewa tersimpan ({penyewa_baru.info()})"
    return redirect(url_for("index"))


@app.route("/sewa", methods=["POST"])
def sewa_kamar():
    global pesan_hasil
    index_penyewa = int(request.form["index_penyewa"])
    nomor_kamar = request.form["nomor_kamar"]
    tanggal_mulai = request.form["tanggal_mulai"]
    durasi_bulan = int(request.form["durasi_bulan"])

    penyewa_dipilih = daftar_penyewa[index_penyewa]

    kamar_ditemukan = None
    for k in daftar_kamar:
        if k.nomor_kamar == nomor_kamar:
            kamar_ditemukan = k
            break

    if not kamar_ditemukan:
        pesan_hasil = f"Kamar dengan nomor '{nomor_kamar}' tidak ditemukan."
        return redirect(url_for("index"))

    penyewa_dipilih.sewa_kamar(kamar_ditemukan)
    sewa_baru = Sewa(penyewa_dipilih, kamar_ditemukan, tanggal_mulai, durasi_bulan)

    if sewa_baru.proses_sewa():
        daftar_sewa.append(sewa_baru)
        pesan_hasil = f"{penyewa_dipilih.nama} berhasil menyewa Kamar {nomor_kamar}. Total: Rp{sewa_baru.hitung_total():,}"
    else:
        pesan_hasil = f"Maaf, Kamar {nomor_kamar} tidak tersedia."

    return redirect(url_for("index"))


@app.route("/checkout/<int:index_sewa>", methods=["POST"])
def checkout(index_sewa):
    global pesan_hasil
    sewa_dipilih = daftar_sewa[index_sewa]
    sewa_dipilih.penyewa.akhiri_sewa(sewa_dipilih)
    pesan_hasil = f"Sewa selesai, Kamar {sewa_dipilih.kamar.nomor_kamar} kembali tersedia."
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)