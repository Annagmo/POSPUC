# music.py
import pygame

# inicializa o mixer
pygame.mixer.init()
pygame.mixer.music.load("assets/trekoMusica.mp3")  # coloquei na pasta assets
pygame.mixer.music.play(-1)  # -1 significa loop infinito

# mantém o script vivo até ser terminado pelo processo principal
while True:
    pygame.time.wait(1000)
