#ud197
Project: Swiss Style Tournament
===
###- Daniel R. Northcutt
Overview
---
Demonstrates development of PostgreSQL database schema and Python code to
coordinate and track a Swiss-style tournament.

Swiss-style tournaments allow all participants to play in every round, pairing
each player based on their current records. This ensures that players with
similar records are paired together. Sometimes, it is not possible to pair
players with exactly the same records, in which case they may be paired up or
down. This means playing someone with a slightly worse or slightly better
record.

In some Swiss tournaments, after the regular rounds (determined at the
beginning of the tournament based on the number of players), the top X
(usually 8) players go on to play a single-elimination playoff. When a player
wins in the quarterfinals, they advance to the semi-finals, and so on.

In straight Swiss tournaments, once the Swiss rounds are over the tournament is
complete and prizes are awarded based on the final standings. There is no top
cut or playoff.
#Contents:

[Objectives](#objectives)

[Requirements](#required-libraries-and-dependencies)

[How to](#how-to-run-this-project)

[Extra Credit](#extra-credit-description)
  * [Functionality](#functionality)
  * [Table Design](#table-design)
  * [Column Design](#column-design)
  * [Code Quality](#code-quality)

[Miscellaneous](#miscellaneous)
* [Image](#miscellaneous)
* [Functions added](#functions-added)
* [Views utilized](#views-utilized)

#Objectives

Write server-side code to function as a database driven Swiss style tournament
coordinator.  Must pass a series of tests, including:

1.  Match Deletion
2.  Player Records Deletion
3.  Player Count
4.  Player Registration
5.  Player Standings Tracking
6.  Player Match Tracking
7.  Player Wins Tracking
8.  Player Pairing

Other:
   1.  Meaningful and useful table structure
   2.  Meaningful columns of proper type
   3.  Appropriate SQL injection protection
   4.  Appropriate commenting and README

May also have (for exceeds):

1.  One or more of the following:
	* Prevent rematches between players
    * [x] Allowance for "bye" rounds if players odd.  No more than one per
      tournament for a player.
    * [x] Support draws.
    * [x] Rank according to OMW (Opponent Match Wins) in case of a final standing
      tie.
    * Support for more than one tournament at a time in the database.
2.  [x] Views are used to make queries more concise.
3.  [x] Primary and foreign keys are correctly specified.
4.  [x] All sorting and aggregation performed in the database.


#Required Libraries and Dependencies

[VirtualBox](https://www.virtualbox.org) (5.0.5 was used)

[Vagrant](https://www.vagrantup.com) (1.7.4 was used)

Python v2.*

PostgreSQL

#How to Run this Project


Clone this full repository and ensure the files are all in the same directory.
(if already cloned from the original repository, only this directory is required.)

From the command line, or terminal, navigate to the vagrant from this repository directory, type:

```
vagrant up
```

ssh into the vagrant box:
```
vagrant ssh
```
Navigate to the project sync folder:
```
cd /vagrant/tournament
```

Create the databases and run the database setup files:
(This will delete any other instance of a database called tournament and create
the schema.)
```
psql -f tournament.sql
```

To run the basic project test files:
(Some additional tests added, commented out.)
```
python tournament_test.py
```

To run the added input based mini-tester:
```
python tester.py
```

#Extra Credit Description
####(Image below in Miscellaneous)
###Functionality
Allowance for BYE round if players are odd in number.  Upon checking
playerStandings, or calling swissRounds, a BYE is created with the id 9999 to
make it highly unlikely that a player id will coincide. (Never say never.)

Support Draws with function reportMatchTie, inserting a boolean into the match
table.

Rank according to OMW.  Using the suggested methodology of [Wizards of the Coast](https://www.wizards.com/dci/downloads/tiebreakers.pdf),
players are shown ranking in the final round with full tie breaking in place as:

* score: 3 points for a win, 1 point for a tie, 0 points for a loss, and 3 points for a BYE
* match-wins:  the player's score, discounting BYE points, divided by the number
of matches the player played multiplied by 3 (or the maximum points possible per round),
discounting BYE matches.
* omw:  opponent match wins, the average of the match-wins of a player's opponents,
discounting an opponent's BYE rounds, divided by the number of matches played by the player,
discounting any BYE matches.

Additional input-based mini-tester added as tester.py

###Table Design
Two tables:
* players
    * id
    * name
* matches
    * id
    * winner
    * loser
    * draw

Multiple views utilized to handle all stats. (Specifically listed below, in Miscellaneous)


###Column Design

Primary keys used on players.id and matches.id
Foreign keys used on matches.winner and matches.loser to reference players.id

###Code Quality

Obviously, much of this is subjective, but...

All aggregating performed in the Database.

Additionally, mixed Case formatting was utilized in the original files given for
functions.  This predetermined style was adhered to throughout the project, but
was painful.



#Miscellaneous

Shows finalResults, with one Draw, a BYE, matchwins, and OMW.

<img src="https://github.com/drnorthcutt/working/blob/extras/vagrant/tournament/img/omw.png" alt="OMW" style="width:800;height:243">

In this example, Riker shows 3 wins and 1 draw over 4 matches, so:

    (3 x 3 points) + (1 x 1 point) for a total score of 10.
    4 matches x 3 possible points per match for a total possible match points of 12.
    10 divided by 12 = 0.8333 repeating, for a matchwins of 83 1/3%.
    His omw is then calculated by the average of his opponent's matchwins.
    In this case, Pike, April, and Archer twice, or (approximately):
        0.33 + 0.6666 + 0.4666 + 0.4666 = 1.9298
    divided by his total matches played.
    Therefore:
        1.9298 divided by 4 for an omw of 0.4825 or 48.25%.

In this example output, Chester Tester had 1 BYE.

    His matchwins, instead of 6 points divided by 3 matches (3 x 3),
    (or 6 / 9 = 0.66 repeating) show properly, disregarding the BYE as:
        3 points divided by 2 matches (2 x 3) = 3 / 6 = 0.5



###Functions added
In addition to the standard functions, the below were added:


deleteByes():

    Remove a BYE when unnecessary.

    This assumes that playerStandings was checked before rounds were played.
    Once a round has been played and a BYE win has been issued, it cannot be
    deleted due to Foreign Key constraints.

evenCheck():

    Insert a BYE if number of players is not even.

    BYE id is set to 9999 to drastically lower the likelihood that any player
      will already have this id number.

reportMatchTie(player1, player2):

    Records the tied outcome of a single match between two players.

    Args:
      player1:  the id number of either player in a tied match
      player2:  the id number of the other player in a tied match

finalResults():

    Return the full standings with tie breakers.

    Shows full standings with calculated scoring, match wins, and opponent
    match wins.  Used at the end of a tournament to completely rank players
    when scores may be tied.  At least one round should be played and reported
    (two rounds if a BYE has been used) before calling this function.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches, score,
      match wins, opponent match wins):

        id:
          the player's unique id (assigned by the database)

        name:
          the player's full name (as registered)

        wins:
          the number of matches the player has won

        draws:
          the number of draws for each player

        matches:
          the number of matches the player has played

        score:
          the points the player has won, calculated as 3 points for a win, 0
          points for a loss, 3 points for a BYE, 1 point for a tie

	   match wins:
          the player's score divided by three times the number of matches the
          player has played, discounting both score and match for a round when
          a player recieved a BYE. If less than 0.33, then 0.33 is displayed.
          (Used to rank players that have a tied score)

        omw:
          opponent match wins, the average match wins of the opponents of a
          player. Calculated by the sum of the match wins of each opponent of
          the player (or 0.33 if an opponent has a match wins score of less)
          divided by the number of rounds played by the player (Used to rank
          players that have both a tied score and match wins)

###Views utilized

    v_wins
        Calculate number of wins

    v_ties
        Calculate number of draws

    v_match_counts
        Calculate number of matches per each player

    v_standings
        Display standings

    v_score
        Calculate score (wins = 3, losses =0, draws = 1)

    v_byeScore
        Calculate scores from BYES as a negative number, to remove from match points

    byeGone
        Calculate scores without BYE wins. (Used only for matchwins and omw.)

    v_matchBye
        Calculate BYE match total

    matchByeGone
        Calculate player match totals without BYE matches. (Used only for match wins and omw.)

    v_matchwins
        Display Match-wins Corrected for BYES

    v_omw
        Calculate Opponent match wins

    v_results
        Aggregate Final player results with tie breakers.
