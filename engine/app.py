from __future__ import annotations

import math
import time

import glfw

from engine.camera import Camera
from engine.renderer import Renderer


class MandelbrotApp:
    def __init__(self) -> None:
        if not glfw.init():
            raise RuntimeError("GLFW initialization failed")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

        self.width = 1280
        self.height = 720
        self.window = glfw.create_window(
            self.width,
            self.height,
            "Mandelbrot Stage 1",
            None,
            None,
        )

        if not self.window:
            glfw.terminate()
            raise RuntimeError("OpenGL 3.3 window creation failed")

        glfw.make_context_current(self.window)
        glfw.swap_interval(0)

        self.camera = Camera(self.width, self.height)
        self.renderer = Renderer(self.width, self.height)

        self.dragging = False
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0
        self.auto_zoom = False
        self.animate_palette = True
        self.palette_id = 0
        self.palette_offset = 0.0
        self.base_iterations = 250

        self.last_time = time.perf_counter()
        self.title_time = self.last_time
        self.frame_count = 0

        glfw.set_window_user_pointer(self.window, self)
        glfw.set_framebuffer_size_callback(self.window, self._framebuffer_size_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_position_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_button_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_key_callback(self.window, self._key_callback)

    @staticmethod
    def _instance(window):
        return glfw.get_window_user_pointer(window)

    @staticmethod
    def _framebuffer_size_callback(window, width, height):
        app = MandelbrotApp._instance(window)
        if app is None or width <= 0 or height <= 0:
            return
        app.width = width
        app.height = height
        app.camera.resize(width, height)
        app.renderer.resize(width, height)

    @staticmethod
    def _cursor_position_callback(window, x, y):
        app = MandelbrotApp._instance(window)
        if app is None:
            return
        if app.dragging:
            app.camera.pan_pixels(x - app.last_mouse_x, y - app.last_mouse_y)
        app.last_mouse_x = x
        app.last_mouse_y = y

    @staticmethod
    def _mouse_button_callback(window, button, action, mods):
        app = MandelbrotApp._instance(window)
        if app is None:
            return
        if button == glfw.MOUSE_BUTTON_LEFT:
            app.dragging = action == glfw.PRESS
            app.last_mouse_x, app.last_mouse_y = glfw.get_cursor_pos(window)

    @staticmethod
    def _scroll_callback(window, x_offset, y_offset):
        app = MandelbrotApp._instance(window)
        if app is None:
            return
        x, y = glfw.get_cursor_pos(window)
        factor = 0.80 ** y_offset
        app.camera.zoom_at(x, y, factor)

    @staticmethod
    def _key_callback(window, key, scancode, action, mods):
        app = MandelbrotApp._instance(window)
        if app is None or action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_SPACE:
            app.auto_zoom = not app.auto_zoom
        elif key == glfw.KEY_R:
            app.camera.reset()
            app.base_iterations = 250
            app.palette_offset = 0.0
            app.auto_zoom = False
        elif key == glfw.KEY_C:
            app.palette_id = (app.palette_id + 1) % 4
        elif key in (glfw.KEY_1, glfw.KEY_2, glfw.KEY_3, glfw.KEY_4):
            app.palette_id = key - glfw.KEY_1
        elif key == glfw.KEY_LEFT_BRACKET:
            app.palette_offset -= 0.05
        elif key == glfw.KEY_RIGHT_BRACKET:
            app.palette_offset += 0.05
        elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD):
            app.base_iterations = min(3000, app.base_iterations + 50)
        elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT):
            app.base_iterations = max(50, app.base_iterations - 50)
        elif key == glfw.KEY_P:
            app.animate_palette = not app.animate_palette

    def _adaptive_iterations(self) -> int:
        zoom_term = max(0.0, math.log10(max(1.0, self.camera.zoom)))
        return min(3000, int(self.base_iterations + zoom_term * 85.0))

    def _update(self, dt: float) -> None:
        move = self.camera.scale * 0.9 * dt
        zoom_factor = math.exp(1.8 * dt)

        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS or glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            self.camera.pan_world(0.0, move)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS or glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            self.camera.pan_world(0.0, -move)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS or glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
            self.camera.pan_world(-move, 0.0)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS or glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.camera.pan_world(move, 0.0)
        if glfw.get_key(self.window, glfw.KEY_Q) == glfw.PRESS:
            self.camera.zoom_at(self.width * 0.5, self.height * 0.5, 1.0 / zoom_factor)
        if glfw.get_key(self.window, glfw.KEY_E) == glfw.PRESS:
            self.camera.zoom_at(self.width * 0.5, self.height * 0.5, zoom_factor)

        if self.auto_zoom:
            self.camera.zoom_at(
                self.width * 0.5,
                self.height * 0.5,
                math.exp(-0.55 * dt),
            )

    def _update_title(self, now: float, iterations: int) -> None:
        self.frame_count += 1
        elapsed = now - self.title_time
        if elapsed < 0.25:
            return

        fps = self.frame_count / elapsed
        self.frame_count = 0
        self.title_time = now

        glfw.set_window_title(
            self.window,
            (
                f"Mandelbrot Stage 1 | {fps:6.1f} FPS | "
                f"zoom {self.camera.zoom:.3e} | "
                f"iterations {iterations} | "
                f"palette {self.palette_id + 1}"
            ),
        )

    def run(self) -> None:
        try:
            while not glfw.window_should_close(self.window):
                now = time.perf_counter()
                dt = min(now - self.last_time, 0.1)
                self.last_time = now

                glfw.poll_events()
                self._update(dt)

                iterations = self._adaptive_iterations()
                self.renderer.render(
                    self.camera,
                    iterations,
                    self.palette_id,
                    self.palette_offset,
                    self.animate_palette,
                )

                glfw.swap_buffers(self.window)
                self._update_title(now, iterations)
        finally:
            glfw.destroy_window(self.window)
            glfw.terminate()
