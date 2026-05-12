"""
Лабораторная работа №7, задание 1.

Прямоугольник, вращающийся в плоскости формы вокруг одной из вершин.
"""

from __future__ import annotations

import math
import os
import time
import tkinter as tk
from tkinter import messagebox, ttk


class RotatingRectangle:
    """
    Прямоугольник в плоскости: одна вершина в начале координат, остальные по осям.

    Вращение задаётся углом (радианы) вокруг вершины (0, 0).
    """

    def __init__(self, width: float, height: float, angle_rad: float = 0.0) -> None:
        self.width = max(width, 1e-6)
        self.height = max(height, 1e-6)
        self.angle_rad = angle_rad

    def corners(self) -> tuple[tuple[float, float], ...]:
        """Возвращает четыре вершины после поворота: (0,0), (w,0), (w,h), (0,h)."""
        w, h = self.width, self.height
        base = ((0.0, 0.0), (w, 0.0), (w, h), (0.0, h))
        c = math.cos(self.angle_rad)
        s = math.sin(self.angle_rad)
        rotated = []
        for x, y in base:
            xr = x * c - y * s
            yr = x * s + y * c
            rotated.append((xr, yr))
        return tuple(rotated)

    def angle_degrees(self) -> float:
        """Текущий угол поворота в градусах."""
        return math.degrees(self.angle_rad)


class RotatingRectangleApp(tk.Tk):  # pylint: disable=too-many-instance-attributes
    """Окно: параметры на экране, анимация, пауза, скриншот в текущую директорию."""

    def __init__(self) -> None:
        super().__init__()
        self.title("ЛР7 — задание 1: вращающийся прямоугольник")
        self.geometry("720x560")

        self._rect = RotatingRectangle(120.0, 80.0, 0.0)
        self._anim_job: str | None = None
        self._paused = False

        ctrl = ttk.Frame(self, padding=8)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl, text="Ширина:").grid(row=0, column=0, sticky=tk.W)
        self._var_w = tk.StringVar(value="120")
        self._entry_w = ttk.Entry(ctrl, textvariable=self._var_w, width=8)
        self._entry_w.grid(row=0, column=1, padx=4)

        ttk.Label(ctrl, text="Высота:").grid(row=0, column=2, sticky=tk.W)
        self._var_h = tk.StringVar(value="80")
        self._entry_h = ttk.Entry(ctrl, textvariable=self._var_h, width=8)
        self._entry_h.grid(row=0, column=3, padx=4)

        ttk.Label(ctrl, text="Скорость (°/с):").grid(row=0, column=4, sticky=tk.W)
        self._var_speed = tk.StringVar(value="45")
        self._entry_speed = ttk.Entry(ctrl, textvariable=self._var_speed, width=8)
        self._entry_speed.grid(row=0, column=5, padx=4)

        ttk.Button(ctrl, text="Применить", command=self._apply_params).grid(
            row=0, column=6, padx=8
        )
        self._btn_pause = ttk.Button(ctrl, text="Пауза", command=self._toggle_pause)
        self._btn_pause.grid(row=0, column=7, padx=4)
        ttk.Button(ctrl, text="Скриншот", command=self._screenshot).grid(
            row=0, column=8, padx=4
        )

        self._canvas = tk.Canvas(self, bg="white", highlightthickness=1)
        self._canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.bind("<Configure>", self._on_resize)
        self._apply_params()
        self._schedule_frame()

    def _center(self) -> tuple[float, float]:
        self.update_idletasks()
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        return w / 2.0, h / 2.0

    def _parse_positive(self, raw: str, name: str) -> float:
        value = float(raw.replace(",", "."))
        if value <= 0:
            raise ValueError(f"{name} должно быть > 0")
        return value

    def _apply_params(self) -> None:
        try:
            w = self._parse_positive(self._var_w.get(), "Ширина")
            h = self._parse_positive(self._var_h.get(), "Высота")
            _ = float(self._var_speed.get().replace(",", "."))
        except ValueError as exc:
            messagebox.showerror("Параметры", str(exc))
            return
        self._rect.width = w
        self._rect.height = h
        self._draw()

    def _deg_per_sec(self) -> float:
        try:
            return float(self._var_speed.get().replace(",", "."))
        except ValueError:
            return 0.0

    def _on_resize(self, _event: object) -> None:
        self._draw()

    def _world_to_canvas(
        self, cx: float, cy: float, x: float, y: float
    ) -> tuple[float, float]:
        # Ось Y канваса направлена вниз — отражаем.
        return cx + x, cy - y

    def _draw(self) -> None:
        self._canvas.delete("all")
        cx, cy = self._center()
        corners = self._rect.corners()
        flat: list[float] = []
        for x, y in corners:
            px, py = self._world_to_canvas(cx, cy, x, y)
            flat.extend((px, py))
        self._canvas.create_polygon(
            *flat, outline="blue", fill="#cfe8ff", width=2, smooth=False
        )
        px0, py0 = self._world_to_canvas(cx, cy, 0.0, 0.0)
        r = 5
        self._canvas.create_oval(
            px0 - r, py0 - r, px0 + r, py0 + r, outline="red", fill="red"
        )

    def _toggle_pause(self) -> None:
        self._paused = not self._paused
        self._btn_pause.configure(text="Продолжить" if self._paused else "Пауза")
        if not self._paused:
            self._schedule_frame()

    def _cancel_anim(self) -> None:
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None

    def _schedule_frame(self) -> None:
        self._cancel_anim()
        if self._paused:
            return
        # Частота кадров фиксированная; «скорость» — градусы в секунду.
        interval_ms = 33
        self._anim_job = self.after(interval_ms, self._tick)

    def _tick(self) -> None:
        if self._paused:
            return
        dps = self._deg_per_sec()
        dt = 0.033
        self._rect.angle_rad += math.radians(dps * dt)
        self._draw()
        self._schedule_frame()

    def _screenshot(self) -> None:
        path = os.path.join(os.getcwd(), f"lab7_task1_{int(time.time() * 1000)}.eps")
        try:
            self._canvas.postscript(
                file=path, colormode="color", width=self._canvas.winfo_width()
            )
        except tk.TclError as exc:
            messagebox.showerror("Скриншот", str(exc))
            return
        messagebox.showinfo("Скриншот", f"Сохранено:\n{path}")


def main() -> None:
    """Запуск приложения."""
    app = RotatingRectangleApp()
    app.mainloop()


if __name__ == "__main__":
    main()
