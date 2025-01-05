# -----------------------------------------------------------------------------
#
# Generic message between people. A message can have reactions and attachments.
#
# -----------------------------------------------------------------------------

import time
import logging

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
        output = "id: " + str(self.id) + NEW_LINE
        output += "timestamp: " + str(self.timestamp) + NEW_LINE
        output += "date_str: " + str(self.date_str) + NEW_LINE
        output += "time_str: " + str(self.time_str) + NEW_LINE
        output += "from_slug: " + str(self.from_slug) + NEW_LINE
        output += "to_slugs: " + str(self.to_slugs) + NEW_LINE
        output += "group_slug: " + self.group_slug + NEW_LINE
        output += "phone_number: " + str(self.phone_number) + NEW_LINE
        output += "processed: " + str(self.processed) + NEW_LINE
        output += "attachments: " + str(len(self.attachments)) + NEW_LINE
        output += "reactions: " + str(len(self.reactions)) + NEW_LINE
        output += "subject: " + str(self.subject) + NEW_LINE
        output += "body: " + str(self.body)
        return output

    # checks if this is a message sent to myself i.e. "Note to Self" feature
    def is_note_to_self(self):
        result = False
        # groups are only used in chats so if this was an email to multiple
        # people, then it's not a note-to-self. So check that I'm the only
        # person in `self.to_slugs` and that `self.group_slug` is empty
        if {self.from_slug} == set(self.to_slugs) and not self.group_slug:
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
        return time.strftime("%Y-%m-%d", self.date_str[:10])
        
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
# Check if the date "YYYY-MM-DD" is in any DatedMessages.date_str.
#
# Parameters:
#  
#   - date_str - the date string to check in the format "YYYY-MM-DD"
#   - dated_messages_list - a list of DatedMessages objects
#
# Returns:
#  
#   - True if the date is found in any DatedMessages.date_str
#   - False otherwise
#
# -----------------------------------------------------------------------------
def date_exists(date_str, dated_messages_list):

    for dated_message in dated_messages_list:
        if dated_message.date_str.startswith(date_str):
            return True
        
    return False

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
                # if from me and to me (and possibly others) OR from someone else to anyone
                if (from_slug == me_slug and person.slug in to_slugs) or (from_slug != me_slug and person.slug == from_slug):
                    add_message(the_message, person)
                    the_message.processed = True

# -----------------------------------------------------------------------------
#
# Check if the messages are between the same people
#
# Parameters:
# 
#   - message_one - the first message
#   - message_two - the second message
# 
# Returns:
#
#   - True if the messages are between the same people
#   - False if the messages are not between the same people 
# 
# -----------------------------------------------------------------------------
def same_people(message_one, message_two):

    if not message_one or not message_two:
        return False
  
    # ensure `date_str` is not None
    if not message_one.date_str or not message_two.date_str:
        return False
    
    # check if the messages are between the same people
    if message_one.from_slug == message_two.from_slug and set(message_one.to_slugs) == set(message_two.to_slugs):
        return True
    
    # check if the messages are within the same group e.g. in SMS or Signal
    if message_one.group_slug == message_two.group_slug: 
        return True
    
    if (message_one.from_slug in message_two.to_slugs) and (message_two.from_slug in message_one.to_slugs):
        # remove the from_slug from each set of to_slugs and compare the remaining sets
        adjusted_to_slugs_one = set(message_one.to_slugs) - {message_two.from_slug}
        adjusted_to_slugs_two = set(message_two.to_slugs) - {message_one.from_slug}
        if adjusted_to_slugs_one == adjusted_to_slugs_two:
            return True
    
    return False

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
#  - the_config - the configuration, an instance of Config
#
# -----------------------------------------------------------------------------
def add_message(the_message, thing):

    date_exists = False

    try:
        # go through existing dates to see if messages are already there
        for messages_on_date in thing.messages:
            
            # see if the date already exists and keep track of this for later
            if messages_on_date.date_str[:10] == the_message.date_str[:10]:
                date_exists = True
                   
                # go through the messages on the date
                for a_message in messages_on_date.messages:

                    # see if the message is between the same people
                    if same_people(the_message, a_message):
                        # add the message to that date and we're done
                        messages_on_date.messages.append(the_message)
                        return

        # date already exists and this is a different conversation, i.e. between
        # different people, so append " - 1" to the date string so that this 
        # message is not mixed in with the other message(s) on the same date
        if date_exists:
            try:
                suffix = 1
                base_date_str = the_message.date_str[:10]
                new_date_str = f"{base_date_str} - {suffix}"
                while any(dm.date_str == new_date_str for dm in thing.messages):
                    suffix += 1
                    new_date_str = f"{base_date_str} - {suffix}"
                the_message.date_str = new_date_str
            except Exception as e:
                logging.error(f"Error in add_message(): {e}")

        # and add the message to the a new DatedMessages object
        new_date = DatedMessages()
        new_date.messages.append(the_message)
        new_date.date_str = the_message.date_str
        thing.messages.append(new_date)

    except Exception as e:
        logging.error(f"Error in add_message(): {e}")

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
