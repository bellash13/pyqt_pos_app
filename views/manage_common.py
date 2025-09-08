
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from db import get_conn
from utils import ask, info, hash_password

class CrudBase(QWidget):
    def __init__(self, headers):
        super().__init__()
        self.conn = get_conn()
        root = QVBoxLayout(self)
        btns = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter")
        self.btn_del = QPushButton("Supprimer")
        btns.addWidget(self.btn_add); btns.addWidget(self.btn_del); btns.addStretch(1)
        root.addLayout(btns)

        self.tbl = QTableWidget(0, len(headers))
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

class ManageCategories(CrudBase):
    def __init__(self):
        super().__init__(["Nom", "Actif"])
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.del_row)
        self.reload()

    def reload(self):
        rows = list(self.conn.execute("SELECT id, name, active FROM categories ORDER BY name"))
        self.tbl.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl.setItem(i,0,QTableWidgetItem(r[1]))
            self.tbl.setItem(i,1,QTableWidgetItem("Oui" if r[2] else "Non"))
            self.tbl.setItem(i,2,QTableWidgetItem(str(r[0])))
        self.tbl.setColumnHidden(2, True)

    def add_row(self):
        self.conn.execute("INSERT INTO categories(name,active) VALUES(?,?)", ("Nouvelle catégorie", 1))
        self.conn.commit()
        self.reload()

    def del_row(self):
        row = self.tbl.currentRow()
        if row<0: return
        cid = int(self.tbl.item(row,2).text())
        if ask(self, "Supprimer la catégorie sélectionnée ?"):
            self.conn.execute("DELETE FROM categories WHERE id=?", (cid,))
            self.conn.commit()
            self.reload()

class ManageProducts(CrudBase):
    def __init__(self):
        super().__init__(["Nom", "Prix", "Catégorie", "Actif"])
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.del_row)
        self.reload()

    def reload(self):
        rows = list(self.conn.execute("""            SELECT p.id, p.name, p.price, c.name AS cat, p.active
            FROM products p JOIN categories c ON c.id=p.category_id
            ORDER BY c.name, p.name
        """))
        self.tbl.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl.setItem(i,0,QTableWidgetItem(r[1]))
            self.tbl.setItem(i,1,QTableWidgetItem(f"{r[2]:.2f}"))
            self.tbl.setItem(i,2,QTableWidgetItem(r[3]))
            self.tbl.setItem(i,3,QTableWidgetItem("Oui" if r[4] else "Non"))
            self.tbl.setItem(i,4,QTableWidgetItem(str(r[0])))
        self.tbl.setColumnHidden(4, True)

    def add_row(self):
        cat = self.conn.execute("SELECT id FROM categories ORDER BY id LIMIT 1").fetchone()
        if not cat:
            info(self, "Créez d'abord une catégorie.")
            return
        self.conn.execute("INSERT INTO products(name,price,category_id,active) VALUES(?,?,?,1)",
                          ("Nouveau produit", 1.0, cat[0]))
        self.conn.commit()
        self.reload()

    def del_row(self):
        row = self.tbl.currentRow()
        if row<0: return
        pid = int(self.tbl.item(row,4).text())
        if ask(self, "Supprimer le produit sélectionné ?"):
            self.conn.execute("DELETE FROM products WHERE id=?", (pid,))
            self.conn.commit()
            self.reload()

class ManageTables(CrudBase):
    def __init__(self):
        super().__init__(["Numéro", "Libellé", "Actif"])
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.del_row)
        self.reload()

    def reload(self):
        rows = list(self.conn.execute("SELECT id, number, COALESCE(label,'') label, active FROM tables ORDER BY number"))
        self.tbl.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl.setItem(i,0,QTableWidgetItem(str(r[1])))
            self.tbl.setItem(i,1,QTableWidgetItem(r[2]))
            self.tbl.setItem(i,2,QTableWidgetItem("Oui" if r[3] else "Non"))
            self.tbl.setItem(i,3,QTableWidgetItem(str(r[0])))
        self.tbl.setColumnHidden(3, True)

    def add_row(self):
        row = self.conn.execute("SELECT COALESCE(MAX(number),0)+1 FROM tables").fetchone()
        n = row[0] or 1
        self.conn.execute("INSERT INTO tables(number,label,active) VALUES(?,?,1)", (n, f"Table {n}"))
        self.conn.commit()
        self.reload()

    def del_row(self):
        row = self.tbl.currentRow()
        if row<0: return
        tid = int(self.tbl.item(row,3).text())
        if ask(self, "Supprimer la table sélectionnée ?"):
            self.conn.execute("DELETE FROM tables WHERE id=?", (tid,))
            self.conn.commit()
            self.reload()

class ManageServers(CrudBase):
    def __init__(self):
        super().__init__(["Nom", "Actif"])
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.del_row)
        # Ajout du bouton Modifier
        self.btn_edit = QPushButton("Modifier")
        self.btn_edit.clicked.connect(self.edit_row)
        self.layout().itemAt(0).layout().insertWidget(1, self.btn_edit)
        self.reload()

    def reload(self):
        rows = list(self.conn.execute("SELECT id, name, active FROM servers ORDER BY name"))
        self.tbl.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl.setItem(i,0,QTableWidgetItem(r[1]))
            self.tbl.setItem(i,1,QTableWidgetItem("Oui" if r[2] else "Non"))
            self.tbl.setItem(i,2,QTableWidgetItem(str(r[0])))
        self.tbl.setColumnHidden(2, True)
        # Sélection automatique de la première ligne si le tableau n'est pas vide
        if len(rows) > 0:
            self.tbl.setCurrentCell(0, 0)
            self.btn_edit.setEnabled(True)
            self.btn_del.setEnabled(True)
        else:
            self.btn_edit.setEnabled(False)
            self.btn_del.setEnabled(False)
        # Connecter le signal de sélection pour activer/désactiver les boutons
        self.tbl.itemSelectionChanged.connect(self.update_buttons_state)

    def update_buttons_state(self):
        row = self.tbl.currentRow()
        has_selection = row >= 0 and self.tbl.rowCount() > 0
        self.btn_edit.setEnabled(has_selection)
        self.btn_del.setEnabled(has_selection)

    def add_row(self):
        self.conn.execute("INSERT INTO servers(name,active) VALUES(?,1)", ("Nouveau serveur",))
        self.conn.commit()
        self.reload()

    def edit_row(self):
        row = self.tbl.currentRow()
        if row < 0:
            info(self, "Sélectionnez un serveur à modifier.")
            return
        id_item = self.tbl.item(row,2)
        name_item = self.tbl.item(row,0)
        active_item = self.tbl.item(row,1)
        if id_item is None or name_item is None or active_item is None:
            info(self, "La sélection est invalide. Veuillez réessayer.")
            return
        sid = int(id_item.text())
        name = name_item.text()
        active = 1 if active_item.text() == "Oui" else 0
        from PyQt5.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Modifier le serveur", "Nom du serveur:", text=name)
        if not ok or not new_name.strip():
            return
        new_active = active
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Activer le serveur", "Le serveur est-il actif ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes if active else QMessageBox.No)
        if reply == QMessageBox.Yes:
            new_active = 1
        else:
            new_active = 0
        self.conn.execute("UPDATE servers SET name=?, active=? WHERE id=?", (new_name, new_active, sid))
        self.conn.commit()
        self.reload()

    def del_row(self):
        row = self.tbl.currentRow()
        if row < 0:
            info(self, "Sélectionnez un serveur à supprimer.")
            return
        id_item = self.tbl.item(row,2)
        if id_item is None:
            info(self, "La sélection est invalide. Veuillez réessayer.")
            return
        sid = int(id_item.text())
        if ask(self, "Supprimer le serveur sélectionné ?"):
            self.conn.execute("DELETE FROM servers WHERE id=?", (sid,))
            self.conn.commit()
            self.reload()

class ManageUsers(CrudBase):
    def __init__(self):
        super().__init__(["Utilisateur", "Rôle", "Actif"])
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.del_row)
        self.reload()

    def reload(self):
        rows = list(self.conn.execute("SELECT id, username, role, active FROM users ORDER BY username"))
        self.tbl.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl.setItem(i,0,QTableWidgetItem(r[1]))
            self.tbl.setItem(i,1,QTableWidgetItem(r[2]))
            self.tbl.setItem(i,2,QTableWidgetItem("Oui" if r[3] else "Non"))
            self.tbl.setItem(i,3,QTableWidgetItem(str(r[0])))
        self.tbl.setColumnHidden(3, True)

    def add_row(self):
        self.conn.execute("INSERT INTO users(username,password_hash,role,active) VALUES(?,?,?,0)",
                          ("nouvel_utilisateur", hash_password("changeme"), "caissier", 0))
        self.conn.commit()
        self.reload()

    def del_row(self):
        row = self.tbl.currentRow()
        if row<0: return
        uid = int(self.tbl.item(row,3).text())
        if ask(self, "Supprimer l'utilisateur ?"):
            self.conn.execute("DELETE FROM users WHERE id=?", (uid,))
            self.conn.commit()
            self.reload()
