import pygame
import sys

# Khởi tạo pygame
pygame.init()

# Tạo màn hình (window) màu đen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Draw Line Example")

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Nhập tọa độ start và end (có thể thay bằng input())
start = (100, 100)   # ví dụ
end = (700, 500)     # ví dụ

# Vòng lặp chính
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tô nền đen
    screen.fill(BLACK)

    # Vẽ đường thẳng màu trắng, độ dày 3
    pygame.draw.line(screen, WHITE, (155,-3), (249,185), 3)

    # Cập nhật màn hình
    pygame.display.flip()

# Thoát pygame
pygame.quit()
sys.exit()