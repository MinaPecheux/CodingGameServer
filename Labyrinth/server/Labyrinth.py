"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: Labyrinth.py
	Contains the class Labyrinth
	-> defines the Labyrinth game (its rules, moves, etc.)

"""


from random import shuffle, random, randint
from CGS.Game import Game
from CGS.Constants import MOVE_OK, MOVE_WIN, MOVE_LOSE
from colorama import Fore
from re import compile

regdd = compile("(\d+)\s+(\d+)")    # regex to parse a "%d %d" string



# TODO: check how to make `pythonic` constants
# see http://stackoverflow.com/questions/11111632/python-best-cleanest-way-to-define-constant-lists-or-dictionarys
# put all these constants in a separate Laby_const.py file ?
ROTATE_LINE_LEFT = 0
ROTATE_LINE_RIGHT = 1
ROTATE_COLUMN_UP = 2
ROTATE_COLUMN_DOWN = 3
MOVE_UP = 4
MOVE_DOWN = 5
MOVE_LEFT = 6
MOVE_RIGHT = 7
DO_NOTHING = 8

Ddx = {MOVE_UP: 0, MOVE_DOWN: 0, MOVE_LEFT: -1, MOVE_RIGHT: 1}      # simple dictionary of x-offsets
Ddy = {MOVE_UP: -1, MOVE_DOWN: 1, MOVE_LEFT: 0, MOVE_RIGHT: 0}





def CreateLaby(sX, sY):
	"""
	Build a Labyrinth (an array of booleans: True=> empty, False=> wall)
	:param sX: number of 2x2 blocks (over X)
	:param sY: number of 2x2 blocks (over Y)
	Build a random (4*sX+1) x (2*sY+1) labyrinth, symmetric with respect column 2*sX

	generation based on https://29a.ch/2009/9/7/generating-maps-mazes-with-python

	A cell is a 2x2 array
	| U X |
	| o R |
	where o is the "origin" of the cell, U and R the Up and Right "doors" (to the next cell), and X a wall
	(the 1st line and 2 column will be the fixed lines/columns of the labyrinth)

	The lab is composed of these cells (except that the 1st line of the lab only have the half-bottom of cells)
	and is symmetric with respect to the middle column

	A path is randomly generated between all these cells, and "doors" are removed accordingly

	Returns a tuple (L,H,lab)
	- L: numbers of rows
	- H: number of lines
	- lab: list of lists (lab[x][y] with 0 <= x <= L and 0 <= y <= H)

	"""
	Directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]

	L = 4 * sX + 1
	H = 2 * sY + 1
	# create a L*H array of False)
	lab = [list((False,)*H) for _ in range(L)]

	shuffle(Directions)
	stack = [(0, 0, list(Directions))]  # X, Y of the cell( 2x2 cell) and directions

	while stack:
		# get the position to treat, and the possible directions
		x, y, direction = stack[-1]
		dx, dy = direction.pop()  # remove one direction

		# if it was the last direction to explore, remove that position to the stack
		if not direction:
			stack.pop()

		# new cell
		nx = x + dx
		ny = y + dy
		# check if we are out of bounds (ny==-1 is ok, but in that case, we will only consider
		# the last line of the cell -> it will be the line number 0)
		if not (0 <= nx <= sX and -1 <= ny < sY):
			continue
		# index of the "origin" of the cell
		ox = 2 * nx
		oy = 2 * ny + 2
		# check if already visited
		if lab[ox][oy]:
			continue
		# else remove the corresponding wall (if within bounds)
		if (0 <= (ox - dx) <= (2 * sX + 1)) and (0 <= (oy - dy) <= (2 * sY + 1)):
			lab[ox - dx][oy - dy] = True
			lab[4 * sX - ox + dx][oy - dy] = True  # and its symmetric
		# remove the origin
		lab[ox][oy] = True
		lab[4 * sX - ox][oy] = True  # and its symmetric
		if random() > 0.75:
			lab[ox + 1][oy - 1] = True
			lab[4 * sX - ox - 1][oy - 1] = True  # and its symmetric

		# add it to the stack
		shuffle(Directions)
		stack.append((nx, ny, list(Directions)))

	return L, H, lab


class Labyrinth(Game):
	"""
	Labyrinth game
	Inherits from Game
	- _players: tuple of the two players
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- _whoPlays: number of the player who should play now (0 or 1)
	- _waitingPlayer: Event used to wait for the players
	- _lastMove, _last_return_code: string and returning code corresponding to the last move

	Add some properties
	- _lab: array (list of lists of booleans) representing the labyrinth
	- _L,_H: length and height of the labyrinth
	- _treasure: coordinate (2-uplet) of the treasure
	- _playerPos: list of the coordinates of the two players (player #0 and player #1)
	- _playerEnergy: list of the energy level of the two players

	"""

	allGames = {}

	def __init__(self, player1, player2, seed=None):
		"""
		Create a labyrinth
		:param player1: 1st Player
		:param player2: 2nd Player
		:param seed: seed of the labyrinth (same seed => same labyrinth); used as seed for the random generator
		"""

		# TODO: add size of the labyrinth in the constructor?

		# random Labyrinth
		totalSize = randint(7, 11)  # sX + sY is randomly in [7;9]
		sX = randint(3, 5)
		self._L, self._H, self._lab = CreateLaby(sX, totalSize - sX)

		# add treasure and players
		self._treasure = (self.L // 2, self.H // 2)
		self._lab[self._treasure[0]][self._treasure[1]] = True  # no wall here

		self._playerPos = []            # list of coordinates
		self._playerPos.append((0, self.H // 2))
		self._playerPos.append((self.L - 1, self.H // 2))

		# Level of energy
		self._playerEnergy = [5, 5]


		for x, y in self._playerPos:
			self._lab[x][y] = True  # no wall here

		# call the superclass constructor (only at the end, because the superclass constructor launches
		# the players and they will immediately requires some Labyrinth's properties)
		super(Labyrinth, self).__init__(player1, player2, seed)

		self._playerEnergy[self._whoPlays] = 4


	@property
	def lab(self):
		return self._lab


	def HTMLrepr(self):
		return "<A href='/game/%s'>%s</A>" % (self.name, self.name)

	def HTMLpage(self):
		# TODO: return a dictionary to fill a html template
		return "Game %s (with players '%s' and '%s'\n<br><br>%s" % (
			self.name, self._players[0].name, self._players[1].name, self)



	def __str__(self):
		"""
		Convert a Game into string (to be send to clients, and display)
		"""
		# TODO: add informations about last move, etc.
		# TODO: use unicode box-drawing characters to display the game (cf https://en.wikipedia.org/wiki/Box-drawing_character)

		lines = []
		for y in range(self.H):
			st = []
			for x in range(self.L):
				# add treasure
				if (x, y) == self._treasure:
					st.append(Fore.GREEN + u"\u2691" + Fore.RESET)
				# add player1
				elif (x, y) == self._playerPos[0]:
					st.append(Fore.BLUE + u"\u265F" + Fore.RESET)
				# add player2
				elif (x, y) == self._playerPos[1]:
					st.append(Fore.RED + u"\u265F" + Fore.RESET)
				# add empty
				elif self.lab[x][y]:
					st.append(" ")
				# or add wall
				else:
					st.append(u"\u2589")
			lines.append("|" + " ".join(st) + "|")

		# add player names
		# TODO: add energy
		br0 = "[]" if self._whoPlays == 0 else "  "
		br1 = "[]" if self._whoPlays == 1 else "  "
		lines[self.H//2] += "\t\t" + br0[0] + Fore.BLUE + "Player 1: " + Fore.RESET + self._players[0].name + br0[1]
		lines[self.H//2 + 2] += "\t\t" + br1[0] + Fore.RED + "Player 2: " + Fore.RESET + self._players[1].name + br1[1]

		head = "+"+"-"*(2*self.L-1)+"+\n"
		return head + "\n".join(lines) + "\n" + head


	@property
	def L(self):
		return self._L


	@property
	def H(self):
		return self._H

	# TODO: (julien) renommer playMove
	def playMove(self, move):
		"""
		Play a move
		- move: a string "%d %d"
		Return a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending
		"""
		# parse the move
		result = regdd.match(move)
		# check if the data receive is valid
		if result is None:
			return MOVE_LOSE, "The move is not in correct form ('%d %d') !"
		# get the type and the value
		move_type = int(result.group(1))
		value = int(result.group(2))
		# check the possible values
		if not (ROTATE_LINE_LEFT <= move_type <= DO_NOTHING):
			return MOVE_LOSE, "The type is not valid !"
		if (ROTATE_LINE_LEFT <= move_type <= ROTATE_LINE_RIGHT) and not (0 <= value < self.H):
			return MOVE_LOSE, "The line number is not valid !"
		if (ROTATE_COLUMN_UP <= move_type <= ROTATE_COLUMN_DOWN) and not (0 <= value < self.L):
			return MOVE_LOSE, "The column number is not valid !"

		# move the player
		if MOVE_UP <= move_type <= MOVE_RIGHT:
			x, y = self._playerPos[self._whoPlays]
			x += Ddx[move_type]
			y += Ddy[move_type]

			# TODO: on rajoute cette règle, ou bien on a droit de cycler ?
			if not (0 <= x < self.L) or not(0 <= y < self.H):
				return MOVE_LOSE, "Cannot go outside of the labyrinth"

			if not self._lab[x][y]:
				return MOVE_LOSE, "Outch! There's a wall where you want to move!"

			# play the move (move the player on the lab)
			self._playerPos[self._whoPlays] = (x, y)

			# check if won
			if (x, y) == self._treasure:
				return MOVE_WIN, "You find the treasure, you win!"
			else:
				return MOVE_OK, ""

		elif move_type == DO_NOTHING:
			return MOVE_OK, ""
		else:
			return MOVE_LOSE, "Rotation not yet implemented"




	def getData(self):
		"""
		Return the datas of the labyrinth (when ask with the GET_GAME_DATA message)
		"""
		msg = []
		for y in range(self.H):
			for x in range(self.L):
				msg.append("1" if self.lab[x][y] else "0")
		return "".join(msg)



	def getDataSize(self):
		"""
		Returns the size of the next incoming data
		Here, the size of the labyrinth
		"""
		return "%d %d" % (self.L, self.H)