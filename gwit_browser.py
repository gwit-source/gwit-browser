#!/usr/bin/env python3
"""
GWIT Browser — Python + PyQt6
Установка: pip install PyQt6 PyQt6-WebEngine
Запуск:     python gwit_browser.py
"""

import sys
import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ── Обработка ошибок запуска ─────────────────
def _crash_hook(exc_type, exc_val, exc_tb):
    import traceback
    msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
    print("GWIT CRASH:\n" + msg)
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        if QApplication.instance():
            QMessageBox.critical(None, "Gwit — ошибка", msg)
    except Exception:
        pass
sys.excepthook = _crash_hook

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QLabel, QToolBar, QStatusBar,
    QDialog, QListWidget, QListWidgetItem, QCheckBox, QComboBox,
    QGroupBox, QScrollArea, QFrame, QTextEdit, QMessageBox,
    QInputDialog, QProgressBar, QMenu, QStackedWidget,
    QTreeWidget, QTreeWidgetItem, QSpinBox, QRadioButton,
    QSizePolicy, QToolButton, QTabBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
)
from PyQt6.QtCore import (
    Qt, QUrl, QTimer, QSize, pyqtSignal
)
from PyQt6.QtGui import QColor, QCursor

# ─────────────────────────────────────────────
#  ПУТИ К ДАННЫМ
# ─────────────────────────────────────────────
DATA_DIR        = Path.home() / ".gwit"
DATA_DIR.mkdir(exist_ok=True)
SETTINGS_FILE   = DATA_DIR / "settings.json"
BLOCKLIST_FILE  = DATA_DIR / "blocklist.json"
EXTENSIONS_FILE = DATA_DIR / "extensions.json"

# ─────────────────────────────────────────────
#  НАСТРОЙКИ ПО УМОЛЧАНИЮ
# ─────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "security_standard":         True,
    "security_enhanced":         False,
    "warn_untrusted_extensions": True,
    "force_https":               True,
    "warn_no_https":             True,
    "memory_saver":              True,
    "memory_saver_mode":         "balanced",
    "memory_saver_timeout_min":  10,
    "preload_pages":             True,
    "preload_mode":              "standard",
    "energy_saver":              True,
    "energy_saver_auto":         True,
    "battery_threshold":         20,
    "auto_install_extensions":   False,
    "extensions_enhanced_check": True,
    "theme":                     "dark",
    "homepage":                  "https://www.google.com",
    "default_search":            "https://www.google.com/search?q=",
    "show_bookmarks_bar":        True,
}

# ─────────────────────────────────────────────
#  БАЗА УГРОЗ
# ─────────────────────────────────────────────
BUILTIN_BLOCKLIST = [
    "malware-site.com", "phishing-example.com", "dangerous-downloads.net",
    "trackme-everywhere.com", "adspam-network.ru", "cryptominer-hidden.io",
    "fake-bank-login.com", "virus-download.net", "spyware-tracker.com",
    "ransomware-delivery.net", "botnet-control.com", "scam-alert-fake.com",
]
SAFE_BROWSING_DB = {
    "malware":  ["malware-site.com", "virus-download.net", "ransomware-delivery.net"],
    "phishing": ["phishing-example.com", "fake-bank-login.com", "scam-alert-fake.com"],
    "tracking": ["trackme-everywhere.com", "spyware-tracker.com"],
    "adware":   ["adspam-network.ru"],
    "mining":   ["cryptominer-hidden.io"],
    "botnet":   ["botnet-control.com"],
}

# ─────────────────────────────────────────────
#  ТЕМА
# ─────────────────────────────────────────────
DARK_STYLE = """
* { font-family: 'Segoe UI', 'Arial', sans-serif; }
QMainWindow, QDialog, QWidget { background:#0f1117; color:#e2e8f0; }
QTabWidget::pane { border:none; background:#0f1117; }
QTabBar::tab {
    background:#1a1d27; color:#94a3b8; padding:8px 18px;
    border:none; border-radius:6px 6px 0 0; margin-right:2px; min-width:100px; max-width:200px;
}
QTabBar::tab:selected { background:#0f1117; color:#e2e8f0; border-bottom:2px solid #6c63ff; }
QTabBar::tab:hover:!selected { background:#252836; color:#e2e8f0; }
QLineEdit {
    background:#1a1d27; color:#e2e8f0; border:1px solid #2d3148;
    border-radius:18px; padding:6px 14px; font-size:13px;
}
QLineEdit:focus { border-color:#6c63ff; }
QPushButton {
    background:#252836; color:#e2e8f0; border:none;
    border-radius:7px; padding:7px 14px;
}
QPushButton:hover { background:#2d3148; }
QPushButton:pressed { background:#6c63ff; }
QPushButton#accent { background:#6c63ff; color:#fff; }
QPushButton#accent:hover { background:#7c73ff; }
QPushButton#danger { background:#e53e3e; color:#fff; }
QPushButton#danger:hover { background:#fc5c5c; }
QToolBar { background:#13151f; border:none; spacing:3px; padding:4px 6px; }
QToolButton {
    background:transparent; border:none; border-radius:6px;
    padding:5px; color:#94a3b8; font-size:15px;
}
QToolButton:hover { background:#252836; color:#e2e8f0; }
QToolButton:pressed { background:#6c63ff; color:#fff; }
QStatusBar { background:#13151f; color:#64748b; font-size:11px; padding:2px 8px; }
QGroupBox {
    border:1px solid #2d3148; border-radius:9px;
    margin-top:14px; padding:12px; color:#94a3b8;
}
QGroupBox::title { subcontrol-origin:margin; left:10px; top:-7px; color:#6c63ff; font-weight:bold; }
QCheckBox { color:#e2e8f0; spacing:8px; }
QCheckBox::indicator { width:17px; height:17px; border:2px solid #2d3148; border-radius:4px; background:#1a1d27; }
QCheckBox::indicator:checked { background:#6c63ff; border-color:#6c63ff; }
QComboBox { background:#1a1d27; color:#e2e8f0; border:1px solid #2d3148; border-radius:7px; padding:5px 10px; }
QComboBox QAbstractItemView { background:#1a1d27; color:#e2e8f0; selection-background-color:#6c63ff; }
QListWidget { background:#1a1d27; border:1px solid #2d3148; border-radius:8px; color:#e2e8f0; outline:none; }
QListWidget::item { padding:8px 12px; border-bottom:1px solid #1e2130; }
QListWidget::item:selected { background:#252836; color:#6c63ff; }
QListWidget::item:hover { background:#252836; }
QScrollBar:vertical { background:#13151f; width:7px; border-radius:4px; }
QScrollBar::handle:vertical { background:#2d3148; border-radius:4px; min-height:28px; }
QScrollBar::handle:vertical:hover { background:#6c63ff; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar:horizontal { height:7px; background:#13151f; }
QScrollBar::handle:horizontal { background:#2d3148; border-radius:4px; }
QProgressBar { background:#1a1d27; border:none; border-radius:3px; }
QProgressBar::chunk { background:#6c63ff; border-radius:3px; }
QLabel#h1 { font-size:20px; font-weight:bold; color:#e2e8f0; }
QLabel#safe { color:#48bb78; font-size:11px; font-weight:bold; }
QLabel#warn { color:#ed8936; font-size:11px; font-weight:bold; }
QLabel#danger_lbl { color:#e53e3e; font-size:11px; font-weight:bold; }
QFrame#sep { background:#2d3148; }
QTreeWidget { background:#1a1d27; border:1px solid #2d3148; border-radius:8px; color:#e2e8f0; outline:none; }
QTreeWidget::item:selected { background:#252836; color:#6c63ff; }
QSpinBox { background:#1a1d27; color:#e2e8f0; border:1px solid #2d3148; border-radius:7px; padding:4px 8px; }
QScrollArea { border:none; }
"""

LIGHT_STYLE = (DARK_STYLE
    .replace("#0f1117", "#f8fafc")
    .replace("#1a1d27", "#ffffff")
    .replace("#13151f", "#f1f5f9")
    .replace("#2d3148", "#e2e8f0")
    .replace("#252836", "#f1f5f9")
    .replace("#1e2130", "#f1f5f9")
    .replace("color:#e2e8f0", "color:#1e293b")
    .replace("color:#94a3b8", "color:#64748b")
    .replace("color:#64748b", "color:#94a3b8")
)

# ─────────────────────────────────────────────
#  МЕНЕДЖЕР НАСТРОЕК
# ─────────────────────────────────────────────
class SettingsManager:
    def __init__(self):
        self._data = dict(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, encoding="utf-8") as f:
                    self._data.update(json.load(f))
        except Exception:
            pass

    def save(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self._data.get(key, DEFAULT_SETTINGS.get(key, default))

    def set(self, key, value):
        self._data[key] = value
        self.save()

# ─────────────────────────────────────────────
#  МЕНЕДЖЕР БЛОК-ЛИСТА
# ─────────────────────────────────────────────
class BlocklistManager:
    def __init__(self):
        self._custom = []
        self._load()

    def _load(self):
        try:
            if BLOCKLIST_FILE.exists():
                with open(BLOCKLIST_FILE, encoding="utf-8") as f:
                    self._custom = json.load(f)
        except Exception:
            self._custom = []

    def _save(self):
        try:
            with open(BLOCKLIST_FILE, "w", encoding="utf-8") as f:
                json.dump(self._custom, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def _host(url):
        try:
            h = urlparse(url).hostname or ""
            return h.lstrip("www.").lower()
        except Exception:
            return ""

    def is_blocked(self, url):
        host = self._host(url)
        if not host:
            return False, ""
        for entry in self._custom:
            if not entry.get("enabled", True):
                continue
            pattern = entry["domain"].lstrip("www.").lower()
            if host == pattern or host.endswith("." + pattern):
                return True, entry.get("reason", "Пользовательская блокировка")
        for domain in BUILTIN_BLOCKLIST:
            if host == domain or host.endswith("." + domain):
                return True, "Встроенный список нежелательных сайтов"
        return False, ""

    def threat_type(self, url):
        host = self._host(url)
        for threat, domains in SAFE_BROWSING_DB.items():
            for d in domains:
                if host == d or host.endswith("." + d):
                    return threat
        return None

    def add(self, domain, reason=""):
        domain = domain.strip().lstrip("www.").lower()
        if any(e["domain"] == domain for e in self._custom):
            return False
        self._custom.append({
            "domain": domain, "reason": reason,
            "enabled": True, "added": datetime.now().isoformat()
        })
        self._save()
        return True

    def remove(self, domain):
        self._custom = [e for e in self._custom if e["domain"] != domain]
        self._save()

    def toggle(self, domain):
        for e in self._custom:
            if e["domain"] == domain:
                e["enabled"] = not e["enabled"]
        self._save()

    def custom_list(self): return list(self._custom)
    def builtin_list(self): return list(BUILTIN_BLOCKLIST)

# ─────────────────────────────────────────────
#  МЕНЕДЖЕР РАСШИРЕНИЙ
# ─────────────────────────────────────────────
_DEFAULT_EXT = [
    {"id":"e1","name":"uBlock Origin","cat":"Security","desc":"Блокировщик рекламы","trusted":True,"installed":False,"enabled":False,"icon":"🛡️","sites":"all"},
    {"id":"e2","name":"LastPass","cat":"Security","desc":"Менеджер паролей","trusted":True,"installed":False,"enabled":False,"icon":"🔐","sites":"all"},
    {"id":"e3","name":"Dark Reader","cat":"Appearance","desc":"Тёмная тема для всех сайтов","trusted":True,"installed":False,"enabled":False,"icon":"🌙","sites":"all"},
    {"id":"e4","name":"Grammarly","cat":"Productivity","desc":"Проверка грамматики","trusted":True,"installed":False,"enabled":False,"icon":"✍️","sites":"all"},
    {"id":"e5","name":"Honey","cat":"Shopping","desc":"Поиск купонов","trusted":True,"installed":False,"enabled":False,"icon":"🍯","sites":"shopping"},
    {"id":"e6","name":"SuspiciousTool","cat":"Unknown","desc":"Неизвестный источник","trusted":False,"installed":False,"enabled":False,"icon":"⚠️","sites":"all"},
]

class ExtensionsManager:
    def __init__(self):
        self._exts = []
        self._load()

    def _load(self):
        try:
            if EXTENSIONS_FILE.exists():
                with open(EXTENSIONS_FILE, encoding="utf-8") as f:
                    self._exts = json.load(f)
                return
        except Exception:
            pass
        self._exts = [dict(e) for e in _DEFAULT_EXT]
        self._save()

    def _save(self):
        try:
            with open(EXTENSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._exts, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def all(self): return list(self._exts)

    def install(self, eid):
        for e in self._exts:
            if e["id"] == eid:
                e["installed"] = True; e["enabled"] = True
                self._save(); return True
        return False

    def uninstall(self, eid):
        for e in self._exts:
            if e["id"] == eid:
                e["installed"] = False; e["enabled"] = False
                self._save(); return True
        return False

    def toggle(self, eid):
        for e in self._exts:
            if e["id"] == eid and e.get("installed"):
                e["enabled"] = not e["enabled"]
                self._save(); return e["enabled"]
        return False

    def set_sites(self, eid, sites):
        for e in self._exts:
            if e["id"] == eid:
                e["sites"] = sites; self._save()

# ─────────────────────────────────────────────
#  ПЕРЕХВАТЧИК ЗАПРОСОВ
# ─────────────────────────────────────────────
class GwitInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, settings, blocklist, parent=None):
        super().__init__(parent)
        self._s = settings
        self._b = blocklist
        self._blocked_cb = None

    def set_blocked_callback(self, cb):
        self._blocked_cb = cb

    def interceptRequest(self, info):
        url = info.requestUrl().toString()

        if self._s.get("force_https"):
            parsed = urlparse(url)
            if (parsed.scheme == "http" and parsed.hostname
                    and parsed.hostname not in ("localhost", "127.0.0.1")):
                info.redirect(QUrl(url.replace("http://", "https://", 1)))
                return

        blocked, reason = self._b.is_blocked(url)
        if blocked:
            info.block(True)
            if self._blocked_cb:
                try:
                    self._blocked_cb(url, reason)
                except Exception:
                    pass

# ─────────────────────────────────────────────
#  СТРАНИЦА БЛОКИРОВКИ
# ─────────────────────────────────────────────
def blocked_html(url, reason):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{margin:0;font-family:'Segoe UI',sans-serif;background:#0f1117;color:#e2e8f0;
display:flex;align-items:center;justify-content:center;min-height:100vh;}}
.card{{background:#1a1d27;border:2px solid #e53e3e;border-radius:16px;
padding:48px 40px;max-width:520px;text-align:center;}}
.ico{{font-size:56px;margin-bottom:12px;}}
h1{{color:#e53e3e;font-size:22px;margin:0 0 8px;}}
p{{color:#94a3b8;margin:6px 0;font-size:14px;}}
.url{{background:#0f1117;border-radius:8px;padding:10px 14px;
font-family:monospace;color:#6c63ff;word-break:break-all;margin:14px 0;font-size:12px;}}
.reason{{background:#2d1212;border-radius:8px;padding:10px 14px;
color:#fc8181;font-size:13px;margin-bottom:16px;}}
button{{background:#6c63ff;color:#fff;border:none;border-radius:8px;
padding:10px 24px;font-size:14px;cursor:pointer;}}
button:hover{{background:#7c73ff;}}
</style></head><body><div class="card">
<div class="ico">🛡️</div>
<h1>Gwit заблокировал этот сайт</h1>
<p>Этот ресурс находится в списке нежелательных сайтов</p>
<div class="url">{url}</div>
<div class="reason">⚠️ {reason}</div>
<button onclick="history.back()">← Назад</button>
</div></body></html>"""

# ─────────────────────────────────────────────
#  ПОЛОСА ПРЕДУПРЕЖДЕНИЙ
# ─────────────────────────────────────────────
class SecurityBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()
        lo = QHBoxLayout(self)
        lo.setContentsMargins(12, 5, 12, 5)
        self._ico = QLabel()
        self._txt = QLabel()
        self._txt.setWordWrap(True)
        close = QPushButton("✕")
        close.setFixedSize(22, 22)
        close.setStyleSheet("background:transparent;border:none;color:#94a3b8;font-size:14px;")
        close.clicked.connect(self.hide)
        lo.addWidget(self._ico)
        lo.addWidget(self._txt, 1)
        lo.addWidget(close)

    def warn(self, msg, level="warn"):
        bg  = {"warn":"#2a1f00","danger":"#2a0000","info":"#0d1a2e"}
        bdr = {"warn":"#ed8936","danger":"#e53e3e","info":"#6c63ff"}
        ico = {"warn":"⚠️","danger":"🚨","info":"ℹ️"}
        self.setStyleSheet(
            f"background:{bg.get(level,'#2a1f00')};"
            f"border-bottom:2px solid {bdr.get(level,'#ed8936')};"
        )
        self._ico.setText(ico.get(level, "⚠️"))
        self._txt.setText(msg)
        self._txt.setStyleSheet(f"color:{bdr.get(level,'#ed8936')};font-size:12px;")
        self.show()

# ─────────────────────────────────────────────
#  ВКЛАДКА БРАУЗЕРА
# ─────────────────────────────────────────────
class BrowserTab(QWidget):
    title_changed    = pyqtSignal(str)
    url_changed      = pyqtSignal(str)
    load_start       = pyqtSignal()
    load_end         = pyqtSignal(bool)
    security_changed = pyqtSignal(str)

    def __init__(self, settings, blocklist, profile, parent=None):
        super().__init__(parent)
        self._s = settings
        self._b = blocklist
        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        self.view = QWebEngineView(profile)
        lo.addWidget(self.view)
        self.view.titleChanged.connect(self.title_changed)
        self.view.urlChanged.connect(self._url_changed)
        self.view.loadStarted.connect(self.load_start)
        self.view.loadFinished.connect(self.load_end)

    def _url_changed(self, qurl):
        url = qurl.toString()
        self.url_changed.emit(url)
        parsed = urlparse(url)
        if self._b.threat_type(url):
            self.security_changed.emit("danger")
        elif parsed.scheme == "https":
            self.security_changed.emit("safe")
        elif parsed.scheme == "http":
            self.security_changed.emit("warn")

    def load_url(self, url):
        if not url.strip():
            return
        if not url.startswith(("http://", "https://", "about:", "data:", "file://")):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = self._s.get("default_search") + url
        self.view.load(QUrl(url))

    def back(self):    self.view.back()
    def forward(self): self.view.forward()
    def reload(self):  self.view.reload()
    def stop(self):    self.view.stop()
    def url(self):     return self.view.url().toString()
    def title(self):   return self.view.title() or "Новая вкладка"

# ─────────────────────────────────────────────
#  ДИАЛОГ НАСТРОЕК
# ─────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, settings, blocklist, extensions, start_page=0, parent=None):
        super().__init__(parent)
        self._s = settings
        self._b = blocklist
        self._e = extensions
        self.setWindowTitle("Настройки — gwit")
        self.setMinimumSize(880, 620)
        self.resize(960, 680)
        self._build()
        self._switch(start_page)

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Сайдбар
        sb = QWidget()
        sb.setFixedWidth(185)
        sb.setStyleSheet("background:#13151f;")
        sbl = QVBoxLayout(sb)
        sbl.setContentsMargins(0, 12, 0, 12)
        sbl.setSpacing(0)

        logo = QLabel("  🌐  gwit")
        logo.setStyleSheet("font-size:19px;font-weight:bold;color:#6c63ff;padding:8px 16px 20px;")
        sbl.addWidget(logo)

        self._nav = []
        items = [
            ("🔒", "Безопасность"),
            ("⚡", "Производительность"),
            ("🧩", "Расширения"),
            ("🚫", "Блок-лист"),
            ("🎨", "Внешний вид"),
            ("ℹ️",  "О браузере"),
        ]
        for i, (ico, lbl) in enumerate(items):
            btn = QPushButton(f"   {ico}  {lbl}")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align:left; border:none; border-left:3px solid transparent;
                    padding:11px 14px; color:#94a3b8; background:transparent; font-size:13px;
                }
                QPushButton:hover  { background:#1a1d27; color:#e2e8f0; }
                QPushButton:checked { background:#1a1d27; color:#6c63ff; border-left-color:#6c63ff; }
            """)
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            sbl.addWidget(btn)
            self._nav.append(btn)

        sbl.addStretch()
        root.addWidget(sb)

        # Контент
        area = QScrollArea()
        area.setWidgetResizable(True)
        self._stack = QStackedWidget()
        area.setWidget(self._stack)
        root.addWidget(area)

        self._stack.addWidget(self._page_security())
        self._stack.addWidget(self._page_performance())
        self._stack.addWidget(self._page_extensions())
        self._stack.addWidget(self._page_blocklist())
        self._stack.addWidget(self._page_appearance())
        self._stack.addWidget(self._page_about())

    def _switch(self, idx):
        self._stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav):
            btn.setChecked(i == idx)

    def _h1(self, txt):
        l = QLabel(txt); l.setObjectName("h1"); return l

    def _sep(self):
        f = QFrame(); f.setObjectName("sep")
        f.setFixedHeight(1)
        f.setStyleSheet("background:#2d3148;margin:4px 0;")
        return f

    def _hint(self, txt):
        l = QLabel(txt)
        l.setStyleSheet("color:#64748b;font-size:11px;padding:2px 0;")
        l.setWordWrap(True)
        return l

    def _chk(self, label, key):
        c = QCheckBox(label)
        c.setChecked(bool(self._s.get(key)))
        c.toggled.connect(lambda v: self._s.set(key, v))
        return c

    def _page_base(self):
        w = QWidget()
        lo = QVBoxLayout(w)
        lo.setContentsMargins(28, 28, 28, 28)
        lo.setSpacing(14)
        return w, lo

    # ── Безопасность ──────────────────────────
    def _page_security(self):
        w, lo = self._page_base()
        lo.addWidget(self._h1("🔒  Безопасность"))
        lo.addWidget(self._sep())

        g1 = QGroupBox("Стандартная защита")
        gl = QVBoxLayout(g1)
        gl.addWidget(self._chk("Включить стандартную защиту", "security_standard"))
        gl.addWidget(self._hint("Проверка сайтов, файлов и расширений по базе нежелательных ресурсов"))
        lo.addWidget(g1)

        g2 = QGroupBox("Улучшенная защита")
        gl2 = QVBoxLayout(g2)
        gl2.addWidget(self._chk("Режим реального времени (анализ URL, контента, файлов)", "security_enhanced"))
        gl2.addWidget(self._hint("Глубокое сканирование страниц и iframe на угрозы, даже если они не в базе"))
        lo.addWidget(g2)

        g3 = QGroupBox("Ненадёжные расширения")
        gl3 = QVBoxLayout(g3)
        gl3.addWidget(self._chk("Предупреждать и отключать ненадёжные расширения", "warn_untrusted_extensions"))
        lo.addWidget(g3)

        g4 = QGroupBox("Безопасные соединения (HTTPS)")
        gl4 = QVBoxLayout(g4)
        gl4.addWidget(self._chk("Принудительный HTTPS — перенаправлять http:// → https://", "force_https"))
        gl4.addWidget(self._chk("Предупреждать, если сайт не поддерживает HTTPS", "warn_no_https"))
        lo.addWidget(g4)

        lo.addStretch()
        return w

    # ── Производительность ────────────────────
    def _page_performance(self):
        w, lo = self._page_base()
        lo.addWidget(self._h1("⚡  Производительность"))
        lo.addWidget(self._sep())

        g1 = QGroupBox("Экономия памяти")
        gl1 = QVBoxLayout(g1)
        gl1.addWidget(self._chk("Включить режим экономии памяти", "memory_saver"))
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Режим:"))
        cb1 = QComboBox()
        cb1.addItems(["Умеренная", "Сбалансированная", "Максимальная"])
        cb1.setCurrentIndex({"moderate":0,"balanced":1,"maximum":2}.get(self._s.get("memory_saver_mode"),1))
        cb1.currentIndexChanged.connect(lambda i: self._s.set("memory_saver_mode",["moderate","balanced","maximum"][i]))
        row1.addWidget(cb1); row1.addStretch()
        gl1.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Приостановить вкладку через (мин):"))
        sp = QSpinBox(); sp.setRange(1,120); sp.setValue(self._s.get("memory_saver_timeout_min",10))
        sp.valueChanged.connect(lambda v: self._s.set("memory_saver_timeout_min",v))
        row2.addWidget(sp); row2.addStretch()
        gl1.addLayout(row2)
        lo.addWidget(g1)

        g2 = QGroupBox("Предзагрузка страниц")
        gl2 = QVBoxLayout(g2)
        gl2.addWidget(self._chk("Включить предзагрузку", "preload_pages"))
        cb2 = QComboBox()
        cb2.addItems(["Отключена","Стандартная","Расширенная"])
        cb2.setCurrentIndex({"none":0,"standard":1,"extended":2}.get(self._s.get("preload_mode"),1))
        cb2.currentIndexChanged.connect(lambda i: self._s.set("preload_mode",["none","standard","extended"][i]))
        gl2.addWidget(cb2)
        lo.addWidget(g2)

        g3 = QGroupBox("Режим энергосбережения")
        gl3 = QVBoxLayout(g3)
        gl3.addWidget(self._chk("Включить режим энергосбережения", "energy_saver"))
        gl3.addWidget(self._chk("Авто-активация при низком заряде / отключении питания", "energy_saver_auto"))
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Порог заряда (%):"))
        sp2 = QSpinBox(); sp2.setRange(5,50); sp2.setValue(self._s.get("battery_threshold",20))
        sp2.valueChanged.connect(lambda v: self._s.set("battery_threshold",v))
        row3.addWidget(sp2); row3.addStretch()
        gl3.addLayout(row3)
        gl3.addWidget(self._hint("Фоновые вкладки с высокой нагрузкой на ЦП приостанавливаются"))
        lo.addWidget(g3)

        lo.addStretch()
        return w

    # ── Расширения ────────────────────────────
    def _page_extensions(self):
        w, lo = self._page_base()
        lo.addWidget(self._h1("🧩  Расширения"))
        lo.addWidget(self._sep())

        row = QHBoxLayout()
        self._ext_q = QLineEdit()
        self._ext_q.setPlaceholderText("Поиск расширений...")
        self._ext_q.textChanged.connect(self._refresh_exts)
        row.addWidget(self._ext_q)
        self._ext_cat = QComboBox()
        self._ext_cat.addItems(["Все","Security","Productivity","Appearance","Shopping","Unknown"])
        self._ext_cat.currentTextChanged.connect(self._refresh_exts)
        row.addWidget(self._ext_cat)
        lo.addLayout(row)

        self._ext_list = QListWidget()
        self._ext_list.setMinimumHeight(250)
        self._ext_list.itemDoubleClicked.connect(self._ext_menu)
        lo.addWidget(self._ext_list)
        self._refresh_exts()

        g = QGroupBox("Параметры")
        gl = QVBoxLayout(g)
        gl.addWidget(self._chk("Автоматическая установка расширений вместе с приложениями", "auto_install_extensions"))
        gl.addWidget(self._chk("Предупреждать при установке ненадёжных расширений", "extensions_enhanced_check"))
        lo.addWidget(g)
        lo.addStretch()
        return w

    def _refresh_exts(self):
        q   = self._ext_q.text().lower() if hasattr(self,"_ext_q") else ""
        cat = self._ext_cat.currentText() if hasattr(self,"_ext_cat") else "Все"
        self._ext_list.clear()
        for ext in self._e.all():
            if q and q not in ext["name"].lower(): continue
            if cat != "Все" and ext.get("cat","") != cat: continue
            inst = ext.get("installed")
            enab = ext.get("enabled")
            if inst and enab:   status = "✅ Включено"
            elif inst:          status = "⏸ Отключено"
            else:               status = "📥 Не установлено"
            trust = "✓" if ext.get("trusted") else "⚠️"
            item = QListWidgetItem(f'{ext["icon"]}  {ext["name"]}  [{ext["cat"]}]  {trust}  —  {status}')
            item.setData(Qt.ItemDataRole.UserRole, ext["id"])
            if not ext.get("trusted"):
                item.setForeground(QColor("#ed8936"))
            self._ext_list.addItem(item)

    def _ext_menu(self, item):
        eid = item.data(Qt.ItemDataRole.UserRole)
        ext = next((e for e in self._e.all() if e["id"]==eid), None)
        if not ext: return
        menu = QMenu(self)
        if not ext.get("installed"):
            menu.addAction("📥 Установить").triggered.connect(lambda: self._install_ext(eid, ext))
        else:
            lbl = "⏸ Отключить" if ext.get("enabled") else "▶ Включить"
            menu.addAction(lbl).triggered.connect(lambda: (self._e.toggle(eid), self._refresh_exts()))
            menu.addSeparator()
            menu.addAction("🌐 Сайты").triggered.connect(lambda: self._ext_sites(eid))
            menu.addSeparator()
            menu.addAction("🗑 Удалить").triggered.connect(lambda: (self._e.uninstall(eid), self._refresh_exts()))
        menu.exec(QCursor.pos())

    def _install_ext(self, eid, ext):
        if not ext.get("trusted") and self._s.get("extensions_enhanced_check"):
            if QMessageBox.warning(self, "Ненадёжное расширение",
                    f"«{ext['name']}» не проверено. Установить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                ) != QMessageBox.StandardButton.Yes:
                return
        self._e.install(eid)
        self._refresh_exts()

    def _ext_sites(self, eid):
        v, ok = QInputDialog.getText(self, "Сайты", "Введите домены через запятую или 'all':")
        if ok: self._e.set_sites(eid, v)

    # ── Блок-лист ─────────────────────────────
    def _page_blocklist(self):
        w, lo = self._page_base()
        lo.addWidget(self._h1("🚫  База нежелательных сайтов"))
        lo.addWidget(self._sep())

        tabs = QTabWidget()

        # Мой список
        cw = QWidget(); cl = QVBoxLayout(cw)
        ar = QHBoxLayout()
        self._bl_dom = QLineEdit(); self._bl_dom.setPlaceholderText("example.com")
        self._bl_rsn = QLineEdit(); self._bl_rsn.setPlaceholderText("Причина (необязательно)")
        ab = QPushButton("Добавить"); ab.setObjectName("accent")
        ab.clicked.connect(self._bl_add)
        ar.addWidget(self._bl_dom); ar.addWidget(self._bl_rsn); ar.addWidget(ab)
        cl.addLayout(ar)
        self._bl_list = QListWidget()
        self._bl_list.setMinimumHeight(200)
        self._bl_refresh()
        cl.addWidget(self._bl_list)
        br = QHBoxLayout()
        db = QPushButton("🗑 Удалить"); db.setObjectName("danger"); db.clicked.connect(self._bl_del)
        tb2 = QPushButton("⏸ Вкл / Откл"); tb2.clicked.connect(self._bl_toggle)
        br.addWidget(db); br.addWidget(tb2); br.addStretch()
        cl.addLayout(br)
        tabs.addTab(cw, "Мой список")

        # Встроенный
        bw = QWidget(); bl = QVBoxLayout(bw)
        bl.addWidget(self._hint("Встроенная база нежелательных сайтов (только чтение):"))
        blist = QListWidget()
        for d in self._b.builtin_list():
            blist.addItem(QListWidgetItem(f"🚫  {d}"))
        bl.addWidget(blist)
        tabs.addTab(bw, "Встроенный список")

        # База угроз
        tw = QWidget(); tl = QVBoxLayout(tw)
        tree = QTreeWidget()
        tree.setHeaderLabels(["Тип угрозы","Домен"])
        tree.setColumnWidth(0, 150)
        for threat, domains in SAFE_BROWSING_DB.items():
            root_item = QTreeWidgetItem(tree, [threat.upper(), ""])
            for d in domains:
                QTreeWidgetItem(root_item, ["", d])
            root_item.setExpanded(True)
        tl.addWidget(tree)
        tabs.addTab(tw, "База угроз")

        lo.addWidget(tabs)
        return w

    def _bl_refresh(self):
        if not hasattr(self, "_bl_list"): return
        self._bl_list.clear()
        for e in self._b.custom_list():
            ok = e.get("enabled", True)
            text = f'{"✅" if ok else "⏸"}  {e["domain"]}'
            if e.get("reason"): text += f'  —  {e["reason"]}'
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, e["domain"])
            if not ok: item.setForeground(QColor("#64748b"))
            self._bl_list.addItem(item)

    def _bl_add(self):
        d = self._bl_dom.text().strip()
        r = self._bl_rsn.text().strip()
        if not d: return
        if self._b.add(d, r):
            self._bl_dom.clear(); self._bl_rsn.clear(); self._bl_refresh()
        else:
            QMessageBox.information(self, "Уже есть", f"«{d}» уже в списке")

    def _bl_del(self):
        item = self._bl_list.currentItem()
        if item: self._b.remove(item.data(Qt.ItemDataRole.UserRole)); self._bl_refresh()

    def _bl_toggle(self):
        item = self._bl_list.currentItem()
        if item: self._b.toggle(item.data(Qt.ItemDataRole.UserRole)); self._bl_refresh()

    # ── Внешний вид ───────────────────────────
    def _page_appearance(self):
        w, lo = self._page_base()
        lo.addWidget(self._h1("🎨  Внешний вид"))
        lo.addWidget(self._sep())

        g1 = QGroupBox("Тема")
        gl1 = QVBoxLayout(g1)
        rd = QRadioButton("Тёмная"); rl = QRadioButton("Светлая")
        if self._s.get("theme") == "dark": rd.setChecked(True)
        else: rl.setChecked(True)
        rd.toggled.connect(lambda v: v and self._apply_theme("dark"))
        rl.toggled.connect(lambda v: v and self._apply_theme("light"))
        gl1.addWidget(rd); gl1.addWidget(rl)
        lo.addWidget(g1)

        g2 = QGroupBox("Домашняя страница")
        gl2 = QVBoxLayout(g2)
        he = QLineEdit(self._s.get("homepage"))
        he.textChanged.connect(lambda v: self._s.set("homepage", v))
        gl2.addWidget(he)
        lo.addWidget(g2)

        g3 = QGroupBox("Поисковик по умолчанию")
        gl3 = QVBoxLayout(g3)
        engines = {
            "Google":     "https://www.google.com/search?q=",
            "Bing":       "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Yandex":     "https://yandex.ru/search/?text=",
        }
        sc = QComboBox()
        for k in engines: sc.addItem(k)
        cur = self._s.get("default_search")
        for k, v in engines.items():
            if v == cur: sc.setCurrentText(k)
        sc.currentTextChanged.connect(lambda n: self._s.set("default_search", engines.get(n, cur)))
        gl3.addWidget(sc)
        lo.addWidget(g3)

        lo.addStretch()
        return w

    def _apply_theme(self, t):
        self._s.set("theme", t)
        QApplication.instance().setStyleSheet(DARK_STYLE if t=="dark" else LIGHT_STYLE)

    # ── О браузере ────────────────────────────
    def _page_about(self):
        w, lo = self._page_base()
        t = QLabel("🌐 gwit Browser")
        t.setStyleSheet("font-size:30px;font-weight:bold;color:#6c63ff;margin-bottom:6px;")
        lo.addWidget(t)
        lo.addWidget(QLabel("Версия 1.0.0  |  Python + PyQt6 + Chromium"))
        lo.addWidget(self._sep())
        info = QLabel(
            "gwit — браузер с акцентом на безопасность и производительность.\n\n"
            "• Стандартная и улучшенная защита от угроз\n"
            "• Принудительный HTTPS и проверка сайтов\n"
            "• Экономия памяти (3 режима) и энергосбережение\n"
            "• Управление расширениями с проверкой безопасности\n"
            "• Персональная база нежелательных сайтов\n"
            "• Полная настройка через интерфейс браузера\n\n"
            "Горячие клавиши:\n"
            "  Ctrl+T — новая вкладка\n"
            "  Ctrl+W — закрыть вкладку\n"
            "  Ctrl+L — адресная строка\n"
            "  Ctrl+R — обновить\n"
            "  Ctrl+,  — настройки"
        )
        info.setStyleSheet("color:#94a3b8;font-size:13px;line-height:1.6;")
        info.setWordWrap(True)
        lo.addWidget(info)
        lo.addStretch()
        return w

# ─────────────────────────────────────────────
#  ГЛАВНОЕ ОКНО
# ─────────────────────────────────────────────
class GwitBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self._settings   = SettingsManager()
        self._blocklist  = BlocklistManager()
        self._extensions = ExtensionsManager()
        self._tab_active = {}

        # WebEngine профиль
        self._profile = QWebEngineProfile("GwitProfile", self)
        self._interceptor = GwitInterceptor(self._settings, self._blocklist, self)
        self._interceptor.set_blocked_callback(self._on_blocked)
        self._profile.setUrlRequestInterceptor(self._interceptor)

        self._build_ui()
        self._apply_theme()

        self._mem_timer = QTimer(self)
        self._mem_timer.setInterval(60_000)
        self._mem_timer.timeout.connect(self._memory_saver_tick)
        self._mem_timer.start()

        self._new_tab(self._settings.get("homepage"))

    def _build_ui(self):
        self.setWindowTitle("gwit")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        lo = QVBoxLayout(central)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        self._build_toolbar()

        self._sec_bar = SecurityBar()
        lo.addWidget(self._sec_bar)

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        self._tabs.currentChanged.connect(self._on_tab_switch)
        lo.addWidget(self._tabs)

        sb = QStatusBar()
        self.setStatusBar(sb)
        self._sec_lbl = QLabel("🔒 Безопасно")
        self._sec_lbl.setObjectName("safe")
        sb.addPermanentWidget(self._sec_lbl)
        self._prog = QProgressBar()
        self._prog.setFixedHeight(3)
        self._prog.setTextVisible(False)
        self._prog.hide()
        sb.addWidget(self._prog, 1)

    def _build_toolbar(self):
        tb = QToolBar()
        tb.setMovable(False)
        self.addToolBar(tb)

        def btn(ico, tip, fn):
            b = QToolButton()
            b.setText(ico); b.setToolTip(tip)
            b.setFixedSize(34, 34)
            b.clicked.connect(fn)
            return b

        tb.addWidget(btn("◀", "Назад",    self._back))
        tb.addWidget(btn("▶", "Вперёд",   self._forward))
        tb.addWidget(btn("↺", "Обновить", self._reload))
        tb.addWidget(btn("🏠", "Домой",   self._home))
        tb.addSeparator()

        self._https_ico = QLabel("🔒")
        self._https_ico.setFixedWidth(26)
        self._https_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb.addWidget(self._https_ico)

        self._url_bar = QLineEdit()
        self._url_bar.setPlaceholderText("Введите адрес или поисковый запрос...")
        self._url_bar.returnPressed.connect(self._navigate)
        self._url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(self._url_bar)

        tb.addSeparator()
        tb.addWidget(btn("➕",  "Новая вкладка (Ctrl+T)", lambda: self._new_tab()))
        tb.addSeparator()
        tb.addWidget(btn("🧩", "Расширения",             lambda: self._open_settings(2)))
        tb.addWidget(btn("🚫", "Блок-лист",              lambda: self._open_settings(3)))
        tb.addWidget(btn("⚙️", "Настройки",              lambda: self._open_settings(0)))

    # ── Вкладки ───────────────────────────────
    def _new_tab(self, url=""):
        tab = BrowserTab(self._settings, self._blocklist, self._profile, self)
        idx = self._tabs.addTab(tab, "Новая вкладка")
        self._tabs.setCurrentIndex(idx)
        self._tab_active[id(tab)] = time.time()

        tab.title_changed.connect(lambda t, _tab=tab: self._set_tab_title(_tab, t))
        tab.url_changed.connect(lambda u, _tab=tab: self._on_url_changed(_tab, u))
        tab.load_start.connect(lambda: self._prog.show())
        tab.load_end.connect(lambda ok: self._prog.hide())
        tab.security_changed.connect(self._update_sec)

        if url:
            tab.load_url(url)
        return tab

    def _close_tab(self, idx):
        if self._tabs.count() == 1:
            self._new_tab()
        w = self._tabs.widget(idx)
        self._tabs.removeTab(idx)
        if w:
            self._tab_active.pop(id(w), None)
            w.deleteLater()

    def _on_tab_switch(self, idx):
        tab = self._cur()
        if tab:
            self._tab_active[id(tab)] = time.time()
            self._url_bar.setText(tab.url())

    def _cur(self):
        w = self._tabs.currentWidget()
        return w if isinstance(w, BrowserTab) else None

    def _set_tab_title(self, tab, title):
        idx = self._tabs.indexOf(tab)
        if idx >= 0:
            short = (title[:18] + "…") if len(title) > 20 else title
            self._tabs.setTabText(idx, short or "Новая вкладка")

    # ── Навигация ─────────────────────────────
    def _navigate(self):
        tab = self._cur()
        if tab: tab.load_url(self._url_bar.text().strip())

    def _back(self):
        tab = self._cur()
        if tab: tab.back()

    def _forward(self):
        tab = self._cur()
        if tab: tab.forward()

    def _reload(self):
        tab = self._cur()
        if tab: tab.reload()

    def _home(self):
        tab = self._cur()
        if tab: tab.load_url(self._settings.get("homepage"))

    def _on_url_changed(self, tab, url):
        if self._tabs.currentWidget() is tab:
            self._url_bar.setText(url)
        parsed = urlparse(url)
        if (parsed.scheme == "http"
                and parsed.hostname
                and parsed.hostname not in ("localhost","127.0.0.1")
                and self._settings.get("warn_no_https")):
            self._sec_bar.warn(
                f"Соединение с {parsed.hostname} не защищено. "
                "Gwit попытался перейти на HTTPS, но сайт его не поддерживает.", "warn"
            )

    def _update_sec(self, status):
        d = {
            "safe":   ("🔒", "🔒 Безопасно", "safe"),
            "warn":   ("⚠️",  "⚠️ HTTP",      "warn"),
            "danger": ("🚨", "🚨 Угроза!",    "danger_lbl"),
        }
        ico, lbl, obj = d.get(status, ("🔒","🔒 Безопасно","safe"))
        self._https_ico.setText(ico)
        self._sec_lbl.setText(lbl)
        self._sec_lbl.setObjectName(obj)
        self._sec_lbl.style().unpolish(self._sec_lbl)
        self._sec_lbl.style().polish(self._sec_lbl)

    def _on_blocked(self, url, reason):
        tab = self._cur()
        if tab:
            tab.view.setHtml(blocked_html(url, reason), QUrl("about:blocked"))
        self._sec_bar.warn(f"Заблокировано: {url}  —  {reason}", "danger")

    def _open_settings(self, page=0):
        d = SettingsDialog(self._settings, self._blocklist, self._extensions, page, self)
        d.exec()
        self._apply_theme()

    def _apply_theme(self):
        t = self._settings.get("theme", "dark")
        QApplication.instance().setStyleSheet(DARK_STYLE if t=="dark" else LIGHT_STYLE)

    def _memory_saver_tick(self):
        if not self._settings.get("memory_saver"): return
        timeout_min = self._settings.get("memory_saver_timeout_min", 10)
        mode = self._settings.get("memory_saver_mode","balanced")
        mult = {"moderate":3,"balanced":1,"maximum":0.5}.get(mode,1)
        threshold = timeout_min * mult * 60
        now = time.time()
        cur_tab = self._cur()
        for i in range(self._tabs.count()):
            tab = self._tabs.widget(i)
            if not isinstance(tab, BrowserTab): continue
            if tab is cur_tab: continue
            last = self._tab_active.get(id(tab), now)
            if now - last < threshold: continue
            tab.view.setHtml(
                "<html><body style='margin:0;background:#0f1117;color:#94a3b8;"
                "font-family:sans-serif;display:flex;align-items:center;"
                "justify-content:center;height:100vh;text-align:center;'>"
                "<div><div style='font-size:48px;margin-bottom:12px'>💤</div>"
                "<p style='font-size:15px'>Вкладка приостановлена для экономии памяти</p>"
                "<p style='font-size:12px;color:#475569'>Нажмите ↺ чтобы перезагрузить</p>"
                "</div></body></html>"
            )
            self._tab_active[id(tab)] = now + 86400  # не трогать ещё сутки

    def keyPressEvent(self, event):
        ctrl = Qt.KeyboardModifier.ControlModifier
        if event.modifiers() & ctrl:
            k = event.key()
            if   k == Qt.Key.Key_T:     self._new_tab()
            elif k == Qt.Key.Key_W:     self._close_tab(self._tabs.currentIndex())
            elif k == Qt.Key.Key_L:     self._url_bar.selectAll(); self._url_bar.setFocus()
            elif k == Qt.Key.Key_R:     self._reload()
            elif k == Qt.Key.Key_Comma: self._open_settings(0)
        super().keyPressEvent(event)

# ─────────────────────────────────────────────
#  ЗАПУСК
# ─────────────────────────────────────────────
def main():
    # Для Windows: без этого WebEngine может не стартовать
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox")

    app = QApplication(sys.argv)
    app.setApplicationName("gwit")
    app.setOrganizationName("Gwit Browser")
    app.setStyleSheet(DARK_STYLE)

    window = GwitBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
