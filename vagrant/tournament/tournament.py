#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute('''

                DELETE
                    FROM matches;

              ''')
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute('''

                DELETE
                    FROM players;

              ''')
    DB.commit()
    DB.close()


def deleteByes():
    """Remove a BYE when unnecessary."""
    DB = connect()
    c = DB.cursor()
    c.execute('''

                DELETE
                    FROM players
                        WHERE id IN
                            (
                                SELECT id
                                    FROM players
                                        WHERE name = 'BYE'
                            );

              ''')
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute('''

                SELECT COUNT(id) AS num
                    FROM players;

              ''')
    players = c.fetchone()[0]
    DB.close()
    return players


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute('''

                INSERT INTO players
                           (name)
                    VALUES (%s);

              ''', (name,))
    DB.commit()
    DB.close()


def evenCheck():
    """Insert a BYE if number of players is not even."""
    DB = connect()
    c = DB.cursor()
    s = countPlayers()
    # Check for even players.
    if (+s % 2) == 0:
        DB.close()
    # Check whether BYE already exists.
    else:
        c.execute('''

                SELECT exists
                    (

                        SELECT true
                            FROM players
                                WHERE name = 'BYE'

                    );

                  ''')
        rows = c.fetchall()
        tf = [row[0] for row in rows]
        if tf == [True]:
            deleteByes()
            DB.close()
        # Add BYE if needed.
        elif tf == [False]:
            registerPlayer("BYE")
            DB.close()
        else:
            DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    evenCheck()
    DB = connect()
    c = DB.cursor()
    c.execute('''

                SELECT *
                    FROM v_standings;

                 ''')
    standing = c.fetchall()
    DB.close()
    return standing


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    result = '''

                INSERT INTO matches
                           (winner, loser)
                    VALUES (%s, %s);

              '''
#    won = '''
#
#                UPDATE players
#                    SET wins = wins+1,
#                        matches = matches+1
#                    WHERE id = %s;
#
#          '''
#    lost = '''
#
#                UPDATE players
#                    SET matches = matches+1
#                    WHERE id = %s;
#
#           '''
    c.execute(result, (winner, loser,))
#    c.execute(won, (winner,))
#    c.execute(lost, (loser,))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    evenCheck()
    DB = connect()
    c = DB.cursor()
    c.execute('''

                SELECT id, name
                    FROM v_standings
                    Order by wins desc;

              ''')
    pairings = []
    # Pull rows and append two at a time from aggregating view.
    each_pair = c.fetchmany(2)
    while each_pair:
        pairing = []
        for row in each_pair:
            pairing += list(row)
        pairings.append(tuple(pairing))
        each_pair = c.fetchmany(2)
    DB.close()
    return pairings
