from datetime import datetime
import uuid

def generate_id():
    return str(uuid.uuid4())[:8].upper()

class Asset:
    def __init__(self, name, asset_type, location, pic):
        self.name     = name
        self.type     = asset_type
        self.location = location
        self.pic      = pic
        self.status   = "Aktif"
        self.id       = generate_id()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        # self di sini = objek yang sedang di-print
        return f"[{self.id}] {self.name} | {self.type} | {self.location} | {self.status}"
    
    def update_status(self, status_baru):
        """Ubah status dan catat waktu update otomatis."""
        self.status     = status_baru
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Konversi objek ke dictionary — untuk disimpan ke JSON."""
        return {
            "id":           self.id,
            "name":         self.name,
            "type":         self.type,
            "location":     self.location,
            "pic":          self.pic,
            "status":       self.status,
            "created_at":   self.created_at,
            "updated_at":   self.updated_at,
        }

# buat dua objek dari blueprint yang sama
pc      = Asset("PC-IGD-01", "PC", "IGD", "Budi")
printer = Asset("PRINTER-FARMASI-01", "Printer", "Farmasi", "Siti")

# akses datanya
print(pc.name)       # PC-IGD-01
print(pc.status)     # Aktif
print(printer.name)  # PRINTER-FARMASI-01
print(pc.id)         # ID unik
print(printer.id)    # ID unik yang BERBEDA
print(pc)
pc.update_status("Rusak")
print(pc)
print(pc.to_dict())
print(pc.updated_at)