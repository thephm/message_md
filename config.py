import json
import os
    
import markdown
import logging

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
MIME_TYPES_FILE_NAME = "mime_types.json"
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
        self.SETTING_CREATE_PEOPLE = "create-people"

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
        self.STR_NO_FIRST_NAME = 32
        self.STR_NO_CONVERSATION_ID = 33
        self.STR_FULL_NAME_NOT_FOUND = 34
        self.STR_CREATE_PEOPLE = 35
        self.STR_NO_FIRST_NAME_FOR_SLUG = 36
        self.STR_FAILED_TO_PARSE_ATTACHMENT = 37
        self.STR_FAILED_TO_PARSE_ATTACHMENT_HEIGHT = 38
        self.STR_FAILED_TO_PARSE_ATTACHMENT_WIDTH = 39
        self.STR_FAILED_TO_PARSE_ATTACHMENT_SIZE = 40
        self.STR_COULD_NOT_PROCESS_MMS_PART = 41
        self.STR_NO_PERSON_WITH_PHONE_NUMBER = 42
        self.STR_COULD_NOT_FIND_MESSAGES_FILE = 43
        self.STR_NO_PERSON_WITH_EMAIL = 44
        self.STR_COULD_NOT_CREATE_MEDIA_FOLDER = 45
        self.STR_DATE_STRING_DOES_NOT_MATCH_FORMAT = 46
        self.STR_THESE_EMAIL_ADDRESSES_NOT_FOUND = 47
        self.STR_OR_WITH_FULL_NAME = 48

        self.MAX_LEN_QUOTED_TEXT = 70

        # fields in people file (PEOPLE_FILE_NAME)
        self.PERSON_FIELD_SLUG = "slug"
        self.PERSON_FIELD_FIRST_NAME = "first-name"
        self.PERSON_FIELD_LAST_NAME = "last-name"
        self.PERSON_FIELD_IGNORE = "ignore"
        self.PERSON_FIELD_FULL_NAME = "profile-full-name"
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
        self.mime_types = []

        self.debug = False

        self.me = person.Person()
    
        # set the default config folder to the folder where this
        # script was run plus 
        folder = os.path.dirname(os.path.realpath(__file__))
        self.config_folder = os.path.join(folder, CONFIG_FOLDER)

        self.settings_filename = "settings.json"
        self.service = ""
        self.filename = fileName
        self.language = self.ENGLISH
        self.media_subfolder = "media"
        self.image_embed = True
        self.image_width = 450
        self.source_folder = "../../messages"
        self.output_folder = "../../output"
        self.attachments_subfolder = "attachments"
        self.archive_subfolder = "archive"
        self.people_subfolder = "People"
        self.groups_subfolder = "groups"
        self.daily_notes_subfolder = "Daily Notes"
        self.include_timestamp = True
        self.include_quote = True
        self.colon_after_context = False
        self.include_reactions = False
        self.time_name_separate = False
        self.folder_per_erson = True
        self.file_per_person = True
        self.file_per_day = True
        self.from_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.imap_server = ""
        self.email_account = ""
        self.email_folders = ""
        self.not_email_folders = ""
        self.password = ""
        self.max_messages = 10000
        self.phone_not_found = [] # array of phone numbers not found
        self.slugs_not_found = [] # array of slugs not found
        self.ids_not_found = [] # array of conversation IDs not found
        self.names_not_found = [] # Signal full name
        self.create_people = False

    # -------------------------------------------------------------------------
    #
    # Return a string represention of the configuration.
    #
    # -------------------------------------------------------------------------
    def __str__(self):
        
        output = self.SETTING_MY_SLUG + ": " + str(self.me.slug) + "\n"
        output += "config_folder: " + str(self.config_folder) + "\n"
        output += self.SETTING_ATTACHMENTS_SUBFOLDER + ": " + str(self.attachments_subfolder) + "\n"
        output += self.SETTING_ARCHIVE_SUBFOLDER + ": " + str(self.archive_subfolder) + "\n"
        output += self.SETTING_OUTPUT_FOLDER + ": " + str(self.output_folder) + "\n"
        output += self.SETTING_MEDIA_SUBFOLDER + ": " + str(self.media_subfolder) + "\n"
        output += self.SETTING_IMAGE_EMBED + ": " + str(self.image_embed) + "\n"
        output += self.SETTING_IMAGE_WIDTH + ": " + str(self.image_width) + "\n"
        output += self.SETTING_FOLDER_PER_PERSON + ": " + str(self.folder_per_person) + "\n"
        output += self.SETTING_FILE_PER_PERSON + ": " + str(self.file_per_person) + "\n"
        output += self.SETTING_FILE_PER_DAY + ": " + str(self.file_per_day) + "\n"
        output += self.SETTING_INCLUDE_TIMESTAMP + ": " + str(self.include_timestamp) + "\n"
        output += self.SETTING_INCLUDE_REACTIONS + ": " + str(self.include_reactions) + "\n"
        output += self.SETTING_INCLUDE_QUOTE + ": " + str(self.include_quote) + "\n"
        output += self.SETTING_COLON_AFTER_CONTEXT + ": " + str(self.colon_after_context) + "\n"
        output += self.SETTING_TIME_NAME_SEPARATE + ": " + str(self.time_name_separate) + "\n"
        output += self.SETTING_DAILY_NOTES_SUBFOLDER + ": " + str(self.daily_notes_subfolder) + "\n"
        output += self.SETTING_IMAP_SERVER + ": " + str(self.imap_server) + "\n"
        output += self.SETTING_EMAIL_ACCOUNT + ": " + str(self.email_account) + "\n"
        output += self.SETTING_EMAIL_FOLDERS + ": " + str(self.email_folders) + "\n"
        output += self.SETTING_NOT_EMAIL_FOLDERS + ": " + str(self.not_email_folders) + "\n"
        output += self.SETTING_MAX_MESSAGES + ": " + str(self.max_messages) + "\n"
        output += self.SETTING_CREATE_PEOPLE + ": " + str(self.create_people) + "\n"
        
        return output

    # -------------------------------------------------------------------------
    #
    # Load the settings from `self.settings_filename` file.
    #
    # -------------------------------------------------------------------------
    def load_settings(self):

        result = False
        settings_file = False

        try:
            settings_filename = os.path.join(self.config_folder, self.settings_filename)
            logging.info("settings_filename='{settings_filename}'")

            try:
                settings_file = open(settings_filename, 'r')
            except Exception as e:
                logging(f"open(settings_filename) Error: {e}")

            if settings_file:

                self.settings = json.load(settings_file)
                self.archive_subfolder = os.path.join(self.source_folder, self.settings[self.SETTING_ARCHIVE_SUBFOLDER])
                messages_filename = self.settings[self.SETTING_MESSAGES_FILE]
                
                if messages_filename:
                    self.filename = os.path.join(self.source_folder, messages_filename)

                    try:
                        self.attachments_subfolder = self.settings[self.SETTING_ATTACHMENTS_SUBFOLDER]
                        self.output_folder = self.settings[self.SETTING_OUTPUT_FOLDER]
                        self.groups_subfolder = self.settings[self.SETTING_GROUPS_SUBFOLDER]
                        self.media_subfolder = self.settings[self.SETTING_MEDIA_SUBFOLDER]
                        self.daily_notes_subfolder = self.settings[self.SETTING_DAILY_NOTES_SUBFOLDER]
                        self.image_embed = self.settings[self.SETTING_IMAGE_EMBED]
                        self.image_width = self.settings[self.SETTING_IMAGE_WIDTH]
                        self.include_timestamp = bool(self.settings[self.SETTING_INCLUDE_TIMESTAMP])
                        self.include_quote = bool(self.settings[self.SETTING_INCLUDE_QUOTE])
                        self.colon_after_context = bool(self.settings[self.SETTING_COLON_AFTER_CONTEXT])
                        self.time_name_separate = bool(self.settings[self.SETTING_TIME_NAME_SEPARATE])
                        self.include_reactions = bool(self.settings[self.SETTING_INCLUDE_REACTIONS])
                        self.folder_per_person = bool(self.settings[self.SETTING_FOLDER_PER_PERSON])
                        self.file_per_person = bool(self.settings[self.SETTING_FILE_PER_PERSON])
                        self.file_per_day = bool(self.settings[self.SETTING_FILE_PER_DAY])
                        self.create_people = bool(self.settings[self.SETTING_CREATE_PEOPLE])
                    except:
                        pass

                # this can be passed on the command line
                try:
                    self.me.slug = self.settings[self.SETTING_MY_SLUG]
                except:
                    pass

                # these can be passed on the command line
                try:
                    self.imap_server = self.settings[self.SETTING_IMAP_SERVER]
                    self.max_messages = self.settings[self.SETTING_MAX_MESSAGES]
                    self.email_account = self.settings[self.SETTING_EMAIL_ACCOUNT]
                    self.email_folders = self.settings[self.SETTING_EMAIL_FOLDERS].split(';')
                    if self.email_folders == ['']:
                        self.email_folders = []
                    self.not_email_folders = self.settings[self.SETTING_NOT_EMAIL_FOLDERS].split(';')
                    if self.not_email_folders == ['']:
                        self.not_email_folders = []
                except:
                    pass
           
                result = True

                settings_file.close()

        except Exception as e:
            logging(f"Error loading settings: {e}")
            pass

        return result
    
    def set_me(self, the_person):
        me = self.me
        me.slug = the_person.slug
        me.first_name = the_person.first_name
        me.last_name = the_person.last_name
        me.mobile = the_person.mobile
        me.linkedin_id = the_person.linkedin_id
        me.email_addresses = the_person.email_addresses
        me.conversation_id = the_person.conversation_id
        me.folder_created = the_person.folder_created
        me.messages = []

    # -------------------------------------------------------------------------
    #
    # Parse the command line arguments.  
    #
    # -------------------------------------------------------------------------
    def get_arguments(self):

        parser = ArgumentParser()

        parser.add_argument("-c", "--config", dest="config_folder", default=".",
                            help=self.STR_CONFIG_FOLDER)
        
        parser.add_argument("-s", "--source_folder", dest="source_folder", default=".",
                            help=self.STR_SOURCE_FOLDER)
        
        parser.add_argument("-f", "--file", dest="filename",
                            help=self.STR_SOURCE_MESSAGE_FILE, metavar="FILE")
        
        parser.add_argument("-o", "--output_folder", dest="output_folder", default=".",
                            help=self.STR_OUTPUT_FOLDER)
        
        parser.add_argument("-l", "--language", dest="language", default="1",
                            help=self.STR_LANGUAGE_SETTING)
        
        parser.add_argument("-m", "--my_slug", dest="my_slug", default="",
                            help=self.STR_MY_SLUG_SETTING)
        
        parser.add_argument("-d", "--debug",
                            action="store_true", dest="debug", default=False,
                            help=self.STR_DONT_PRINT_DEBUG_MSGS)
        
        parser.add_argument("-b", "--begin", dest="from_date", default="",
                            help=self.STR_FROM_DATE)
        
        parser.add_argument("-i", "--imap", dest="imap_server", default="",
                            help=self.STR_IMAP_SERVER)
        
        parser.add_argument("-e", "--email", dest="email_account", default="",
                            help=self.STR_EMAIL_ACCOUNT)

        parser.add_argument("-p", "--password", dest="password", default="",
                            help=self.STR_PASSWORD)
        
        parser.add_argument("-r", "--folders", dest="password", default="",
                            help=self.STR_EMAIL_FOLDERS)
        
        parser.add_argument("-x", "--max", dest="max_messages", default="",
                            help=self.STR_MAX_MESSAGES)
        
        parser.add_argument("-a", "--add", action="store_true", dest="create_people", default="",
                            help=self.STR_CREATE_PEOPLE)
        
        args = parser.parse_args()

        return args

    # -------------------------------------------------------------------------
    #
    # Load the configuration settings and override where command-line options
    # were provided.
    #
    # -------------------------------------------------------------------------
    def setup(self, service):

        loaded = False
        init = False

        if len(service):
            self.service = service

        # load the command-line arguments
        args = self.get_arguments()

        if not args: 
            return init

        # need this since `load_settings` needs to know where to 
        # find the config
        if args.config_folder:
            self.config_folder = args.config_folder

        self.load_settings()

        if args.debug:
            self.debug = args.debug

        # then override them with any command line settings
        if args.source_folder:
            self.source_folder = args.source_folder

        if args.filename:
            self.filename = os.path.join(args.source_folder, args.filename)
        
        if args.output_folder:
            self.output_folder = args.output_folder
        
        if args.my_slug:
            self.me.slug = args.my_slug

        if args.from_date:
            self.from_date = args.from_date

        if args.imap_server:
            self.imap_server = args.imap_server

        if args.email_account:
            self.email_account = args.email_account

        if args.password:
            self.password = args.password

        if args.max_messages:
            self.max_messages = int(args.max_messages)

        if args.create_people:
            self.create_people = args.create_people

        if self.load_strings():
            if self.load_mime_types():
                if self.load_people():
                    if self.load_groups():
                        loaded = True

        self.people_folder = os.path.join(self.output_folder, self.people_subfolder)
        self.groups_folder = os.path.join(self.people_folder, self.groups_subfolder)

        if self.debug == True:
            print(self)

        if loaded and self.me.slug:
            # email service doesn't require a messages file
            if self.service == markdown.YAML_SERVICE_EMAIL:
                if not self.email_account:
                    print('Need an email address. Use "-e <email_address>"')
                elif not self.password:
                    print('Need an email password. Use "-p <password>"')
                elif not self.imap_server:
                    print('Need an IMAP server. Use "-i <server>"')
                else:
                    init = True
            elif not self.filename:
                print('No messages file specified')
            elif not os.path.exists(self.filename):
                print('The messages file "' + self.filename + '" could not be found')
            else:
                init = True
        
        elif not self.me.slug:
            print('Your slug is not defined. Use \"-m slug\" to specify it.')
            print('Setup failed.')
        
        return init

#    def setsource_folder(folder_name, self):
#        self.source_folder = folder_name
        
    # -------------------------------------------------------------------------
    #
    # Load strings used in the script and return the number of strings loaded.
    #
    # -------------------------------------------------------------------------
    def load_strings(self):

        try:
            strings_filename = os.path.join(RESOURCES_FOLDER, STRINGS_FILE_NAME)
            strings_file = open(strings_filename, 'r')

            if strings_file:
                for line in strings_file:
                    line = line.rstrip()
                    try:
                        x = json.loads(line)
                        string = [x[self.LANGUAGE_FIELD], x[self.STRING_NUMBER], x[self.STRING_TEXT]]
                        self.strings.append(string)
                    except Exception as e:
                        pass
                strings_file.close()
            else:
                print('failed to open ' + strings_filename)
        except Exception as e:
            print(e)
        
        return len(self.strings)
    
    # -------------------------------------------------------------------------
    #
    # Given a filename, return the MIME type or None if none found
    #
    # Parameters:
    #
    #   - filename - the name of the file to check
    #
    # -------------------------------------------------------------------------
    def get_mime_type(self, filename):
        try:
            # ensure the MIME types are loaded
            if not self.mime_types:
                raise ValueError("MIME types are not loaded.")
            
            # extract the file extension (case-insensitive)
            suffix = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            
            # directly find the MIME type in the reverse mapping
            for mime_type, ext in self.mime_types.items():
                if ext.lower() == suffix:
                    return mime_type

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error determining MIME type: {e}")

        # default to None if no match is found
        return None
        
    # -------------------------------------------------------------------------
    #
    # Load the mapping of file extensions to MIME type, e.g. `jpg` is JPEG
    #
    # -------------------------------------------------------------------------
    def load_mime_types(self):

        self.mime_types = None
        
        try:
            # build the path to the MIME types file
            mime_types_filename = os.path.join(RESOURCES_FOLDER, MIME_TYPES_FILE_NAME)
            
            # use a context manager to handle the file
            with open(mime_types_filename, 'r') as mime_types_file:
                self.mime_types = json.load(mime_types_file)
        
        except FileNotFoundError:
            print(f"Error: MIME types file not found at {mime_types_filename}")
        
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse MIME types file: {e}")

        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")

        if self.mime_types is None:
            print(self.get_str(self.STR_COULD_NOT_LOAD_MIME_TYPES))
        
        return self.mime_types
    
    # -------------------------------------------------------------------------
    #
    # Lookup a person's first name from their mobile number.
    #
    # ------------------------------------------------------------------------- 
    def get_first_name_by_number(self, number):
        
        global Strings

        first_name = ""
        the_person = self.get_person_by_number(number, self.people)
        
        if the_person:
            try: 
                first_name = the_person.first_name
            except Exception as e:   
                print(self.get_str(self.STR_NO_FIRST_NAME) + ": " + number)
                print(e)
                pass

        if not first_name and self.debug and len(number) not in self.phone_not_found:
            print(self.get_str(self.STR_PERSON_NOT_FOUND) + ": " + number)
            self.phone_not_found.append(number)

        return first_name

    # -------------------------------------------------------------------------
    #
    # Lookup a person's first-name from their slug
    #
    # -------------------------------------------------------------------------
    def get_first_name_by_slug(self, slug):

        first_name = ""

        for the_person in self.people:
            if the_person.slug == slug:
                first_name = the_person.first_name

        if not first_name and self.debug and slug not in self.slugs_not_found:
            print(self.get_str(self.STR_PERSON_NOT_FOUND) + " " + slug)
            self.slugs_not_found.append(slug)

        return first_name
    
    # -------------------------------------------------------------------------
    #
    # Get the slug for a group of people based on a collection of phone numbers
    #
    # -------------------------------------------------------------------------
    def get_group_slug_by_phone_numbers(self, phone_numbers):
        slugs = []
        slug = ""
        found = False

        # first get the slugs for the phone numbers
        for phone_number in phone_numbers:
            the_person = self.get_person_by_number(phone_number)
            if the_person:
                slugs.append(the_person.slug)
        
        # add myself to the slugs if not there already
        if self.me.slug not in slugs:
            slugs.append(self.me.slug)

        if len(slugs):
            for the_group in self.groups:
                # use set() in case they're not in the same order
                if set(the_group.members) == set(slugs):
                    slug = the_group.slug
                    found = True
                    break

        if not found:
            print(self.get_str(self.STR_COULD_NOT_FIND_A_GROUP) + str(slugs))

        return slug
                    
    # -------------------------------------------------------------------------
    #
    # Lookup the group slug based on it's unique ID.
    #
    # -------------------------------------------------------------------------
    def get_group_slug(self, id):
        slug = ""

        for the_group in self.groups:
            if the_group.id == id:
                slug = the_group.slug
        
        return slug

    # -------------------------------------------------------------------------
    #
    # Lookup the group slug based on a conversation ID.
    #
    # -------------------------------------------------------------------------
    def get_group_slug_by_conversation_id(self, id):    
        slug = ""

        for the_group in self.groups:
            if the_group.conversation_id == id:
                slug = the_group.slug
        
        return slug
    
    # -------------------------------------------------------------------------
    #
    # Parse the email address(es) for the person. Placeholder for now
    #
    # -------------------------------------------------------------------------
    def parse_email(the_person, data):
        count = 0

        return count

    # -------------------------------------------------------------------------
    #
    # Load the people and return the number of people loaded from the 
    # `people.json` config file.
    #
    # -------------------------------------------------------------------------
    def load_people(self):

        try:
            people_filename = os.path.join(self.config_folder, PEOPLE_FILE_NAME)
            people_file = open(people_filename, 'r', encoding="utf-8")

            print(people_filename)
            if not os.path.exists(people_filename):
                return False

            try:
                json_people = json.load(people_file)
            except Exception as e:
                print(e)
                return False    

            for json_person in json_people:
                try:
                    the_person = person.Person()

                    # the person must have a slug
                    the_person.slug = json_person[self.PERSON_FIELD_SLUG]
                    
                    # the person can optionally have these fields
                    try:
                        the_person.first_name = json_person[self.PERSON_FIELD_FIRST_NAME]
                    except:
                        pass
                    
                    try:
                        the_person.last_name = json_person[self.PERSON_FIELD_LAST_NAME]
                    except:
                        pass

                    try:                            
                        the_person.full_name = json_person[self.PERSON_FIELD_FULL_NAME]
                    except:
                        pass

                    if not the_person.full_name:
                        if the_person.first_name and the_person.last_name:
                            the_person.full_name = the_person.first_name + " " + the_person.last_name
                        elif the_person.first_name:
                            the_person.full_name = the_person.first_name
                        elif the_person.last_name:
                            the_person.full_name = the_person.last_name

                    try:
                        the_person.linkedin_id = json_person[self.PERSON_FIELD_LINKEDIN_ID]
                    except:
                        pass

                    mobile = json_person[self.PERSON_FIELD_MOBILE]
                    if mobile:
                        mobile = mobile.replace('+', '').replace('-', '')
                        the_person.mobile = mobile
                    
                    try:
                        email_addresses = json_person[self.PERSON_FIELD_EMAIL].lower()
                        the_person.email_addresses = email_addresses.split(";")
                    except:
                        pass #not everyone needs one of thesex

                    try:
                        the_person.conversation_id = json_person[self.PERSON_FIELD_CONVERSATION_ID]
                    except:
                        pass # not everyone will have one of these

                    # add this person to the collection of people
                    self.people.append(the_person)

                    # see if it's me and save me!
                    # @todo: don't think me should be a separate object in config, just the slug
                    if the_person.slug == self.me.slug:
                        self.set_me(the_person)

                except Exception as e:
                    print('Error loading person: ' + the_person.slug)
                    print(e)
                    pass

        except Exception as e:
            print(e)
            return

        people_file.close()

        return len(self.people)

    # -------------------------------------------------------------------------
    #
    # Load the groups and return the number of groups loaded.
    #
    # -------------------------------------------------------------------------
    def load_groups(self):

        try:
            groups_filename = os.path.join(self.config_folder, GROUPS_FILE_NAME)
            groups_file = open(groups_filename, 'r', encoding="utf-8")
            json_groups = json.load(groups_file)

            for json_group in json_groups[self.GROUP_COLLECTION]:
                the_group = group.Group()
                try:
                    the_group.id = json_group[self.GROUP_FIELD_ID]
                    the_group.slug = json_group[self.GROUP_FIELD_SLUG]
                    the_group.description = json_group[self.GROUP_FIELD_DESCRIPTION]
                    try:
                        the_group.conversation_id = json_group[self.GROUP_FIELD_CONVERSATION_ID]
                    except:
                        pass
                    try:
                        the_group.members = [person_slug for person_slug in json_group[self.GROUP_FIELD_PEOPLE]]
                        self.groups.append(the_group)
                    except:
                        pass

                except:
                    pass

            groups_file.close()
        
        except Exception as e:
            print(e)

        return len(self.groups)
    
    # -------------------------------------------------------------------------
    #
    # Retrieve a Person based on their email address.
    #
    # -------------------------------------------------------------------------
    def get_person_by_email(self, email_address):

        result = False

        for the_person in self.people:
            if len(the_person.email_addresses):
                if email_address in the_person.email_addresses:
                    result = the_person
                    break

        return result

    # -------------------------------------------------------------------------
    #
    # Lookup a person in people array from their phone number. Matches the last 
    # 10 digits which is not perfect but good enough for me! 
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
    # -------------------------------------------------------------------------
    def get_person_by_number(self, number):

        for the_person in self.people:
            if len(the_person.mobile):
                try:
                    if the_person.mobile[-10:] == number[-10:]:
                        return the_person
                except:
                    return False
            
    # -------------------------------------------------------------------------
    #
    # Lookup a person using their full name. Returns the Person object.  
    #
    # Parameters:
    # 
    #   - name - the full name of the person
    #
    # Notes:
    #
    #   - Added this for Signal contacts that use "Private" mode which 
    #     hides their phone number. In that case, we can refer to their 
    #     `profileFullName' field
    #
    # -------------------------------------------------------------------------
    def get_person_by_full_name(self, name):

        if name:
            for the_person in self.people:
                if the_person.full_name == name:
                    return the_person

        if name not in self.names_not_found:
            # only tell the user that the person was found if `create_people`
            # setting is False because the person will be created if it's True
            if not self.create_people:
                print(self.get_str(self.STR_FULL_NAME_NOT_FOUND) + ": " + name)
            self.names_not_found.append(name)

        return False
                
    # -------------------------------------------------------------------------
    #
    # Lookup a person in people array from their LinkedIn ID.
    # 
    # Parameters:
    # 
    #   - id - the LinkedIn ID
    #
    # -------------------------------------------------------------------------
    def get_person_by_linkedin_id(self, id):

        if not len(id):
            return False

        for the_person in self.people:
            try:
                if the_person.linkedin_id == id:
                    return the_person
            except Exception as e:
                print("Error looking up person by LinkedIn ID.")
                print(e)
                return False
            
    # -------------------------------------------------------------------------
    #
    # Lookup a person in people array from their Conversation ID.
    #
    # Parameters:
    # 
    #   - id - conversation ID for the person
    #
    # Returns:
    #
    #   - False if no person found
    #   - Person object if found 
    # 
    # Notes:
    # 
    #   - @todo: if this is specific to Signal, should not be here
    #
    # -------------------------------------------------------------------------
    def get_person_by_conversation_id(self, id):

        if len(id):
            for the_person in self.people:
                try:
                    if the_person.conversation_id == id:
                        return the_person
                except Exception as e:
                    print(e)
                    pass
        
        if (id == "c2f6b486-7f31-4f52-8fa8-01e1056cdb72"):
            pass

        # if here, then the `conversation_id` was not associated to anyone
        if id not in self.ids_not_found:
            if self.debug:
                print(self.get_str(self.STR_NO_CONVERSATION_ID) + ": " + id)
            # remember it so we don't display an error every time
            self.ids_not_found.append(id)

        return False
             
    # -------------------------------------------------------------------------
    #
    # Get a string out of strings based on its ID.
    # 
    # Parameters:
    # 
    #   - id - the string ID
    #
    # -------------------------------------------------------------------------
    def get_str(self, string_number):

        result = ""

        for string in self.strings:
            try:
                if (int(string[self.STRINGS_NUMBER_INDEX]) == int(string_number) and
                    int(string[self.STRINGS_LANGUAGE_INDEX]) == self.language):
                    result = string[self.STRINGS_TEXT_INDEX]
            except:
                pass

        return result
    