#Game of tic tac toe. This version is fully functional. Some formatting and code structure details still missing.

gameboard = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]

gameover = 0
player = 1
emptycells = 9

p1_rows = [0,0,0]
p1_columns = [0,0,0]
p1_diagonals = [0,0]

p2_rows = [0,0,0]
p2_columns = [0,0,0]
p2_diagonals = [0,0]

while 1:
    #Request and record moves from two players.
    print "Player " + str(player) + "'s turn to play."
    inputcell = raw_input("Type your move in row,col format: ")
    print "\n"

    playcell = inputcell.split(',')
    playrow = int(playcell[0])
    playcolumn = int(playcell[1])

    if playrow < 0 or playrow > 2 or playcolumn < 0 or playcolumn > 2:
        print "Invalid move input. Row,col must be an int value between 0,0 and 2,2\n"
    else:
        currentmove = gameboard[playrow][playcolumn]

        if currentmove != 0:
            print "Invalid move. Cell has already been played\n"
        else:
            if player == 1:
                gameboard[playrow][playcolumn] ='X'

                p1_rows[playrow] = p1_rows[playrow] + 1
                p1_columns[playcolumn] = p1_columns[playcolumn] + 1
                if (playrow == playcolumn):
                    p1_diagonals[0] = p1_diagonals[0] + 1
                if (playrow - playcolumn == 2) or (playcolumn - playrow == 2) or (playrow == 1 and playcolumn == 1):
                    p1_diagonals[1] = p1_diagonals[1] + 1

                player = 2
                emptycells = emptycells - 1
            else:
                gameboard[playrow][playcolumn] = 'O'

                p2_rows[playrow] = p2_rows[playrow] + 1
                p2_columns[playcolumn] = p2_columns[playcolumn] + 1
                if (playrow == playcolumn):
                    p2_diagonals[0] = p2_diagonals[0] + 1
                if (playrow - playcolumn == 2) or (playcolumn - playrow == 2) or (playrow == 1 and playcolumn == 1):
                    p2_diagonals[1] = p2_diagonals[1] + 1

                player = 1
                emptycells = emptycells - 1

        print "row/col   0   1   2",
        i = 0
        for row in gameboard:
            print "\n" + str(i) + "      ",
            i = i + 1
            for cell in row:
                print "  " + str(cell),
        print "\n"

        for row in p1_rows:
            if row == 3:
                print "Player 1 WINS\n"
                gameover = 1
                break
        for column in p1_columns:
            if column == 3:
                print "Player 1 WINS\n"
                gameover = 1
                break
        for diagonal in p1_diagonals:
            if diagonal == 3:
                print "Player 1 WINS\n"
                gameover = 1
                break
        for row in p2_rows:
            if row == 3:
                print "Player 2 WINS\n"
                gameover = 1
                break
        for column in p2_columns:
            if column == 3:
                print "Player 2 WINS\n"
                gameover = 1
                break
        for diagonal in p2_diagonals:
            if diagonal == 3:
                print "Player 2 WINS\n"
                gameover = 1
                break

        if gameover == 1:
            break
        if emptycells == 0:
            print "Game over. Result: DRAW\n"
            break

