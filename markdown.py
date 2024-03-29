import os
import re
import time

#import pathlib
from pathlib import Path

import person
import group

# some constants
NEW_LINE = "\n"
SPACE = " "
TWO_SPACES = SPACE + SPACE
MD_QUOTE = ">" + SPACE
NEW_LINE = "\n"
WELL_AGED = 30 # seconds
OUTPUT_FILE_EXTENSION = ".md"

# YAML front matter 
YAML_DASHES = "---" + NEW_LINE
YAML_PEOPLE = "people"
YAML_SERVICE = "service"
YAML_TAGS = "tags"
YAML_DATE = "date"
YAML_TIME = "time"
YAML_SERVICE_SIGNAL = "signal"
YAML_SERVICE_SMS = "sms"
YAML_SERVICE_LINKEDIN = "linkedin"
YAML_SERVICE_EMAIL = "email"
TAG_CHAT = "chat"
TAG_EMAIL = "email"
YAML_SUBJECT = "subject"
YAML_MESSAGE_ID = "message-id"

# -----------------------------------------------------------------------------
#
# Create a folder for a specific person or group's messages.
#
# Parameters:
#
#    - thing - a Person or a Group
#    - theConfig - all of the Config(uration)
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
def createThingFolder(thing, theConfig):
        
    created = False
    folder = ""

    if isinstance(thing, person.Person):
        folder = os.path.join(theConfig.outputFolder, theConfig.peopleSubFolder)
    elif isinstance(thing, group.Group):
        folder = theConfig.groupsFolder

    if len(folder) and len(thing.slug):
        thingFolder = os.path.join(folder, thing.slug)
        try:
            created = createFolder(thingFolder)
        except Exception as e:
            print(e)

    return created

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
# Create a dated Markdown file with the messages between myself and the person.
#  
# Doesn't create/append to existing file as it's not smart enough to look 
# inside the file to see what is already there.
#
# Only create files for messages after `config.fromDate` if there's a date set
#
# Parameters:
#
#   - entity - a Person or a Group object
#   - folder - folder where the markdown file is to be created
#   - config - config settings
# 
# -----------------------------------------------------------------------------
def createMarkdownFile(entity, folder, theConfig):

    exists = False
    
    for datedMessages in entity.messages:

        for theMessage in datedMessages.messages:

            if theConfig.fromDate and (theMessage.dateStr < theConfig.fromDate):
                continue

            # convert to Markdown and if no message, move on to the next one
            theMarkdown = getMarkdown(theMessage, theConfig, entity)
            if not len(theMarkdown):
                continue

            # where the output files will go
            fileName = theMessage.dateStr + OUTPUT_FILE_EXTENSION

            if theMessage.isNoteToSelf():
                dailyNotesFolder = createDailyNotesFolders(theConfig)
                fileName = os.path.join(dailyNotesFolder, fileName)
            else: 
                createThingFolder(entity, theConfig)
                fileName = os.path.join(folder, fileName)
            
            exists = os.path.exists(fileName)

            outputFile = openOutputFile(fileName, theConfig)
            
            if outputFile:
                # add the front matter if this is a new file
                if exists == False and (not theMessage.isNoteToSelf() or theMessage.groupSlug):
                    frontMatter = getFrontMatter(theMessage, theConfig)
                    outputFile.write(frontMatter)
         
                # don't add to the file if it's previously created
                # UNLESS it's a note-to-self
                age = time.time() - os.path.getctime(fileName)
                if age < WELL_AGED or theMessage.isNoteToSelf():
                    try:
                        outputFile.write(getMarkdown(theMessage, theConfig, entity))
                        outputFile.close()
                    except Exception as e:
                        print(e)
                        pass

# -----------------------------------------------------------------------------
#
# Parameters:
#
#   - fileName: the file to open
#   - theConfig: all the settings, instance of Config
#
# Returns: a file handle
#
# -----------------------------------------------------------------------------
def openOutputFile(fileName, theConfig):

    outputFile = False

    try:
        outputFile = open(fileName, 'a', encoding="utf-8")

    except Exception as e:
        print(theConfig.getStr(theConfig.STR_ERROR) + " " + theConfig.getStr(theConfig.STR_COULD_NOT_OPEN_FILE) + " " + str(e))
        print(e)

    return outputFile

# -----------------------------------------------------------------------------
# 
# Create the metadata aka FrontMatter for the Markdown file
#
# Parameters:
#
#    theMessage - the messages to be added
#    theConfig - the configuration, an instance of Config
#
# Notes:
#
#    `service` is what was used to send/receive message e.g. YAML_SERVICE_SMS
#
# -----------------------------------------------------------------------------
def getFrontMatter(theMessage, theConfig):

    frontMatter = YAML_DASHES 
    frontMatter += YAML_TAGS + ": ["
    
    if theConfig.service == YAML_SERVICE_EMAIL:
        frontMatter += TAG_EMAIL
    else:
        frontMatter += TAG_CHAT

    if theMessage.groupSlug:
        frontMatter += ", " + theMessage.groupSlug
    frontMatter += "]" + NEW_LINE
    frontMatter += YAML_PEOPLE + ": ["
    
    if not theMessage.groupSlug:
        frontMatter += theMessage.fromSlug

        if len(theMessage.toSlugs) and theMessage.isNoteToSelf() == False:
            frontMatter += ", " + ", ".join(theMessage.toSlugs)
    
    elif len(theMessage.groupSlug):
        firstTime = True
        for group in theConfig.groups:
            if group.slug == theMessage.groupSlug:
                for personSlug in group.members:
                    if not firstTime: 
                        frontMatter += ", "
                    frontMatter += personSlug
                    firstTime = False
                break

    elif len(theMessage.fromSlug) and theMessage.fromSlug != theConfig.me.slug:
        frontMatter += ", " + theMessage.fromSlug

    if len(theMessage.dateStr)==0: 
        dateStr = "null"
    else:
        dateStr = theMessage.dateStr

    if len(theMessage.timeStr)==0: 
        timeStr = "null"
    else: 
        timeStr = theMessage.timeStr

    frontMatter += "]" + NEW_LINE
    frontMatter += YAML_DATE + ": " + dateStr + NEW_LINE
    frontMatter += YAML_TIME + ": " + timeStr + NEW_LINE
    subject = theMessage.subject

    if subject and isinstance(subject, str): 
        # replace double quotes with single quotes inside double-quoted strings
        subject = re.sub(r'"([^"]*)"', lambda match: "'" + match.group(1) + "'", subject)
        frontMatter += YAML_SUBJECT + ": \"" + subject + "\"" + NEW_LINE
    frontMatter += YAML_SERVICE + ": " + theConfig.service + NEW_LINE
    frontMatter += YAML_DASHES + NEW_LINE

    return frontMatter

# -----------------------------------------------------------------------------
#
# Format a Message object in Markdown
#
# Parameters:
#
#    - theMessage - the message being converted to Markdown
#    - theConfig - for settings
#    - people - array of Persons
#
# -----------------------------------------------------------------------------
def getMarkdown(theMessage, theConfig, people):

    text = ""
    firstName = ""
    fromSlug = theMessage.fromSlug

    if theConfig.timeNameSeparate:
        text += NEW_LINE + theMessage.timeStr + NEW_LINE

    if fromSlug:
        firstName = theConfig.getFirstNameBySlug(fromSlug)
    else: 
        # assume it's from me
        if theConfig.me.slug not in theMessage.toSlugs:
            firstName = theConfig.me.firstName

    # I've seen cases with SMS Backup where `from_address="null"` and,
    # in turn, code can't get a source slug, so we skip the message
    if not firstName:
        if (theConfig.debug):
            print("No first name, fromSlug='" + fromSlug + "'")
            print(theMessage)
        return text

    # don't include first name if Note-to-Self since I know who I am!
    if not theMessage.isNoteToSelf(): 
        text += firstName

    if not theConfig.timeNameSeparate and theConfig.includeTimestamp:
        if not theMessage.isNoteToSelf():
            text += " " + theConfig.getStr(theConfig.STR_AT) + " "
        text += theMessage.timeStr

    if theConfig.colonAfterContext: 
        text += ":"

    if not theConfig.timeNameSeparate: 
        text += NEW_LINE

    for theAttachment in theMessage.attachments:
        link = theAttachment.generateLink(theConfig)
        text += link

    text += NEW_LINE

    try:
        quotedText = theMessage.quote.text
        lengthOfQuotedText = len(theMessage.quote.text)

        if theConfig.includeQuote and hasattr(theMessage.quote, 'text') and lengthOfQuotedText:
        
            if lengthOfQuotedText:
                text += MD_QUOTE + MD_QUOTE
                if theMessage.quote.authorName:
                    text += theMessage.quote.authorName + ": "
                if lengthOfQuotedText > theConfig.MAX_LEN_QUOTED_TEXT:
                    quotedText = quotedText[:theConfig.MAX_LEN_QUOTED_TEXT]
                    lastSpace = quotedText.rfind(' ')
                    text += quotedText[:lastSpace] 
                    text += "..."
                else: 
                    text += quotedText

                text += NEW_LINE + MD_QUOTE + NEW_LINE
    except:
        pass

    if len(theMessage.body):
        if theConfig.service != YAML_SERVICE_EMAIL:
            text += MD_QUOTE
        text += theMessage.body + NEW_LINE

    if theConfig.includeReactions and len(theMessage.reactions):
        text += MD_QUOTE + NEW_LINE + MD_QUOTE
        for theReaction in theMessage.reactions:
            firstName = theConfig.getFirstNameBySlug(theReaction.fromSlug)
            text += str(theReaction.emoji) + " *" + firstName.lower() + "*   "
        text += NEW_LINE

    # can have messages with only a body or reactions or attachments
    if len(theMessage.body) or len(theMessage.reactions):
        text += NEW_LINE
    elif not len(theMessage.attachments): # if none of them then it's invalid
        text = ""

    return text

# -----------------------------------------------------------------------------
#
# Create folders for the daily notes. 
#
# Parameters:
#
#    - theConfig - all of the Config(uration)
#
# Notes:
#
#    - this is for notes-to-self that are stored in a separate folder from all
#      of the other messages
# 
# -----------------------------------------------------------------------------
def createDailyNotesFolders(theConfig):

    dailyNotesFolder = os.path.join(theConfig.outputFolder, theConfig.dailyNotesSubFolder)
    createFolder(dailyNotesFolder)
    mediaSubFolder = os.path.join(dailyNotesFolder, theConfig.mediaSubFolder)
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
#   - peopleFolder: root folder where the subfolder per-person / files created
#   - theMessage: the current message being processed
#   - theConfig - all of the Config(uration)
#
# -----------------------------------------------------------------------------
def getMediaFolderName(entity, peopleFolder, theMessage, theConfig):

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if type(entity) == group.Group:
        folder = os.path.join(peopleFolder, entity.slug)

    elif theMessage.isNoteToSelf() and len(theConfig.dailyNotesSubFolder):
        folder = os.path.join(theConfig.outputFolder, theConfig.dailyNotesSubFolder)

    elif theMessage.hasAttachment() and theMessage.fromSlug == theConfig.me.slug:
        folder = os.path.join(peopleFolder, theConfig.me.slug)
    
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
#   - theMessage: the current message being processed
#   - theConfig: the configuration
#
# -----------------------------------------------------------------------------
def getMarkdownFolderName(entity, outputFolder, theMessage, theConfig):

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if isinstance(entity, group.Group):
        folder = os.path.join(outputFolder, entity.slug)
    elif theMessage.isNoteToSelf() and len(theConfig.dailyNotesSubFolder):
         folder = theConfig.dailyNotesSubFolder
    else:
        folder = os.path.join(outputFolder, entity.slug)

    return folder
