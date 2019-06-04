import pygame
import math
from computer_vision import Detector
from collections import deque

pygame.init()

display_width = 400
display_height = 321
BLACK = (0, 0, 0)
GREEN = (0, 255, 255)

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Slash!')
clock = pygame.time.Clock()

slash_img = pygame.image.load("slash.png")
slash_img = pygame.transform.scale(slash_img, (300, 75))
detector = Detector(0)

pts = deque(maxlen=10)
slash_duration = 10
slashes = []

def quitgame():
    pygame.quit()
    quit()
	
def update_slash(center, angle):
	rotated = pygame.transform.rotate(slash_img, angle)
	rect = rotated.get_rect()
	rect.center = center
	gameDisplay.blit(rotated, rect)
	
def run():
	gameDisplay.fill(BLACK)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quitgame()
	
	pts.appendleft(detector.get_color_center("blue"))

	for i in range(1, len(pts)):
		if pts[i - 1] is None or pts[i] is None:
			continue
		if i <= 4:
			pygame.draw.line(gameDisplay, GREEN, pts[i - 1], pts[i] , 5)
	
	for i in range(len(pts)):
		if pts[i] != None:
			if math.sqrt((pts[0][0]-pts[i][0])**2 + (pts[0][1]-pts[i][1])**2) > 200:
				angle = math.atan2(pts[0][1] - pts[i][1], pts[0][0] - pts[i][0]) / math.pi * 180 * -1
				point = (pts[0][0] + (pts[i][0] - pts[0][0]) // 2, pts[0][1] + (pts[i][1] - pts[0][1]) // 2) 
				slashes.append( [point, angle, 0] )
				for j in range(len(pts)):
					pts.pop()
				break
		else:
			break
	
	slashes_len = len(slashes)
	i = 0
	while i < slashes_len:
		if slashes[i][2] > slash_duration:
			slashes.pop(i)
			i -= 1
			slashes_len -= 1
		else:
			update_slash(slashes[i][0], slashes[i][1])
			slashes[i][2] += 1
		i += 1
	
	pygame.display.update()
	clock.tick(60)
