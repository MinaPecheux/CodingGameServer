
#include <stdio.h>
#include <stdlib.h>
#include "../clientAPI/labyrinthAPI.h"

typedef struct {
	int sizeX,sizeY;	/* labyrinth size */
	char* lab;			/* labyrinth data */
	int trX,trY;		/* treasure position */
	int X,Y;			/* our position */
	int opX,opY;		/* opponent position */
	int player;			/* gives who plays (0: us, 1: the opponent) */
} t_laby;




/* wait for a labyrinth
 * and fill the t_lab structure from the server
 */
void getLabyrinth(char* labName, t_laby* laby)
{
	int x,y,type;
	waitForLabyrinth(labName, &laby->sizeX, &laby->sizeY);
	laby->lab = (char*) calloc( laby->sizeX*laby->sizeY, sizeof(char));
	do {

		/* get ONE data */
		retrieveData( &type, &x, &y);
		/* deal with it */
		if (type==WALL)
			laby->lab[ x + y*laby->sizeX ] = 1;
		else if (type==US) {
			laby->X = x;
			laby->Y = y;
		}
		else if (type==OPPONENT) {
			laby->opX = x;
			laby->opY = y;
		}
		else if (type==TREASURE) {
			laby->trX = x;
			laby->trY = y;
		}
	} while (type != END_OF_DATA);
}

/* rotate a line of the labyrinth */
void rotateLine( t_laby* laby, int line, int delta)
{
}

/* rotate a column of the labyrinth */
void rotateColumn( t_laby* laby, int column, int delta)
{
}



/* Play a move (change the labyrinth and coordinate accordingly */
void playMove( t_laby* laby, int type, int val)
{
	if (type==ROTATE_LINE_UP)
		rotateLine(laby, val, 1);
	else if (type==ROTATE_LINE_DOWN)
		rotateLine(laby, val, -1);
	else if (type==ROTATE_COLUMN_UP)
		rotateColumn(laby, val, 1);
	else if (type==ROTATE_COLUMN_DOWN)
		rotateColumn(laby, val, -1);
	else {
		/* pointer to the position of the current player */
		int *pX = laby->player ? &laby->X : &laby->opX;
		int *pY = laby->player ? &laby->Y : &laby->opY;

		if (type == MOVE_UP)
			*pY = (*pY + 1) % laby->sizeY;
		else if (type == MOVE_DOWN)
			*pY = (*pY + laby->sizeY - 1) %
				  laby->sizeY;    // add sizeY to avoid negative value (modulo of negative value is negative in C...)
		else if (type == MOVE_RIGHT)
			*pX = (*pX + 1) % laby->sizeX;
		else if (type == MOVE_LEFT)
			*pX = (*pX + laby->sizeX - 1) % laby->sizeX;    // idem
	}
}





int main()
{
	char labName[50];	/* name of the labyrinth */
	t_laby lab;
	int finished;		/* indicates if the game is over */
	int type, val;		/* used for a move */


	/* connection to the server */
	connectToServer( "localhost", "babyLaby");
	printf("Youhou, connecté au serveur !\n");


	/* play over and over... 
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (1)
	{

		/* wait for a game, and retrieve informations about it */
		//getLabyrinth( labName, &lab);
	  waitForLabyrinth( labName,&(lab.sizeX), &(lab.sizeY));
		printf("On commence!\n");
			
		/* who's start ? */
		//lab.player = getWhoStarts();
		
		do {
			finished=0;
//			if (lab.player==1)	/* The opponent plays */
//			{
//				//finished = getMove( &type, &val);
//				playMove( &lab, type, val);
//			}
//			else
//			{
//				//.... choose what to play
//				type=MOVE_UP;
//				val=0;
//				//finished = sendMove(type, val);
//				playMove( &lab, type, val);
//			}
//			/* display the labyrinth */
//			printLabyrinth();
//			/* change player */
//			lab.player = !lab.player;

		} while (!finished);
	

		/* we do not forget to free the allocated array */
		free(lab.lab);
	}
	
	/* end the connection, because we are polite */
	closeConnection();

	return EXIT_SUCCESS;
}

