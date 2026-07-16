from __future__ import annotations

import math


class Camera:
    def __init__(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)
        self.center_x = -0.743643887037151
        self.center_y = 0.131825904205330
        self.scale = 2.2

    def reset(self) -> None:
        self.center_x = -0.743643887037151
        self.center_y = 0.131825904205330
        self.scale = 2.2

    def resize(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)

    def screen_to_complex(self, x: float, y: float) -> tuple[float, float]:
        nx = (2.0 * x - self.width) / self.height
        ny = (self.height - 2.0 * y) / self.height
        return (
            self.center_x + nx * self.scale,
            self.center_y + ny * self.scale,
        )

    def zoom_at(self, x: float, y: float, factor: float) -> None:
        before_x, before_y = self.screen_to_complex(x, y)
        self.scale = max(self.scale * factor, 1e-14)
        after_x, after_y = self.screen_to_complex(x, y)
        self.center_x += before_x - after_x
        self.center_y += before_y - after_y

    def pan_pixels(self, dx: float, dy: float) -> None:
        factor = 2.0 * self.scale / self.height
        self.center_x -= dx * factor
        self.center_y += dy * factor

    def pan_world(self, dx: float, dy: float) -> None:
        self.center_x += dx
        self.center_y += dy

    @property
    def zoom(self) -> float:
        return 2.2 / self.scale

    @property
    def estimated_decimal_digits(self) -> int:
        if self.scale >= 1.0:
            return 0
        return max(0, int(-math.log10(self.scale)))
