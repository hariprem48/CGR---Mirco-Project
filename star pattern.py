import matplotlib.pyplot as plt

x = range(-10, 11)

# y = x
y1 = [i for i in x]

# y = -x
y2 = [-i for i in x]

# y = 0
y3 = [0 for i in x]

# x = 0 (vertical line)
y4 = range(-10, 11)

plt.plot(x, y1, label="y = x")
plt.plot(x, y2, label="y = -x")
plt.plot(x, y3, label="y = 0")
plt.plot([0, 0], [-10, 10], label="x = 0")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Star Pattern of Lines")

plt.legend()
plt.grid()
plt.show()