# app/models/asset.py
# Tanggung jawab: mendefinisikan bentuk data Asset.
# File ini TIDAK boleh berisi logika bisnis —
# hanya struktur data dan konversi.

import uuid
from datetime import datetime
from typing import Optional


def generate_id() -> str:
    """Generate ID unik 8 karakter."""
    return str(uuid.uuid4())[:8].upper()


class Asset:
    """
    Representasi satu unit asset IT.
    Berisi data asset dan method konversi —
    bukan logika bisnis seperti save atau delete.
    """

    def __init__(
    self,
    name: str,
    asset_type: str,
    brand: str,
    serial: str,
    purchase_date: str,
    location: str,
    pic: str,
    notes: str = "",
    status: str = "Aktif",
    # field baru — garansi & vendor
    harga_beli: int = 0,
    vendor: str = "",
    no_kontrak: str = "",
    masa_garansi_bulan: int = 0,
    tgl_garansi_mulai: str = "",
    ) -> None:
        self.name               = name
        self.type               = asset_type
        self.brand              = brand
        self.serial             = serial
        self.purchase_date      = purchase_date
        self.location           = location
        self.pic                = pic
        self.notes              = notes
        self.status             = status
        self.harga_beli         = harga_beli
        self.vendor             = vendor
        self.no_kontrak         = no_kontrak
        self.masa_garansi_bulan = masa_garansi_bulan
        self.tgl_garansi_mulai  = tgl_garansi_mulai

        self.id         = generate_id()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} | {self.type} | {self.location} | {self.status}"

    def update_status(self, status_baru: str) -> None:
        self.status     = status_baru
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "name":              self.name,
            "type":              self.type,
            "brand":             self.brand,
            "serial":            self.serial,
            "purchase_date":     self.purchase_date,
            "location":          self.location,
            "pic":               self.pic,
            "notes":             self.notes,
            "status":            self.status,
            "harga_beli":        self.harga_beli,
            "vendor":            self.vendor,
            "no_kontrak":        self.no_kontrak,
            "masa_garansi_bulan": self.masa_garansi_bulan,
            "tgl_garansi_mulai": self.tgl_garansi_mulai,
            "created_at":        self.created_at,
            "updated_at":        self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        asset = cls(
            name               = data["name"],
            asset_type         = data["type"],
            brand              = data.get("brand", ""),
            serial             = data.get("serial", ""),
            purchase_date      = data.get("purchase_date", ""),
            location           = data["location"],
            pic                = data["pic"],
            notes              = data.get("notes", ""),
            status             = data.get("status", "Aktif"),
            harga_beli         = data.get("harga_beli", 0) or 0,
            vendor             = data.get("vendor", "") or "",
            no_kontrak         = data.get("no_kontrak", "") or "",
            masa_garansi_bulan = data.get("masa_garansi_bulan", 0) or 0,
            tgl_garansi_mulai  = data.get("tgl_garansi_mulai", "") or "",
        )
        asset.id         = data["id"]
        asset.created_at = data["created_at"]
        asset.updated_at = data["updated_at"]
        return asset