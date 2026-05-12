# app/services/pdf_service.py
# Tanggung jawab: generate file PDF laporan asset.

from fpdf import FPDF
from datetime import datetime
from typing import Optional


class LaporanAsset(FPDF):
    """
    Class turunan dari FPDF.
    Kita override method header() dan footer()
    supaya muncul otomatis di setiap halaman.

    Ini contoh inheritance OOP — LaporanAsset
    mewarisi semua method FPDF, lalu kita
    tambahkan/override yang kita butuhkan.
    """

    def header(self):
        """Otomatis dipanggil di awal setiap halaman."""
        # font: Arial, Bold, 12pt
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(30, 30, 30)      # warna background gelap
        self.set_text_color(255, 255, 255)   # teks putih

        # cell(lebar, tinggi, teks, border, ln, align, fill)
        self.cell(0, 10, "IT Asset Management System", fill=True, align="C")
        self.ln(5)

        # reset warna
        self.set_text_color(0, 0, 0)

    def footer(self):
        """Otomatis dipanggil di akhir setiap halaman."""
        # posisi 15mm dari bawah
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)

        # nomor halaman
        self.cell(0, 10,
            f"Halaman {self.page_no()} | Dicetak: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            align="C"
        )


def generate_laporan_asset(asset: dict, riwayat: list) -> bytes:
    """
    Generate PDF laporan untuk satu asset.

    Parameter:
        asset   → dictionary data asset
        riwayat → list riwayat servis

    Return:
        bytes → isi file PDF, siap dikirim ke browser
    """
    pdf = LaporanAsset()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Judul laporan ─────────────────────────────
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "LAPORAN ASSET IT", align="C")
    pdf.ln(12)

    # ── Informasi asset ───────────────────────────
    _section_title(pdf, "Informasi Asset")

    fields = [
        ("ID Asset",           asset.get("id", "-")),
        ("Nama Asset",         asset.get("name", "-")),
        ("Jenis",              asset.get("type", "-")),
        ("Merk / Model",       asset.get("brand", "-") or "-"),
        ("Serial Number",      asset.get("serial", "-") or "-"),
        ("Tanggal Pembelian",  asset.get("purchase_date", "-") or "-"),
        ("Lokasi",             asset.get("location", "-")),
        ("PIC",                asset.get("pic", "-")),
        ("Status",             asset.get("status", "-")),
        ("Catatan",            asset.get("notes", "-") or "-"),
        ("Dibuat",             asset.get("created_at", "-")),
        ("Terakhir Update",    asset.get("updated_at", "-")),
    ]

    for label, nilai in fields:
        _row_field(pdf, label, nilai)

    pdf.ln(8)

    # ── Riwayat servis ────────────────────────────
    _section_title(pdf, f"Riwayat Servis ({len(riwayat)} catatan)")

    if not riwayat:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 8, "Belum ada riwayat servis.", align="C")
        pdf.set_text_color(0, 0, 0)
    else:
        # header tabel
        _tabel_header(pdf, ["Tanggal", "Jenis", "Deskripsi", "Teknisi", "Biaya"])

        # baris data
        for s in riwayat:
            biaya = f"Rp {s['biaya']:,}" if s.get("biaya") else "-"
            _tabel_row(pdf, [
                s.get("tanggal", "-"),
                s.get("jenis", "-"),
                s.get("deskripsi", "-"),
                s.get("teknisi", "-"),
                biaya,
            ])

        # total biaya
        total = sum(s.get("biaya", 0) for s in riwayat)
        if total > 0:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 8,
                f"Total Biaya Servis: Rp {total:,}",
                align="R"
            )

    # return sebagai bytes
    # "S" = return string (bytes), bukan simpan ke file
    return bytes(pdf.output())


def generate_laporan_semua(assets: list) -> bytes:
    """
    Generate PDF laporan semua asset dalam satu file.
    Cocok untuk laporan bulanan ke manajemen.
    """
    pdf = LaporanAsset()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # judul
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "LAPORAN INVENTARIS ASSET IT", align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 8,
        f"Total: {len(assets)} asset | Dicetak: {datetime.now().strftime('%d %B %Y')}",
        align="C"
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # ringkasan per status
    _section_title(pdf, "Ringkasan Status")

    from collections import Counter
    per_status = Counter(a.get("status", "-") for a in assets)
    for status, jumlah in per_status.most_common():
        _row_field(pdf, status, str(jumlah) + " asset")

    pdf.ln(8)

    # tabel semua asset
    _section_title(pdf, "Daftar Asset")
    _tabel_header(pdf, ["ID", "Nama", "Jenis", "Lokasi", "Status", "PIC"])

    for a in assets:
        _tabel_row(pdf, [
            a.get("id", "-"),
            a.get("name", "-"),
            a.get("type", "-"),
            a.get("location", "-"),
            a.get("status", "-"),
            a.get("pic", "-"),
        ])

    return bytes(pdf.output())


# ── Helper functions internal ─────────────────────

def _section_title(pdf: FPDF, title: str) -> None:
    """Buat judul section dengan background abu."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, f"  {title}", fill=True)
    pdf.ln(6)
    pdf.set_fill_color(255, 255, 255)


def _row_field(pdf: FPDF, label: str, nilai: str) -> None:
    """Buat satu baris label: nilai."""
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(55, 7, label)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f": {nilai}")
    pdf.ln()


def _tabel_header(pdf: FPDF, kolom: list) -> None:
    """Buat header tabel."""
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)

    # lebar kolom — dibagi rata
    lebar = 190 / len(kolom)
    for k in kolom:
        pdf.cell(lebar, 7, k, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)


def _tabel_row(pdf: FPDF, data: list) -> None:
    """Buat satu baris tabel."""
    pdf.set_font("Helvetica", "", 9)
    lebar = 190 / len(data)

    # warna selang-seling (zebra striping)
    # page_no() dan get_y() untuk cek posisi
    for i, nilai in enumerate(data):
        # truncate teks panjang supaya tidak overflow
        teks = str(nilai)
        if len(teks) > 25:
            teks = teks[:22] + "..."
        pdf.cell(lebar, 6, teks, border=1)
    pdf.ln()