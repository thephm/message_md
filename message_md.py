import os
import shutil

import pathlib
from pathlib import Path

from argparse import ArgumentParser
from datetime import datetime
import message
import attachment
import markdown

def getArguments(theConfig):

    parser = ArgumentParser()
    
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
        
    args = parser.parse_args()

    return args

def setup(theConfig, service):

    loaded = False

    if len(service):
        theConfig.service = service

    args = getArguments(theConfig)

    if args.debug:
        theConfig.debug = args.debug
    
    # load the default settings
    if theConfig.loadSettings():

        # then override them with any command line settings
        if args.fileName:
            theConfig.fileName = args.fileName
    
        if args.outputFolder:
            theConfig.outputFolder = args.outputFolder
        
        if args.sourceFolder:
            theConfig.sourceFolder = args.sourceFolder

        if args.mySlug:
            theConfig.mySlug = args.mySlug

        if theConfig.loadStrings():
            if theConfig.loadMIMETypes():
                if theConfig.loadPeople():
                    if theConfig.loadGroups():
                        loaded = True

    theConfig.peopleFolder = os.path.join(theConfig.outputFolder, theConfig.peopleSubFolder)
    theConfig.groupsFolder = os.path.join(theConfig.peopleFolder, theConfig.groupsSubFolder)
    
    if theConfig.debug:
        print("sourceFolder: " + theConfig.sourceFolder)
        print("messages file: " + theConfig.fileName)
        print("outputFolder: " + theConfig.outputFolder)
        print("peopleFolder: " + theConfig.peopleFolder)
        print("groupsFolder: " + theConfig.groupsFolder)

    if not loaded:
        print('Setup failed.')
    
    return loaded

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

    messagesFile = os.path.join(theConfig.sourceFolder, theConfig.fileName)

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
    print(destFile)
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
            
    if os.path.exists(destFile) and loadMessages(destFile, messages, reactions, theConfig):
        
        message.addReactions(messages, reactions)
        message.addMessages(messages, theConfig)

        attachment.moveAttachments(theConfig.people, theConfig.peopleFolder, theConfig)
        attachment.moveAttachments(theConfig.groups, theConfig.groupsFolder, theConfig)

        for thePerson in theConfig.people:
            folder = os.path.join(theConfig.peopleFolder, thePerson.slug)
            markdown.createMarkdownFile(thePerson, folder, theConfig)

        for theGroup in theConfig.groups:
            folder = os.path.join(theConfig.groupsFolder, theGroup.slug)
            markdown.createMarkdownFile(theGroup, folder, theConfig)

    return True