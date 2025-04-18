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

class Reason_Box(QGroupBox):
    def __init__(self):
        super().__init__("Allabeler")
        self.setMinimumSize(1342, 1324)
        self.last_mouse_pos = None
        self.last_press_time = None
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 40, 200, 25)  # Adjust the geometry as needed
        self.progress_bar.setValue(0)
        
        self.drawing_enabled = False  # Add this attribute
        
        self.selected_button = None
        
        self.confidenceList = [[0,1,"I"],[1,1,"I"],[2,1,"I"],[3,1,"I"]]
        
        self.comboIndex = 0
        
        self.current_row = 1
        self.csv_data = None
        self.selected_column = 4  # Change this to select a different column
        
        # Specify the file path to your CSV file
        self.csv_file_path = "new_images_re_1121.csv"
        
        self.load_csv_data("first")
        
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
        
        self.nextImage = QPushButton("Label", self)
        self.nextImage.clicked.connect(self.namePlease)
        self.nextImage.setMinimumWidth(200)
        self.nextImage.setMinimumHeight(100)
        
        font = self.nextImage.font()  # Get the current font
        font.setPointSize(20)  # Set the font size 
        self.nextImage.setFont(font)
        
        self.imageList = []
        for index, images in enumerate(self.csv_data):
            self.imageList.append(["ID",self.csv_data[index][0],self.csv_data[index][1],"your Label","your Label2",self.csv_data[index][2],0,"Y/N",1,"Y/N",1,"Y/N",1,"Y/N",1,self.csv_data[index][3]])
        random.shuffle(self.imageList)
        # Create a QGroupBox to encapsulate imageGroupBox and sliders_group_box
        mainGroupBox = QGroupBox("Main Group")
        
        subGroupBox = QGroupBox("Sub Group")

        # Create SlidersGroupBox
        self.slidersGroupBox = SlidersGroupBox()
        
        self.slidersGroupBox.slider_value_changed_signal.connect(self.handle_slider_value_changed)
        self.slidersGroupBox.combo_value_changed_signal.connect(self.handle_combo_value_changed)
        self.slidersGroupBox.button_clicked_signal.connect(self.handle_button_clicked)

        # Create a QGroupBox for image display
        imageGroupBox = QGroupBox("image")
        imageGroupBox.setMinimumWidth(505)
        #imageGroupBox.setStyleSheet("QGroupBox { border: 0; }")
        
        # Create a QLabel for displaying an image
        label = QLabel()

        # Load an image using QPixmap
        pixmap = QPixmap("Example.png")  # Replace with the actual path to your image
        pixmap = pixmap.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)  # Align the image to the center

        
        # Create a QGraphicsView widget to display the image
        self.image_view = QGraphicsView()
        self.image_view.setFixedSize(500, 500)

        # Create a QGraphicsScene to hold the image
        self.image_scene = QGraphicsScene()
        self.image_view.setScene(self.image_scene)

        # Add an image to the scene
        image_path = "./original/" + self.imageList[self.current_index][2]
        image = QPixmap(image_path)
        image = image.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio)
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
        
        textGroupBox = QGroupBox("Instruction")
        
        # Set the font for the title label
        title_font = QFont()
        title_font.setPointSize(18)  # Adjust the font size as needed
        textGroupBox.setFont(title_font)
        
        # Create a QLabel for instructions
        instruction_label = QLabel("1. look for the feature \n2. click on the feature button and select if the feature is visible by selecting \"O\", if not select \"X\"\n3. draw the box of the feature \n4. match the confidence level of that specific feature by dragging the slider  \n5. Redo the same process for the rest of the features in that order")
        instruction_label.setAlignment(Qt.AlignLeft)

        # Set the font for the instruction label
        instruction_font = QFont()
        instruction_font.setPointSize(16)
        instruction_label.setFont(instruction_font)
        
        # Create a layout for textGroupBox
        textLayout = QVBoxLayout()

        # Add the instruction label to the layout
        textLayout.addWidget(instruction_label)

        # Set the layout for textGroupBox
        textGroupBox.setLayout(textLayout)
        
        # Create and add a QGroupBox
        Labelbox = QGroupBox("Label")
        Labelbox_layout = QHBoxLayout()

        # Add widgets to the group box layout (e.g., QLabel, QSpinBox, etc.)
        # Example: group_box_layout.addWidget(QLabel("Your Additional Information"))
        
        # Add buttons to group_box2_layout
        button1 = QPushButton("Arthritis")
        button2 = QPushButton("Non-Arthritis")
        button1.setStyleSheet(f"font-size: 20px;")
        button2.setStyleSheet(f"font-size: 20px;")
        # Connect button click signals to custom methods
        button1.clicked.connect(lambda: self.on_button_pressed(button1, button2))
        button2.clicked.connect(lambda: self.on_button_pressed(button2, button1))
        Labelbox_layout.addWidget(button1)
        Labelbox_layout.addWidget(button2)
        
        # Set the layout for the group box
        Labelbox.setLayout(Labelbox_layout)
        
        # Set up the layout for the combined group
        mainLayout = QGridLayout()
        mainLayout.addWidget(imageGroupBox, 1, 0, 4, 4)
        mainLayout.addWidget(self.slidersGroupBox , 1, 4, 1, 1)
        mainLayout.addWidget(textGroupBox, 0, 0, 1, 5)
        mainLayout.addWidget(self.nextImage, 4, 4, 1, 1)
        mainLayout.addWidget(Labelbox, 2, 4, 1, 1)
        mainGroupBox.setLayout(mainLayout)
        
        subLayout = QGridLayout()
        subLayout.addWidget(label, 0, 1, 1, 1)
        subGroupBox.setLayout(subLayout)
        subGroupBox.setMaximumWidth(1200)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.text_input, 0, 0, 1, 1)
        self.layout.addWidget(saveID, 0, 1, 1, 1)
        self.layout.addWidget(subGroupBox, 1, 0, 2, 2)
        self.layout.addWidget(mainGroupBox, 0, 2, 3, 3)
        self.layout.addWidget(self.progress_bar, 4, 0, 1, 5)
        self.setLayout(self.layout)
    def on_button_pressed(self, clicked_button, other_button):
        # Highlight the pressed button
        clicked_button.setStyleSheet("background-color: yellow; font-size: 20px;")
        self.imageList[self.current_index][3] = clicked_button.text()
        # Remove the highlight from the other button
        other_button.setStyleSheet("font-size: 20px;")
        # Perform other actions as needed when the button is pressed
        print(f"{clicked_button.text()} pressed.")
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
            style = Qt.SolidLine if self.confidenceList[self.selected_button][2] == "O" else Qt.DashLine

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
            self.Label.setText(f"Error: {str(e)}")
            self.open_button.setEnabled(False)
        self.csv_data = [row for row in self.csv_data if any(target_text.strip().lower() in cell.strip().lower() for cell in row)]
    def next_image(self):
        self.update_index()
        if(self.current_index < len(self.imageList)):
            image_path = "./original/" + self.imageList[self.current_index][2]

            # Set the image as the pixmap for the label
            image = QPixmap(image_path)
            image = image.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio)
            
            # Set the image as the pixmap for the QLabel within the QGroupBox
            self.image_item.setPixmap(image)
            self.clear_rectangles()
            self.slidersGroupBox.reset_sliders_group_box()
        else:
            
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
            # if self.imageList[self.current_index][3] != "your label" and self.has_one_rectangle_of_each_color():
                # if self.current_index < len(self.imageList) - 1:
                    # self.show_duplicated_image_popup()
                # elif self.current_index == len(self.imageList) - 1:
                    # self.show_duplicated_image_popup()
                    # self.save_data()
                # else:
                    # self.show_count_popup()
                    # self.show_table_popup()
                    # self.show_finish_popup()
            # else:
                # # Show a warning message if there is not at least one rectangle of each color
                # warning_message = QMessageBox()
                # warning_message.setIcon(QMessageBox.Warning)
                # warning_message.setFixedSize(800, 200)
                # warning_message.setWindowTitle("Incomplete Labeling")
                # warning_message.setText("Please draw all your reasoning on the graphic before proceeding")
                # warning_message.exec_()
            if self.current_index < len(self.imageList) - 1:
                self.show_duplicated_image_popup()
            elif self.current_index == len(self.imageList) - 1:
                self.show_duplicated_image_popup()
                self.save_data()
            else:
                self.show_count_popup()
                self.show_table_popup()
                self.show_finish_popup()
    def show_duplicated_image_popup(self):
        popup = QDialog(self)
        popup.setWindowTitle("Duplicated Image with Boxes")
        print(self.imageList[self.current_index][1])
        
        # Create a QLabel for displaying the XAI image
        xai_label = QLabel()
        xai_label.setAlignment(Qt.AlignCenter)
        
        self.feedback_messages = []

        # Load the XAI image (replace with your actual XAI image path)
        xai_image_path = "./xai/" + self.imageList[self.current_index][2]
        xai_image = QPixmap(xai_image_path)
        xai_image = xai_image.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio)
        
        image = cv2.imread(xai_image_path)
        resized_image = cv2.resize(image, (500,500))

        hsv = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a QLabel for displaying the duplicated image
        duplicated_label = QLabel()
        duplicated_label.setAlignment(Qt.AlignCenter)
        
        # Load the original image
        original_image_path = "./original/" + self.imageList[self.current_index][2]
        original_image = cv2.imread(original_image_path)
        resized_original_image = cv2.resize(original_image, (500,500))

        result_image = np.copy(resized_original_image)
        tint_color = (0, 0, 255, 0.25)

        # Iterate through contours and draw filled bounding boxes on the resized original image
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            overlay = resized_original_image.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), tint_color[:3], -1)
            resized_original_image = cv2.addWeighted(resized_original_image, 1 - tint_color[3], overlay, tint_color[3], 0)

            # Create a QGraphicsRectItem for the drawn rectangle
            rect_item = QGraphicsRectItem(x, y, w, h)
            rect_item.setPen(QPen(Qt.red))  # Set the pen color to red
            self.rectangles.append(rect_item)  # Add the rectangle to the list of rectangles

        # Convert OpenCV image to QImage
        height, width, channel = resized_original_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(resized_original_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(q_image)

        # Scale the QPixmap to make it bigger
        scaled_pixmap = pixmap.scaledToWidth(500)  # Adjust the width as needed

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
        duplicated_view.setFixedSize(505, 505)
        duplicated_view.setScene(duplicated_scene)
        
        # Iterate through the rectangles and check for overlap
        for rect_item in self.rectangles:
            rect = rect_item.rect()
            color = ""
            # Check if the rectangle item intersects with any red box
            overlap_percentage = self.check_overlap(rect)
            if overlap_percentage > 0:
                # Get the pen color of the rectangle
                pen_color = rect_item.pen().color()
                
                # Convert the pen color to an RGB tuple
                pen_color_rgb = (pen_color.red(), pen_color.green(), pen_color.blue())

                print(f"The color of the rectangle is: {pen_color_rgb}")
                for i in range(4):
                    if pen_color_rgb == self.get_button_color(i):
                        color = self.get_button_color_name(i)
                
                
                # Save the feedback message to the list
                feedback_text = f"Overlap detected with {color} and AI focus area" + f": {overlap_percentage:.2f}% overlap"
                self.feedback_messages.append(feedback_text)
        
        # Set the XAI image as the pixmap for the QLabel
        xai_label.setPixmap(xai_image)
        
        # Create and add a QGroupBox
        group_box = QGroupBox("Feedback")
        group_box_layout = QVBoxLayout()
        
        # Add widgets to the group box layout (e.g., QLabel, QSpinBox, etc.)
        # Example: group_box_layout.addWidget(QLabel("Your Additional Information"))
        # Create a local QLabel for feedback messages
        feedback_label = QLabel()
        feedback_label.setAlignment(Qt.AlignLeft)
        if len(self.feedback_messages) > 1:
            feedback_label.setText("\n".join(self.feedback_messages[:-1]))
        else:
            feedback_label.setText("There is no overlap with the AI focus area")
        feedback_label.setStyleSheet(f"font-size: 16px;")
        group_box_layout.addWidget(feedback_label)
        
        # Set the layout for the group box
        group_box.setLayout(group_box_layout)
        
        
        # Create and add a QGroupBox
        group_box2 = QGroupBox("Label")
        group_box2_layout = QHBoxLayout()

        # Add widgets to the group box layout (e.g., QLabel, QSpinBox, etc.)
        # Example: group_box_layout.addWidget(QLabel("Your Additional Information"))
        
        # Add buttons to group_box2_layout
        button1 = QPushButton("Arthritis")
        button2 = QPushButton("Non-Arthritis")
        button1.setStyleSheet(f"font-size: 20px;")
        button2.setStyleSheet(f"font-size: 20px;")
        button1.clicked.connect(popup.accept)  # Close the popup when button1 is clicked
        button2.clicked.connect(popup.accept)  # Close the popup when button2 is clicked
        button1.clicked.connect(lambda: self.on_button_clicked(duplicated_view, "Arthritis"))
        button2.clicked.connect(lambda: self.on_button_clicked(duplicated_view, "Non-Arthritis"))
        button1.clicked.connect(self.next_image)
        button2.clicked.connect(self.next_image)
        group_box2_layout.addWidget(button1)
        group_box2_layout.addWidget(button2)
        
        AI_label = QLabel(f"AI Suggestion: {self.imageList[self.current_index][15]}")
        AI_label.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        AI_label.setAlignment(Qt.AlignCenter)
        
        Your_label = QLabel(f"Your Label: {self.imageList[self.current_index][3]}")
        Your_label.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        Your_label.setAlignment(Qt.AlignCenter)
        
        # Set the layout for the group box
        group_box2.setLayout(group_box2_layout)
        
        # Create a QGroupBox for colored labels
        color_group_box = QGroupBox("Color Labels")
        color_group_box_layout = QHBoxLayout()

        # Define colors and corresponding labels
        color_labels = [(0, f"Narrow Joint Space: {self.confidenceList[0][2]}, {self.confidenceList[0][1]}"), (1, f"Osteophytes: {self.confidenceList[1][2]}, {self.confidenceList[1][1]}"), (2, f"Irregularity: {self.confidenceList[2][2]}, {self.confidenceList[2][1]}"), (3, f"Tibial Spiking: {self.confidenceList[3][2]}, {self.confidenceList[3][1]}")]

        for color, label_text in color_labels:
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {'rgb' + str(self.get_button_color(color+1))}; font-weight: bold; font-size: 20px;")
            label.setAlignment(Qt.AlignCenter)
            color_group_box_layout.addWidget(label)

        # Set the layout for the color group box
        color_group_box.setLayout(color_group_box_layout)
        
        # Create a layout to arrange the views side by side
        layout = QGridLayout()
        layout.addWidget(xai_label, 0, 0, 1, 1)
        layout.addWidget(duplicated_view, 0, 1, 1, 1)
        layout.addWidget(AI_label, 1, 0, 1, 1)
        layout.addWidget(Your_label, 1, 1, 1, 1)
        layout.addWidget(group_box, 3, 0, 1, 2)
        layout.addWidget(group_box2, 4, 0, 1, 2)
        layout.addWidget(color_group_box, 2, 0, 1, 2)  # Add the color group box to the layout

        # Set the layout for the pop-up
        popup.setLayout(layout)
        if self.rectangles:
            last_rect_item = self.rectangles.pop(-1)
        # Show the pop-up
        
        popup.exec_()
    def on_button_clicked(self, duplicated_view, label):
        filename = f"./drawing_experimental/{self.imageList[self.current_index][0]}_{self.imageList[self.current_index][1]}_{label}.png"
        self.save_duplicated_image(duplicated_view, filename)
        self.imageList[self.current_index][0] = self.text
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
        if self.current_index == len(self.imageList) - 1:
            self.nextImage.setText("Done")

    def save_duplicated_image(self, duplicated_view, filename):
        pixmap = QPixmap(duplicated_view.viewport().size())
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        duplicated_view.render(painter)
        painter.end()
 
        pixmap.save(filename)
        print(f"Image saved to: {filename}")
    def calculate_overlap(self, rect_coords, contour_coords):
        # Rectangles are assumed to be in the format (x, y, width, height)
        poly1 = Polygon([(rect_coords[0], rect_coords[1]),
                         (rect_coords[0] + rect_coords[2], rect_coords[1]),
                         (rect_coords[0] + rect_coords[2], rect_coords[1] + rect_coords[3]),
                         (rect_coords[0], rect_coords[1] + rect_coords[3])])

        poly2 = Polygon([(contour_coords[0], contour_coords[1]),
                         (contour_coords[0] + contour_coords[2], contour_coords[1]),
                         (contour_coords[0] + contour_coords[2], contour_coords[1] + contour_coords[3]),
                         (contour_coords[0], contour_coords[1] + contour_coords[3])])

        # Calculate the intersection area
        intersection = poly1.intersection(poly2).area

        # Calculate the percentage overlap
        overlap_percentage = (intersection / poly1.area) * 100

        return overlap_percentage
        
    # Modify your existing check_overlap function to use calculate_overlap
    def check_overlap(self, rect):
        if len(self.rectangles) < 2 or rect == self.rectangles[-1]:
            return 0  # No overlap if there are fewer than two rectangles

        last_rect_item = self.rectangles[-1]  # Get the last rectangle item from the list
        last_rect_coords = last_rect_item.rect().getCoords()
        
        rect_coords = rect.getCoords()

        overlap_percentage = self.calculate_overlap(last_rect_coords, rect_coords)

        if overlap_percentage > 0:
            return overlap_percentage

        return 0  # No overlap with any of the previous rectangles
 
    def clear_graphics_view(self):
        # Remove the current QGraphicsView from the image_groupbox_layout
        self.layout.removeWidget(self.image_view)
        self.image_view.setParent(None)

        # Create a QLabel with the "complete.png" image
        complete_label = QLabel()
        complete_image = QPixmap("complete.png")  # Replace with the actual path to your image
        complete_image = complete_image.scaled(QSize(400, 400), Qt.AspectRatioMode.KeepAspectRatio)
        complete_label.setPixmap(complete_image)
        complete_label.setAlignment(Qt.AlignCenter | Qt.AlignRight)

        # Add the label to the image_groupbox_layout
        self.layout.addWidget(complete_label, 1, 1, 2, 2)

    def mousePressEvent(self, event):
        if self.image_item.boundingRect().contains(self.image_view.mapToScene(event.pos())):
            if self.selected_button == None or self.selected_button+1 == 0:
                self.drawing_enabled = False
            else:
                if self.confidenceList[self.selected_button][2] != "I":
                    self.drawing_enabled = True
                    print("works")
                    self.update_pen()
                else:
                    self.drawing_enabled = False
                if event.button() == Qt.RightButton and self.drawing_enabled:
                    # Draw a new rectangle
                    self.drawing_rect = True
                    self.start_point = self.image_view.mapToScene(event.pos())
                    self.current_rect = QGraphicsRectItem()
                    self.current_rect.setPen(self.pen)
                    self.image_scene.addItem(self.current_rect)
                elif event.button() == Qt.LeftButton:
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
    def show_count_popup(self):
        matching_count = sum(1 for item in self.imageList if item[4] == item[5])

        count_message = QMessageBox()
        count_message.setIcon(QMessageBox.Information)
        count_message.setWindowTitle("Total correct Label")
        count_message.setText(f"Labeling Score: {matching_count}/10")
        count_message.exec_()
        
    def show_table_popup(self):
        # Create a custom QDialog for the table grid
        table_dialog = QDialog(self)
        table_dialog.setWindowTitle("Table of Solution")

        # Adjust the size of the dialog
        table_dialog.resize(950, 1000)

        # Create a QTableWidget
        table_widget = QTableWidget()

        # Set the column count
        table_widget.setColumnCount(6)

        # Set the column headers
        table_widget.setHorizontalHeaderLabels(["ID", "Image Number", "Image", "Your Label", "Answer", "Time"])

        # Add data to the table
        for row, data in enumerate(self.imageList):
            # Set the row height for all rows
            table_widget.verticalHeader().setDefaultSectionSize(300)  # Adjust the height as needed
            table_widget.insertRow(row)

            # Column 1: Text
            text_item = QTableWidgetItem(data[0])
            table_widget.setItem(row, 0, text_item)

            # Column 2: Integer
            integer_item = QTableWidgetItem(str(data[1]))
            table_widget.setItem(row, 1, integer_item)
            
            table_widget.setColumnWidth(2, 300)  # Adjust the width as needed for the image column

            # Optionally, you can set the other column widths based on content
            for col in range(table_widget.columnCount()):
                table_widget.resizeColumnToContents(col)
            
            # Column 3: Images
            image_item = QTableWidgetItem()
            image_path = "./original/" + data[2]
            image_label = QLabel()
            image_label.setPixmap(QPixmap(image_path).scaledToWidth(300))  # Adjust the width as needed
            table_widget.setCellWidget(row, 2, image_label)

            # Columns 4 and 5: Text
            text_item = QTableWidgetItem(data[4])
            table_widget.setItem(row, 3, text_item)
            
            text_item = QTableWidgetItem(data[5])
            table_widget.setItem(row, 4, text_item)

            # Column 6: Time (assuming image_data[5] is a QDateTime object)
            time_item = QTableWidgetItem(str(data[6]/1000)+ " sec")
            table_widget.setItem(row, 5, time_item)

        layout = QVBoxLayout()
        layout.addWidget(table_widget)

        table_dialog.setLayout(layout)

        # Show the custom dialog
        result = table_dialog.exec_()
if __name__ == "__main__":
    app = QApplication([])
    window = Reason_Box()
    window.show()
    app.exec_()