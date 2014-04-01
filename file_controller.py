import xor
from random import randint

class Index(object):
  """Index file controller for specialized reads and writes to an .index file.

  Index unifies and abstracts all reads and writes to an .index file. It acts 
  as a controller and stores data about the size of entries in an .index file 
  so that other functions don't need to know this information. All data that 
  comes out of Index are FindTopics rather than raw bytes.

  Class Variables:
    _NAME_LENGTH the size(in bytes) of a name of an entry in an .index file.
    _OFFSET_LENGTH the size/width of the numerical byte offset for a topic.
    _END_BYTE_LENGTH the width of the numerical ending byte for a topic.
    _ENTRY_LENGTH the total size(in bytes) of an entry in an .index file.
    OFFSET_BASE the radix of the offset.

  Member Variables:
    _filestream the actual .index file-like object to read and write from.
      This object must support a reOpen() method.
    _entries tuple containing all entries in .index.
      This has a value of None until the 'entries' field is accessed.
      When _write() is called, the entries are no longer accurate; _entries
      will then have a value of None.

  """

  _NAME_LENGTH = 32
  _OFFSET_LENGTH = 6
  _END_BYTE_LENGTH = 6
  _ENTRY_LENGTH = _NAME_LENGTH + _OFFSET_LENGTH + _END_BYTE_LENGTH
  OFFSET_BASE = 16

  def __init__(self, filestream):
    """Initialize an Index object given an extended file object."""

    self._filestream  = filestream
    self._entries = None

  def _setWrite(self):
    """Reopen the internal file object for write mode.
    
    If _filestream is already opened in 'w' mode, nothing happens.
    
    """
    self._filestream = self._filestream.reOpen("w")

  def _setRead(self):
    """Reopen the internal file object for read mode and flush the I/O buffer.
    
    If _filestream is already opened in 'r' mode, nothing happens.

    """
    self._filestream = self._filestream.reOpen("r")

  def close(self):
    """Close and Flush the internal filestream of the Index."""

    self._filestream.close()

  @property
  def entries(self):
    """Lazily load all entries in the .index file into memory.

    Return a sorted tuple of FindTopic objects.
    """

    if not self._entries:
      self._entries = tuple(self._allEntries())
    return self._entries

  def _nextEntry(self):
    """Return the next entry in the index file.

    Read from the .index file and return a FindTopic object representing the 
    next topic entry in the .index file. If there are no more entries within 
    the .index file, return None.

    """
    self._setRead()
    name = self._filestream.read(self._NAME_LENGTH)
    offset = self._filestream.read(self._OFFSET_LENGTH)
    endset = self._filestream.read(self._END_BYTE_LENGTH)
    if name and offset and endset:
      return FindTopic(name, offset, endset)

  def _allEntries(self):
    """Yield a generator over all the entries in the .index file.
    
    _allEntries makes repreated calls to _nextEntry() and returns FindTopic
    objects. The loop that yields data is conditional upon whether the next
    FindTopic object evaluates to a False value(None as returned upon failure
    of _nextEntry()). 

    """
    #Seek to the beggining
    self._filestream.seek(0)
    tempEntry = self._nextEntry()
    #This would be a great place for a do-while
    while(tempEntry):
      yield tempEntry
      tempEntry = self._nextEntry()

  def insertEntries(self, newEntries):
    """Given an iterable object of NewTopics, insert them.

    Entries in .index are kept in sorted order, so self.entries and
    entries must be merged together and written to .index in sorted order.

    """
    oldEntries = self.entries
    j = 0
    for i in newEntries:
      while j < len(oldEntries) and oldEntries[j].name < i.name:
        self._write(oldEntries[j])
        j+=1
      self._write(i)
    #Write any left overs
    while j < len(oldEntries):
      self._write(oldEntries[j])
      j+=1

  def _write(self, newTopic):
    """Given a newTopic object, write its name, offset, and endset to disk.

    NOTE: If Index.OFFSET_BASE changes from 16, this change must also be
    reflected for formating offset and endsets.
    
    """

    self._setWrite()
    self._filestream.write(newTopic.name)
    #Write, ensuring the proper width
    self._filestream.write("{0:0{1}x}". \
      format(newTopic.offset, self._OFFSET_LENGTH))
    self._filestream.write("{0:0{1}x}". \
      format(newTopic.endset, self._END_BYTE_LENGTH))
    #self.entries are no longer accurate: cause them to reload
    self._entries = None

class Corpora(object):
  """Corpora controller for specialized reads and writes to a .corpora file.

  Corpora unifies and abstracts all reads and writes to an .corpora file.
  It acts as a controller and stores data about the storage schema in a
  .corpora file so that other functions don't need to know this information.
  All data that comes out of Corpora are ?????????? rather than raw bytes.

  Class Variables:

  Member Variables:
    _filestream the actual .corpora file-like object to read and write from.

  """

  def __init__(self, filestream):
    """Initialize a Corpora object given an *opened* .corpora file."""

    self._filestream = filestream

  def _setAppend(self):
    """Reopen the internal file object for append mode.
    
    If _filestream is already opened in 'a' mode, nothing happens.
    
    """
    self._filestream = self._filestream.reOpen("a")

  def _setRead(self):
    """Reopen the internal file object for read mode and flush the I/O buffer.
    
    If _filestream is already opened in 'r' mode, nothing happens.

    """
    self._filestream = self._filestream.reOpen("r")

  def close(self):
    """Close and Flush the internal filestream of the Corpora."""

    self._filestream.close()

  def getCorpus(self, topic):
    """Given a FindTopic object, locate and return its corresponding corpus."""

    self._setRead()
    (self._filestream).seek(topic.offset)
    return self._filestream.read(topic.endset - topic.offset)

  def _write(self, newTopic):
    """Given a NewTopic object, write its corpus to disk.

    Write the new corpus to the end of the .corpora file. Set the offset field
    of the given newTopic to reflect where the newly written corpus is located.
    
    """
    self._setAppend()
    newTopic.setOffset(self._filestream.tell())
    self._filestream.write(newTopic.corpus)

  def insertEntries(self, newEntries):
    """Given an iterable object over NewTopic objects, write them to disk."""

    for n in newEntries:
      self._write(n)

class FindTopic(object):
  """Find Topic object with name and offset.

  Find Topic is an object created from a search on an Index.
  This stores the name of a topic as well as the offset, and endset of the
  corrseponding corpus.
  This is *different* from a NewTopic object. FindTopic doesn't know
  anything about the corpus of a topic.

  --

  Class Variables:
    NULL is the 'null' or filler character. It ensures that every entry's
      name in the index file occupies Topic.NAME_LENGTH bytes (and always 
      (Topic.LENGTH-Topic.NAME_LENGTH) more for offset)

  Member Variables:
    name the name of this topic stripped down to contain no NULL characters
    offset the offset of the corresponding corpus in the corpora file.
      It is parsed as a hexadecimal number.
  """

  NULL = "\x00"

  def __init__(self, raw_name, raw_offset, raw_endset):
    """FindTopic initializer.

    Create a FindTopic given the unprocessed output from reading an Index.
    This will strip away excess characters from the raw_name and parse string
    offset and endset to integers.

    """
    self.name = raw_name
    self.offset = int(raw_offset, Index.OFFSET_BASE)
    self.endset = int(raw_endset, Index.OFFSET_BASE)

  def cleanName(self):
    """Return the name field human readable."""

    return self.name[:self.name.rfind(self.NULL)]

class NewTopic(object):
  """New Topic object with name and corpus.

  New Topic is an object to help serialize input when writing to both index
  and corpora files. It contains a padded name and corresponding corpus.
  This is *different* from a FindTopic object. NewTopics are for going into
  files where as FindTopic is for coming out of files. NewTopic is friends
  of both Index and FindTopic. It is very important that the corpus field of
  a New Topic is only accessed when it needs to be written to disk. Premature
  access will cause destruction of the corpus.

  Class Variables:
    _RANGE tuple representing character range on which to pad name.

  Member Variables:
    name the name of the topic (with Null characters)
    printName the human readable name to return when str() is called.
    corpus the corpus that corresponds to the given name
    offset the byte offset of the beginning of the entry in the .corpora file.
    endset the byte offset of the last byte in the .corpora file.

  """

  _RANGE  = (ord(FindTopic.NULL)+1, 0xff)

  def __init__(self, name, corpus):
    """Initialize a Topic given a name and corpus.

    If the given name length is greater than or equal to Index._NAME_LENGTH, the
    name will be truncated. Otherwise, pad the given name with characters until
    it is Index._NAME_LENGTH characters long.

    """
    self.printName = name
    if len(name) >= Index._NAME_LENGTH: #Truncate the name
      self.name = name[:Index._NAME_LENGTH-1] + FindTopic.NULL
    else:
      self.name = name + FindTopic.NULL + "".join(chr(randint(*self._RANGE)) \
        for _ in xrange(Index._NAME_LENGTH-len(name)-1))
    self._corpus = corpus
    #Data not computed yet
    self.offset = None
    self.endset = None

  def __str__(self):
    """Return the human readable string representation of the NewTopic."""

    return self.printName

  @property
  def corpus(self):
    """Return the corpus for the New Topic and delete the pointer to it."""

    c = self._corpus
    self._corpus = None
    return c

  def setOffset(self, offset):
    """Given an offset, set the field and compute the endset."""

    self.offset = offset
    self.endset = offset + len(self._corpus)

  def __lt__(self, obj):
    """Determine if the NewTopic is less than another.

    Only the name fields of the two NewTopic objects are compared.
    An exception is raised if the given object has no name field.
    This interface is used for sorting in a priority queue.
    """

    return self.name < obj.name

  def __le__(self, obj):
    """Determine if the NewTopic is less than or equal to another."""

    return self < obj or self == obj

  def __eq__(self, obj):
    """Determine if the NewTopic is equal to another."""

    return self.name == obj.name

  def __ne__(self, obj):
    """Determine if the NewTopic is not equal to another."""

    return not self == obj.name

  def __gt__(self, obj):
    """Determine if the NewTopic is greater than another."""

    return not self <= obj

  def __ge__(self, obj):
    """Determine if the NewTopic is greater than or equal to another."""

    return self > obj or self == obj

class EncryptedFile(file):
  """Encrypted file stream with the same interface as a normal file.

  Encrypted file has the same interface as a normal file, but uses an 
  encryption algorithm to encrypt written data and decrypt read data. 
  For this purpose, an additional encryption key is needed for file 
  operations. This key will not be saved as plaintext in memory.

  Class Variables:
    _ENCRYPT the encryption function with which I/O goes through this file.
      This function must have the interface: func(data,key) and serve as both
      an encryption and decryption function.

  Member Variables:
    _access generated encryption key to encrypt the passed-in file encryption 
      key with.
    _key the key with which to decrypt the file. This is user provided.

  """

  @staticmethod
  def _ENCRYPT(*args):
    """Wrapper to have a static method make a function."""
    return xor.cipher(*args)
    return args[0]
  _DECRYPT = _ENCRYPT 

  def __init__(self,name,key,mode="r"):
    """Encrypted file initializer.

    Params:
      name a string containing the name or path of the file to open.
      mode the mode with which to open the file.
      key the encryption key to use for encryption and decryption.
    Note: None of the parameters may be omitted as that would interfere with
    the built-in keyword arguments and/or confuse the interface.

    """
    file.__init__(self,name,mode)
    #Generate a random key to encrypt the file key with.
    self._access = reduce(lambda x,y:x+y,map(lambda _:chr(randint(0,255)),range(255)))
    self.__key = self._ENCRYPT(key,self._access)
    key = None

  @property
  def _key(self):
    """Return the plaintext key for the Encrypted file."""

    return self._DECRYPT(self.__key, self._access)

  def write(self, byte):
    """Write a string to an encrypted file.

    No encryption key is needed as an argument; it is saved upon instantiation.
    The procedure encrypt(key,access) gives the plaintext key.

    """
    file.write(self, self._ENCRYPT(byte, self._key))

  def read(self,size=-1):
    """Read bytes from the encrypted file given optional size."""

    return self._DECRYPT(file.read(self,size), self._key)

  def close(self):
    """Close this file object. 

    Close this file and delete the keys so that this file may be garbage-
    collected. This is for both memory safety and security purposes.

    """
    self.flush()
    file.close(self)
    self.__key = self._access = None

  def reOpen(self, mode):
    """Return Encrypted file instance for the filestream opened in given mode.

    If the Encrypted file is already in the given mode, return itself. No key
    is needed.

    """
    if self.mode != mode:
      f = self.__class__(self.name, self._key, mode)
      self.close()
      return f

    return self

class Environment(object):
  """Environment object that keeps tracks of persistent data.
  
  Environment is esentially a wrapper to both the primary Index and Corpora
  objects for a single session. For instantiation, the given Index and Corpora
  objects must already be initialized; Environement does no initialization.
  Environment provides read only access to its Index and Corpora references
  via property decorators.

  Class Variables:
    _INDEX name of the index file.
    _CORPORA name of the corpora file.

  Member Variables:
    _index Index object that keeps an index of topic names.
    _corpora Corpora object that stores corresponding corpora.

  """

  _INDEX = ".index"
  _CORPORA = ".corpora"

  @staticmethod
  def setup(key):
    """Setup the program environment given an encryption key

    Factory for Environment object. Locate the pathes of the Index and Corpora
    files. If these files do no exist in the current directory, they are
    automatically created. Return an Environment instance.

    """
    #key = "1%90ji!mk;r=9j{\o2"
    #Try to open the file in read mode, if it errors, open in write-mode
    try:
      i = EncryptedFile(Environment._INDEX, key)
    except IOError:
      i = EncryptedFile(Environment._INDEX, key, "w")
    try:
      c = EncryptedFile(Environment._CORPORA, key)
    except IOError:
      c = EncryptedFile(Environment._CORPORA, key, "w")

    key = None
    return Environment(Index(i), Corpora(c))

  def __init__(self, index, corpora):
    """Initialize new Environment given Index and Corpora objects."""

    self._index = index
    self._corpora = corpora

  def insertEntries(self, newEntries):
    """Given an iterable object over NewTopics, write them to disk.

    The given iterable object must:
      Contain NewTopic objects
      Iterate over the NewTopic objects in sorted order, sorted by name
      Must not be a destructive iterator

    Wrapper for Index.insertEntries() and Corpora.insertEntries(); NewTopics
    are inserted in the correct order, by calling Corpora before Index to
    properly mutate the newTopic objects.

    """
    self._corpora.insertEntries(newEntries)
    self._index.insertEntries(newEntries)

  def close(self):
    """Close the Index and Corpora objects.

    Wrapper for Index.close() and Corpora.close().

    """
    self._index.close()
    self._corpora.close()

  @property
  def index(self):
    """Return the Index stored by the Environment."""

    return self._index

  @property
  def corpora(self):
    """Return the Corpora stored by the Environement."""

    return self._corpora

def search(query, body, left=0, right=-1):
  """conduct binary search on tuple of FindTopic objects."""
  if right == -1:
    right = len(body)
  if left >= right or len(query) == 0:
    return []
  
  mid = (left+right)/2
  #partial match: do some more searching
  if re.match(query, body[mid]):
    results = [body[mid]]
    for i in xrange(mid-1,0,-1):
      if re.match(query, body[i]):
        results.append(body[i])
      else:
        break
    for i in xrange(mid+1,len(body)):
      if re.match(query, body[i]):
        results.append(body[i])
      else:
        break
    return results
  elif query > body[mid]:
    return search(query, body, mid+1, right)
  else:
    return search(query, body, left, mid)
