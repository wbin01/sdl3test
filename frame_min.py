import sys
import sdl3

class Frame(object):
    """..."""
    def __init__(self) -> None:
        # sdl3.SDL_SetHint(sdl3.SDL_HINT_RENDER_DRIVER, b'vulkan')
        if sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO) < 0:  # DONT use SDL_INIT_EVERYTHING
            print('SDL3 init error:', sdl3.SDL_GetError())
            sys.exit(1)

        frame_flags = (
            sdl3.SDL_WINDOW_BORDERLESS | sdl3.SDL_WINDOW_ALWAYS_ON_TOP | sdl3.SDL_WINDOW_TRANSPARENT)
        self.__frame = sdl3.SDL_CreateWindow(
            b'Transparente Frame - SDL3 + PySDL3', 640, 480, frame_flags)

        if not self.__frame:
            print('Frame creation error:', sdl3.SDL_GetError())
            sdl3.SDL_Quit()
            sys.exit(1)

        sdl3.SDL_SetWindowOpacity(self.__frame, 0.80)
        self.__renderer = sdl3.SDL_CreateRenderer(self.__frame, None)

        if not self.__renderer:
            print('Renderer creation error:', sdl3.SDL_GetError())
            sdl3.SDL_DestroyWindow(self.__frame)
            sdl3.SDL_Quit()
            sys.exit(1)

        # VSync optional
        sdl3.SDL_SetRenderVSync(self.__renderer, 1)  # 1 = on, 0 = off, -1 = adapt

        self.__running = True
        
    def run(self) -> int:
        while self.__running:
            event = sdl3.SDL_Event()

            while sdl3.SDL_PollEvent(event):
                if event.type == sdl3.SDL_EVENT_QUIT:
                    self.__running = False
                if event.type == sdl3.SDL_EVENT_KEY_DOWN:
                    if event.key.keysym.sym == sdl3.SDLK_ESCAPE:
                        self.__running = False

            # Clear Frame with alpha 0
            sdl3.SDL_SetRenderDrawColor(self.__renderer, 0, 0, 0, 0)
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

        sdl3.SDL_DestroyRenderer(self.__renderer)
        sdl3.SDL_DestroyWindow(self.__frame)
        sdl3.SDL_Quit()
        return 0


if __name__ == "__main__":
    app = Frame()
    sys.exit(app.run())

# SDL_RENDERER_DRIVER=vulkan python -O main.py
