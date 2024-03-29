# This module is part of the spambayes project, which is Copyright 2002-3
# The Python Software Foundation and is covered by the Python Software
# Foundation license.

# Simple Python library for Outlook Express mailboxes handling
# Based on C++ work by Arne Schloh <oedbx@aroh.de>

__author__ = "Romain Guy"

import binascii
import os
import struct

###########################################################################
## DBX FILE HEADER
###########################################################################
class dbxFileHeader:
  """
     Each Outlook Express DBX file has a file header.
     This header defines many properties, only a few of which interest us.

     The only properties which are required are defined by indexes. The
     indexes are static attributes of the class and their names begin with
     "fh". You can access their values through the method getEntry().
  """

  HEADER_SIZE    = 0x24bc              # total header size
  HEADER_ENTRIES = HEADER_SIZE >> 2    # total of entries in the header

  MAGIC_NUMBER   = 0xfe12adcfL         # specific to DBX files
  OFFLINE        = 0x26fe9d30L         # specific to offline.dbx
  FOLDERS        = 0x6f74fdc6L         # specific to folders.dbx
  POP3UIDL       = 0x6f74fdc7L         # specific to pop3uidl.dbx

  # various entries indexes
  FH_FILE_INFO_LENGTH       = 0x07     # file info length
  FH_FIRST_FOLDER_LIST_NODE = 0x1b     # pointer to the first folder list node
  FH_LAST_FOLDER_LIST_NODE  = 0x1c     # pointer to the last folder list node
  FH_MESSAGE_CONDITIONS_PTR = 0x22     # pointer to the message conditions object
  FH_FOLDER_CONDITIONS_PTR  = 0x23     # pointer to the folder conditions object
  FH_ENTRIES                = 0x31     # entries in tree
  FH_TREE_ROOT_NODE_PTR     = 0x39     # pointer to the root node of a tree

  FILE_HEADER_ENTRIES = \
  [ ( 0x07,  "file info length"                                ),
    ( 0x09,  "pointer to the last variable segment"            ),
    ( 0x0a,  "length of a variable segment"                    ),
    ( 0x0b,  "used space of the last variable segment"         ),
    ( 0x0c,  "pointer to the last tree segment"                ),
    ( 0x0d,  "length of a tree segment"                        ),
    ( 0x0e,  "used space of the last tree segment"             ),
    ( 0x0f,  "pointer to the last message segment"             ),
    ( 0x10,  "length of a message segment"                     ),
    ( 0x11,  "used space of the last message segment"          ),
    ( 0x12,  "root pointer to the deleted message list"        ),
    ( 0x13,  "root pointer to the deleted tree list"           ),
    ( 0x15,  "used space in the middle sector of the file"     ),
    ( 0x16,  "reusable space in the middle sector of the file" ),
    ( 0x17,  "index of the last entry in the tree"             ),
    ( 0x1b,  "pointer to the first folder list node"           ),
    ( 0x1c,  "pointer to the last folder list node"            ),
    ( 0x1f,  "used space of the file"                          ),
    ( 0x22,  "pointer to the message conditions object"        ),
    ( 0x23,  "pointer to the folder conditions object"         ),
    ( 0x31,  "entries in the tree"                             ),
    ( 0x32,  "entries in the 2.nd tree"                        ),
    ( 0x33,  "entries in the 3.rd tree"                        ),
    ( 0x39,  "pointer to the root node of the tree"            ),
    ( 0x3a,  "pointer to the root node of the 2.nd tree"       ),
    ( 0x3b,  "pointer to the root node of the 3.rd tree"       ),
    ( 0x9f,  "used space for indexed info objects"             ),
    ( 0xa0,  "used space for conditions objects"               ),
    ( 0xa2,  "used space for folder list objects"              ),
    ( 0xa3,  "used space for tree objects"                     ),
    ( 0xa4,  "used space for message objects"                  )]

  def __init__(self, dbxStream):
    """Initialize the DBX header by reading it directly from the passed
    stream."""
    dbxStream.seek(0)
    self.dbxBuffer = dbxStream.read(dbxFileHeader.HEADER_SIZE)

  def isMessages(self):
    """Return true iff the DBX is a messages DBX."""
    return not (self.isFolders() or self.isPOP3UIDL() or self.isOffline())

  def isFolders(self):
    """Return true if the DBX is the folders DBX."""
    return self.getEntry(1) == dbxFileHeader.FOLDERS

  def isPOP3UIDL(self):
    """Return true if the DBX is the POP3UIDL DBX."""
    return self.getEntry(1) == dbxFileHeader.POP3UIDL

  def isOffline(self):
    """Return true if the DBX is the offline DBX."""
    return self.getEntry(1) == dbxFileHeader.OFFLINE

  def isValid(self):
    """Return true if the DBX is a valid DBX file."""
    return self.getEntry(0) == dbxFileHeader.MAGIC_NUMBER

  def getHeaderBuffer(self):
    """Return the bytes buffer containing the whole header."""
    return self.dbxBuffer

  def getEntry(self, dbxEntry):
    """Return the n-th entry as a long integer."""
    return struct.unpack("L",
                         self.dbxBuffer[dbxEntry * 4:(dbxEntry * 4) + 4])[0]

  def getEntryAsHexStr(self, dbxEntry):
    """Return the n-th entry as an hexadecimal string.
    (Little endian encoding!)"""
    return '0x' + \
           binascii.hexlify(self.dbxBuffer[dbxEntry * 4:(dbxEntry * 4) + 4])

###########################################################################
## DBX FILE INFO
###########################################################################

class dbxFileInfo:
  """
    Following the DBX header there is DBX info. This part gives the name of
    the folder described by the current DBX.
  """

  MESSAGE_FILE_INFO = 0x618

  def __init__(self, dbxStream, dbxLength):
    """Reads the DBX info part from a DBX stream."""
    dbxStream.seek(dbxFileHeader.HEADER_SIZE)
    self.dbxLength = dbxLength
    self.dbxBuffer = dbxStream.read(dbxLength)

  def isFoldersInfo(self):
    """Return true if the info belongs to folders.dbx."""
    return self.dbxLength != dbxFileInfo.MESSAGE_FILE_INFO

  def getFolderName(self):
    """Returns the folder name."""
    if not self.isFoldersInfo():
      name = [c for c in self.dbxBuffer[0x105:0x210] if ord(c) != 0]
      return "".join(name)
    else:
      return None

  def getCreationTime(self):
    """Not implemented yet."""
    if self.isFoldersInfo():
      return "Not implemented yet"
    else:
      return None

###########################################################################
## DBX TREE
###########################################################################

class dbxTree:
  """Stands for the tree which stores the messages in a given folder."""

  TREE_NODE_SIZE = 0x27c          # size of a tree node

  def __init__(self, dbxStream, dbxAddress, dbxValues):
    """Reads the addresses of the stored messages."""
    self.dbxValues = [i for i in range(dbxValues)]
    # XXX : silly fix !
    if dbxAddress > 0:
      self.__readValues(dbxStream, 0, dbxAddress, 0, dbxValues)

  def __readValues(self, dbxStream, dbxParent, dbxAddress, dbxPosition, dbxValues):
    dbxStream.seek(dbxAddress)
    dbxBuffer = dbxStream.read(dbxTree.TREE_NODE_SIZE)

    count = 0
    entries = ((self.getEntry(dbxBuffer, 4) >> 8) & 0xff)

    if self.getEntry(dbxBuffer, 2) != 0:
      self.__readValues(dbxStream, dbxAddress, self.getEntry(dbxBuffer, 2),
                                   dbxPosition, self.getEntry(dbxBuffer, 5))
      count += self.getEntry(dbxBuffer, 5)

    for i in range(entries):
      pos = 6 + i * 3

      if self.getEntry(dbxBuffer, pos) != 0:
        count += 1
        value = dbxPosition + count
        self.dbxValues[value - 1] = self.getEntry(dbxBuffer, pos)

      if self.getEntry(dbxBuffer, pos + 1) != 0:
        self.__readValues(dbxStream, dbxAddress, self.getEntry(dbxBuffer, pos + 1),
                                     dbxPosition + count, self.getEntry(dbxBuffer, pos + 2))
        count += self.getEntry(dbxBuffer, pos + 2)

  def getEntry(self, dbxBuffer, dbxEntry):
    """Return the n-th entry as a long integer."""
    return struct.unpack("L", dbxBuffer[dbxEntry * 4:(dbxEntry * 4) + 4])[0]

  def getValue(self, dbxIndex):
    """Return the address of the n-th message."""
    return self.dbxValues[dbxIndex]

###########################################################################
## DBX INDEXED INFO
###########################################################################

class dbxIndexedInfo:
  """
    Messages and folders mailboxes contain the "message info" and "folders
    info" entities.
    These entities are indexed info sequences. This is their base class.
  """

  MAX_INDEX = 0x20        # max index
  DT_NONE   = 0           # data type none

  def __init__(self, dbxStream, dbxAddress):
    """Reads the indexed infos from the passed stream."""
    self.dbxBodyLength   = 0L
    self.dbxObjectLength = 0L
    self.dbxEntries      = 0L
    self.dbxCounter      = 0L
    self.dbxBuffer       = []
    self.dbxIndexes      = 0L
    self.dbxBegin        = [0L for i in range(dbxIndexedInfo.MAX_INDEX)]
    self.dbxLength       = [i  for i in self.dbxBegin]
    self.dbxAddress       = dbxAddress
    self.__readIndexedInfo(dbxStream)

  def __readIndexedInfo(self, dbxStream):
    dbxStream.seek(self.dbxAddress)
    temp = dbxStream.read(12)

    self.dbxBodyLength   =  self.__getEntry(temp, 1)
    self.dbxObjectLength =  self.__getEntry(temp, 2) & 0xffff
    self.dbxEntries      = (self.__getEntry(temp, 2) >> 16) & 0xff
    self.dbxCounter      = (self.__getEntry(temp, 1) >> 24) & 0xff
    self.dbxBuffer       =  dbxStream.read(self.dbxBodyLength) # bytes array

    isIndirect           = bool(0)                             # boolean
    lastIndirect         = 0
    data                 = self.dbxEntries << 2                # index within dbxBuffer

    for i in range(self.dbxEntries):
      value      = self.__getEntry(self.dbxBuffer, i)
      isDirect   = value & 0x80
      index      = value & 0x7f
      value    >>= 8
      if isDirect:
        self.__setIndex(index, (i << 2) + 1, 3)
      else:
        self.__setIndex(index, data + value)
        if isIndirect:
          self.__setEnd(lastIndirect, data + value)
          isIndirect   = bool(1)
          lastIndirect = index
      self.dbxIndexes |= 1 << index

    if isIndirect:
      self.__setEnd(lastIndirect, self.dbxBodyLength)

  def __setIndex(self, dbxIndex, dbxBegin, dbxLength = 0):
    if dbxIndex < dbxIndexedInfo.MAX_INDEX:
      self.dbxBegin[dbxIndex] = dbxBegin
      self.dbxLength[dbxIndex] = dbxLength

  def __setEnd(self, dbxIndex, dbxEnd):
    if dbxIndex < dbxIndexedInfo.MAX_INDEX:
      self.dbxLength[dbxIndex] = dbxEnd - self.dbxBegin[dbxIndex]

  def __getEntry(self, dbxBuffer, dbxEntry):
    return struct.unpack("L", dbxBuffer[dbxEntry * 4:(dbxEntry * 4) + 4])[0]

  def getIndexText(self, dbxIndex):
    """Returns the description of the given indexed field."""
    return ""

  def getIndexDataType(self, dbxIndex):
    """Returns the data type of the given index."""
    return dt_None

  def getValue(self, dbxIndex):
    """Returns a tuple : (index in buffer of the info, length of the info)."""
    return (self.dbxBegin[dbxIndex], self.dbxLength[dbxIndex])

  def getValueAsLong(self, dbxIndex):
    """Returns the indexed info as a long value."""
    data, length = self.getValue(dbxIndex)
    value  = 0
    if data:
      value = struct.unpack("L", self.dbxBuffer[data:data + 4])[0]
      if length < 4:
        value &= (1 << (length << 3)) - 1
    return value

  def getString(self, dbxIndex):
    """Returns the indexed info as a string value."""
    index = self.dbxBegin[dbxIndex]
    end = index
    for c in self.dbxBuffer[index:]:
      if ord(c) == 0: break
      end += 1
    return self.dbxBuffer[index:end]

  def getAddress(self):
    return self.dbxAddress

  def getBodyLength(self):
    return self.dbxBodyLength

  def getEntries(self):
    return self.dbxEntries

  def getCounter(self):
    return self.dbxCounter

  def getIndexes(self):
    return self.dbxIndexes

  def isIndexed(self, dbxIndex):
    return self.dbxIndexes & (1 << dbxIndex)

###########################################################################
## DBX MESSAGE INFO
###########################################################################

class dbxMessageInfo(dbxIndexedInfo):
  """
    The message info structure inherits from the index info one. It just
    defines extra constants which allow to access pertinent info.
  """

  MI_INDEX           = 0x0                   # index of the message
  MI_FLAGS           = 0x1                   # the message flags
  MI_MESSAGE_ADDRESS = 0x4                   # the address of the message
  MI_SUBJECT         = 0x8                   # the subject of the message

  # label of each indexed info
  INDEX_LABEL = \
  [ "message index"                , "flags"                          ,
    "time message created/send"    , "body lines"                     ,
    "message address"              , "original subject"               ,
    "time message saved"           , "message id"                     ,
    "subject"                      , "sender eMail address and name"  ,
    "answered to message id"       , "server/newsgroup/message number",
    "server"                       , "sender name"                    ,
    "sender eMail address"         , "id 0f"                          ,
    "message priority"             , "message text length"            ,
    "time message created/received", "receiver name"                  ,
    "receiver eMail address"       , "id 15"                          ,
    "id 16"                        , "id 17"                          ,
    "id 18"                        , "id 19"                          ,
    "OE account name"              , "OE account registry key"        ,
    "message text structure"       , "id 1d"                          ,
    "id 1e"                        , "id 1f"                           ]

  DT_NONE      = 0                    # index is none
  DT_INT4      = 1                    # index is a long integer (32 bits)
  DT_STRING    = 2                    # index is a string
  DT_DATE_TIME = 3                    # index is date/time
  DT_DATA      = 4                    # index is data

  # the data type of each index
  INDEX_DATA_TYPE = \
  [ DT_INT4  , DT_INT4  , DT_DATE_TIME, DT_INT4  , DT_INT4  , DT_STRING, DT_DATE_TIME, DT_STRING,
    DT_STRING, DT_STRING, DT_STRING   , DT_STRING, DT_STRING, DT_STRING, DT_STRING   , DT_NONE  ,
    DT_INT4  , DT_INT4  , DT_DATE_TIME, DT_STRING, DT_STRING, DT_NONE  , DT_INT4     , DT_NONE  ,
    DT_INT4  , DT_INT4  , DT_STRING   , DT_STRING, DT_DATA  , DT_NONE  , DT_NONE     , DT_NONE   ]

  def getIndexText(self, dbxIndex):
    return dbxMessageInfo.INDEX_LABEL[dbxIndex]

  def getIndexDataType(self, dbxIndex):
    return dbxMessageInfo.INDEX_DATA_TYPE[dbxIndex]

###########################################################################
## DBX MESSAGE
###########################################################################

class dbxMessage:
  def __init__(self, dbxStream, dbxAddress):
    self.dbxAddress = dbxAddress
    self.dbxText   = ""
    self.dbxLength = 0L
    self.__readMessageText(dbxStream)

  def __getEntry(self, dbxBuffer, dbxEntry):
    if len(dbxBuffer) < (dbxEntry * 4) + 4:
      return None
    return struct.unpack("L", dbxBuffer[dbxEntry * 4:(dbxEntry * 4) + 4])[0]

  def __readMessageText(self, dbxStream):
    address = self.dbxAddress
    header = ""

    while (address):
      dbxStream.seek(address)
      header = dbxStream.read(16)

      self.dbxLength += self.__getEntry(header, 2)
      address          = self.__getEntry(header, 3)

    pos = ""
    address = self.dbxAddress

    while (address):
      dbxStream.seek(address)
      header  = dbxStream.read(16)
      pos    += dbxStream.read(self.__getEntry(header, 2))
      address  = self.__getEntry(header, 3)

    self.dbxText = pos

  def getText(self):
    return self.dbxText

###########################################################################
## TEST DRIVER
###########################################################################

if __name__ == '__main__':
  import sys
  import getopt

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hp')
  except getopt.error, msg:
    print >>sys.stderr, str(msg) + '\n\n' + __doc__
    sys.exit()

  print_message = False
  for opt, arg in opts:
    if opt == '-h':
      print >>sys.stderr, __doc__
      sys.exit()
    elif opt == '-p':
      print_message = True

  if not args:
    print "Please enter a directory with dbx files."
    sys.exit()

  MAILBOX_DIR = args[0]  

  files = [os.path.join(MAILBOX_DIR, file) for file in \
           os.listdir(MAILBOX_DIR) if os.path.splitext(file)[1] == '.dbx']

  for file in files:
    try:
      print
      print file

      dbx = open(file, "rb", 0)
      header = dbxFileHeader(dbx)

      print "IS VALID DBX  :", header.isValid()

      if header.isMessages():
        info = dbxFileInfo(dbx, header.getEntry(dbxFileHeader.FH_FILE_INFO_LENGTH))
        print "MAILBOX NAME  :", info.getFolderName()
        print "CREATION TIME :", info.getCreationTime()

        entries = header.getEntry(dbxFileHeader.FH_ENTRIES)
        address  = header.getEntry(dbxFileHeader.FH_TREE_ROOT_NODE_PTR)

        if address and entries:
          tree = dbxTree(dbx, address, entries)

          for i in range(entries):
            address = tree.getValue(i)
            messageInfo = dbxMessageInfo(dbx, address)

            if messageInfo.isIndexed(dbxMessageInfo.MI_MESSAGE_ADDRESS):
              messageAddress = messageInfo.getValueAsLong(dbxMessageInfo.MI_MESSAGE_ADDRESS)
              message        = dbxMessage(dbx, messageAddress)

              if print_message:
                print
                print "Message :", messageInfo.getString(dbxMessageInfo.MI_SUBJECT)
                print "=" * (len(messageInfo.getString(dbxMessageInfo.MI_SUBJECT)) + 9)
                print
                print message.getText()

    except Exception, (strerror):
      print strerror

    dbx.close()
