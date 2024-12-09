import sys
import requests
from io import BytesIO
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from skimage import io
import numpy as np
import plotly.graph_objects as go
from skimage import color
from pyciede2000 import ciede2000
from PIL import Image
import io


# Main Graphical User Interface class for the interactive viewer
class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()  # Initialize QMain window
        self.setWindowTitle("Dust RGB Image Viewer")
        self.initUI()  # initialize coponents of the UI

        # RGB reference values for different dust/climate conditions
        self.rgb_centers = (
            np.array(
                [
                    [235, 50, 175],  # Dust aloft
                    [150, 5, 5],  # High, thick cloud
                    [5, 1, 5],  # High, thin cloud
                    [140, 75, 15],  # Mid, thick cloud
                    [15, 90, 20],  # Mid, thin cloud
                    [170, 130, 190],  # Low, thick cloud (warm climate)
                    [170, 130, 50],  # Low, thick cloud (cold climate)
                ]
            )
            / 255.0
        )  # Normalize values to be between 0 and 1

        # Convert RGB reference colors to L*A*B* color space
        self.lab_centers = color.rgb2lab(self.rgb_centers.reshape(1, -1, 3)).reshape(
            -1, 3
        )
        self.lab_centers_conditions = [
            "Dust aloft",
            "High, thick cloud",
            "High, thin cloud",
            "Mid, thick cloud",
            "Mid, thin cloud",
            "Low, thick cloud (warm climate)",
            "Low, thick cloud (cold climate)",
        ]

    # Setup the layout and default values of the graphical user interface
    def initUI(self):
        main_layout = QHBoxLayout()

        # Left Panel: Input fields for map bounds and API credentials,
        # filling with default values that can be edited
        self.north_input = QLineEdit("60.0")
        self.west_input = QLineEdit("-10.0")
        self.south_input = QLineEdit("30.0")
        self.east_input = QLineEdit("40.0")
        self.timestamp_input = QLineEdit("2024-12-12T18:00:00Z")
        self.username_input = QLineEdit("chicago_chugh_tara")
        self.password_input = QLineEdit("Qdxy1TxR14")
        self.password_input.setEchoMode(
            QLineEdit.Password
        )  # Hide the password so it's not in plain text

        # Button to get image from the API
        self.fetch_button = QPushButton("Fetch Image")
        self.fetch_button.clicked.connect(self.fetch_image)

        # Label to show pixel information/interpretation
        self.info_label = QLabel("Pixel Info: N/A")
        self.info_label.setWordWrap(True)

        # Setup the layout of the left panel, which has all the input boxes and buttons
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Map Coordinate Bounds:"))
        left_panel.addWidget(QLabel("North:"))
        left_panel.addWidget(self.north_input)
        left_panel.addWidget(QLabel("West:"))
        left_panel.addWidget(self.west_input)
        left_panel.addWidget(QLabel("South:"))
        left_panel.addWidget(self.south_input)
        left_panel.addWidget(QLabel("East:"))
        left_panel.addWidget(self.east_input)
        left_panel.addWidget(QLabel("Timestamp (must be within previous day UTC):"))
        left_panel.addWidget(self.timestamp_input)
        left_panel.addWidget(QLabel("Meteomatics API Username:"))
        left_panel.addWidget(self.username_input)
        left_panel.addWidget(QLabel("Meteomatics API Password:"))
        left_panel.addWidget(self.password_input)
        left_panel.addWidget(self.fetch_button)
        left_panel.addWidget(self.info_label)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        # Setup right panel, which has the image viewer part of the application
        self.image_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.image_view.setScene(self.scene)

        # Add left and right panels together into one combined layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.image_view)

        # Setup central widget of the window
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Fill this with image data after we fetch the image from the API
        self.image_data = None

    # Fetches the image from the API based on the text input parameters
    def fetch_image(self):
        # Get the inputs for coordinates, timestamp, and API credentials
        north = self.north_input.text()
        west = self.west_input.text()
        south = self.south_input.text()
        east = self.east_input.text()
        timestamp = self.timestamp_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        # Return an error if not all information is filled in
        if not all([north, west, south, east, timestamp, username, password]):
            self.info_label.setText("Error: All fields must be filled.")
            return

        # Construct API request URL for Meteomatics API
        BASE_URL = "https://api.meteomatics.com"
        PARAMETER = "sat_day_fog:idx"
        COORDINATES = f"{north},{west}_{south},{east}"
        RESOLUTION = "0.1,0.1"
        FORMAT = "png"

        url = f"{BASE_URL}/{timestamp}/{PARAMETER}/{COORDINATES}:{RESOLUTION}/{FORMAT}"

        try:
            # Make the PI request
            response = requests.get(url, auth=(username, password))
            response.raise_for_status()

            # Process image data using PILLOW
            image = Image.open(io.BytesIO(response.content))
            image = image.convert("RGB")  # Ensure RGB format
            data = image.tobytes()
            width, height = image.size

            # Create QImage from the image data
            q_image = QImage(data, width, height, 3 * width, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            self.image_data = np.array(
                image
            )  # Store image data as a numpy array for analysis
            self.display_image(pixmap)  # display the image in the viewer
            self.info_label.setText("Pixel Info: Click on the image.")
        except Exception as e:
            self.info_label.setText(f"Error fetching image: {e}")

    # Clear the right panel and display the new image in the viewers
    def display_image(self, pixmap):
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.image_view.setScene(self.scene)
        self.image_view.mousePressEvent = self.get_pixel_info

    # Handle pixel clicks on the images to display pixel information
    def get_pixel_info(self, event):
        if self.image_data is None:
            self.info_label.setText("Error: No image loaded.")
            return

        # Get the position of the mouse click in the image
        pos = self.image_view.mapToScene(event.pos())
        x = int(pos.x())
        y = int(pos.y())

        # Make sure the mouse click is within the image bounds
        if 0 <= x < self.image_data.shape[1] and 0 <= y < self.image_data.shape[0]:
            north = float(self.north_input.text())
            west = float(self.west_input.text())
            south = float(self.south_input.text())
            east = float(self.east_input.text())

            # Calculate the lat lon from the pixel by a linear transformation
            lat = north - ((north - south) / self.image_data.shape[0]) * y
            lon = west + ((east - west) / self.image_data.shape[1]) * x

            # Get RGB values of the pixel and convert to LAB, find distances to 7 represetative colors
            # and assign to closest one.
            pixel = self.image_data[y, x]
            rgb = tuple(pixel / 255.0)
            lab_converted = color.rgb2lab(np.array(rgb).reshape(1, 1, 3)).reshape(-1, 3)
            # Calculate the color difference (ΔE using CIEDE formula) to each LAB center
            distances = [
                ciede2000(lab_converted[0], center)["delta_E_00"]
                for center in self.lab_centers
            ]
            min_distance = min(distances)

            # Display the closest dust/climate condition if the ΔE is small
            if min_distance < 20:
                nearest_index = np.argmin(distances)
                self.info_label.setText(
                    f"Lat/Lon: ({lat:.4f}, {lon:.4f}): {self.lab_centers_conditions[nearest_index]}, ΔE: {min_distance:.2f}"
                )
            else:
                self.info_label.setText(
                    f"Lat/Lon: ({lat:.4f}, {lon:.4f}): No Dust RGB Climate Conditions Found"
                )

        else:
            self.info_label.setText("Pixel Info: Out of bounds.")


if __name__ == "__main__":
    # Start up the application and open the window
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.resize(800, 600)
    viewer.show()
    sys.exit(app.exec_())
