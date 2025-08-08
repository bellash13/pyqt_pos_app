
from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QAction, QToolBar
from styles import MAIN_QSS
from views.pos_view import PosView
from views.reports_view import ReportsView
from views.manage_common import ManageCategories, ManageProducts, ManageTables, ManageServers, ManageUsers

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle("Buvette/Restaurant POS")
        self.resize(1100, 700)
        self.setStyleSheet(MAIN_QSS)

        self.tabs = QTabWidget()
        self.pos = PosView()
        self.reports = ReportsView()
        self.tabs.addTab(self.pos, "POS")
        self.tabs.addTab(self.reports, "Rapports")
        self.setCentralWidget(self.tabs)

        tb = QToolBar("Admin")
        self.addToolBar(tb)

        act_cats = QAction("Catégories", self)
        act_cats.triggered.connect(lambda: self.open_admin_tab(ManageCategories(), "Catégories"))
        tb.addAction(act_cats)

        act_prods = QAction("Produits", self)
        act_prods.triggered.connect(lambda: self.open_admin_tab(ManageProducts(), "Produits"))
        tb.addAction(act_prods)

        act_tables = QAction("Tables", self)
        act_tables.triggered.connect(lambda: self.open_admin_tab(ManageTables(), "Tables"))
        tb.addAction(act_tables)

        act_srv = QAction("Serveurs", self)
        act_srv.triggered.connect(lambda: self.open_admin_tab(ManageServers(), "Serveurs"))
        tb.addAction(act_srv)

        act_users = QAction("Utilisateurs", self)
        act_users.triggered.connect(lambda: self.open_admin_tab(ManageUsers(), "Utilisateurs"))
        tb.addAction(act_users)

        if self.current_user["role"] != "admin":
            tb.setVisible(False)

    def open_admin_tab(self, widget: QWidget, title: str):
        idx = self.tabs.addTab(widget, f"Admin – {title}")
        self.tabs.setCurrentIndex(idx)
