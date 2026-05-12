"""Interactive visualization for points and a line."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
import os
import random
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


@dataclass(slots=True)
class Point:
    """Point on the plane."""

    x: float
    y: float

    def distance_to_line(self, line: "Line") -> float:
        """Return distance from the point to the line."""
        numerator = abs(line.a * self.x + line.b * self.y + line.c)
        denominator = math.sqrt(line.a**2 + line.b**2)
        return numerator / denominator


@dataclass(slots=True)
class Line:
    """Line in the form ax + by + c = 0."""

    a: float
    b: float
    c: float

    def y_from_x(self, x_value: float) -> float | None:
        """Return y for a given x when possible."""
        if self.b == 0:
            return None
        return -(self.a * x_value + self.c) / self.b

    def x_constant(self) -> float | None:
        """Return x for a vertical line when possible."""
        if self.b != 0 or self.a == 0:
            return None
        return -self.c / self.a


class GeometryApp:  # pylint: disable=too-many-instance-attributes
    """Tkinter application for point-line visualization."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("СПП ЛР7 - Point и Line")
        self.root.geometry("1180x760")

        self.count_var = tk.IntVar(value=12)
        self.speed_var = tk.IntVar(value=300)
        self.a_var = tk.DoubleVar(value=1.0)
        self.b_var = tk.DoubleVar(value=-1.0)
        self.c_var = tk.DoubleVar(value=0.0)
        self.range_var = tk.DoubleVar(value=10.0)
        self.seed_var = tk.IntVar(value=14)
        self.status_var = tk.StringVar(
            value="Задайте параметры и нажмите «Построить»."
        )

        self.points: list[Point] = []
        self.line = Line(1.0, -1.0, 0.0)
        self.current_index = 0
        self.best_index: int | None = None
        self.best_distance = -1.0
        self.animation_job: str | None = None
        self.is_paused = False

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        self._build_layout()
        self._draw_scene()

    def _build_layout(self) -> None:
        control_frame = ttk.Frame(self.root, padding=12)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_frame, text="Количество точек").pack(anchor="w")
        ttk.Spinbox(
            control_frame,
            from_=1,
            to=200,
            textvariable=self.count_var,
            width=12,
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(control_frame, text="Коэффициент a").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.a_var, width=14).pack(
            anchor="w", pady=(0, 8)
        )
        ttk.Label(control_frame, text="Коэффициент b").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.b_var, width=14).pack(
            anchor="w", pady=(0, 8)
        )
        ttk.Label(control_frame, text="Коэффициент c").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.c_var, width=14).pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Label(control_frame, text="Диапазон координат").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.range_var, width=14).pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Label(control_frame, text="Зерно генератора").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.seed_var, width=14).pack(
            anchor="w", pady=(0, 12)
        )

        ttk.Label(control_frame, text="Скорость (мс)").pack(anchor="w")
        ttk.Scale(
            control_frame,
            from_=50,
            to=1200,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=220,
        ).pack(anchor="w", pady=(0, 10))
        ttk.Label(control_frame, textvariable=self.speed_var).pack(anchor="w")

        ttk.Button(control_frame, text="Построить", command=self.start_animation).pack(
            fill=tk.X, pady=(16, 4)
        )
        ttk.Button(control_frame, text="Пауза / продолжить", command=self.toggle_pause).pack(
            fill=tk.X, pady=4
        )
        ttk.Button(control_frame, text="Изменить параметры", command=self.apply_live_changes).pack(
            fill=tk.X, pady=4
        )
        ttk.Button(control_frame, text="Скриншот", command=self.save_screenshot).pack(
            fill=tk.X, pady=4
        )

        ttk.Label(
            control_frame,
            textvariable=self.status_var,
            wraplength=240,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(16, 0))

        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def generate_data(self) -> None:
        """Generate random points and reset animation state."""
        point_range = float(self.range_var.get())
        if point_range <= 0:
            raise ValueError("Диапазон координат должен быть больше нуля")

        point_count = int(self.count_var.get())
        if point_count <= 0:
            raise ValueError("Количество точек должно быть больше нуля")

        line = Line(
            float(self.a_var.get()),
            float(self.b_var.get()),
            float(self.c_var.get()),
        )
        if line.a == 0 and line.b == 0:
            raise ValueError("Коэффициенты a и b не могут одновременно быть нулём")

        random.seed(int(self.seed_var.get()))
        self.points = [
            Point(
                x=random.uniform(-point_range, point_range),
                y=random.uniform(-point_range, point_range),
            )
            for _ in range(point_count)
        ]
        self.line = line
        self.current_index = 0
        self.best_index = None
        self.best_distance = -1.0
        self.is_paused = False

    def start_animation(self) -> None:
        """Start visualization from scratch."""
        self._cancel_animation()
        try:
            self.generate_data()
        except ValueError as error:
            messagebox.showerror("Ошибка параметров", str(error))
            return

        self.status_var.set(
            "Анимация запущена. Проверяем точки и ищем самую удалённую от прямой."
        )
        self._draw_scene()
        self._animate_step()

    def _animate_step(self) -> None:
        """Process next point in the animation."""
        if self.is_paused:
            return

        if self.current_index >= len(self.points):
            if self.best_index is not None:
                best_point = self.points[self.best_index]
                self.status_var.set(
                    "Готово. Самая удалённая точка: "
                    f"({best_point.x:.2f}; {best_point.y:.2f}), "
                    f"расстояние = {self.best_distance:.3f}"
                )
            self._draw_scene()
            self.animation_job = None
            return

        current_point = self.points[self.current_index]
        current_distance = current_point.distance_to_line(self.line)
        if current_distance > self.best_distance:
            self.best_distance = current_distance
            self.best_index = self.current_index

        self.status_var.set(
            f"Проверка точки {self.current_index + 1}/{len(self.points)}. "
            f"Текущее расстояние = {current_distance:.3f}"
        )
        self._draw_scene()
        self.current_index += 1
        self.animation_job = self.root.after(int(self.speed_var.get()), self._animate_step)

    def toggle_pause(self) -> None:
        """Pause or resume animation."""
        if not self.points:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.status_var.set("Анимация приостановлена.")
            self._cancel_animation()
        else:
            self.status_var.set("Анимация продолжена.")
            self._animate_step()

    def apply_live_changes(self) -> None:
        """Apply current parameters without restarting the whole app."""
        was_running = bool(self.animation_job) or self.is_paused
        self._cancel_animation()
        try:
            self.generate_data()
        except ValueError as error:
            messagebox.showerror("Ошибка параметров", str(error))
            return

        self.status_var.set("Параметры обновлены на лету.")
        self._draw_scene()
        if was_running:
            self._animate_step()

    def save_screenshot(self) -> None:
        """Save current figure to the active working directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"geometry_scene_{timestamp}.png",
        )
        self.figure.savefig(output_path, dpi=180)
        self.status_var.set(f"Скриншот сохранён: {output_path}")

    def _draw_scene(self) -> None:
        """Render current points and line."""
        self.axis.clear()
        self.axis.set_title("Точки и прямая")
        self.axis.set_xlabel("X")
        self.axis.set_ylabel("Y")
        self.axis.grid(True, linestyle="--", alpha=0.4)

        if self.points:
            x_values = [point.x for point in self.points]
            y_values = [point.y for point in self.points]
            self.axis.scatter(x_values, y_values, color="#2b6cb0", label="Точки")

            if self.current_index > 0 and self.current_index - 1 < len(self.points):
                current = self.points[self.current_index - 1]
                self.axis.scatter(
                    [current.x],
                    [current.y],
                    color="#dd6b20",
                    s=140,
                    label="Текущая точка",
                )

            if self.best_index is not None:
                best = self.points[self.best_index]
                self.axis.scatter(
                    [best.x],
                    [best.y],
                    color="#c53030",
                    s=180,
                    label="Самая удалённая точка",
                )

        point_range = max(float(self.range_var.get()), 1.0)
        x_min, x_max = -point_range, point_range

        vertical_x = self.line.x_constant()
        if vertical_x is not None:
            self.axis.axvline(vertical_x, color="#1a202c", linewidth=2, label="Прямая")
        else:
            line_y1 = self.line.y_from_x(x_min)
            line_y2 = self.line.y_from_x(x_max)
            if line_y1 is not None and line_y2 is not None:
                self.axis.plot(
                    [x_min, x_max],
                    [line_y1, line_y2],
                    color="#1a202c",
                    linewidth=2,
                    label="Прямая",
                )

        self.axis.set_xlim(x_min - 1, x_max + 1)
        self.axis.set_ylim(x_min - 1, x_max + 1)
        self.axis.legend(loc="upper right")
        self.canvas.draw_idle()

    def _cancel_animation(self) -> None:
        """Cancel pending Tkinter callback."""
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def run(self) -> None:
        """Run the Tkinter main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    GeometryApp().run()
