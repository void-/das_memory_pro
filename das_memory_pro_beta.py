import curses
import curses.textpad
import re
import priority_queue
import file_controller

class Menu(object):
  """Menu object defines an abstract, user-interactive menu.

  This class is not meant to be instantiated, but provide an abstract base for
  subclasses.

  Class Variables:
    NAME string representing human-readable name of the menu.
    ENTER ascii character representing return key.
    ESC ascii character representing escape key.
    QUIT method Id for the quit() method.
    HELP method Id for the displayHelp() method.
    Screen curses window object representing the entire screen.
    MAX_Y maximum y coordinate value of the Screen.
    MAX_X maximum x coordinate value of the Screen.
    HelpWindow curses window object for displaying help menu.

  Member Variables:
    bindings python dictionary mapping keys to method ids.
    _quit boolean that looping is dependant on.

  """
  NAME = "Menu"
  ENTER = "\n"
  ESC = "\x1B"
  BACKSPACE = "KEY_BACKSPACE"
  QUIT = "Quit."
  HELP = "Help."
  Screen = curses.initscr()
  MAX_Y = Screen.getmaxyx()[0]
  MAX_X = Screen.getmaxyx()[1]
  HelpWindow = curses.newwin(8, 80, 1, 0)

  def __init__(self):
    """Initialize a new Menu.

    Construct a default bindings dictionary and set _quit to False. Clear the
    main screen.

    """
    self.bindings = {"q":self.QUIT, "h":self.HELP}
    self._quit = False
    self.Screen.clear()
    self.Screen.addstr(0,0, self.NAME)

  def execute(self, cmd):
    """Given a string command, find which method it corresponds and execute.

    Lookup the given command in the bindings dictionary and execute the
    corresponding method. If the command cannot be found, execute some default
    action.

    """
    mId = self.bindings[cmd] if (cmd in self.bindings) else -1

    if mId == self.QUIT:
      self.quit()
    elif mId == self.HELP:
      self.displayHelp()
    else: #Id not found: do nothing
      pass

  def getChar(self):
    """Return a character received via character based input.
    
    In the case of pressing the backspace key, the multi-character string at
    Menu.BACKSPACE is returned.

    """
    return self.Screen.getkey()

  def getLine(self):
    """Return an entire line of input received via character based input.
    
    Inputed characters will not be echoed to the terminal.

    """
    result = ""
    c = self.getChar()
    #Great place for a do-while
    while c != self.ENTER:
      if c == self.BACKSPACE:
        result = result[:-1]
      else:
        result+=c
      c = self.getChar()
    return result

  def loop(self):
    """Loop and execute user input until the _quit boolean is set to false."""

    while (not self._quit):
      self.execute(self.getChar())

  def quit(self):
    """Set the _quit boolean to False, causing loop() to terminate."""

    self._quit = True

  def displayHelp(self):
    """Display key bindings to the user."""

    self.HelpWindow.clear()
    self.HelpWindow.addstr(0, 0, str(self.bindings))
    self.HelpWindow.refresh()

class MainMenu(Menu):
  """MainMenu subclasses Menu to provide a specific implementation.
  
  Class Variables:
    NAME string representing human-readable name of the menu.
    MOTD string to display when the program is first executed.
    MOTD_Y y location on the screen to display MOTD.
    MOTD_X x location on the screen to display MOTD.
    SEARCH method id for the searchMenu() method.
    CREATE method if for the createMenu() method.

  Member Variables:
    env Environment object that contains file objects.

  """
  NAME = "Main Menu"
  MOTD = "Das Memory Pro BETA: void-"
  MOTD_Y = Menu.MAX_Y // 2
  MOTD_X = Menu.MAX_X // 2
  PASS_Y = Menu.MAX_Y - 2
  SEARCH = "Search Menu."
  CREATE = "Create Menu."

  def __init__(self):
    """Initialize a new MainMenu and create a new Envivonment instance.
    
    Instantiating a new MainMenu is critical to the execution of the entire
    program. Configure the curses window and diplay MainMenu.MOTD to the
    screen. A corresponding call to MainMenu.loop() is necessary to reset the
    terminal to its previous configuration.

    """
    Menu.__init__(self)
    self.bindings["f"] = self.SEARCH
    self.bindings["n"] = self.CREATE
    #Clear the screen and write MOTD to the center
    curses.cbreak()
    self.Screen.keypad(1)
    curses.noecho()
    curses.curs_set(0)#Invisible cursor

    self.Screen.addstr(self.MOTD_Y, self.MOTD_X, self.MOTD)
    self.Screen.addstr(self.PASS_Y, 0, "Enter password:")
    self.Screen.refresh()
    self.env = file_controller.Environment.setup(self.getLine())
    self.Screen.deleteln()
    self.Screen.refresh()

  def loop(self):
    """Wrapper to Menu.loop(), but resets the terminal upon return."""

    Menu.loop(self)
    curses.nocbreak()
    self.Screen.keypad(0)
    curses.echo()
    curses.endwin()

  def execute(self, cmd):
    """Given a string command lookup and execute the corresponing method."""

    mId = self.bindings[cmd] if (cmd in self.bindings) else -1

    if mId == self.SEARCH:
       self.searchMenu()
    elif mId == self.CREATE:
       self.createMenu()
    else: #Not found, check super
       Menu.execute(self, cmd)

  def searchMenu(self):
    """Construct an anonymous SearchMenu and loop."""

    SearchMenu(self.env).loop()
    self.Screen.clear()
    self.Screen.addstr(0, 0, self.NAME)
    self.Screen.refresh()

  def createMenu(self):
    """Construct an anonymous CreateMenu and loop."""

    CreateMenu(self.env).loop()
    self.Screen.clear()
    self.Screen.addstr(0, 0, self.NAME)
    self.Screen.refresh()

class SearchMenu(Menu):
  """Search Menu class defines a search menu.

  SearchMenu inherits from Menu the loop() method which is the main driver for
  this class. For standard usage, instantiate a new SearchMenu object given a
  reference to an Environment object and call the loop() method. loop() will
  take in user input and make calls to execute() based up the overridden values
  stored in bindings.

  Class Variables:
    NAME string representing human-readable name of the menu.
    INSERT method Id for the insert() method.
    SELECTDOWN method Id for the selectDown() method.
    SELECTUP method Id for the selectUp() method.
    SELECTFIRST method Id for the selectFirst() method.
    SELECTLAST method Id for the selectLast() method.
    SELECTMID method Id for the selectMid() method.
    DETAIL method Id for the detail() method.
    QUERY_Y y location on the screen to display the query window.
    RESULTS_Y y location on the screen to display the results window.
    DETAIL_Y y location on the screen to display the detail window.
    MODE_X x location on the screen to display the mode window.
    SELECT_NAME string representing select mode name.
    INSERT_NAME string representing insert mode name.

  Member Variables:
    env reference to the Environment instance for the session.
    topics reference to the topics stored in the Index object.
      This is to reduce the length of the name of the variable.
    searchResults python list containing FindTopic objects related to what the
      user has recently searched.
    selectCursor currently selected index in the searchResults list.
      A value of -1 indicates no selection.
    resultsWindow curses window object to display searchResults.
    queryWindow curses window object to display the query during searching.
    detailWindow curses window object to display corpora from detail().
    modeWindow curses window to display the current user mode.

  """
  NAME = "Search Menu"
  INSERT = "Enter insert mode to search."
  SELECT_DOWN = "Select down."
  SELECT_UP = "Select up."
  SELECT_FIRST = "Select first."
  SELECT_LAST = "Select last."
  SELECT_MID = "select middle."
  DETAIL = "View Corpus."

  QUERY_Y = Menu.MAX_Y - 1
  RESULTS_Y = Menu.MAX_Y // 4
  DETAIL_Y = Menu.MAX_Y // 2
  MODE_X = int(Menu.MAX_X * .80)
  SELECT_NAME = "select"
  INSERT_NAME = "insert"
  INSERT_TIP = "Press esc to re-enter normal mode."

  def __init__(self, env):
    """Initialize a new SearchMenu given an Environment instance.
    
    Create new bindings for all the methods specific to SearchMenu. Instantiate
    a new screen for displaying results.

    """
    Menu.__init__(self)
    self.env = env
    self.topics = env.index.entries
    self.searchResults = []
    self.selectCursor = -1
    self.bindings["i"] = self.INSERT
    self.bindings["j"] = self.SELECT_DOWN
    self.bindings["k"] = self.SELECT_UP
    self.bindings["H"] = self.SELECT_FIRST
    self.bindings["L"] = self.SELECT_LAST
    self.bindings["M"] = self.SELECT_MID
    self.bindings[self.ENTER] = self.DETAIL

    self.resultsWindow = curses.newwin(10, 32, self.RESULTS_Y, 0)
    self.queryWindow = curses.newwin(1, 80, self.QUERY_Y, 0)
    self.detailWindow = curses.newwin(5, 80, self.DETAIL_Y, 0)
    self.modeWindow = curses.newwin(1, len(self.SELECT_NAME)+1, self.QUERY_Y, \
      self.MODE_X)
    self.modeWindow.addstr(0, 0, self.SELECT_NAME)
    self.modeWindow.refresh()

  def execute(self, cmd):
    """Given a string as a command, execute the corresponding method."""

    mId = self.bindings[cmd] if (cmd in self.bindings) else -1

    if mId == self.INSERT:
      self.insert()
    elif mId == self.SELECT_DOWN:
      self.selectDown()
    elif mId == self.SELECT_UP:
      self.selectUp()
    elif mId == self.SELECT_FIRST:
      self.selectFirst()
    elif mId == self.SELECT_LAST:
      self.selectLast()
    elif mId == self.SELECT_MID:
      self.selectMid()
    elif mId == self.DETAIL:
      self.detail()
    else:
      Menu.execute(self, cmd)

  def selectDown(self):
    """Increment the selection cursor by one, selecting the next entry."""

    self.selectCursor += (self.selectCursor < (len(self.searchResults)-1) )
    self.updateCursor()

  def selectUp(self):
    """Decrement the selection cursor by one, selecting the previous entry."""

    self.selectCursor -= (self.selectCursor > 0)
    self.updateCursor()

  def selectFirst(self):
    """Set selection cursor to 0, if it is a valid index of searchResults."""

    self.selectCursor = 0 if len(self.searchResults) else self.selectCursor
    self.updateCursor()

  def selectLast(self):
    """Set selection cursor to the last, valid index of searchResults."""

    self.selectCursor = len(self.searchResults)-1
    self.updateCursor()

  def selectMid(self):
    """Set selection cursor to the middle element if it is a valid index."""

    self.selectCursor = len(self.searchResults)//2 if len(self.searchResults) \
      else self.selectCursor
    self.updateCursor()

  def updateCursor(self):
    """Redraw the selection cursor."""

    if self.selectCursor > -1:
      for j in xrange(self.resultsWindow.getmaxyx()[0]):
        self.resultsWindow.addch(j, 0, " ")
        self.resultsWindow.addstr(self.selectCursor, 0, ">")
      self.resultsWindow.refresh()

  def detail(self):
    """Display the corpus at index selectCursor in searchResults.

    If selectCursor is not at a valid index, do nothing.

    """
    if self.selectCursor > -1:
      self.detailWindow.clear()
      self.detailWindow.addstr(self.env.corpora.getCorpus( \
        self.searchResults[self.selectCursor]))
      self.detailWindow.refresh()

  def insert(self):
    """Accept input from the user and do a real-time, incremental search.

    The users search query is written to a box and the results, or topic names
    are written to resultsWindow.

    """
    MAX_RESULTS = 10
    query = ""
    t = None
    self.detailWindow.clear() #clear detail window
    self.detailWindow.refresh()
    self.HelpWindow.clear()
    self.HelpWindow.addstr(self.INSERT_TIP)
    self.HelpWindow.refresh()
    #Insert mode
    self.modeWindow.addstr(0, 0, self.INSERT_NAME)
    self.modeWindow.refresh()
    #Clear any previous queries
    self.queryWindow.clear()
    self.queryWindow.refresh()
    while True:
      t = self.getChar()
      if t == self.ESC:
        break #dont clear results, save it for selecting through
      else:
        if t == self.BACKSPACE and len(query) > 0:
          query = query[:-1]
        elif t != self.ENTER:
          query+=t
        self.queryWindow.clear()
        self.queryWindow.addstr(query)

        self.searchResults = [] #empty the results list from before
        self.selectCursor = -1 #select nothing
        self.search(query) #mutate self.results

        self.resultsWindow.clear()
        for j in xrange(len(self.searchResults)):
          if j > MAX_RESULTS:
            break
          #add results, each on its own line
          self.resultsWindow.addstr(j, 1, self.searchResults[j].cleanName())
        self.queryWindow.refresh()
        self.resultsWindow.refresh()
    self.modeWindow.addstr(0, 0, self.SELECT_NAME)
    self.modeWindow.refresh()
    self.HelpWindow.clear()
    self.HelpWindow.refresh()

  def search(self, query, left=0, right=-1):
    """Conduct binary search on self.topics and populate searchResults.""" 

    if right == -1:
      right = len(self.topics)
    if left >= right or len(query) == 0:
      self.searchResults = []
      return

    mid = (left+right)//2
    #First match: do some more searching
    if re.match(query, self.topics[mid].name):
      self.searchResults.append(self.topics[mid])
      #linearly search up from the match
      for i in xrange(mid-1,0,-1):
        if re.match(query, self.topics[i].name):
          self.searchResults.append(self.topics[i])
        else:
          break
      #linearly search down from the match
      for i in xrange(mid+1,len(self.topics)):
        if re.match(query, self.topics[i].name):
          self.searchResults.append(self.topics[i])
        else:
          break
    elif query > self.topics[mid].name:
      self.search(query, mid+1, right)
    else:
      self.search(query, left, mid)

class CreateMenu(Menu):
  """CreateMenu defines a Menu at which NewTopics can be created.

  Class Variables:
    NAME string representing human readable name of the CreateMenu.
    INSERT method Id for the insert() method.
    SAVE_AND_QUIT method Id for the saveAndQuit() method.
    NEW_Y y location of the new topics window.
    NEW_X x location of the new topics window.
    INSERT_Y y location of the insertion window.
    INSERT_X x location of the insertion window.

  Member Variables:
    env reference the the Environment instance for the session.
    new iterable, self sorting data structure to hold new topics.

  """
  NAME = "Create Menu"
  INSERT = "Create new topic."
  SAVE_AND_QUIT = "Save and Quit."
  NEW_Y = Menu.MAX_Y // 4
  NEW_X = int(Menu.MAX_X * .65) 
  INSERT_Y = Menu.MAX_Y // 2

  def __init__(self, env):
    """Initialize a new CreateMenu given an Environment instance."""

    Menu.__init__(self)
    self.env = env 
    self.newTopics = priority_queue.PriorityQueue()
    self.bindings["i"] = self.INSERT
    self.bindings["Z"] = self.SAVE_AND_QUIT
    self.newTopicsWindow = curses.newwin(10, 32, self.NEW_Y, self.NEW_X)
    self.nameWindow = curses.newwin(1, 80, self.INSERT_Y, 0)
    self.corpusWindow = curses.newwin(1, 80, self.INSERT_Y+2, 0)

  def execute(self, cmd):
    """Given a string as a command, execute the corresponding method."""

    mId = self.bindings[cmd] if (cmd in self.bindings) else -1

    if mId == self.INSERT:
      self.insert()
    elif mId == self.SAVE_AND_QUIT:
      self.saveAndQuit()
    else: #Not found, check super
      Menu.execute(self, cmd)

  def insert(self):
    """Create a new Topic by accepting a name and corpus from the user."""

    self.Screen.addstr(self.INSERT_Y-1, 0, "enter name")
    self.Screen.refresh()
    box = curses.textpad.Textbox(self.nameWindow)
    curses.curs_set(1)
    self.nameWindow.refresh()
    name = box.edit()

    self.Screen.addstr(self.INSERT_Y+1, 0, "enter corpus")
    self.Screen.refresh()
    box2 = curses.textpad.Textbox(self.corpusWindow)
    self.corpusWindow.refresh()
    corpus = box2.edit()
    curses.curs_set(0)

    #Delete the entered text
    self.corpusWindow.clear()
    self.nameWindow.clear()
    self.corpusWindow.refresh()
    self.nameWindow.refresh()

    self.newTopics.insert(file_controller.NewTopic(name, corpus))
    self.newTopicsWindow.clear()
    j = 0
    for t in self.newTopics:
      self.newTopicsWindow.addstr(j, 0, str(t))
      j+=1
    self.newTopicsWindow.refresh()

  def saveAndQuit(self):
    """Write all the new topics to disk and exit the CreateMenu."""

    #Write only if any NewTopics were created.
    if len(self.newTopics) > 0:
      self.env.insertEntries(self.newTopics)
    self.quit()

if __name__ == "__main__":
  MainMenu().loop()
