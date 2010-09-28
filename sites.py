from math import sqrt, exp
import random

import matplotlib.pyplot as plt

import pygame
from pygame.locals import *

class Simulation:

    WIDTH = 640
    HEIGHT = 480

    LINE = 4

    DRAW_FRAMES = 100

    FUDGE = 0.1

    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.grid_size = min(self.WIDTH/(self.dimensions[0] + 1),
                             self.HEIGHT/(self.dimensions[1] + 1))
        self.bg_rect = pygame.Rect(max(0, (self.WIDTH - (self.dimensions[0] + 1) * self.grid_size) / 2),
                                   max(0, (self.HEIGHT - (self.dimensions[1] + 1) * self.grid_size) / 2),
                                   (self.dimensions[0] + 1) * self.grid_size,
                                   (self.dimensions[1] + 1) * self.grid_size)

        self.sites = [[[max(0, min(1, random.gauss(0.5, 0.125)))
                        for i in range(5)]
                       for y in range(self.dimensions[1])]
                      for x in range(self.dimensions[0])]

    def background(self, screen):
        screen.fill((255,255,255), self.bg_rect)

    def similarity(self, p1, p2):
        return 1 - sqrt(sum([(c1-c2)*(c1-c2) for c1, c2 in zip(p1, p2)]))
    
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

    def interact(self, active, neighb):
        different = [i for i in range(len(active))
                     if active[i] != neighb[i]]
        if len(different) > 0:
            i = random.sample(different, 1)[0]
            active[i] = neighb[i]

    def try_event(self):
        active = self.random_site()
        neighb = self.random_neighbor(active)
        active_site = self.sites[active[0]][active[1]]
        neighb_site = self.sites[neighb[0]][neighb[1]]
        if random.random() < self.similarity(active_site, neighb_site):
            self.interact(active_site, neighb_site)

    def report(self):
        for x in range(len(self.sites)):
            for y in range(len(self.sites[0])):
                print self.similarity(self.sites[0][0],
                                      self.sites[x][y])
        for i in range(len(self.sites[0][0])):
            plt.subplot(len(self.sites[0][0]),1,i).set_ylim(0,100)
            plt.hist([self.sites[x][y][i] for x in
                      [x for x in range(len(self.sites)) for y in
                       [y for y in range(len(self.sites[0]))]]],
                     100, (0,1))
        plt.show()
    
    def run(self):
        pygame.init()

        screen = pygame.display.set_mode((self.WIDTH,self.HEIGHT), HWSURFACE)
        pygame.display.set_caption('Sites')

        self.report()

        done = False
        n = 0
        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        done = True
                    elif event.key == K_SPACE:
                        self.report()

            self.try_event()
            n += 1
            if n > self.DRAW_FRAMES:
                
                self.background(screen)
                self.lines(screen)

                pygame.display.flip()
                
                n = 0

if __name__ == '__main__':
    Simulation((10,10)).run()
