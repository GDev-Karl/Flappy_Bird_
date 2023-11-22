import pygame
from pygame.locals import *
import random

clock = pygame.time.Clock()
fps = 60

pygame.init()

w = 600
h = 700
size = (w, h)
run = True

ecran = pygame.display.set_mode(size) 
pygame.display.set_caption("Flappy_Bird")

#variables du jeu 
defilement_sol = 0
vitesse_defilement = 4
score = 0

ecart_vetical_tube = 250
frequence_tube = 900 #en milliseconde
temps_actuel = pygame.time.get_ticks()
temps_dernier_tube = pygame.time.get_ticks() - frequence_tube

fly = False  #variable permettant de savoir si l'oiseau vole ou pas 
game_over = False
passe_tube = False
collide = False #variable permettant de savoir s'il ya déjà eu collision 

font = pygame.font.SysFont("cambria", 60, True) #police
WHITE = (255, 255, 255) #couleur

#l'arrière plan
fond = pygame.image.load("img/bg.png")
fond  = pygame.transform.scale(fond, (w, 550))

#boutton restart
restart_img = pygame.image.load("img/restart.png")

#sol
sol = pygame.image.load("img/ground.png")
sol = pygame.transform.scale(sol, (w+20, 180))

#son
flap_sound = pygame.mixer.Sound("sound/sfx_wing.wav")
die_sound = pygame.mixer.Sound("sound/sfx_die.wav")
hit_sound = pygame.mixer.Sound("sound/sfx_hit.wav")
point_sound = pygame.mixer.Sound("sound/sfx_point.wav")


def draw_score(text, font, color, x, y):
    img = font.render(text, True, color)
    ecran.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(h / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        "gère l'apparition des sprites de l'oiseau ainsi que de leur animation"
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.cpt = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0 #vélocité
        self.click = False

    def update(self):
        """gestion des mouvements des images""" 
        #s'il vole on gère la gravité
        if fly:
            # Gestion de la gavité
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 550:
                self.rect.y += int(self.vel)    
                #print(self.rect.y)

        if not game_over:
            #Gestion du saut
            if pygame.mouse.get_pressed()[0] == 1 and not self.click:
                self.vel = -6

            #Chargement des images
            self.cpt += 1
            temps_recharge = 5

            if self.cpt > temps_recharge:
                self.cpt = 0
                self.index += 1
                if  self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            
            #rotation de l'oiseau
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        # position 1 pour le haut, et -1 pour le bas
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(ecart_vetical_tube / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(ecart_vetical_tube / 2)]

    def update(self):
        self.rect.x -= vitesse_defilement + 1
        if self.rect.right < 0:
            self.kill()

class Button():

    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        
        action = False
        #position de la souris
        pos = pygame.mouse.get_pos()

        #verification des collisions entre le curseur et l'image
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #affiche le boutton restart
        ecran.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(h / 2))
bird_group.add(flappy)

restart_button = Button(w // 2 - 50, h// 2 - 100, restart_img)

while run:

    clock.tick(fps) #mise a jour du temps

    #Chargement de l'arrière plan
    ecran.blit(fond, (0, 0))

    pipe_group.draw(ecran)
    bird_group.draw(ecran)
    bird_group.update()

    #chagement du sol
    ecran.blit(sol, (defilement_sol, 550))

    #calcul du score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and passe_tube == False:
            passe_tube = True
        if passe_tube:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                point_sound.play() 
                passe_tube = False
                ecart_vetical_tube -= 10
    draw_score(str(score), font, WHITE, int(w / 2), 60)

    #verification des collisions
    if not collide:
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
            hit_sound.play()
            die_sound.play()
            collide = True

    if not game_over and fly:
    
        #generation de nouveax tubes
        temps_tube_actuel = pygame.time.get_ticks()
        if temps_tube_actuel - temps_dernier_tube > frequence_tube:
            largeur_tube = random.randint(-100, 100)
            tube_haut = Pipe(w, int((h-180) / 2) + largeur_tube, 1)
            tube_bas = Pipe(w, int((h-180) / 2) + largeur_tube, -1)
            pipe_group.add(tube_haut)
            pipe_group.add(tube_bas)
            temps_dernier_tube = temps_tube_actuel

        defilement_sol -= vitesse_defilement
        if abs(defilement_sol) > 35: #si a valeur absolue du defilement est > 35 pixels on le remet à 0
            defilement_sol = 0
        pipe_group.update()

    #verifie si l'oiseau a toucher le sol
    if flappy.rect.bottom >= 550:
        game_over = True
        fly = False

    #verification de la fin du jeu pour recommencer
    if game_over:
        if restart_button.draw() == True:
            game_over = False
            collide = False
            ecart_vetical_tube = 250
            score = reset_game()

    #gestion des evenements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if fly == False:
                fly = True
            if not game_over:
                flap_sound.play()

    pygame.display.update()

pygame.quit()
