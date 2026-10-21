import os
import sys
import webview
from pathlib import Path
from src.ui.api import BridgeAPI

CURRENT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = CURRENT_DIR / "templates"
INDEX_HTML = TEMPLATES_DIR / "index.html"

def start_gui():
    """Inicia la ventana de escritorio con PyWebView conectada a BridgeAPI."""
    api = BridgeAPI()

    window = webview.create_window(
        title="SteamAgent Desktop — AI Gaming Companion",
        url=str(INDEX_HTML),
        js_api=api,
        width=960,
        height=680,
        resizable=False,
        frameless=False,
        background_color="#07090e"
    )

    api.set_window(window)

    # Iniciar con motor QT
    webview.start(gui="qt", debug=False)

if __name__ == "__main__":
    start_gui()
