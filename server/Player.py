import logging
from logging.handlers import RotatingFileHandler
from threading import Event


logger = logging.getLogger()		# general logger ('root')


class Player:
	"""
	A Player

	- _logger: a logger, used to log info/debug/errors
	- _name: its name
	- _game: the game it is involved with
	- _waitingGame: an Event used to wait for the game to start (set when a game is set)

	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.whoPlays == self)
	- opponent's turn (game.whoPlays != self)
	"""
	allPlayers = {}

	def __init__(self, name):
		# create the logger of the player
		self._logger = logging.getLogger(name)
		# add an handler to write the log to a file (1Mo max) *if* it doesn't exist
		if not self._logger.handlers:
			file_handler = RotatingFileHandler('logs/players/'+name+'.log', 'a', 1000000, 1)
			file_handler.setLevel(logging.INFO)
			file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
			file_handler.setFormatter(file_formatter)
			self._logger.addHandler(file_handler)


		self.logger.warning( "=================================")
		self.logger.warning( name + " just log in.")

		# name
		self._name = name

		# add itself to the dictionary of games
		self.allPlayers[name] = self

		# game
		self._game = None

		# waitGame event
		self._waitingGame = Event()
		self._waitingGame.clear()


	def HTMLrepr(self):
		return "<B><A href='/player/"+self._name+"'>"+self._name+"</A></B>"


	def HTMLpage(self):
		#TODO: return a dictionary to fill a template
		return self.HTMLrepr()


	@classmethod
	def removePlayer(cls, name):
		pl = cls.getFromName(name)
		if pl is not None:
			pl.logger.warning( name +" just log out.")
			del cls.allPlayers[name]


	@classmethod
	def getFromName(cls, name):
		"""
		Get a player form its name
		:param name: (string) name of the player
		:return: the player (the object) or None if this player doesn't exist
		"""
		return cls.allPlayers.get( name, None)




	@property
	def opponent(self):
		"""
		Return our opponent in the game
		"""
		if self._game is None:
			return None
		elif self._game.player1 is self:
			return self._game.player2
		else:
			return self._game.player1



	@property
	def name(self):
		return self._name


	@property
	def logger(self):
		return self._logger

	@property
	def game(self):
		return self._game

	@game.setter
	def game(self,g):
		self._game = g
		self.logger.warning("Enter in game "+g.name)
		# since we have a game, then we can set the Event
		self._waitingGame.set()


