from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                             QLineEdit, QDoubleSpinBox, QCheckBox, QDialogButtonBox,
                             QAbstractItemView, QHeaderView)
from PyQt5.QtCore import Qt
from db import get_conn
from utils import info, warn, ask

class ManageCurrencies(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = get_conn()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter")
        self.btn_edit = QPushButton("Modifier")
        self.btn_delete = QPushButton("Supprimer")
        self.btn_refresh = QPushButton("Actualiser")
        
        self.btn_add.clicked.connect(self.add_currency)
        self.btn_edit.clicked.connect(self.edit_currency)
        self.btn_delete.clicked.connect(self.delete_currency)
        self.btn_refresh.clicked.connect(self.load_data)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Symbole", "Taux de change", "Actif"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
    
    def load_data(self):
        self.table.setRowCount(0)
        rows = list(self.conn.execute("SELECT id, code, name, symbol, exchange_rate, active FROM currencies ORDER BY code"))
        
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row[1]))  # code
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[2]))  # name
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[3]))  # symbol
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{row[4]:.4f}"))  # exchange_rate
            self.table.setItem(row_idx, 4, QTableWidgetItem("Oui" if row[5] else "Non"))  # active
            
            # Stocker l'ID dans la première cellule
            self.table.item(row_idx, 0).setData(Qt.UserRole, row[0])
    
    def get_selected_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.UserRole)
        return None
    
    def add_currency(self):
        dialog = CurrencyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.conn.execute("""
                    INSERT INTO currencies (code, name, symbol, exchange_rate, active)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['code'], data['name'], data['symbol'], data['exchange_rate'], data['active']))
                self.conn.commit()
                self.load_data()
                info(self, "Devise ajoutée avec succès.")
            except Exception as e:
                warn(self, f"Erreur lors de l'ajout: {str(e)}")
    
    def edit_currency(self):
        currency_id = self.get_selected_id()
        if not currency_id:
            warn(self, "Sélectionnez une devise à modifier.")
            return
        
        # Récupérer les données actuelles
        row = self.conn.execute("SELECT * FROM currencies WHERE id=?", (currency_id,)).fetchone()
        if not row:
            warn(self, "Devise introuvable.")
            return
        
        dialog = CurrencyDialog(self)
        dialog.set_data({
            'code': row[1],
            'name': row[2], 
            'symbol': row[3],
            'exchange_rate': row[4],
            'active': bool(row[5])
        })
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.conn.execute("""
                    UPDATE currencies SET code=?, name=?, symbol=?, exchange_rate=?, active=?
                    WHERE id=?
                """, (data['code'], data['name'], data['symbol'], data['exchange_rate'], data['active'], currency_id))
                self.conn.commit()
                self.load_data()
                info(self, "Devise modifiée avec succès.")
            except Exception as e:
                warn(self, f"Erreur lors de la modification: {str(e)}")
    
    def delete_currency(self):
        currency_id = self.get_selected_id()
        if not currency_id:
            warn(self, "Sélectionnez une devise à supprimer.")
            return
        
        if ask(self, "Êtes-vous sûr de vouloir supprimer cette devise ?"):
            try:
                self.conn.execute("DELETE FROM currencies WHERE id=?", (currency_id,))
                self.conn.commit()
                self.load_data()
                info(self, "Devise supprimée avec succès.")
            except Exception as e:
                warn(self, f"Erreur lors de la suppression: {str(e)}")


class CurrencyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Devise")
        self.setModal(True)
        self.resize(400, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        self.code_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.symbol_edit = QLineEdit()
        self.exchange_rate_spin = QDoubleSpinBox()
        self.exchange_rate_spin.setDecimals(4)
        self.exchange_rate_spin.setRange(0.0001, 9999999.9999)
        self.exchange_rate_spin.setValue(1.0)
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)
        
        layout.addRow("Code:", self.code_edit)
        layout.addRow("Nom:", self.name_edit)
        layout.addRow("Symbole:", self.symbol_edit)
        layout.addRow("Taux de change:", self.exchange_rate_spin)
        layout.addRow("Actif:", self.active_check)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_data(self):
        return {
            'code': self.code_edit.text().strip().upper(),
            'name': self.name_edit.text().strip(),
            'symbol': self.symbol_edit.text().strip(),
            'exchange_rate': self.exchange_rate_spin.value(),
            'active': self.active_check.isChecked()
        }
    
    def set_data(self, data):
        self.code_edit.setText(data.get('code', ''))
        self.name_edit.setText(data.get('name', ''))
        self.symbol_edit.setText(data.get('symbol', ''))
        self.exchange_rate_spin.setValue(data.get('exchange_rate', 1.0))
        self.active_check.setChecked(data.get('active', True))
    
    def accept(self):
        data = self.get_data()
        if not data['code'] or not data['name'] or not data['symbol']:
            warn(self, "Tous les champs sont obligatoires.")
            return
        super().accept()
