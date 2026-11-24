from flask import Flask, render_template
from kamar import Kamar

app = Flask(__name__)

daftar_kamar = [
    Kamar("101", "Reguler", 750_000),
    Kamar("102", "VIP AC", 1_200_000),
    Kamar("103", "Reguler", 750_000)
]


@app.route("/")
def index():
    return render_template("index.html", daftar_kamar=daftar_kamar)


if __name__ == "__main__":
    app.run(debug=True)