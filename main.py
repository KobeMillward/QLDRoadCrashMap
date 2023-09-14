import csv
import folium
import io
import sys
from PyQt5 import QtWidgets, QtWebEngineWidgets

def update_map(web):
    data_bytes = io.BytesIO()
    new_map = folium.Map(location=[-25.290053, 152.864781])
    new_map.save(data_bytes, close_file=False)
    w.setHtml(data_bytes.getvalue().decode())
    return data_bytes

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    m = folium.Map(location=[-27.470457, 153.025974])

    data_b = io.BytesIO()
    m.save(data_b, close_file=False)

    w = QtWebEngineWidgets.QWebEngineView()
    w.setHtml(data_b.getvalue().decode())
    w.resize(640, 480)
    w.show()

    update_map(w)

    sys.exit(app.exec_())

