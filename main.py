from graphics import *

def main():
    b = [[0,0,0], [0,0,0], [0,0,0]]
    win = GraphWin("Calendar", 600, 600)
    board(win)
    i = 0
    while(i < 9 and w(b)):
        clickPoint = win.getMouse()
        if(i % 2 == 0):
            Xs(win, clickPoint,b)
            print(b)
        else:
            Os(win, clickPoint,b)
            print(b)
        i += 1

    
    #exec(open(hack.py).read())
    input("press enter to close")
    

def Os(win, clickPoint,b):
    
    if(clickPoint.getX() <= 200):
        if(clickPoint.getY() <= 200):
            drawO(win, Point(100, 100))
            b[0][0] = 2
        elif(clickPoint.getY() <= 400):
            drawO(win, Point(100, 300))
            b[0][1] = 2
        else:
            drawO(win, Point(100, 500))
            b[0][2] = 2
    elif(clickPoint.getX() <= 400):
        if(clickPoint.getY() <= 200):
            drawO(win, Point(300, 100))
            b[1][0] = 2
        elif(clickPoint.getY() <= 400):
            drawO(win, Point(300, 300))
            b[1][1] = 2
        else:
            drawO(win, Point(300, 500))
            b[1][2] = 2
    else:
        if(clickPoint.getY() <= 200):
            drawO(win, Point(500, 100))
            b[2][0] = 2
        elif(clickPoint.getY() <= 400):
            drawO(win, Point(500, 300))
            b[2][1] = 2
        else:
            drawO(win, Point(500, 500))
            b[2][2] = 2


def Xs(win, clickPoint, b):
   
    if(clickPoint.getX() <= 200):
        if(clickPoint.getY() <= 200):
            drawX(win, Point(100, 100))
            b[0][0] = 1
        elif(clickPoint.getY() <= 400):
            drawX(win, Point(100, 300))
            b[0][1] = 1
        else:
            drawX(win, Point(100, 500))
            b[0][2] = 1
    elif(clickPoint.getX() <= 400):
        if(clickPoint.getY() <= 200):
            drawX(win, Point(300, 100))
            b[1][0] = 1
        elif(clickPoint.getY() <= 400):
            drawX(win, Point(300, 300))
            b[1][1] = 1
        else:
            drawX(win, Point(300, 500))
            b[1][2] = 1
    else:
        if(clickPoint.getY() <= 200):
            drawX(win, Point(500, 100))
            b[2][0] = 1
        elif(clickPoint.getY() <= 400):
            drawX(win, Point(500, 300))
            b[2][1] = 1
        else:
            drawX(win, Point(500, 500))
            b[2][2] = 1


def board(win):
    l = Line(Point(200,600), Point(200, 0))
    l.draw(win)
    l = Line(Point(400,600), Point(400, 0))
    l.draw(win)
    l = Line(Point(600,200), Point(0, 200))
    l.draw(win)
    l = Line(Point(600,400), Point(0, 400))
    l.draw(win)

def drawX(win, click):
    px = click.getX()
    py = click.getY()
    l = Line(Point(px + 40, py + 40), Point(px-40, py - 40))
    l.draw(win)
    l = Line(Point(px - 40, py + 40), Point(px + 40, py - 40))
    l.draw(win)

def drawO(win, click):
    px = click.getX()
    py = click.getY()
    c = Circle(Point(px, py), 40)
    c.draw(win)

def w(b):
    for i in range(len(b)):
        if(b[i][0] == b[i][1] and b[i][1] == b[i][2] and b[i][1] != 0):
            print("F")
            return False
    for i in range(len(b[0])):
        if(b[0][i] == b[1][i] and b[1][i] == b[2][i] and b[1][i] != 0):
            print("F")
            return False
    if(b[0][0] == b[1][1] and b[1][1] == b[2][2] and b[1][1] != 0):
        print("F")
        return False
    if(b[2][0] == b[1][1] and b[1][1] == b[0][2] and b[1][1] != 0):
        print("F")
        return False
    return True


    


main()