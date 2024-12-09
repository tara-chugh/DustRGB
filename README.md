# Dust RGB Satellite Image Viewer
## Executive Summary
Satellites capture images at multiple wavelengths of light, which helps identify different particles in Earth’s atmosphere because they reflect light differently. However, detecting dust plumes in satellite images is challenging since fog, dust, and clouds often appear in similar colors. Scientists overcome this by creating “Dust RGB” composite images that combine data from multiple wavelengths, making it easier to distinguish these atmospheric features by their unique colors. Currently, interpreting these images requires specialized meteorologists to analyze them manually. My project automates this process by using color-matching techniques that mimic human color perception to classify Dust RGB image pixels into distinct atmospheric conditions. Users can specify a region and time, view the satellite imagery, and identify dust conditions by clicking on pixels, with real-time classifications provided. While the tool's results match manual interpretations, further validation by meteorologists is needed to improve its accuracy. This project enhances accessibility to atmospheric analysis and opens possibilities for integrating additional climate data and expert feedback to refine the tool.

# Instructions for running the code: 
## Dependencies
Install all the necessary python libraries with this command: `pip install requests numpy pyqt5 scikit-image plotly pyciede2000 pillow`


## Make the 3D LAB color space plot
Run the LAB_3d_Plot.py file (with 'python3 LAB_3d_Plot.py' in the command line). It will take a moment for the plot to be generated. The plot will open as an HTML file and should open in your browser. The plot is interactive, so you can zoom, rotate, and click on the plot.

<img width="253" alt="Screenshot 2024-12-09 at 12 19 08 PM" src="https://github.com/user-attachments/assets/90ced773-65a6-472c-9b4e-e639dc28aa33">

## Run the interactive image viewer
Run the app.py file (with 'python3 app.py' in the command line). It should open up a new window with the interactive viwer in it. Fill in all the fields on the left hand column (example values are provided in the text boxes). Note that the timestamp must be within the past 24 hours UTC (this is all that the free Meteomatics API subscription allows us to query). Press 'Fetch Image' for the image to show up on the right hand panel. If you inputted any of the input fields incorrectly, an error will appear on the bottom left. Click around on different parts of the image, and see the climate interpretation of those locations on the bottom left of the window.

The free Meteomatics API that I set up is a 2-week trial, so it expires on Dec 18. After this, the API credentials text box would need to be updated.

![ezgif-7-78edfdda95](https://github.com/user-attachments/assets/ead7b0ad-0ef9-49c5-870e-5ecb9be31ae9)
