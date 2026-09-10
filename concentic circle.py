import matplotlib.pyplot as plt

x = range(-7, 8)

r_values = [2, 4, 6]

for r in r_values:
    y1 = [(r**2 - i**2)**0.5 for i in x if abs(i) <= r]
    x1 = [i for i in x if abs(i) <= r]
    y2 = [-y for y in y1]

    plt.plot(x1, y1, label=f"r = {r}")
    plt.plot(x1, y2)

plt.xlabel("x")
plt.ylabel("y")
plt.title("Concentric Circles")
plt.legend()
plt.grid()
plt.axis("equal")
plt.show()
