import tkinter as tk

# Create window
window = tk.Tk()
window.title("Geometric Primitives")
window.geometry("800x600")

# Create canvas
canvas = tk.Canvas(window, width=800, height=600, bg="white")
canvas.pack()

# 1. Line
canvas.create_line(50, 50, 250, 50, fill="red", width=5)

# 2. Circle
canvas.create_oval(300, 30, 400, 130, fill="blue", outline="black", width=2)

# 3. Rectangle
canvas.create_rectangle(50, 150, 250, 280, fill="green", outline="black", width=2)

# 4. Ellipse
canvas.create_oval(300, 160, 500, 280, fill="yellow", outline="black", width=2)

# 5. Polygon (triangle)
canvas.create_polygon(
    600, 150,
    550, 280,
    700, 280,
    fill="purple",
    outline="black",
    width=2
)

# 6. Polygon (pentagon)
canvas.create_polygon(
    600, 350,
    680, 410,
    650, 510,
    550, 510,
    520, 410,
    fill="orange",
    outline="black",
    width=2
)

# Run window
window.mainloop()