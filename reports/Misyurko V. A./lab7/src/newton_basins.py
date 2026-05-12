"""Interactive Newton basins fractal viewer."""

from __future__ import annotations

from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class NewtonBasinsApp:  # pylint: disable=too-many-instance-attributes
    """Tkinter app for interactive Newton basins visualization."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("СПП ЛР7 - Бассейны Ньютона")
        self.root.geometry("1260x820")

        self.degree_var = tk.IntVar(value=3)
        self.resolution_var = tk.IntVar(value=360)
        self.iterations_var = tk.IntVar(value=35)
        self.speed_var = tk.IntVar(value=5)
        self.tolerance_var = tk.DoubleVar(value=0.0001)
        self.range_var = tk.DoubleVar(value=1.8)
        self.status_var = tk.StringVar(
            value="Настройте параметры и нажмите «Построить фрактал»."
        )

        self.figure = Figure(figsize=(8.6, 7), dpi=100)
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        self.image = None
        self.current_row = 0
        self.total_rows = 0
        self.is_paused = False
        self.render_job: str | None = None

        self.grid_real: np.ndarray | None = None
        self.grid_imag: np.ndarray | None = None
        self.result: np.ndarray | None = None
        self.roots: np.ndarray | None = None

        self._build_layout()
        self._init_blank_scene()

    def _build_layout(self) -> None:
        control_frame = ttk.Frame(self.root, padding=12)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_frame, text="Степень z^n - 1").pack(anchor="w")
        ttk.Spinbox(
            control_frame, from_=2, to=8, textvariable=self.degree_var, width=12
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(control_frame, text="Разрешение").pack(anchor="w")
        ttk.Spinbox(
            control_frame,
            from_=100,
            to=900,
            increment=20,
            textvariable=self.resolution_var,
            width=12,
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(control_frame, text="Итерации Ньютона").pack(anchor="w")
        ttk.Spinbox(
            control_frame,
            from_=5,
            to=100,
            textvariable=self.iterations_var,
            width=12,
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(control_frame, text="Точность").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.tolerance_var, width=14).pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Label(control_frame, text="Диапазон по осям").pack(anchor="w")
        ttk.Entry(control_frame, textvariable=self.range_var, width=14).pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Label(control_frame, text="Скорость отрисовки (мс)").pack(anchor="w")
        ttk.Scale(
            control_frame,
            from_=1,
            to=80,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=220,
        ).pack(anchor="w", pady=(0, 8))
        ttk.Label(control_frame, textvariable=self.speed_var).pack(anchor="w")

        ttk.Button(
            control_frame,
            text="Построить фрактал",
            command=self.start_render,
        ).pack(fill=tk.X, pady=(16, 4))
        ttk.Button(
            control_frame,
            text="Пауза / продолжить",
            command=self.toggle_pause,
        ).pack(fill=tk.X, pady=4)
        ttk.Button(
            control_frame,
            text="Изменить параметры",
            command=self.apply_live_changes,
        ).pack(fill=tk.X, pady=4)
        ttk.Button(
            control_frame,
            text="Скриншот",
            command=self.save_screenshot,
        ).pack(fill=tk.X, pady=4)

        ttk.Label(
            control_frame,
            textvariable=self.status_var,
            wraplength=250,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(16, 0))

        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _validate_params(self) -> None:
        if self.degree_var.get() < 2:
            raise ValueError("Степень должна быть не меньше 2")
        if self.resolution_var.get() < 50:
            raise ValueError("Разрешение должно быть не меньше 50")
        if self.iterations_var.get() <= 0:
            raise ValueError("Количество итераций должно быть положительным")
        if self.tolerance_var.get() <= 0:
            raise ValueError("Точность должна быть больше нуля")
        if self.range_var.get() <= 0:
            raise ValueError("Диапазон должен быть больше нуля")

    def _prepare_grid(self) -> None:
        self._validate_params()
        degree = self.degree_var.get()
        resolution = self.resolution_var.get()
        plane_range = self.range_var.get()

        axis_values = np.linspace(-plane_range, plane_range, resolution)
        self.grid_real, self.grid_imag = np.meshgrid(axis_values, axis_values)
        self.result = np.zeros((resolution, resolution, 3), dtype=float)
        self.roots = np.array(
            [np.exp(2j * np.pi * root / degree) for root in range(degree)],
            dtype=complex,
        )
        self.total_rows = resolution
        self.current_row = 0
        self.is_paused = False

    def start_render(self) -> None:
        """Start fractal rendering from scratch."""
        self._cancel_render()
        try:
            self._prepare_grid()
        except ValueError as error:
            messagebox.showerror("Ошибка параметров", str(error))
            return

        self.status_var.set("Построение началось.")
        self._render_next_row()

    def _render_next_row(self) -> None:
        """Render one row and schedule the next one."""
        if self.is_paused:
            return

        if (
            self.grid_real is None
            or self.grid_imag is None
            or self.result is None
            or self.roots is None
        ):
            return

        if self.current_row >= self.total_rows:
            self.status_var.set("Построение завершено.")
            self.render_job = None
            return

        row_complex = self.grid_real[self.current_row] + 1j * self.grid_imag[self.current_row]
        rendered_row = self._compute_row(row_complex)
        self.result[self.current_row] = rendered_row
        self.current_row += 1

        self._draw_current_result()
        progress = self.current_row / self.total_rows * 100
        self.status_var.set(
            f"Построение: {self.current_row}/{self.total_rows} строк ({progress:.1f}%)."
        )
        self.render_job = self.root.after(int(self.speed_var.get()), self._render_next_row)

    def _compute_row(  # pylint: disable=too-many-locals
        self, row_complex: np.ndarray
    ) -> np.ndarray:
        """Compute colors for one row of the fractal."""
        degree = self.degree_var.get()
        max_iterations = self.iterations_var.get()
        tolerance = self.tolerance_var.get()
        roots = self.roots
        assert roots is not None

        z_values = row_complex.copy()
        iteration_counts = np.zeros_like(z_values, dtype=int)

        for iteration in range(max_iterations):
            derivative = degree * np.power(z_values, degree - 1)
            safe_mask = np.abs(derivative) > 1e-12
            z_values[safe_mask] = z_values[safe_mask] - (
                (np.power(z_values[safe_mask], degree) - 1) / derivative[safe_mask]
            )

            distances = np.abs(z_values[:, None] - roots[None, :])
            converged = distances.min(axis=1) < tolerance
            just_converged = (iteration_counts == 0) & converged
            iteration_counts[just_converged] = iteration + 1

        distances = np.abs(z_values[:, None] - roots[None, :])
        root_indices = distances.argmin(axis=1)
        normalized_iterations = np.where(
            iteration_counts == 0,
            max_iterations,
            iteration_counts,
        ) / max_iterations

        palette = np.array(
            [
                [0.87, 0.24, 0.24],
                [0.20, 0.52, 0.89],
                [0.18, 0.67, 0.42],
                [0.94, 0.72, 0.18],
                [0.55, 0.36, 0.80],
                [0.11, 0.72, 0.76],
                [0.90, 0.46, 0.15],
                [0.48, 0.48, 0.48],
            ],
            dtype=float,
        )
        colors = palette[root_indices % len(palette)]
        brightness = 0.35 + 0.65 * (1 - normalized_iterations[:, None])
        return np.clip(colors * brightness, 0, 1)

    def toggle_pause(self) -> None:
        """Pause or resume rendering."""
        if self.result is None:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.status_var.set("Построение приостановлено.")
            self._cancel_render()
        else:
            self.status_var.set("Построение продолжено.")
            self._render_next_row()

    def apply_live_changes(self) -> None:
        """Rebuild fractal with current parameters."""
        self.start_render()
        self.status_var.set("Параметры обновлены, построение перезапущено.")

    def save_screenshot(self) -> None:
        """Save current image to the active working directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"newton_basins_{timestamp}.png",
        )
        self.figure.savefig(output_path, dpi=180)
        self.status_var.set(f"Скриншот сохранён: {output_path}")

    def _init_blank_scene(self) -> None:
        self.axis.clear()
        self.axis.set_title("Бассейны Ньютона")
        self.axis.set_xlabel("Re(z)")
        self.axis.set_ylabel("Im(z)")
        self.axis.text(
            0.5,
            0.5,
            "Нажмите «Построить фрактал»",
            ha="center",
            va="center",
            transform=self.axis.transAxes,
        )
        self.canvas.draw_idle()

    def _draw_current_result(self) -> None:
        """Draw current partially rendered image."""
        assert self.result is not None
        plane_range = self.range_var.get()
        self.axis.clear()
        self.axis.set_title(
            f"Бассейны Ньютона для z^{self.degree_var.get()} - 1"
        )
        self.axis.set_xlabel("Re(z)")
        self.axis.set_ylabel("Im(z)")
        self.axis.imshow(
            self.result,
            origin="lower",
            extent=(-plane_range, plane_range, -plane_range, plane_range),
        )
        self.canvas.draw_idle()

    def _cancel_render(self) -> None:
        if self.render_job is not None:
            self.root.after_cancel(self.render_job)
            self.render_job = None

    def run(self) -> None:
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    NewtonBasinsApp().run()
