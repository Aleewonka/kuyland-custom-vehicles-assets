# Kuyland Custom Vehicles — Public Asset CDN & Auto-Manifest

Repositori **publik** ini berfungsi sebagai CDN gratis berbasis GitHub untuk menghosting aset `.dff` / `.txd` kendaraan kustom dan men-generate file `vehicles.json` secara otomatis via GitHub Actions.

- **CDN Base URL:** `https://raw.githubusercontent.com/Aleewonka/kuyland-custom-vehicles-assets/main/`
- **Raw Manifest URL:** `https://raw.githubusercontent.com/Aleewonka/kuyland-custom-vehicles-assets/main/vehicles.json`

> **Catatan Uji Coba Awal:** File `20001_test_car.*` dan `20002_test_bike.*` saat ini berisi **placeholder bytes** (hanya untuk menguji handshake, unduhan WinHTTP, dan verifikasi cache SHA-256). **Ganti** dengan file `.dff` dan `.txd` mod GTA:SA asli sebelum melakukan spawn visual di dalam game.

---

## Cara Menambah / Mengganti Model Kendaraan Custom

1. Upload file `.dff` dan `.txd` mod kendaraan GTA:SA Anda ke folder `vehicles/` (batas ukuran GitHub per file: `< 100 MB`, idealnya `< 25 MB` agar cepat diunduh pemain).
2. Edit file `catalog.json` — cukup isi `virtualModelId` (`>= 20000`), `baseModelId` (`400–611`), `vehicleClass` (`automobile` / `bike` / `bmx`), `dffPath`, `txdPath`, dan optional `handling`/`bikeHandling` (**tidak perlu** menghitung SHA-256 atau ukuran byte secara manual).
3. Commit & push ke branch `main` (atau simpan langsung lewat GitHub Web UI).
4. **GitHub Actions** (`Generate vehicles.json Manifest`) akan otomatis menghitung SHA-256 + ukuran byte asli setiap file, memvalidasi kesesuaian kelas kendaraan, dan meng-commit `vehicles.json` terbaru dalam ~10 detik.
5. Unduh `vehicles.json` terbaru ke server open.mp (`config/vehicles.json`):
   ```powershell
   Invoke-WebRequest "https://raw.githubusercontent.com/Aleewonka/kuyland-custom-vehicles-assets/main/vehicles.json" -OutFile "config/vehicles.json"
   ```
   atau di Linux:
   ```bash
   curl -fsSL "https://raw.githubusercontent.com/Aleewonka/kuyland-custom-vehicles-assets/main/vehicles.json" -o config/vehicles.json
   ```
6. Jalankan `/kcvreload` (`ReloadCustomVehicles()`) di server open.mp tanpa perlu restart server!
