import numpy as np
import matplotlib.pyplot as plt

# Polygon vertices
polygon = [(20, 20), (70, 20), (80, 60), (50, 80), (20, 60)]

WIDTH = 100
HEIGHT = 100


# Flood Fill
def flood_fill(img, x, y, old, new):
    if old == new:
        return

    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue

        if img[y, x] != old:
            continue

        img[y, x] = new

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))


# Create polygon boundary
img1 = np.zeros((HEIGHT, WIDTH), dtype=int)

# Draw boundary
for i in range(len(polygon)):
    x1, y1 = polygon[i]
    x2, y2 = polygon[(i + 1) % len(polygon)]

    steps = max(abs(x2 - x1), abs(y2 - y1))

    for j in range(steps + 1):
        x = int(x1 + (x2 - x1) * j / steps)
        y = int(y1 + (y2 - y1) * j / steps)
        img1[y, x] = 1

# Flood fill from inside
flood_fill(img1, 50, 40, 0, 2)


# Scan-Line Fill
img2 = np.zeros((HEIGHT, WIDTH), dtype=int)

for y in range(HEIGHT):
    intersections = []

    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]

        if y1 != y2 and min(y1, y2) <= y < max(y1, y2):
            x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            intersections.append(int(x))

    intersections.sort()

    for i in range(0, len(intersections), 2):
        if i + 1 < len(intersections):
            img2[y, intersections[i]:intersections[i + 1] + 1] = 1


# Display results
fig, ax = plt.subplots(1, 2, figsize=(10, 5))

ax[0].imshow(img1, origin="lower")
ax[0].set_title("Flood Fill")
ax[0].set_xlabel("X")
ax[0].set_ylabel("Y")

ax[1].imshow(img2, origin="lower")
ax[1].set_title("Scan-Line Fill")
ax[1].set_xlabel("X")
ax[1].set_ylabel("Y")

plt.tight_layout()
plt.show()