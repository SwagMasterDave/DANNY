from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QStackedWidget, QApplication, QProgressBar, QTableWidgetItem, QTableWidget, QGraphicsRectItem, QGraphicsView, QInputDialog, QDialog, QDialogButtonBox, QMenu, QGraphicsScene, QMessageBox, QListWidgetItem, QMainWindow, QListView, QVBoxLayout, QLCDNumber, QLineEdit, QGridLayout, QWidget, QAbstractButton, QPushButton, QLabel, QListWidget,QHBoxLayout, QComboBox, QTextEdit, QSlider , QGroupBox
from PyQt5.QtGui import QPainter, QColor, QPalette, QPen, QPainterPath, QImage, QPixmap, QIcon, QFont
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QPoint, QRectF, QRect, QAbstractListModel, QModelIndex, QUrl, QByteArray, QDateTime
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import sys
import requests
import json
from PIL import Image
from io import BytesIO
import os, io
import replicate
import shutil
import csv
import random
import cv2
import numpy as np
from shapely.geometry import Polygon

class SlidersGroupBox(QGroupBox):
        
    slider_value_changed_signal = pyqtSignal(int, int)  # Signal for slider value changes (slider index, new value)
    combo_value_changed_signal = pyqtSignal(int, str)    # Signal for combo box value changes (combo index, new value)
    button_clicked_signal = pyqtSignal(int)             # Signal for button clicks (button index)

    def __init__(self):
        super().__init__("Legend")
        super().setStyleSheet(f"font-size: 20px; font-weight: bold;")
        self.sliders = []
        self.buttons = []
        self.combos = []  # Add a list to store the QComboBox instances
        self.selected_button = None  # Keep track of the selected button

        for i in range(1, 5):
            #slider = QSlider(Qt.Horizontal)
            #slider.setRange(1, 7)
            #slider.setTickInterval(1)
            #slider.setTickPosition(QSlider.TicksBelow | QSlider.TicksAbove)
            #slider.setMaximumWidth(400)
            #slider.valueChanged.connect(self.slider_value_changed)

            combo = QComboBox()
            combo.addItems(["Present", "Not Present", "Ambiguous"])  # Add your desired items
            combo.setCurrentIndex(-1)  # Set the default index
            combo.currentIndexChanged.connect(self.combo_value_changed)
            # Set the fixed width for the combo box
            combo.setFixedWidth(150)  # Adjust the width as needed


            button = QPushButton(self.get_button_color_name(i))
            button.setStyleSheet(f"color: {'rgb' + str(self.get_button_color(i))};")
            button.clicked.connect(self.button_clicked)
            button.setFixedWidth(250)

            button_font = QFont()
            button_font.setPointSizeF(16)
            button.setFont(button_font)

            #self.sliders.append(slider)
            self.combos.append(combo)  # Append the QComboBox instance to the list
            self.buttons.append(button)

        layout_overall = QGridLayout()
        #confidenceLevel = QLabel("Confidence Level")
        #label = QLabel("1         2         3         4         5         6         7")
        #text_font = QFont()
        #text_font.setPointSize(12)
        #label.setFont(text_font)
        #label.setAlignment(Qt.AlignCenter)
        #confidenceLevel.setFont(text_font)
        #confidenceLevel.setAlignment(Qt.AlignCenter)
        #label.setMaximumHeight(40)
        #layout_overall.addWidget(confidenceLevel, 0, 2)
        #layout_overall.addWidget(label, 1, 2)

        for i in range(4):
            layout_overall.addWidget(self.buttons[i], i + 2, 1)
            layout_overall.addWidget(self.combos[i], i + 2, 0)
            #self.sliders[i].setValue(4)
            #layout_overall.addWidget(self.sliders[i], i + 2, 2)  # Add the QComboBox next to the slider
        
        layout_overall.setColumnStretch(1, 2)
        self.setLayout(layout_overall)
        self.setFixedWidth(500)  # Adjust the width to accommodate the new QComboBox

    def get_button_color(self, index):
        colors = [
            (255, 165, 0),
            (0, 100, 0),
            (0, 0, 255),
            (128, 0, 128)
        ]
        return colors[index - 1]
    def get_button_color_name(self, index):
        colors = [
            ("Narrow Joint Space"),
            ("Osteophytes"),
            ("Irregularity"),
            ("Tibial Spiking")
        ]
        return colors[index - 1]
    def combo_value_changed(self):
        sender_combo = self.sender()
        if sender_combo:
            index = self.combos.index(sender_combo)
            selected_value = sender_combo.currentText()
            self.combo_value_changed_signal.emit(index, selected_value)

    def slider_value_changed(self):
        sender_slider = self.sender()
        if sender_slider:
            index = self.sliders.index(sender_slider)
            selected_value = sender_slider.value()
            self.slider_value_changed_signal.emit(index, selected_value)

    def button_clicked(self):
        sender_button = self.sender()
        if sender_button:
            index = self.buttons.index(sender_button)

            if self.selected_button:
                # Reset the style of the previously selected button
                self.selected_button.setStyleSheet(f"color: {'rgb' + str(self.get_button_color(self.buttons.index(self.selected_button) + 1))};")

            # Toggle the style sheet of the clicked button
            if sender_button == self.selected_button:
                self.selected_button = None  # If the same button is clicked again, remove the selection
                
                # Emit the button_clicked_signal with the index
                self.button_clicked_signal.emit(-1)
            else:
                sender_button.setStyleSheet(f"color: {'rgb' + str(self.get_button_color(index + 1))}; background-color: yellow;")
                self.selected_button = sender_button

                # Emit the button_clicked_signal with the index
                self.button_clicked_signal.emit(index)
    def reset_sliders_group_box(self):
        # Reset sliders, combos, and selected button
        for i in range(4):
            #self.sliders[i].setValue(4)
            self.combos[i].setCurrentIndex(-1)
            self.buttons[i].setStyleSheet(f"color: {'rgb' + str(self.get_button_color(i + 1))};")
        
        # Reset the selected button
        if self.selected_button:
            self.selected_button.setStyleSheet(f"color: {'rgb' + str(self.get_button_color(self.buttons.index(self.selected_button) + 1))};")
            self.selected_button = None