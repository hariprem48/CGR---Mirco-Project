import numpy as np
import matplotlib.pyplot as plt


# Starting and ending points
x1, y1 = 1, 1
x2, y2 = 10, 6


# DDA Algorithm
def dda_line(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    # Calculate number of steps
    steps = max(abs(dx), abs(dy))

    # Calculate increments
    x_increment = dx / steps
    y_increment = dy / steps

    # Starting point
    x = x1
    y = y1

    points = []

    # Generate points
    for i in range(steps + 1):

        points.append((round(x), round(y)))

        x = x + x_increment
        y = y + y_increment

    return points


# Get DDA points
points = dda_line(x1, y1, x2, y2)


# Separate X and Y coordinates
x_points = [point[0] for point in points]
y_points = [point[1] for point in points]


# Plot the graph
plt.figure(figsize=(8, 6))

# Draw line
plt.plot(
    x_points,
    y_points,
    marker='s',
    linewidth=2,
    markersize=8,
    label="DDA Line"
)


# Label each point
for x, y in points:

    plt.text(
        x + 0.1,
        y + 0.1,
        f"({x},{y})",
        fontsize=9
    )


# Graph settings
plt.title("DDA Line Drawing Algorithm", fontsize=16)

plt.xlabel("X")
plt.ylabel("Y")

plt.xlim(0, 11)
plt.ylim(0, 7)

plt.xticks(np.arange(0, 12, 1))
plt.yticks(np.arange(0, 8, 1))

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.show()