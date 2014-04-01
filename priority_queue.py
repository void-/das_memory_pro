class PriorityQueue(object):
  """Priority queue is a type of min-heap that stores entries based upon datetime objects.

  Priority queue supports the following operations with the following run times.
    min() return the entry with the minimum time.   O(1)
    removeMin() remove the entry with the minimum time and return it. O(log(n))
    insert() insert a new entry into the priority queue. It must have a field named time. O(log(n))

  Member Variables:
    heap python list that stores all the entries.
      The rule is that every child of an entry has a greater time.
      this heap has a None entry at index 1, so that parent/child indicies work well.
       0 1 2 3 4 5 6
      [X,A,B,C,D,E,F]
      As children are B and c
      Bs and Cs parents are A
      Bs children are D and E
      Cs children are F

      get the children of node n: 2n, 2n+1
      get the parent of node n: n//2
       
  """

  def __init__(self):
    """Initialize an empty priority queue."""

    self.heap = [None,]

  def __len__(self):
    """Return the number of entries in the priority queue.
    
    Since the heap array always has an entry at index 0, subtract 1 from its length.

    """
    return len(self.heap) - 1

  def __str__(self):
    """Return the string representation of the priority queue."""

    return str(self.heap)

  def __iter__(self):
    """Non-destructively iterate over all the entries in sorted order."""

    hc = PriorityQueue()
    #copy the internal heap
    hc.heap = list(self.heap)
    t = hc.removeMin()
    #great place for a do-while
    while t:
      yield t
      t = hc.removeMin()

  def min(self):
    """Return the entry with the minimum time. If this priority queue is empty, return None."""

    if len(self) > 0:
      return self.heap[1]

  def removeMin(self):
    """Remove the entry with the minimum time value in the priority queue.

    If this priority queue is empty, return None.
    Insert the last entry in the heap into the root.
    Bubble it down the heap until it satisfies the heap-order property.
    If there is the case that the entry being bubbled is greater than both children,
    swap with the lesser of the two.

    TODO: Fix the excessively long lines: these are for checking list index bounds

    """
    if len(self) == 0:
      return
    save = self.heap[1] #save the entry to return it later
    if len(self) == 1:
      return self.heap.pop()
    #poping index 1 and then trying to assign to it would cause an error
    self.heap[1] = self.heap.pop() #make the initial swap
    entryNo = 1

    #Bubble down the heap
    while entryNo < len(self) and ((leftChild(entryNo) <= len(self) and self.heap[entryNo] > self.heap[leftChild(entryNo)]) or (rightChild(entryNo) <= len(self) and self.heap[entryNo] > self.heap[rightChild(entryNo)])):
      #greater than both
      if (leftChild(entryNo) <= len(self) and self.heap[entryNo] > self.heap[leftChild(entryNo)]) and (rightChild(entryNo) <= len(self) and self.heap[entryNo] > self.heap[rightChild(entryNo)]):
        if self.heap[leftChild(entryNo)] < self.heap[rightChild(entryNo)]:
          #swap left
          self.heap[leftChild(entryNo)], self.heap[entryNo] = self.heap[entryNo], self.heap[leftChild(entryNo)]
          entryNo = leftChild(entryNo)
        else:
          #swap right
          self.heap[rightChild(entryNo)], self.heap[entryNo] = self.heap[entryNo], self.heap[rightChild(entryNo)]
          entryNo = rightChild(entryNo)
      elif rightChild(entryNo) <= len(self) and self.heap[entryNo] > self.heap[rightChild(entryNo)]:
        #swap right
        self.heap[rightChild(entryNo)], self.heap[entryNo] = self.heap[entryNo], self.heap[rightChild(entryNo)]
        entryNo = rightChild(entryNo)
      else:
        #swap left
        self.heap[leftChild(entryNo)], self.heap[entryNo] = self.heap[entryNo], self.heap[leftChild(entryNo)]
        entryNo = leftChild(entryNo)
    return save

  def insert(self, entry):
    """Insert an item into the priority queue.
    
    Insert an item into the last free index in the priority queue.
    The heap-order property must still be satisfied, so the new entry 
    must be bubbled up the heap until its value is less than that of its
    parent.

    """
    self.heap.append(entry)
    entryNo = len(self) #index for the item just inserted

    if entryNo == 1: #dont do anything if there's just 1 entry
      return

    #while the new entry has not yet reached the top of the heap and it hasnt satisfied the heap-order property
    while entryNo > 1 and entry < self.heap[parent(entryNo)]: 
      #swap entry and parent
      self.heap[entryNo], self.heap[parent(entryNo)] =  self.heap[parent(entryNo)], self.heap[entryNo]
      entryNo = parent(entryNo)

def parent(n):
  return n//2

def leftChild(n):
  return n*2

def rightChild(n):
  return n*2 +1
