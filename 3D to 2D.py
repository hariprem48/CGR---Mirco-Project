import numpy as np
import matplotlib.pyplot as plt

# Distance of projection plane
d = 5

# 3D cube vertices
points_3d = np.array([
    [1, 1, 1, 1],
    [3, 1, 1, 1],
    [3, 3, 1, 1],
    [1, 3, 1, 1],

    [1, 1, 3, 1],
    [3, 1, 3, 1],
    [3, 3, 3, 1],
    [1, 3, 3, 1]
], dtype=float)

# Cube edges
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Perspective projection matrix
P = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 1/d, 0]
])

# Matrix multiplication
projected = points_3d @ P.T

# Perspective division
points_2d = projected[:, :2] / projected[:, 3, np.newaxis]

# Create figure
fig = plt.figure(figsize=(12, 6))

# ---------------- 3D OBJECT ----------------
ax1 = fig.add_subplot(121, projection='3d')

for a, b in edges:
    ax1.plot(
        [points_3d[a, 0], points_3d[b, 0]],
        [points_3d[a, 1], points_3d[b, 1]],
        [points_3d[a, 2], points_3d[b, 2]]
    )

ax1.scatter(
    points_3d[:, 0],
    points_3d[:, 1],
    points_3d[:, 2]
)

ax1.set_title("Original 3D Object")
ax1.set_xlabel("X")
ax1.set_ylabel("Y")
ax1.set_zlabel("Z")

# ---------------- 2D OBJECT ----------------
ax2 = fig.add_subplot(122)

for a, b in edges:
    ax2.plot(
        [points_2d[a, 0], points_2d[b, 0]],
        [points_2d[a, 1], points_2d[b, 1]]
    )

ax2.scatter(
    points_2d[:, 0],
    points_2d[:, 1]
)

ax2.set_title("2D Perspective Projection")
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.grid()
ax2.axis("equal")

plt.tight_layout()
plt.show()