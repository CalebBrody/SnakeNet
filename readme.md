SnakeNet is an easy to read easy to run Q Learning implementation for the classic game snake.

SnakeLearn.py trains an AI from scratch.  Note that the AI is not given any instructions about the rules of the game prior to play.  If the AI attempts an illegal move (going backwards, walking out of bounds, ect.) this is treated as a death.  Use command line options to adjust the settings and observe changes in snake performance.

SnakeNet saves a highlight reel of each snake generation as a gif.

Generation 1

![Gen 1.gif](Generation1.gif)

Generation 2

![Gen 2.gif](Generation2.gif)

Generation 3

![Gen 3.gif](Generation3.gif)

Generation 4

![Gen 4.gif](Generation4.gif)

usage: python SnakeLearn.py [-h] [-m M] [-i l] [-t H] [-G N] [-rG R] [-g G] [-H H] [-z Z]

optional arguments:
  -h, --help            show this help message and exit
  -m M, --Map Size M    Width of the playable map
  -i l, --Iterations l  Number of times model is trained per genration
  -t H, --Hunger H      Maximum number of turns snake can go without eating
                        and not die
  -G N, --Games N       Number of games played per genration by a skilled
                        snake
  -rG R, --Random Games R
                        Number of games played per genration by an unskilled
                        snake
  -g G, --Generations G
                        Number of generations to train
  -H H, --Highlights H  Number of games to put in the highlight Reel
  -z Z, --Gifsize Z     Approximate width of highlight Reel gif in pixels
