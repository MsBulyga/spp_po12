"""
Модуль для лабораторной работы №7.
"""

import tkinter as tk
from tkinter import messagebox
import math
import time
import os
from PIL import ImageGrab


class FractalApp:
    """Класс приложения для построения фрактала 'Дерево Пифагора'"""

    def __init__(self, root):
        self.root = root
        self.root.title("Задание 2")
        self.root.geometry("900x700")

        self.canvas = None
        self.info_label = None
        self._draw_job = None

        self.depth_var = tk.IntVar(value=9)
        self.angle_var = tk.IntVar(value=35)
        self.scale_var = tk.DoubleVar(value=0.75)

        self.setup_ui()
        self.root.after(100, self.draw_fractal)

    def setup_ui(self):
        """Настройка элементов пользовательского интерфейса"""
        control_frame = tk.Frame(
            self.root, width=250, bg="#f0f0f0", padx=15, pady=15
        )
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self.root, bg="#1e1e1e")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            control_frame, text="Настройки фрактала",
            font=("Arial", 12, "bold"), bg="#f0f0f0"
        ).pack(pady=(0, 15))

        tk.Label(
            control_frame, text="Глубина (Детализация):", bg="#f0f0f0"
        ).pack(anchor="w")

        tk.Scale(
            control_frame, from_=1, to=12, orient=tk.HORIZONTAL,
            variable=self.depth_var, command=self.request_redraw,
            bg="#f0f0f0", length=200
        ).pack(pady=(0, 15))

        tk.Label(
            control_frame, text="Угол ветвления (в градусах):", bg="#f0f0f0"
        ).pack(anchor="w")

        tk.Scale(
            control_frame, from_=10, to=90, orient=tk.HORIZONTAL,
            variable=self.angle_var, command=self.request_redraw,
            bg="#f0f0f0", length=200
        ).pack(pady=(0, 15))

        tk.Label(
            control_frame, text="Укорачивание веток:", bg="#f0f0f0"
        ).pack(anchor="w")

        tk.Scale(
            control_frame, from_=0.5, to=0.85, resolution=0.01,
            orient=tk.HORIZONTAL, variable=self.scale_var,
            command=self.request_redraw, bg="#f0f0f0", length=200
        ).pack(pady=(0, 20))

        btn_screenshot = tk.Button(
            control_frame, text="Скриншот",
            command=self.take_screenshot, bg="#add8e6", height=2
        )
        btn_screenshot.pack(fill=tk.X, pady=10)

        self.info_label = tk.Label(
            control_frame, text="Ожидание...", bg="#f0f0f0",
            fg="#555555", justify=tk.LEFT
        )
        self.info_label.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    def request_redraw(self, *_args):
        """Отложенный вызов перерисовки для плавности работы ползунков"""
        if self._draw_job is not None:
            self.root.after_cancel(self._draw_job)
        self._draw_job = self.root.after(100, self.draw_fractal)

    def get_color(self, current_depth):
        """Вычисление цвета (от коричневого ствола к зеленым листьям)"""
        max_depth = self.depth_var.get()
        if max_depth <= 1:
            return "#228b22"

        ratio = (max_depth - current_depth) / (max_depth - 1)
        r = int(139 + (34 - 139) * ratio)
        g = int(69 + (139 - 69) * ratio)
        b = int(19 + (34 - 19) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_tree(self, pos, angle, length, current_depth):
        """Рекурсивная функция отрисовки веток фрактала"""
        if current_depth == 0:
            return

        x, y = pos
        rad = math.radians(angle)
        x_new = x + length * math.cos(rad)
        y_new = y - length * math.sin(rad)

        width = max(1, int(current_depth * 1.2))
        color = self.get_color(current_depth)

        self.canvas.create_line(
            x, y, x_new, y_new,
            width=width, fill=color, capstyle=tk.ROUND
        )

        branch_angle = self.angle_var.get()
        scale = self.scale_var.get()

        self.draw_tree(
            (x_new, y_new), angle + branch_angle,
            length * scale, current_depth - 1
        )
        self.draw_tree(
            (x_new, y_new), angle - branch_angle,
            length * scale, current_depth - 1
        )

    def draw_fractal(self):
        """Подготовка холста и запуск алгоритма фрактала"""
        self._draw_job = None
        self.canvas.delete("all")

        depth = self.depth_var.get()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        start_pos = (width // 2, height - 20)
        start_length = 130
        start_angle = 90

        t_start = time.time()
        self.draw_tree(start_pos, start_angle, start_length, depth)
        t_end = time.time()

        lines_count = (2**depth) - 1
        stats_text = (
            f"Статистика генерации:\n"
            f"Отрисовано линий: {lines_count}\n"
            f"Время: {t_end - t_start:.3f} сек."
        )
        self.info_label.config(text=stats_text)

    def take_screenshot(self):
        """Создание скриншота активного окна"""
        x0 = self.root.winfo_rootx()
        y0 = self.root.winfo_rooty()
        x1 = x0 + self.root.winfo_width()
        y1 = y0 + self.root.winfo_height()

        try:
            img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
            filename = f"pythagoras_tree_{int(time.time())}.png"
            filepath = os.path.join(os.getcwd(), filename)
            img.save(filepath)
            messagebox.showinfo("Успех", f"Скриншот сохранен:\n{filepath}")
        except OSError as error:
            messagebox.showerror("Ошибка", f"Не удалось сделать скриншот.\n{error}")


def main():
    """Главная функция для запуска приложения"""
    root = tk.Tk()
    _app = FractalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
