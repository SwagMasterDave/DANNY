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
from SlidersGroupBox import SlidersGroupBox
from collections import defaultdict

class Reason_Box(QGroupBox):
    def __init__(self):
        super().__init__("Allabeler Second Session")
        self.last_mouse_pos = None
        self.last_press_time = None
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 40, 200, 25)  # Adjust the geometry as needed
        self.progress_bar.setValue(0)
        
        self.drawing_enabled = False  # Add this attribute
        
        self.selected_button = None
        
        self.confidenceList = [[0,4,""],[1,4,""],[2,4,""],[3,4,""]]
        
        self.comboIndex = 0
        
        self.current_row = 1
        self.csv_data = None
        self.selected_column = 4  # Change this to select a different column
        
        # Specify the file path to your CSV file
        self.csv_file_path = "new_images_re_1121.csv"
        
        self.load_csv_data("second")
        
        self.current_index = 0
        
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter ID Here...")
        self.text_input.setMaximumWidth(800)
        self.text_input.setMinimumHeight(100)
        
        font = self.text_input.font()  # Get the current font
        font.setPointSize(20)  # Set the font size 
        self.text_input.setFont(font)
        
        self.text = ""
        
        saveID = QPushButton("Save ID", self)
        saveID.clicked.connect(self.on_submit)
        saveID.setMaximumWidth(200)
        saveID.setMinimumHeight(100)
        
        font = saveID.font()  # Get the current font
        font.setPointSize(20)  # Set the font size 
        saveID.setFont(font)
        
        self.nextImage = QPushButton("Next Step", self)
        self.nextImage.clicked.connect(self.namePlease)
        self.nextImage.setMinimumWidth(200)
        self.nextImage.setFixedHeight(100)
        
        font = self.nextImage.font()  # Get the current font
        font.setPointSize(20)  # Set the font size 
        self.nextImage.setFont(font)
        
        self.imageList = []
        for index, images in enumerate(self.csv_data):
            self.imageList.append(["ID",self.csv_data[index][0],self.csv_data[index][1],"your Label","your Label2",self.csv_data[index][2],0,"Y/N",1,"Y/N",1,"Y/N",1,"Y/N",1,self.csv_data[index][3],"Second","total percentage","confidence level"])
        random.shuffle(self.imageList)
        for index, img in enumerate(self.imageList):
            print(img[1])
        # Create a QGroupBox to encapsulate imageGroupBox and sliders_group_box
        self.mainGroupBox = QGroupBox("")
        self.mainGroupBox.setMinimumWidth(850)

        # Create SlidersGroupBox
        self.slidersGroupBox = SlidersGroupBox()
        
        self.slidersGroupBox.slider_value_changed_signal.connect(self.handle_slider_value_changed)
        self.slidersGroupBox.combo_value_changed_signal.connect(self.handle_combo_value_changed)
        self.slidersGroupBox.button_clicked_signal.connect(self.handle_button_clicked)

        # Create a QGroupBox for image display
        imageGroupBox = QGroupBox("X-Ray Image")
        imageGroupBox.setMinimumWidth(305)
        imageGroupBox.setStyleSheet(f"font-size: 20px; font-weight: bold;")
        
        # Create a QLabel for displaying an image
        label = QLabel()

        # Load an image using QPixmap
        pixmap = QPixmap("Example.png")  # Replace with the actual path to your image
        pixmap = pixmap.scaled(QSize(300, 300), Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)  # Align the image to the center

        
        # Create a QGraphicsView widget to display the image
        self.image_view = QGraphicsView()
        self.image_view.setFixedSize(300, 300)

        # Create a QGraphicsScene to hold the image
        self.image_scene = QGraphicsScene()
        self.image_view.setScene(self.image_scene)

        # Add an image to the scene
        image_path = "./original/" + self.imageList[self.current_index][2]
        image = QPixmap(image_path)
        image = image.scaled(QSize(300, 300), Qt.AspectRatioMode.KeepAspectRatio)
        self.image_item = self.image_scene.addPixmap(image)

        # ... (other image display setup code)

        # Add the QGraphicsView to the imageGroupBox
        imageLayout = QVBoxLayout()
        imageLayout.addWidget(self.image_view, alignment=Qt.AlignCenter)
        imageGroupBox.setLayout(imageLayout)
        
        self.image_view.setRenderHint(QPainter.Antialiasing)
        self.image_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.image_view.setRenderHint(QPainter.HighQualityAntialiasing)
        self.image_view.setRenderHint(QPainter.NonCosmeticDefaultPen)
        self.image_view.setRenderHint(QPainter.TextAntialiasing)
        self.image_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.image_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.image_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.image_view.mousePressEvent = self.mousePressEvent
        self.image_view.mouseMoveEvent = self.mouseMoveEvent
        self.image_view.mouseReleaseEvent = self.mouseReleaseEvent

        # Create a variable to keep track of drawing red rectangles
        self.drawing_rect = False

        # Create a list to store the drawn rectangles
        self.rectangles = []

        # Create a pen for drawing
        self.pen = QPen()
        self.pen.setColor(QColor(255, 165, 0))  # Set the pen color (red)
        self.pen.setWidth(4)  # Set the pen width
        
        # Create and add a QGroupBox
        self.Labelbox = QGroupBox("First Label")
        #Labelbox.setMaximumHeight(200)
        self.Labelbox.setFixedHeight(100)
        self.Labelbox.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        Labelbox_layout = QHBoxLayout()
        
        # Add buttons to group_box2_layout
        self.button1 = QPushButton("Arthritis")
        self.button2 = QPushButton("Non-Arthritis")
        self.button1.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        self.button2.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        # Connect button click signals to custom methods
        self.button1.clicked.connect(lambda: self.on_button_pressed(self.button1, self.button2))
        self.button2.clicked.connect(lambda: self.on_button_pressed(self.button2, self.button1))
        Labelbox_layout.addWidget(self.button1)
        Labelbox_layout.addWidget(self.button2)
        
        # Set the layout for the group box
        self.Labelbox.setLayout(Labelbox_layout)
        
        # Set up the layout for the combined group
        mainLayout = QGridLayout()
        mainLayout.addWidget(imageGroupBox, 0, 0, 2, 2)
        mainLayout.addWidget(self.slidersGroupBox, 0, 2, 2, 1)
        mainLayout.addWidget(self.nextImage, 4, 0, 1, 3)
        mainLayout.addWidget(self.Labelbox, 3, 0, 1, 3)
        self.mainGroupBox.setLayout(mainLayout)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.text_input, 0, 0, 1, 1)
        self.layout.addWidget(saveID, 0, 1, 1, 1)
        self.layout.addWidget(self.mainGroupBox, 1, 0, 3, 3)
        self.layout.addWidget(self.progress_bar, 4, 0, 1, 6)
        self.setLayout(self.layout)
    def setupSubGroupBox(self):
        if self.current_index == 0:
            pass
        else:
            self.layout.removeWidget(self.subGroupBox)
        self.subGroupBox = QGroupBox("")
        self.subGroupBox.setMinimumWidth(850)
        
        self.feedback_messages = []

        # Load the XAI image (replace with your actual XAI image path)
        xai_image_path = "./xai/" + self.imageList[self.current_index][2]
        xai_image = QPixmap(xai_image_path)
        xai_image = xai_image.scaled(QSize(300, 300), Qt.AspectRatioMode.KeepAspectRatio)
        
        image = cv2.imread(xai_image_path)
        resized_image = cv2.resize(image, (300,300))

        hsv = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)
        lower_cyan = np.array([0, 100, 100])
        upper_cyan = np.array([20, 255, 255])
        mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a QLabel for displaying the duplicated image
        duplicated_label = QLabel()
        duplicated_label.setAlignment(Qt.AlignCenter)
        
        # Load the original image
        original_image_path = "./original/" + self.imageList[self.current_index][2]
        original_image = cv2.imread(original_image_path)
        resized_original_image = cv2.resize(original_image, (300,300))

        result_image = np.copy(resized_original_image)
        #tint_color = (0, 0, 255, 0.25)

        # Iterate through contours and draw filled bounding boxes on the resized original image
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            #overlay = resized_original_image.copy()
            #cv2.rectangle(overlay, (x, y), (x + w, y + h), tint_color[:3], -1)
            #resized_original_image = cv2.addWeighted(resized_original_image, 1 - tint_color[3], overlay, tint_color[3], 0)

            # Create a QGraphicsRectItem for the drawn rectangle
            rect_item = QGraphicsRectItem(x, y, w, h)
            rect_item.setPen(QPen(Qt.red,4))  # Set the pen color to red
            self.rectangles.append(rect_item)  # Add the rectangle to the list of rectangles

        # Convert OpenCV image to QImage
        height, width, channel = resized_original_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(resized_original_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(q_image)

        # Scale the QPixmap to make it bigger
        scaled_pixmap = pixmap.scaledToWidth(300)  # Adjust the width as needed

        # Create a new QGraphicsScene to hold the duplicated image
        duplicated_scene = QGraphicsScene()

        # Add the original image to the duplicated scene
        duplicated_scene.addPixmap(pixmap)

        # Add the drawn rectangles to the duplicated scene
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen = rect_item.pen()
            rect_item_copy = QGraphicsRectItem(rect)
            rect_item_copy.setPen(pen)
            duplicated_scene.addItem(rect_item_copy)

        # Create a QGraphicsView widget to display the duplicated image
        duplicated_view = QGraphicsView()
        duplicated_view.setFixedSize(305, 305)
        duplicated_view.setScene(duplicated_scene)
        
        self.total_percentage = self.save_scanning_percentage_image(duplicated_view, "./scanning_percentage_image.png")
        
        #Total_feedback_text = f"Total percent of overlaped area of AI focus Area: " + f"{self.total_percentage:.2f}% overlap"
        
        for button_number in range(1, 5):
            percentage_overlap = self.save_scanning_percentage_image_in_image(duplicated_view, "./scanning_percentage_image2.png", self.get_button_color(button_number))
            color = self.get_button_color_name(button_number)
            buttonColor = self.rgb_to_hex(self.get_button_color(button_number))
            feedback_text = f"<font color='{buttonColor}'> {color}" + f": {percentage_overlap:.2f}% overlap<font>"
            self.feedback_messages.append(feedback_text)
        
        # Create and add a QGroupBox
        group_box = QGroupBox("Overlap Percentage")
        group_box.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        group_box_layout = QVBoxLayout()
        
        # Create a local QLabel for feedback messages
        feedback_label = QLabel(self.feedback_messages[0])
        feedback_label.setAlignment(Qt.AlignLeft)
        feedback_label.setStyleSheet(f"font-size: 16px;font-weight: normal;")
        group_box_layout.addWidget(feedback_label)

        # Create a local QLabel for feedback messages
        feedback_label2 = QLabel(self.feedback_messages[1])
        feedback_label2.setAlignment(Qt.AlignLeft)
        feedback_label2.setStyleSheet(f"font-size: 16px;font-weight: normal;")
        group_box_layout.addWidget(feedback_label2)

        # Create a local QLabel for feedback messages
        feedback_label3 = QLabel(self.feedback_messages[2])
        feedback_label3.setAlignment(Qt.AlignLeft)
        feedback_label3.setStyleSheet(f"font-size: 16px;font-weight: normal;")
        group_box_layout.addWidget(feedback_label3)

        # Create a local QLabel for feedback messages
        feedback_label4 = QLabel(self.feedback_messages[3])
        feedback_label4.setAlignment(Qt.AlignLeft)
        feedback_label4.setStyleSheet(f"font-size: 16px;font-weight: normal;")
        group_box_layout.addWidget(feedback_label4)
        
        feedback_labelT = QLabel()
        feedback_labelT.setAlignment(Qt.AlignLeft)
        #feedback_labelT.setText(Total_feedback_text)
        feedback_labelT.setStyleSheet(f"font-size: 16px;font-weight: bold;")
        group_box_layout.addWidget(feedback_labelT)
        
        # Set the layout for the group box
        group_box.setLayout(group_box_layout)
        
        # Create and add a QGroupBox
        group_box2 = QGroupBox("Final Label")
        group_box2.setFixedHeight(100)
        #group_box2.setMaximumHeight(200)
        group_box2.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        group_box2_layout = QHBoxLayout()

        # Add widgets to the group box layout (e.g., QLabel, QSpinBox, etc.)
        # Example: group_box_layout.addWidget(QLabel("Your Additional Information"))
        
        # Add buttons to group_box2_layout
        self.button11 = QPushButton("Arthritis")
        self.button21 = QPushButton("Non-Arthritis")
        button3 = QPushButton("Next Image")  # New button for Next Image
        self.button11.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        self.button21.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        button3.setStyleSheet(f"font-size: 30px;font-weight: normal;")
        self.button11.clicked.connect(lambda: self.on_button_pressed2(self.button11,self.button21))
        self.button21.clicked.connect(lambda: self.on_button_pressed2(self.button21,self.button11))
        self.button11.clicked.connect(lambda: self.on_button_clicked(duplicated_view, "Arthritis"))
        self.button21.clicked.connect(lambda: self.on_button_clicked(duplicated_view, "Non-Arthritis"))
        button3.clicked.connect(self.warnSelf)
        button3.setFixedHeight(100)
        group_box2_layout.addWidget(self.button11)
        group_box2_layout.addWidget(self.button21)

        
        AI_label = QLabel(f"<font color='red'>AI Suggestion:</font> {self.imageList[self.current_index][15]}")
        AI_label.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        AI_label.setAlignment(Qt.AlignLeft)
        
        # Set the layout for the group box
        group_box2.setLayout(group_box2_layout)
        
        # Create a QGroupBox for colored labels
        color_group_box = QGroupBox("Legend")
        color_group_box.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        color_group_box_layout = QVBoxLayout()
        
        # Define colors and corresponding labels
        color_labels = [(0, f"Narrow Joint Space: {self.confidenceList[0][2]}"), (1, f"Osteophytes: {self.confidenceList[1][2]}"), (2, f"Irregularity: {self.confidenceList[2][2]}"), (3, f"Tibial Spiking: {self.confidenceList[3][2]}")]

        for color, label_text in color_labels:
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {'rgb' + str(self.get_button_color(color+1))}; font-weight: bold; font-size: 14px;")
            label.setAlignment(Qt.AlignLeft)
            color_group_box_layout.addWidget(label)

        # Set the layout for the color group box
        color_group_box.setLayout(color_group_box_layout)
        
        The_label = QLabel("")
        if self.total_percentage > 50.0:
            The_label.setText("The AI seems to consider the parts \nyou think are important as important.")
        else:
            The_label.setText("The AI seems to consider different \nparts as important.")
        The_label.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        The_label.setAlignment(Qt.AlignLeft)

        subsubFeedBack =  QGroupBox("")
        subsubFeedBack.setFlat(True)
        subsubFBLayout = QGridLayout()
        subsubFBLayout.addWidget(AI_label, 0, 0, 1, 1)
        subsubFBLayout.addWidget(The_label, 1, 0, 1, 1)   
        subsubFeedBack.setLayout(subsubFBLayout)

        subFeedBack =  QGroupBox("FeedBack")
        subFeedBack.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        subFBLayout = QGridLayout()
        subFBLayout.addWidget(subsubFeedBack, 0, 0, 1, 1)
        #subFBLayout.addWidget(color_group_box, 2, 0, 1, 1)
        subFBLayout.addWidget(group_box, 2, 0, 1, 1)
        subFeedBack.setLayout(subFBLayout)

        imageDisplay = QGroupBox("AI focus spot")
        imageDisplay.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        imageDisplayLayout = QGridLayout()
        imageDisplayLayout.addWidget(duplicated_view, 0, 0, 1, 1)
        imageDisplay.setLayout(imageDisplayLayout)

        # Create a layout to arrange the views side by side
        subLayout = QGridLayout()
        subLayout.addWidget(imageDisplay, 0, 0, 1, 1)
        subLayout.addWidget(subFeedBack, 0, 1, 1, 1)
        subLayout.addWidget(group_box2, 1, 0, 1, 2)
        subLayout.addWidget(button3, 2, 0, 1, 2)  # Add the new button to the layout

        # Set the layout for the pop-up
        self.subGroupBox = QGroupBox("")
        self.subGroupBox.setLayout(subLayout)
        self.layout.addWidget(self.subGroupBox, 1, 3, 3, 3)
        if self.rectangles:
            last_rect_item = self.rectangles.pop(-1)
    def rgb_to_hex(self, rgb):
        """Converts an RGB tuple to hexadecimal color representation."""
        return "#{:02x}{:02x}{:02x}".format(*rgb)    
    def warnSelf(self):
        if self.imageList[self.current_index][4] == "your Label2":
            incomplete_message = QMessageBox()
            incomplete_message.setIcon(QMessageBox.Warning)
            incomplete_message.setFixedSize(800, 200) 
            incomplete_message.setWindowTitle("Select the choice")
            incomplete_message.setText("Please make your label before going to the next image")
            incomplete_message.exec_()
        else:
            state = self.show_confidence_dialog()
            if state == True:
                self.next_image()
                self.mainGroupBox.setEnabled(True)
                if self.current_index > len(self.imageList) - 1:
                    self.slidersGroupBox.setEnabled(False)
                    self.Labelbox.setEnabled(False)
                    self.nextImage.setText("Done")
                    red_color = QColor(255, 0, 0)
                    self.nextImage.setStyleSheet(f"color: {red_color.name()};font-size: 30px; font-weight: bold;")
    def on_button_pressed(self, clicked_button, other_button):
        # Highlight the pressed button
        clicked_button.setStyleSheet("background-color: yellow; font-size: 20px; font-weight: bold;")
        self.imageList[self.current_index][3] = clicked_button.text()
        # Remove the highlight from the other button
        other_button.setStyleSheet("font-size: 20px; font-weight: bold;")
        # Perform other actions as needed when the button is pressed
        print(f"{clicked_button.text()} pressed.")
    def on_button_pressed2(self, clicked_button, other_button):
        # Highlight the pressed button
        clicked_button.setStyleSheet("background-color: yellow; font-size: 20px; font-weight: bold;")
        self.imageList[self.current_index][4] = clicked_button.text()
        # Remove the highlight from the other button
        other_button.setStyleSheet("font-size: 20px; font-weight: bold;")
        # Perform other actions as needed when the button is pressed
        print(f"{clicked_button.text()} pressed.")
    def reset_button(self):
        self.button1.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        self.button2.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        self.button11.setStyleSheet(f"font-size: 20px;font-weight: bold;")
        self.button21.setStyleSheet(f"font-size: 20px;font-weight: bold;")
    def on_button_press(self):
        if self.current_index < len(self.imageList):
            current_time = QDateTime.currentDateTime()

            if self.last_press_time is not None:
                time_difference = self.last_press_time.msecsTo(current_time)
                print(f"Time between presses: {time_difference} milliseconds")
                self.imageList[self.current_index][6] = time_difference

            self.last_press_time = current_time
    def on_submit(self):
        self.text = self.text_input.text()
        if self.text != "":
            self.on_button_press()
    
    def handle_slider_value_changed(self, slider_index, new_value):
        print(f"Slider {slider_index + 1} value changed to: {new_value}")
        for con in self.confidenceList:
            if con[0] == slider_index:
                con[1] = new_value

    def handle_combo_value_changed(self, combo_index, new_value):
        print(f"Combo {combo_index + 1} value changed to: {new_value}")
        for con in self.confidenceList:
            if con[0] == combo_index:
                con[2] = new_value

    def handle_button_clicked(self, button_index):
        if button_index == None:
            print("it is blank")
        print(f"Button {button_index + 1} clicked.")
        self.selected_button = button_index
        
    def update_pen(self):
        if self.confidenceList[self.selected_button][2] != "I":
            print(self.selected_button+1)
            color = self.get_button_color(self.selected_button + 1)
            style = Qt.SolidLine if self.confidenceList[self.selected_button][2] == "Present" else Qt.DashLine

            # Set the pen color and style
            self.pen.setColor(QColor(*color))
            self.pen.setStyle(style)

            # You can also print or use the pen values as needed
            print(f"Pen Color: {color}, Style: {style}")
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
            ("Irregularity of cortical surface"),
            ("Tibial Spiking")
        ]
        return colors[index - 1]
    def get_rectangle_color_index(self, color):
        # This function returns the color index based on the color value
        colors = [
            (255, 165, 0),
            (0, 100, 0),
            (0, 0, 255),
            (128, 0, 128)
        ]
        for index, c in enumerate(colors):
            if c == color:
                return index + 1  # Adding 1 to make it 1-based index
        return None
    def has_one_rectangle_of_each_color(self):
        color_count = {1: 0, 2: 0, 3: 0, 4: 0}  # Assuming you have 4 colors, adjust as needed
        
        for rect_item in self.rectangles:
            color = rect_item.pen().color()
            r, g, b, _ = color.getRgb()  # Directly access R, G, B values

            color_index = self.get_rectangle_color_index((r, g, b))
            if color_index is not None:
                color_count[color_index] += 1

                # Print individual R, G, B values
                print(f"Color {color_index}: R={r}, G={g}, B={b}")
        print("Color Count:")
        print(color_count)
        
        result = all(count > 0 for count in color_count.values())
        print(f"Result: {result}")
        return result
    def clear_rectangles(self):
        for rect_item in self.rectangles:
            self.image_scene.removeItem(rect_item)
        self.rectangles.clear()
    def load_csv_data(self, target_text):
        try:
            with open(self.csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                self.csv_data = list(csv_reader)
                if not self.csv_data:
                    raise Exception("CSV file is empty")
        except Exception as e:
            self.csv_data = None
        self.csv_data = [row for row in self.csv_data if any(target_text.strip().lower() in cell.strip().lower() for cell in row)]
    def next_image(self):
        self.update_index()
        if(self.current_index < len(self.imageList)):
            image_path = "./original/" + self.imageList[self.current_index][2]

            # Set the image as the pixmap for the label
            image = QPixmap(image_path)
            image = image.scaled(QSize(300, 300), Qt.AspectRatioMode.KeepAspectRatio)
            
            # Set the image as the pixmap for the QLabel within the QGroupBox
            self.image_item.setPixmap(image)
            self.clear_rectangles()
            self.reset_button()
            self.slidersGroupBox.reset_sliders_group_box()
            self.subGroupBox.hide()
        else:
            self.subGroupBox.hide()
            self.clear_graphics_view()
    def namePlease(self):
        if self.text == "":
            incomplete_message = QMessageBox()
            incomplete_message.setIcon(QMessageBox.Warning)
            incomplete_message.setFixedSize(800, 200) 
            incomplete_message.setWindowTitle("ID not submitted")
            incomplete_message.setText("Need to fill in ID and submit")
            incomplete_message.exec_()
        else:
            a = self.confidenceList[0][2]
            b = self.confidenceList[1][2]
            c = self.confidenceList[2][2]
            d = self.confidenceList[3][2]
            print(a)
            print(b)
            print(c)
            print(d)
            if self.current_index > len(self.imageList) - 1:
                self.save_data()
                self.show_finish_popup()
            #elif self.imageList[self.current_index][3] != "your Label" and self.has_one_rectangle_of_each_color():
            elif self.imageList[self.current_index][3] != "your Label" and a != "" and b != "" and c != "" and d != "":
                self.mainGroupBox.setEnabled(False)
                if self.current_index == 0:
                    if self.imageList[self.current_index][4] == "your Label2":
                        self.setupSubGroupBox()
                    else:
                        pass
                elif self.current_index < len(self.imageList) - 1:
                    if self.imageList[self.current_index][4] == "your Label2":
                        self.setupSubGroupBox()
                    else:
                        pass
                elif self.current_index == len(self.imageList) - 1:
                    if self.imageList[self.current_index][4] == "your Label2":
                        self.setupSubGroupBox()
                    else:
                        pass
                else:
                    pass
            else:
                # Show a warning message if there is not at least one rectangle of each color
                warning_message = QMessageBox()
                warning_message.setIcon(QMessageBox.Warning)
                warning_message.setFixedSize(800, 200)
                warning_message.setWindowTitle("Incomplete Labeling")
                warning_message.setText("Please make your first decision before proceeding")
                warning_message.exec_()
            # if self.current_index < len(self.imageList) - 1:
                # self.show_duplicated_image_popup()
            # elif self.current_index == len(self.imageList) - 1:
                # self.show_duplicated_image_popup()
                # self.save_data()
            # else:
                # self.show_count_popup()
                # self.show_table_popup()
                # self.show_finish_popup()
    def save_scanning_percentage_image(self, duplicated_view, filename):
        # Create a QPainterPath to store the regions covered by red rectangles
        red_rects_path = QPainterPath()

        # Draw the red rectangles first and store their regions in the QPainterPath
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen_color = rect_item.pen().color()

            if pen_color == Qt.red:
                red_rects_path.addRect(rect)
        # Create a QPixmap with a white background
        pixmap = QPixmap(duplicated_view.viewport().size())
        pixmap.fill(Qt.white)

        # Create a QPainter to draw on the QPixmap
        painter = QPainter(pixmap)

        # Set the clip region to the area covered by red rectangles
        painter.setClipPath(red_rects_path)
        
        # Draw the red rectangles first and store their regions in the QPainterPath
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen_color = rect_item.pen().color()

            if pen_color == Qt.red:
                # Create a QPainterPath for the red rectangle
                red_rect_path = QPainterPath()
                red_rect_path.addRect(rect)

                # Draw the red rectangle
                painter.setPen(QPen(Qt.red))
                painter.fillRect(rect, Qt.red)
                painter.drawRect(rect)
        
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen_color = rect_item.pen().color()

            if pen_color != Qt.red:
                # Create a QPainterPath for the blue rectangle
                blue_rect_path = QPainterPath()
                blue_rect_path.addRect(rect)

                # Draw the blue rectangle
                painter.setPen(QPen(Qt.blue))
                painter.fillRect(rect, Qt.blue)
                painter.drawRect(rect)

        # End painting
        painter.end()
        
        # Save the modified image
        pixmap.save(filename)
        
        # Load the saved image to count the number of red and blue pixels
        saved_pixmap = QPixmap(filename)
        image = saved_pixmap.toImage()
        red_pixels = 0
        blue_pixels = 0

        for x in range(saved_pixmap.width()):
            for y in range(saved_pixmap.height()):
                pixel_color = image.pixelColor(x, y)

                if pixel_color == Qt.red:
                    red_pixels += 1
                elif pixel_color == Qt.blue:
                    blue_pixels += 1
        total_pixels = red_pixels + blue_pixels
        
        # Calculate the percentage based on the counts
        percent_red = (red_pixels / total_pixels) * 100.0
        percent_blue = (blue_pixels / total_pixels) * 100.0

        print(f"Scanning percentage image saved to: {filename}")
        print(f"Percentage of red pixels: {percent_red}%")
        print(f"Percentage of blue pixels: {percent_blue}%")

        return percent_blue

    def save_scanning_percentage_image_in_image(self, duplicated_view, filename, color):
        print("input name: \n")
        print(color)
        colors = self.rgb_to_hex(color)
        print("input output name: \n")
        print(colors)
        # Create a QPainterPath to store the regions covered by red rectangles
        red_rects_path = QPainterPath()

        # Draw the red rectangles first and store their regions in the QPainterPath
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen_color = rect_item.pen().color()

            if pen_color == Qt.red:
                red_rects_path.addRect(rect)
        # Create a QPixmap with a white background
        pixmap = QPixmap(duplicated_view.viewport().size())
        pixmap.fill(Qt.white)

        # Create a QPainter to draw on the QPixmap
        painter = QPainter(pixmap)

        # Set the clip region to the area covered by red rectangles
        painter.setClipPath(red_rects_path)
        
        # Draw the red rectangles first and store their regions in the QPainterPath
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen_color = rect_item.pen().color()
            print("Color label: \n")
            print(pen_color.name())
            if pen_color == Qt.red:
                # Create a QPainterPath for the red rectangle
                red_rect_path = QPainterPath()
                red_rect_path.addRect(rect)

                # Draw the red rectangle
                painter.setPen(QPen(Qt.red))
                painter.fillRect(rect, Qt.red)
                painter.drawRect(rect)
        
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            pen_color = rect_item.pen().color()

            if pen_color.name() == colors:
                # Create a QPainterPath for the blue rectangle
                blue_rect_path = QPainterPath()
                blue_rect_path.addRect(rect)

                # Draw the blue rectangle
                painter.setPen(QPen(Qt.blue))
                painter.fillRect(rect, Qt.blue)
                painter.drawRect(rect)

        # End painting
        painter.end()
        
        # Save the modified image
        pixmap.save(filename)
        
        # Load the saved image to count the number of red and blue pixels
        saved_pixmap = QPixmap(filename)
        image = saved_pixmap.toImage()
        red_pixels = 0
        blue_pixels = 0

        for x in range(saved_pixmap.width()):
            for y in range(saved_pixmap.height()):
                pixel_color = image.pixelColor(x, y)

                if pixel_color == Qt.red:
                    red_pixels += 1
                elif pixel_color == Qt.blue:
                    blue_pixels += 1
        total_pixels = red_pixels + blue_pixels
        
        # Calculate the percentage based on the counts
        percent_red = (red_pixels / total_pixels) * 100.0
        percent_blue = (blue_pixels / total_pixels) * 100.0

        print(f"Scanning percentage image saved to: {filename}")
        print(f"Percentage of red pixels: {percent_red}%")
        print(f"Percentage of blue pixels: {percent_blue}%")

        return percent_blue

    def on_button_clicked(self, duplicated_view, label):
        self.imageList[self.current_index][0] = self.text
        filename = f"./drawing_experimental/{self.imageList[self.current_index][0]}_{self.imageList[self.current_index][1]}_{label}.png"
        self.save_duplicated_image(duplicated_view, filename)
        self.imageList[self.current_index][4] = label
        self.on_button_press()
        self.imageList[self.current_index][7] = self.confidenceList[0][2]
        self.imageList[self.current_index][8] = self.confidenceList[0][1]
        self.imageList[self.current_index][9] = self.confidenceList[1][2]
        self.imageList[self.current_index][10] = self.confidenceList[1][1]
        self.imageList[self.current_index][11] = self.confidenceList[2][2]
        self.imageList[self.current_index][12] = self.confidenceList[2][1]
        self.imageList[self.current_index][13] = self.confidenceList[3][2]
        self.imageList[self.current_index][14] = self.confidenceList[3][1]
        self.imageList[self.current_index][17] = f"{self.total_percentage:.2f}%"

        self.selected_button = None
    def save_duplicated_image(self, duplicated_view, filename):
        pixmap = QPixmap(duplicated_view.viewport().size())
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        duplicated_view.render(painter)
        painter.end()
 
        pixmap.save(filename)
        print(f"Image saved to: {filename}")

    def clear_graphics_view(self):
        # Remove the current QGraphicsView from the image_groupbox_layout
        self.layout.removeWidget(self.image_view)
        self.image_view.setParent(None)

    def mousePressEvent(self, event):
        if self.image_item.boundingRect().contains(self.image_view.mapToScene(event.pos())):
            if self.selected_button == None or self.selected_button+1 == 0:
                self.drawing_enabled = False
            else:
                if self.confidenceList[self.selected_button][2] == "Present":
                    self.drawing_enabled = True
                    print("works")
                    self.update_pen()
                else:
                    self.drawing_enabled = False
                if event.button() == Qt.LeftButton and self.drawing_enabled:
                    # Draw a new rectangle
                    self.drawing_rect = True
                    self.start_point = self.image_view.mapToScene(event.pos())
                    self.current_rect = QGraphicsRectItem()
                    self.current_rect.setPen(self.pen)
                    self.image_scene.addItem(self.current_rect)
                elif event.button() == Qt.RightButton:
                    # Check if the click occurred over an existing rectangle
                    item = self.image_scene.itemAt(self.image_view.mapToScene(event.pos()), self.image_view.transform())
                    if item and isinstance(item, QGraphicsRectItem):
                        # Remove the selected rectangle
                        self.image_scene.removeItem(item)
                        self.rectangles.remove(item)
        super().mousePressEvent(event)

    def change_outline_color_and_style(self, color, style):
        self.pen.setColor(color)
        self.pen.setStyle(style)

    def mouseMoveEvent(self, event):
        if self.drawing_rect:
            end_point = self.image_view.mapToScene(event.pos())
            rect = self.calculateRect(self.start_point, end_point)

            # Ensure the rectangle stays within the image_view boundaries
            rect = rect.intersected(self.image_item.boundingRect())

            self.current_rect.setRect(rect)

    def mouseReleaseEvent(self, event):
        if self.drawing_rect:
            self.drawing_rect = False
            end_point = self.image_view.mapToScene(event.pos())
            rect = self.calculateRect(self.start_point, end_point)

            # Ensure the rectangle stays within the image_view boundaries
            rect = rect.intersected(self.image_item.boundingRect())

            # Check if the rectangle size is larger than 10 pixels in either dimension
            if rect.width() > 10 and rect.height() > 10:
                self.current_rect.setRect(rect)

                # Shift the rectangle by the original view position to match the image's position
                rect = self.current_rect.rect()
                self.current_rect.setRect(rect)

                self.rectangles.append(self.current_rect)
            else:
                # The rectangle is too small, so don't add it to the graphic scene
                self.image_scene.removeItem(self.current_rect)
    def show_confidence_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Confidence Level")
        dialog.setFixedSize(700,300)

        layout = QVBoxLayout(dialog)

        label = QLabel("How confident are you with your labeling?")
        label.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(1, 7)

        value_label = QLabel('Value: 1')
        numbers = QLabel("1                2                3                4                5                6                7")
        numbers.setStyleSheet(f"font-size: 20px; font-weight: bold;")
        numbers.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(numbers)
        layout.addWidget(slider)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        slider.valueChanged.connect(lambda value: value_label.setText(f'Value: {value}'))

        result = dialog.exec_()

        if result == QDialog.Accepted:
            confidence_value = slider.value()
            self.imageList[self.current_index][18] = confidence_value
            print(f"Confidence value: {confidence_value}")
            return True
        else:
            print("Dialog closed without accepting")
            return False
    def calculateRect(self, start, end):
        return QRectF(start, end).normalized()
    def update_index(self):
        self.current_index += 1
        if self.current_index < len(self.imageList)+1:
            progress_value = int((self.current_index / len(self.imageList)) * 100)
            self.progress_bar.setValue(progress_value)
    def write_to_csv(self):
        # Define the CSV file path
        csv_file_path = "ExperimentalDataSet.csv"  # Update with your desired file path

        # Create or open the CSV file in append mode
        with open(csv_file_path, mode='a', newline='') as file:
            csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(self.imageList)
    def save_data(self):
        # Save the data to the CSV file or perform any other necessary action
        self.imageList.sort(key=lambda x: int(x[1]))  # Sort the data based on image number
        self.write_to_csv()
        print("Data saved!")
    def show_finish_popup(self):
        # Create a custom QDialog for the message and close button
        popup_dialog = QDialog(self)
        popup_dialog.setWindowTitle("Confirmation")

        # Adjust the size of the dialog
        popup_dialog.resize(400, 200)

        # Remove the question mark icon from the window
        popup_dialog.setWindowFlags(popup_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        label = QLabel("Data saved successfully.")
        
        font = QFont()
        font.setPointSize(30)  # Set the font size to 16 (you can use your desired size)
        font.setBold(True)

        # Apply the font to the QGroupBox's title
        label.setFont(font)
        
        layout.addWidget(label)

        close_button = QPushButton("Close Entire Program")
        
        font = QFont()
        font.setPointSize(20)  # Set the font size to 16 (you can use your desired size)
        font.setBold(True)

        # Apply the font to the QGroupBox's title
        close_button.setFont(font)
        
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        popup_dialog.setLayout(layout)

        # Show the custom dialog
        result = popup_dialog.exec_()
if __name__ == "__main__":
    app = QApplication([])
    window = Reason_Box()
    window.show()
    app.exec_()