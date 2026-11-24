from flask import Flask, render_template, request, redirect, url_for
from kamar import Kamar
from penyewa import Penyewa

app = Flask(__name__)

daftar_kamar = [
    Kamar("101", "Reguler", 750_000),
    Kamar("102", "VIP AC", 1_200_000),
    Kamar("103", "Reguler", 750_000)
]
daftar_kamar[2].sewakan()

daftar_penyewa = []
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


@app.route("/cek", methods=["POST"])
def cek_kamar():
    global pesan_hasil
    cari_nomor = request.form["nomor_kamar"]

    kamar_ditemukan = None
    for k in daftar_kamar:
        if k.nomor_kamar == cari_nomor:
            kamar_ditemukan = k
            break

    if kamar_ditemukan:
        if kamar_ditemukan.tersedia():
            pesan_hasil = f"Kamar {kamar_ditemukan.nomor_kamar} ({kamar_ditemukan.tipe}) masih tersedia."
        else:
            pesan_hasil = f"Maaf, Kamar {kamar_ditemukan.nomor_kamar} tidak tersedia."
    else:
        pesan_hasil = f"Kamar dengan nomor '{cari_nomor}' tidak ditemukan."

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)