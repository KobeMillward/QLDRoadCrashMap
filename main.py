import urllib.request
import folium
import io
import sys
import os
import pandas as pd
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QProgressBar, QCheckBox
from PyQt5 import QtWebEngineWidgets
from math import floor
from folium.plugins import FastMarkerCluster
from CollapsibleBox import CollapsableBox


class VisualisationWindow(QWidget):

    def __init__(self):
        super().__init__()

        with open("crash_data.csv", "r") as csv_file:
            self.data = pd.read_csv("./crash_data.csv")

        self.years = self.data['Crash_Year'].unique()
        self.selectedYears = self.years.tolist()
        self.months = self.data['Crash_Month'].unique()
        self.selectedMonths = self.months.tolist()
        self.severity = self.data['Crash_Severity'].unique()
        self.selectedSeverity = self.severity.tolist()
        self.roadConditions = self.data['Crash_Road_Surface_Condition'].unique()
        self.selectedRoadConditions = self.roadConditions.tolist()

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.leftPanel = QWidget()
        self.leftPanelLayout = QVBoxLayout()
        self.leftPanel.setLayout(self.leftPanelLayout)
        self.main_layout.addWidget(self.leftPanel)

        # Year Filter Menu
        year_filter_menu = CollapsableBox.CollapsibleBox("Year")
        year_filter_menu_layout = QVBoxLayout()
        for year in self.years:
            year_filter_checkbox = QCheckBox(str(year))
            year_filter_checkbox.toggle()
            year_filter_checkbox.stateChanged.connect(self.updateYearFilterFactory(year))
            year_filter_menu_layout.addWidget(year_filter_checkbox)
        year_filter_menu.setContentLayout(year_filter_menu_layout)
        self.leftPanelLayout.addWidget(year_filter_menu)

        # Month Filter Menu
        month_filter_menu = CollapsableBox.CollapsibleBox("Month")
        month_filter_menu_layout = QVBoxLayout()
        for month in self.months:
            month_filter_checkbox = QCheckBox(month)
            month_filter_checkbox.toggle()
            month_filter_checkbox.stateChanged.connect(self.updateMonthFilterFactory(month))
            month_filter_menu_layout.addWidget(month_filter_checkbox)
        month_filter_menu.setContentLayout(month_filter_menu_layout)
        self.leftPanelLayout.addWidget(month_filter_menu)

        # Severity Filter Menu
        severity_filter_menu = CollapsableBox.CollapsibleBox("Severity")
        severity_filter_menu_layout = QVBoxLayout()
        for severity in self.severity:
            severity_filter_checkbox = QCheckBox(severity)
            severity_filter_checkbox.toggle()
            severity_filter_checkbox.stateChanged.connect(self.updateSeverityFilterFactory(severity))
            severity_filter_menu_layout.addWidget(severity_filter_checkbox)
        severity_filter_menu.setContentLayout(severity_filter_menu_layout)
        self.leftPanelLayout.addWidget(severity_filter_menu)

        # Road Conditions Menu
        road_conditions_menu = CollapsableBox.CollapsibleBox("Road Conditions")
        road_conditions_menu_layout = QVBoxLayout()
        for condition in self.roadConditions:
            condition_filter_checkbox = QCheckBox(condition)
            condition_filter_checkbox.toggle()
            condition_filter_checkbox.stateChanged.connect(self.updateRoadConditionFilterFactory(condition))
            road_conditions_menu_layout.addWidget(condition_filter_checkbox)
        road_conditions_menu.setContentLayout(road_conditions_menu_layout)
        self.leftPanelLayout.addWidget(road_conditions_menu)

        filterButton = QPushButton("Filter")
        filterButton.clicked.connect(self.updateMap)

        self.leftPanelLayout.addWidget(filterButton)

        self.map_panel = QtWebEngineWidgets.QWebEngineView()
        self.main_layout.addWidget(self.map_panel)
        self.updateMap()

    def updateYearFilterFactory(self, year):
        def updateYearFilter():
            if year in self.selectedYears:
                self.selectedYears.remove(year)
            else:
                self.selectedYears.append(year)
        return updateYearFilter

    def updateMonthFilterFactory(self, month):
        def updateMonthFilter():
            if month in self.selectedMonths:
                self.selectedMonths.remove(month)
            else:
                self.selectedMonths.append(month)
        return updateMonthFilter

    def updateSeverityFilterFactory(self, severity):
        def updateSeverityFilter():
            if severity in self.selectedSeverity:
                self.selectedSeverity.remove(severity)
            else:
                self.selectedSeverity.append(severity)
        return updateSeverityFilter

    def updateRoadConditionFilterFactory(self, condition):
        def updateRoadConditionFilter():
            if condition in self.selectedRoadConditions:
                self.selectedRoadConditions.remove(condition)
            else:
                self.selectedRoadConditions.append(condition)
        return updateRoadConditionFilter

    def updateMap(self):

        callback = ("function(row) {"
                    "   var markerSize = 3 + row[3]*3;"
                    "   var markerColour = '#99ff00';"
                    "   if (row[2] == 'Fatal') {"
                    "       markerColour = '#ff0000';"
                    "   } else if (row[2] == 'Hospitalisation') {"
                    "       markerColour = '#ffe600';"
                    "   }"
                    "   var marker = L.circleMarker(new L.LatLng(row[0], row[1]), "
                    "{radius: markerSize, color: markerColour, fill: true, fillOpacity: 0.8});"
                    "   var popup = L.popup({maxWidth: '300'});"
                    "   var popup_text = $(`<div style='width: 100%; height:100%;'>Latitude: ${row[0]}<br/>"
                    "Longitude: ${row[1]}<br/>Severity: ${row[2]}</div>`)[0];"
                    "   popup.setContent(popup_text);"
                    "   marker.bindPopup(popup);"
                    "   return marker;"
                    "}")

        popups = ["Longitude: {}<br>".format(self.data['Crash_Longitude'])]

        filtered_data = self.data[self.data['Crash_Year'].isin(self.selectedYears)]
        filtered_data = filtered_data[filtered_data['Crash_Month'].isin(self.selectedMonths)]
        filtered_data = filtered_data[filtered_data['Crash_Severity'].isin(self.selectedSeverity)]
        filtered_data = filtered_data[filtered_data['Crash_Road_Surface_Condition'].isin(self.selectedRoadConditions)]

        m = folium.Map(location=[-27.470266, 153.025974], zoom_start=10)
        m.add_child(FastMarkerCluster(filtered_data[['Crash_Latitude', 'Crash_Longitude', 'Crash_Severity',
                                                     'Count_Casualty_Total']].values.tolist(),
                                      #popups=popups,
                                      callback=callback,
                                      options={
                                          'disableClusteringAtZoom': 17,
                                          'maxClusterRadius': 40
                                      })
                    )
        m.save("map.html")
        map_url = QUrl.fromLocalFile("/map.html")
        self.map_panel.load(map_url)

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
    else:
        w = VisualisationWindow()
        w.show()
        app.exec_()
