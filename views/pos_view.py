
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QDateTime
import datetime
from db import get_conn
from utils import info, warn, ask, money

class PosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = get_conn()
        self.current_order_id = None

        root = QVBoxLayout(self)

        # Selection bar
        sel = QHBoxLayout()
        sel.addWidget(QLabel("Table:"))
        self.cmb_table = QComboBox()
        sel.addWidget(self.cmb_table)
        sel.addSpacing(20)
        sel.addWidget(QLabel("Serveur:"))
        self.cmb_server = QComboBox()
        sel.addWidget(self.cmb_server)
        sel.addStretch(1)
        self.btn_new = QPushButton("Nouvelle facture")
        self.btn_new.clicked.connect(self.new_order)
        sel.addWidget(self.btn_new)
        self.btn_close = QPushButton("Clôturer")
        self.btn_close.clicked.connect(self.close_order)
        sel.addWidget(self.btn_close)
        root.addLayout(sel)

        # product grid + cart
        area = QHBoxLayout()

        # products panel
        self.products_panel = QWidget()
        self.grid = QGridLayout(self.products_panel)
        self.grid.setContentsMargins(0,0,0,0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.products_panel)

        area.addWidget(scroll, 2)

        # cart
        cart_panel = QVBoxLayout()
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["Produit", "PU", "Qté", "Total", ""])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        cart_panel.addWidget(self.tbl)

        btns = QHBoxLayout()
        self.lbl_total = QLabel("Total: 0,00")
        btns.addWidget(self.lbl_total)
        btns.addStretch(1)
        self.btn_minus = QPushButton("- Qté")
        self.btn_minus.clicked.connect(self.decr_qty)
        self.btn_plus = QPushButton("+ Qté")
        self.btn_plus.clicked.connect(self.incr_qty)
        self.btn_remove = QPushButton("Supprimer ligne")
        self.btn_remove.clicked.connect(self.remove_line)
        btns.addWidget(self.btn_minus); btns.addWidget(self.btn_plus); btns.addWidget(self.btn_remove)
        cart_panel.addLayout(btns)

        right = QWidget()
        right.setLayout(cart_panel)
        area.addWidget(right, 1)

        root.addLayout(area)
        self.reload_selectors()
        self.load_products_grid()

    def reload_selectors(self):
        self.cmb_table.clear()
        for row in self.conn.execute("SELECT id, number, COALESCE(label,'') AS label FROM tables WHERE active=1 ORDER BY number"):
            self.cmb_table.addItem(f"#{row['number']} {row['label']}", row[0])

        self.cmb_server.clear()
        for row in self.conn.execute("SELECT id, name FROM servers WHERE active=1 ORDER BY name"):
            self.cmb_server.addItem(row[1], row[0])

    def load_products_grid(self):
        # Clear grid
        while self.grid.count():
            item = self.grid.itemAt(0)
            w = item.widget()
            self.grid.removeWidget(w)
            w.deleteLater()

        row_idx = 0
        col_idx = 0
        # categories
        cats = list(self.conn.execute("SELECT id, name FROM categories WHERE active=1 ORDER BY name"))
        for cat in cats:
            title = QLabel(f"— {cat[1]} —")
            title.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(title, row_idx, 0, 1, 3)
            row_idx += 1
            col_idx = 0
            for p in self.conn.execute("SELECT id,name,price FROM products WHERE active=1 AND category_id=? ORDER BY name", (cat[0],)):
                btn = QPushButton(f"{p[1]}\n{p[2]:.2f}")
                btn.clicked.connect(lambda _, pid=p[0]: self.add_product(pid))
                self.grid.addWidget(btn, row_idx, col_idx)
                col_idx += 1
                if col_idx >= 3:
                    col_idx = 0
                    row_idx += 1
            row_idx += 1

    def add_product(self, product_id):
        if not self.current_order_id:
            if not self.new_order():
                return
        # add item or increase qty
        row = self.conn.execute("SELECT name, price FROM products WHERE id=?", (product_id,)).fetchone()
        # check if exists
        existing = self.conn.execute("SELECT id, qty FROM order_items WHERE order_id=? AND product_id=?",
                                     (self.current_order_id, product_id)).fetchone()
        if existing:
            self.conn.execute("UPDATE order_items SET qty=qty+1 WHERE id=?", (existing[0],))
        else:
            self.conn.execute("INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,?,?)",
                              (self.current_order_id, product_id, 1, row[1]))
        self.conn.commit()
        self.refresh_cart()

    def new_order(self):
        table_id = self.cmb_table.currentData()
        server_id = self.cmb_server.currentData()
        if not table_id or not server_id:
            warn(self, "Choisissez une table et un serveur.")
            return False
        # open existing open order for table?
        exist = self.conn.execute("SELECT id FROM orders WHERE status='open' AND table_id=?", (table_id,)).fetchone()
        if exist:
            self.current_order_id = exist[0]
        else:
            now = datetime.datetime.now().isoformat(timespec="seconds")
            cur = self.conn.execute("INSERT INTO orders(table_id,server_id,status,created_at) VALUES(?,?, 'open', ?)",
                               (table_id, server_id, now))
            self.current_order_id = cur.lastrowid
            self.conn.commit()
        self.refresh_cart()
        return True

    def refresh_cart(self):
        if not self.current_order_id:
            self.tbl.setRowCount(0)
            self.lbl_total.setText("Total: 0,00")
            return
        rows = list(self.conn.execute("""            SELECT oi.id, p.name, oi.qty, oi.price, (oi.qty*oi.price) AS total
            FROM order_items oi JOIN products p ON p.id=oi.product_id
            WHERE oi.order_id=?
            ORDER BY oi.id
        """, (self.current_order_id,)))
        self.tbl.setRowCount(len(rows))
        total = 0.0
        for r_idx, r in enumerate(rows):
            self.tbl.setItem(r_idx, 0, QTableWidgetItem(r[1]))
            self.tbl.setItem(r_idx, 1, QTableWidgetItem(f"{r[3]:.2f}"))
            self.tbl.setItem(r_idx, 2, QTableWidgetItem(str(r[2])))
            self.tbl.setItem(r_idx, 3, QTableWidgetItem(f"{r[4]:.2f}"))
            self.tbl.setItem(r_idx, 4, QTableWidgetItem(str(r[0])))  # hidden id
            total += r[4]
        self.tbl.setColumnHidden(4, True)
        self.lbl_total.setText(f"Total: {money(total)}")

    def _current_item_id(self):
        row = self.tbl.currentRow()
        if row < 0: return None
        return int(self.tbl.item(row, 4).text())

    def incr_qty(self):
        oid = self._current_item_id()
        if not oid: return
        self.conn.execute("UPDATE order_items SET qty=qty+1 WHERE id=?", (oid,))
        self.conn.commit()
        self.refresh_cart()

    def decr_qty(self):
        oid = self._current_item_id()
        if not oid: return
        row = self.conn.execute("SELECT qty FROM order_items WHERE id=?", (oid,)).fetchone()
        if row and row[0] > 1:
            self.conn.execute("UPDATE order_items SET qty=qty-1 WHERE id=?", (oid,))
        else:
            if ask(self, "Quantité 1 → supprimer la ligne ?"):
                self.conn.execute("DELETE FROM order_items WHERE id=?", (oid,))
        self.conn.commit()
        self.refresh_cart()

    def remove_line(self):
        oid = self._current_item_id()
        if not oid: return
        if ask(self, "Supprimer cette ligne ?"):
            self.conn.execute("DELETE FROM order_items WHERE id=?", (oid,))
            self.conn.commit()
            self.refresh_cart()

    def close_order(self):
        if not self.current_order_id:
            warn(self, "Aucune facture ouverte.")
            return
        tot = self.conn.execute("SELECT COALESCE(SUM(qty*price),0) FROM order_items WHERE order_id=?",
                                (self.current_order_id,)).fetchone()[0] or 0.0
        self.conn.execute("UPDATE orders SET status='closed', closed_at=datetime('now'), total=? WHERE id=?",
                          (tot, self.current_order_id))
        self.conn.commit()
        info(self, f"Facture clôturée. Total payé: {money(tot)}")
        self.current_order_id = None
        self.refresh_cart()
