#! /usr/bin/env python

"""message.py - Core Spambayes classes.

Classes:
    Stats - provides statistical information about previous activity.

Abstract:

    Provide statistics on the activity that spambayes has done - for
    example the number of messages classified as each type, and the
    number of messages trained as each type.  This information is
    retrieved from the messageinfo database, so is as reliable as that
    is <wink>.

To Do:
    o People would like pretty graphs, so maybe that could be done.
    o People have requested time-based statistics - mail per hour,
      spam per hour, and so on.
    o The possible stats to show are pretty much endless.  Some to
      consider would be: percentage of mail that is fp/fn/unsure,
      percentage of mail correctly classified.
    o Suggestions?

"""

# This module is part of the spambayes project, which is Copyright 2002-3
# The Python Software Foundation and is covered by the Python Software
# Foundation license.

__author__ = "Tony Meyer <ta-meyer@ihug.co.nz>"
__credits__ = "Mark Hammond, all the spambayes folk."

from spambayes.message import msginfoDB

class Stats(object):
    class __empty_msg:
        def getId(self):
            return self.id

    def __init__(self):
        self.CalculateStats()

    def Reset(self):
        self.cls_spam = 0
        self.cls_ham = 0
        self.cls_unsure = 0
        self.trn_spam = 0
        self.trn_ham = 0
        self.trn_unsure_ham = 0
        self.trn_unsure_spam = 0
        self.fp = 0
        self.fn = 0
        self.total = 0

    def CalculateStats(self):
        self.Reset()
        for msg in msginfoDB.db:
            self.total += 1
            m = self.__empty_msg()
            m.id = msg
            msginfoDB._getState(m)
            if m.c == 's':
                self.cls_spam += 1
                if m.t == 0:
                    self.fn += 1
            elif m.c == 'h':
                self.cls_ham += 1
                if m.t == 1:
                    self.fp += 1
            elif m.c == 'u':
                self.cls_unsure += 1
                if m.t == 0:
                    self.trn_unsure_ham += 1
                elif m.t == 1:
                    self.trn_unsure_spam += 1
            if m.t == 1:
                self.trn_spam += 1
            elif m.t == 0:
                self.trn_ham += 1

    def GetStats(self):
        if self.total == 0:
            return ["SpamBayes has processed zero messages"]
        chunks = []
        push = chunks.append
        perc_ham = 100.0 * self.cls_ham / self.total
        perc_spam = 100.0 * self.cls_spam / self.total
        perc_unsure = 100.0 * self.cls_unsure / self.total
        format_dict = dict(perc_spam=perc_spam, perc_ham=perc_ham,
                           perc_unsure=perc_unsure, num_seen = self.total)
        format_dict.update(self.__dict__)
        push("SpamBayes has processed %(num_seen)d messages - " \
             "%(cls_ham)d (%(perc_ham).0f%%) good, " \
             "%(cls_spam)d (%(perc_spam).0f%%) spam " \
             "and %(cls_unsure)d (%(perc_unsure)d%%) unsure." % format_dict)
        push("%(trn_ham)d message(s) were manually " \
             "classified as good (with %(fp)d " \
             "being false positives)." % format_dict)
        push("%(trn_spam)d message(s) were manually " \
             "classified as spam (with %(fn)d " \
             "being false negatives)." % format_dict)
        push("%(trn_unsure_ham)d unsure message(s) were manually " \
             "identified as good, and %(trn_unsure_spam)d as spam." \
             % format_dict)
        return chunks

if __name__=='__main__':
    s = Stats()
    print "\n".join(s.GetStats())
