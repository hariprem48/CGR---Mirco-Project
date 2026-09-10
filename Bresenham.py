import numpy as np
import matplotlib.pyplot as plt


# Starting and ending points
x1, y1 = 1, 1
x2, y2 = 10, 6


# Bresenham's Line Drawing Algorithm
def bresenham_line(x1, y1, x2, y2):

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1

    x = x1
    y = y1

    points = []

    # Decision parameter
    p = 2 * dy - dx

    while True:

        points.append((x, y))

        # Stop when endpoint is reached
        if x == x2 and y == y2:
            break

        # Update decision parameter
        if p < 0:

            x = x + sx
            p = p + 2 * dy

        else:

            x = x + sx
            y = y + sy
            p = p + 2 * dy - 2 * dx

    return points


# Get Bresenham points
points = bresenham_line(x1, y1, x2, y2)


# Separate X and Y coordinates
x_points = [point[0] for point in points]
y_points = [point[1] for point in points]


# Plot the graph
plt.figure(figsize=(8, 6))


# Draw line and points
plt.plot(
    x_points,
    y_points,
    marker='s',
    linewidth=2,
    markersize=8,
    label="Bresenham Line"
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
plt.title(
    "Bresenham's Line Drawing Algorithm",
    fontsize=16
)

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