
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox, QSpinBox,
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QDateTime
import datetime
import os
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
        sel.addSpacing(20)
        sel.addWidget(QLabel("Devise:"))
        self.cmb_currency = QComboBox()
        sel.addWidget(self.cmb_currency)
        sel.addStretch(1)
        self.btn_new = QPushButton("Nouvelle facture")
        self.btn_new.clicked.connect(self.new_order)
        sel.addWidget(self.btn_new)
        self.btn_transfer = QPushButton("Transférer Table")
        self.btn_transfer.clicked.connect(self.transfer_table)
        sel.addWidget(self.btn_transfer)
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
        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(["Produit", "PU", "Qté", "Remise %", "Total", ""])
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
        self.btn_discount = QPushButton("Remise")
        self.btn_discount.clicked.connect(self.apply_item_discount)
        self.btn_remove = QPushButton("Supprimer ligne")
        self.btn_remove.clicked.connect(self.remove_line)
        btns.addWidget(self.btn_minus); btns.addWidget(self.btn_plus)
        btns.addWidget(self.btn_discount); btns.addWidget(self.btn_remove)
        cart_panel.addLayout(btns)
        
        # Boutons de remise et PDF
        extra_btns = QHBoxLayout()
        self.btn_order_discount = QPushButton("Remise Facture")
        self.btn_order_discount.clicked.connect(self.apply_order_discount)
        self.btn_print_pdf = QPushButton("Imprimer PDF")
        self.btn_print_pdf.clicked.connect(self.print_invoice_pdf)
        extra_btns.addWidget(self.btn_order_discount)
        extra_btns.addWidget(self.btn_print_pdf)
        extra_btns.addStretch()
        cart_panel.addLayout(extra_btns)

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
        
        self.cmb_currency.clear()
        for row in self.conn.execute("SELECT id, code, symbol FROM currencies WHERE active=1 ORDER BY code"):
            self.cmb_currency.addItem(f"{row[1]} ({row[2]})", row[0])

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
        currency_id = self.cmb_currency.currentData()
        if not table_id or not server_id or not currency_id:
            warn(self, "Choisissez une table, un serveur et une devise.")
            return False
        # open existing open order for table?
        exist = self.conn.execute("SELECT id FROM orders WHERE status='open' AND table_id=?", (table_id,)).fetchone()
        if exist:
            self.current_order_id = exist[0]
        else:
            now = datetime.datetime.now().isoformat(timespec="seconds")
            cur = self.conn.execute("INSERT INTO orders(table_id,server_id,status,created_at,currency_id) VALUES(?,?, 'open', ?, ?)",
                               (table_id, server_id, now, currency_id))
            self.current_order_id = cur.lastrowid
            self.conn.commit()
        self.refresh_cart()
        return True

    def refresh_cart(self):
        if not self.current_order_id:
            self.tbl.setRowCount(0)
            self.lbl_total.setText("Total: 0,00")
            return
        rows = list(self.conn.execute("""            
            SELECT oi.id, p.name, oi.qty, oi.price, oi.discount_percent,
                   (oi.qty*oi.price*(1-COALESCE(oi.discount_percent,0)/100)) AS total
            FROM order_items oi JOIN products p ON p.id=oi.product_id
            WHERE oi.order_id=?
            ORDER BY oi.id
        """, (self.current_order_id,)))
        self.tbl.setRowCount(len(rows))
        subtotal = 0.0
        for r_idx, r in enumerate(rows):
            self.tbl.setItem(r_idx, 0, QTableWidgetItem(r[1]))
            self.tbl.setItem(r_idx, 1, QTableWidgetItem(f"{r[3]:.2f}"))
            self.tbl.setItem(r_idx, 2, QTableWidgetItem(str(r[2])))
            self.tbl.setItem(r_idx, 3, QTableWidgetItem(f"{r[4] or 0:.1f}%"))
            self.tbl.setItem(r_idx, 4, QTableWidgetItem(f"{r[5]:.2f}"))
            self.tbl.setItem(r_idx, 5, QTableWidgetItem(str(r[0])))  # hidden id
            subtotal += r[5]
        self.tbl.setColumnHidden(5, True)
        
        # Récupérer la remise de commande
        order_row = self.conn.execute("SELECT discount_amount FROM orders WHERE id=?", (self.current_order_id,)).fetchone()
        order_discount = order_row[0] if order_row and order_row[0] else 0
        
        final_total = subtotal - order_discount
        self.lbl_total.setText(f"Sous-total: {money(subtotal)} | Remise: -{money(order_discount)} | Total: {money(final_total)}")

    def _current_item_id(self):
        row = self.tbl.currentRow()
        if row < 0: return None
        return int(self.tbl.item(row, 5).text())

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
        
        # Calculer le total avec remises
        subtotal = self.conn.execute("""
            SELECT COALESCE(SUM(qty*price*(1-COALESCE(discount_percent,0)/100)),0) 
            FROM order_items WHERE order_id=?
        """, (self.current_order_id,)).fetchone()[0] or 0.0
        
        order_discount = self.conn.execute("SELECT COALESCE(discount_amount,0) FROM orders WHERE id=?", 
                                         (self.current_order_id,)).fetchone()[0] or 0.0
        
        total = subtotal - order_discount
        
        self.conn.execute("UPDATE orders SET status='closed', closed_at=datetime('now'), total=? WHERE id=?",
                          (total, self.current_order_id))
        self.conn.commit()
        info(self, f"Facture clôturée. Total payé: {money(total)}")
        self.current_order_id = None
        self.refresh_cart()

    def apply_item_discount(self):
        """Applique une remise sur un article"""
        item_id = self._current_item_id()
        if not item_id:
            warn(self, "Sélectionnez un article.")
            return
        
        # Récupérer la remise actuelle
        current_discount = self.conn.execute("SELECT COALESCE(discount_percent,0) FROM order_items WHERE id=?", 
                                           (item_id,)).fetchone()[0]
        
        dialog = DiscountDialog(self, current_discount)
        if dialog.exec_() == QDialog.Accepted:
            discount = dialog.get_discount()
            self.conn.execute("UPDATE order_items SET discount_percent=? WHERE id=?", (discount, item_id))
            self.conn.commit()
            self.refresh_cart()

    def apply_order_discount(self):
        """Applique une remise sur toute la commande"""
        if not self.current_order_id:
            warn(self, "Aucune facture ouverte.")
            return
        
        # Récupérer la remise actuelle
        current_discount = self.conn.execute("SELECT COALESCE(discount_amount,0) FROM orders WHERE id=?", 
                                           (self.current_order_id,)).fetchone()[0]
        
        dialog = OrderDiscountDialog(self, current_discount)
        if dialog.exec_() == QDialog.Accepted:
            discount_type, discount_value = dialog.get_discount()
            
            if discount_type == "amount":
                discount_amount = discount_value
            else:  # percentage
                subtotal = self.conn.execute("""
                    SELECT COALESCE(SUM(qty*price*(1-COALESCE(discount_percent,0)/100)),0) 
                    FROM order_items WHERE order_id=?
                """, (self.current_order_id,)).fetchone()[0] or 0.0
                discount_amount = subtotal * discount_value / 100
            
            self.conn.execute("UPDATE orders SET discount_amount=? WHERE id=?", 
                            (discount_amount, self.current_order_id))
            self.conn.commit()
            self.refresh_cart()

    def transfer_table(self):
        """Transfère une commande vers une autre table"""
        if not self.current_order_id:
            warn(self, "Aucune facture ouverte.")
            return
        
        # Récupérer la table actuelle
        current_table = self.conn.execute("SELECT table_id FROM orders WHERE id=?", 
                                        (self.current_order_id,)).fetchone()[0]
        
        dialog = TableTransferDialog(self, current_table)
        if dialog.exec_() == QDialog.Accepted:
            new_table_id = dialog.get_new_table()
            if new_table_id == current_table:
                warn(self, "Sélectionnez une table différente.")
                return
            
            # Vérifier si la nouvelle table a déjà une commande ouverte
            existing = self.conn.execute("SELECT id FROM orders WHERE status='open' AND table_id=?", 
                                       (new_table_id,)).fetchone()
            if existing:
                warn(self, "La table de destination a déjà une commande ouverte.")
                return
            
            # Effectuer le transfert
            self.conn.execute("UPDATE orders SET table_id=? WHERE id=?", (new_table_id, self.current_order_id))
            
            # Enregistrer le transfert dans l'historique
            self.conn.execute("""
                INSERT INTO table_transfers (order_id, from_table_id, to_table_id, transferred_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (self.current_order_id, current_table, new_table_id))
            
            self.conn.commit()
            
            # Mettre à jour la sélection de table
            for i in range(self.cmb_table.count()):
                if self.cmb_table.itemData(i) == new_table_id:
                    self.cmb_table.setCurrentIndex(i)
                    break
            
            info(self, "Commande transférée avec succès.")

    def print_invoice_pdf(self):
        """Génère et ouvre la facture en PDF"""
        if not self.current_order_id:
            warn(self, "Aucune facture ouverte.")
            return
        
        try:
            from pdf_generator import InvoicePDFGenerator
            generator = InvoicePDFGenerator()
            success, result = generator.generate_invoice(self.current_order_id)
            
            if success:
                info(self, f"Facture PDF générée: {result}")
                # Optionnel: ouvrir le PDF
                if ask(self, "Voulez-vous ouvrir le PDF ?"):
                    os.startfile(result)  # Windows
            else:
                warn(self, f"Erreur: {result}")
        except ImportError:
            warn(self, "Module reportlab non installé. Installez-le avec: pip install reportlab")
        except Exception as e:
            warn(self, f"Erreur lors de la génération PDF: {str(e)}")


class DiscountDialog(QDialog):
    def __init__(self, parent=None, current_discount=0):
        super().__init__(parent)
        self.setWindowTitle("Remise sur article")
        self.setModal(True)
        self.resize(300, 120)
        
        layout = QFormLayout(self)
        
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0.0, 100.0)
        self.discount_spin.setSuffix(" %")
        self.discount_spin.setValue(current_discount)
        
        layout.addRow("Remise:", self.discount_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_discount(self):
        return self.discount_spin.value()


class OrderDiscountDialog(QDialog):
    def __init__(self, parent=None, current_discount=0):
        super().__init__(parent)
        self.setWindowTitle("Remise sur facture")
        self.setModal(True)
        self.resize(300, 150)
        
        layout = QFormLayout(self)
        
        self.percentage_radio = QCheckBox("Remise en pourcentage")
        self.percentage_radio.setChecked(True)
        self.percentage_radio.toggled.connect(self.toggle_discount_type)
        layout.addRow(self.percentage_radio)
        
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0.0, 999999.99)
        self.discount_spin.setValue(current_discount)
        self.toggle_discount_type()
        
        layout.addRow("Valeur:", self.discount_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def toggle_discount_type(self):
        if self.percentage_radio.isChecked():
            self.discount_spin.setSuffix(" %")
            self.discount_spin.setRange(0.0, 100.0)
        else:
            self.discount_spin.setSuffix(" €")
            self.discount_spin.setRange(0.0, 999999.99)
    
    def get_discount(self):
        discount_type = "percentage" if self.percentage_radio.isChecked() else "amount"
        return discount_type, self.discount_spin.value()


class TableTransferDialog(QDialog):
    def __init__(self, parent=None, current_table_id=None):
        super().__init__(parent)
        self.setWindowTitle("Transférer vers une table")
        self.setModal(True)
        self.resize(300, 120)
        self.current_table_id = current_table_id
        
        layout = QFormLayout(self)
        
        self.table_combo = QComboBox()
        self.load_tables()
        
        layout.addRow("Nouvelle table:", self.table_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def load_tables(self):
        conn = get_conn()
        for row in conn.execute("SELECT id, number, COALESCE(label,'') AS label FROM tables WHERE active=1 AND id != ? ORDER BY number", 
                               (self.current_table_id,)):
            self.table_combo.addItem(f"#{row['number']} {row['label']}", row[0])
        conn.close()
    
    def get_new_table(self):
        return self.table_combo.currentData()
