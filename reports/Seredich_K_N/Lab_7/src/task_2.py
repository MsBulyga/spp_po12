"""
Лабораторная работа №7, задание 2.

Построение множества Жюлиа (итерация z -> z^2 + c).
"""

from __future__ import annotations

import math
import os
import tempfile
import time
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox, ttk


def _julia_escape_steps(z: complex, c: complex, max_iter: int, bound: float) -> int:
    """Число шагов до выхода за границу; max_iter если не вышло."""
    for n in range(max_iter):
        if abs(z) > bound:
            return n
        z = z * z + c
    return max_iter


@dataclass(frozen=True)
class JuliaView:  # pylint: disable=too-many-instance-attributes
    """Параметры окна отображения множества Жюлиа в комплексной плоскости."""

    width: int
    height: int
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    max_iter: int
    escape_bound: float


class JuliaSet:
    """
    Множество Жюлиа на прямоугольнике комплексной плоскости.

    Цвет по числу итераций до «убегания».
    """

    def __init__(self, c: complex, view: JuliaView) -> None:
        self.c = c
        self.view = view

    def escape_steps(self, z: complex) -> int:
        """Число итераций до выхода за границу для начальной точки z."""
        return _julia_escape_steps(
            z, self.c, self.view.max_iter, self.view.escape_bound
        )

    def _rgb_for_steps(self, steps: int) -> tuple[int, int, int]:
        if steps >= self.view.max_iter:
            return 0, 0, 0
        t = steps / max(self.view.max_iter, 1)
        r = int(255 * (0.5 + 0.5 * math.sin(6.28 * t)))
        g = int(255 * (0.5 + 0.5 * math.sin(6.28 * t + 2.1)))
        b = int(255 * (0.5 + 0.5 * math.sin(6.28 * t + 4.2)))
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

    def _scanline_rgb(self, row_index: int, width: int, dx: float, dy: float) -> bytes:
        """Один горизонтальный ряд пикселей (RGB)."""
        im = self.view.ymax - row_index * dy
        line = bytearray(width * 3)
        k = 0
        for i in range(width):
            re = self.view.xmin + i * dx
            steps = self.escape_steps(complex(re, im))
            r, g, b = self._rgb_for_steps(steps)
            line[k] = r
            line[k + 1] = g
            line[k + 2] = b
            k += 3
        return bytes(line)

    def ppm_bytes(self) -> bytes:
        """Сырые данные изображения P6 (PPM binary)."""
        w, h = self.view.width, self.view.height
        header = f"P6\n{w} {h}\n255\n".encode("ascii")
        dx = (self.view.xmax - self.view.xmin) / max(w - 1, 1)
        dy = (self.view.ymax - self.view.ymin) / max(h - 1, 1)
        body = bytearray()
        for j in range(h):
            body.extend(self._scanline_rgb(j, w, dx, dy))
        return header + bytes(body)


class JuliaApp(tk.Tk):  # pylint: disable=too-many-instance-attributes
    """Ввод параметров c и области; отображение PPM; сохранение в текущую директорию."""

    def __init__(self) -> None:
        super().__init__()
        self.title("ЛР7 — задание 2: множество Жюлиа")
        self.geometry("640x620")

        ctrl = ttk.Frame(self, padding=8)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl, text="Re(c):").grid(row=0, column=0, sticky=tk.W)
        self._var_re = tk.StringVar(value="-0.7269")
        ttk.Entry(ctrl, textvariable=self._var_re, width=10).grid(
            row=0, column=1, padx=4
        )

        ttk.Label(ctrl, text="Im(c):").grid(row=0, column=2, sticky=tk.W)
        self._var_im = tk.StringVar(value="0.1889")
        ttk.Entry(ctrl, textvariable=self._var_im, width=10).grid(
            row=0, column=3, padx=4
        )

        ttk.Label(ctrl, text="max_iter:").grid(row=1, column=0, sticky=tk.W)
        self._var_iter = tk.StringVar(value="80")
        ttk.Entry(ctrl, textvariable=self._var_iter, width=10).grid(
            row=1, column=1, padx=4
        )

        ttk.Label(ctrl, text="Масштаб (радиус):").grid(row=1, column=2, sticky=tk.W)
        self._var_radius = tk.StringVar(value="2.0")
        ttk.Entry(ctrl, textvariable=self._var_radius, width=10).grid(
            row=1, column=3, padx=4
        )

        ttk.Label(ctrl, text="Ширина:").grid(row=2, column=0, sticky=tk.W)
        self._var_w = tk.StringVar(value="400")
        ttk.Entry(ctrl, textvariable=self._var_w, width=10).grid(
            row=2, column=1, padx=4
        )

        ttk.Label(ctrl, text="Высота:").grid(row=2, column=2, sticky=tk.W)
        self._var_h = tk.StringVar(value="400")
        ttk.Entry(ctrl, textvariable=self._var_h, width=10).grid(
            row=2, column=3, padx=4
        )

        ttk.Button(ctrl, text="Построить", command=self._render).grid(
            row=0, column=4, rowspan=3, padx=12, ipadx=8, ipady=8
        )
        ttk.Button(ctrl, text="Сохранить PPM", command=self._save_ppm).grid(
            row=0, column=5, rowspan=3, padx=4, ipadx=6, ipady=8
        )

        self._label = ttk.Label(self)
        self._label.pack()

        self._photo: tk.PhotoImage | None = None
        self._last_ppm: bytes | None = None

    def _parse_int(self, raw: str, name: str, minimum: int = 1) -> int:
        value = int(float(raw.replace(",", ".")))
        if value < minimum:
            raise ValueError(f"{name} должно быть >= {minimum}")
        return value

    def _parse_float(self, raw: str, name: str) -> float:
        try:
            return float(raw.replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"{name}: неверное число") from exc

    def _build_julia(self) -> JuliaSet:
        re_c = self._parse_float(self._var_re.get(), "Re(c)")
        im_c = self._parse_float(self._var_im.get(), "Im(c)")
        max_iter = self._parse_int(self._var_iter.get(), "max_iter", 1)
        radius = self._parse_float(self._var_radius.get(), "Масштаб")
        if radius <= 0:
            raise ValueError("Масштаб должен быть > 0")
        w = self._parse_int(self._var_w.get(), "Ширина", 50)
        h = self._parse_int(self._var_h.get(), "Высота", 50)
        c = complex(re_c, im_c)
        view = JuliaView(
            width=w,
            height=h,
            xmin=-radius,
            xmax=radius,
            ymin=-radius,
            ymax=radius,
            max_iter=max_iter,
            escape_bound=2.0,
        )
        return JuliaSet(c, view)

    def _render(self) -> None:
        try:
            julia = self._build_julia()
        except ValueError as exc:
            messagebox.showerror("Параметры", str(exc))
            return
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            ppm = julia.ppm_bytes()
        finally:
            self.config(cursor="")
        self._last_ppm = ppm
        # PhotoImage(data=...) с PPM в base64 на Windows часто даёт TclError;
        # загрузка из временного файла поддерживается стабильнее.
        tmp_path = ""
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".ppm", prefix="lab7_julia_")
            with os.fdopen(fd, "wb") as tmp_file:
                tmp_file.write(ppm)
            self._photo = tk.PhotoImage(master=self, file=tmp_path)
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        self._label.configure(image=self._photo)

    def _save_ppm(self) -> None:
        if not self._last_ppm:
            messagebox.showinfo("Сохранение", "Сначала нажмите «Построить».")
            return
        path = os.path.join(os.getcwd(), f"lab7_task2_{int(time.time() * 1000)}.ppm")
        try:
            with open(path, "wb") as file:
                file.write(self._last_ppm)
        except OSError as exc:
            messagebox.showerror("Сохранение", str(exc))
            return
        messagebox.showinfo("Сохранение", f"Сохранено:\n{path}")


def main() -> None:
    """Запуск приложения."""
    app = JuliaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
