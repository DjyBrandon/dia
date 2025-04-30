from canvas import initialize, move_it, register
import tkinter as tk
import time  # 新增时间模块


start_time = time.time()

window = tk.Tk()  # Create the main window
canvas = initialize(window)  # Initialize the canvas
registry_actives, registry_passives, counter = register(canvas)  # Register simulation objects
moves = 0  # Initialize move count
move_it(canvas, registry_actives, registry_passives, counter, moves)  # Start the simulation loop
window.mainloop()  # Start the Tkinter event loop

end_time = time.time()
duration = end_time - start_time
print(f"总运行时间: {duration:.2f}秒")
