from __future__ import annotations

from pathlib import Path
import time

import moderngl

from engine.camera import Camera


class Renderer:
    def __init__(self, width: int, height: int) -> None:
        self.ctx = moderngl.create_context(require=330)
        self.ctx.viewport = (0, 0, width, height)

        shader_dir = Path(__file__).resolve().parent.parent / "shaders"
        vertex_source = (shader_dir / "quad.vert").read_text(encoding="utf-8")
        fragment_source = (shader_dir / "mandelbrot.frag").read_text(encoding="utf-8")

        self.program = self.ctx.program(
            vertex_shader=vertex_source,
            fragment_shader=fragment_source,
        )
        self.vao = self.ctx.vertex_array(self.program, [])
        self.start_time = time.perf_counter()

    def resize(self, width: int, height: int) -> None:
        self.ctx.viewport = (0, 0, width, height)

    def render(
        self,
        camera: Camera,
        max_iterations: int,
        palette_id: int,
        palette_offset: float,
        animate_palette: bool,
    ) -> None:
        elapsed = time.perf_counter() - self.start_time

        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.program["u_center"].value = (camera.center_x, camera.center_y)
        self.program["u_scale"].value = camera.scale
        self.program["u_resolution"].value = (
            float(camera.width),
            float(camera.height),
        )
        self.program["u_max_iterations"].value = max_iterations
        self.program["u_palette_id"].value = palette_id
        self.program["u_palette_offset"].value = palette_offset
        self.program["u_time"].value = elapsed if animate_palette else 0.0
        self.vao.render(mode=moderngl.TRIANGLES, vertices=3)
