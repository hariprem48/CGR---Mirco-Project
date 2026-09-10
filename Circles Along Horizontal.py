import matplotlib.pyplot as plt
import math

centers = [(0, 0), (4, 0), (8, 0)]
r = 2

for h, k in centers:
    x = [h + r * math.cos(i * 0.01) for i in range(629)]
    y = [k + r * math.sin(i * 0.01) for i in range(629)]
    plt.plot(x, y)

plt.xlabel("x")
plt.ylabel("y")
plt.title("Circles Along Horizontal Axis")
plt.grid()
plt.axis("equal")
plt.show()