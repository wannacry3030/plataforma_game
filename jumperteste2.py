import pygame
from pygame.locals import *
import sys
import random
import time
import pygame.mixer
import imageio

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
game_over = False

FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("mago legal")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf_left = pygame.image.load("snowman_left.png")
        self.surf_right = pygame.image.load("snowman_right.png")
        self.surf = self.surf_right  # Inicialmente, carrega a imagem voltada para a direita
        self.rect = self.surf.get_rect()

        self.pos = vec((10, 360))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False
        self.score = 0
        self.direction = "right"  # Inicialmente, o personagem está voltado para a direita

    def move(self):
        self.acc = vec(0, 0.5)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
            # Altera a direção para "left" quando a tecla "left" é pressionada
            self.direction = "left"
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
            # Altera a direção para "right" quando a tecla "right" é pressionada
            self.direction = "right"

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    if hits[0].point:
                        hits[0].point = False
                        self.score += 1
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False

    def draw(self):
        if self.direction == "left":
            self.surf = self.surf_left
        elif self.direction == "right":
            self.surf = self.surf_right
        displaysurface.blit(self.surf, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, width=43, height=28):
        super().__init__()

        self.original_image = pygame.image.load("batleft.gif")
        self.surf = pygame.transform.scale(
            self.original_image, (width, height))
        self.rect = self.surf.get_rect()

        # Set the initial x position on either the left or right side of the screen
        if random.choice([True, False]):
            self.rect.left = 0
            self.speed = random.randint(1, 3)
        else:
            self.rect.right = WIDTH
            self.speed = random.randint(-3, -1)

        self.rect.centery = random.randint(0, HEIGHT - 30)

        self.point = True
        self.moving = True

    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving:
            self.rect.move_ip(self.speed, 0)
            if hits:
                global game_over
                game_over = True
                P1.pos.x += self.speed
            if self.speed > 0 and self.rect.left > WIDTH:
                self.kill()
            if self.speed < 0 and self.rect.right < 0:
                self.kill()

    def update_image(self):
        # Scale the image using the original dimensions
        self.surf = pygame.transform.scale(
            self.original_image, (self.rect.width, self.rect.height))


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.image = pygame.image.load("Coin.png")
        self.rect = self.image.get_rect()

        self.rect.topleft = pos

    def update(self):
        if self.rect.colliderect(P1.rect):
            P1.score += 5
            self.kill()


class Platform(pygame.sprite.Sprite):
    def __init__(self, width=0, height=18):
        super().__init__()

        if width == 0:
            width = random.randint(50, 120)

        self.image = pygame.image.load("platform.png")
        self.surf = pygame.transform.scale(self.image, (width, height))
        self.rect = self.surf.get_rect(
            center=(random.randint(0, WIDTH-10), random.randint(0, HEIGHT-30)))

        self.point = True
        self.moving = True
        self.speed = random.randint(-1, 1)

        if self.speed == 0:
            self.moving = False

    def generateCoin(self):
        if self.speed == 0:
            coins.add(Coin((self.rect.centerx, self.rect.centery - 50)))

    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving:
            self.rect.move_ip(self.speed, 0)
            if hits:
                P1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH


def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
        return False


def plat_gen():
    while len(platforms) < 6:
        width = random.randrange(50, 100)
        p = Platform()
        C = True

        while C:
            p = Platform()
            p.rect.center = (random.randrange(
                0, WIDTH - width), random.randrange(-50, 0))
            C = check(p, platforms)

        p.generateCoin()
        platforms.add(p)
        all_sprites.add(p)


all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()

PT1 = Platform(450, 80)

background = pygame.image.load("background.png")
PT1.rect = PT1.surf.get_rect(center=(WIDTH/2, HEIGHT - 10))
PT1.moving = False
PT1.point = False

P1 = Player()
E1 = Enemy()

all_sprites.add(PT1)
all_sprites.add(P1)
all_sprites.add(E1)
platforms.add(PT1)

for x in range(random.randint(4, 5)):
    C = True
    pl = Platform()
    while C:
        pl = Platform()
        C = check(pl, platforms)
    pl.generateCoin()
    platforms.add(pl)
    all_sprites.add(pl)

# Tempo inicial para o próximo spawn de inimigo
enemy_spawn_time = pygame.time.get_ticks() + random.randint(2000, 5000)
game_over = False

while not game_over:
    P1.update()
    E1.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                P1.cancel_jump()

    if pygame.sprite.spritecollideany(P1, enemies):
        game_over = True
        P1.vel.y = 0  # Adicione esta linha para parar o movimento vertical do jogador

    if P1.rect.top > HEIGHT:
        game_over = True

    if game_over:
        for entity in all_sprites:
            entity.kill()
        time.sleep(1)
        displaysurface.fill((255, 0, 0))
        pygame.display.update()
        time.sleep(1)
        pygame.quit()
        sys.exit()

    if P1.rect.top <= HEIGHT / 3:
        P1.pos.y += abs(P1.vel.y)
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()

        for coin in coins:
            coin.rect.y += abs(P1.vel.y)
            if coin.rect.top >= HEIGHT:
                coin.kill()

    if pygame.time.get_ticks() > enemy_spawn_time:
        enemy_spawn_time = pygame.time.get_ticks() + random.randint(2000, 5000)
        E = Enemy()
        all_sprites.add(E)
        enemies.add(E)  # Adicionar o objeto Enemy ao grupo de inimigos

    plat_gen()
    displaysurface.blit(background, (0, 0))
    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(P1.score), True, (123, 255, 0))
    displaysurface.blit(g, (WIDTH/2, 10))

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()

    for coin in coins:
        displaysurface.blit(coin.image, coin.rect)
        coin.update()

    P1.draw()

    pygame.display.update()
    FramePerSec.tick(FPS)
