#Code to play the game snake and write a gif
#Writen by Caleb Brody
#Inspired by University of Texas at Austin paper
#http://nn.cs.utexas.edu/downloads/papers/stanley.gecco02_1.pdf

import gc
import imageio
from PIL import Image
import numpy as np
import pandas as pd

#Setup global variables
#These variables can be referenced by bother programs as SnakeGame.MapSize (more pythonic than SnakeGame.SetMapSize)
MapSize=16
Px_Size=int(600/MapSize)

class Location:
	def __init__(self, x=None, y=None):
		if x is None:
			self.loc = np.array([ np.random.randint(MapSize),np.random.randint(MapSize)] )
		else:
			self.loc = np.array((x,y))
			
	def __eq__(self, other):
		return np.product(self.loc == other.loc)
		
	def __add__(self, other):
		return self.loc + other.loc
		
	def __str__(self):
		return self.loc.__str__()
		
	def move(self, other):
		self.loc +=other.loc
		
	def turn(self, direction):
		if direction==0:
			pass
		elif direction==1:
			# Turn Left
			self.loc=np.array((self.loc[1], self.loc[0])) 
		elif direction==2:
			#Turn Right
			self.loc=-np.array((self.loc[1], self.loc[0]))
		else:
			raise ValueError("cant turn direction " + str(by))
			
	def copy(self):
		return Location(self.loc[0], self.loc[1])
		
	def CardinalDirections(self):
		#Return a list, oriented at self, of all Cardinal Directions 
		dict={}
		for i in range(3):
			tmp=self.copy()
			tmp.turn(i)
			dict[i]=tmp
		return dict
		
	def oob(self): #Out of bounds
		return np.sum(self.loc<0)>0 or np.sum(self.loc>MapSize )>0 
	
		
game = pd.DataFrame()

def PlayGame(brain, save=False, TurnMax=400, Hunger=99999):
	StartGame()
	Alive = True
	turn = 0
	VisibleState =[0]*9
	gif, StateLog, RewardLog  = [], [],[]
	HungerCounter=0
	while Alive and HungerCounter<Hunger and turn < TurnMax:
		turn += 1
		decision = brain( VisibleState)
		StateLog.append(VisibleState + VectoriseDecision(decision))
		VisibleState , reward = MoveSnake(decision)
		RewardLog.append( reward )
		if reward < 0:
			Alive = False
		elif reward > 0 :
			HungerCounter=0
		else:
			HungerCounter+=1
		if save:
			if turn % 100==0:
				gc.collect()

			gif.append(DrawBoard())
	StateLog.append([0]*12)
	return gif, StateLog, RewardLog
	
def AddFood():
    game.food=Location()
    if game.food in game.tail:
        AddFood()

def StartGame():
	game.snake=Location()
	game.tail=[game.snake.copy()]
	game.head=Location(0,1)
	AddFood()

def RandomMove(VisibleState):
	return np.random.randint(3)
def MinimumDistance2Target(x,y, loc, target,default=0):
    if (loc[0]-target[0])*(y-1) == (loc[1]-target[1]) *(x-1) and sum(loc!=target):
        return max(-(loc[0]-target[0])*(x-1), -(loc[1]-target[1])*(y-1))
    return default
def VectoriseDecision(x):
		return [x==0, x==1, x==2]
		
def MoveSnake(angle):
	game.head.turn(angle)
	game.snake.move(game.head)
	
	reward=0
	if game.snake in game.tail:
		reward=-.99
	else:
		game.tail.append(game.snake.copy())
	if game.snake.oob():
		reward=-1
	if game.snake==game.food:
		reward+=1
		AddFood()
	else:
		game.tail=game.tail[1:]

	return GetVisibleState() , reward

def GetVisibleState():
	CardinalDirections = game.head.CardinalDirections()
	
	WallRing, FoodRing, SelfRing = [], [], []
	for i in range(3):
		x,y = CardinalDirections[i].loc+1
		wall=np.array([(x>0)*MapSize , (y>0)*MapSize ])
		dist = np.abs( game.snake.loc-wall )
		if y==1:
			WallRing.append( dist[0]) 
		elif x==1:
			WallRing.append(dist[1]) 
		FoodRing.append( MinimumDistance2Target(x,y, game.snake.loc, game.food.loc ) )
		SelfRing.append( np.min( [MinimumDistance2Target(x,y, game.snake.loc, i.loc, MapSize*2 ) for i in game.tail]) )
	return WallRing + FoodRing + SelfRing

def ScaleFor3dy(x,z, th=.75):
	return int  (x*(th**(z/MapSize)) * Px_Size )
	
def ScaleFor3dx(x, z, th=.85):
	return int  (((x-MapSize/2.)*(th**(z/Px_Size/MapSize)) + MapSize/2.) * Px_Size )
	
def DrawBox(i, board, color, th=.75):
	x, y = i.loc 
	
	for height in range( ScaleFor3dy(y,y) , ScaleFor3dy(y+1,y+1) ):
		board[-height,  ScaleFor3dx(x, height+0., th=.75) :  ScaleFor3dx(x+1, height+0., th=.75) ]=color
	
def DrawBoard():
	board = np.zeros((MapSize*Px_Size+Px_Size+1, MapSize*Px_Size+Px_Size+1, 3), dtype=np.uint8)
	for i in game.tail:
		if not i.oob(): 
			DrawBox(i, board, [255,0,0])
	DrawBox(game.food, board, [0,255,0])
	
	return board

if __name__ == "__main__":
	gif, _, __= PlayGame(RandomMove,  save=True)
	imageio.mimsave("game.gif", gif)			
