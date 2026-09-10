import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# --------------------------------
# Parameters
# --------------------------------
R = 2
hc, kc = 0, 0

# 6 different colors for outside circles
outside_colors = [
    "red",
    "orange",
    "green",
    "cyan",
    "blue",
    "purple"
]

# 2 colors for center circle
center_top_color = "yellow"
center_bottom_color = "pink"

theta = np.linspace(0, 2 * np.pi, 500)

# --------------------------------
# Create figure
# --------------------------------
fig, ax = plt.subplots(figsize=(8, 8))

# --------------------------------
# Find 6 outside circle centers
# --------------------------------
centers = []

for i in range(6):

    angle = 2 * np.pi * i / 6

    h = hc + R * np.cos(angle)
    k = kc + R * np.sin(angle)

    centers.append((h, k))


# --------------------------------
# Fill 6 outside circles
# --------------------------------
for i, (h, k) in enumerate(centers):

    x = h + R * np.cos(theta)
    y = k + R * np.sin(theta)

    ax.fill(
        x,
        y,
        color=outside_colors[i],
        alpha=0.65
    )


# --------------------------------
# Center circle - 2 colors
# --------------------------------

# Top half
top = Wedge(
    (hc, kc),
    R,
    0,
    180,
    facecolor=center_top_color,
    alpha=0.8
)

ax.add_patch(top)

# Bottom half
bottom = Wedge(
    (hc, kc),
    R,
    180,
    360,
    facecolor=center_bottom_color,
    alpha=0.8
)

ax.add_patch(bottom)


# --------------------------------
# Draw 7 circle outlines
# --------------------------------

# Center circle
x = hc + R * np.cos(theta)
y = kc + R * np.sin(theta)

ax.plot(
    x,
    y,
    color="black",
    linewidth=2
)

# 6 outside circles
for h, k in centers:

    x = h + R * np.cos(theta)
    y = k + R * np.sin(theta)

    ax.plot(
        x,
        y,
        color="black",
        linewidth=2
    )


# --------------------------------
# Formatting
# --------------------------------
ax.set_aspect("equal")

ax.set_xlim(-4.2, 4.2)
ax.set_ylim(-4.2, 4.2)

ax.set_facecolor("white")
fig.patch.set_facecolor("white")

ax.axis("off")

plt.show()