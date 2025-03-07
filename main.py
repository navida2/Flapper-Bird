import pygame
from pygame.locals import *
import random
import json

clock = pygame.time.Clock()
fps = 60
pygame.init()


screen_width = 864
screen_height = 936

font = pygame.font.SysFont('Bauhaus 92', 60)
white = (255, 255, 255)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')
bg = pygame.image.load('bg.png')
ground_image = pygame.image.load('ground.png')
button_image = pygame.image.load('restart.png')
scroll = 0
scroll_speed = 4
flying = False
run = True
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.velocity = 0
        self.clicked = False
    
    def update(self):
        if flying:
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.velocity)
        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.velocity = -10
                self.clicked = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index],  -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap) / 2]
        if position == -1:
            self.rect.topleft = [x, y + (int(pipe_gap) / 2)]
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, img):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.topleft = (x,y)
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.img, (self.rect.x, self.rect.y))
        return action
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100,int(screen_height / 2))
bird_group.add(flappy)
button = Button(screen_width / 2 - 50, screen_height /2 -100, button_image )
while run:
    clock.tick(fps)
    screen.blit(bg, (0,0))
    pipe_group.draw(screen)
    
    bird_group.draw(screen)
    bird_group.update()

    screen.blit(ground_image, (scroll,768))
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
             if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                 score += 1
                 pass_pipe = False
    draw_text(str(score), font, white, int(screen_width)/ 2, 20)
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    if flappy.rect.bottom >= 768:
        game_over = True
        flying =False
    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width,int(screen_height / 2) +pipe_height, -1)
            top_pipe= Pipe(screen_width,int(screen_height / 2) +pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        scroll -= scroll_speed
        if abs(scroll) > 35:
            scroll = 0
        pipe_group.update()

    if game_over:
        scores = json.load(open('score.json'))
        #draw_text(f"Highscore:{scores["highscore"]} ")
        if scores["highscore"] < score:
            with open('score.json', 'w') as f:
                json.dump({"highscore": score}, f)
        draw_text(f"Highscore:{scores["highscore"]}",font, white, 100, screen_width/2)

        if button.draw():
            game_over = False
            score = reset_game()
            flappy.index = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True
    pygame.display.update()
pygame.quit()