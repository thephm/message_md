import json
import os
    
import markdown

import person
import group
from datetime import datetime

import pathlib
from pathlib import Path
from argparse import ArgumentParser

# config
CONFIG_FOLDER = "config"
STRINGS_FILE_NAME = "strings.json"
PEOPLE_FILE_NAME  = "people.json"
GROUPS_FILE_NAME  = "groups.json"
MIME_TYPES_FILE_NAME = "MIMETypes.json"
RESOURCES_FOLDER = "../../github/message_md/resources"

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

def Config():
    if _Config._instance is None:
        _Config._instance = _Config()
    return _Config._instance

# keeps all of the configuration
class _Config:
    _instance = None

    def __init__(self, fileName=""):

        self.SETTING_MY_SLUG = "my-slug"
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
        self.SETTING_IMAP_SERVER = "imap-server"
        self.SETTING_EMAIL_FOLDERS = "email-folders"
        self.SETTING_NOT_EMAIL_FOLDERS = "not-email-folders"
        self.SETTING_EMAIL_ACCOUNT = "email-account"
        self.SETTING_MAX_MESSAGES = "max-messages"

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
        self.STR_MOBILE_NOT_FOUND = 13
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
        self.STR_FROM_DATE = 25
        self.STR_CONFIG_FOLDER = 26
        self.STR_EMAIL_ACCOUNT = 27
        self.STR_PASSWORD = 28
        self.STR_IMAP_SERVER = 29
        self.STR_EMAIL_FOLDERS = 30
        self.STR_MAX_MESSAGES = 31

        self.MAX_LEN_QUOTED_TEXT = 70

        # fields in people file (PEOPLE_FILE_NAME)
        self.PERSON_FIELD_SLUG = "slug"
        self.PERSON_FIELD_FIRST_NAME = "first-name"
        self.PERSON_FIELD_LAST_NAME = "last-name"
        self.PERSON_FIELD_MOBILE = "mobile"
        self.PERSON_FIELD_EMAIL = "email"
        self.PERSON_FIELD_LINKEDIN_ID = "linkedin-id"
        self.PERSON_FIELD_CONVERSATION_ID = "conversation-id"

        # fields in groups file (GROUPS_FILE_NAME)
        self.GROUP_COLLECTION = "groups"
        self.GROUP_FIELD_ID = "id"
        self.GROUP_FIELD_SLUG = "slug"
        self.GROUP_FIELD_DESCRIPTION = "description"
        self.GROUP_FIELD_PEOPLE = "people"
        self.GROUP_FIELD_CONVERSATION_ID = "conversation-id"

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

        self.me = person.Person()
    
        # set the default config folder to the folder where this
        # script was run plus 
        folder = os.path.dirname(os.path.realpath(__file__))
        self.configFolder = os.path.join(folder, CONFIG_FOLDER)

        self.settingsFileName = "settings.json"
        self.service = ""
        self.reversed = False
        self.fileName = fileName
        self.language = self.ENGLISH
        self.mediaSubFolder = "media"
        self.imageEmbed = True
        self.imageWidth = 450
        self.sourceFolder = "../../messages"
        self.outputFolder = "../../output"
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
        self.fromDate = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.imapServer = ""
        self.emailAccount = ""
        self.emailFolders = ""
        self.password = ""
        self.maxMessages = 10000

    def __str__(self):
        
        output = self.SETTING_MY_SLUG + ": " + str(self.me.slug) + "\n"
        output += "configFolder: " + str(self.configFolder) + "\n"
        output += self.SETTING_ATTACHMENTS_SUBFOLDER + ": " + str(self.attachmentsSubFolder) + "\n"
        output += self.SETTING_ARCHIVE_SUBFOLDER + ": " + str(self.archiveSubFolder) + "\n"
        output += self.SETTING_OUTPUT_FOLDER + ": " + str(self.outputFolder) + "\n"
        output += self.SETTING_MEDIA_SUBFOLDER + ": " + str(self.mediaSubFolder) + "\n"
        output += self.SETTING_IMAGE_EMBED + ": " + str(self.imageEmbed) + "\n"
        output += self.SETTING_IMAGE_WIDTH + ": " + str(self.imageWidth) + "\n"
        output += self.SETTING_FOLDER_PER_PERSON + ": " + str(self.folderPerPerson) + "\n"
        output += self.SETTING_FILE_PER_PERSON + ": " + str(self.filePerPerson) + "\n"
        output += self.SETTING_FILE_PER_DAY + ": " + str(self.filePerDay) + "\n"
        output += self.SETTING_INCLUDE_TIMESTAMP + ": " + str(self.includeTimestamp) + "\n"
        output += self.SETTING_INCLUDE_REACTIONS + ": " + str(self.includeReactions) + "\n"
        output += self.SETTING_INCLUDE_QUOTE + ": " + str(self.includeQuote) + "\n"
        output += self.SETTING_COLON_AFTER_CONTEXT + ": " + str(self.colonAfterContext) + "\n"
        output += self.SETTING_TIME_NAME_SEPARATE + ": " + str(self.timeNameSeparate) + "\n"
        output += self.SETTING_DAILY_NOTES_SUBFOLDER + ": " + str(self.dailyNotesSubFolder) + "\n"
        output += self.SETTING_IMAP_SERVER + ": " + str(self.imapServer) + "\n"
        output += self.SETTING_EMAIL_ACCOUNT + ": " + str(self.emailAccount) + "\n"
        output += self.SETTING_EMAIL_FOLDERS + ": " + str(self.emailFolders) + "\n"
        output += self.SETTING_NOT_EMAIL_FOLDERS + ": " + str(self.notEmailFolders) + "\n"
        output += self.SETTING_MAX_MESSAGES + ": " + str(self.maxMessages) + "\n"
        
        return output

    def loadSettings(self):

        result = False

        try:
            settingsFileName = os.path.join(self.configFolder, self.settingsFileName)
            print("settingsFileName=" + settingsFileName)

            try:
                settingsFile = open(settingsFileName, 'r')
            except Exception as e:
                print(e)

            if settingsFile:

                self.settings = json.load(settingsFile)
                self.archiveSubFolder = os.path.join(self.sourceFolder, self.settings[self.SETTING_ARCHIVE_SUBFOLDER])
                messagesFileName = self.settings[self.SETTING_MESSAGES_FILE]
                
                if messagesFileName:
                    self.fileName = os.path.join(self.sourceFolder, messagesFileName)
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

                # this can be passed on the command line
                try:
                    self.me.slug = self.settings[self.SETTING_MY_SLUG]
                except:
                    pass

                # these can be passed on the command line
                try:
                    self.imapServer = self.settings[self.SETTING_IMAP_SERVER]
                    self.maxMessages = self.settings[self.SETTING_MAX_MESSAGES]
                    self.emailAccount = self.settings[self.SETTING_EMAIL_ACCOUNT]
                    self.emailFolders = self.settings[self.SETTING_EMAIL_FOLDERS].split(';')
                    if self.emailFolders == ['']:
                        self.emailFolders = []
                    self.notEmailFolders = self.settings[self.SETTING_NOT_EMAIL_FOLDERS].split(';')
                    if self.notEmailFolders == ['']:
                        self.notEmailFolders = []
                except:
                    pass
           
                result = True

            settingsFile.close()

        except Exception as e:
            print("Error loading settings.")
            print(e)
            pass

        return result
    
    def setMe(self, thePerson):
        me = self.me
        me.slug = thePerson.slug
        me.firstName = thePerson.firstName
        me.lastName = thePerson.lastName
        me.mobile = thePerson.mobile
        me.linkedInId = thePerson.linkedInId
        me.emailAddresses = thePerson.emailAddresses
        me.conversationId = thePerson.conversationId
        me.folderCreated = thePerson.folderCreated
        me.messages = []

    def getArguments(self):

        parser = ArgumentParser()

        parser.add_argument("-c", "--config", dest="configFolder", default=".",
                            help=self.STR_CONFIG_FOLDER)
        
        parser.add_argument("-s", "--sourcefolder", dest="sourceFolder", default=".",
                            help=self.STR_SOURCE_FOLDER)
        
        parser.add_argument("-f", "--file", dest="fileName",
                            help=self.STR_SOURCE_MESSAGE_FILE, metavar="FILE")
        
        parser.add_argument("-o", "--outputfolder", dest="outputFolder", default=".",
                            help=self.STR_OUTPUT_FOLDER)
        
        parser.add_argument("-l", "--language", dest="language", default="1",
                            help=self.STR_LANGUAGE_SETTING)
        
        parser.add_argument("-m", "--myslug", dest="mySlug", default="",
                            help=self.STR_MY_SLUG_SETTING)
        
        parser.add_argument("-d", "--debug",
                            action="store_true", dest="debug", default=False,
                            help=self.STR_DONT_PRINT_DEBUG_MSGS)
        
        parser.add_argument("-b", "--begin", dest="fromDate", default="",
                            help=self.STR_FROM_DATE)
        
        parser.add_argument("-i", "--imap", dest="imapServer", default="",
                            help=self.STR_IMAP_SERVER)
        
        parser.add_argument("-e", "--email", dest="emailAccount", default="",
                            help=self.STR_EMAIL_ACCOUNT)

        parser.add_argument("-p", "--password", dest="password", default="",
                            help=self.STR_PASSWORD)
        
        parser.add_argument("-r", "--folders", dest="password", default="",
                            help=self.STR_EMAIL_FOLDERS)
        
        parser.add_argument("-x", "--max", dest="maxMessages", default="",
                            help=self.STR_MAX_MESSAGES)
        
        args = parser.parse_args()

        return args

    def setup(self, service, reversed=False):

        loaded = False
        init = False

        if len(service):
            self.service = service

        if reversed:
            self.reversed = True

        # load the command-line arguments
        args = self.getArguments()

        if not args: 
            return init

        # need this since loadSettings needs to know where to 
        # find the config
        if args.configFolder:
            self.configFolder = args.configFolder

        self.loadSettings()

        if args.debug:
            self.debug = args.debug

        # then override them with any command line settings
        if args.sourceFolder:
            self.sourceFolder = args.sourceFolder

        if args.fileName:
            self.fileName = os.path.join(args.sourceFolder, args.fileName)
        
        if args.outputFolder:
            self.outputFolder = args.outputFolder
        
        if args.mySlug:
            self.me.slug = args.mySlug

        if args.fromDate:
            self.fromDate = args.fromDate

        if args.imapServer:
            self.imapServer = args.imapServer

        if args.emailAccount:
            self.emailAccount = args.emailAccount

        if args.password:
            self.password = args.password

        if args.maxMessages:
            self.maxMessages = int(args.maxMessages)

        if self.loadStrings():
            if self.loadMIMETypes():
                if self.loadPeople():
                    if self.loadGroups():
                        loaded = True

        self.peopleFolder = os.path.join(self.outputFolder, self.peopleSubFolder)
        self.groupsFolder = os.path.join(self.peopleFolder, self.groupsSubFolder)

        if self.debug == True:
            print(self)

        if loaded and self.me.slug:
            # email service doesn't require a messages file
            if self.service == markdown.YAML_SERVICE_EMAIL:
                if not self.emailAccount:
                    print('Need an email address. Use "-e <email_address>"')
                elif not self.password:
                    print('Need an email password. Use "-p <password>"')
                elif not self.imapServer:
                    print('Need an IMAP server. Use "-i <server>"')
                else:
                    init = True
            elif not self.fileName:
                print('No messages file specified')
            elif not os.path.exists(self.fileName):
                print('The messages file could not be found')
            else:
                init = True
        
        elif not self.me.slug:
            print('Your slug is not defined. Use \"-m slug\" to specify it.')
            print('Setup failed.')
        
        return init

    def setSourceFolder(folderName, self):
        self.sourceFolder = folderName
        
    # load strings, returns the number of strings loaded
    def loadStrings(self):

        try:
            stringsFileName = os.path.join(RESOURCES_FOLDER, STRINGS_FILE_NAME)
            stringsFile = open(stringsFileName, 'r')

            if stringsFile:
                for line in stringsFile:
                    line = line.rstrip()
                    try:
                        x = json.loads(line)
                        string = [x[self.LANGUAGE_FIELD], x[self.STRING_NUMBER], x[self.STRING_TEXT]]
                        self.strings.append(string)
                    except Exception as e:
                        pass
                stringsFile.close()
            else:
                print("failed to open " + stringsFileName)
        except Exception as e:
            print(e)
        
        return len(self.strings)
    
    # given a filename, return the MIME type or None if none found
    def getMIMEType(self, filename):

        MIMETypes = self.MIMETypes

        # get the suffix
        parts = filename.split('.')
        suffix = parts[parts.length - 1]
    
        # find the type
        for mimeType, ext in MIMETypes.items():
            if ext == suffix:
                return mimeType
            
        return None
        
    def loadMIMETypes(self):

        self.MIMETypes = False

        try:
            MIMETypesFileName = os.path.join(RESOURCES_FOLDER, MIME_TYPES_FILE_NAME)
            MIMETypesFile = open(MIMETypesFileName, 'r')
            self.MIMETypes = json.load(MIMETypesFile)
        except:
            print(self.getStr(self.STR_COULD_NOT_LOAD_MIME_TYPES))

        return self.MIMETypes
    
    # Lookup a person's first name from their mobile number
    def getFirstNameByNumber(self, number):
        
        global Strings

        firstName = ""
        thePerson = self.getPersonByNumber(number, self.people)
        
        if thePerson:
            try: 
                firstName = thePerson.firstName
            except Exception as e:   
                print(self.getStr(self.STR_PERSON_NOT_FOUND) + ": " + number)
                print(e)
                pass

        if not firstName:
            print(self.getStr(self.STR_PERSON_NOT_FOUND) + ": " + number)

        return firstName

    # Lookup a person's first-name from their slug
    def getFirstNameBySlug(self, slug):

        firstName = ""

        for thePerson in self.people:
            if thePerson.slug == slug:
                firstName = thePerson.firstName

        if not firstName:
            print(self.getStr(self.STR_PERSON_NOT_FOUND) + ": " + slug)
    
        return firstName
    
    def getGroupSlugByPhoneNumbers(self, phoneNumbers):
        slugs = []
        slug = ""
        found = False

        # first get the slugs for the phone numbers
        for phoneNumber in phoneNumbers:
            thePerson = self.getPersonByNumber(phoneNumber)
            if thePerson:
                slugs.append(thePerson.slug)
        
        # add myself to the slugs if not there already
        if self.me.slug not in slugs:
            slugs.append(self.me.slug)

        if len(slugs):
            for theGroup in self.groups:
                # use set() in case they're not in the same order
                if set(theGroup.members) == set(slugs):
                    slug = theGroup.slug
                    found = True
                    break

        if not found:
            print(self.getStr(self.STR_COULD_NOT_FIND_A_GROUP) + str(slugs))

        return slug
                    
    # Lookup the group slug based on it's unique ID
    def getGroupSlug(self, id):
        slug = ""

        for theGroup in self.groups:
            if theGroup.id == id:
                slug = theGroup.slug
        
        return slug

    # Lookup the group slug based on a conversation ID
    def getGroupSlugByConversationId(self, id):
        slug = ""

        for theGroup in self.groups:
            if theGroup.conversationId == id:
                slug = theGroup.slug
        
        return slug
    
    # Parse the email address(es) for the person
    def parseEmail(thePerson, data):
        count = 0

        return count

    # load the people, returns number of people loaded
    def loadPeople(self):

        try:
            peopleFileName = os.path.join(self.configFolder, PEOPLE_FILE_NAME)
            peopleFile = open(peopleFileName, 'r', encoding="utf-8")

            print(peopleFileName)
            if not os.path.exists(peopleFileName):
                return False

            try:
                jsonPeople = json.load(peopleFile)
            except Exception as e:
                print(e)
                return False    

            for jsonPerson in jsonPeople:
                try:
                    thePerson = person.Person()
                    thePerson.slug = jsonPerson[self.PERSON_FIELD_SLUG]
                    thePerson.firstName = jsonPerson[self.PERSON_FIELD_FIRST_NAME]
                    thePerson.lastName = jsonPerson[self.PERSON_FIELD_LAST_NAME]
                    
                    mobile = jsonPerson[self.PERSON_FIELD_MOBILE]
                    if mobile:
                        mobile = mobile.replace('+', '').replace('-', '')
                        thePerson.mobile = mobile
                    
                    thePerson.linkedInId = jsonPerson[self.PERSON_FIELD_LINKEDIN_ID]
                    try:
                        emailAddresses = jsonPerson[self.PERSON_FIELD_EMAIL]
                        thePerson.emailAddresses = emailAddresses.split(";")
                    except:
                        pass #not everyone needs one of these
                    try:
                        thePerson.conversationId = jsonPerson[self.PERSON_FIELD_CONVERSATION_ID]
                    except:
                        pass # not everyone will have one of these

                    # add this person to the collection of people
                    self.people.append(thePerson)

                    # see if it's me and save me!
                    if thePerson.slug == self.me.slug:
                        self.setMe(thePerson)

                except Exception as e:
                    print("Error loading person.")
                    print(e)
                    pass

        except Exception as e:
            print(e)
            return

        peopleFile.close()

        return len(self.people)

    # load the groups, returns number of groups loaded
    def loadGroups(self):

        try:
            groupsFileName = os.path.join(self.configFolder, GROUPS_FILE_NAME)
            groupsFile = open(groupsFileName, 'r', encoding="utf-8")
            jsonGroups = json.load(groupsFile)

            for jsonGroup in jsonGroups[self.GROUP_COLLECTION]:
                theGroup = group.Group()
                try:
                    theGroup.id = jsonGroup[self.GROUP_FIELD_ID]
                    theGroup.slug = jsonGroup[self.GROUP_FIELD_SLUG]
                    theGroup.description = jsonGroup[self.GROUP_FIELD_DESCRIPTION]
                    try:
                        theGroup.conversationId = jsonGroup[self.GROUP_FIELD_CONVERSATION_ID]
                    except:
                        pass
                    try:
                        for personSlug in jsonGroup[self.GROUP_FIELD_PEOPLE]:
                            theGroup.members.append(personSlug)
                        self.groups.append(theGroup)
                    except:
                        pass

                except:
                    pass

            groupsFile.close()
        
        except Exception as e:
            print(e)

        return len(self.groups)
    
    def getPersonByEmail(self, emailAddress):

        result = False

        for thePerson in self.people:
            if len(thePerson.emailAddresses):
                if emailAddress in thePerson.emailAddresses:
                    result = thePerson
                    break

        return result

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
    # Parameters:
    # 
    #   - number - the phone number
    #
    # -----------------------------------------------------------------------------
    def getPersonByNumber(self, number):

        for thePerson in self.people:
            if len(thePerson.mobile):
                try:
                    if thePerson.mobile[-10:] == number[-10:]:
                        return thePerson
                except:
                    return False
            
    # -----------------------------------------------------------------------------
    #
    # Lookup a person in people array from their LinkedIn ID.
    # 
    # -----------------------------------------------------------------------------
    def getPersonByLinkedInId(self, id):

        if not len(id):
            return False

        for thePerson in self.people:
            try:
                if thePerson.linkedInId == id:
                    return thePerson
            except Exception as e:
                print("Error looking up person by LinkedIn ID.")
                print(e)
                return False
            
        print(self.getStr(self.STR_PERSON_NOT_FOUND) + ": " + id)
  
    # -----------------------------------------------------------------------------
    #
    # Lookup a person in people array from their Conversation ID.
    #
    # Parameters:
    # 
    #   - id - conversation ID for the person
    #
    # Returns:
    #   - False if no person found
    #   - Person object if found 
    # -----------------------------------------------------------------------------
    def getPersonByConversationId(self, id):

        if len(id):

            for thePerson in self.people:
                try:
                    if thePerson.conversationId == id:
                        return thePerson
                except Exception as e:
                    print(e)
                    pass

        print(self.getStr(self.STR_PERSON_NOT_FOUND) + ": " + id)

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
    