import os
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
YAML_PERSON_SLUGS = "person-slugs"
YAML_SERVICE_SLUG = "service-slug"
YAML_TAGS = "tags"
YAML_DATE = "date"
YAML_TIME = "time"
YAML_SERVICE_SIGNAL = "signal"
YAML_SERVICE_SMS = "sms"
TAG_CHAT = "chat"

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
                    frontMatter = getFrontMatter(theMessage, theConfig.mySlug, theConfig)
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
#    mySlug - short label that represents me, e.g. 'bernie'
#    theConfig - the configuration, an instance of Config
#
# Notes:
#
#    `service` is what was used to send/receive message e.g. YAML_SERVICE_SMS
#
# -----------------------------------------------------------------------------
def getFrontMatter(theMessage, mySlug, theConfig):

    frontMatter = YAML_DASHES 
    frontMatter += YAML_TAGS + ": [" + TAG_CHAT + "]" + NEW_LINE
    frontMatter += YAML_PERSON_SLUGS + ": ["
    
    if not theMessage.groupSlug:
        frontMatter += theMessage.sourceSlug

        if len(theMessage.destinationSlug) and theMessage.isNoteToSelf() == False:
            frontMatter += ", " + theMessage.destinationSlug
    
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

    elif len(theMessage.sourceSlug) and theMessage.sourceSlug != mySlug:
        frontMatter += ", " + theMessage.sourceSlug

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
    frontMatter += YAML_SERVICE_SLUG + ": " + theConfig.service + NEW_LINE
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

    if theConfig.timeNameSeparate:
        text += NEW_LINE + theMessage.timeStr + NEW_LINE

    firstName = theConfig.getFirstNameBySlug(theMessage.sourceSlug)

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
        text += theAttachment.generateLink(theConfig)
    
    text += NEW_LINE + MD_QUOTE

    if theConfig.includeQuote and hasattr(theMessage.quote, 'text') and len(theMessage.quote.text):
    
        lengthOfQuotedText = len(theMessage.quote.text)
        if lengthOfQuotedText:
            text += MD_QUOTE + theMessage.quote.authorName + ": "
            quotedText = theMessage.quote.text
            if lengthOfQuotedText > theConfig.MAX_LEN_QUOTED_TEXT:
                quotedText = quotedText.quote.text[:theConfig.MAX_LEN_QUOTED_TEXT]
                lastSpace = quotedText.rfind(' ')
                text += quotedText[:lastSpace] 
                text += "..."
            else: 
                text += quotedText

            text += NEW_LINE + MD_QUOTE + NEW_LINE + MD_QUOTE

    if len(theMessage.body):
        text += theMessage.body + NEW_LINE

    if theConfig.includeReactions and len(theMessage.reactions):
        text += MD_QUOTE + NEW_LINE + MD_QUOTE
        for theReaction in theMessage.reactions:
            firstName = theConfig.getFirstNameBySlug(theReaction.sourceSlug)
            text += theReaction.emoji + "*" + firstName.lower() + "*   "
        text += NEW_LINE

    text += NEW_LINE

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
#   - outputFolder: root folder where the subfolder per-person / files created
#   - theMessage: the current message being processed
#   - mySlug: slug of the person who runs this tool
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

    elif theMessage.hasAttachment() and theMessage.sourceSlug == theConfig.mySlug:
        folder = os.path.join(peopleFolder, theConfig.mySlug)
    
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
