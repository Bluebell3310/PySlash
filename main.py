import pygame
import math
from collections import deque
from settings import *
from sprites import *
from computer_vision import Detector

class Game:
	def __init__(self):
		pygame.init()
		self.gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
		pygame.display.set_caption(TITLE)
		self.clock = pygame.time.Clock()
		self.running = True
		self.load_data()
		self.score_blue = 0
		self.score_green = 0
		self.round = 1
		self.font_name = pygame.font.match_font('arial')

	def load_data(self):
		self.slash_img = pygame.image.load("slash.png")
		self.slash_img = pygame.transform.scale(self.slash_img, (250, 63))
		self.sword_swing_sound = pygame.mixer.Sound("sword_swing.wav")

	def new(self):
		self.all_sprites = pygame.sprite.Group()
		self.detector_blue = Detector(0, "blue")
		self.detector_green = Detector(1, "green")
		self.pts_blue = deque(maxlen=10)
		self.pts_green = deque(maxlen=10)
		self.slashes_blue = []  # [point, angle, 0, True]
		self.slashes_green = []
		self.slash_duration = 10
		self.player_blue = Player(self, "blue")
		self.player_green = Player(self, "green")
		self.ready_blue = False
		self.ready_count_blue = 0
		self.ready_green = False
		self.ready_count_green = 0
		self.rounding = False
		self.ending = False
		self.ending_start_time = 0
		self.run()
	
	def run(self):
		self.playing = True
		while self.playing:
			self.clock.tick(FPS)
			if self.player_blue.die and self.player_green.die:
				self.draw()
				last_update = pygame.time.get_ticks()
				now = pygame.time.get_ticks()
				while now - last_update > 5000:
					now = pygame.time.get_ticks()
				self.round += 1
				self.new()
			elif self.player_blue.die:
				self.draw()
				self.score_green += 1
				self.round += 1
				last_update = pygame.time.get_ticks()
				now = pygame.time.get_ticks()
				while now - last_update > 5000:
					now = pygame.time.get_ticks()
				if self.score_green >= 2:
					self.playing = False
				else:
					self.new()
			elif self.player_green.die:
				self.draw()
				self.score_blue += 1
				self.round += 1
				last_update = pygame.time.get_ticks()
				now = pygame.time.get_ticks()
				while now - last_update > 5000:
					now = pygame.time.get_ticks()
				if self.score_blue >= 2:
					self.playing = False
				else:
					self.new()
			self.events()
			self.update()
			self.draw()
	
	def events(self):
        # Game Loop - events，按鍵事件
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				if self.playing:
					self.playing = False
				self.running = False

		if len(self.pts_blue) > 0 and not self.ready_blue and \
		   220 > self.pts_blue[0][0] > 180 and  480 > self.pts_blue[0][1] > 440:
			self.ready_count_blue += 1
			if self.ready_count_blue >= 51:
				self.ready_blue = True
		else:
			self.ready_count_blue = 0

		if len(self.pts_green) > 0 and not self.ready_green and \
		   620 > self.pts_green[0][0] > 580 and 480 > self.pts_green[0][1] > 440:
			self.ready_count_green += 1
			if self.ready_count_green >= 51:
				self.ready_green = True
		else:
			self.ready_count_green = 0

		if self.ready_blue and self.ready_green and not self.rounding and not self.ending:
			self.rounding = True
			self.round_start()


	def round_start(self):
		self.round_start_time = pygame.time.get_ticks()
		self.player_blue.current_frame = -1
		self.player_green.current_frame = -1
		self.player_blue.standing = False
		self.player_green.standing = False
		self.player_blue.pre_slashing = True
		self.player_green.pre_slashing = True
	
	def round_end(self):
		self.ending_start_time = pygame.time.get_ticks()
		self.ending = True
		self.player_blue.current_frame = -1
		self.player_green.current_frame = -1
		self.player_blue.slashing = False
		self.player_green.slashing = False
		self.player_blue.after_slashing = True
		self.player_green.after_slashing = True

	def update(self):
		self.all_sprites.update()
		pt = self.detector_blue.get_color_center()
		if pt != None:
			self.pts_blue.appendleft((pt[0], pt[1] + 300))
		pt = self.detector_green.get_color_center()
		if pt != None:
			self.pts_green.appendleft((pt[0] + 400, pt[1] + 300))
		if self.rounding:
			now = pygame.time.get_ticks()
			if now - self.round_start_time > 10000:
				self.rounding = False
				self.round_end()

	def draw(self):
		self.gameDisplay.fill(WHITE)
		self.draw_text(str(self.round), 45, BLACK, 400, 10)
		self.draw_text(str(self.score_blue), 30, BLUE, 320, 30)
		self.draw_text(str(self.score_green), 30, GREEN, 480, 30)
		self.all_sprites.draw(self.gameDisplay)
		pygame.draw.rect(self.gameDisplay, BLACK, (0, 300, 400, 621))
		pygame.draw.rect(self.gameDisplay, BLUE, (0, 300, 398, 621), 4)
		self.draw_text(str(len(self.slashes_blue)),30, WHITE, 25, 320)
		pygame.draw.rect(self.gameDisplay, BLACK, (400, 300, 400, 621))
		pygame.draw.rect(self.gameDisplay, GREEN, (401, 300, 398, 621), 4)
		self.draw_text(str(len(self.slashes_green)), 30, WHITE, 765, 320)
		if not self.ready_blue:
			pygame.draw.rect(self.gameDisplay, (255-self.ready_count_blue*5, 255-self.ready_count_blue*5, 255), (180, 440, 40, 40))
		if not self.ready_green:
			pygame.draw.rect(self.gameDisplay, (255-self.ready_count_green*5, 255, 255-self.ready_count_green*5), (580, 440, 40, 40))

		if self.rounding:
			self.draw_slashes()

		for i in range(1, len(self.pts_blue)):
			if self.pts_blue[i - 1] is None or self.pts_blue[i] is None:
				continue
			pygame.draw.line(self.gameDisplay, BLUE, self.pts_blue[i - 1], self.pts_blue[i] , 5)

		for i in range(1, len(self.pts_green)):
			if self.pts_green[i - 1] is None or self.pts_green[i] is None:
				continue
			pygame.draw.line(self.gameDisplay, GREEN, self.pts_green[i - 1], self.pts_green[i] , 5)

		if self.ending:
			now = pygame.time.get_ticks()
			if now - self.ending_start_time > 3000:
				if len(self.slashes_blue) > len(self.slashes_green):
					self.player_green.dead(self.slashes_blue)
				elif len(self.slashes_green) > len(self.slashes_blue):
					self.player_blue.dead(self.slashes_green)
				else:
					self.player_green.dead(self.slashes_blue)
					self.player_blue.dead(self.slashes_green)

		pygame.display.flip()

	def draw_slashes(self):
		for i in range(len(self.pts_blue)):
			if self.pts_blue[i] != None:
				if math.sqrt((self.pts_blue[0][0]-self.pts_blue[i][0])**2 + (self.pts_blue[0][1]-self.pts_blue[i][1])**2) > 250:
					angle = math.atan2(self.pts_blue[0][1] - self.pts_blue[i][1], self.pts_blue[0][0] - self.pts_blue[i][0]) / math.pi * 180 * -1
					point = (self.pts_blue[0][0] + (self.pts_blue[i][0] - self.pts_blue[0][0]) // 2, self.pts_blue[0][1] + (self.pts_blue[i][1] - self.pts_blue[0][1]) // 2) 
					self.slashes_blue.append( [point, angle, 0, True] )
					self.sword_swing_sound.play()
					for j in range(len(self.pts_blue)):
						self.pts_blue.pop()
					break
			else:
				break
		
		for i in range(len(self.pts_green)):
			if self.pts_green[i] != None:
				if math.sqrt((self.pts_green[0][0]-self.pts_green[i][0])**2 + (self.pts_green[0][1]-self.pts_green[i][1])**2) > 250:
					angle = math.atan2(self.pts_green[0][1] - self.pts_green[i][1], self.pts_green[0][0] - self.pts_green[i][0]) / math.pi * 180 * -1
					point = (self.pts_green[0][0] + (self.pts_green[i][0] - self.pts_green[0][0]) // 2, self.pts_green[0][1] + (self.pts_green[i][1] - self.pts_green[0][1]) // 2) 
					self.slashes_green.append( [point, angle, 0, True] )
					self.sword_swing_sound.play()
					for j in range(len(self.pts_green)):
						self.pts_green.pop()
					break
			else:
				break
		
		for i in range(len(self.slashes_blue)):
			if self.slashes_blue[i][2] > self.slash_duration:
				self.slashes_blue[i][3] = False
			else:
				self.update_slash(self.slashes_blue[i][0], self.slashes_blue[i][1])
				self.slashes_blue[i][2] += 1
		
		for i in range(len(self.slashes_green)):
			if self.slashes_green[i][2] > self.slash_duration:
				self.slashes_green[i][3] = False
			else:
				self.update_slash(self.slashes_green[i][0], self.slashes_green[i][1])
				self.slashes_green[i][2] += 1

	def update_slash(self, center, angle):
		rotated = pygame.transform.rotate(self.slash_img, angle)
		rect = rotated.get_rect()
		rect.center = center
		self.gameDisplay.blit(rotated, rect)
	
	def gameover(self):
		self.gameDisplay.fill(WHITE)
		if self.score_blue >= 2:
			self.draw_text("BLUE WIN!", 70, BLUE, 400, 270)
		elif self.score_green >= 2:
			self.draw_text("GREEN WIN!", 70, GREEN, 400, 270)
		pygame.display.flip()
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
	
	def draw_text(self, text, size, color, x, y):
		font = pygame.font.Font(self.font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.gameDisplay.blit(text_surface, text_rect)

game = Game()
while game.running:
	game.new()
	game.gameover()
	
pygame.quit()
quit()