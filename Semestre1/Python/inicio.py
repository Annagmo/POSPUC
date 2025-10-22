import pygame
import sys
import subprocess
import time

pygame.init()

pygame.mixer.init()

pygame.mixer.music.load("assets/trekoMusica.mp3") #começa logo no inicio

pygame.mixer.music.play(-1) 

W, H = 800, 720
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("Kobayashi Combat")
font = pygame.font.Font("assets/IRISFont.ttf", 24) #fonte q eu fiz pra outro jogo meu uns anos atras, era english based então n tem acento.
small_font = pygame.font.Font("assets/IRISFont.ttf", 20) 

WHITE, GREEN, BLUE, RED = (255,255,255), (0,255,0), (0,100,255), (255,0,0) #queria usar o colorist mas ai o povo que rodar teria que baixar

background = pygame.image.load("assets/background.png").convert()
background = pygame.transform.scale(background, (W, H))

def show_intro():
    run = True
    while run:
        win.blit(background, (0,0))

        title_surf = font.render("Bem-vindo ao Kobayashi Combat!", True, BLUE)
        win.blit(title_surf, (W//2 - title_surf.get_width()//2, H//4))

        instructions = [
            "Mova a Enterprise com as setas ou WASD.",
            "Mire seus tiros com o mouse.",
            "Atire com o botao esquerdo do mouse.",
            "Destrua os Klingons para vencer!"
        ]

        for i, text in enumerate(instructions):
            instr_surf = small_font.render(text, True, RED)
            win.blit(instr_surf, (W//2 - instr_surf.get_width()//2, H//2 + i*40))

        prompt = small_font.render("Clique ou espaco para comecar.", True, GREEN)
        win.blit(prompt, (W//2 - prompt.get_width()//2, H - 100))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                run = False
                return True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    run = False
                    return True

if __name__ == "__main__":
    start_game = show_intro()
    if start_game:

        #Depois que eu lembrei q o jogo q eu tava querendo fazer é baseado no Asteroids de 79 não o space invaders. 
        game_process = subprocess.Popen([sys.executable, "StarTrekInvaders.py"])

        #wait fecha
        game_process.wait()

        #mata a musica
        pygame.mixer.music.stop()

        pygame.quit()
