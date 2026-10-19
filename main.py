"""
Konverter Mata Uang - GUI Tkinter (lintas platform)
Jalankan: python main.py
Kurs live dari open.er-api.com (gratis, tanpa API key), dengan cache & kurs cadangan offline.
"""
import json
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.request import Request, urlopen

API_URL = "https://open.er-api.com/v6/latest/USD"
CACHE_FILE = Path(__file__).with_name("rates_cache.json")
HISTORY_FILE = Path(__file__).with_name("history.json")
CACHE_TTL = 6 * 3600  # detik

CURRENCY_NAMES = {
    "IDR": "Rupiah Indonesia", "USD": "Dolar AS", "EUR": "Euro",
    "GBP": "Poundsterling", "JPY": "Yen Jepang", "SGD": "Dolar Singapura",
    "MYR": "Ringgit Malaysia", "THB": "Baht Thailand", "AUD": "Dolar Australia",
    "CAD": "Dolar Kanada", "CHF": "Franc Swiss", "CNY": "Yuan Tiongkok",
    "HKD": "Dolar Hong Kong", "KRW": "Won Korea", "INR": "Rupee India",
    "SAR": "Riyal Saudi", "AED": "Dirham UEA", "NZD": "Dolar Selandia Baru",
    "PHP": "Peso Filipina", "VND": "Dong Vietnam", "BRL": "Real Brasil",
    "RUB": "Rubel Rusia", "TRY": "Lira Turki", "ZAR": "Rand Afrika Selatan",
    "MXN": "Peso Meksiko", "SEK": "Krona Swedia", "NOK": "Krone Norwegia",
    "DKK": "Krone Denmark", "PLN": "Zloty Polandia", "TWD": "Dolar Taiwan",
}

# Kurs cadangan (perkiraan kasar, basis USD) bila offline & belum ada cache
FALLBACK_RATES = {
    "USD": 1.0, "IDR": 16500, "EUR": 0.92, "GBP": 0.78, "JPY": 150, "SGD": 1.34,
    "MYR": 4.4, "THB": 34, "AUD": 1.52, "CAD": 1.38, "CHF": 0.88, "CNY": 7.2,
    "HKD": 7.8, "KRW": 1350, "INR": 84, "SAR": 3.75, "AED": 3.67, "NZD": 1.65,
    "PHP": 57, "VND": 25000, "BRL": 5.5, "RUB": 95, "TRY": 34, "ZAR": 18,
    "MXN": 19.5, "SEK": 10.5, "NOK": 10.8, "DKK": 6.9, "PLN": 4.0, "TWD": 32,
}


def fmt_number(value: float, code: str) -> str:
    """Format angka gaya Indonesia: 1.234.567,89"""
    decimals = 0 if code in ("IDR", "JPY", "KRW", "VND") else 2
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def parse_amount(text: str) -> float:
    """Terima '1.000,50' maupun '1000.50'."""
    t = text.strip().replace(" ", "")
    if not t:
        raise ValueError("kosong")
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):   # gaya Indonesia
            t = t.replace(".", "").replace(",", ".")
        else:                              # gaya Inggris
            t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".")
    return float(t)


class RateService:
    def __init__(self):
        self.rates = dict(FALLBACK_RATES)
        self.updated = "Kurs cadangan (offline)"
        self.live = False
        self._load_cache()

    def _load_cache(self):
        try:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            self.rates = data["rates"]
            self.updated = f"Cache: {data['updated']}"
            self.live = True
            self.cache_age = time.time() - data["ts"]
        except Exception:
            self.cache_age = float("inf")

    def needs_refresh(self) -> bool:
        return self.cache_age > CACHE_TTL

    def fetch(self):
        req = Request(API_URL, headers={"User-Agent": "CurrencyConverter/1.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("result") != "success":
            raise RuntimeError("Respons API tidak valid")
        self.rates = data["rates"]
        self.updated = datetime.now().strftime("Live: %d/%m/%Y %H:%M")
        self.live = True
        self.cache_age = 0
        CACHE_FILE.write_text(
            json.dumps({"rates": self.rates, "ts": time.time(), "updated": self.updated}),
            encoding="utf-8",
        )

    def convert(self, amount: float, src: str, dst: str) -> float:
        return amount / self.rates[src] * self.rates[dst]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Konverter Mata Uang")
        self.geometry("560x640")
        self.minsize(520, 600)
        self.service = RateService()
        self.history = self._load_history()
        self._build_style()
        self._build_ui()
        self._render_history()
        if self.service.needs_refresh():
            self.refresh_rates()
        else:
            self._set_status()
        self.bind("<Return>", lambda e: self.convert())

    # ---------- UI ----------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(bg="#f4f6fb")
        style.configure("TFrame", background="#f4f6fb")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f4f6fb", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1f3a8a")
        style.configure("Result.TLabel", background="#ffffff",
                        font=("Segoe UI", 22, "bold"), foreground="#047857")
        style.configure("Sub.TLabel", background="#ffffff", foreground="#6b7280",
                        font=("Segoe UI", 9))
        style.configure("Status.TLabel", foreground="#6b7280", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"),
                        foreground="#ffffff", background="#2563eb", padding=8)
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        style.configure("TButton", padding=6)

    def _build_ui(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="💱 Konverter Mata Uang", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Kurs live • bisa offline • riwayat tersimpan").pack(anchor="w", pady=(0, 10))

        card = ttk.Frame(root, style="Card.TFrame", padding=16)
        card.pack(fill="x")

        ttk.Label(card, text="Jumlah", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.amount_var = tk.StringVar(value="1")
        entry = ttk.Entry(card, textvariable=self.amount_var, font=("Segoe UI", 14))
        entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 12))
        entry.focus()

        codes = sorted(self.service.rates.keys(), key=lambda c: (c not in CURRENCY_NAMES, c))
        labels = [self._label(c) for c in codes]
        self.from_var = tk.StringVar(value=self._label("USD"))
        self.to_var = tk.StringVar(value=self._label("IDR"))

        ttk.Label(card, text="Dari", style="Card.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(card, text="Ke", style="Card.TLabel").grid(row=2, column=2, sticky="w")
        self.from_cb = ttk.Combobox(card, textvariable=self.from_var, values=labels,
                                    state="readonly", width=24)
        self.to_cb = ttk.Combobox(card, textvariable=self.to_var, values=labels,
                                  state="readonly", width=24)
        self.from_cb.grid(row=3, column=0, sticky="ew", pady=2)
        self.to_cb.grid(row=3, column=2, sticky="ew", pady=2)
        ttk.Button(card, text="⇄", width=3, command=self.swap).grid(row=3, column=1, padx=8)
        for cb in (self.from_cb, self.to_cb):
            cb.bind("<<ComboboxSelected>>", lambda e: self.convert())

        card.columnconfigure(0, weight=1)
        card.columnconfigure(2, weight=1)

        ttk.Button(card, text="Konversi", style="Accent.TButton",
                   command=self.convert).grid(row=4, column=0, columnspan=3,
                                              sticky="ew", pady=(14, 8))

        self.result_var = tk.StringVar(value="—")
        self.rate_var = tk.StringVar(value="")
        ttk.Label(card, textvariable=self.result_var, style="Result.TLabel",
                  wraplength=480).grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Label(card, textvariable=self.rate_var, style="Sub.TLabel").grid(
            row=6, column=0, columnspan=3, sticky="w")

        btns = ttk.Frame(card, style="Card.TFrame")
        btns.grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Button(btns, text="📋 Salin hasil", command=self.copy_result).pack(side="left")
        ttk.Button(btns, text="🔄 Perbarui kurs", command=self.refresh_rates).pack(side="left", padx=8)

        ttk.Label(root, text="Riwayat", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(14, 4))
        hist_frame = ttk.Frame(root)
        hist_frame.pack(fill="both", expand=True)
        self.hist_list = tk.Listbox(hist_frame, font=("Consolas", 10), height=8,
                                    borderwidth=0, highlightthickness=1,
                                    highlightbackground="#d1d5db")
        sb = ttk.Scrollbar(hist_frame, command=self.hist_list.yview)
        self.hist_list.configure(yscrollcommand=sb.set)
        self.hist_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        ttk.Button(root, text="Hapus riwayat", command=self.clear_history).pack(anchor="e", pady=(6, 0))

        self.status_var = tk.StringVar()
        ttk.Label(root, textvariable=self.status_var, style="Status.TLabel").pack(anchor="w", pady=(8, 0))

    # ---------- helpers ----------
    @staticmethod
    def _label(code: str) -> str:
        name = CURRENCY_NAMES.get(code)
        return f"{code} — {name}" if name else code

    @staticmethod
    def _code(label: str) -> str:
        return label.split(" ")[0]

    def _set_status(self, extra: str = ""):
        self.status_var.set(f"{self.service.updated}{' • ' + extra if extra else ''}")

    # ---------- actions ----------
    def swap(self):
        a, b = self.from_var.get(), self.to_var.get()
        self.from_var.set(b)
        self.to_var.set(a)
        self.convert()

    def convert(self):
        try:
            amount = parse_amount(self.amount_var.get())
        except ValueError:
            messagebox.showwarning("Input tidak valid", "Masukkan angka yang benar, mis. 1500 atau 1.500,75")
            return
        src, dst = self._code(self.from_var.get()), self._code(self.to_var.get())
        try:
            result = self.service.convert(amount, src, dst)
            unit_rate = self.service.convert(1, src, dst)
        except KeyError:
            messagebox.showerror("Error", "Mata uang tidak tersedia.")
            return
        text = f"{fmt_number(amount, src)} {src} = {fmt_number(result, dst)} {dst}"
        self.result_var.set(text)
        self.rate_var.set(f"1 {src} = {unit_rate:,.6f} {dst}".replace(",", "X").replace(".", ",").replace("X", "."))
        self._add_history(text)

    def copy_result(self):
        text = self.result_var.get()
        if text and text != "—":
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_status("hasil disalin ✔")

    def refresh_rates(self):
        self._set_status("memperbarui kurs…")

        def worker():
            try:
                self.service.fetch()
                self.after(0, lambda: (self._set_status("berhasil diperbarui ✔"),
                                       self.result_var.get() != "—" and self.convert()))
            except Exception as exc:
                self.after(0, lambda: self._set_status(f"gagal update ({type(exc).__name__}), pakai kurs tersimpan"))

        threading.Thread(target=worker, daemon=True).start()

    # ---------- history ----------
    def _load_history(self):
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_history(self):
        try:
            HISTORY_FILE.write_text(json.dumps(self.history[-100:], ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass

    def _add_history(self, text: str):
        stamp = datetime.now().strftime("%H:%M")
        entry = f"[{stamp}] {text}"
        if self.history and self.history[-1].endswith(text):
            return
        self.history.append(entry)
        self._save_history()
        self._render_history()

    def _render_history(self):
        self.hist_list.delete(0, tk.END)
        for item in reversed(self.history[-50:]):
            self.hist_list.insert(tk.END, item)

    def clear_history(self):
        self.history.clear()
        self._save_history()
        self._render_history()


if __name__ == "__main__":
    App().mainloop()
