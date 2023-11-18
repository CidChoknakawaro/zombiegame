import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
PLAYER_SPEED = 5
ZOMBIE_SPEED = 2
BULLET_SPEED = 10
MAX_AMMO = 30

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Display Surface
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Achi")

# Player Setup
player = pygame.Rect(WIDTH // 2 - 25, HEIGHT // 2 - 25, 50, 50)
player_ammo = MAX_AMMO

# Ammo pack Setup
ammo_packs = []
for _ in range(5):
    ammo_pack = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
    ammo_packs.append(ammo_pack)

# Zombie Setup
def generate_zombies(num_zombies):
    zombies = []
    for _ in range(num_zombies):
        zombie = pygame.Rect(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50), 50, 50)
        zombies.append(zombie)
    return zombies

level = 1
zombies = generate_zombies(level * 5)

# Bullets Setup
bullets = []

# Score
score = 0

# Font
font = pygame.font.Font(None, 36)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
YOU_WIN = 3
game_state = MENU

# "Game over, Try Again" text
game_over_text = font.render("Game Over", True, WHITE)
try_again_text = font.render("Try Again", True, WHITE)

# "You Win!, Next level" text
you_win_text = font.render("You Win!", True, WHITE)
next_level_text = font.render("Next Level", True, WHITE)

# Player Sprite
player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (100, 100))

# Bullet Sprite
bullet_image = pygame.image.load('bullet.png')
bullet_image = pygame.transform.scale(bullet_image, (20, 20))

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, angle, image):
        super(Bullet, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)
        self.angle = angle

    def update(self):
        # Moving the bullet
        self.rect.x += BULLET_SPEED * math.cos(self.angle)
        self.rect.y += BULLET_SPEED * math.sin(self.angle)

# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_state == MENU:
        # Menu screen
        screen.fill((0, 0, 0))
        start_text = font.render("Click to Start", True, WHITE)
        screen.blit(start_text, (WIDTH // 2 - 80, HEIGHT // 2 - 18))

        if event.type == pygame.MOUSEBUTTONDOWN:
            game_state = PLAYING

    elif game_state == PLAYING:
        # Move the player
        keys = pygame.key.get_pressed()

        # Calculate the new position
        new_x = player.x
        new_y = player.y

        if keys[pygame.K_w]:
            new_y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            new_y += PLAYER_SPEED
        if keys[pygame.K_a]:
            new_x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            new_x += PLAYER_SPEED

        # Screen boundaries
        if 0 <= new_x <= WIDTH - player.width and 0 <= new_y <= HEIGHT - player.height:
            # Update the player's position
            player.x = new_x
            player.y = new_y

        # Get player position
        player_center = (player.x + player.width // 2, player.y + player.height // 2)

        # Shoot bullets
        if event.type == pygame.MOUSEBUTTONDOWN and player_ammo > 0:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(mouse_y - player_center[1], mouse_x - player_center[0])
                bullet = Bullet(player.centerx, player.centery, angle, bullet_image)
                bullets.append(bullet)
                player_ammo -= 1

        # Move bullets
        for bullet in bullets:
            bullet.update()

        # Move zombies towards the player
        for zombie in zombies:
            zombie_center = (zombie.x + zombie.width // 2, zombie.y + zombie.height // 2)
            angle = math.atan2(player_center[1] - zombie_center[1], player_center[0] - zombie_center[0])
            zombie.x += ZOMBIE_SPEED * math.cos(angle)
            zombie.y += ZOMBIE_SPEED * math.sin(angle)

        # Bullet collision with zombies
        for bullet in bullets[:]:
            for zombie in zombies[:]:
                if bullet.rect.colliderect(zombie):
                    bullets.remove(bullet)
                    zombies.remove(zombie)
                    score += 1

        # Player collision with zombies
        for zombie in zombies[:]:
            if player.colliderect(zombie):
                game_state = GAME_OVER

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw player, zombies, and bullets
        screen.blit(player_image, player.topleft)
        for zombie in zombies:
            pygame.draw.rect(screen, RED, zombie)
        for bullet in bullets:
            screen.blit(bullet.image, bullet.rect.topleft)

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw ammo packs
        for ammo_pack in ammo_packs:
            pygame.draw.rect(screen, YELLOW, ammo_pack)

        # Draw ammo count
        ammo_text = font.render(f"Ammo: {player_ammo}/{MAX_AMMO}", True, WHITE)
        screen.blit(ammo_text, (WIDTH - 150, 10))

        # All zombies are defeated, "You Win" screen
        if not zombies:
            game_state = YOU_WIN

        # Game over
        if player_ammo == 0:
            game_state = GAME_OVER

        # Collecting ammo packs
        for ammo_pack in ammo_packs[:]:
            if player.colliderect(ammo_pack):
                ammo_packs.remove(ammo_pack)
                player_ammo = min(MAX_AMMO, player_ammo + 10)

        # Generate new ammo packs
        if len(ammo_packs) < 5:
            new_ammo_pack = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
            ammo_packs.append(new_ammo_pack)

    elif game_state == GAME_OVER:
        screen.fill((0, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 18))
        screen.blit(try_again_text, (WIDTH // 2 - 80, HEIGHT // 2 + 18))

        if event.type == pygame.MOUSEBUTTONDOWN:
            game_state = PLAYING
            level = 1
            zombies = generate_zombies(level * 5)
            bullets = []
            score = 0
            player_ammo = MAX_AMMO

    elif game_state == YOU_WIN:
        screen.fill((0, 0, 0))
        screen.blit(you_win_text, (WIDTH // 2 - 60, HEIGHT // 2 - 18))
        screen.blit(next_level_text, (WIDTH // 2 - 80, HEIGHT // 2 + 18))

        if event.type == pygame.MOUSEBUTTONDOWN:
            level += 1
            zombies = generate_zombies(level * 5)
            game_state = PLAYING
            player_ammo = MAX_AMMO

    # Update the display
    pygame.display.flip()

    # Limit frames per second
    pygame.time.Clock().tick(60)