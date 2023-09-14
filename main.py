import csv
import folium
import io
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5 import QtWebEngineWidgets


def get_data():
    pass


def create_gui():
    m = folium.Map(location=[-27.470457, 153.025974])

    data_b = io.BytesIO()
    m.save(data_b, close_file=False)

    # Create GUI
    app = QApplication(sys.argv)
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

    get_data()
    create_gui()

