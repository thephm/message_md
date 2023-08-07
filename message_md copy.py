import time
import json
import os
import shutil
from datetime import datetime
import pathlib
from pathlib import Path
from argparse import ArgumentParser

# config
CONFIG_FOLDER = "config"
OUTPUT_FILE_EXTENSION = ".md"

# some constants
SPACE = " "
TWO_SPACES = SPACE + SPACE
MD_QUOTE = ">" + SPACE
NEW_LINE = "\n"
WELL_AGED = 30 # seconds

# YAML front matter 
YAML_DASHES = "---" + NEW_LINE
YAML_PERSON_SLUGS = "person-slugs"
YAML_SERVICE_SLUG = "service-slug"
YAML_TAGS = "tags"
YAML_DATE = "date"
YAML_TIME = "time"
YAML_SERVICE_SIGNAL = "signal"
YAML_SERVICE_SMS = "sms"
TAG_CHAT = "chat"

class Person:
    def __init__(self):
        self.phoneNumber = ""
        self.slug = ""
        self.firstName = ""
        self.lastName = ""
        self.folderCreated = False
        self.messages = []  # collection of messages by day

class Group:
    def __init__(self):
        self.id = ""
        self.slug = ""
        self.description = ""
        self.members = []  # collection of `Person.slug`s
        self.messages = [] # collection of messages by day

# not used yet, thinking about it
class Setting:
    def __init__(self):
        self.key = ""
        self.value = 0

class String:
    def __init__(self):
        self.number = 0
        self.language = 0
        self.text = ""

# keeps all of the configuration
class Config:
    def __init__(self, fileName=""):

        # find the folder where this file is
        folder = os.path.dirname(os.path.realpath(__file__))
        folder = os.path.join(folder, CONFIG_FOLDER)

        self.STRINGS_FILE_NAME = os.path.join(folder, "strings.json")
        self.PEOPLE_FILE_NAME  = os.path.join(folder, "people.json")
        self.GROUPS_FILE_NAME  = os.path.join(folder, "groups.json")
        self.MIME_TYPES_FILE_NAME = os.path.join(folder, "MIMETypes.json")

        ## configuration field names (SETTINGS_FILE_NAME)
        self.SETTING_OUTPUT_FOLDER = "output-folder"
        self.SETTING_PEOPLE_SUBFOLDER = "people-subfolder"
        self.SETTING_GROUPS_SUBFOLDER = "groups-subfolder"
        self.SETTING_MESSAGES_FILE = "messages-file"
        self.SETTING_ATTACHMENTS_SUBFOLDER = "attachments-subfolder"
        self.SETTING_INCLUDE_TIMESTAMP = "include-timestamp"
        self.SETTING_INCLUDE_QUOTE = "include-quote"
        self.SETTING_COLON_AFTER_CONTEXT = "colon-after-context" 
        self.SETTING_TIME_NAME_SEPARATE = "time-name-separate"
        self.SETTING_MEDIA_SUBFOLDER = "media-subfolder"
        self.SETTING_IMAGE_EMBED = "image-embed"
        self.SETTING_IMAGE_WIDTH = "image-width"
        self.SETTING_ARCHIVE_SUBFOLDER = "archive-subfolder"
        self.SETTING_INCLUDE_REACTIONS = "include-reactions"
        self.SETTING_FOLDER_PER_PERSON = "folder-per-person"
        self.SETTING_FILE_PER_PERSON = "file-per-person"
        self.SETTING_FILE_PER_DAY = "file-per-day"
        self.SETTING_DAILY_NOTES_SUBFOLDER = "daily-notes-subfolder"

        # within array of string fields (after loaded)
        self.STRINGS_LANGUAGE_INDEX = 0
        self.STRINGS_NUMBER_INDEX = 1
        self.STRINGS_TEXT_INDEX = 2

        # string fields
        self.LANGUAGE_FIELD = "language"
        self.STRING_NUMBER = "number"
        self.STRING_TEXT = "text"

        # languages
        self.ENGLISH = 1

        # string numbers
        self.STR_NOT_FOUND = 0
        self.STR_AT = 1
        self.STR_ERROR = 2
        self.STR_COULD_NOT_OPEN_FILE = 3
        self.STR_PERSON_NOT_FOUND = 4
        self.STR_FAILED_TO_WRITE = 6
        self.STR_COULD_NOT_LOAD_MIME_TYPES = 7
        self.STR_UNKNOWN_MIME_TYPE = 8
        self.STR_COULD_NOT_MOVE_THE_ATTACHMENT = 9
        self.STR_COULD_NOT_MOVE_MESSAGES_FILE = 10
        self.STR_COULD_NOT_OPEN_MESSAGES_FILE = 11
        self.STR_COULD_CREATE_ARCHIVE_SUBFOLDER = 12
        self.STR_PHONE_NUMBER_NOT_FOUND = 13
        self.STR_NO_MESSAGE_BODY_OR_ATTACHMENT = 15
        self.STR_SOURCE_MESSAGE_FILE = 16
        self.STR_DONT_PRINT_DEBUG_MSGS = 17
        self.STR_OUTPUT_FOLDER = 18
        self.STR_SOURCE_FOLDER = 19
        self.STR_COULD_NOT_LOAD_CONFIG = 20
        self.STR_LANGUAGE_SETTING = 21
        self.STR_MY_SLUG_SETTING = 22
        self.STR_COULD_NOT_COPY_MESSAGES_FILE = 23
        self.STR_COULD_NOT_FIND_A_GROUP = 24

        self.MAX_LEN_QUOTED_TEXT = 70

        # fields in people file (PEOPLE_FILE_NAME)
        self.PERSON_FIELD_NUMBER = "number"
        self.PERSON_FIELD_SLUG = "person-slug"
        self.PERSON_FIELD_FIRST_NAME = "first-name"
        self.PERSON_FIELD_LAST_NAME = "last-name"
        self.PERSON_FIELD_LINKEDIN_ID = "linkedin-id"

        # fields in groups file (GROUPS_FILE_NAME)
        self.GROUP_COLLECTION = "groups"
        self.GROUP_FIELD_ID = "id"
        self.GROUP_FIELD_SLUG = "slug"
        self.GROUP_FIELD_DESCRIPTION = "description"
        self.GROUP_FIELD_PEOPLE = "people"

        # within array of person fields (after loaded)
        # #todo this is STUPID and needs to be removed!
        self.PERSON_INDEX_NUMBER = 0
        self.PERSON_INDEX_SLUG = 1
        self.PERSON_INDEX_FIRST_NAME = 2

        self.settings = []
        self.strings = []
        self.people = []
        self.groups = []
        self.MIMETypes = []

        self.debug = False
        self.settingsFileName = os.path.join(folder, "settings.json")
        self.service = ""
        self.fileName = fileName
        self.messagesFile = "messages.json"
        self.language = self.ENGLISH
        self.mySlug = "NOMYSLUG"
        self.mediaSubFolder = "media"
        self.imageEmbed = True
        self.imageWidth = 450
        self.sourceFolder = "../messages"
        self.outputFolder = "../output"
        self.attachmentsSubFolder = "attachments"
        self.archiveSubFolder = "archive"
        self.peopleSubFolder = "People"
        self.groupsSubFolder = "groups"
        self.dailyNotesSubFolder = "Daily Notes"
        self.includeTimestamp = True
        self.includeQuote = True
        self.colonAfterContext = False
        self.includeReactions = False
        self.timeNameSeparate = False
        self.folderPerPerson = True
        self.filePerPerson = True
        self.filePerDay = True

    def loadSettings(self):

        result = False

        try:
            settingsFile = open(self.settingsFileName, 'r')
            self.settings = json.load(settingsFile)
            self.archiveSubFolder = os.path.join(self.sourceFolder, self.settings[self.SETTING_ARCHIVE_SUBFOLDER])
            self.messagesFile = os.path.join(self.sourceFolder, self.settings[self.SETTING_MESSAGES_FILE])
            self.attachmentsSubFolder = self.settings[self.SETTING_ATTACHMENTS_SUBFOLDER]
            self.outputFolder = self.settings[self.SETTING_OUTPUT_FOLDER]
            self.groupsSubFolder = self.settings[self.SETTING_GROUPS_SUBFOLDER]
            self.mediaSubFolder = self.settings[self.SETTING_MEDIA_SUBFOLDER]
            self.dailyNotesSubFolder = self.settings[self.SETTING_DAILY_NOTES_SUBFOLDER]
            self.imageEmbed = self.settings[self.SETTING_IMAGE_EMBED]
            self.imageWidth = self.settings[self.SETTING_IMAGE_WIDTH]
            self.includeTimestamp = bool(self.settings[self.SETTING_INCLUDE_TIMESTAMP])
            self.includeQuote = bool(self.settings[self.SETTING_INCLUDE_QUOTE])
            self.colonAfterContext = bool(self.settings[self.SETTING_COLON_AFTER_CONTEXT])
            self.timeNameSeparate = bool(self.settings[self.SETTING_TIME_NAME_SEPARATE])
            self.includeReactions = bool(self.settings[self.SETTING_INCLUDE_REACTIONS])
            self.folderPerPerson = bool(self.settings[self.SETTING_FOLDER_PER_PERSON])
            self.filePerPerson = bool(self.settings[self.SETTING_FILE_PER_PERSON])
            self.filePerDay = bool(self.settings[self.SETTING_FILE_PER_DAY])

            if self.debug == True:
                print(self.SETTING_ATTACHMENTS_SUBFOLDER + ": " + str(self.attachmentsSubFolder))
                print(self.SETTING_ARCHIVE_SUBFOLDER + ": " + str(self.archiveSubFolder))
                print(self.SETTING_OUTPUT_FOLDER + ": " + str(self.outputFolder))
                print(self.SETTING_MEDIA_SUBFOLDER + ": " + str(self.mediaSubFolder))
                print(self.SETTING_IMAGE_EMBED + ": " + str(self.imageEmbed))
                print(self.SETTING_IMAGE_WIDTH + ": " + str(self.imageWidth))
                print(self.SETTING_FOLDER_PER_PERSON + ": " + str(self.folderPerPerson))
                print(self.SETTING_FILE_PER_PERSON + ": " + str(self.filePerPerson))
                print(self.SETTING_FILE_PER_DAY + ": " + str(self.filePerDay))
                print(self.SETTING_INCLUDE_TIMESTAMP + ": " + str(self.includeTimestamp))
                print(self.SETTING_INCLUDE_REACTIONS + ": " + str(self.includeReactions))
                print(self.SETTING_INCLUDE_QUOTE + ": " + str(self.includeQuote))
                print(self.SETTING_COLON_AFTER_CONTEXT + ": " + str(self.colonAfterContext))
                print(self.SETTING_TIME_NAME_SEPARATE + ": " + str(self.timeNameSeparate))
                print(self.SETTING_DAILY_NOTES_SUBFOLDER + ": " + str(self.dailyNotesSubFolder))

            result = True
            settingsFile.close()

        except Exception as e:
            print("Error loading settings.")
            print(e)
            pass

        return result

    def setMessagesFile(fileName, self):
        self.messagesFile = fileName

    def setSourceFolder(folderName, self):
        self.sourceFolder = folderName
        
    # load strings, returns the number of strings loaded
    def loadStrings(self):

        try:
            stringsFile = open(self.STRINGS_FILE_NAME, 'r')

            for line in stringsFile:
                line = line.rstrip()
                x = json.loads(line)
                string = [x[self.LANGUAGE_FIELD], x[self.STRING_NUMBER], x[self.STRING_TEXT]]
                self.strings.append(string)

            stringsFile.close()
        except Exception as e:
            print(e)

        return len(self.strings)
        
    def loadMIMETypes(self):

        self.MIMETypes = False

        try:
            MIMETypesFile = open(self.MIME_TYPES_FILE_NAME, 'r')
            self.MIMETypes = json.load(MIMETypesFile)
        except:
            print(self.getStr(self.STR_COULD_NOT_LOAD_MIME_TYPES))

        return self.MIMETypes
    
    # Lookup a person's first name from their phone number
    def getFirstNameByNumber(self, number):
        
        global Strings

        firstName = ""
        person = self.getPersonByNumber(number, self.people)
        
        if person:
            try: 
                firstName = person.firstName
            except Exception as e:   
                print(self.getStr(self.STR_PERSON_NOT_FOUND))
                print(e)
                pass

        return firstName

    # Lookup a person from their phone number
    def getFirstNameBySlug(self, slug):

        firstName = ""

        for person in self.people:
            if person.slug == slug:
                firstName = person.firstName
    
        return firstName
    
    def getGroupSlugByPhoneNumbers(self, phoneNumbers):
        slugs = []
        slug = ""
        found = False

        # first get the slugs for the phone numbers
        for phoneNumber in phoneNumbers:
            person = self.getPersonByNumber(phoneNumber)
            if person:
                slugs.append(person.slug)
        
        # add myself to the slugs if not there already
        if self.mySlug not in slugs:
            slugs.append(self.mySlug)

        if len(slugs):
            for group in self.groups:
                # use set() in case they're not in the same order
                if set(group.members) == set(slugs):
                    slug = group.slug
                    found = True
                    break

        if found == False:
            print( self.getStr(self.STR_COULD_NOT_FIND_A_GROUP) + str(slugs))

        return slug
                    
    # Lookup the group slug based on it's unique ID
    def getGroupSlug(self, id):
        slug = ""

        for group in self.groups:
            if group.id == id:
                slug = group.slug
        
        return slug


    # load the people, returns number of people loaded
    def loadPeople(self):

        try:
            peopleFile = open(self.PEOPLE_FILE_NAME, 'r', encoding="utf-8")
            jsonPeople = json.load(peopleFile)

            for jsonPerson in jsonPeople:
                try:
                    person = Person()
                    person.slug = jsonPerson[self.PERSON_FIELD_SLUG]
                    person.firstName = jsonPerson[self.PERSON_FIELD_FIRST_NAME]
                    person.lastName = jsonPerson[self.PERSON_FIELD_LAST_NAME]
                    person.phoneNumber = jsonPerson[self.PERSON_FIELD_NUMBER]
                    person.linkedInId = jsonPerson[self.PERSON_FIELD_LINKEDIN_ID]
                    self.people.append(person)
                except Exception as e:  
                    pass

        except Exception as e:
            print(e)
            return

        peopleFile.close()

        return len(self.people)

    # load the groups, returns number of groups loaded
    def loadGroups(self):

        try:
            groupsFile = open(self.GROUPS_FILE_NAME, 'r', encoding="utf-8")
            jsonGroups = json.load(groupsFile)

            for jsonGroup in jsonGroups[self.GROUP_COLLECTION]:
                group = Group()
                try:
                    group.id = jsonGroup[self.GROUP_FIELD_ID]
                    group.slug = jsonGroup[self.GROUP_FIELD_SLUG]
                    group.description = jsonGroup[self.GROUP_FIELD_DESCRIPTION]
                    try:
                        for personSlug in jsonGroup[self.GROUP_FIELD_PEOPLE]:
                            group.members.append(personSlug)
                        self.groups.append(group)
                    except:
                        pass

                except:
                    pass

            groupsFile.close()
        
        except Exception as e:
            print(e)

        return len(self.groups)
    
    # get the Person object representing me
    def getMe(self):
        
        person = Person()

        for person in self.people:
            if person.slug == self.mySlug:
                break
        
        return person

    # -----------------------------------------------------------------------------
    #
    # Lookup a person in people array from their phone number. Matches the last 10
    # digits which is not perfect but good enough for me! 
    # 
    # Why do this? because sometimes numbers are shown with "+1" for
    # their country code and other times not. For example:
    #
    #  '2985551212' and '+12895551212"
    #
    # -----------------------------------------------------------------------------
    def getPersonByNumber(self, number):

        for person in self.people:
            try:
                if person.phoneNumber[-10:] == number[-10:]:
                    return person
            except:
                return False
        
    # get a string out of strings based on its ID
    def getStr(self, stringNumber):

        result = ""

        for string in self.strings:
            try:
                if (int(string[self.STRINGS_NUMBER_INDEX]) == int(stringNumber) and
                    int(string[self.STRINGS_LANGUAGE_INDEX]) == self.language):
                    result = string[self.STRINGS_TEXT_INDEX]
            except:
                pass

        return result
    
class Attachment:
    def __init__(self):
        self.type = "" # contentType
        self.id = ""
        self.size = 0
        self.fileName = ""
        self.customFileName = ""
        self.width = 0
        self.height = 0
        self.voiceNote = False

    def isImage(self):
        isImage = False

        if self.type[:5] == "image":
            isImage = True

        return isImage

    # Get the file name with suffix based on it's content type
    def addSuffix(self, config):

        fileName = self.id
        try:
            suffix = config.MIMETypes[self.type]
            if len(suffix):
                fileName += "." + suffix 
        except Exception as e:
            print(config.getStr(config.STR_UNKNOWN_MIME_TYPE) + ": '" + self.type + "' (" + self.id + ')')
            print(e)
            pass

        return fileName

    # Generates the Markdown for media links e.g. [[photo.jpg]]
    def generateLink(self, config):

        link = ""

        # @todo this should be part of the Signal code not here! 
        # originally, I included 'media/file.jpg' but since Obsidian
        # finds any file in the vault, no need to tell it where it is
        if config.service == YAML_SERVICE_SIGNAL:
            fileName = self.addSuffix(config)
        else:
            fileName = self.id
    
        if len(fileName):
            if self.isImage() and config.imageEmbed:
                link = "!"
            link += "[[" + fileName
            if self.isImage() and config.imageWidth:
                link += "|" + str(config.imageWidth)
            link += "]]" + NEW_LINE

        return link

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

    def addAttachment(self, attachment):
        self.attachments.append(attachment)

class DatedMessages:
    def __init__(self):
        self.dateStr = ""
        self.messages = []

# create a folder
def createFolder(folder):
    
    result = False

    if not os.path.exists(folder):
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
            result = True
        except Exception as e:
            print(e)
    else:
        # already existed so lie that it was created
        result = True

    return result

# -----------------------------------------------------------------------------
#
# Create folders for the daily notes. 
#
# Parameters:
#
#    - config - all of the Config(uration)
#
# Notes:
#
#    - this is for notes-to-self that are stored in a separate folder from all
#      of the other messages
# 
# -----------------------------------------------------------------------------
def createDailyNotesFolders(config):

    dailyNotesFolder = os.path.join(config.outputFolder, config.dailyNotesSubFolder)
    createFolder(dailyNotesFolder)
    mediaSubFolder = os.path.join(dailyNotesFolder, config.mediaSubFolder)
    createFolder(mediaSubFolder)

    return dailyNotesFolder

# -----------------------------------------------------------------------------
#
# Generate the output folder name for the media files (attachments).
#
# Notes
# 
#   - if it's a regular message, the folder will be the destination person slug
#   - if it's an attachment, the folder will be the source (sender)
#
# Parameters:
#
#   - entity: a Person or a Group object
#   - outputFolder: root folder where the subfolder per-person / files created
#   - message: the current message being processed
#   - mySlug: slug of the person who runs this tool
#
# -----------------------------------------------------------------------------
def getMediaFolderName(entity, peopleFolder, message, config):

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if type(entity) == Group:
        folder = os.path.join(peopleFolder, entity.slug)

    elif message.isNoteToSelf() and len(config.dailyNotesSubFolder):
        folder = os.path.join(config.outputFolder, config.dailyNotesSubFolder)

    elif message.hasAttachment() and message.sourceSlug == config.mySlug:
        folder = os.path.join(peopleFolder, config.mySlug)
    
    else:
        folder = os.path.join(peopleFolder, entity.slug)

    return folder

# -----------------------------------------------------------------------------
#
# Generate the output folder name.
#
# Notes
# 
#   - if it's a regular message, the folder will be the destination person slug
#
# Parameters:
#
#   - entity: a Person or a Group object
#   - outputFolder: root folder where the subfolder per-person / files created
#   - message: the current message being processed
#   - config: the configuration
#
# -----------------------------------------------------------------------------
def getMarkdownFolderName(entity, outputFolder, message, config):

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if isinstance(entity, Group):
        folder = os.path.join(outputFolder, entity.slug)
    elif message.isNoteToSelf() and len(config.dailyNotesSubFolder):
         folder = config.dailyNotesSubFolder
    else:
        folder = os.path.join(outputFolder, entity.slug)

    return folder

# -----------------------------------------------------------------------------
#
# Create a folder for a specific person or group's messages.
#
# Parameters:
#
#    - thing - a Person or a Group
#    - config - all of the Config(uration)
#
# Returns:
#
#    - False - folder was not created
#    - True - folder was created
#
# Notes:
#
#    - the `media` sub-folder will be created separately
#
# -----------------------------------------------------------------------------
def createThingFolder(thing, config):
        
    created = False
    folder = ""

    if isinstance(thing, Person):
        folder = os.path.join(config.outputFolder, config.peopleSubFolder)
    elif isinstance(thing, Group):
        folder = config.groupsFolder

    if len(folder) and len(thing.slug):
        thingFolder = os.path.join(folder, thing.slug)
        try:
            created = createFolder(thingFolder)
        except Exception as e:
            print(e)

    return created

# -----------------------------------------------------------------------------
#
# Format a Message object in Markdown
#
# Parameters:
#
#    - message - the message being converted to Markdown
#    - config - for settings
#    - people - array of Persons
#
# -----------------------------------------------------------------------------
def getMarkdown(message, config, people):

    text = ""

    if config.timeNameSeparate:
        text += NEW_LINE + message.timeStr + NEW_LINE

    firstName = config.getFirstNameBySlug(message.sourceSlug)

    # don't include first name if Note-to-Self since I know who I am!
    if not message.isNoteToSelf(): 
        text += firstName

    if not config.timeNameSeparate and config.includeTimestamp:
        if not message.isNoteToSelf():
            text += " " + config.getStr(config.STR_AT) + " "
        text += message.timeStr

    if config.colonAfterContext: 
        text += ":"
        
    if not config.timeNameSeparate: 
        text += NEW_LINE

    for attachment in message.attachments:
        text += attachment.generateLink(config)
    
    text += NEW_LINE + MD_QUOTE

    if config.includeQuote and len(message.quote.text):
    
        lengthOfQuotedText = len(message.quote.text)
        if lengthOfQuotedText:
            text += MD_QUOTE + message.quote.authorName + ": "
            quotedText = message.quote.text
            if lengthOfQuotedText > config.MAX_LEN_QUOTED_TEXT:
                quotedText = quotedText.quote.text[:config.MAX_LEN_QUOTED_TEXT]
                lastSpace = quotedText.rfind(' ')
                text += quotedText[:lastSpace] 
                text += "..."
            else: 
                text += quotedText

            text += NEW_LINE + MD_QUOTE + NEW_LINE + MD_QUOTE

    if len(message.body):
        text += message.body + NEW_LINE

    if config.includeReactions and len(message.reactions):
        text += MD_QUOTE + NEW_LINE + MD_QUOTE
        for reaction in message.reactions:
            firstName = config.getFirstNameBySlug(reaction.sourceSlug)
            text += reaction.emoji + "*" + firstName.lower() + "*   "
        text += NEW_LINE

    text += NEW_LINE

    return text

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

    for message in messages:
        for reaction in reactions:
            if message.timeStamp == reaction.targetTimeSent:
                message.reactions.append(reaction)
                count +=1

    return count

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
def appendMessage(message, thing):

    dateFound = False

    try:

        # go through existing dates and add message there
        for messagesOnDate in thing.messages:
            if message.dateStr == messagesOnDate.dateStr:
                dateFound = True
                messagesOnDate.messages.append(message)

        # if the date was not found, create it
        if dateFound == False:
            newDate = DatedMessages()
            newDate.dateStr = message.dateStr
            newDate.messages.append(message)
            thing.messages.append(newDate)

    except Exception as e:
        print(e)

# -----------------------------------------------------------------------------
#
# Divy up the messages to the groups and people they were with, by day
# 
# Parameters:
#
#    messages - the messages to be added
#    config - the configuration, an instance of Config
#
# -----------------------------------------------------------------------------
def addMessages(messages, config):

    me = config.getMe()
    
    for message in messages:
        if len(message.groupSlug):
            for group in config.groups:
                if message.groupSlug == group.slug:
                    appendMessage(message, group)
                    message.processed = True

        if not message.processed:
            if message.isNoteToSelf():
                appendMessage(message, me)
                message.processed = True
            else:
                for person in config.people:
                    if person.slug != me.slug and (person.slug == message.destinationSlug or person.slug == message.sourceSlug): 
                        appendMessage(message, person)
                        message.processed = True
                        break
    return


# -----------------------------------------------------------------------------
# 
# Create the metadata aka FrontMatter for the Markdown file
#
# Parameters:
#
#    message - the messages to be added
#    mySlug - short label that represents me, e.g. 'bernie'
#    config - the configuration, an instance of Config
#
# Notes:
#
#    `service` is what was used to send/receive message e.g. YAML_SERVICE_SMS
#
# -----------------------------------------------------------------------------
def getFrontMatter(message, mySlug, config):

    frontMatter = YAML_DASHES 
    frontMatter += YAML_TAGS + ": [" + TAG_CHAT + "]" + NEW_LINE
    frontMatter += YAML_PERSON_SLUGS + ": ["
    
    if not message.groupSlug:
        frontMatter += message.sourceSlug

        if len(message.destinationSlug) and message.isNoteToSelf() == False:
            frontMatter += ", " + message.destinationSlug
    
    elif len(message.groupSlug):
        firstTime = True
        for group in config.groups:
            if group.slug == message.groupSlug:
                for personSlug in group.members:
                    if not firstTime: 
                        frontMatter += ", "
                    frontMatter += personSlug
                    firstTime = False
                break

    elif len(message.sourceSlug) and message.sourceSlug != mySlug:
        frontMatter += ", " + message.sourceSlug

    if len(message.dateStr)==0: 
        dateStr = "null"
    else:
        dateStr = message.dateStr

    if len(message.timeStr)==0: 
        timeStr = "null"
    else: 
        timeStr = message.timeStr

    frontMatter += "]" + NEW_LINE
    frontMatter += YAML_DATE + ": " + dateStr + NEW_LINE
    frontMatter += YAML_TIME + ": " + timeStr + NEW_LINE
    frontMatter += YAML_SERVICE_SLUG + ": " + config.service + NEW_LINE
    frontMatter += YAML_DASHES + NEW_LINE

    return frontMatter

# -----------------------------------------------------------------------------
#
# Parameters:
#
#   - fileName: the file to open
#   - config: all the settings, instance of Config
#
# Returns: a file handle
#
# -----------------------------------------------------------------------------
def openOutputFile(fileName, config):

    outputFile = False

    try:
        outputFile = open(fileName, 'a', encoding="utf-8")

    except Exception as e:
        print(config.getStr(config.STR_ERROR) + " " + config.getStr(config.STR_COULD_NOT_OPEN_FILE) + " " + str(e))
        print(e)

    return outputFile

# -----------------------------------------------------------------------------
#
# Create a dated Markdown file with the messages between myself and the person.
#  
# Doesn't create/append to existing file as it's not smart enough to look 
# inside the file to see what is already there.
#
# Parameters:
#
#   - entity - a Person or a Group object
#   - folder - folder where the markdown file is to be created
#   - config - config settings
# 
# -----------------------------------------------------------------------------
def createMarkdownFile(entity, folder, config):

    exists = False
    
    for datedMessages in entity.messages:

        for message in datedMessages.messages:

            # where the output files will go
            fileName = message.dateStr + OUTPUT_FILE_EXTENSION

            if message.isNoteToSelf():
                dailyNotesFolder = createDailyNotesFolders(config)
                fileName = os.path.join(dailyNotesFolder, fileName)
            else: 
                createThingFolder(entity, config)
                fileName = os.path.join(folder, fileName)
            
            exists = os.path.exists(fileName)
            outputFile = openOutputFile(fileName, config)
            
            if outputFile:
                # add the front matter if this is a new file
                if exists == False and (not message.isNoteToSelf() or message.groupSlug):
                    frontMatter = getFrontMatter(message, config.mySlug, config)
                    outputFile.write(frontMatter)
         
                # don't add to the file if it's previously created
                # UNLESS it's a note-to-self
                age = time.time() - os.path.getctime(fileName)
                if age < WELL_AGED or message.isNoteToSelf():
                    try:
                        outputFile.write(getMarkdown(message, config, entity))
                        outputFile.close()
                    except Exception as e:
                        pass

# -----------------------------------------------------------------------------
#
# Move the attachments from the attachments folder to the folder of the
# specific person that shared them. If it's a group message, move the 
# attachments under the `group` folder.
#
# Parameters
# 
#   - entities - either a collection of Person or Group objects
#   - folder - top-level folder where the files will go
#   - config - all the configuration
# 
# -----------------------------------------------------------------------------
def moveAttachments(entities, folder, config):

    sourceFile = ""
    destFile = ""

    for entity in entities:
        for datedMessages in entity.messages:
            for message in datedMessages.messages:
                destFolder = getMediaFolderName(entity, folder, message, config)
                destFolder = os.path.join(destFolder, config.mediaSubFolder)

                # create the `media` subfolder if it doesn't exist
                if len(message.attachments) and not os.path.exists(destFolder):
                    createFolder(destFolder)

                for attachment in message.attachments:
                    if len(attachment.id):
                        sourceFile = os.path.join(config.sourceFolder, config.attachmentsSubFolder)
                        sourceFile = os.path.join(sourceFile, attachment.id)
                        
                        # Signal doesn't add a file suffix, so we add it here
                        if config.service == YAML_SERVICE_SIGNAL:
                            destFile = os.path.join(destFolder, attachment.addSuffix(config))
                        else:
                            destFile = os.path.join(destFolder, attachment.id)

                        if config.debug:
                            print(sourceFile + ' -> ' + destFile)
                        
                        if os.path.exists(sourceFile) and not os.path.exists(destFile):
                            try: 
                                if config.debug:
                                    shutil.copy(sourceFile, destFile)
                                else:
                                    shutil.move(sourceFile, destFile)
                            except Exception as e:
                                print(config.getStr(config.STR_COULD_NOT_MOVE_THE_ATTACHMENT) + ": " + sourceFile + " -> " + destFile)
                                print(e)

# -----------------------------------------------------------------------------
#
# Set up all of the folders and then call back to loadMessages() from the 
# client of this library to do specific message-type (e.g. SMS) loading of
# the messages. 
#
# Parameters
# 
#   - config - settings including collections of Groups of Persons
#   - loadMessages - function that loads the messages into `messages[]`
#   - messages - array containing all of the Messages
#   - reactions - array containing all of the Reactions
# 
# -----------------------------------------------------------------------------
def markdown(config, loadMessages, messages, reactions):

    messagesFile = os.path.join(config.sourceFolder, config.fileName)

    suffix = pathlib.Path(messagesFile).suffix

    # make a copy of the source file if in debug mode or move it so 
    # we know it's been dealt with / processed.
    try:
        Path(config.archiveSubFolder).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(config.getStr(config.STR_COULD_CREATE_ARCHIVE_SUBFOLDER) + ": " + messagesFile)
        print(e)
        return False

    nowStr = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%m-%S')
    fileName = config.service + '_' + nowStr + suffix
    destFile = os.path.join(config.archiveSubFolder, fileName)
    print(destFile)
    try:
        if config.debug:
            shutil.copy(messagesFile, destFile)
        elif os.path.exists(config.archiveSubFolder):
            shutil.move(messagesFile, destFile)

    except Exception as e:
        if config.debug:
            print(config.getStr(config.STR_COULD_NOT_MOVE_MESSAGES_FILE) + ": " + messagesFile)
        else:
            print(config.getStr(config.STR_COULD_NOT_COPY_MESSAGES_FILE) + ": " + messagesFile)
        print(e)
        pass
            
    if os.path.exists(destFile) and loadMessages(destFile, messages, reactions, config):
        
        addReactions(messages, reactions)
        addMessages(messages, config)

        moveAttachments(config.people, config.peopleFolder, config)
        moveAttachments(config.groups, config.groupsFolder, config)

        for person in config.people:
            folder = os.path.join(config.peopleFolder, person.slug)
            createMarkdownFile(person, folder, config)

        for group in config.groups:
            folder = os.path.join(config.groupsFolder, group.slug)
            createMarkdownFile(group, folder, config)

    return True

def getArguments(config):

    parser = ArgumentParser()
    
    parser.add_argument("-s", "--sourcefolder", dest="sourceFolder", default=".",
                        help=config.STR_SOURCE_FOLDER)
    
    parser.add_argument("-f", "--file", dest="fileName",
                        help=config.STR_SOURCE_MESSAGE_FILE, metavar="FILE")
    
    parser.add_argument("-o", "--outputfolder", dest="outputFolder", default=".",
                        help=config.STR_OUTPUT_FOLDER)
    
    parser.add_argument("-l", "--language", dest="language", default="1",
                        help=config.STR_LANGUAGE_SETTING)
    
    parser.add_argument("-m", "--myslug", dest="mySlug", default="NOSLUG",
                        help=config.STR_MY_SLUG_SETTING)
    
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help=config.STR_DONT_PRINT_DEBUG_MSGS)
        
        
    args = parser.parse_args()

    return args

def setup(config, service):

    loaded = False

    if len(service):
        config.service = service

    args = getArguments(config)

    if args.debug:
        config.debug = args.debug
    
    # load the default settings
    if config.loadSettings():

        # then override them with any command line settings
        if args.fileName:
            config.fileName = args.fileName
    
        if args.outputFolder:
            config.outputFolder = args.outputFolder
        
        if args.sourceFolder:
            config.sourceFolder = args.sourceFolder

        if args.mySlug:
            config.mySlug = args.mySlug

        if config.loadStrings():
            if config.loadMIMETypes():
                if config.loadPeople():
                    if config.loadGroups():
                        loaded = True

    config.peopleFolder = os.path.join(config.outputFolder, config.peopleSubFolder)
    config.groupsFolder = os.path.join(config.peopleFolder, config.groupsSubFolder)
    
    if config.debug:
        print("sourceFolder: " + config.sourceFolder)
        print("messages file: " + config.fileName)
        print("outputFolder: " + config.outputFolder)
        print("peopleFolder: " + config.peopleFolder)
        print("groupsFolder: " + config.groupsFolder)

    if not loaded:
        print('Setup failed.')
    
    return loaded