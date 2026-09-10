import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# --------------------------------
# Circle parameters
# --------------------------------
R = 5
xc, yc = 0, 0

# Slant angle of parallel chords
angle = np.radians(8)

# Direction along the chords
dx = np.cos(angle)
dy = np.sin(angle)

# Perpendicular direction
nx = -np.sin(angle)
ny = np.cos(angle)

# 4 parallel chord positions
d = [-2.5, -0.8, 0.8, 2.5]

# --------------------------------
# Create figure
# --------------------------------
fig, ax = plt.subplots(figsize=(8, 8))

# --------------------------------
# Circle clipping boundary
# --------------------------------
circle = Circle(
    (xc, yc),
    R,
    facecolor="none",
    edgecolor="black",
    linewidth=3
)

ax.add_patch(circle)

# --------------------------------
# SHADED BANDS
# --------------------------------
shaded_bands = [
    (d[0], d[1]),   # upper band
    (d[2], d[3])    # lower band
]

for d1, d2 in shaded_bands:

    t = np.linspace(-10, 10, 1000)

    # Four corners of large band
    x1 = d1 * nx + t * dx
    y1 = d1 * ny + t * dy

    x2 = d2 * nx + t * dx
    y2 = d2 * ny + t * dy

    # Fill grey band
    band = ax.fill(
        np.concatenate([x1, x2[::-1]]),
        np.concatenate([y1, y2[::-1]]),
        color="lightgrey"
    )[0]

    # Clip the band to the circle
    band.set_clip_path(circle)

# --------------------------------
# DIAGONAL HATCHING
# --------------------------------
for d1, d2 in shaded_bands:

    for t in np.arange(-10, 10, 0.45):

        x_start = d1 * nx + t * dx
        y_start = d1 * ny + t * dy

        x_end = d2 * nx + t * dx
        y_end = d2 * ny + t * dy

        line, = ax.plot(
            [x_start, x_end],
            [y_start, y_end],
            color="black",
            linewidth=0.8
        )

        # Clip hatch lines to circle
        line.set_clip_path(circle)

# --------------------------------
# DRAW THE 4 PARALLEL CHORDS
# --------------------------------
for distance in d:

    # Calculate chord length
    half_length = np.sqrt(R**2 - distance**2)

    # First endpoint
    x1 = distance * nx - half_length * dx
    y1 = distance * ny - half_length * dy

    # Second endpoint
    x2 = distance * nx + half_length * dx
    y2 = distance * ny + half_length * dy

    ax.plot(
        [x1, x2],
        [y1, y2],
        color="black",
        linewidth=2
    )

# --------------------------------
# Center point
# --------------------------------
ax.plot(
    xc,
    yc,
    "ko",
    markersize=6
)

# --------------------------------
# Formatting
# --------------------------------
ax.set_aspect("equal")

ax.set_xlim(-5.5, 5.5)
ax.set_ylim(-5.5, 5.5)

ax.axis("off")

plt.show()