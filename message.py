import time

NEW_LINE = "\n"

# The message being replied to, if this is a reply vs. a new message
class Quote:
    def __init__(self):
        self.id = ""         # timeStamp of the message being replied
        self.authorSlug = "" # person-slug being quoted
        self.authorName = "" # name of the person being quoted
        self.text = ""       # text being quoted

# Typically an emoji reaction to someone's message
class Reaction:
    def __init__(self):
        self.emoji = ""
        self.targetTimeSent = 0 # which timestamp the emoji relates to
        self.sourceSlug = "" # person who had the reaction

# An actual message
# 
# - If groupSlug is non-blank, then personSlug will be blank
# - If personSlug is non-blank, then groupSlug will be blank
class Message:
    def __init__(self):
        self.id = ""              # ID from the messaging system
        self.time = 0             # time.struct_time object
        self.timeStamp = 0        # original timestamp in the message
        self.dateStr = ""         # YYYY-MM-DD
        self.timeStr = ""         # hh:mm in 24 hour clock
        self.groupSlug = ""       # the group the message sent to
        self.phoneNumber = ""     # phone number of the sender
        self.sourceSlug = ""      # `person-slug` of who the message is from
        self.destinationSlug = "" # `person-slug` who the message was sent to
        self.body = ""            # actual content of the message
        self.targetSentTimestamp = "" # which timestamp the emoji relates to
                                  # @todo this is specific to Signal 
        self.processed = False    # True if the message been dealt with
        self.quote = Quote()      # quoted text if replying
        self.attachments = []
        self.reactions = []

    def __str__(self):
        output = str(self.timeStamp)
        output += "id: " + self.id + NEW_LINE
        output += "timeStamp: " + str(self.timeStamp) + NEW_LINE
        output += "dateStr: " + self.dateStr + NEW_LINE
        output += "timeStr: " + self.timeStr + NEW_LINE
        output += "sourceSlug: " + self.sourceSlug + NEW_LINE
        output += "destinationSlug: " + self.destinationSlug + NEW_LINE
        output += "groupSlug: " + self.groupSlug + NEW_LINE
        output += "phoneNumber: " + self.phoneNumber + NEW_LINE
        output += "processed: " + str(self.processed) + NEW_LINE
        output += "attachmemts: " + str(len(self.attachments)) + NEW_LINE
        output += "reactions: " + str(len(self.reactions)) + NEW_LINE
        output += "body: " + self.body
        return output

    # checks if this is a message sent to myself i.e. "Note to Self" feature
    def isNoteToSelf(self):
        result = False
        if self.sourceSlug == self.destinationSlug and not self.groupSlug:
            result = True
        return result
    
    # depends on the self.timeStamp attribute being set to valid int
    def setDateTime(self):
        try:
            # convert the time seconds since epoch to a time.struct_time object
            self.time = time.localtime(self.timeStamp)
            self.dateStr = time.strftime("%Y-%m-%d", self.time)
            self.timeStr = time.strftime("%H:%M", self.time)
            result = True
        except:
            result = False
            
        return result
    
    def getDateStr(self):
        return time.strftime("%Y-%m-%d", self.dateStr)
        
    def getTimeStr(self):
        return time.strftime("%H:%M", self.timeStr)

    def hasAttachment(self):
        if len(self.attachments): return True
        else: return False

    def addAttachment(self, theAttachment):
        self.attachments.append(theAttachment)

class DatedMessages:
    def __init__(self):
        self.dateStr = ""
        self.messages = []

# -----------------------------------------------------------------------------
#
# Divy up messages to the groups and people they were with, by day
# 
# Parameters:
#
#    messages - the messages to be added
#    theConfig - the configuration, an instance of Config
#
# -----------------------------------------------------------------------------
def addMessages(messages, theConfig):

    me = theConfig.getMe()
    
    for theMessage in messages:

        if theMessage and len(theMessage.groupSlug):
            for group in theConfig.groups:
                if theMessage.groupSlug == group.slug:
                    addMessage(theMessage, group, theConfig.reversed)
                    theMessage.processed = True

        if theMessage and not theMessage.processed:
            
            if theMessage.isNoteToSelf():
                addMessage(theMessage, me, theConfig.reversed)
                theMessage.processed = True
            else:
                for person in theConfig.people:
                    if person.slug != me.slug and (person.slug == theMessage.destinationSlug or person.slug == theMessage.sourceSlug): 
                        addMessage(theMessage, person, theConfig.reversed)
                        theMessage.processed = True
                        break
    return

# -----------------------------------------------------------------------------
#
# Add the message to the group or person on the day it was sent.
#
# Some services export messages from newest to oldest (i.e., LinkedIn) where
# others do what would be expected (i.e., SMS Backup, Signal)
# 
# Parameters:
#
#    message - the message to be added
#    thing - the group or person the message is to be added to
#    reversed - `True` if messages ordered from newest to oldest
#
# -----------------------------------------------------------------------------
def addMessage(theMessage, thing, reversed=False):

    dateFound = False

    try:

        # go through existing dates and add message there
        for messagesOnDate in thing.messages:
            if theMessage.dateStr == messagesOnDate.dateStr:
                dateFound = True
                if reversed:
                    messagesOnDate.messages.insert(0, theMessage)
                else:
                    messagesOnDate.messages.append(theMessage)

        # if the date was not found, create it
        if dateFound == False:
            newDate = DatedMessages()
            newDate.dateStr = theMessage.dateStr
            if reversed:
                newDate.messages.insert(0, theMessage)
            else:
                newDate.messages.append(theMessage)
            thing.messages.append(newDate)

    except Exception as e:
        print(e)

# -----------------------------------------------------------------------------
#
# Go through all of the messages and then the reactions and add them
# to the corresponding messages based on their timestamp (and author).
#
# Returns: number of reactions matched
#
# -----------------------------------------------------------------------------
def addReactions(messages, reactions):
    
    count = 0

    for theMessage in messages:
        for theReaction in reactions:
            if theMessage.timeStamp == theReaction.targetTimeSent:
                theMessage.reactions.append(theReaction)
                count +=1

    return count
