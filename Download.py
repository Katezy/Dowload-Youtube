import sys
import os
import webbrowser
import yt_dlp
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QRadioButton, QComboBox, QPushButton,
    QProgressBar, QListWidget, QFileDialog, QMenuBar, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer

class DownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Downloader")
        self.resize(600, 400)

        # Default Download Folder
        self.download_path = os.path.expanduser("~/Downloads")

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Menu Bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        add_multiple_action = QAction("Add Multiple URL", self)
        open_folder_action = QAction("Open Folder Program", self)
        open_folder_action.triggered.connect(self.open_program_folder)
        file_menu.addAction(add_multiple_action)
        file_menu.addAction(open_folder_action)

        # URL Input
        url_layout = QHBoxLayout()
        url_label = QLabel("Enter YouTube URL:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        # Video/Audio Options
        options_layout = QHBoxLayout()
        self.video_option = QRadioButton("Video")
        self.audio_option = QRadioButton("Audio")
        self.video_option.setChecked(True)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "4K"])
        fps_label = QLabel("FPS:")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["MP3", "WAV"])
        self.audio_format_combo.setEnabled(False)

        self.video_option.toggled.connect(
            lambda checked: self.toggle_audio_video(checked)
        )
        options_layout.addWidget(self.video_option)
        options_layout.addWidget(self.resolution_combo)
        options_layout.addWidget(fps_label)
        options_layout.addWidget(self.fps_combo)
        options_layout.addWidget(self.audio_option)
        options_layout.addWidget(self.audio_format_combo)
        main_layout.addLayout(options_layout)

        # Change Location
        location_layout = QHBoxLayout()
        location_label = QLabel("Change Location:")
        self.location_input = QLineEdit(self.download_path)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_folder)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(browse_button)
        main_layout.addLayout(location_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # History List
        history_layout = QVBoxLayout()
        history_label = QLabel("History List:")
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.open_file_path)
        clear_history_button = QPushButton("Clear History")
        clear_history_button.clicked.connect(self.history_list.clear)
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_list)
        history_layout.addWidget(clear_history_button)
        main_layout.addLayout(history_layout)

        # Download Button
        download_button = QPushButton("Download")
        download_button.clicked.connect(self.start_download)
        main_layout.addWidget(download_button)

        # Apply Custom Styles (CSS/QSS)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C2F3D;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QComboBox, QPushButton {
                background-color: #3E4A60;
                color: white;
                border: 1px solid #6D7885;
                padding: 5px;
                border-radius: 5px;
            }
            QRadioButton {
                color: white;
            }
            QPushButton {
                background-color: #8A64FF;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6A4BE6;
            }
            QProgressBar {
                background-color: #3E4A60;
                border-radius: 5px;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #8A64FF;
                border-radius: 5px;
            }
            QListWidget {
                background-color: #3E4A60;
                color: white;
                border: 1px solid #6D7885;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #8A64FF;
            }
        """)

    def toggle_audio_video(self, checked):
        self.resolution_combo.setEnabled(checked)
        self.fps_combo.setEnabled(checked)
        self.audio_format_combo.setEnabled(not checked)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.location_input.setText(folder)
            self.download_path = folder

    def start_download(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL!")
            return

        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Downloading... 0%")
        QTimer.singleShot(500, lambda: self.update_progress(30, "Downloading... 30%"))
        QTimer.singleShot(1000, lambda: self.update_progress(70, "Downloading... 70%"))
        QTimer.singleShot(1500, lambda: self.update_progress(100, "Download complete!"))
        QTimer.singleShot(2000, lambda: self.finish_download(url))

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)

    def finish_download(self, url):
        filename = self.get_filename_from_url(url)
        file_path = os.path.join(self.download_path, filename)

        # Simulate File Creation (using yt-dlp to download real file)
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': file_path,  # Use the dynamic file name
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.history_list.addItem(file_path)
            QMessageBox.information(self, "Download Complete", f"File saved to: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Download Failed", f"Error: {e}")

        self.progress_bar.setValue(0)

    def get_filename_from_url(self, url):
        # This function gets the title of the video from YouTube URL and formats it as a filename
        ydl_opts = {'quiet': True, 'force_generic_extractor': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get("title", "Downloaded_File")
            return f"{title}.mp4" if self.video_option.isChecked() else f"{title}.mp3"

    def open_file_path(self, item):
        path = item.text()
        if os.path.exists(path):
            webbrowser.open(path)
        else:
            QMessageBox.warning(self, "Error", "File not found!")

    def open_program_folder(self):
        webbrowser.open(self.download_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderWindow()
    window.show()
    sys.exit(app.exec_())
