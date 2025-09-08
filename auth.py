
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, on_login, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.on_login = on_login
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Nom d'utilisateur"))
        self.user = QLineEdit()
        self.user.setText("admin")
        layout.addWidget(self.user)

        layout.addWidget(QLabel("Mot de passe"))
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)        
        self.pwd.setFocus()
        layout.addWidget(self.pwd)

        btns = QHBoxLayout()
        self.btn_ok = QPushButton("Se connecter")
        self.btn_ok.clicked.connect(self.try_login)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

    def try_login(self):
        self.on_login(self.user.text().strip(), self.pwd.text())
