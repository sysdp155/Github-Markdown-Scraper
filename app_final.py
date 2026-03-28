import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QProgressBar, QFileDialog, QComboBox, QSpinBox)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from github_scraper import GitHubRandomScraper
from pathlib import Path

class ScraperThread(QThread):
    progress = Signal(str, int)
    finished = Signal(int)
    
    def __init__(self, country, output_dir, max_users):
        super().__init__()
        self.country = country
        self.output_dir = output_dir
        self.max_users = max_users
        self.scraper = None
        
    def run(self):
        try:
            self.scraper = GitHubRandomScraper()
            count = self.scraper.scrape_random_users(
                self.country, 
                self.output_dir, 
                self.max_users,
                self.update_progress
            )
            self.finished.emit(count)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}", 0)
            self.finished.emit(-1)
    
    def update_progress(self, message, percent):
        self.progress.emit(message, percent)
    
    def stop(self):
        if self.scraper:
            self.scraper.stop()

class ModernScraperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scraper_thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('GitHub Markdown Scraper')
        self.setGeometry(100, 100, 700, 550)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #007acc;
                border: 2px solid #3d3d3d;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #808080;
            }
            #stopButton {
                background-color: #d13438;
            }
            #stopButton:hover {
                background-color: #a82a2d;
            }
            #stopButton:pressed {
                background-color: #7f2022;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
            QProgressBar {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('GitHub Markdown Scraper')
        title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel('Randomly scrape .md files from GitHub users by country')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(subtitle)
        
        # Country Filter
        country_layout = QHBoxLayout()
        country_label = QLabel('Country Filter:')
        self.country_combo = QComboBox()
        self.country_combo.addItems([
            'United States', 'China', 'India', 'United Kingdom', 'Germany',
            'Canada', 'France', 'Japan', 'Brazil', 'Russia', 'South Korea',
            'Australia', 'Spain', 'Italy', 'Netherlands', 'Sweden', 'Poland',
            'Switzerland', 'Singapore', 'Israel', 'Ukraine', 'Turkey', 'Mexico',
            'Argentina', 'Belgium', 'Austria', 'Denmark', 'Norway', 'Finland',
            'Ireland', 'New Zealand', 'Portugal', 'Czech Republic', 'Romania',
            'Greece', 'Hungary', 'Vietnam', 'Thailand', 'Indonesia', 'Malaysia',
            'Philippines', 'Pakistan', 'Bangladesh', 'Egypt', 'South Africa',
            'Nigeria', 'Kenya', 'Chile', 'Colombia', 'Peru'
        ])
        country_layout.addWidget(country_label)
        country_layout.addWidget(self.country_combo)
        layout.addLayout(country_layout)
        
        # Max Users
        users_layout = QHBoxLayout()
        users_label = QLabel('Max Users to Scrape:')
        self.users_spinbox = QSpinBox()
        self.users_spinbox.setMinimum(1)
        self.users_spinbox.setMaximum(50)
        self.users_spinbox.setValue(10)
        self.users_spinbox.setMaximumWidth(100)
        users_layout.addWidget(users_label)
        users_layout.addWidget(self.users_spinbox)
        users_layout.addStretch()
        layout.addLayout(users_layout)
        
        # Output Directory
        output_layout = QHBoxLayout()
        output_label = QLabel('Output Folder:')
        self.output_input = QLineEdit()
        self.output_input.setText('scraped_files')
        self.browse_button = QPushButton('Browse')
        self.browse_button.setMaximumWidth(100)
        self.browse_button.clicked.connect(self.browse_folder)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.browse_button)
        layout.addLayout(output_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Scraping')
        self.start_button.clicked.connect(self.start_scraping)
        
        self.stop_button = QPushButton('Stop')
        self.stop_button.setObjectName('stopButton')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scraping)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log Output
        log_label = QLabel('Log:')
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_input.setText(folder)
    
    def start_scraping(self):
        country = self.country_combo.currentText()
        output_dir = self.output_input.text().strip()
        max_users = self.users_spinbox.value()
        
        self.log(f'Starting random scraper for country: {country}')
        self.log(f'Max users: {max_users}')
        self.log(f'Output directory: {output_dir}')
        self.log('---')
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.scraper_thread = ScraperThread(country, output_dir, max_users)
        self.scraper_thread.progress.connect(self.update_progress)
        self.scraper_thread.finished.connect(self.scraping_finished)
        self.scraper_thread.start()
    
    def stop_scraping(self):
        if self.scraper_thread:
            self.log('Stopping scraper...')
            self.scraper_thread.stop()
            self.stop_button.setEnabled(False)
    
    def update_progress(self, message, percent):
        self.log(message)
        self.progress_bar.setValue(percent)
    
    def scraping_finished(self, count):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if count >= 0:
            self.log('---')
            self.log(f'Scraping completed! Total files: {count}')
        self.scraper_thread = None
    
    def log(self, message):
        self.log_output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernScraperUI()
    window.show()
    sys.exit(app.exec())
