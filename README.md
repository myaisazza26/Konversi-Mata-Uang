# 💱 Konverter Mata Uang (Python + Tkinter)

Aplikasi desktop GUI lintas platform (Windows / macOS / Linux) untuk Visual Studio Code.

## Fitur
- Kurs live dari `open.er-api.com` (gratis, tanpa API key), 160+ mata uang
- Cache 6 jam + kurs cadangan saat offline
- Tombol tukar (⇄), salin hasil, perbarui kurs manual
- Format angka Indonesia (1.234.567,89) dan input fleksibel
- Riwayat konversi tersimpan otomatis (`history.json`)
- Tekan **Enter** untuk konversi

## Cara menjalankan di VS Code
1. Install Python 3.8+ dan ekstensi **Python** (Microsoft) di VS Code.
2. Buka folder ini: `File > Open Folder`.
3. Buka `main.py`, lalu tekan **F5** (atau tombol ▶ Run), atau di terminal:
   ```
   python main.py
   ```
   (macOS/Linux: `python3 main.py`)

## Membuat file .exe / aplikasi (opsional)
```
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```
Hasilnya ada di folder `dist/`.

## Struktur
```
main.py              # seluruh kode aplikasi
requirements.txt
.vscode/launch.json  # konfigurasi F5 VS Code
```
