import sys
import sdl3

def main():
    if sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO) < 0:  # DONT use SDL_INIT_EVERYTHING
        print('SDL3 init error:', sdl3.SDL_GetError())
        sys.exit(1)
    # sdl3.SDL_SetHint(sdl3.SDL_HINT_RENDER_DRIVER, b'vulkan')

    window_flags = (
        sdl3.SDL_WINDOW_BORDERLESS | sdl3.SDL_WINDOW_ALWAYS_ON_TOP | sdl3.SDL_WINDOW_TRANSPARENT)

    window = sdl3.SDL_CreateWindow(
        b'Transparente Frame - SDL3 + PySDL3', 640, 480, window_flags)

    if not window:
        print('Window creation error:', sdl3.SDL_GetError())
        sdl3.SDL_Quit()
        sys.exit(1)

    sdl3.SDL_SetWindowOpacity(window, 0.80)
    renderer = sdl3.SDL_CreateRenderer(window, None)

    if not renderer:
        print('Renderer creation error:', sdl3.SDL_GetError())
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
        sys.exit(1)

    # VSync optional
    sdl3.SDL_SetRenderVSync(renderer, 1)  # 1 = on, 0 = off, -1 = adapt

    running = True
    while running:
        event = sdl3.SDL_Event()

        while sdl3.SDL_PollEvent(event):
            if event.type == sdl3.SDL_EVENT_QUIT:
                running = False
            if event.type == sdl3.SDL_EVENT_KEY_DOWN:
                if event.key.keysym.sym == sdl3.SDLK_ESCAPE:
                    running = False

        # Clear with alpha 0
        sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 100)
        sdl3.SDL_RenderClear(renderer)

        # Draw transparent rect - SDL_FRect!
        sdl3.SDL_SetRenderDrawColor(renderer, 255, 100, 100, 220)
        frect = sdl3.SDL_FRect(x=100.0, y=100.0, w=440.0, h=280.0)
        sdl3.SDL_RenderFillRect(renderer, frect)   # ← direct on object

        # Green lines (SDL_RenderLine - It also accepts floats)
        sdl3.SDL_SetRenderDrawColor(renderer, 100, 255, 100, 255)
        for i in range(15):
            sdl3.SDL_RenderLine(renderer, 50.0 + i * 40.0, 50.0, 100.0 + i * 40.0, 400.0)

        sdl3.SDL_RenderPresent(renderer)
        sdl3.SDL_Delay(10)

    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# SDL_RENDERER_DRIVER=vulkan python -O main.py
