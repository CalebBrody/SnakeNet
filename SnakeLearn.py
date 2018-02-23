from __future__ import print_function
#Code to play the game snake and write a gif
#Writen by Caleb Brody
#Inspired by University of Texas at Austin paper
#http://nn.cs.utexas.edu/downloads/papers/stanley.gecco02_1.pdf

import argparse
import numpy as np
import sys
import pandas as pd
from sklearn import ensemble
import SnakeGame

def TrainModel(model, x, y, FutureState):
	q= y+GetBestAftermath(model, FutureState)
	for i in range(args.loops): 
		model.fit(x, y+GetBestAftermath(model, FutureState) ) 
		q= y+GetBestAftermath(model, FutureState)
		q_hat= model.predict(x) 
		print ("Iteration",i+1, 100*np.cov(q,q_hat)[1,0]/np.var(q) , "percent var retained by model.")
		
def GetBestAftermath(Q, FutureState):
	Aftermaths=np.zeros((FutureState.shape[0],3))
	# Allocate memory now so we dont need to copy arrays later.
	# These arrays can get big
	for i in range(3):
		FutureState[:, -3:]=SnakeGame.VectoriseDecision(i)
		Aftermaths[:,i] = Q.predict(FutureState).reshape(-1) 
	return np.max( Aftermaths, axis=1) 
	
x,y,FutureState=[],[],[]
MostImportantStates = [[],[],[]]
hunger = 99999

def Positive_Integer(value):
	if not (int(value)==float(value) and int(value)>0):
		raise argparse.ArgumentTypeError("%s is an invalid value" % value)
	return int(value)

parser = argparse.ArgumentParser(description='Trains an AI to play the popular ATARI game snake from scratch.  Note that the AI is not given any instructions about the rules of the game prior to play.  If the AI attempts an illegal move (going backwards, walking out of bounds, ect.) this is treated as a death.  Use command line options to adjust the settings and observe changes in snake performance.  Outputs highlight reel of each snake generation to gif.')
parser.add_argument('-m', '--Map Size',  metavar='M', dest='MapSize',default=8, help='Width of the playable map', type=Positive_Integer)
parser.add_argument('-i', '--Iterations',  metavar='l', dest='loops',default=3, help='Number of times model is trained per genration', type=Positive_Integer) 
parser.add_argument('-t', '--Hunger',  metavar='H',   dest='Hunger',default=50, help='Maximum number of turns snake can go without eating and not die', type=Positive_Integer) 
parser.add_argument('-T', '--MaxTurns',  metavar='T',   dest='TurnMax',default=400, help='Maximum number of turns per game', type=Positive_Integer) 
parser.add_argument('-G', '--Games',  metavar='N',    dest='Games',default=210, help='Number of games played per genration by a skilled snake', type=Positive_Integer) 
parser.add_argument('-rG', '--Random Games',  metavar='R', dest='rGames',default=100, help='Number of games played per genration by an unskilled snake', type=Positive_Integer) 
parser.add_argument('-g', '--Generations',  metavar='G',   dest='Generations',default=7, help='Number of generations to train', type=Positive_Integer) 
parser.add_argument('-H', '--Highlights',  metavar='H',    dest='Highlight',default=1, help='Number of games to put in the highlight Reel', type=Positive_Integer) 
parser.add_argument('-z', '--Gifsize',  metavar='Z',       dest='Size',default=600, help='Approximate width of highlight Reel gif in pixels', type=Positive_Integer)  

print ()
args = parser.parse_args()
parser.print_help()
print ()

def PlayGames(brain, games, silent=False, save=False, hunger=99999, TurnMax=args.TurnMax):
	global x,y,FutureState, MostImportantStates
	apples=[]
	turns=[]
	gifs=[]
	for i in range( games):
		gif, StateLog, RewardLog = SnakeGame.PlayGame(brain, TurnMax=TurnMax, Hunger=hunger, save=save) 
		turns.append(len(RewardLog))
		apples.append(sum(RewardLog)+1)
		gifs.append(gif)
		x+=StateLog[:-1]
		y+=RewardLog
		FutureState+=StateLog[1:]
	ImportantStates=np.array(y)!=0
	MostImportantStates[0]+=np.array(x)[ImportantStates].tolist()
	MostImportantStates[1]+=np.array(y)[ImportantStates].tolist()
	MostImportantStates[2]+=np.array(FutureState)[ImportantStates].tolist()
	if not silent: print ("Observed", len(y),"states, on average lived", np.mean( turns), "turns, ate", np.mean( apples), "times.") 
	return 	apples, turns, gifs


SnakeGame.MapSize=args.MapSize
Px_Size=         int(600/args.MapSize)
if Px_Size<1:
         raise argparse.ArgumentTypeError("Invalid Gifsize") 

# Get the first round of data by moving randomly
PlayGames(lambda state: np.random.randint(3), args.rGames)

params = {'n_estimators':500, 'max_depth':5, 'min_samples_split': 2,
          'learning_rate': 0.01, 'loss': 'ls'}
Q = ensemble.GradientBoostingRegressor(**params)
Q.fit(np.array(x), y )
TrainModel(Q, np.array(x), y  , np.array(FutureState))

def MakeDecision(state):
	Decision=0
	BestAftermath_hat=0
	for i in range(3):
		Aftermath_hat=Q.predict(np.array(state+SnakeGame.VectoriseDecision(i)).reshape(1,-1) ) 
		if  Aftermath_hat>BestAftermath_hat:
			BestAftermath_hat=Aftermath_hat
			Decision=i
	return Decision
	
for Generation in range(args.Generations):
	x,y,FutureState=MostImportantStates
	MostImportantStates = [[],[],[]]
	print ()
	print ( "     Generation", Generation+1) 
	PlayGames(lambda state: np.random.randint(3), args.rGames, silent=True) 
	apples, turns, gifs = PlayGames(MakeDecision, args.Games) 

	if max(turns) > args.Games and hunger>args.Hunger:
		hunger=args.Hunger
		print ("SNAKE PERFORMING WELL.  ACTIVATING HUNGER" )
	apples, turns, gifs = PlayGames(MakeDecision, args.Highlight*2,TurnMax=99999, save=True, silent=True, hunger=hunger) 
	HighlightReel=[]
	for i in tuple( np.where(np.array(apples) >= sorted(apples)[-args.Highlight]))[0] :
		HighlightReel+=gifs[i]		
	SnakeGame.imageio.mimsave("Generation"+ str(  Generation+1 )+".gif", HighlightReel)
	del HighlightReel
	del gifs
	SnakeGame.gc.collect()
	if Generation < args.Generations-1:
		TrainModel(Q, np.array(x), y  , np.array(FutureState))


	

