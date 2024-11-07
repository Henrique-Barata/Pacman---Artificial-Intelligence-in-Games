from math import sqrt
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from BehaviourTree import *
from tasks import *

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.targetname = None
        self.name = PACMAN    
        self.color = YELLOW
        self.powerpellet = False
        self.pellet = None
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.ghosts = None
        self.nodes = None
        self.pelletList = None
        self.ghostPaths = None
        self.numEaten = 0
        self.newDirection = None
        self.newpath = []
        self.ghostsNodeWithPath = []

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP
        self.goal = None
        self.pellet = None

    # def update(self, dt):	
    #     self.sprites.update(dt)
    #     self.position += self.directions[self.direction]*self.speed*dt
    #     direction = self.getValidKey()
    #     if self.overshotTarget():
    #         self.node = self.target
    #         if self.node.neighbors[PORTAL] is not None:
    #             self.node = self.node.neighbors[PORTAL]
    #         self.target = self.getNewTarget(direction)
    #         if self.target is not self.node:
    #             self.direction = direction
    #         else:
    #             self.target = self.getNewTarget(self.direction)

    #         if self.target is self.node:
    #             self.direction = STOP
    #         self.setPosition()
    #     else: 
    #         if self.oppositeDirection(direction):
    #             self.reverseDirection()

    
    def update2(self, dt):  
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        self.getPathsGhost()
        
        # Criação da árvore de comportamento
        tree = Selector(
            Sequence(
                IsGhostNear(self),
                Selector(
                    Sequence(
                        AmPowered(self),
                        ChaseGhost(self)
                    ),
                    Escape(self)
                )
            ),
            Selector(
                Sequence(
                    IsGoalDefined(self),
                    DefineGoal(self),
                    HeadToPellet(self)
                ),
                HeadToPellet(self)
            )
        )
        
        
        # Execução da árvore de comportamento
        tree.run()
        
        direction = self.newDirection
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def update(self,dt):
        self.sprites.update(dt)
    # def getValidKey(self):
    #     key_pressed = pygame.key.get_pressed()
    #     if key_pressed[K_UP]:
    #         return UP
    #     if key_pressed[K_DOWN]:
    #         return DOWN
    #     if key_pressed[K_LEFT]:
    #         return LEFT
    #     if key_pressed[K_RIGHT]:
    #         return RIGHT
    #     return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                self.pellet = None
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def getPathsGhost(self):
        self.ghostPaths = []
        self.ghostsNodeWithPath = []
        pacmanNode = self.node
        if(self.direction == 0):
            pacmanNextNode = pacmanNode
        else:
            pacmanNextNode = pacmanNode.neighbors[self.direction]
        for g in self.ghosts:
            if g.name == INKY and self.numEaten < 30:
                continue
            if g.name == CLYDE and self.numEaten < 70:
                continue
            ghostNode = g.node
            ghostNextNode = ghostNode.neighbors[g.direction]
            self.ghostPaths.append(self.shortestPath(pacmanNextNode, ghostNextNode))
            self.ghostsNodeWithPath.append(ghostNode)
    
    def shortestPath(self, start, goal):
        d= self.manhatan(start.position, goal.position)
        return self.shortestPath2(goal, [(d, [start])], [])

    def shortestPath2(self, goal, lopen, lclosed):
        if lopen == []:
            return []
        else:
            lopen = sorted(lopen, key=lambda x: x[0])
            path = lopen[0][1]
            node = path[0]
            lopen = lopen[1:]

            if node.position == goal.position:   
                return path
           
            else:
               lclosed.append(node)

               neighbours = []
               neighbours.append(node.neighbors[LEFT])
               neighbours.append(node.neighbors[RIGHT])
               neighbours.append(node.neighbors[UP])
               neighbours.append(node.neighbors[DOWN])
               neighbours.append(node.neighbors[PORTAL])
               for n in neighbours:
                    if n != None and n not in lclosed:
                       lopen.append((self.manhatan(n.position, goal.position), [n]+path))
            return self.shortestPath2(goal, lopen, lclosed)
    
    def getClosestPellet(self):
        sDistance = 1000
        for p in self.pelletList:
            d = self.manhatan(self.position, p.position)
            if d < sDistance:
                sDistance = d
                self.pellet = p

    def getPathPellet(self):
        self.newpath = []
        if self.direction == 3:
            self.newpath = [self.node]
            return
        print("-------------------------------------------------------------------------------------")
        for n in self.nodes.nodesLUT:
            node = self.nodes.nodesLUT.get(n)
            if(node.position.x == self.goal.position.x and node.position.y  == self.goal.position.y):
                print("1")
                self.newpath = self.shortestPath(self.node, node)
                return
        lastNode = None    
        for node2 in self.getLineNodes(self.goal.position.x):                
                if(node2.position.y > self.goal.position.y): 
                        if(lastNode is None):
                            break
                        print("2")
                        if(self.node.position == lastNode.position):
                            self.newpath.append(node2)
                            return 
                        elif(self.node.position == node2.position):
                            self.newpath.append(lastNode)
                            return                         
                        if(self.manhatan(self.node.position, lastNode.position) < self.manhatan(self.node.position,node2.position)):
                            self.newpath = self.shortestPath(self.node.neighbors.get(self.direction), lastNode)                            
                            self.newpath.append(node2)
                        else:
                            self.newpath = self.shortestPath(self.node.neighbors.get(self.direction), node2)  
                            self.newpath.append(lastNode)
                        print(self.newpath)                                    
                        #return self.shortestPath(self.node.neighbors.get(self.direction), node2).append(lastNode)
                        return
                lastNode = node2

        for node2 in self.getColumNodes(self.goal.position.y):
            #if(node2.position.x - self.goal.position.x):    
                if(node2.position.x > self.goal.position.x):
                    if(lastNode is None):
                        break
                    print("3")
                    print(self.node.position)
                    #print(self.node.neighbors.get(self.direction).position)
                    if(self.node.position == lastNode.position):
                        self.newpath.append(node2)
                        return 
                    elif(self.node.position == node2.position):
                        self.newpath.append(lastNode)
                        return  
                    if(self.manhatan(self.node.position, lastNode.position) < self.manhatan(self.node.position,node2.position)):
                        self.newpath = self.shortestPath(self.node.neighbors.get(self.direction), lastNode)  
                        self.newpath.append(node2)
                    else:
                        self.newpath = self.shortestPath(self.node.neighbors.get(self.direction), node2)  
                        self.newpath.append(lastNode)
                    print(self.newpath)  
                    print(lastNode.position)  
                    print(node2.position) 
                    return      
                lastNode = node2
    
    def getLineNodes(self, pos):
        noodes = []
        for n in self.nodes.nodesLUT:
            node = self.nodes.nodesLUT.get(n) 
            if(node.position.x == pos):
                noodes.append(node)
        return noodes
    
    def getColumNodes(self, pos):
        noodes = []
        for n in self.nodes.nodesLUT:
            node = self.nodes.nodesLUT.get(n)
            if(node.position.y == pos):
                noodes.append(node)
        return noodes
    
    def getDirectionPellet(self):           
        for node in self.newpath:            
            if(self.node.neighbors.get(LEFT) == node):
                self.newDirection = LEFT
            elif(self.node.neighbors.get(UP) == node):
                self.newDirection = UP
            elif(self.node.neighbors.get(RIGHT) == node):
                self.newDirection = RIGHT               
            elif(self.node.neighbors.get(DOWN) == node):
                self.newDirection = DOWN

    def havePallet(self):
        if(self.pellet.__class__ == None.__class__):
            self.goal = None
        return
    
    def getDirectionPellet(self):           
        for node in self.newpath:
            if(self.node.neighbors.get(LEFT) == node):
                self.newDirection = LEFT
            elif(self.node.neighbors.get(UP) == node):
                self.newDirection = UP
            elif(self.node.neighbors.get(RIGHT) == node):
                self.newDirection = RIGHT               
            elif(self.node.neighbors.get(DOWN) == node):
                self.newDirection = DOWN   

    def manhatan(self,p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)
