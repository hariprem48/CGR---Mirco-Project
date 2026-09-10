import matplotlib.pyplot as plt

centers = [(0, 0), (0, 4), (0, 8)]
r = 2

for h, k in centers:
    x = [h + r * __import__("math").cos(t) for t in [i * 0.01 for i in range(629)]]
    y = [k + r * __import__("math").sin(t) for t in [i * 0.01 for i in range(629)]]
    plt.plot(x, y)

plt.xlabel("x")
plt.ylabel("y")
plt.title("Circles Along Vertical Axis")
plt.grid()
plt.axis("equal")
plt.show()