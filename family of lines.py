import matplotlib.pyplot as plt

x = range(-10, 11)

m_values = [-8, -4, 0, 4, 8]

for m in m_values:
    y = [m*i + 1 for i in x]
    plt.plot(x, y, label=f"m = {m}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Family of Lines: y = mx + 1")

plt.legend()
plt.grid()
plt.show()