import time
import sys

start_total = time.time()

start_import = time.time()
import sdl3
print(f"Import sdl3: {time.time() - start_import:.2f}s")


def main():
    start = time.time()
    if sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO) < 0:  # NÃO usar SDL_INIT_EVERYTHING
        print("Falha ao inicializar SDL3:", sdl3.SDL_GetError())
        sys.exit(1)
    print(f"SDL_Init: {time.time() - start:.2f}s")

    window_flags = (
        sdl3.SDL_WINDOW_BORDERLESS |
        sdl3.SDL_WINDOW_ALWAYS_ON_TOP |
        sdl3.SDL_WINDOW_TRANSPARENT
    )

    start = time.time()
    window = sdl3.SDL_CreateWindow(
        b"Teste Transparente - SDL3 + PySDL3",
        640,
        480,
        window_flags
    )
    print(f"CreateWindow: {time.time() - start:.2f}s")

    if not window:
        print("Falha ao criar janela:", sdl3.SDL_GetError())
        sdl3.SDL_Quit()
        sys.exit(1)

    sdl3.SDL_SetWindowOpacity(window, 0.80)

    # Correção: só 2 argumentos!
    start = time.time()
    renderer = sdl3.SDL_CreateRenderer(window, None)
    print(f"CreateRenderer: {time.time() - start:.2f}s")

    if not renderer:
        print("Falha ao criar renderer:", sdl3.SDL_GetError())
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
        sys.exit(1)

    # VSync opcional (depois da criação)
    sdl3.SDL_SetRenderVSync(renderer, 1)  # 1 = ligado, 0 = off, -1 = adaptativo

    running = True
    while running:
        event = sdl3.SDL_Event()
        while sdl3.SDL_PollEvent(event):
            if event.type == sdl3.SDL_EVENT_QUIT:
                running = False
            if event.type == sdl3.SDL_EVENT_KEY_DOWN:
                if event.key.keysym.sym == sdl3.SDLK_ESCAPE:
                    running = False

        # Limpa com alpha 0
        sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 100)
        sdl3.SDL_RenderClear(renderer)

        # Desenha retângulo semi-transparente (usando SDL_FRect!)
        sdl3.SDL_SetRenderDrawColor(renderer, 255, 100, 100, 220)
        frect = sdl3.SDL_FRect(x=100.0, y=100.0, w=440.0, h=280.0)
        sdl3.SDL_RenderFillRect(renderer, frect)   # ← passa o objeto diretamente

        # Linhas (SDL_RenderLine aceita floats também)
        sdl3.SDL_SetRenderDrawColor(renderer, 100, 255, 100, 255)
        for i in range(15):
            sdl3.SDL_RenderLine(renderer,
                                50.0 + i * 40.0, 50.0,
                                100.0 + i * 40.0, 400.0)

        sdl3.SDL_RenderPresent(renderer)
        sdl3.SDL_Delay(10)

    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# No final, antes de sys.exit
print(f"Tempo total do script: {time.time() - start_total:.2f}s")
