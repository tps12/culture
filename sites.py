from math import sqrt
import random

import pygame
from pygame.locals import *

class Dimension:
    def __init__(self, color, index = None, shape = None):
        self.color = color
        self.index = index
        self.shape = shape

class Simulation:

    WIDTH = 800
    HEIGHT = 600

    LINE = 4
    HIST_WIDTH = 10

    DRAW_FRAMES = 1000
    LIMIT = 0

    DELTA = 0.25
    EPSILON = 0.001

    THRESHOLD = 1

    CONFORMITY = Dimension((255,255,0), 0, lambda x: 1 - 2 * pow(x - 1,2))
    CONVICTION = Dimension((0,255,255), 1, lambda x: x)

    DIMENSIONS = [CONFORMITY, CONVICTION] + [Dimension((0,255,0))
                                             for i in range(13)]

    KUNG_FU_INDEX = len(DIMENSIONS)-1

    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.grid_size = min(self.WIDTH/2/(self.dimensions[0] + 1),
                             self.HEIGHT/(self.dimensions[1] + 1))
        self.bg_rect = pygame.Rect(max(0, (self.WIDTH/2 - (self.dimensions[0] + 1) * self.grid_size) / 2),
                                   max(0, (self.HEIGHT - (self.dimensions[1] + 1) * self.grid_size) / 2),
                                   (self.dimensions[0] + 1) * self.grid_size,
                                   (self.dimensions[1] + 1) * self.grid_size)
        self.hist_rect = self.bg_rect.move(self.bg_rect.width,0)

        def uniform():
            return random.random()
        def gaussian():
            return max(0, min(1, random.gauss(0.5, 0.125)))

        self.sites = [[[uniform()
                        for d in self.DIMENSIONS]
                       for y in range(self.dimensions[1])]
                      for x in range(self.dimensions[0])]

        self.selection = None

    def background(self, screen, rect):
        screen.fill((255,255,255), rect)

    def hist(self, screen):
        height = self.hist_rect.height / len(self.DIMENSIONS)
        sites = self.dimensions[0] * self.dimensions[1]
        
        for i in range(len(self.DIMENSIONS)):
            color = self.DIMENSIONS[i].color
            counts = [0 for n in range(self.hist_rect.width/self.HIST_WIDTH)]
            for value in [self.sites[x][y][i]
                          for y in range(self.dimensions[1])
                          for x in range(self.dimensions[0])]:
                counts[int(value * len(counts))
                       if value < 1
                       else len(counts)-1] += 1
            for j in range(len(counts)):
                if counts[j] > 0:
                    bar = height * counts[j]/float(sites)
                    rect = pygame.Rect(self.hist_rect.left + j*self.HIST_WIDTH,
                                       self.hist_rect.top + (i+1)*height - bar,
                                       self.HIST_WIDTH, bar)
                    screen.fill(color, rect)
                    if self.selection != None:
                        sel = self.selection
                        value = self.sites[sel[0]][sel[1]][i]
                        if ((value < 1 and j == int(value * len(counts))) or
                            value == 1 and j == len(counts)-1):
                            pygame.draw.rect(screen, (0,0,255),
                                             rect.inflate(4,4), 1)

    def similarity(self, p1, p2):
        d = sqrt(sum([(c1-c2)*(c1-c2) for c1, c2 in zip(p1, p2)]))/sqrt(len(p1))
        return 0 if d > self.THRESHOLD else 1 - d
    
    def color(self, p1, p2):
        gray = 255 - int(self.similarity(p1, p2) * 255)
        return (gray, gray, gray)

    def lines(self, screen):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                start = (self.bg_rect.left + (x+1) * self.grid_size,
                         self.bg_rect.top + (y+1) * self.grid_size)
                if x < self.dimensions[0] - 1:
                    end = (start[0] + self.grid_size, start[1])
                    color = self.color(self.sites[x][y], self.sites[x+1][y])
                    pygame.draw.line(screen, color, start, end, self.LINE)
                if y < self.dimensions[1] - 1:
                    end = (start[0], start[1] + self.grid_size)
                    color = self.color(self.sites[x][y], self.sites[x][y+1])
                    pygame.draw.line(screen, color, start, end, self.LINE)
                    
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                pygame.draw.circle(screen, (0,0,0),
                                   (self.bg_rect.left + (x+1) * self.grid_size,
                                    self.bg_rect.top + (y+1) * self.grid_size),
                                   self.LINE)

        if self.selection != None:
            pygame.draw.circle(screen, (0,0,255),
                               (self.bg_rect.left + (self.selection[0]+1) * self.grid_size,
                                self.bg_rect.top + (self.selection[1]+1) * self.grid_size),
                               self.LINE + 2, 1)

    def random_site(self):
        return (random.randint(0, len(self.sites)-1),
                random.randint(0, len(self.sites[0])-1))

    def random_neighbor(self, site):
        x,y = site
        neighbors = []
        if x > 0:
            neighbors.append((x-1,y))
        if x < len(self.sites)-1:
            neighbors.append((x+1,y))
        if y > 0:
            neighbors.append((x,y-1))
        if y < len(self.sites[0])-1:
            neighbors.append((x,y+1))
        return random.sample(neighbors, 1)[0]

    def sway(self, active, neighb, index):
        a, n = active[index], neighb[index]
        d = a-n
        sign = 1
        if d < 0:
            d = -d
        else:
            sign = -1
        if d > self.EPSILON:
            if d > self.DELTA:
                d = self.DELTA
            delta = max(0, min(d, random.gauss(d/2, d/8)))
            if self.CONFORMITY in self.DIMENSIONS:
                delta *= self.CONFORMITY.shape(active[self.CONFORMITY.index])
            active[index] = max(0, min(1, a + sign * delta))
        else:
            active[index] = n

    def mill(self, active, index):
        delta = max(-self.DELTA, min(self.DELTA, random.gauss(0, self.DELTA/4)))
        if self.CONVICTION in self.DIMENSIONS:
            delta *= (1 - self.CONVICTION.shape(active[self.CONVICTION.index]))
        active[index] = max(0, min(1, active[index] + delta))

    def interact(self, active, neighb):
        i = max(range(len(active)), key=lambda i: abs(active[i] - neighb[i]))
        if active[i] != neighb[i]:
            self.sway(active, neighb, i)

    def try_event(self):
        active = self.random_site()
        neighb = self.random_neighbor(active)
        active_site = self.sites[active[0]][active[1]]
        neighb_site = self.sites[neighb[0]][neighb[1]]
        if random.random() < self.similarity(active_site, neighb_site):
            self.interact(active_site, neighb_site)
            if (0 <= self.KUNG_FU_INDEX < len(active_site) and
                active_site[self.KUNG_FU_INDEX] > 1):
                exit()
        else:
            self.mill(active_site, random.randint(0, len(active_site)-1))
    
    def run(self):
        pygame.init()

        screen = pygame.display.set_mode((self.WIDTH,self.HEIGHT), HWSURFACE)
        pygame.display.set_caption('Sites')

        done = False
        n = 0
        steps = 0
        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        done = True
                elif event.type == MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    edge = self.bg_rect.topleft
                    coords = [int((pos[i] - edge[i])/float(self.grid_size) - 0.5)
                              for i in range(2)]
                    if (0 <= coords[0] < self.dimensions[0] and
                        0 <= coords[1] < self.dimensions[1]):
                        self.selection = coords if self.selection != coords else None

            if self.LIMIT == 0 or steps < self.LIMIT:
                self.try_event()
                steps += 1

            n += 1
            if n > self.DRAW_FRAMES:

                for rect in [self.bg_rect, self.hist_rect]:
                    self.background(screen, rect)
                self.lines(screen)
                self.hist(screen)

                pygame.display.flip()
                
                n = 0

if __name__ == '__main__':
    Simulation((12,12)).run()
