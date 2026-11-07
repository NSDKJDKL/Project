from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import sys
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self, profile_id, db_manager):
        super().__init__()
        self.profile_id = profile_id
        self.db = db_manager
        
        self.setWindowTitle("Майнинг Ферма")
        self.resize(600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        status_layout = QHBoxLayout()
        
        self.lbl_balance = QLabel("💰 $0.0")
        self.lbl_crypto = QLabel("🪙 0.0000")
        self.lbl_temp = QLabel("🌡️ 24°C")
        
        for lbl in [self.lbl_balance, self.lbl_crypto, self.lbl_temp]:
            lbl.setFont(QFont("Arial", 12))
            
        status_layout.addWidget(self.lbl_balance)
        status_layout.addWidget(self.lbl_crypto)
        status_layout.addWidget(self.lbl_temp)
        main_layout.addLayout(status_layout)
        self.grid_layout = QGridLayout()
        self.slot_buttons = []
        
        for i in range(16):
            btn = QPushButton(f"Слот {i+1}\nПусто")
            btn.setFixedHeight(80)
            btn.setStyleSheet("background-color: #2e2e2e; color: white; border: 1px solid #555;")
            btn.clicked.connect(lambda checked, idx=i: self.on_slot_clicked(idx))
            
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(btn, row, col)
            self.slot_buttons.append(btn)
            
        main_layout.addLayout(self.grid_layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_tick)
        self.timer.start(1000)
        
        self.update_ui()

    def update_ui(self):
        profile = self.db.get_profile(self.profile_id)
        if profile:
            self.lbl_balance.setText(f"💰 ${profile['balance']:.2f}")
            self.lbl_crypto.setText(f"🪙 {profile['crypto_balance']:.4f}")
        inventory = self.db.get_inventory(self.profile_id)
        
        for btn in self.slot_buttons:
            btn.setText("Пусто")
            
        for item in inventory:
            slot_idx = item['slot_index']
            if 0 <= slot_idx < 16:
                self.slot_buttons[slot_idx].setText(f"{item['name']}\n{item['hashrate']} MH/s\n⚙️ {item['condition']:.0f}%")

    def game_tick(self):
        self.db.process_tick(self.profile_id)
        self.update_ui()

    def on_slot_clicked(self, slot_index):
        print(f"Клик по слоту {slot_index}")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = DatabaseManager()
    
    profiles = db.get_profiles()
    if not profiles:
        test_id = db.create_profile("TestVitaly")
    else:
        test_id = profiles[0]['id']
    
    window = MainWindow(test_id, db)
    window.show()
    sys.exit(app.exec())