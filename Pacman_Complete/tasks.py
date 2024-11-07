from math import sqrt
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from BehaviourTree import *
from pacman import *


class IsGhostNear(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run(self):
        print('NEAR')
        paths = self.pacman.ghostPaths
        if len(paths) == 0:
            return False
        
        distances = []
        for path in paths:
            distances.append(self.pathDistance(path))
        if min(distances) < NEAR:
            index = distances.index(min(distances))
            self.pacman.pathClosestGhost = paths[index]
            self.pacman.pellet = None
            self.pacman.goal = None
            return True
        return False
    
    def pathDistance(self, path):
        i=0
        d=0
        while i < len(path)-1:
            d += self.pacman.manhatan(path[i].position, path[i+1].position)
            i +=1
        return d

class AmPowered(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run(self):
        return self.pacman.powerpellet

class ChaseGhost(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run(self):
        print('Pow')
        ghosts = self.pacman.pathClosestGhost
        self.pacman.goal = ghosts[-1].position
        validDirections = self.pacman.validDirections()
        direction = self.pacman.goalDirection(validDirections)
        self.pacman.newDirection = direction
        return True

class Escape(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman
    
    def run(self):
        self.pacman.newdirection = self.pacman.direction*-1

    def run2(self):
        print('ESC')
        ghosts = self.pacman.ghostPaths
        validDirections = []
        if self.pacman.node.neighbors[self.pacman.direction].neighbors[LEFT] != None:
            validDirections.append(LEFT)
        if self.pacman.node.neighbors[self.pacman.direction].neighbors[RIGHT] != None:
            validDirections.append(RIGHT)
        if self.pacman.node.neighbors[self.pacman.direction].neighbors[UP] != None:
            validDirections.append(UP)
        if self.pacman.node.neighbors[self.pacman.direction].neighbors[DOWN] != None:
            validDirections.append(DOWN)
        print(validDirections)
        
        self.pacman.newDirection = self.getFurtherDirection(validDirections, ghosts)
        self.pacman.goal = self.pacman.node.neighbors[self.pacman.direction].neighbors[self.pacman.newDirection].position
        return True
    
    def getFurtherDirection(self,validDirections, ghosts):
        if len(validDirections) == 1:
            return validDirections[0]
        dir = 0
        distances = []
        for d in validDirections:
            dist=0
            for g in ghosts:
                if self.pathDistance(g) < NEAR:
                    p = self.pacman.shortestPath(self.pacman.node.neighbors[self.pacman.direction].neighbors[d], g[-1])
                    dist += self.pathDistance(p)
            distances.append(dist)    
        index = distances.index(min(distances))
        print('DISTANCE')
        print(min(distances))
        print(validDirections[index])
        return validDirections[index]

    def pathDistance(self, path):
        i=0
        d=0
        while i < len(path)-1:
            d += self.pacman.manhatan(path[i].position, path[i+1].position)
            i +=1
        return d               


class IsGoalDefined(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run(self):
        print('isDef')
        return (self.pacman.pellet.__class__ == None.__class__) 

class DefineGoal(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run(self):
        print('DEF')
        self.pacman.getClosestPellet() 
        self.pacman.goal = self.pacman.pellet
        #self.pacman.newpath = 
        self.pacman.getPathPellet() 
        return True

class HeadToPellet(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run2(self):
        validDirections = []
        if self.pacman.node.neighbors[LEFT] != None:
            validDirections.append(LEFT)
        if self.pacman.node.neighbors[RIGHT] != None:
            validDirections.append(RIGHT)
        if self.pacman.node.neighbors[UP] != None:
            validDirections.append(UP)
        if self.pacman.node.neighbors[DOWN] != None:
            validDirections.append(DOWN)
        if self.pacman.node.neighbors[PORTAL] != None:
            validDirections.append(PORTAL)
        
        v = self.pacman.validDirections()
        self.pacman.newDirection = self.pacman.goalDirection(v)
        return True
    
    def run(self):
        print('HeadToPellett')
        self.pacman.getDirectionPellet()
        return True 

class CloserPellet(Task):
    def __init__(self, pacman):
        super().__init__()
        self.pacman = pacman

    def run(self):
        self.pacman.getClosestPellet()
        self.pacman.pellet = self.pacman.pellet.position
        self.pacman.goal = self.pacman.pellet
        return True