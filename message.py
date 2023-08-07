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
        output += "sourceSlug: " + self.sourceSlug + NEW_LINE
        output += "destinationSlug: " + self.destinationSlug + NEW_LINE
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
            timeInSeconds = self.timeStamp/1000
            # convert the time seconds since epoch to a time.struct_time object
            self.time = time.localtime(timeInSeconds)
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
        if len(theMessage.groupSlug):
            for group in theConfig.groups:
                if theMessage.groupSlug == group.slug:
                    appendMessage(theMessage, group)
                    theMessage.processed = True

        if not theMessage.processed:
            if theMessage.isNoteToSelf():
                appendMessage(theMessage, me)
                theMessage.processed = True
            else:
                for person in theConfig.people:
                    if person.slug != me.slug and (person.slug == theMessage.destinationSlug or person.slug == theMessage.sourceSlug): 
                        appendMessage(theMessage, person)
                        theMessage.processed = True
                        break
    return

# -----------------------------------------------------------------------------
#
# Add the message to the group or person on the day it was sent.
# 
# Parameters:
#
#    message - the message to be added
#    thing - the group or person the message is to be added to
#
# -----------------------------------------------------------------------------
def appendMessage(theMessage, thing):

    dateFound = False

    try:

        # go through existing dates and add message there
        for messagesOnDate in thing.messages:
            if theMessage.dateStr == messagesOnDate.dateStr:
                dateFound = True
                messagesOnDate.messages.append(theMessage)

        # if the date was not found, create it
        if dateFound == False:
            newDate = DatedMessages()
            newDate.dateStr = theMessage.dateStr
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
