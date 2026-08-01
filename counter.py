import sys
import os
import shutil
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QMessageBox, 
                               QStackedWidget, QFrame)
from PySide6.QtCore import QTimer, QThread, Signal, Qt
from PySide6.QtGui import QFont

# ========================
# 1. UPDATE ENGINE
# ========================

class UpdateEngine(QThread):
    """Update engine - ikurura counter.py iva kuri GitHub"""
    update_status = Signal(str)
    update_done = Signal(bool, str)  # has_update, commit_message
    
    def __init__(self, repo_url):
        super().__init__()
        self.repo_url = repo_url
        self.app_path = Path.cwd()
        self.update_path = self.app_path / "._update_cache"
        self.commit_message = ""
        self.new_file_hash = None
        self.current_file_hash = None
        
    def run(self):
        try:
            # ====== 1. Reba niba hari internet ======
            if not self._has_internet():
                self.update_status.emit("⚠️ Nta internet")
                self.update_done.emit(False, "")
                return
                
            self.update_status.emit("📥 Reba update...")
            
            # ====== 2. Kurura dosiye counter.py iva kuri GitHub ======
            raw_url = self.repo_url.replace(
                "https://github.com/",
                "https://raw.githubusercontent.com/"
            ) + "/main/counter.py"
            
            import requests
            response = requests.get(raw_url, timeout=30)
            
            if response.status_code != 200:
                raw_url = self.repo_url.replace(
                    "https://github.com/",
                    "https://raw.githubusercontent.com/"
                ) + "/master/counter.py"
                response = requests.get(raw_url, timeout=30)
                
            if response.status_code != 200:
                self.update_status.emit("❌ Ntashobora kugera kuri GitHub")
                self.update_done.emit(False, "")
                return
                
            # ====== 3. Kura commit message ======
            api_url = self.repo_url.replace(
                "https://github.com/",
                "https://api.github.com/repos/"
            ) + "/commits/main"
            
            commit_response = requests.get(api_url, timeout=30)
            if commit_response.status_code == 200:
                commits = commit_response.json()
                if commits and len(commits) > 0:
                    self.commit_message = commits[0].get('commit', {}).get('message', 'Update')
            else:
                api_url = self.repo_url.replace(
                    "https://github.com/",
                    "https://api.github.com/repos/"
                ) + "/commits/master"
                commit_response = requests.get(api_url, timeout=30)
                if commit_response.status_code == 200:
                    commits = commit_response.json()
                    if commits and len(commits) > 0:
                        self.commit_message = commits[0].get('commit', {}).get('message', 'Update')
            
            # ====== 4. Hash ya dosiye ======
            new_content = response.content
            self.new_file_hash = hashlib.md5(new_content).hexdigest()
            
            current_file = self.app_path / "counter.py"
            if current_file.exists():
                with open(current_file, 'rb') as f:
                    current_content = f.read()
                    self.current_file_hash = hashlib.md5(current_content).hexdigest()
            else:
                self.current_file_hash = None
                
            # ====== 5. Reba niba hari update ======
            if self.new_file_hash != self.current_file_hash:
                # Kubika dosiye nshya
                self.update_path.mkdir(exist_ok=True)
                
                # Andika dosiye nshya
                with open(current_file, 'wb') as f:
                    f.write(new_content)
                
                self.update_status.emit(f"✅ Update yakoze: {self.commit_message[:50]}...")
                self.update_done.emit(True, self.commit_message)
            else:
                self.update_status.emit("ℹ️ Nta update ihari")
                self.update_done.emit(False, "")
                
        except Exception as e:
            self.update_status.emit(f"❌ Error: {str(e)}")
            self.update_done.emit(False, "")
            
    def _has_internet(self):
        try:
            import requests
            requests.get("https://github.com", timeout=5)
            return True
        except:
            return False

# ========================
# 2. POROGARAMU NKURU
# ========================

class CounterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.repo_url = "https://github.com/sofferrwanda-ctrl/updatezindiro-ui"
        self.update_engine = None
        
        # Setup UI
        self.setup_ui()
        
        # Ereka Welcome page mbere
        self.show_welcome_page()
        
    def setup_ui(self):
        self.setWindowTitle("Counter App v1.0")
        self.setGeometry(100, 100, 500, 550)
        self.setMinimumSize(400, 450)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ========== HEADER ==========
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("🚀 Counter App")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # ========== STACKED WIDGET ==========
        self.stacked_widget = QStackedWidget()
        
        self.welcome_page = self.create_welcome_page()
        self.stacked_widget.addWidget(self.welcome_page)
        
        self.counter_page = self.create_counter_page()
        self.stacked_widget.addWidget(self.counter_page)
        
        main_layout.addWidget(self.stacked_widget)
        
        # ========== UPDATE BUTTON ==========
        update_layout = QHBoxLayout()
        update_layout.addStretch()
        
        self.update_btn = QPushButton("🔄 Check for Updates")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        """)
        self.update_btn.clicked.connect(self.check_for_updates)
        update_layout.addWidget(self.update_btn)
        update_layout.addStretch()
        
        main_layout.addLayout(update_layout)
        
        # ========== STATUS / MESSAGE ==========
        self.status_label = QLabel("✅ Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                color: #7f8c8d;
                font-size: 12px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # ========== ABOUT ==========
        about_btn = QPushButton("ℹ️ About")
        about_btn.setStyleSheet(self.button_style("#34495e"))
        about_btn.clicked.connect(self.show_about)
        main_layout.addWidget(about_btn, alignment=Qt.AlignCenter)
        
    def create_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("👋")
        icon_label.setFont(QFont("Arial", 60))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        welcome_text = QLabel("Welcome!")
        welcome_text.setFont(QFont("Arial", 28, QFont.Bold))
        welcome_text.setAlignment(Qt.AlignCenter)
        welcome_text.setStyleSheet("color: #2c3e50;")
        layout.addWidget(welcome_text)
        
        sub_text = QLabel("Kanda Start ngo utangire kubara")
        sub_text.setFont(QFont("Arial", 14))
        sub_text.setAlignment(Qt.AlignCenter)
        sub_text.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(sub_text)
        
        start_btn = QPushButton("🚀 Start")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        start_btn.clicked.connect(self.go_to_counter)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        return page
        
    def create_counter_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        
        self.counter_label = QLabel("0")
        self.counter_label.setFont(QFont("Arial", 64, QFont.Bold))
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 30px;
                background-color: #ecf0f1;
                border-radius: 15px;
                min-height: 100px;
            }
        """)
        layout.addWidget(self.counter_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_increment = QPushButton("➕ Ondera")
        btn_increment.setStyleSheet(self.button_style("#27ae60"))
        btn_increment.clicked.connect(self.increment)
        
        btn_decrement = QPushButton("➖ Gabanura")
        btn_decrement.setStyleSheet(self.button_style("#e74c3c"))
        btn_decrement.clicked.connect(self.decrement)
        
        btn_reset = QPushButton("🔄 Siba")
        btn_reset.setStyleSheet(self.button_style("#3498db"))
        btn_reset.clicked.connect(self.reset)
        
        btn_layout.addWidget(btn_increment)
        btn_layout.addWidget(btn_decrement)
        btn_layout.addWidget(btn_reset)
        layout.addLayout(btn_layout)
        
        back_btn = QPushButton("⬅️ Back")
        back_btn.setStyleSheet(self.button_style("#95a5a6"))
        back_btn.clicked.connect(self.go_to_welcome)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        return page
        
    def button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """
        
    # ========== NAVIGATION ==========
    
    def show_welcome_page(self):
        self.stacked_widget.setCurrentIndex(0)
        self.title_label.setText("👋 Welcome")
        
    def go_to_counter(self):
        self.stacked_widget.setCurrentIndex(1)
        self.title_label.setText("📊 Counter")
        
    def go_to_welcome(self):
        self.show_welcome_page()
        
    # ========== IBIKORWA BYA COUNTER ==========
    
    def increment(self):
        self.counter += 1
        self.counter_label.setText(str(self.counter))
        
    def decrement(self):
        self.counter -= 1
        self.counter_label.setText(str(self.counter))
        
    def reset(self):
        self.counter = 0
        self.counter_label.setText("0")
        
    # ========== UPDATE SYSTEM ==========
    
    def check_for_updates(self):
        """Kora update iyo ukanda button"""
        if self.update_engine and self.update_engine.isRunning():
            self.status_label.setText("⏳ Update ikora...")
            return
            
        # Hindura button
        self.update_btn.setEnabled(False)
        self.update_btn.setText("⏳ Checking...")
        self.status_label.setText("🔄 Reba update...")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                color: #e65100;
                font-size: 12px;
                background-color: #fff3e0;
                border-radius: 5px;
            }
        """)
        
        self.update_engine = UpdateEngine(self.repo_url)
        self.update_engine.update_status.connect(self.update_status)
        self.update_engine.update_done.connect(self.update_done)
        self.update_engine.start()
        
    def update_status(self, message):
        self.status_label.setText(message)
        
    def update_done(self, has_update, commit_message):
        """Iyo update irangiye"""
        # Subiza button
        self.update_btn.setEnabled(True)
        self.update_btn.setText("🔄 Check for Updates")
        
        if has_update:
            # Update yakoze
            self.status_label.setText(f"✅ Update yakoze: {commit_message[:50]}...")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    color: #2e7d32;
                    font-size: 12px;
                    background-color: #e8f5e9;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            
            # Alert box
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("✅ Update yakoze!")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(
                f"""
                <div style="text-align: center;">
                    <h2 style="color: #27ae60;">✅ Update yakoze!</h2>
                    <p style="font-size: 14px; color: #34495e;">
                        <b>New commit:</b><br>
                        <span style="color: #3498db;">{commit_message[:200]}</span>
                    </p>
                    <p style="font-size: 12px; color: #7f8c8d;">
                        Dosiye counter.py yasimbuwe.<br>
                        Porogaramu izikubura (restart) ngo ibyubahwe.
                    </p>
                </div>
                """
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            self._restart_app()
        else:
            # Nta update
            self.status_label.setText("ℹ️ No update available")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    color: #7f8c8d;
                    font-size: 12px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                }
            """)
            
            # Alert box
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("ℹ️ No Update")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(
                """
                <div style="text-align: center;">
                    <h2 style="color: #7f8c8d;">ℹ️ No Update Available</h2>
                    <p style="font-size: 14px; color: #34495e;">
                        You already have the latest version.
                    </p>
                    <p style="font-size: 12px; color: #95a5a6;">
                        No new commits found on GitHub.
                    </p>
                </div>
                """
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
    def _restart_app(self):
        try:
            self.close()
            python = sys.executable
            script = sys.argv[0]
            import subprocess
            subprocess.Popen([python, script])
            sys.exit(0)
        except:
            pass
            
    # ========== ABOUT ==========
    
    def show_about(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("ℹ️ About Counter App")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(
            """
            <div style="text-align: center;">
                <h1 style="color: #2c3e50;">🚀 Counter App</h1>
                <p style="font-size: 16px; color: #34495e;">
                    <b>Version:</b> 1.0.1<br><br>
                    <b>Developed by:</b> <span style="color: #3498db;">Kevin</span><br><br>
                    <b>Technology:</b> PySide6<br><br>
                    <span style="color: #7f8c8d; font-size: 12px;">
                        © 2026 - Soffer Rwanda
                    </span>
                </p>
            </div>
            """
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

# ========================
# 4. KUTANGIZA POROGARAMU
# ========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = CounterApp()
    window.show()
    
    sys.exit(app.exec())