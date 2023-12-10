import json
import os

import person
import group
from datetime import datetime

import pathlib
from pathlib import Path

# config
CONFIG_FOLDER = "config"
STRINGS_FILE_NAME = "strings.json"
PEOPLE_FILE_NAME  = "people.json"
GROUPS_FILE_NAME  = "groups.json"
MIME_TYPES_FILE_NAME = "MIMETypes.json"

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
        self.STR_FROM_DATE = 25
        self.STR_CONFIG_FOLDER = 26

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
    
        # set the default config folder to the folder where this
        # script was run plus 
        folder = os.path.dirname(os.path.realpath(__file__))
        self.configFolder = os.path.join(folder, CONFIG_FOLDER)

        self.settingsFileName = "settings.json"
        self.service = ""
        self.reversed = False
        self.fileName = fileName
        self.language = self.ENGLISH
        self.mySlug = "NOMYSLUG"
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

    def loadSettings(self):

        result = False

        try:
            settingsFileName = os.path.join(self.configFolder, self.settingsFileName)
            settingsFile = open(settingsFileName, 'r')
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

    def setSourceFolder(folderName, self):
        self.sourceFolder = folderName
        
    # load strings, returns the number of strings loaded
    def loadStrings(self):

        try:
            stringsFileName = os.path.join(self.configFolder, STRINGS_FILE_NAME)
            stringsFile = open(stringsFileName, 'r')

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
            MIMETypesFileName = os.path.join(self.configFolder, MIME_TYPES_FILE_NAME)
            MIMETypesFile = open(MIMETypesFileName, 'r')
            self.MIMETypes = json.load(MIMETypesFile)
        except:
            print(self.getStr(self.STR_COULD_NOT_LOAD_MIME_TYPES))

        return self.MIMETypes
    
    # Lookup a person's first name from their phone number
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

    # Lookup a person from their phone number
    def getFirstNameBySlug(self, slug):

        firstName = ""

        for thePerson in self.people:
            if thePerson.slug == slug:
                firstName = thePerson.firstName

        if not firstName:
            print(self.getStr(self.STR_COULD_NOT_FIND_PERSON) + ": " + slug)
    
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
        if self.mySlug not in slugs:
            slugs.append(self.mySlug)

        if len(slugs):
            for theGroup in self.groups:
                # use set() in case they're not in the same order
                if set(theGroup.members) == set(slugs):
                    slug = theGroup.slug
                    found = True
                    break

        if not found:
            print( self.getStr(self.STR_COULD_NOT_FIND_A_GROUP) + str(slugs))

        return slug
                    
    # Lookup the group slug based on it's unique ID
    def getGroupSlug(self, id):
        slug = ""

        for theGroup in self.groups:
            if theGroup.id == id:
                slug = theGroup.slug
        
        return slug


    # load the people, returns number of people loaded
    def loadPeople(self):

        try:
            peopleFileName = os.path.join(self.configFolder, PEOPLE_FILE_NAME)
            peopleFile = open(peopleFileName, 'r', encoding="utf-8")
            jsonPeople = json.load(peopleFile)

            for jsonPerson in jsonPeople:
                try:
                    thePerson = person.Person()
                    thePerson.slug = jsonPerson[self.PERSON_FIELD_SLUG]
                    thePerson.firstName = jsonPerson[self.PERSON_FIELD_FIRST_NAME]
                    thePerson.lastName = jsonPerson[self.PERSON_FIELD_LAST_NAME]
                    thePerson.phoneNumber = jsonPerson[self.PERSON_FIELD_NUMBER]
                    thePerson.linkedInId = jsonPerson[self.PERSON_FIELD_LINKEDIN_ID]
                    self.people.append(thePerson)
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
    
    # get the Person object representing me
    def getMe(self):
        
        thePerson = person.Person()

        for thePerson in self.people:
            if thePerson.slug == self.mySlug:
                break
        
        return thePerson

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

        for thePerson in self.people:
            try:
                if thePerson.phoneNumber[-10:] == number[-10:]:
                    return thePerson
            except:
                return False
            
    # -----------------------------------------------------------------------------
    #
    # Lookup a person in people array from their LinkedIn ID.
    # 
    # -----------------------------------------------------------------------------
    def getPersonByLinkedInId(self, id):

        for thePerson in self.people:
            try:
                if thePerson.linkedInId == id:
                    return thePerson
            except Exception as e:
                print("Error looking up person by LinkedIn ID.")
                print(e)
                return False
            
        print(self.getStr(self.STR_PERSON_NOT_FOUND) + ": " + id)

            
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
    