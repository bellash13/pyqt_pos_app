
import sys
from PyQt5.QtWidgets import QApplication
from db import init_db, auth_user
from auth import LoginDialog
from main_window import MainWindow
from utils import warn

def main():
    app = QApplication(sys.argv)
    init_db()

    user_holder = {"obj": None}
    def on_login(u, p):
        user = auth_user(u, p)
        if user:
            user_holder["obj"] = user
            dlg.accept()
        else:
            warn(dlg, "Identifiants invalides.")

    global dlg
    dlg = LoginDialog(on_login)
    if dlg.exec_() != dlg.Accepted or not user_holder["obj"]:
        sys.exit(0)

    win = MainWindow(user_holder["obj"])
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
