from canvas import initialize, move_it, register
import tkinter as tk

window = tk.Tk()  # Create the main window
canvas = initialize(window)  # Initialize the canvas
registry_actives, registry_passives, counter = register(canvas)  # Register simulation objects
moves = 0  # Initialize move count
move_it(canvas, registry_actives, registry_passives, counter, moves)  # Start the simulation loop
window.mainloop()  # Start the Tkinter event loop

