# -----------------------------------------------------------------------------
#
# Generic message between people. A message can have reactions and attachments.
#
# -----------------------------------------------------------------------------

import time

NEW_LINE = "\n"

# The message being replied to, if this is a reply vs. a new message
class Quote:
    def __init__(self):
        self.id = ""          # timestamp of the message being replied
        self.author_slug = "" # person-slug being quoted
        self.author_name = "" # name of the person being quoted
        self.text = ""        # text being quoted

# Typically an emoji reaction to someone's message
class Reaction:
    def __init__(self):
        self.emoji = ""
        self.target_time_sent = 0 # which timestamp the emoji relates to
        self.from_slug = ""       # person who had the reaction

# -----------------------------------------------------------------------------
#
# An actual message.
# 
# - If `group_slug`` is non-blank, then `personSlug`` will be blank
# - If `personSlug`` is non-blank, then `group_slug`` will be blank
# 
# -----------------------------------------------------------------------------
class Message:
    def __init__(self):
        self.id = ""            # ID from the messaging system
        self.time = 0           # time.struct_time object
        self.timestamp = 0      # original timestamp in the message
        self.date_str = ""      # YYYY-MM-DD
        self.time_str = ""      # hh:mm in 24 hour clock
        self.group_slug = ""    # the group the message sent to
        self.phone_number = ""  # phone number of the sender
        self.from_slug = ""     # Person `slug` of who the message is from
        self.to_slugs = []      # Person `slug` who the message was sent to
        self.body = ""          # actual content of the message
        self.target_sent_timestamp = "" # which timestamp the emoji relates to
                                # @todo this is specific to Signal 
        self.processed = False  # True if the message been dealt with
        self.quote = Quote()    # quoted text if replying
        self.attachments = []
        self.reactions = []
        self.subject = ""
        self.service = ""       # mesaging service e.g. YAML_SERVICE_SIGNAL

    def __str__(self):
        output = "id: " + self.id + NEW_LINE
        output += "timestamp: " + str(self.timestamp) + NEW_LINE
        output += "date_str: " + self.date_str + NEW_LINE
        output += "time_str: " + self.time_str + NEW_LINE
        output += "from_slug: " + self.from_slug + NEW_LINE
        output += "to_slugs: " + str(self.to_slugs) + NEW_LINE
        output += "group_slug: " + self.group_slug + NEW_LINE
        output += "phone_number: " + str(self.phone_number) + NEW_LINE
        output += "processed: " + str(self.processed) + NEW_LINE
        output += "attachments: " + str(len(self.attachments)) + NEW_LINE
        output += "reactions: " + str(len(self.reactions)) + NEW_LINE
        output += "subject: " + self.subject + NEW_LINE
        output += "body: " + self.body
        return output

    # checks if this is a message sent to myself i.e. "Note to Self" feature
    def is_note_to_self(self):
        result = False
        if (self.from_slug in self.to_slugs) and not self.group_slug:
            result = True
        return result
    
    # depends on the self.timestamp attribute being set to valid int
    def set_date_time(self):
        try:
            # convert the time seconds since epoch to a time.struct_time object
            self.time = time.localtime(self.timestamp)
            self.date_str = time.strftime("%Y-%m-%d", self.time)
            self.time_str = time.strftime("%H:%M", self.time)
            result = True
        except:
            result = False
            
        return result
    
    def get_date_str(self):
        return time.strftime("%Y-%m-%d", self.date_str)
        
    def get_time_str(self):
        return time.strftime("%H:%M", self.time_str)

    def has_attachment(self):
        if len(self.attachments): return True
        else: return False

    def add_attachment(self, the_attachment):
        self.attachments.append(the_attachment)

class DatedMessages:
    def __init__(self):
        self.date_str = ""
        self.messages = []

# -----------------------------------------------------------------------------
#
# Divy up messages to the groups and people they were with, by day.
# 
# Parameters:
#
#   - messages - the messages to be added
#   - the_config - the configuration, an instance of Config
#
# -----------------------------------------------------------------------------
def add_messages(messages, the_config):

    for the_message in messages:
        if bool(the_message.group_slug):
            for group in the_config.groups:
                if the_message.group_slug == group.slug:
                    add_message(the_message, group)
                    the_message.processed = True

        if not the_message.processed:
            from_slug = the_message.from_slug
            me_slug = the_config.me.slug
            to_slugs = the_message.to_slugs
            
            for person in the_config.people:
                this_slug = person.slug
                if (from_slug == me_slug and this_slug in to_slugs) or (from_slug != me_slug and this_slug == from_slug):
                    add_message(the_message, person)
                    the_message.processed = True

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
#  - message - the message to be added
#  - thing - the group or person the message is to be added to
#
# -----------------------------------------------------------------------------
def add_message(the_message, thing):

    date_found = False
    try:
        # go through existing dates and add the message there
        for messages_on_date in thing.messages:
            if the_message.date_str == messages_on_date.date_str:
                date_found = True
                thing.messages_on_date.messages.append(the_message)

        # if the date was not found, create it
        if date_found == False:
            new_date = DatedMessages()
            new_date.date_str = the_message.date_str
            new_date.messages.append(the_message)
            thing.messages.append(new_date)

    except Exception as e:
        pass

# -----------------------------------------------------------------------------
#
# Go through all of the messages and then the reactions and add them to the 
# corresponding messages based on their timestamp (and author).
#
# Returns: the number of reactions matched
#
# -----------------------------------------------------------------------------
def add_reactions(messages, reactions):
    
    count = 0

    for the_message in messages:
        for the_reaction in reactions:
            if the_message.timestamp == the_reaction.target_time_sent:
                the_message.reactions.append(the_reaction)
                count +=1

    return count
