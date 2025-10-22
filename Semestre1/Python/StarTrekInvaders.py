import pygame, math, random

#screen setup
pygame.init()
W, H = 800, 720
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("Kobayashi Combat")
pygame.mouse.set_visible(False)
font = pygame.font.Font("assets/IRISFont.ttf", 20) 

# cores
WHITE, RED, GREEN, BLUE, BLACK = (255,255,255), (255,0,0), (0,255,0), (0,100,255), (0,0,0)

#Import de imagens
background = pygame.image.load("assets/background.png").convert()
background = pygame.transform.scale(background, (W, H))

enterprise_base = pygame.image.load("assets/enterprise.png").convert_alpha()
enterprise_base = pygame.transform.scale(enterprise_base, (49, 101))

klingon_base = pygame.image.load("assets/klingon.png").convert_alpha()
klingon_base = pygame.transform.scale(klingon_base, (72, 49))  

# Naves
class Ship:
    def __init__(self, x, y, color, health, speed=4, image=None):
        self.x, self.y, self.color, self.health, self.speed = x, y, color, health, speed
        self.bullets, self.can_shoot = [], True
        self.image = image
        self.angle = 0  # angulo pra que as naves fiquem olhando uma pra outra

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, 50, 50)

    @property
    def center(self):
        return (self.x + 25, self.y + 25)

    def move(self, keys):
        # movimento com setas. Ou WASD pra pessoas destras.
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] + keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP] + keys[pygame.K_s] - keys[pygame.K_w]) * self.speed
        self.x = min(max(self.x + dx, 0), W - 50)
        self.y = min(max(self.y + dy, 0), H - 50)

    def shoot(self, tx, ty, speed=10):
        if not self.can_shoot:
            return
        dx, dy = tx - self.center[0], ty - self.center[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx, dy = dx / dist * speed, dy / dist * speed
        self.bullets.append([pygame.Rect(self.center[0], self.center[1], 6, 6), dx, dy])
        if self.color == GREEN:
            self.can_shoot = False

    def update_bullets(self):
        updated = []
        for b, dx, dy in self.bullets:
            b.x += dx
            b.y += dy
            if 0 < b.x < W and 0 < b.y < H:
                updated.append([b, dx, dy])
        self.bullets = updated

    def draw(self, surf, target=None):
        if self.image:
            if target:
                dx, dy = target.center[0] - self.center[0], target.center[1] - self.center[1]
                self.angle = math.degrees(math.atan2(-dy, dx)) - 90  # -90 pra top facing
            rotated_img = pygame.transform.rotate(self.image, self.angle)
            rect = rotated_img.get_rect(center=self.center)
            surf.blit(rotated_img, rect.topleft)
        else:
            pygame.draw.rect(surf, self.color, (self.x, self.y, 50, 50))

        for b, _, _ in self.bullets:
            pygame.draw.rect(surf, WHITE, b)


# funcs simples de ajuda por ser topdown game:

def vector_to(a, b, s): #função de vetor distancia entre as naves
    dx, dy = (b.x - a.x), (b.y - a.y)
    d = math.hypot(dx, dy)
    return (dx / d * s, dy / d * s) if d else (0, 0)

#função para tirar vida de ambas as naves
def check_hits(shooter, target, level):
    hits = []
    for b, dx, dy in shooter.bullets:
        if target.rect.colliderect(b):
            if shooter.color == GREEN:  # se for o player
                target.health -= 10 + (level - 1) * 10
            else:
                target.health -= 10
        else:
            hits.append((b, dx, dy))
    shooter.bullets = hits

def separate_ships(a, b): 
    #função pra uma nave n ficar em cima da outra pq fica feio. 
    #Eu Sou mais acostumada com jogo em godot mas não sabia se aqui tinha collision polygon.

    if a.rect.colliderect(b.rect):
        overlap_x = (a.rect.width + b.rect.width) / 2 - abs(a.rect.centerx - b.rect.centerx)
        overlap_y = (a.rect.height + b.rect.height) / 2 - abs(a.rect.centery - b.rect.centery)
        if overlap_x < overlap_y:
            if a.rect.centerx < b.rect.centerx:
                a.x -= overlap_x / 2
                b.x += overlap_x / 2
            else:
                a.x += overlap_x / 2
                b.x -= overlap_x / 2
        else:
            if a.rect.centery < b.rect.centery:
                a.y -= overlap_y / 2
                b.y += overlap_y / 2
            else:
                a.y += overlap_y / 2
                b.y -= overlap_y / 2

#mostra tela de novo nivel e fim do jogo
def show_message(text, color=WHITE, delay=1500):
    win.blit(background, (0,0))
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(W//2, H//2))
    win.blit(text_surf, text_rect.topleft)
    pygame.display.flip()
    pygame.time.wait(delay)


def spawn_enemy(enemies, level, min_dist):
    for _ in range(1000):  # tenta bastante vezes
        x = random.randint(50, W - 100)
        y = random.randint(50, H // 2)
        new_enemy = Ship(x, y, RED, 100 + 20 * level, 3 + level * 0.3, image=klingon_base)
        if all(math.hypot(new_enemy.center[0] - e.center[0], new_enemy.center[1] - e.center[1]) >= min_dist for e in enemies):
            return new_enemy
    raise Exception("Não foi possível posicionar inimigos sem sobreposição.")

def run_level(level):
    clock = pygame.time.Clock()
    
    player_speed = 4 + (level - 1) * 0.1  # começa com 4 e aumenta 0.1 por nível
    player_life = 100 + (level - 1) * 10 #da 10 a mais de vida, vai q ajuda
    #max life a cada nivel
    player = Ship(W//2, H-150, GREEN, player_life, player_speed, image=enterprise_base) #x, y, color, health, speed=4, image=None

    enemies = []
    min_dist = 80  #min distancia entre Klingons aleatoriamente posicionados
    try:
        for _ in range(level):
            enemies.append(spawn_enemy(enemies, level, min_dist))
    except Exception:
        show_message("Erro.", RED, 3000) #Poo sempre bom
        return False, level

    shoot_timer = 0
    run = True
    while run:
        clock.tick(60)
        win.blit(background, (0,0))

        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONUP:
                player.can_shoot = True

        keys = pygame.key.get_pressed()
        player.move(keys) 

        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            player.shoot(mx, my)
        pygame.draw.circle(win, BLUE, (mx, my), 10)

        #Move inimigos
        for enemy in enemies:
            vx, vy = vector_to(enemy, player, enemy.speed)
            enemy.x += vx
            enemy.y += vy

        #separa Klingons de Enterprise
        for enemy in enemies:
            separate_ships(player, enemy)

        #Separa entre Klingons
        for i in range(len(enemies)):
            for j in range(i+1, len(enemies)):
                separate_ships(enemies[i], enemies[j])

        player.update_bullets()
        for enemy in enemies:
            enemy.update_bullets()

        # desenha as naves olhando uma para a outra
        player.draw(win, target=enemies[0] if enemies else None)
        for enemy in enemies:
            enemy.draw(win, target=player)

        # inimigos atiram a cada 30 ticks
        shoot_timer += 1
        if shoot_timer >= 30:
            for enemy in enemies:
                enemy.shoot(player.center[0], player.center[1], 7)
            shoot_timer = 0

        # checa se acertou
        for enemy in enemies:
            check_hits(player, enemy, level)
            check_hits(enemy, player, level)

        # HUD
        level_text = font.render(f"Nivel: {level}", True, WHITE)
        win.blit(level_text, (10, 10))
        win.blit(font.render(f"Vida Player: {player.health}", True, GREEN), (10, 50))
        for idx, enemy in enumerate(enemies):
            win.blit(font.render(f"Vida Inimigo {idx+1}: {enemy.health}", True, RED), (10, 80 + idx*30)) #posiciona aleatorio q n é lá aleatorio msm

        # remove Klingons mortos
        enemies = [e for e in enemies if e.health > 0]

        #vê se venceu ou perdeu e dá o level
        if not enemies:
            return True 
        if player.health <= 0:
            return False, level  

        pygame.display.flip()

#Main loop de níveis infinitos
def main():
    level = 1
    while level <= 10: 
        show_message(f"Prepare-se para o nivel {level}!", BLUE, 1500)
        result = run_level(level)
        if result is True:
            level += 1
        else:
            _, reached_level = result
            show_message(f"Parabens, voce chegou ate o nivel {reached_level}!", GREEN, 3000) 

            text_surf = font.render("Pressione Z para sair", True, WHITE)
            text_rect = text_surf.get_rect(center=(W//2, H//2 + 40))
            win.blit(text_surf, text_rect.topleft)
            pygame.display.flip()

            while True:
                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_z:
                        pygame.quit()
                        exit()

    if level > 10:
        show_message(f"Parabens, voce terminou o jogo!", GREEN, 3000)

        text_surf = font.render("Pressione Z para sair", True, WHITE)
        text_rect = text_surf.get_rect(center=(W//2, H//2 + 40))
        win.blit(text_surf, text_rect.topleft)
        pygame.display.flip()

        while True:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key == pygame.K_z:
                    pygame.quit()
                    exit()

    

main()
