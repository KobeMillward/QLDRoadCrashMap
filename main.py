import sys
import folium
import pandas as pd
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, \
    QCheckBox, QScrollArea
from PyQt5 import QtWebEngineWidgets
from folium.plugins import FastMarkerCluster
from CollapsibleBox import CollapsableBox


class VisualisationWindow(QWidget):
    """
    Main window for the visualisation
    """
    def __init__(self):
        super().__init__()

        with open("crash_data.csv", "r") as csv_file:
            self.data = pd.read_csv("./crash_data.csv")
        # Clean data
        self.data.drop(self.data[self.data['Crash_Latitude'] == -0.0000095141966955].index, inplace=True)

        # Set up filters
        self.years = self.data['Crash_Year'].unique()
        self.selectedYears = self.years.tolist()
        self.months = self.data['Crash_Month'].unique()
        self.selectedMonths = self.months.tolist()
        self.severity = self.data['Crash_Severity'].unique()
        self.selectedSeverity = self.severity.tolist()
        self.roadConditions = self.data['Crash_Road_Surface_Condition'].unique()
        self.selectedRoadConditions = self.roadConditions.tolist()
        self.lightingConditions = self.data['Crash_Lighting_Condition'].unique()
        self.selectedLightingConditions = self.lightingConditions.tolist()

        # Set up layout
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.leftPanel = QWidget()
        self.leftPanelLayout = QVBoxLayout()
        self.leftPanel.setLayout(self.leftPanelLayout)

        # Filter menus
        self.createFilterMenu("Year", self.years, self.selectedYears)
        self.createFilterMenu("Month", self.months, self.selectedMonths)
        self.createFilterMenu("Severity", self.severity, self.selectedSeverity)
        self.createFilterMenu("Road Conditions", self.roadConditions, self.selectedRoadConditions)
        self.createFilterMenu("Lighting Conditions", self.lightingConditions, self.selectedLightingConditions)

        filterButton = QPushButton("Filter")
        filterButton.clicked.connect(self.updateMap)

        self.leftPanelLayout.addWidget(filterButton)

        self.map_panel = QtWebEngineWidgets.QWebEngineView()
        self.leftScroll = QScrollArea()
        self.leftScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.leftScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.leftScroll.setWidgetResizable(True)
        self.leftScroll.setWidget(self.leftPanel)
        self.main_layout.addWidget(self.leftScroll)
        self.main_layout.addWidget(self.map_panel)
        self.setWindowTitle("QLD Road Crash Map")
        self.updateMap()

    def createFilterMenu(self, name, filter_list, selected_list):
        filter_menu = CollapsableBox.CollapsibleBox(name)
        filter_menu_layout = QVBoxLayout()
        for item in filter_list:
            filter_checkbox = QCheckBox(str(item))
            filter_checkbox.toggle()
            filter_checkbox.stateChanged.connect(self.updateFilterFactoryFactory(item, selected_list))
            filter_menu_layout.addWidget(filter_checkbox)
        filter_menu.setContentLayout(filter_menu_layout)
        self.leftPanelLayout.addWidget(filter_menu)

    def updateFilterFactoryFactory(self, condition, filter):
        """
        Creates a filter factory function for each filter
        :param condition: Specific condition within filter set
        :param filter: Filter set
        :return: A filter factory function to create a filter menu
        """
        def updateFilterFactory(con, inFilter):
            def updateFilter():
                if con in inFilter:
                    inFilter.remove(con)
                else:
                    inFilter.append(con)
            return updateFilter
        return updateFilterFactory(condition, filter)

    def updateMap(self):
        """
        Function to update the map called on each filter update.
        :return: None
        """
        # Callback function to create popups and alter marker appearance.
        callback = ("function(row) {"
                    "   var markerSize = 3 + row[3]*3;"
                    "   var markerColour = '#00ff00';"
                    "   if (row[2] == 'Fatal') {"
                    "       markerColour = '#ff0000';"
                    "   } else if (row[2] == 'Hospitalisation' || row[2] == 'Medical treatment') {"
                    "       markerColour = '#ff8800';"
                    "   } else if (row[2] == 'Minor injury') {"
                    "       markerColour = '#ffea00';"
                    "   }"
                    "   var marker = L.circleMarker(new L.LatLng(row[0], row[1]), "
                    "{radius: markerSize, color: markerColour, fill: true, fillOpacity: 0.8});"
                    "   var popup = L.popup({maxWidth: '300'});"
                    "   var popup_text = $(`<div style='width: 100%; height:100%;'>Latitude: ${row[0]}<br/>"
                    "Longitude: ${row[1]}<br/>Severity: ${row[2]}<br/>Road Condition: ${row[4]}<br/>"
                    "Date: ${row[5]} ${row[6]} ${row[7]}<br/>Fatality: ${row[8]}<br/>Hospitalised: ${row[9]}<br/>"
                    "Medically Treated: ${row[10]}<br/>Minor Injury: ${row[11]}<br/>"
                    "Lighting Condition: ${row[12]}</div>`)[0];"
                    "   popup.setContent(popup_text);"
                    "   marker.bindPopup(popup);"
                    "   return marker;"
                    "}")

        # Filter data set on each filter
        filtered_data = self.data[self.data['Crash_Year'].isin(self.selectedYears)]
        filtered_data = filtered_data[filtered_data['Crash_Month'].isin(self.selectedMonths)]
        filtered_data = filtered_data[filtered_data['Crash_Severity'].isin(self.selectedSeverity)]
        filtered_data = filtered_data[filtered_data['Crash_Road_Surface_Condition'].isin(self.selectedRoadConditions)]

        # Update clustering size based on filtered data size
        clusteringZoomSize = 17
        if len(filtered_data.index) < 50000:
            clusteringZoomSize = 15
        if len(filtered_data.index) < 1000:
            clusteringZoomSize = 8

        # Create map and add markers
        m = folium.Map(location=[-27.470266, 153.025974], zoom_start=10)
        m.add_child(FastMarkerCluster(filtered_data[['Crash_Latitude', 'Crash_Longitude', 'Crash_Severity',
                                                     'Count_Casualty_Total', 'Crash_Road_Surface_Condition', 'Crash_Day_Of_Week',
                                                     'Crash_Month', 'Crash_Year', 'Count_Casualty_Fatality',
                                                     'Count_Casualty_Hospitalised', 'Count_Casualty_MedicallyTreated',
                                                     'Count_Casualty_MinorInjury', 'Crash_Lighting_Condition']].values.tolist(),
                                      callback=callback,
                                      options={
                                          'disableClusteringAtZoom': clusteringZoomSize,
                                          'spiderfyOnMaxZoom': 'disabled',
                                          'maxClusterRadius': 40
                                      })
                    )

        # Save and display map
        m.save("map.html")
        map_url = QUrl.fromLocalFile("/map.html")
        self.map_panel.load(map_url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VisualisationWindow()
    w.show()
    app.exec_()
