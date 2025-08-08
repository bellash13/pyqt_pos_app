
import hashlib
from PyQt5.QtWidgets import QMessageBox

def hash_password(pwd: str) -> str:
    return hashlib.sha256(("pos_salt__" + pwd).encode("utf-8")).hexdigest()

def info(parent, text):
    QMessageBox.information(parent, "Info", text)

def warn(parent, text):
    QMessageBox.warning(parent, "Attention", text)

def ask(parent, text) -> bool:
    return QMessageBox.question(parent, "Confirmer", text, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes

def money(v: float) -> str:
    return f"{v:,.2f}".replace(",", " ").replace(".", ",")
