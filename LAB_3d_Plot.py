import numpy as np
import plotly.graph_objects as go
from skimage import color
from pyciede2000 import ciede2000

# Define RGB center points for the 7 representative samples.
rgb_centers = (
    np.array(
        [
            [235, 50, 175],
            [150, 5, 5],
            [5, 1, 5],
            [140, 75, 15],
            [15, 90, 20],
            [170, 130, 190],
            [170, 130, 50],
        ]
    )
    / 255.0
)  # Normalize RGB to [0, 1] range

# Convert RGB centers to the L*a*b* color space
lab_centers = color.rgb2lab(rgb_centers.reshape(1, -1, 3)).reshape(-1, 3)

# Create 3D grid in Lab space using the L*a*b* dimension ranges
# Show only 64 points in each dimension so the plot gets generated quickly.
L = np.linspace(0, 100, 64)  # L* = Lightness
a = np.linspace(-128, 127, 64)  # a* = Green to Red
b = np.linspace(-128, 127, 64)  # b* = Blue to Yellow
LL, aa, bb = np.meshgrid(L, a, b, indexing="ij")
lab_points = np.stack([LL.ravel(), aa.ravel(), bb.ravel()], axis=-1)

# Calculate CIEDE2000 color differences for each point in the L*a*b* space,
# using the CIEDE2000 function from pyciede2000. Then assign each point in the L*a*b*
# space to the representative color that it most closely matches (has the smallest
# CIEDE difference with).
nearest_indices = []
for point in lab_points:
    distances = [ciede2000(point, center)["delta_E_00"] for center in lab_centers]
    min_distance = min(distances)
    nearest_indices.append(np.argmin(distances))

nearest_indices = np.array(nearest_indices)

# Map colors from nearest centers of representative colors.
rgb_colors = np.zeros((len(nearest_indices), 3))
rgb_colors[nearest_indices != -1] = rgb_centers[nearest_indices[nearest_indices != -1]]

# Maka a 3D plot in Plotly.
fig = go.Figure()

fig.add_trace(
    go.Scatter3d(
        x=lab_points[:, 0],  # L* = Lightness
        y=lab_points[:, 1],  # a* = Green-Red
        z=lab_points[:, 2],  # b* = Blue-Yellow
        mode="markers",
        marker=dict(size=2, color=rgb_colors, opacity=0.7),
    )
)

# Set bounds for hte plot in L*a*b* space.
fig.update_layout(
    scene=dict(
        xaxis=dict(title="L* (Lightness)", range=[0, 100]),
        yaxis=dict(title="a* (Green to Red)", range=[-128, 127]),
        zaxis=dict(title="b* (Blue to Yellow)", range=[-128, 127]),
    ),
    title="3D Space Colored by Nearest RGB Centers (CIEDE2000)",
)

# Show the HTML plot in browser.
fig.show()
