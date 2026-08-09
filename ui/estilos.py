ESTILO_GLOBAL = """
QMainWindow, QWidget { background: #f6f7fb; color: #1f2937; font-family: Inter, 'Noto Sans', sans-serif; font-size: 14px; }
QTabWidget::pane { border: 0; }
QTabBar::tab { padding: 14px 26px; color: #64748b; background: transparent; border-bottom: 3px solid transparent; }
QTabBar::tab:selected { color: #2563eb; border-bottom-color: #2563eb; font-weight: 600; }
QPushButton { background: #2563eb; color: white; border: 0; border-radius: 7px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #1d4ed8; }
QPushButton[secondary="true"] { background: #e8edf5; color: #334155; }
QPushButton[danger="true"] { background: #dc2626; }
QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox { background: white; border: 1px solid #dbe2ea; border-radius: 7px; padding: 7px; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border-color: #2563eb; }
QTableWidget, QListWidget { background: white; border: 1px solid #e2e8f0; border-radius: 9px; alternate-background-color: #f8fafc; }
QHeaderView::section { background: #eef2f7; color: #475569; border: 0; padding: 9px; font-weight: 600; }
QProgressBar { background: #e2e8f0; border: 0; border-radius: 6px; height: 12px; text-align: center; }
QProgressBar::chunk { background: #3b82f6; border-radius: 6px; }
QFrame#card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; }
QLabel#titulo { font-size: 25px; font-weight: 700; color: #0f172a; }
QLabel#subtitulo { font-size: 16px; font-weight: 650; color: #334155; }
QLabel#valorGrande { font-size: 23px; font-weight: 700; color: #0f172a; }
QLabel[muted="true"] { color: #64748b; }
"""
