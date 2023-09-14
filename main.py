import urllib.request

import folium
import io
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt5 import QtWebEngineWidgets
import os
from math import floor

class DataRequestWindow(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Data must be downloaded (~179 MB)"))
        buttonOptionsFrame = QWidget()
        buttonOptionsFrame.setLayout(QHBoxLayout())
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel)
        download_button = QPushButton("Download")
        download_button.clicked.connect(self.download)
        buttonOptionsFrame.layout().addWidget(cancel_button)
        buttonOptionsFrame.layout().addWidget(download_button)
        layout.addWidget(buttonOptionsFrame)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

    def cancel(self):
        exit(0)

    def handleProgress(self, blocknum, blocksize, totalsize):
        read_data = blocknum * blocksize

        if totalsize > 0:
            download_percentage = floor(read_data * 100 / totalsize)
            self.progress_bar.setValue(download_percentage)
            QApplication.processEvents()

    def download(self):
        URL = "https://www.data.qld.gov.au/dataset/f3e0ca94-2d7b-44ee-abef-d6b06e9b0729/resource/e88943c0-5968-4972-a" \
              "15f-38e120d72ec0/download/crash_data_queensland_1_crash_locations.csv"
        filename = "./crash_data.csv"
        try:
            urllib.request.urlretrieve(URL, filename, self.handleProgress)
        except:
            # Delete file safely
            if os.path.isfile("./crash_data.csv"):
                os.remove("./crash_data.csv")
            exit(-1)

def create_gui():
    m = folium.Map(location=[-27.470457, 153.025974])

    data_b = io.BytesIO()
    m.save(data_b, close_file=False)

    # Create GUI
    app = QApplication([])
    window = QWidget()
    # Right Frame (Map)
    right_frame = QWidget()
    right_frame_layout = QVBoxLayout()
    map_view = QtWebEngineWidgets.QWebEngineView()
    map_view.setHtml(data_b.getvalue().decode())
    right_frame_layout.addWidget(map_view)
    right_frame.setLayout(right_frame_layout)

    # Left Frame (Options)
    left_frame = QWidget()
    left_frame_layout = QVBoxLayout()
    left_frame_layout.addWidget(QPushButton("Left 1"))
    update_button = QPushButton("Update")

    def update_map():
        data_bytes = io.BytesIO()
        new_map = folium.Map(location=[-25.290053, 152.864781])
        new_map.save(data_bytes, close_file=False)
        map_view.setHtml(data_bytes.getvalue().decode())

    update_button.clicked.connect(update_map)
    left_frame_layout.addWidget(update_button)
    left_frame.setLayout(left_frame_layout)

    # Window Layout
    window_layout = QHBoxLayout()
    window_layout.addWidget(left_frame)
    window_layout.addWidget(right_frame)
    window.setLayout(window_layout)

    # Run App
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not os.path.isfile("./crash_data.csv"):
        # Create data download request gui
        w = DataRequestWindow()
        w.show()
        app.exec_()

    #create_gui()

