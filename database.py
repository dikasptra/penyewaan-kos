import sqlite3
from kamar import Kamar
from penyewa import Penyewa
from sewa import Sewa
from pembayaran import Pembayaran

NAMA_DB = "kos.db"

def koneksi():
    conn = sqlite3.connect(NAMA_DB)
    conn.row_factory = sqlite3.Row
    return conn

def buat_tabel():
    conn = koneksi()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kamar (
            nomor_kamar TEXT PRIMARY KEY,
            tipe TEXT NOT NULL,
            harga_per_bulan INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS penyewa (
            id_penyewa TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            no_telepon TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sewa (
            id_sewa INTEGER PRIMARY KEY AUTOINCREMENT,
            id_penyewa TEXT NOT NULL,
            nomor_kamar TEXT NOT NULL,
            tanggal_mulai TEXT NOT NULL,
            durasi_bulan INTEGER NOT NULL,
            aktif INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pembayaran (
            id_pembayaran INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sewa INTEGER NOT NULL,
            jumlah INTEGER NOT NULL,
            tanggal_bayar TEXT NOT NULL
        )
    """)

    jumlah_kamar = conn.execute("SELECT COUNT(*) FROM kamar").fetchone()[0]
    if jumlah_kamar == 0:
        conn.execute("INSERT INTO kamar VALUES (?, ?, ?, ?)", ("101", "Reguler", 750000, "tersedia"))
        conn.execute("INSERT INTO kamar VALUES (?, ?, ?, ?)", ("102", "VIP AC", 1200000, "tersedia"))
        conn.execute("INSERT INTO kamar VALUES (?, ?, ?, ?)", ("103", "Reguler", 750000, "tersedia"))

    conn.execute("""
        UPDATE kamar
        SET status = CASE
            WHEN EXISTS (
                SELECT 1 FROM sewa
                WHERE sewa.nomor_kamar = kamar.nomor_kamar AND sewa.aktif = 1
            ) THEN 'disewa'
            ELSE 'tersedia'
        END
    """)

    conn.commit()
    conn.close()

# KAMAR
def buat_objek_kamar(row):
    return Kamar(row["nomor_kamar"], row["tipe"], row["harga_per_bulan"], row["status"])

def ambil_semua_kamar():
    conn = koneksi()
    rows = conn.execute("SELECT * FROM kamar ORDER BY nomor_kamar").fetchall()
    conn.close()
    return [buat_objek_kamar(r) for r in rows]

def cari_kamar(nomor_kamar):
    conn = koneksi()
    row = conn.execute("SELECT * FROM kamar WHERE nomor_kamar = ?", (nomor_kamar,)).fetchone()
    conn.close()
    if row is None:
        return None
    return buat_objek_kamar(row)

def simpan_kamar(kamar):
    conn = koneksi()
    try:
        conn.execute(
            "INSERT INTO kamar VALUES (?, ?, ?, ?)",
            (kamar.nomor_kamar, kamar.tipe, kamar.harga_per_bulan, kamar.status)
        )
        conn.commit()
        berhasil = True
    except sqlite3.IntegrityError:
        berhasil = False
    conn.close()
    return berhasil

def update_kamar(kamar):
    conn = koneksi()
    conn.execute(
        "UPDATE kamar SET tipe = ?, harga_per_bulan = ?, status = ? WHERE nomor_kamar = ?",
        (kamar.tipe, kamar.harga_per_bulan, kamar.status, kamar.nomor_kamar)
    )
    conn.commit()
    conn.close()

def hapus_kamar(nomor_kamar):
    conn = koneksi()
    conn.execute("DELETE FROM kamar WHERE nomor_kamar = ?", (nomor_kamar,))
    conn.commit()
    conn.close()

def kamar_punya_sewa(nomor_kamar):
    conn = koneksi()
    jumlah = conn.execute("SELECT COUNT(*) FROM sewa WHERE nomor_kamar = ?", (nomor_kamar,)).fetchone()[0]
    conn.close()
    return jumlah > 0

# PENYEWA
def buat_objek_penyewa(row):
    return Penyewa(row["id_penyewa"], row["nama"], row["no_telepon"])

def ambil_semua_penyewa():
    conn = koneksi()
    rows = conn.execute("SELECT * FROM penyewa ORDER BY nama").fetchall()
    conn.close()
    return [buat_objek_penyewa(r) for r in rows]

def cari_penyewa(id_penyewa):
    conn = koneksi()
    row = conn.execute("SELECT * FROM penyewa WHERE id_penyewa = ?", (id_penyewa,)).fetchone()
    conn.close()
    if row is None:
        return None
    return buat_objek_penyewa(row)

def simpan_penyewa(penyewa):
    conn = koneksi()
    try:
        conn.execute(
            "INSERT INTO penyewa VALUES (?, ?, ?)",
            (penyewa.id_penyewa, penyewa.nama, penyewa.no_telepon)
        )
        conn.commit()
        berhasil = True
    except sqlite3.IntegrityError:
        berhasil = False
    conn.close()
    return berhasil

def update_penyewa(penyewa):
    conn = koneksi()
    conn.execute(
        "UPDATE penyewa SET nama = ?, no_telepon = ? WHERE id_penyewa = ?",
        (penyewa.nama, penyewa.no_telepon, penyewa.id_penyewa)
    )
    conn.commit()
    conn.close()

def hapus_penyewa(id_penyewa):
    conn = koneksi()
    conn.execute("DELETE FROM penyewa WHERE id_penyewa = ?", (id_penyewa,))
    conn.commit()
    conn.close()

def penyewa_punya_sewa(id_penyewa):
    conn = koneksi()
    jumlah = conn.execute("SELECT COUNT(*) FROM sewa WHERE id_penyewa = ?", (id_penyewa,)).fetchone()[0]
    conn.close()
    return jumlah > 0

# SEWA 
def buat_objek_sewa(row):
    penyewa = cari_penyewa(row["id_penyewa"])
    kamar = cari_kamar(row["nomor_kamar"])
    return Sewa(penyewa, kamar, row["tanggal_mulai"], row["durasi_bulan"], bool(row["aktif"]), row["id_sewa"])

def ambil_semua_sewa():
    conn = koneksi()
    rows = conn.execute("SELECT * FROM sewa ORDER BY id_sewa").fetchall()
    conn.close()
    return [buat_objek_sewa(r) for r in rows]

def cari_sewa(id_sewa):
    conn = koneksi()
    row = conn.execute("SELECT * FROM sewa WHERE id_sewa = ?", (id_sewa,)).fetchone()
    conn.close()
    if row is None:
        return None
    return buat_objek_sewa(row)

def simpan_sewa(sewa):
    conn = koneksi()
    conn.execute(
        "INSERT INTO sewa (id_penyewa, nomor_kamar, tanggal_mulai, durasi_bulan, aktif) VALUES (?, ?, ?, ?, ?)",
        (sewa.penyewa.id_penyewa, sewa.kamar.nomor_kamar, sewa.tanggal_mulai, sewa.durasi_bulan, 1 if sewa.aktif else 0)
    )
    conn.commit()
    conn.close()

def update_status_sewa(sewa):
    conn = koneksi()
    conn.execute("UPDATE sewa SET aktif = ? WHERE id_sewa = ?", (1 if sewa.aktif else 0, sewa.id_sewa))
    conn.commit()
    conn.close()

def hapus_sewa(id_sewa):
    conn = koneksi()
    conn.execute("DELETE FROM pembayaran WHERE id_sewa = ?", (id_sewa,))
    conn.execute("DELETE FROM sewa WHERE id_sewa = ?", (id_sewa,))
    conn.commit()
    conn.close()

# PEMBAYARAN
def buat_objek_pembayaran(row):
    sewa = cari_sewa(row["id_sewa"])
    return Pembayaran(
        sewa,
        row["jumlah"],
        row["tanggal_bayar"],
        row["id_pembayaran"],
        row["total_dibayar"]
    )

def ambil_semua_pembayaran():
    conn = koneksi()
    rows = conn.execute("""
        SELECT pembayaran.*,
               (SELECT COALESCE(SUM(p2.jumlah), 0)
                FROM pembayaran AS p2
                WHERE p2.id_sewa = pembayaran.id_sewa) AS total_dibayar
        FROM pembayaran
        ORDER BY id_pembayaran
    """).fetchall()
    conn.close()
    return [buat_objek_pembayaran(r) for r in rows]

def total_pembayaran(id_sewa):
    conn = koneksi()
    total = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) FROM pembayaran WHERE id_sewa = ?",
        (id_sewa,)
    ).fetchone()[0]
    conn.close()
    return total

def simpan_pembayaran(pembayaran):
    conn = koneksi()
    conn.execute(
        "INSERT INTO pembayaran (id_sewa, jumlah, tanggal_bayar) VALUES (?, ?, ?)",
        (pembayaran.sewa.id_sewa, pembayaran.jumlah, pembayaran.tanggal_bayar)
    )
    conn.commit()
    conn.close()

def hapus_pembayaran(id_pembayaran):
    conn = koneksi()
    conn.execute("DELETE FROM pembayaran WHERE id_pembayaran = ?", (id_pembayaran,))
    conn.commit()
    conn.close()