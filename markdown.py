# Functions to generate the actual Markdown files include any 
# corresponding metadata a.k.a. frontmatter.

import os
import re
import time
import logging

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

errored_people = []

def create_thing_folder(thing, the_config):
    """
    Create a folder for a specific person or group's messages.

    Args:   
        thing: a Person or a Group object
        the_config (Config): an instance of Config containing configuration settings

    Returns:
        bool: True if the folder was created or already exists, False otherwise
    """

    import os        
    created = False
    folder = ""

    if isinstance(thing, person.Person):
        folder = os.path.join(the_config.output_folder, the_config.people_subfolder)
    elif isinstance(thing, group.Group):
        folder = the_config.groups_folder

    if len(folder) and len(thing.slug):
        thing_folder = os.path.join(folder, thing.slug)
        try:
            created = create_folder(thing_folder)
        except Exception as e:
            logging.error(f"create_thing_folder Exception '{e}'. Folder: '{thing_folder}'")

    return created

def create_folder(folder):
    """
    Create a folder if it does not exist.
    
    Args:
        folder(str): the path to the folder to create
    
    Returns:
        bool: True if the folder was created or already exists, False
            if there was an error creating it
    """
    
    result = False

    if not os.path.exists(folder):
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
            result = True
        except Exception as e:
            logging.error(f"create_folder Exception '{e}'. Folder: '{folder}'")
    else:
        # already existed so lie that it was created
        result = True

    return result

def create_markdown_file(entity, folder, the_config):
    """
    Create a Markdown file for the messages of a Person or Group.

    Args:  
        entity (Group or Person): A Person or Group object containing messages
        folder (str): The folder where the Markdown file will be created
        the_config (Config): An instance of Config containing configuration settings
        
    Returns: None

    Notes:
        - Only create files for messages after `config.from_date` if there's 
        a date set
        - Checks if the file already exists and only writes to it if it is not
        too old (less than WELL_AGED seconds) or if the message is a note-to-self.
        - Formats each message into Markdown, including metadata such as date, 
        time, subject, service, and tags.   
    """

    exists = False
    
    for dated_messages in entity.messages:

        for the_message in dated_messages.messages:

            if the_config.from_date and (the_message.date_str[:10] < the_config.from_date):
                continue

            # convert to Markdown and if no message, move on to the next one
            the_markdown = format_markdown(the_message, the_config, entity)
            if not len(the_markdown):
                continue

            # where the output files will go
            filename = the_message.date_str + OUTPUT_FILE_EXTENSION

            if the_message.is_note_to_self():
                daily_notes_folder = create_daily_notes_folders(the_config)
                filename = os.path.join(daily_notes_folder, filename)
            else: 
                create_thing_folder(entity, the_config)
                filename = os.path.join(folder, filename)
            
            exists = os.path.exists(filename)

            output_file = open_output_file(filename, the_config)
            
            if output_file:
                if exists == False:
                    frontmatter = get_frontmatter(the_message, the_config)
                    output_file.write(frontmatter)

                # don't add to the file if it's previously created
                # UNLESS it's a note-to-self
                age = time.time() - os.path.getctime(filename)
                
                if age < WELL_AGED or the_message.is_note_to_self():
                    try:
                        output_file.write(format_markdown(the_message, the_config, entity))
                        output_file.close()
                    except Exception as e:
                        pass

def open_output_file(filename, the_config):
    """
    Open a file for appending, creating it if it doesn't exist.

    Args:
        filename (str): The name of the file to open
        the_config (Config): An instance of Config containing configuration settings
    
    Returns:
        output_file: A file handle for the opened file, or False if it could not be opened
    """

    output_file = False

    try:
        output_file = open(filename, 'a', encoding="utf-8")

    except Exception as e:
        logging.error(f"{the_config.get_str(the_config.STR_ERROR)}. Exception '{e}'")

    return output_file

def get_frontmatter(the_message, the_config):
    """
    Generate the metadata aka frontmatter for a Markdown file based on the 
    message details.

    Args:
        the_message (Message): The message object containing details like date, time, subject, etc.
        the_config (Config): An instance of Config containing configuration settings
    
    Returns:
        str: the frontmatter string formatted in YAML
    
    Notes:
        - `service` is what was used to send/receive message e.g. YAML_SERVICE_SMS
        - Ensures the `to_slugs` list is unique and ordered.
        - The frontmatter is formatted with YAML dashes and includes the service type
        (e.g., email, chat).
    """

    # remove duplicate slugs and preserve the order
    the_message.to_slugs = list(dict.fromkeys(the_message.to_slugs))

    frontmatter = YAML_DASHES 

    # add the tags to the frontmatter
    frontmatter += YAML_TAGS + ": ["
    
    if the_config.service == YAML_SERVICE_EMAIL:
        frontmatter += TAG_EMAIL
    else:
        frontmatter += TAG_CHAT

    if the_message.group_slug:
        frontmatter += ", " + the_message.group_slug
    frontmatter += "]" + NEW_LINE

    # add the people to the frontmatter
    frontmatter += YAML_PEOPLE + ": ["
    
    if not len(the_message.group_slug):
        frontmatter += the_message.from_slug

        if len(the_message.to_slugs) and not the_message.is_note_to_self():
            frontmatter += ", " + ", ".join(the_message.to_slugs)
    
    elif len(the_message.group_slug):
        for group in the_config.groups:
            if group.slug == the_message.group_slug:
                first_time = True
                for person_slug in group.members:
                    if not first_time: 
                        frontmatter += ", "
                    frontmatter += person_slug
                    first_time = False
                break

    frontmatter += "]" + NEW_LINE

    if len(the_message.date_str)==0: 
        date_str = "null"
    else:
        date_str = the_message.date_str

    if len(the_message.time_str)==0: 
        time_str = "null"
    else: 
        time_str = the_message.time_str

    frontmatter += YAML_DATE + ": " + date_str[:10] + NEW_LINE
    frontmatter += YAML_TIME + ": " + time_str + NEW_LINE
    subject = the_message.subject

    if subject and isinstance(subject, str): 
        # replace double quotes with single quotes inside double-quoted strings
        # no, I didn't figure this out on my own, thanks to ChatGPT :) 
        subject = re.sub(r'"([^"]*)"', lambda match: "'" + match.group(1) + "'", subject)
        frontmatter += YAML_SUBJECT + ": \"" + subject + "\"" + NEW_LINE
    frontmatter += YAML_SERVICE + ": " + the_config.service + NEW_LINE
    frontmatter += YAML_DASHES + NEW_LINE

    return frontmatter

def format_markdown(the_message, the_config, people):
    """
    Format a Message object into Markdown text.
    
    Args:
        the_message (Message): the message to format
        the_config (Config): an instance of Config containing configuration settings
        people ([Person]): a list of Person objects to get first names from
        
    Returns:
        str: the formatted Markdown text for the message
    """

    global errored_people

    text = ""
    first_name = ""
    from_slug = the_message.from_slug

    if the_config.time_name_separate:
        text += NEW_LINE + the_message.time_str + NEW_LINE

    if len(from_slug):
        first_name = the_config.get_first_name_by_slug(from_slug)
    else: 
        # assume it's from me
        if the_config.me.slug not in the_message.to_slugs:
            first_name = the_config.me.first_name

    # I've seen cases with SMS Backup where `from_address="null"` and,
    # in turn, code can't get a source slug, so we skip the message
    if not first_name:
        if the_config.debug and from_slug not in errored_people:
            error_str = the_config.get_str(the_config.STR_NO_FIRST_NAME_FOR_SLUG)
            errored_people.append(from_slug)
            logging.error(f"{error_str} '{from_slug}'")
            print(the_message)
        return text

    # don't include first name if Note-to-Self since I know who I am!
    if not the_message.is_note_to_self(): 
        text += first_name

    if not the_config.time_name_separate and the_config.include_timestamp:
        if not the_message.is_note_to_self():
            text += " " + the_config.get_str(the_config.STR_AT) + " "
        text += the_message.time_str

    if the_config.colon_after_context: 
        text += ":"

    if not the_config.time_name_separate: 
        text += NEW_LINE

    for the_attachment in the_message.attachments:
        text += NEW_LINE
        link = the_attachment.generate_link(the_config)
        text += link

    text += NEW_LINE

    try:
        quoted_text = the_message.quote.text
        len_quoted_text = len(the_message.quote.text)

        if the_config.include_quote and hasattr(the_message.quote, 'text') and len_quoted_text:
        
            if len_quoted_text:
                text += MD_QUOTE + MD_QUOTE
                if the_message.quote.author_name:
                    text += the_message.quote.author_name + ": "
                if len_quoted_text > the_config.MAX_LEN_QUOTED_TEXT:
                    quoted_text = quoted_text[:the_config.MAX_LEN_QUOTED_TEXT]
                    last_space = quoted_text.rfind(' ')
                    text += quoted_text[:last_space] 
                    text += "..."
                else: 
                    text += quoted_text

                text += NEW_LINE + MD_QUOTE + NEW_LINE
    except:
        pass

    # quote all lines in the body
    if len(the_message.body):
        body_lines = the_message.body.split('\n')
        quoted_body = '\n'.join([MD_QUOTE + line for line in body_lines])
        text += quoted_body + NEW_LINE

    if the_config.include_reactions and len(the_message.reactions):
        text += MD_QUOTE + NEW_LINE + MD_QUOTE
        for the_reaction in the_message.reactions:
            first_name = the_config.get_first_name_by_slug(the_reaction.from_slug)
            text += str(the_reaction.emoji) + " *" + first_name.lower() + "*   "
        text += NEW_LINE

    # can have messages with only a body or reactions or attachments
    if len(the_message.body) or len(the_message.reactions):
        text += NEW_LINE
    elif not len(the_message.attachments): # if none of them then it's invalid
        text = ""

    return text

def create_daily_notes_folders(the_config):
    """
    Create the daily notes folder structure if it doesn't exist.
    
    Args:
        - the_config (Config): an instance of Config containing configuration settings
    
    Returns:
        daily_notes_folder (str): the path to the daily notes folder

    Notes:
        - this is for notes-to-self that are stored in a separate folder from all
      of the other messages
    """

    daily_notes_folder = os.path.join(the_config.output_folder, the_config.daily_notes_subfolder)
    create_folder(daily_notes_folder)
    media_subfolder = os.path.join(daily_notes_folder, the_config.media_subfolder)
    create_folder(media_subfolder)

    return daily_notes_folder

def get_media_folder_name(entity, people_folder, the_message, the_config):
    """
    Generate the output folder name for media files (attachments).

    Args:
        - entity: a Person or a Group object
        - people_folder (str): root folder where the subfolder per-person created
        - the_message (Message): the current message being processed
        - the_config (Config): the configuration instance
    
    Returns:
        folder: the folder path where the media files will be stored

    Notes
        - if it's a regular message, folder will be destination person slug
        - if it's an attachment, the folder will be the source (sender)
    """

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if type(entity) == group.Group:
        folder = os.path.join(people_folder, entity.slug)

    elif the_message.is_note_to_self() and len(the_config.daily_notes_subfolder):
        folder = os.path.join(the_config.output_folder, the_config.daily_notes_subfolder)

    elif the_message.has_attachment() and the_message.from_slug == the_config.me.slug:
        folder = os.path.join(people_folder, the_config.me.slug)
    
    else:
        folder = os.path.join(people_folder, entity.slug)

    return folder

def get_markdown_folder_name(entity, output_folder, the_message, the_config):
    """
    Generate the output folder name for the Markdown files.
    
    Args:
        entity: a Person or a Group object
        output_folder (str): root folder where the subfolder per-person / 
            files are created
        the_message (Message): the current message being processed
        the_config (Config): the configuration instance
    
    Returns:
        str: the folder path where the Markdown files will be stored
    """

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if isinstance(entity, group.Group):
        folder = os.path.join(output_folder, entity.slug)
    elif the_message.is_note_to_self() and len(the_config.daily_notes_subfolder):
        folder = the_config.daily_notes_subfolder
    else:
        folder = os.path.join(output_folder, entity.slug)

    return folder
