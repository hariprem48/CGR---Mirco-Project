import matplotlib.pyplot as plt

x = range(-10, 11)

m_values = [-8, -6, -4, 0, 4, 6, 8]

for m in m_values:
    y = [m * i for i in x]
    plt.plot(x, y, label=f"m = {m}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Fan Pattern of Lines: y = mx")

plt.legend()
plt.grid()
plt.show()