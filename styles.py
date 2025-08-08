
MAIN_QSS = r'''
QWidget {
    font-family: Segoe UI, Arial;
    font-size: 12pt;
}
QToolBar { spacing: 8px; }
QPushButton {
    border: 1px solid #888;
    border-radius: 8px;
    padding: 6px 10px;
}
QPushButton:hover { background: #efefef; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {
    border: 1px solid #999;
    border-radius: 6px;
    padding: 4px 6px;
}
QHeaderView::section {
    background: #f0f0f0;
    padding: 6px;
    border: none;
}
QTableView {
    gridline-color: #ddd;
    selection-background-color: #d0e8ff;
}
QTabWidget::pane {
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 4px;
}
'''
