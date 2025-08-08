
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QDate
from db import get_conn
from utils import money

class ReportsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = get_conn()

        root = QVBoxLayout(self)

        filt = QHBoxLayout()
        filt.addWidget(QLabel("Du"))
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate())
        filt.addWidget(self.date_from)
        filt.addWidget(QLabel("au"))
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())
        filt.addWidget(self.date_to)

        filt.addSpacing(20)
        filt.addWidget(QLabel("Serveur"))
        self.cmb_server = QComboBox()
        self.cmb_server.addItem("Tous", None)
        for r in self.conn.execute("SELECT id, name FROM servers WHERE active=1 ORDER BY name"):
            self.cmb_server.addItem(r[1], r[0])
        filt.addSpacing(10)
        filt.addWidget(QLabel("Table"))
        self.cmb_table = QComboBox()
        self.cmb_table.addItem("Toutes", None)
        for r in self.conn.execute("SELECT id, number FROM tables WHERE active=1 ORDER BY number"):
            self.cmb_table.addItem(f"#{r[1]}", r[0])

        self.btn_run = QPushButton("Afficher")
        self.btn_run.clicked.connect(self.run_report)
        filt.addWidget(self.btn_run)
        filt.addStretch(1)
        root.addLayout(filt)

        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(["Date", "Heure", "Table", "Serveur", "Status", "Total"])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

    def run_report(self):
        d1 = self.date_from.date().toString("yyyy-MM-dd")
        d2 = self.date_to.date().toString("yyyy-MM-dd")
        sid = self.cmb_server.currentData()
        tid = self.cmb_table.currentData()

        sql = """SELECT o.id, date(o.created_at) d, time(o.created_at) t, t1.number AS tab, s.name AS srv,
                 o.status, o.total
                 FROM orders o
                 JOIN tables t1 ON t1.id=o.table_id
                 JOIN servers s ON s.id=o.server_id
                 WHERE date(o.created_at) BETWEEN ? AND ?"""
        params = [d1, d2]
        if sid:
            sql += " AND o.server_id=?"
            params.append(sid)
        if tid:
            sql += " AND o.table_id=?"
            params.append(tid)
        sql += " ORDER BY o.created_at DESC"

        rows = list(self.conn.execute(sql, params))
        self.tbl.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl.setItem(i, 0, QTableWidgetItem(r[1]))
            self.tbl.setItem(i, 1, QTableWidgetItem(r[2]))
            self.tbl.setItem(i, 2, QTableWidgetItem(str(r[3])))
            self.tbl.setItem(i, 3, QTableWidgetItem(r[4]))
            self.tbl.setItem(i, 4, QTableWidgetItem(r[5]))
            self.tbl.setItem(i, 5, QTableWidgetItem(money(r[6])))
