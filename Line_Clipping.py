import numpy as np
import matplotlib.pyplot as plt


# Clipping window
xmin, ymin = 30, 30
xmax, ymax = 70, 70

# Original line
x1, y1 = 10, 20
x2, y2 = 90, 80


# --------------------------------------------------
# COHEN-SUTHERLAND LINE CLIPPING
# --------------------------------------------------

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


# Find region code
def compute_code(x, y):

    code = INSIDE

    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT

    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP

    return code


# Cohen-Sutherland algorithm
def cohen_sutherland(x1, y1, x2, y2):

    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)

    accept = False

    while True:

        # Both points are inside
        if code1 == 0 and code2 == 0:
            accept = True
            break

        # Line is completely outside
        elif (code1 & code2) != 0:
            break

        else:

            # Select the point outside
            if code1 != 0:
                code = code1
            else:
                code = code2

            # Find intersection
            if code & TOP:

                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax

            elif code & BOTTOM:

                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin

            elif code & RIGHT:

                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax

            elif code & LEFT:

                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            # Replace outside point
            if code == code1:

                x1, y1 = x, y
                code1 = compute_code(x1, y1)

            else:

                x2, y2 = x, y
                code2 = compute_code(x2, y2)

    if accept:
        return x1, y1, x2, y2

    return None


# --------------------------------------------------
# LIANG-BARSKY LINE CLIPPING
# --------------------------------------------------

def liang_barsky(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [
        x1 - xmin,
        xmax - x1,
        y1 - ymin,
        ymax - y1
    ]

    u1 = 0
    u2 = 1

    for i in range(4):

        if p[i] == 0:

            # Line is parallel to boundary
            if q[i] < 0:
                return None

        else:

            u = q[i] / p[i]

            if p[i] < 0:

                u1 = max(u1, u)

            else:

                u2 = min(u2, u)

    if u1 > u2:
        return None

    # Calculate clipped points
    cx1 = x1 + u1 * dx
    cy1 = y1 + u1 * dy

    cx2 = x1 + u2 * dx
    cy2 = y1 + u2 * dy

    return cx1, cy1, cx2, cy2


# Apply both algorithms
cohen_result = cohen_sutherland(x1, y1, x2, y2)
liang_result = liang_barsky(x1, y1, x2, y2)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

fig, ax = plt.subplots(1, 2, figsize=(12, 5))


# --------------------------------------------------
# COHEN-SUTHERLAND GRAPH
# --------------------------------------------------

ax[0].plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'k-',
    linewidth=2
)

# Original line
ax[0].plot(
    [x1, x2],
    [y1, y2],
    'r--',
    label="Original Line"
)

# Clipped line
if cohen_result:

    cx1, cy1, cx2, cy2 = cohen_result

    ax[0].plot(
        [cx1, cx2],
        [cy1, cy2],
        'b-',
        linewidth=3,
        label="Clipped Line"
    )

    ax[0].scatter(
        [cx1, cx2],
        [cy1, cy2],
        color='blue'
    )


ax[0].set_title("Cohen-Sutherland")
ax[0].set_xlabel("X")
ax[0].set_ylabel("Y")
ax[0].set_xlim(0, 100)
ax[0].set_ylim(0, 100)
ax[0].grid(True)
ax[0].legend()


# --------------------------------------------------
# LIANG-BARSKY GRAPH
# --------------------------------------------------

ax[1].plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'k-',
    linewidth=2
)

# Original line
ax[1].plot(
    [x1, x2],
    [y1, y2],
    'r--',
    label="Original Line"
)

# Clipped line
if liang_result:

    cx1, cy1, cx2, cy2 = liang_result

    ax[1].plot(
        [cx1, cx2],
        [cy1, cy2],
        'b-',
        linewidth=3,
        label="Clipped Line"
    )

    ax[1].scatter(
        [cx1, cx2],
        [cy1, cy2],
        color='blue'
    )


ax[1].set_title("Liang-Barsky")
ax[1].set_xlabel("X")
ax[1].set_ylabel("Y")
ax[1].set_xlim(0, 100)
ax[1].set_ylim(0, 100)
ax[1].grid(True)
ax[1].legend()


plt.tight_layout()
plt.show()