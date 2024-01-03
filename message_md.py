import os
import shutil

import pathlib
from pathlib import Path

from argparse import ArgumentParser
from datetime import datetime
import config
import markdown
import attachment
import message

def getArguments(theConfig):

    parser = ArgumentParser()

    parser.add_argument("-c", "--config", dest="configFolder", default=".",
                        help=theConfig.STR_CONFIG_FOLDER)
    
    parser.add_argument("-s", "--sourcefolder", dest="sourceFolder", default=".",
                        help=theConfig.STR_SOURCE_FOLDER)
    
    parser.add_argument("-f", "--file", dest="fileName",
                        help=theConfig.STR_SOURCE_MESSAGE_FILE, metavar="FILE")
    
    parser.add_argument("-o", "--outputfolder", dest="outputFolder", default=".",
                        help=theConfig.STR_OUTPUT_FOLDER)
    
    parser.add_argument("-l", "--language", dest="language", default="1",
                        help=theConfig.STR_LANGUAGE_SETTING)
    
    parser.add_argument("-m", "--myslug", dest="mySlug", default="NOSLUG",
                        help=theConfig.STR_MY_SLUG_SETTING)
    
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help=theConfig.STR_DONT_PRINT_DEBUG_MSGS)
    
    parser.add_argument("-b", "--begin", dest="fromDate", default="",
                        help=theConfig.STR_FROM_DATE)
     
    args = parser.parse_args()

    return args

def setup(theConfig, service, reversed=False):

    loaded = False
    init = False

    if len(service):
        theConfig.service = service

    if reversed:
        theConfig.reversed = True

    args = getArguments(theConfig)

    if args.debug:
        theConfig.debug = args.debug

    if args.configFolder:
        theConfig.configFolder = args.configFolder
  
    # load the default settings
    if theConfig.loadSettings():

        # then override them with any command line settings
        if args.sourceFolder:
            theConfig.sourceFolder = args.sourceFolder

        if args.fileName:
            theConfig.fileName = os.path.join(args.sourceFolder, args.fileName)
        
        if args.outputFolder:
            theConfig.outputFolder = args.outputFolder
        
        if args.mySlug:
            theConfig.mySlug = args.mySlug

        if args.fromDate:
            theConfig.fromDate = args.fromDate

        if theConfig.loadStrings():
            if theConfig.loadMIMETypes():
                if theConfig.loadPeople():
                    if theConfig.loadGroups():
                        loaded = True

    theConfig.peopleFolder = os.path.join(theConfig.outputFolder, theConfig.peopleSubFolder)
    theConfig.groupsFolder = os.path.join(theConfig.peopleFolder, theConfig.groupsSubFolder)
    
    if theConfig.debug:
        print("configFolder: " + theConfig.configFolder)
        print("sourceFolder: " + theConfig.sourceFolder)
        print("fileName: " + theConfig.fileName)
        print("outputFolder: " + theConfig.outputFolder)
        print("peopleFolder: " + theConfig.peopleFolder)
        print("groupsFolder: " + theConfig.groupsFolder)
        print("fromDate: " + theConfig.fromDate)

    if loaded:
        # email service doesn't require a messages file
        if theConfig.service == markdown.YAML_SERVICE_EMAIL:
            init = True
        elif not theConfig.fileName:
            print('No messages file specified')
        elif not os.path.exists(theConfig.fileName):
            print('The messages file could not be found')
        else:
            init = True
    else:
        print('Setup failed.')
    
    return init

# -----------------------------------------------------------------------------
#
# Creates an archive subfolder and then either copies or moves - depending on 
# configuration - the message file there, names the file with date/time, and
# returns the file path.
#
# Parameters
# 
#   - theConfig - settings including collections of Groups of Persons
# 
# -----------------------------------------------------------------------------
def setupFolders(theConfig):

    destFile = ""
    
    if not theConfig.fileName:
        return False

    messagesFile = theConfig.fileName

    suffix = pathlib.Path(messagesFile).suffix

    # make a copy of the source file if in debug mode or move it so 
    # we know it's been dealt with / processed.
    try:
        Path(theConfig.archiveSubFolder).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(theConfig.getStr(theConfig.STR_COULD_CREATE_ARCHIVE_SUBFOLDER) + ": " + messagesFile)
        print(e)
        return False

    nowStr = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%m-%S')
    fileName = theConfig.service + '_' + nowStr + suffix
    destFile = os.path.join(theConfig.archiveSubFolder, fileName)
    try:
        if theConfig.debug:
            shutil.copy(messagesFile, destFile)
        elif os.path.exists(theConfig.archiveSubFolder):
            shutil.move(messagesFile, destFile)

    except Exception as e:
        if theConfig.debug:
            print(theConfig.getStr(theConfig.STR_COULD_NOT_MOVE_MESSAGES_FILE) + ": " + messagesFile)
        else:
            print(theConfig.getStr(theConfig.STR_COULD_NOT_COPY_MESSAGES_FILE) + ": " + messagesFile)
            print(e)
        pass

    return destFile

# -----------------------------------------------------------------------------
#
# Set up all of the folders and then call back to loadMessages() from the 
# client of this library to do specific message-type (e.g. SMS) loading of
# the messages. 
#
# Parameters
# 
#   - theConfig - settings including collections of Groups of Persons
#   - loadMessages - function that loads the messages into `messages[]`
#   - messages - array containing all of the Messages
#   - reactions - array containing all of the Reactions
# 
# -----------------------------------------------------------------------------
def getMarkdown(theConfig, loadMessages, messages, reactions):

    destFile = ""

    # email doesn't have a messages file to parse
    if theConfig.service != markdown.YAML_SERVICE_EMAIL:
        destFile = setupFolders(theConfig)

    if theConfig.service != markdown.YAML_SERVICE_EMAIL or os.path.exists(destFile): 
        
        if loadMessages(destFile, messages, reactions, theConfig):
            
            # add the reactions to the corresponding messages
            message.addReactions(messages, reactions)

            # divy up messages to the groups and people they were with
            message.addMessages(messages, theConfig)

            # for email service, the attachments are put in the right folder 
            # as each email attachment is processed. No need to move them 
            if theConfig.service != markdown.YAML_SERVICE_EMAIL:
                attachment.moveAttachments(theConfig.people, theConfig.peopleFolder, theConfig)
                attachment.moveAttachments(theConfig.groups, theConfig.groupsFolder, theConfig)

            # generate the Markdown for each person
            for thePerson in theConfig.people:
                folder = os.path.join(theConfig.peopleFolder, thePerson.slug)
                markdown.createMarkdownFile(thePerson, folder, theConfig)

            # generate the Markdown for each group
            for theGroup in theConfig.groups:
                folder = os.path.join(theConfig.groupsFolder, theGroup.slug)
                markdown.createMarkdownFile(theGroup, folder, theConfig)

    return True