"""
Графические примитивы и фракталы.
Задание 1: Вращающийся четырехугольник
Задание 2: Треугольник Серпинского
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dataclasses import dataclass
import math


@dataclass
class QuadConfig:
    """Конфигурация для четырехугольника."""
    width: int
    height: int


@dataclass
class SierpConfig:
    """Конфигурация для треугольника Серпинского."""
    p1: tuple
    p2: tuple
    p3: tuple
    depth: int


class RotatingQuadrilateral:
    """Класс для отображения вращающегося четырехугольника."""

    def __init__(self, canvas, center, config, angle=0):
        self.canvas = canvas
        self.center = center
        self.config = config
        self.angle = angle
        self.polygon_id = None
        self.color = "#3498db"

    def get_vertices(self):
        """Вычислить координаты вершин."""
        hw = self.config.width / 2
        hh = self.config.height / 2
        vertices = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rotated = []
        for x, y in vertices:
            new_x = self.center[0] + x * cos_a - y * sin_a
            new_y = self.center[1] + x * sin_a + y * cos_a
            rotated.append((new_x, new_y))
        return rotated

    def draw(self):
        """Отобразить четырехугольник."""
        if self.polygon_id:
            self.canvas.delete(self.polygon_id)
        vertices = self.get_vertices()
        flat_vertices = [coord for vertex in vertices for coord in vertex]
        self.polygon_id = self.canvas.create_polygon(
            flat_vertices, fill=self.color, outline="black", width=2
        )

    def update_angle(self, delta_angle):
        """Обновить угол поворота."""
        self.angle = (self.angle + delta_angle) % 360
        self.draw()


class SierpinskiTriangle:
    """Класс для отображения треугольника Серпинского."""

    def __init__(self, canvas, config, color_map=None):
        self.canvas = canvas
        self.config = config
        self.color_map = color_map if color_map is not None else self._default_colors()
        self.triangle_ids = []

    def _default_colors(self):
        """Вернуть цвета по умолчанию."""
        return ["#2ecc71", "#27ae60", "#1e8449", "#145a32", "#0b5345", "#082032"]

    def draw(self):
        """Отобразить фрактал."""
        for tid in self.triangle_ids:
            self.canvas.delete(tid)
        self.triangle_ids = []
        self._draw_triangle(
            self.config.p1, self.config.p2, self.config.p3, self.config.depth
        )

    def get_triangle_count(self):
        """Вернуть количество треугольников в фрактале."""
        return 3 ** self.config.depth

    def _draw_triangle(self, p1, p2, p3, depth):
        """Рекурсивно построить треугольник."""
        if depth == 0:
            color = self.color_map[0]
            points = list(p1) + list(p2) + list(p3)
            tid = self.canvas.create_polygon(points, fill=color, outline="black")
            self.triangle_ids.append(tid)
        else:
            m12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            m23 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
            m31 = ((p3[0] + p1[0]) / 2, (p3[1] + p1[1]) / 2)

            self._draw_triangle(p1, m12, m31, depth - 1)
            self._draw_triangle(m12, p2, m23, depth - 1)
            self._draw_triangle(m31, m23, p3, depth - 1)


class GraphicsApp:
    """Основное приложение с графическими примитивами и фракталами."""

    def __init__(self, root):
        self.root = root
        self.root.title("Графические примитивы и фракталы")
        self.root.geometry("900x700")

        self.paused = False
        self.animation_running = False
        self.quad = None
        self.sierpinski = None
        self.ui_elements = {}

        self.setup_ui()

    def setup_ui(self):
        """Настроить пользовательский интерфейс."""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.ui_elements["tabs"] = {}
        self.ui_elements["tabs"]["quad"] = ttk.Frame(notebook)
        self.ui_elements["tabs"]["sierp"] = ttk.Frame(notebook)
        notebook.add(self.ui_elements["tabs"]["quad"], text="Четырехугольник")
        notebook.add(self.ui_elements["tabs"]["sierp"], text="Треугольник Серпинского")

        self.setup_quad_tab()
        self.setup_sierpinski_tab()
        self.setup_control_buttons(control_frame)

    def setup_quad_tab(self):
        """Настроить вкладку четырехугольника."""
        parent = self.ui_elements["tabs"]["quad"]
        input_frame = ttk.LabelFrame(parent, text="Параметры четырехугольника")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="Ширина:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.ui_elements["controls"] = {}
        self.ui_elements["controls"]["quad_width"] = ttk.Spinbox(
            input_frame, from_=50, to=300, width=10
        )
        self.ui_elements["controls"]["quad_width"].set(150)
        self.ui_elements["controls"]["quad_width"].grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Высота:").grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.W
        )
        self.ui_elements["controls"]["quad_height"] = ttk.Spinbox(
            input_frame, from_=50, to=300, width=10
        )
        self.ui_elements["controls"]["quad_height"].set(100)
        self.ui_elements["controls"]["quad_height"].grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Скорость (град/кадр):").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.ui_elements["controls"]["quad_speed"] = ttk.Spinbox(
            input_frame, from_=1, to=20, width=10
        )
        self.ui_elements["controls"]["quad_speed"].set(3)
        self.ui_elements["controls"]["quad_speed"].grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Создать", command=self.create_quad).grid(
            row=1, column=2, columnspan=2, padx=5, pady=5
        )

        self.ui_elements["canvases"] = {}
        self.ui_elements["canvases"]["quad"] = tk.Canvas(
            parent, bg="white", width=600, height=500
        )
        self.ui_elements["canvases"]["quad"].pack(padx=5, pady=5)

    def setup_sierpinski_tab(self):
        """Настроить вкладку фрактала."""
        parent = self.ui_elements["tabs"]["sierp"]
        input_frame = ttk.LabelFrame(parent, text="Параметры фрактала")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="Глубина рекурсии:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.ui_elements["controls"]["sierp_depth"] = ttk.Spinbox(
            input_frame, from_=1, to=7, width=10
        )
        self.ui_elements["controls"]["sierp_depth"].set(5)
        self.ui_elements["controls"]["sierp_depth"].grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Размер:").grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.W
        )
        self.ui_elements["controls"]["sierp_size"] = ttk.Spinbox(
            input_frame, from_=200, to=500, width=10
        )
        self.ui_elements["controls"]["sierp_size"].set(400)
        self.ui_elements["controls"]["sierp_size"].grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(input_frame, text="Построить", command=self.create_sierpinski).grid(
            row=0, column=4, padx=5, pady=5
        )

        self.ui_elements["canvases"]["sierp"] = tk.Canvas(
            parent, bg="white", width=600, height=500
        )
        self.ui_elements["canvases"]["sierp"].pack(padx=5, pady=5)

    def setup_control_buttons(self, frame):
        """Настроить кнопки управления."""
        ttk.Button(frame, text="Пауза/Продолжить", command=self.toggle_pause).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(frame, text="Скриншот", command=self.take_screenshot).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(frame, text="Выход", command=self.root.quit).pack(
            side=tk.RIGHT, padx=5
        )

    def get_quad_config(self):
        """Получить конфигурацию четырехугольника."""
        width = int(self.ui_elements["controls"]["quad_width"].get())
        height = int(self.ui_elements["controls"]["quad_height"].get())
        return QuadConfig(width, height)

    def get_sierpinski_config(self):
        """Получить конфигурацию фрактала."""
        size = int(self.ui_elements["controls"]["sierp_size"].get())
        depth = int(self.ui_elements["controls"]["sierp_depth"].get())
        p1 = (300, 50)
        p2 = (300 - size / 2, 50 + size * math.sqrt(3) / 2)
        p3 = (300 + size / 2, 50 + size * math.sqrt(3) / 2)
        return SierpConfig(p1, p2, p3, depth)

    def create_quad(self):
        """Создать четырехугольник."""
        config = self.get_quad_config()

        canvas = self.ui_elements["canvases"]["quad"]
        canvas.delete("all")
        self.quad = RotatingQuadrilateral(canvas, (300, 250), config)
        self.quad.draw()

        if not self.animation_running:
            self.animation_running = True
            self.animate_quad()

    def animate_quad(self):
        """Анимировать вращение."""
        if self.animation_running and self.quad:
            if not self.paused:
                speed = int(self.ui_elements["controls"]["quad_speed"].get())
                self.quad.update_angle(speed)
            self.root.after(30, self.animate_quad)

    def create_sierpinski(self):
        """Создать фрактал."""
        config = self.get_sierpinski_config()

        canvas = self.ui_elements["canvases"]["sierp"]
        canvas.delete("all")
        self.sierpinski = SierpinskiTriangle(canvas, config)
        self.sierpinski.draw()

    def toggle_pause(self):
        """Переключить паузу."""
        self.paused = not self.paused

    def take_screenshot(self):
        """Сохранить скриншот."""
        try:
            notebook = self.root.nametowidget(self.root.winfo_children()[1])
            current_tab = notebook.index(notebook.select())

            canvas = self.ui_elements["canvases"]["quad"] if current_tab == 0 else \
                     self.ui_elements["canvases"]["sierp"]

            file_path = filedialog.asksaveasfilename(
                defaultextension=".eps",
                filetypes=[("EPS files", "*.eps"), ("All files", "*.*")],
            )

            if file_path:
                canvas.postscript(
                    file=file_path,
                    colormode="color",
                    width=canvas.winfo_width(),
                    height=canvas.winfo_height(),
                )
                messagebox.showinfo("Скриншот", f"Сохранено: {file_path}")
        except OSError as err:
            messagebox.showerror("Ошибка", str(err))
        except tk.TclError as err:
            messagebox.showerror("Ошибка", str(err))


def main():
    """Запустить приложение."""
    root = tk.Tk()
    GraphicsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
