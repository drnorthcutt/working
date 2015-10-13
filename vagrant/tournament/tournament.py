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
    """Remove a BYE when unnecessary.

    This assumes that playerStandings was checked before rounds were played.
    Once a round has been played and a BYE win has been issued, it cannot be
    deleted due to Foreign Key constraints.
    """
    DB = connect()
    c = DB.cursor()
    c.execute('''

                DELETE
                    FROM players
                        WHERE id = 9999;

              ''')
    DB.commit()
    DB.close()


def countPlayers():
    """Return the number of players currently registered."""
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
    """Add a player to the tournament database.

    The database assigns a unique serial id number for the player.

    Args:
      name: the full name of a player (need not be unique).
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
    """Insert a BYE if number of players is not even.

    BYE id is set to 9999 to drastically lower the likelihood that any player
    will already have this id number.
    """
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
                                WHERE id = 9999

                    );

                  ''')
        rows = c.fetchall()
        tf = [row[0] for row in rows]
        if tf == [True]:
            deleteByes()
            DB.close()
        # Add BYE if needed.
        elif tf == [False]:
            c.execute('''

                INSERT INTO players
                           (id, name)
                    VALUES (%s, %s);

              ''', (9999, 'BYE',))
            DB.commit()
            DB.close()
        else:
            DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the unique id of a player (assigned by the database)
        name: the full name of a player (as registered)
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
    c.execute(result, (winner, loser,))
    DB.commit()
    DB.close()


def reportMatchTie(player1, player2):
    """Records the tied outcome of a single match between two players.

    Args:
      player1:  the id number of either player in a tied match
      player2:  the id number of the other player in a tied match
    """
    DB = connect()
    c = DB.cursor()
    result = '''

                INSERT INTO matches
                           (winner, loser, draw)
                    VALUES (%s, %s, %s);

             '''
    c.execute(result, (player1, player2, 'True',))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.  For uneven players, evenCheck adds a BYE
    player.

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


def finalResults():
    """Return the full standings with tie breakers.

    Shows full standings with calculated scoring, match wins, and opponent
    match wins.  Used at the end of a tournament to completely rank players
    when scores may be tied.  At least one round should be played and reported
    (two rounds if a BYE has been used) before calling this function.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches, score,
      match wins, opponent match wins):

        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        draws: the number of draws for each player
        matches: the number of matches the player has played
        score: the points the player has won, calculated as 3 points for a win,
            0 points for a loss, 3 points for a BYE, 1 point for a tie
        match wins: the player's score divided by three times the number of
            matches the player has played, discounting both score and match for
            a round when a player recieved a BYE. If less than 0.33, then 0.33
            is displayed.  (Used to rank players that have a tied score)
        omw: opponent match wins, the average match wins of the opponents of a
            player. Calculated by the sum of the match wins of each opponent
            of the player (or 0.33 if an opponent has a match wins score of
            less) divided by the number of rounds played by the player (Used to
            rank players that have both a tied score and match wins)
    """
    DB = connect()
    c = DB.cursor()
    c.execute('''

                SELECT *
                    FROM v_results;

              ''')
    standing = c.fetchall()
    DB.close()
    return standing
