import tkinter as tk

# Create window
window = tk.Tk()
window.title("Addition of Two Numbers - Flowchart")
window.geometry("600x700")

canvas = tk.Canvas(window, width=600, height=700, bg="white")
canvas.pack()

# Function to draw arrow
def arrow(x1, y1, x2, y2):
    canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2)

# START - Oval
canvas.create_oval(220, 30, 380, 90, outline="black", width=2)
canvas.create_text(300, 60, text="START", font=("Arial", 14, "bold"))

# Arrow
arrow(300, 90, 300, 130)

# INPUT - Parallelogram
points = [
    190, 130,
    410, 130,
    380, 190,
    160, 190
]
canvas.create_polygon(points, outline="black", fill="white", width=2)
canvas.create_text(285, 160, text="Input A and B", font=("Arial", 13))

# Arrow
arrow(300, 190, 300, 230)

# PROCESS - Rectangle
canvas.create_rectangle(180, 230, 420, 290, outline="black", width=2)
canvas.create_text(300, 260, text="Sum = A + B", font=("Arial", 13))

# Arrow
arrow(300, 290, 300, 330)

# OUTPUT - Parallelogram
points = [
    190, 330,
    410, 330,
    380, 390,
    160, 390
]
canvas.create_polygon(points, outline="black", fill="white", width=2)
canvas.create_text(285, 360, text="Display Sum", font=("Arial", 13))

# Arrow
arrow(300, 390, 300, 430)

# STOP - Oval
canvas.create_oval(220, 430, 380, 490, outline="black", width=2)
canvas.create_text(300, 460, text="STOP", font=("Arial", 14, "bold"))

# Run window
window.mainloop()