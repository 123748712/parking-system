import serial
import pygame
import math
import app

# 시리얼 포트 설정
ser = serial.Serial('COM6', 9600, timeout=1)
# Pygame 초기화
pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arduino Radar")
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

# 색상 정의
GREEN = (98, 245, 31)
RED = (255, 10, 10)
BLACK = (0, 0, 0)

def draw_radar_base():
    center = (WIDTH // 2, HEIGHT - int(HEIGHT * 0.074))
    for r_factor in [0.9375, 0.73, 0.521, 0.313]:
        pygame.draw.arc(screen, GREEN, 
                        [center[0] - WIDTH * r_factor / 2, center[1] - WIDTH * r_factor / 2,
                         WIDTH * r_factor, WIDTH * r_factor],
                        math.pi, 2 * math.pi, 2)
    for angle in range(0, 181, 30):
        x = center[0] + WIDTH // 2 * math.cos(math.radians(angle))
        y = center[1] - WIDTH // 2 * math.sin(math.radians(angle))
        pygame.draw.line(screen, GREEN, center, (x, y), 2)

def draw_line(angle):
    center = (WIDTH // 2, HEIGHT - int(HEIGHT * 0.074))
    length = HEIGHT - int(HEIGHT * 0.12)
    x = center[0] + length * math.cos(math.radians(angle))
    y = center[1] - length * math.sin(math.radians(angle))
    pygame.draw.line(screen, GREEN, center, (x, y), 2)

def draw_object(angle, distance):
    if distance > 40:
        return
    center = (WIDTH // 2, HEIGHT - int(HEIGHT * 0.074))
    pix_distance = distance * ((HEIGHT - HEIGHT * 0.1666) * 0.025)
    x = center[0] + pix_distance * math.cos(math.radians(angle))
    y = center[1] - pix_distance * math.sin(math.radians(angle))
    pygame.draw.circle(screen, RED, (int(x), int(y)), 5)

def draw_text(angle, distance):
    status = "In Range" if distance <= 40 else "Out of Range"
    pygame.draw.rect(screen, BLACK, [0, HEIGHT - int(HEIGHT * 0.0648), WIDTH, HEIGHT])
    screen.blit(font.render(f"Angle: {angle}", True, GREEN), (WIDTH * 0.52, HEIGHT - 30))
    screen.blit(font.render(f"Distance: {distance} cm", True, GREEN), (WIDTH * 0.7, HEIGHT - 30))
    screen.blit(font.render(status, True, GREEN), (WIDTH * 0.3, HEIGHT - 30))

# 메인 루프
running = True
angle = 0
distance = 0

while running:
    screen.fill((0, 4))  # 모션 블러 효과
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if ser.in_waiting:
        try:
            data = ser.read_until(b'.').decode().strip('.')
            if ',' in data:
                angle_str, distance_str = data.split(',')
                angle = int(angle_str)
                distance = int(distance_str)
        except:
            pass

    draw_radar_base()
    draw_line(angle)
    draw_object(angle, distance)
    draw_text(angle, distance)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()