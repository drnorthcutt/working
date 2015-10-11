#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("'); delete from players; --")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("'); delete from players; --")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testExtras():
    """Test extra credit options BYE and Swiss Pairings with BYE

    If uneven players are registered, create BYE and pair randomly.  Use pair
    to create first round, insert results and pair again.
    """
    # Clear data:
    deleteMatches()
    deletePlayers()
    # Register players
    players = ["D Vader", "L Skywalker", "P Leia", "R2D2", "J Hutt", "Yoda",
               "H Solo"]
    [registerPlayer(x) for x in players]
    # Test BYE creation for uneven players
    prior = countPlayers()
    pairings = swissPairings()
    print "Original players:"
    print prior
    print ""
    print "Current players:"
    after = countPlayers()
    print after
    if (after) != 8:
        raise ValueError(
            "BYE not created!")
    if (after) == 8:
        print ""
        print "BYE created succcessfully."
    print ""
    # Test pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    pairings = swissPairings()
    if len(pairings) != 4:
        raise ValueError(
            "For 8 players, swissPairings should return 4 pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4),
    (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id5, id7])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "After one match, players with one win are paired."


def test_omw():
    """Test Opponent Match Wins

    If players have same number of wins, OMW ranks players by opponent
    wins. This test case checks for OMW proper ordering.
    """
    # Clear data:
    deleteMatches()
    deletePlayers()
    # Register players:
    players = ["Robert April", "Jonathan Archer", "Willard Decker",
               "Rachel Garrett", "John Harriman", "Edward Jellico",
               "James T. Kirk", "Jean-Luc Picard", "Christopher Pike",
               "William T. Riker"]
    [registerPlayer(x) for x in players]
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8, id9, id10] = [row[0] for row in standings]
    # Create matches:
    reportMatch(id10, id9)
    reportMatch(id1, id8)
    reportMatch(id2, id7)
    reportMatch(id3, id6)
    reportMatch(id4, id5)
    reportMatch(id10, id1)
    reportMatch(id2, id3)
    reportMatch(id4, id6)
    reportMatch(id5, id7)
    reportMatch(id8, id9)
    reportMatch(id10, id2)
    reportMatch(id1, id3)
    reportMatch(id6, id8)
    reportMatch(id6, id2)
    # Check results
    standings = finalResults()
    print ""
    print "Results: (playerId, name, wins, matches, score, match wins, omw)"
    print standings
    print ""
    correct_results = frozenset([id10, id4, id1, id6, id2, id5, id3, id8, id9, id7])
    user_results = frozenset([row[0] for row in standings])
    if correct_results != user_results:
        print "Expected:", correct_results
        print "Received:", user_results
        raise ValueError("Incorrect player rank!")
    print "OMW is reporting correctly"


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print ""
    print "Test Extra Credit:"
    print ""
    testExtras()
    test_omw()
    print ""
    print "Success!  All tests pass!"


