import folium
import io
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5 import QtWebEngineWidgets
from urllib.request import urlopen
from os.path import isfile

def get_data():
    LIMIT = 30000 # API has a 32000 request size limit
    URL = "https://www.data.qld.gov.au/api/3/action/datastore_search?resource_id=e88943c0-5968-4972-a15f-38e120d72ec0&limit="+str(LIMIT)
    try:
        data = []
        for req_i in range(0, 13):
            fileobj = urlopen(URL + "&offset=" + str(req_i*LIMIT))
            res_json = json.loads(fileobj.read())
            res_result = res_json["result"]
            data = data + res_result["records"]
            print("Request: " + str(req_i+1) + "/13")
        with open("crash_data.json", "w") as datafile:
            json.dump(data, datafile, indent=2)
    except:
        exit(-1)


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
    if not isfile("./crash_data.json"):
        get_data()

    #create_gui()

