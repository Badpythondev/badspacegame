import pygame
import sys
import random
import time
import json
import tkinter as tk
from tkinter import ttk
from classes import Button
pygame.init()
pygame.mixer.init()
Win_h = 800
Win_w = 800
fps = 60
scores_dict = {}
clock = pygame.time.Clock()
screen = pygame.display.set_mode((Win_h, Win_w))
pygame.display.set_caption("Space Shooter Game")
# Load images
with open("spaceassets\.settings\settings.json","r") as file:
    data=json.load(file)
settings_values=[]
highscore_values=[]
for obj in data["settings"]:
    settings_values.append(obj)
settings_values=settings_values[0]
for obj in data["highscores"]:
    highscore_values.append(obj)
highscore_values=highscore_values[0]
bg_img = pygame.image.load("spaceassets/background.png").convert()
spaceship_img = pygame.image.load("spaceassets/player.png").convert_alpha()
alien_img = pygame.image.load("spaceassets/alien.png").convert_alpha()
heart_img = pygame.image.load("spaceassets/heart.png").convert_alpha()
lost_heart_img = pygame.image.load("spaceassets/lostheart.png").convert_alpha()
bullets_img = pygame.image.load("spaceassets/bullet.png").convert_alpha()
healthup_img = pygame.image.load("spaceassets/healthup.png").convert_alpha()
atkup=pygame.image.load("spaceassets/atkup.png").convert_alpha()
icon=pygame.image.load("spaceassets/icon.png").convert_alpha()
button_restart=pygame.image.load("spaceassets/restart_button.png").convert_alpha()
button_quit=pygame.image.load("spaceassets/quit_button.png").convert_alpha()
endscreen=pygame.image.load("spaceassets/endscreen.png").convert_alpha()
button_settings=pygame.image.load("spaceassets/settings_button.png").convert_alpha()
button_continue=pygame.image.load("spaceassets/continue_button.png").convert_alpha()
music_playing = settings_values["music_playing"]
shoot_sound = settings_values["shoot_sound"]
endscreenvar = settings_values["endscreenvar"]
tips =settings_values["tips"]
pygame.display.set_icon(icon)
# Scale images
heart_img = pygame.transform.scale(heart_img, (33, 33))
lost_heart_img = pygame.transform.scale(lost_heart_img, (33, 33))
bullets_img = pygame.transform.scale(bullets_img, (50, 33))
pen_duration=6000
# Define sizes
SPACESHIP_WIDTH = 100
SPACESHIP_HEIGHT = 100
goleft=False
# Initialize variables
player_lives = 3
score = 0
bgy1, bgy2 = 0, -Win_h  # Initial positions for two background images
scrollspeed = 2
xspeed = 0
FIRE_DELAY = 250
last_bullet_time = pygame.time.get_ticks()
possible_spawn_location = [0, 100, 200, 300, 400, 500, 600, 700]
aliens = []
bullets_list = []
healthups = []
penups=[]
fire_rate=250
initial_player_lives = player_lives
autorun=False
font = pygame.font.Font("spaceassets/tnr.ttf", 40)
font2 = pygame.font.Font("spaceassets/tnr.ttf", 12)
spawn_rate=2
paused=False
strtbtn = Button(button_restart, 468, 672, 0.1)#image,x,y,scale
extbtn = Button(button_quit, 138, 672, 0.1)
settingbtn=Button(button_settings,208,554,0.2)
continuebtn=Button(button_continue,208,308,0.2)
startbtnwidth,extbtnwidth=strtbtn.width,extbtn.width
atkups=[]
loop=0
class PowerUp:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.picked_up = False
def draw_hearts(num_lives):
    for i in range(num_lives):
        screen.blit(heart_img, (i * 33, 0))
    for i in range(num_lives, initial_player_lives):
        screen.blit(lost_heart_img, (i * 33, 0))
def toggle_music():
    global music_playing , settings_values
    music_playing =settings_values['music_playing']= not music_playing
    update_settings()
def toggle_shoot():
    global shoot_sound, settings_values
    shoot_sound =settings_values["shoot_sound"]= not shoot_sound
    update_settings()
def random_powerup():
    if random.randint(0, 1000) == 1 :
        x = random.choice(possible_spawn_location)
        powerup = PowerUp(x, 0, healthup_img)
        healthups.append(powerup)

def updatehealthpick():
    global score, player_lives, initial_player_lives, healthups, healthup_img, spaceship_img
    for health in healthups:
        if not health.picked_up:  # Access the 'picked_up' property directly
            health.y += scrollspeed
            healthup_rect = pygame.Rect(health.x, health.y, healthup_img.get_width(), healthup_img.get_height())
            spaceship_rect = spaceship_img.get_rect().move(spaceshipx, 600)
            if healthup_rect.colliderect(spaceship_rect):
                if player_lives < 10 and initial_player_lives < 10:
                    initial_player_lives+=1
                    player_lives += 1
                    score += 1
                elif player_lives <= initial_player_lives:
                    player_lives = player_lives + 1
                    score += 2
                elif initial_player_lives >= 10 and player_lives >= 10:
                    score += 5
                health.picked_up = True
        else:
            healthups.remove(health)
        if health.y<=0:
            healthups.remove(health)
def draw_score():
    text = font.render("Score: " + str(score), True, (0, 255, 100))
    text_widith=text.get_width()
    screen.blit(text, (400-(text_widith/2), 0))
def continue_playing():
    pygame.mixer.music.play()
def handle_input():
    global xspeed, space_held
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                xspeed = -6
            elif event.key == pygame.K_RIGHT:
                xspeed = 6
            elif event.key == pygame.K_SPACE:
                space_held = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                xspeed = 0
            elif event.key == pygame.K_SPACE:
                space_held = False


def update_spaceship_position():
    global spaceshipx , goleft
    spaceshipx += xspeed
    if spaceshipx < 0:
        spaceshipx = 0
    elif spaceshipx > Win_w - SPACESHIP_HEIGHT:
        spaceshipx = Win_w - SPACESHIP_HEIGHT
    if autorun and goleft:
        spaceshipx-=5
        if spaceshipx==0:
            goleft=False
    elif autorun and not goleft:
        spaceshipx+=5
        if spaceshipx ==700:
            goleft=True
    
def spawn_aliens():
    if random.randint(0, 100) < spawn_rate:
        aliens.append({"x": random.choice(possible_spawn_location), "y": 0, "alive": True})

def handle_bullet_collision():
    global score
    for bullet in bullets_list:
        bullet_rect = pygame.Rect(bullet["x"], bullet["y"], bullets_img.get_width(), bullets_img.get_height())
        for alien in aliens:
            if alien["alive"]:
                alien_rect = pygame.Rect(alien["x"], alien["y"], alien_img.get_width(), alien_img.get_height())
                if bullet_rect.colliderect(alien_rect):
                    if not bullet["infpen"]:
                        bullet["y"] = -100  # Move the bullet off-screen to remove it
                    alien["alive"] = False
                    score += 1

def update_aliens():
    global score, player_lives
    for alien in aliens:
        if alien["alive"]:
            alien["y"] += scrollspeed

            # Check if the alien touches the ground
            if alien["y"] >= Win_h:
                alien["alive"] = False
                score += 1
                player_lives -= 1

            # Check for collision with the spaceship
            spaceship_rect = pygame.Rect(spaceshipx, 600, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
            alien_rect = pygame.Rect(alien["x"], alien["y"], alien_img.get_width(), alien_img.get_height())
            if alien_rect.colliderect(spaceship_rect):
                alien["alive"] = False
                player_lives -= 1
                score += 1
def show_tips():
    global tips , settings_values
    tips=settings_values["tips"]= not tips
    update_settings()
def update_settings():
    global data, settings_values, highscore_values
    data = {
        "settings": [settings_values],
        "highscores": [highscore_values]
    }
    with open("spaceassets/.settings/settings.json", "w") as jsonfilew:
        json.dump(data,jsonfilew, indent=4)
def defaultsettings():
    global settings_values
    settings_values = {
        "music_playing": True,
        "shoot_sound": True,
        "endscreenvar": True,
        "tips": True
    }
    update_settings()
def handle_bullet_shooting():
    global last_bullet_time, loop
    if space_held:
        current_time = pygame.time.get_ticks()
        if current_time - last_bullet_time >= fire_rate:
            bullets_list.append({"x": spaceshipx + SPACESHIP_WIDTH // 2 - bullets_img.get_width() // 2, "y": 600, "infpen": False})
            last_bullet_time = current_time
            if shoot_sound:
                loop+=1
                if (loop % 2)==0:
                    if (loop % 2)==0 :
                        pygame.mixer.music.load("spaceassets/laser1.mp3")
                    else:
                        pygame.mixer.music.load("spaceassets/laser2.mp3")
                    pygame.mixer.music.play()

def remove_dead_aliens():
    global aliens
    aliens = [alien for alien in aliens if alien["y"] < Win_h or alien["alive"]]

def draw_objects():
    for bullet in bullets_list:
        bullet["y"] -= 5  # Move the bullets upwards
        screen.blit(bullets_img, (bullet["x"], bullet["y"]))
        if bullet["y"]<=0:
            bullets_list.remove(bullet)
    for alien in aliens:
        if alien["alive"]:
            screen.blit(alien_img, (alien["x"], alien["y"]))

    for health in healthups:
        if not health.picked_up:
            screen.blit(healthup_img, (health.x, health.y))  # Use dot notation to access properties
    spaceship_rect = spaceship_img.get_rect().move(spaceshipx, 600)
    screen.blit(spaceship_img, spaceship_rect)

def check_game_over():
    global running, score, player_lives, initial_player_lives, spaceshipx, space_held, autorun,xspeed
    if player_lives <= 0:
        


        while not extbtn.pressed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
            screen.fill((255, 0, 0))
            text = font.render("Score: " + str(score), True, (0, 0, 0))
            screen.blit(text, (400, 0))
            draw_hearts(player_lives)
            extbtn.draw(screen)
            strtbtn.draw(screen)
            pygame.display.update()
            if extbtn.pressed and not strtbtn.pressed:
                running=False
                break
            if strtbtn.pressed:
                
                player_lives = 3
                initial_player_lives=3
                score = 0
                strtbtn.pressed=False
                extbtn.pressed=False
                aliens.clear()
                bullets_list.clear()
                spaceshipx=400-(spaceship_img.get_width()/2)
                autorun=False
                space_held=False
                xspeed=0
                screen.fill((0,0,0))
                text=font.render("starting in 3",True,(255,255,255))
                screen.blit(text, (400-(text.get_width()/2), 400))
                pygame.display.update()
                time.sleep(1)
                screen.fill((0,0,0))
                text=font.render("starting in 2",True,(255,255,255))
                screen.blit(text, (400-(text.get_width()/2), 400))
                pygame.display.update()
                time.sleep(1)
                screen.fill((0,0,0))
                text=font.render("starting in 1",True,(255,255,255))
                screen.blit(text, (400-(text.get_width()/2), 400))
                pygame.display.update()
                time.sleep(1)
                break
def endscreentoggle():
    global endscreenvar , settings_values
    endscreenvar=settings_values["endscreenvar"]=not endscreenvar
    update_settings()
def update_bullet_position():
    for bullet in bullets_list:
        bullet["y"] -= 5  # Move the bullets upwards
        if bullet["y"] <= 0:
            bullets_list.remove(bullet)
def toggle_pause():
    global paused
    paused = not paused
running = True
space_held = True
spaceshipx = 400
atkup_duration = 0
def draw_powerups():
    for atk in atkups:
        if not atk.picked_up:
            screen.blit(atk.image, (atk.x, atk.y))
def update_settings_in_loop():
    global tips, endscreenvar, shoot_sound, music_playing
    tips=settings_values["tips"]
    endscreenvar=settings_values["endscreenvar"]
    shoot_sound=settings_values["shoot_sound"]
    music_playing=settings_values["music_playing"]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key==pygame.K_a:
                xspeed = -5
                autorun = False
            elif event.key == pygame.K_RIGHT or event.key==pygame.K_d:
                xspeed = 5
                autorun = False
            elif event.key == pygame.K_SPACE:
                space_held = True
            elif event.key == pygame.K_q:
                player_lives = 0
            elif event.key == pygame.K_z and autorun:
                autorun = False
                scrollspeed = 2
            elif event.key == pygame.K_z and not autorun:
                autorun = True
                scrollspeed = 1
            elif event.key == pygame.K_x and not space_held:
                space_held = True
            elif event.key == pygame.K_x and space_held:
                space_held = False
            elif event.key == pygame.K_p:
                toggle_pause()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                xspeed = 0
            elif event.key == pygame.K_SPACE:
                space_held = False
    
    if not paused:
        update_spaceship_position()
        spawn_aliens()
        handle_bullet_shooting()
        update_aliens()
        handle_bullet_collision()
        remove_dead_aliens()
        random_powerup()
        updatehealthpick()
        draw_powerups()
        if atkup_duration > 0:
            atkup_duration -= clock.get_time()

            if atkup_duration <= 0:
                fire_rate = 250 
        if spawn_rate>15:
           spawn_rate += 0.01  # Increase spawn rate slightly per frame
        if FIRE_DELAY > 50:
            FIRE_DELAY -= 0.01
            fire_rate=FIRE_DELAY
        # Scroll the background
        bgy1 += scrollspeed
        bgy2 += scrollspeed
        # Reset the positions when one image moves out of the screen
        if bgy1 >= Win_h:
            bgy1 = -Win_h
        if bgy2 >= Win_h:
            bgy2 = -Win_h
        # Draw elements
        screen.blit(bg_img, (0, bgy1))
        screen.blit(bg_img, (0, bgy2))
        draw_objects()

        draw_hearts(player_lives)
        draw_score()
        # Update the position of the bullets
        update_bullet_position()
        if tips:
            helptext=font2.render("A/leftarrow=go left, D/rightarrow=go right, z=game is played automaticly x=autofire,p=pause",True,(255,255,255))
            screen.blit(helptext,(400-(helptext.get_width()/2),770-(helptext.get_height()/2)))
    else:
        screen.fill("darkred")
        continuebtn.draw(screen)
        settingbtn.draw(screen)
        text=font.render("Paused",True,(255,255,255))
        screen.blit(text, (400-(text.get_width()/2), text.get_height()+30))
        if continuebtn.pressed and not settingbtn.pressed:
            paused=False
        if settingbtn.pressed:
            settings_window = tk.Tk()
            settings_window.title("Settings")
            pygame.mixer.music.pause()
            # Add a label to indicate the purpose of the toggle
            label1 = tk.Label(settings_window, text="Toggle SFX:")
            label1.pack()

            # Create a Checkbutton (toggle) for music
            music_toggle = ttk.Checkbutton(settings_window, text="General Music", variable=tk.BooleanVar(value=music_playing), command=toggle_music)
            shoot_toggle= ttk.Checkbutton(settings_window,text="Shooting SFX",variable=tk.BooleanVar(value=shoot_sound), command=toggle_shoot)
            label2 = tk.Label(settings_window, text="Misc")
            credits_toggle= ttk.Checkbutton(settings_window,text="Credits",variable=tk.BooleanVar(value=endscreenvar), command=endscreentoggle)
            tips_toggle= ttk.Checkbutton(settings_window,text="Tips",variable=tk.BooleanVar(value=tips), command=show_tips)
            button_default=tk.Button(settings_window,text="Default values",command=defaultsettings)
            music_toggle.pack()
            shoot_toggle.pack()
            label2.pack()
            credits_toggle.pack()
            tips_toggle.pack()
            button_default.pack()
            # Add this to display the settings window
            settings_window.geometry("150x150")
            settings_window.mainloop()
    update_settings_in_loop()
    check_game_over()
    pygame.display.update()
    clock.tick(fps)
if not running and endscreenvar==True:
    screen.blit(endscreen,(0,0))
    if music_playing:
        pygame.mixer.music.load("spaceassets/trumpet.mp3")
        pygame.mixer.music.play()
        pygame.display.update()
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)
    else :
        pygame.display.update()
        time.sleep(6)
pygame.quit()
sys.exit()