from tournament import *

def test():
    print ""
    print "1 -- player standings"
    print "p -- to register players"
    print "c -- clear players  *note*  Players cannot be cleared if they have matches."
    print "m to clear matches  *note* Clearing matches will not clear players."
    print "Press any other key to exit"
    print "bye -- delete bye"
    print ""
    answer = raw_input("What would you like to do? \n")
    if answer == "1":
        standings = playerStandings()
        current = countPlayers()
        print ""
        print standings
        print ""
        print "Current number of players:"
        print current
        test()
    elif answer == "p":
        print ""
        number = countPlayers()
        print "Current Players:"
        print number
        print ""
        player = raw_input("Enter a new Player's name: \n")
        registerPlayer(player)
        number2 = countPlayers()
        print "New current players:"
        print number2
        print ""
        test()
    elif answer == "m":
        print ""
        print "WARNING:"
        print "THIS WILL DELETE ALL MATCHES!"
        print ""
        player = raw_input("Are you sure? [ y or n] \n")
        if player == "y":
            deleteMatches()
            num = countPlayers()
            print ""
            print "Current players:"
            print num
            print ""
            test()
        else:
            print ""
            print "Okay... Going back..."
            print ""
            test()
    elif answer == "c":
        print ""
        print "WARNING:"
        print "THIS WILL DELETE ALL PLAYERS!"
        print ""
        player = raw_input("Are you sure? [ y or n] \n")
        if player == "y":
            deletePlayers()
            num = countPlayers()
            print ""
            print "Current players:"
            print num
            print ""
            test()
        else:
            print ""
            print "Okay... Going back..."
            print ""
            test()
    elif answer == "bye":
        deleteByes()
        test()
    elif answer == 3:
        end

if __name__ == '__main__':
    test()
