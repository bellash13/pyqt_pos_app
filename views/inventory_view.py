from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                             QSpinBox, QDialogButtonBox, QAbstractItemView, 
                             QHeaderView, QComboBox, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from db import get_conn
from utils import info, warn, ask
import datetime

class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = get_conn()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Gestion de l'Inventaire")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        self.btn_adjust = QPushButton("Ajuster Stock")
        self.btn_set_limits = QPushButton("Définir Limites")
        self.btn_refresh = QPushButton("Actualiser")
        self.btn_init_missing = QPushButton("Initialiser Produits Manquants")
        
        self.btn_adjust.clicked.connect(self.adjust_stock)
        self.btn_set_limits.clicked.connect(self.set_limits)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_init_missing.clicked.connect(self.init_missing_products)
        
        btn_layout.addWidget(self.btn_adjust)
        btn_layout.addWidget(self.btn_set_limits)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_init_missing)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Produit", "Stock Actuel", "Stock Min", "Stock Max", "Statut", "Dernière MAJ"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Légende
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Légende:"))
        
        low_label = QLabel("Stock Faible")
        low_label.setStyleSheet("background-color: #ffcccc; padding: 2px;")
        legend_layout.addWidget(low_label)
        
        out_label = QLabel("Rupture")
        out_label.setStyleSheet("background-color: #ff9999; padding: 2px;")
        legend_layout.addWidget(out_label)
        
        ok_label = QLabel("Stock OK")
        ok_label.setStyleSheet("background-color: #ccffcc; padding: 2px;")
        legend_layout.addWidget(ok_label)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
    
    def load_data(self):
        self.table.setRowCount(0)
        
        query = """
            SELECT i.*, p.name as product_name
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE p.active = 1
            ORDER BY p.name
        """
        rows = list(self.conn.execute(query))
        
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            # Produit
            item = QTableWidgetItem(row['product_name'])
            item.setData(Qt.UserRole, row['id'])  # Stocker l'ID de l'inventaire
            item.setData(Qt.UserRole + 1, row['product_id'])  # Stocker l'ID du produit
            self.table.setItem(row_idx, 0, item)
            
            # Stock actuel
            current_stock = QTableWidgetItem(str(row['current_stock']))
            self.table.setItem(row_idx, 1, current_stock)
            
            # Stock min/max
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['min_stock'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(row['max_stock'])))
            
            # Statut et couleur
            status = self._get_stock_status(row['current_stock'], row['min_stock'])
            status_item = QTableWidgetItem(status)
            
            # Colorier selon le statut
            if status == "Rupture":
                color = QColor(255, 153, 153)  # Rouge clair
            elif status == "Stock Faible":
                color = QColor(255, 204, 204)  # Rouge très clair
            else:
                color = QColor(204, 255, 204)  # Vert clair
            
            for col in range(6):
                if self.table.item(row_idx, col):
                    self.table.item(row_idx, col).setBackground(color)
            
            self.table.setItem(row_idx, 4, status_item)
            
            # Dernière mise à jour
            last_updated = row['last_updated'][:19] if row['last_updated'] else ""
            self.table.setItem(row_idx, 5, QTableWidgetItem(last_updated))
    
    def _get_stock_status(self, current, minimum):
        if current <= 0:
            return "Rupture"
        elif current <= minimum:
            return "Stock Faible"
        else:
            return "Stock OK"
    
    def get_selected_inventory_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.UserRole)
        return None
    
    def get_selected_product_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.UserRole + 1)
        return None
    
    def adjust_stock(self):
        inventory_id = self.get_selected_inventory_id()
        if not inventory_id:
            warn(self, "Sélectionnez un produit.")
            return
        
        # Récupérer les données actuelles
        row = self.conn.execute("SELECT * FROM inventory WHERE id=?", (inventory_id,)).fetchone()
        if not row:
            warn(self, "Inventaire introuvable.")
            return
        
        dialog = StockAdjustmentDialog(self)
        dialog.set_current_stock(row['current_stock'])
        
        if dialog.exec_() == QDialog.Accepted:
            new_stock = dialog.get_new_stock()
            try:
                self.conn.execute("""
                    UPDATE inventory 
                    SET current_stock=?, last_updated=datetime('now') 
                    WHERE id=?
                """, (new_stock, inventory_id))
                self.conn.commit()
                self.load_data()
                info(self, "Stock mis à jour avec succès.")
            except Exception as e:
                warn(self, f"Erreur lors de la mise à jour: {str(e)}")
    
    def set_limits(self):
        inventory_id = self.get_selected_inventory_id()
        if not inventory_id:
            warn(self, "Sélectionnez un produit.")
            return
        
        # Récupérer les données actuelles
        row = self.conn.execute("SELECT * FROM inventory WHERE id=?", (inventory_id,)).fetchone()
        if not row:
            warn(self, "Inventaire introuvable.")
            return
        
        dialog = StockLimitsDialog(self)
        dialog.set_limits(row['min_stock'], row['max_stock'])
        
        if dialog.exec_() == QDialog.Accepted:
            min_stock, max_stock = dialog.get_limits()
            try:
                self.conn.execute("""
                    UPDATE inventory 
                    SET min_stock=?, max_stock=?, last_updated=datetime('now') 
                    WHERE id=?
                """, (min_stock, max_stock, inventory_id))
                self.conn.commit()
                self.load_data()
                info(self, "Limites de stock mises à jour.")
            except Exception as e:
                warn(self, f"Erreur lors de la mise à jour: {str(e)}")
    
    def init_missing_products(self):
        """Initialise l'inventaire pour les produits qui n'en ont pas"""
        try:
            query = """
                INSERT INTO inventory (product_id, current_stock, min_stock, max_stock, last_updated)
                SELECT p.id, 0, 10, 100, datetime('now')
                FROM products p
                WHERE p.active = 1 
                AND p.id NOT IN (SELECT DISTINCT product_id FROM inventory)
            """
            cursor = self.conn.execute(query)
            count = cursor.rowcount
            self.conn.commit()
            
            if count > 0:
                info(self, f"{count} produits initialisés dans l'inventaire.")
                self.load_data()
            else:
                info(self, "Aucun nouveau produit à initialiser.")
        except Exception as e:
            warn(self, f"Erreur lors de l'initialisation: {str(e)}")


class StockAdjustmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajuster le Stock")
        self.setModal(True)
        self.resize(300, 150)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        self.current_label = QLabel()
        self.new_stock_spin = QSpinBox()
        self.new_stock_spin.setRange(0, 99999)
        
        layout.addRow("Stock actuel:", self.current_label)
        layout.addRow("Nouveau stock:", self.new_stock_spin)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def set_current_stock(self, stock):
        self.current_label.setText(str(stock))
        self.new_stock_spin.setValue(stock)
    
    def get_new_stock(self):
        return self.new_stock_spin.value()


class StockLimitsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Limites de Stock")
        self.setModal(True)
        self.resize(300, 150)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 99999)
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 99999)
        
        layout.addRow("Stock minimum:", self.min_spin)
        layout.addRow("Stock maximum:", self.max_spin)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def set_limits(self, min_stock, max_stock):
        self.min_spin.setValue(min_stock)
        self.max_spin.setValue(max_stock)
    
    def get_limits(self):
        return self.min_spin.value(), self.max_spin.value()
    
    def accept(self):
        if self.min_spin.value() >= self.max_spin.value():
            warn(self, "Le stock maximum doit être supérieur au stock minimum.")
            return
        super().accept()
