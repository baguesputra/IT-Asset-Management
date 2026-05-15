from fpdf import FPDF
from datetime import datetime
from collections import Counter
from config import RS_NAMA, RS_ALAMAT

SISTEM_NAMA = "IT Asset Management System"

HITAM      = (0, 0, 0)
PUTIH      = (255, 255, 255)
ABU_GELAP  = (50, 50, 50)
ABU_SEDANG = (100, 100, 100)
ABU_TERANG = (220, 220, 220)
ABU_MUDA   = (245, 245, 245)
GARIS      = (180, 180, 180)

PAGE_W     = 210   # A4 width mm
MARGIN     = 20
CONTENT_W  = PAGE_W - (MARGIN * 2)  # 170mm


class PDFBersih(FPDF):
    def __init__(self, judul_laporan="LAPORAN"):
        super().__init__()
        self.judul_laporan = judul_laporan
        self.set_margins(MARGIN, 28, MARGIN)

    def header(self):
        self.set_y(10)

        # Nama RS
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*ABU_GELAP)
        self.cell(110, 6, RS_NAMA, align="L")

        # Nama sistem (kanan)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*ABU_SEDANG)
        self.cell(0, 6, SISTEM_NAMA, align="R")
        self.ln(6)

        # Alamat
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*ABU_SEDANG)
        self.cell(0, 4, RS_ALAMAT, align="L")
        self.ln(5)

        # Garis tebal
        self.set_draw_color(*ABU_GELAP)
        self.set_line_width(0.8)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())
        self.ln(1)

        # Garis tipis
        self.set_draw_color(*GARIS)
        self.set_line_width(0.2)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())

        self.set_text_color(*HITAM)
        self.set_line_width(0.3)

    def footer(self):
        self.set_y(-13)
        self.set_draw_color(*GARIS)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())
        self.ln(2)

        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*ABU_SEDANG)
        self.cell(60, 5, SISTEM_NAMA, align="L")
        self.cell(60, 5,
            f"Dicetak: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            align="C"
        )
        self.cell(0, 5, f"Halaman {self.page_no()}", align="R")


def _judul_section(pdf, teks):
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(0, 5, teks.upper(), align="L")
    pdf.ln(1)
    pdf.set_draw_color(*ABU_GELAP)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
    pdf.ln(5)
    pdf.set_text_color(*HITAM)
    pdf.set_line_width(0.3)


def _field(pdf, label, nilai, lebar_label=50):
    """Satu baris field — label kiri, nilai kanan."""
    nilai_str = str(nilai).strip() if nilai else "-"

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(lebar_label, 6.5, label, align="L")

    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(6, 6.5, ":", align="C")

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*HITAM)
    # multi_cell untuk nilai panjang — tidak terpotong
    pdf.multi_cell(0, 6.5, nilai_str, align="L")


def _field_dua_kolom(pdf, label1, nilai1, label2, nilai2):
    """Dua field dalam satu baris — lebar kolom sama."""
    lebar_label = 38
    lebar_nilai = 42
    lebar_sep   = 6

    # Kolom kiri
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(lebar_label, 6.5, label1, align="L")
    pdf.cell(lebar_sep, 6.5, ":", align="C")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*HITAM)
    v1 = str(nilai1).strip() if nilai1 else "-"
    pdf.cell(lebar_nilai, 6.5, v1, align="L")

    # Kolom kanan
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(lebar_label, 6.5, label2, align="L")
    pdf.cell(lebar_sep, 6.5, ":", align="C")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*HITAM)
    v2 = str(nilai2).strip() if nilai2 else "-"
    pdf.cell(0, 6.5, v2, align="L")
    pdf.ln()


def _tabel_header(pdf, kolom, lebar_kolom):
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(*ABU_MUDA)
    pdf.set_draw_color(*GARIS)
    pdf.set_text_color(*ABU_GELAP)
    pdf.set_line_width(0.3)

    for i, k in enumerate(kolom):
        pdf.cell(lebar_kolom[i], 7, k, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(*HITAM)


def _tabel_baris(pdf, data, lebar_kolom, zebra=False):
    """
    Baris tabel dengan tinggi dinamis — teks tidak terpotong.
    Pakai multi_cell untuk kolom deskripsi.
    """
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_draw_color(*GARIS)
    pdf.set_line_width(0.3)

    fill_color = (250, 250, 250) if zebra else PUTIH
    pdf.set_fill_color(*fill_color)

    # hitung tinggi baris berdasarkan kolom terpanjang
    tinggi = 6.5

    x_awal = pdf.get_x()
    y_awal = pdf.get_y()

    for i, nilai in enumerate(data):
        teks = str(nilai).strip() if nilai else "-"
        pdf.set_xy(x_awal + sum(lebar_kolom[:i]), y_awal)
        pdf.cell(lebar_kolom[i], tinggi, teks, border=1, fill=True, align="L")

    pdf.set_xy(x_awal, y_awal + tinggi)
    pdf.ln(0)


def _tanda_tangan(pdf):
    """Bagian tanda tangan 3 kolom yang simetris."""
    pdf.ln(10)
    _judul_section(pdf, "Verifikasi & Persetujuan")

    lebar_ttd  = CONTENT_W / 3   # 56.67mm tiap kolom
    tinggi_ttd = 18

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*ABU_SEDANG)

    jabatan = ["Dibuat oleh,", "Diperiksa oleh,", "Disetujui oleh,"]
    nama    = ["Staff IT", "Kepala IT", "Manajemen"]

    x_mulai = MARGIN

    # baris jabatan
    for j in jabatan:
        pdf.cell(lebar_ttd, 5, j, align="C")
    pdf.ln(tinggi_ttd)

    # garis tanda tangan — simetris
    y_garis = pdf.get_y()
    for i in range(3):
        x_start = x_mulai + (i * lebar_ttd) + 8
        x_end   = x_start + lebar_ttd - 16
        pdf.line(x_start, y_garis, x_end, y_garis)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*ABU_GELAP)
    for n in nama:
        pdf.cell(lebar_ttd, 5, n, align="C")
    pdf.ln()

    pdf.set_text_color(*HITAM)


def generate_laporan_asset(asset, riwayat):
    pdf = PDFBersih("LAPORAN ASSET")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Judul ────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*ABU_GELAP)
    pdf.cell(0, 9, "LAPORAN DETAIL ASSET", align="C")
    pdf.ln(8)

    # Info dokumen — di bawah judul, tidak menimpa
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(0, 5,
        f"Nomor Dokumen: {asset.get('id', '-')}     "
        f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}",
        align="C"
    )
    pdf.ln(8)

    # Garis dekoratif di bawah judul
    pdf.set_draw_color(*ABU_TERANG)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN + 30, pdf.get_y(), PAGE_W - MARGIN - 30, pdf.get_y())
    pdf.set_line_width(0.3)
    pdf.ln(6)

    # ── Identitas asset ──────────────────────────────────
    _judul_section(pdf, "Identitas Asset")

    _field_dua_kolom(pdf,
        "ID Asset",  asset.get("id", "-"),
        "Status",    asset.get("status", "-")
    )
    _field(pdf, "Nama Asset",     asset.get("name", "-"))
    _field_dua_kolom(pdf,
        "Jenis Asset", asset.get("type", "-"),
        "Merk / Model", asset.get("brand", "-") or "-"
    )
    _field(pdf, "Serial Number",  asset.get("serial", "-") or "-")

    # ── Penempatan ───────────────────────────────────────
    _judul_section(pdf, "Penempatan & Penanggung Jawab")

    _field_dua_kolom(pdf,
        "Lokasi",        asset.get("location", "-"),
        "PIC",           asset.get("pic", "-")
    )
    _field(pdf,
        "Tanggal Pembelian",
        asset.get("purchase_date", "-") or "-"
    )

    # Catatan
    if asset.get("notes") and asset["notes"].strip():
        _judul_section(pdf, "Catatan")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*HITAM)
        pdf.multi_cell(CONTENT_W, 6, asset["notes"].strip())

    # ── Riwayat servis ───────────────────────────────────
    _judul_section(pdf,
        f"Riwayat Servis  ({len(riwayat)} Catatan)"
    )

    if not riwayat:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*ABU_SEDANG)
        pdf.cell(0, 8, "Belum ada riwayat servis tercatat.", align="C")
        pdf.set_text_color(*HITAM)
    else:
        # lebar kolom total = 170mm
        lebar = [24, 35, 65, 30, 16]
        _tabel_header(pdf,
            ["Tanggal", "Jenis", "Deskripsi", "Teknisi", "Biaya"],
            lebar
        )

        for idx, s in enumerate(riwayat):
            biaya = f"Rp{s['biaya']:,}" if s.get("biaya") else "-"

            # deskripsi — potong di 60 karakter supaya muat
            desk = s.get("deskripsi", "-") or "-"
            if len(desk) > 55:
                desk = desk[:52] + "..."

            _tabel_baris(pdf, [
                s.get("tanggal", "-"),
                s.get("jenis", "-"),
                desk,
                s.get("teknisi", "-"),
                biaya,
            ], lebar, zebra=(idx % 2 == 1))

        # total biaya
        total = sum(s.get("biaya", 0) or 0 for s in riwayat)
        if total > 0:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*ABU_GELAP)
            pdf.cell(0, 6,
                f"Total Biaya Servis: Rp {total:,}",
                align="R"
            )

    # Tanda tangan
    _tanda_tangan(pdf)

    return bytes(pdf.output())


def generate_laporan_semua(assets):
    pdf = PDFBersih("LAPORAN INVENTARIS")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Judul ────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*ABU_GELAP)
    pdf.cell(0, 9, "LAPORAN INVENTARIS ASSET IT", align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*ABU_SEDANG)
    pdf.cell(0, 5,
        f"Per Tanggal: {datetime.now().strftime('%d %B %Y')}     "
        f"Total: {len(assets)} Asset",
        align="C"
    )

    pdf.ln(6)
    pdf.set_draw_color(*ABU_TERANG)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN + 30, pdf.get_y(), PAGE_W - MARGIN - 30, pdf.get_y())
    pdf.set_line_width(0.3)
    pdf.ln(6)

    # ── Ringkasan ────────────────────────────────────────
    _judul_section(pdf, "Ringkasan")

    per_status = Counter(a.get("status", "-") for a in assets)
    per_lokasi = Counter(a.get("location", "-") for a in assets)

    _field_dua_kolom(pdf,
        "Total Asset", str(len(assets)),
        "Aktif",       str(per_status.get("Aktif", 0))
    )
    _field_dua_kolom(pdf,
        "Rusak",      str(per_status.get("Rusak", 0)),
        "Perbaikan",  str(per_status.get("Perbaikan", 0))
    )
    if per_lokasi:
        top = per_lokasi.most_common(1)[0]
        _field(pdf, "Lokasi Terbanyak",
               f"{top[0]} ({top[1]} asset)")

    # ── Daftar asset ─────────────────────────────────────
    _judul_section(pdf, "Daftar Asset")

    # total lebar = 170mm
    lebar = [10, 40, 20, 32, 28, 22, 18]
    _tabel_header(pdf,
        ["No", "Nama Asset", "Jenis", "Merk", "Serial", "Lokasi", "Status"],
        lebar
    )

    for idx, a in enumerate(assets, 1):
        # potong teks panjang
        nama   = a.get("name", "-")
        merk   = (a.get("brand", "-") or "-")[:18]
        serial = (a.get("serial", "-") or "-")[:16]

        _tabel_baris(pdf, [
            str(idx),
            nama,
            a.get("type", "-"),
            merk,
            serial,
            a.get("location", "-"),
            a.get("status", "-"),
        ], lebar, zebra=(idx % 2 == 0))

    # Tanda tangan
    _tanda_tangan(pdf)

    return bytes(pdf.output())