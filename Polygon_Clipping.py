import numpy as np
import matplotlib.pyplot as plt


# Original polygon
polygon = [
    (20, 20),
    (80, 20),
    (90, 60),
    (50, 90),
    (10, 60)
]


# Clipping window
xmin, ymin = 30, 30
xmax, ymax = 70, 70


# --------------------------------------------------
# SUTHERLAND-HODGMAN POLYGON CLIPPING
# --------------------------------------------------

def inside(point, edge):

    x, y = point

    if edge == "left":
        return x >= xmin

    elif edge == "right":
        return x <= xmax

    elif edge == "bottom":
        return y >= ymin

    elif edge == "top":
        return y <= ymax


# Find intersection point
def intersection(p1, p2, edge):

    x1, y1 = p1
    x2, y2 = p2

    if edge == "left":

        x = xmin
        y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)

    elif edge == "right":

        x = xmax
        y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)

    elif edge == "bottom":

        y = ymin
        x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)

    elif edge == "top":

        y = ymax
        x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)

    return (x, y)


# Clip polygon against one boundary
def clip_polygon(polygon, edge):

    output = []

    if len(polygon) == 0:
        return output

    previous = polygon[-1]

    for current in polygon:

        current_inside = inside(current, edge)
        previous_inside = inside(previous, edge)

        # Case 1:
        # Current and previous points are inside
        if current_inside and previous_inside:

            output.append(current)

        # Case 2:
        # Current is inside, previous is outside
        elif current_inside and not previous_inside:

            output.append(
                intersection(previous, current, edge)
            )

            output.append(current)

        # Case 3:
        # Current is outside, previous is inside
        elif not current_inside and previous_inside:

            output.append(
                intersection(previous, current, edge)
            )

        # Case 4:
        # Both are outside
        # Nothing is added

        previous = current

    return output


# Apply clipping against all four boundaries
def sutherland_hodgman(polygon):

    edges = ["left", "right", "bottom", "top"]

    for edge in edges:

        polygon = clip_polygon(polygon, edge)

    return polygon


# Perform clipping
clipped_polygon = sutherland_hodgman(polygon)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 7))


# Draw clipping window
ax.plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'k-',
    linewidth=2,
    label="Clipping Window"
)


# Draw original polygon
original_x = [point[0] for point in polygon]
original_y = [point[1] for point in polygon]

original_x.append(original_x[0])
original_y.append(original_y[0])

ax.plot(
    original_x,
    original_y,
    'r--',
    linewidth=2,
    label="Original Polygon"
)


# Draw original polygon vertices
ax.scatter(
    original_x[:-1],
    original_y[:-1],
    color='red'
)


# Draw clipped polygon
if clipped_polygon:

    clipped_x = [point[0] for point in clipped_polygon]
    clipped_y = [point[1] for point in clipped_polygon]

    clipped_x.append(clipped_x[0])
    clipped_y.append(clipped_y[0])

    ax.plot(
        clipped_x,
        clipped_y,
        'b-',
        linewidth=3,
        label="Clipped Polygon"
    )

    ax.fill(
        clipped_x,
        clipped_y,
        alpha=0.3
    )

    # Clipped vertices
    ax.scatter(
        clipped_x[:-1],
        clipped_y[:-1],
        color='blue'
    )


# Graph settings
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

ax.set_xlabel("X")
ax.set_ylabel("Y")

ax.set_title("Sutherland-Hodgman Polygon Clipping")

ax.grid(True)
ax.legend()

plt.tight_layout()
plt.show()