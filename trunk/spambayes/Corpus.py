#! /usr/bin/env python

'''Corpus.py - Spambayes corpus management framework.

Classes:
    Corpus - a collection of Messages
    ExpiryCorpus - a "young" Corpus
    MessageFactory - creates a Message

Abstract:
    A corpus is defined as a set of messages that share some common
    characteristic relative to spamness.  Examples might be spam, ham,
    unsure, or untrained, or "bayes rating between .4 and .6.  A
    corpus is a collection of messages.  Corpus is a dictionary that
    is keyed by the keys of the messages within it.  It is iterable,
    and observable.  Observers are notified when a message is added
    to or removed from the corpus.

    Corpus is designed to cache message objects.  By default, it will
    only engage in lazy creation of message objects, keeping those
    objects in memory until the corpus instance itself is destroyed.
    In large corpora, this could consume a large amount of memory.  A
    cacheSize operand is implemented on the constructor, which is used
    to limit the *number* of messages currently loaded into memory.
    The instance variable that implements this cache is
    Corpus.Corpus.msgs, a dictionary.  Access to this variable should
    be through keys(), [key], or using an iterator.  Direct access
    should not be used, as subclasses that manage their cache may use
    this variable very differently.

    Iterating Corpus objects is potentially very expensive, as each
    message in the corpus will be brought into memory.  For large
    corpora, this could consume a lot of system resources.

    ExpiryCorpus is designed to keep a corpus of file messages that
    are guaranteed to be younger than a given age.  The age is
    specified on the constructor, as a number of seconds in the past.
    If a message file was created before that point in time, the a
    message is deemed to be "old" and thus ignored.  Access to a
    message that is deemed to be old will raise KeyError, which should
    be handled by the corpus user as appropriate.  While iterating,
    KeyError is handled by the iterator, and messages that raise
    KeyError are ignored.

    As messages pass their "expiration date," they are eligible for
    removal from the corpus. To remove them properly,
    removeExpiredMessages() should be called.  As messages are removed,
    observers are notified.

    ExpiryCorpus function is included into a concrete Corpus through
    multiple inheritance. It must be inherited before any inheritance
    that derives from Corpus.  For example:

        class RealCorpus(Corpus)
           ...

        class ExpiryRealCorpus(Corpus.ExpiryCorpus, RealCorpus)
           ...

    Messages have substance, which is is the textual content of the
    message. They also have a key, which uniquely defines them within
    the corpus.  This framework makes no assumptions about how or if
    messages persist.

    MessageFactory is a required factory class, because Corpus is
    designed to do lazy initialization of messages and, as an abstract
    class, must know how to create concrete instances of the correct
    class.

To Do:
    o Suggestions?

    '''

# This module is part of the spambayes project, which is Copyright 2002-3
# The Python Software Foundation and is covered by the Python Software
# Foundation license.

__author__ = "Tim Stone <tim@fourstonesExpressions.com>"
__credits__ = "Richie Hindle, Tim Peters, all the spambayes contributors."

from __future__ import generators

try:
    True, False
except NameError:
    # Maintain compatibility with Python 2.2
    True, False = 1, 0
    def bool(val):
        return not not val

import sys           # for output of docstring
import time
import re
from spambayes import tokenizer
from spambayes.Options import options

SPAM = True
HAM = False

class Corpus:
    '''An observable dictionary of Messages'''

    def __init__(self, factory, cacheSize=-1):
        '''Constructor(MessageFactory)'''

        self.msgs = {}            # dict of all messages in corpus
                                  # value is None if msg not currently loaded
        self.keysInMemory = []    # keys of messages currently loaded
                                  # this *could* be derived by iterating msgs
        self.cacheSize = cacheSize  # max number of messages in memory
        self.observers = []       # observers of this corpus
        self.factory = factory    # factory for the correct Message subclass

    def addObserver(self, observer):
        '''Register an observer, which should implement
        onAddMessage, onRemoveMessage'''

        self.observers.append(observer)

    def addMessage(self, message):
        '''Add a Message to this corpus'''

        if options["globals", "verbose"]:
            print 'adding message %s to corpus' % (message.key())

        self.cacheMessage(message)

        for obs in self.observers:
            # there is no reason that a Corpus observer MUST be a Trainer
            # and so it may very well not be interested in AddMessage events
            # even though right now the only observable events are
            # training related
            if hasattr(obs, "onAddMessage"):
                obs.onAddMessage(message)

    def removeMessage(self, message):
        '''Remove a Message from this corpus'''
        key = message.key()
        if options["globals", "verbose"]:
            print 'removing message %s from corpus' % (key)
        self.unCacheMessage(key)
        del self.msgs[key]

        for obs in self.observers:
            # see comments in event loop in addMessage
            if hasattr(obs, "onRemoveMessage"):
                obs.onRemoveMessage(message)

    def cacheMessage(self, message):
        '''Add a message to the in-memory cache'''
        # This method should probably not be overridden
        key = message.key()

        if options["globals", "verbose"]:
            print 'placing %s in corpus cache' % (key)

        self.msgs[key] = message

        # Here is where we manage the in-memory cache size...
        self.keysInMemory.append(key)

        if self.cacheSize > 0:       # performance optimization
            if len(self.keysInMemory) > self.cacheSize:
                keyToFlush = self.keysInMemory[0]
                self.unCacheMessage(keyToFlush)

    def unCacheMessage(self, key):
        '''Remove a message from the in-memory cache'''
        # This method should probably not be overridden

        if options["globals", "verbose"]:
            print 'Flushing %s from corpus cache' % (key)

        try:
            ki = self.keysInMemory.index(key)
        except ValueError:
            pass
        else:
            del self.keysInMemory[ki]

        self.msgs[key] = None

    def takeMessage(self, key, fromcorpus):
        '''Move a Message from another corpus to this corpus'''
        msg = fromcorpus[key]
        msg.load() # ensure that the substance has been loaded
        fromcorpus.removeMessage(msg)
        self.addMessage(msg)

    def get(self, key, default=None):
        if self.msgs.get(key, "") is "":
            return default
        else:
            return self[key]

    def __getitem__(self, key):
        '''Corpus is a dictionary'''
        amsg = self.msgs.get(key)

        if amsg is None:
            amsg = self.makeMessage(key)     # lazy init, saves memory
            self.cacheMessage(amsg)

        return amsg

    def keys(self):
        '''Message keys in the Corpus'''
        return self.msgs.keys()

    def __iter__(self):
        '''Corpus is iterable'''
        for key in self.keys():
            try:
                yield self[key]
            except KeyError:
                pass

    def __str__(self):
        '''Instance as a printable string'''
        return self.__repr__()

    def __repr__(self):
        '''Instance as a representative string'''
        raise NotImplementedError

    def makeMessage(self, key):
        '''Call the factory to make a message'''

        # This method will likely be overridden
        msg = self.factory.create(key)

        return msg


class ExpiryCorpus:
    '''Mixin Class - Corpus of "young" file system artifacts'''

    def __init__(self, expireBefore):
        '''Constructor'''
        self.expireBefore = expireBefore

    def removeExpiredMessages(self):
        '''Kill expired messages'''

        for msg in self:
            if msg.createTimestamp() < time.time() - self.expireBefore:
                if options["globals", "verbose"]:
                    print 'message %s has expired' % (msg.key())
                self.removeMessage(msg)


class MessageFactory:
    '''Abstract Message Factory'''

    def __init__(self):
        '''Constructor()'''
        pass

    def create(self, key):
        '''Create a message instance'''
        raise NotImplementedError


if __name__ == '__main__':
    print >>sys.stderr, __doc__
