from canvas import initialize, move_it, register
import tkinter as tk

"""主函数，程序入口点"""
window = tk.Tk()  # 创建主窗口
canvas = initialize(window)  # 初始化画布
registry_actives, registry_passives, counter = register(
    canvas
)  # 注册模拟对象
moves = 0  # 初始化移动步数
# 开始模拟循环
move_it(canvas, registry_actives, registry_passives, counter, moves)
window.mainloop()  # 启动Tkinter事件循环
