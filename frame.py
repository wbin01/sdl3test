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
        
    def run(self) -> int:
        self.__event_loop()

        sdl3.SDL_DestroyRenderer(self.__renderer)
        sdl3.SDL_DestroyWindow(self.__frame)
        sdl3.SDL_Quit()
        return 0
    
    def __event_loop(self) -> None:
        while self.__running:
            event = sdl3.SDL_Event()

            while sdl3.SDL_PollEvent(event):
                print(self.__resize_region)
                if event.type == sdl3.SDL_EVENT_QUIT:
                    self.__running = False
                
                if event.type == sdl3.SDL_EVENT_KEY_DOWN:
                    if event.key.keysym.sym == sdl3.SDLK_ESCAPE:
                        self.__running = False
                
                if event.type == sdl3.SDL_EVENT_MOUSE_BUTTON_DOWN:
                    if event.button.button == sdl3.SDL_BUTTON_LEFT:
                        self.__resize_region = self.__detect_resize_region()
                        if self.__resize_region != ResizeRegion.NONE:
                            self.__update_resize()
                        else:
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
            sdl3.SDL_SetRenderDrawColor(self.__renderer, 0, 0, 0, 100)
            sdl3.SDL_RenderClear(self.__renderer)

            # Draw transparent red rect - SDL_FRect!
            sdl3.SDL_SetRenderDrawColor(self.__renderer, 255, 100, 100, 220)
            frect = sdl3.SDL_FRect(x=100.0, y=100.0, w=440.0, h=280.0)
            sdl3.SDL_RenderFillRect(self.__renderer, frect)   # ← direct on object

            # Green lines (SDL_RenderLine - It also accepts floats)
            sdl3.SDL_SetRenderDrawColor(self.__renderer, 100, 255, 100, 255)
            for i in range(15):
                sdl3.SDL_RenderLine(self.__renderer, 50.0 + i * 40.0, 50.0, 100.0 + i * 40.0, 400.0)

            sdl3.SDL_RenderPresent(self.__renderer)
            sdl3.SDL_Delay(10)

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
    
    def __start_resize(self):
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
    
    def __stop_resize(self):
        self.__resizing = False
        self.__resize_region = ResizeRegion.NONE

    def __update_resize(self):
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
