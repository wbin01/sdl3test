#!/usr/bin/env python3
import sys
from ctypes import c_float, c_int

import sdl3

from resize_region import ResizeRegion


class Frame(object):
    """..."""
    def __init__(self) -> None:
        # Init
        if sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO) < 0:  # DONT use SDL_INIT_EVERYTHING
            # SDL_SetHint(sdl3.SDL_HINT_RENDER_DRIVER, b'vulkan')
            print('SDL3 init error:', sdl3.SDL_GetError())
            sys.exit(1)

        # Frame
        self.__frame = sdl3.SDL_CreateWindow(
            b'Transparente Frame - SDL3 + PySDL3', 640, 480,
            (sdl3.SDL_WINDOW_BORDERLESS | sdl3.SDL_WINDOW_TRANSPARENT))

        if not self.__frame:
            print('Frame creation error:', sdl3.SDL_GetError())
            sdl3.SDL_Quit()
            sys.exit(1)

        sdl3.SDL_SetWindowOpacity(self.__frame, 0.80)

        # Renderer
        self.__renderer = sdl3.SDL_CreateRenderer(self.__frame, None)

        if not self.__renderer:
            print('Renderer creation error:', sdl3.SDL_GetError())
            sdl3.SDL_DestroyWindow(self.__frame)
            sdl3.SDL_Quit()
            sys.exit(1)

        sdl3.SDL_SetRenderVSync(self.__renderer, 1)  # VSync optional | 1 = on, 0 = off, -1 = adapt
        
        # Control Frame
        self.__running = True

        # Control Frame - Drag 
        self.__dragging = False
        self.__drag_offset_x = 0
        self.__drag_offset_y = 0

        # Control Frame - resize
        self.__resizing = False
        self.__resize_region = ResizeRegion.NONE
        self.__resize_border = 8

        # Control Cursor
        self.__cursor = {
            'TOP': sdl3.SDL_CreateSystemCursor(8),
            'BOTTOM': sdl3.SDL_CreateSystemCursor(8),
            'LEFT': sdl3.SDL_CreateSystemCursor(7),
            'RIGHT': sdl3.SDL_CreateSystemCursor(7),
            'TOPLEFT': sdl3.SDL_CreateSystemCursor(5),
            'BOTTOMRIGHT': sdl3.SDL_CreateSystemCursor(5),
            'TOPRIGHT': sdl3.SDL_CreateSystemCursor(6),
            'BOTTOMLEFT': sdl3.SDL_CreateSystemCursor(6),
            'NONE': sdl3.SDL_CreateSystemCursor(0),
            'DRAG': sdl3.SDL_CreateSystemCursor(9),
        }
        self.__last_resize_cursor_on_hover = 'NONE'
        
    def run(self) -> int:
        self.__event_loop()
        self.__destroy()
        return 0
    
    def __destroy(self):
        for c in self.__cursor.values():
            sdl3.SDL_DestroyCursor(c)

        sdl3.SDL_DestroyRenderer(self.__renderer)
        sdl3.SDL_DestroyWindow(self.__frame)
        sdl3.SDL_Quit()

    def __event_loop(self) -> None:
        while self.__running:
            event = sdl3.SDL_Event()

            while sdl3.SDL_PollEvent(event):

                resize_region = self.__detect_resize_region()
                if resize_region.value != self.__last_resize_cursor_on_hover:
                    self.__update_cursor(resize_region.value)
                    self.__last_resize_cursor_on_hover = resize_region.value

                if event.type == sdl3.SDL_EVENT_QUIT:
                    self.__running = False
                
                if event.type == sdl3.SDL_EVENT_KEY_DOWN:
                    if event.key.keysym.sym == sdl3.SDLK_ESCAPE:
                        self.__running = False
                
                if event.type == sdl3.SDL_EVENT_MOUSE_BUTTON_DOWN:
                    if event.button.button == sdl3.SDL_BUTTON_LEFT:
                        self.__resize_region = self.__detect_resize_region()
                        if self.__resize_region != ResizeRegion.NONE:
                            self.__update_cursor(self.__resize_region.value)
                            self.__update_resize()
                        else:
                            self.__update_cursor('DRAG')
                            self.__update_drag()

                elif event.type == sdl3.SDL_EVENT_MOUSE_BUTTON_UP:
                    if event.button.button == sdl3.SDL_BUTTON_LEFT:
                        self.__stop_resize()
                        self.__stop_drag()

                elif event.type == sdl3.SDL_EVENT_MOUSE_MOTION:
                    if self.__resize_region != ResizeRegion.NONE:
                        self.__start_resize()
                    elif self.__dragging:
                        self.__start_drag()

            # Clear Frame with alpha 0
            sdl3.SDL_SetRenderDrawColor(self.__renderer, 0, 0, 0, 0)
            sdl3.SDL_RenderClear(self.__renderer)

            w = c_int()
            h = c_int()
            sdl3.SDL_GetWindowSize(self.__frame, w, h)
            self.draw_rect(0, 0, w.value, h.value, (200, 200, 200, 255), 8)
            self.draw_rect(1, 1, w.value - 2, h.value - 2, (100, 100, 100, 255), 7)

            sdl3.SDL_RenderPresent(self.__renderer)
            sdl3.SDL_Delay(10)
    
    def __draw_filled_circle(self, cx, cy, r):
        for dy in range(-r, r + 1):
            dx = int((r*r - dy*dy) ** 0.5)
            sdl3.SDL_RenderLine(self.__renderer, cx - dx, cy + dy, cx + dx, cy + dy)

    def draw_rect(self, x, y, w, h, color, r):
        tl = tr = br = bl = r
        rmax = min(w // 2, h // 2)
        tl = min(tl, rmax)
        tr = min(tr, rmax)
        br = min(br, rmax)
        bl = min(bl, rmax)

        sdl3.SDL_SetRenderDrawColor(self.__renderer, *color)

        # Middle
        sdl3.SDL_RenderFillRect(
            self.__renderer, sdl3.SDL_FRect(x + tl, y, w - tl - tr, h))
        
        # Left
        sdl3.SDL_RenderFillRect(
            self.__renderer, sdl3.SDL_FRect(x, y + tl, tl, h - tl - bl))
        
        # Right
        sdl3.SDL_RenderFillRect(
            self.__renderer, sdl3.SDL_FRect(x + w - tr, y + tr, tr, h - tr - br))

        # Corners circles
        if tl:
            self.__draw_filled_circle(x + tl, y + tl, tl)
        if tr:
            self.__draw_filled_circle(x + w - tr - 1, y + tr, tr)
        if br:
            self.__draw_filled_circle(x + w - br - 1, y + h - br - 1, br)
        if bl:
            self.__draw_filled_circle(x + bl, y + h - bl - 1, bl)

    def __detect_resize_region(self) -> ResizeRegion:
        mx = c_float()
        my = c_float()
        sdl3.SDL_GetGlobalMouseState(mx, my)

        wx = c_int()
        wy = c_int()
        sdl3.SDL_GetWindowPosition(self.__frame, wx, wy)

        ww = c_int()
        wh = c_int()
        sdl3.SDL_GetWindowSize(self.__frame, ww, wh)

        x = mx.value - wx.value
        y = my.value - wy.value

        b = self.__resize_border
        w = ww.value
        h = wh.value

        left   = x < b
        right  = x > w - b
        top    = y < b
        bottom = y > h - b

        if top and left:
            return ResizeRegion.TOPLEFT
        if top and right:
            return ResizeRegion.TOPRIGHT
        if bottom and left:
            return ResizeRegion.BOTTOMLEFT
        if bottom and right:
            return ResizeRegion.BOTTOMRIGHT
        if top:
            return ResizeRegion.TOP
        if bottom:
            return ResizeRegion.BOTTOM
        if left:
            return ResizeRegion.LEFT
        if right:
            return ResizeRegion.RIGHT

        return ResizeRegion.NONE
    
    def __update_cursor(self, cursor_name: str) -> None:
        if self.__resizing or self.__dragging:
            return

        sdl3.SDL_SetCursor(self.__cursor[cursor_name])
    
    def __start_resize(self) -> None:
        if not self.__resizing:
            return

        mx = c_float()
        my = c_float()
        sdl3.SDL_GetGlobalMouseState(mx, my)

        dx = mx.value - self.__start_mx.value
        dy = my.value - self.__start_my.value

        x = self.__start_x.value
        y = self.__start_y.value
        w = self.__start_w.value
        h = self.__start_h.value

        r = self.__resize_region

        if r in (ResizeRegion.RIGHT, ResizeRegion.TOPRIGHT, ResizeRegion.BOTTOMRIGHT):
            w += dx

        if r in (ResizeRegion.LEFT, ResizeRegion.TOPLEFT, ResizeRegion.BOTTOMLEFT):
            x += dx
            w -= dx

        if r in (ResizeRegion.BOTTOM, ResizeRegion.BOTTOMLEFT, ResizeRegion.BOTTOMRIGHT):
            h += dy

        if r in (ResizeRegion.TOP, ResizeRegion.TOPLEFT, ResizeRegion.TOPRIGHT):
            y += dy
            h -= dy

        w = max(100, int(w))
        h = max(100, int(h))

        sdl3.SDL_SetWindowPosition(self.__frame, int(x), int(y))
        sdl3.SDL_SetWindowSize(self.__frame, w, h)
    
    def __stop_resize(self) -> None:
        self.__resizing = False
        self.__resize_region = ResizeRegion.NONE
        self.__update_cursor('NONE')

    def __update_resize(self) -> None:
        self.__resizing = True

        self.__start_mx = c_float()
        self.__start_my = c_float()
        sdl3.SDL_GetGlobalMouseState(self.__start_mx, self.__start_my)

        self.__start_x = c_int()
        self.__start_y = c_int()
        sdl3.SDL_GetWindowPosition(self.__frame, self.__start_x, self.__start_y)

        self.__start_w = c_int()
        self.__start_h = c_int()
        sdl3.SDL_GetWindowSize(self.__frame, self.__start_w, self.__start_h)

    def __start_drag(self) -> None:
        # if not self.__dragging or self.__resizing:
        #     return
        
        if hasattr(sdl3, "SDL_StartWindowMove"):
            sdl3.SDL_StartWindowMove(self.__frame)
        else:
            mx = c_float()
            my = c_float()
            sdl3.SDL_GetGlobalMouseState(mx, my)

            new_x = int(mx.value - self.__drag_offset_x)
            new_y = int(my.value - self.__drag_offset_y)

            sdl3.SDL_SetWindowPosition(self.__frame, new_x, new_y)
    
    def __stop_drag(self) -> None:
        self.__dragging = False
        self.__update_cursor('NONE')
    
    def __update_drag(self) -> None:
        self.__dragging = True

        mx = c_float()
        my = c_float()
        sdl3.SDL_GetGlobalMouseState(mx, my)

        wx = c_int()
        wy = c_int()
        sdl3.SDL_GetWindowPosition(self.__frame, wx, wy)

        self.__drag_offset_x = mx.value - wx.value
        self.__drag_offset_y = my.value - wy.value

if __name__ == "__main__":
    app = Frame()
    sys.exit(app.run())

# SDL_RENDERER_DRIVER=vulkan python -O main.py
# SDL_VIDEODRIVER=x11 SDL_RENDERER_DRIVER=vulkan python -O frame.py
