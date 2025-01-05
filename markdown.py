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

# -----------------------------------------------------------------------------
#
# Create a folder for a specific person or group's messages.
#
# Parameters:
#
#    - thing - a Person or a Group
#    - the_config - all of the Config(uration)
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
def create_thing_folder(thing, the_config):
        
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

# create a folder
def create_folder(folder):
    
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

# -----------------------------------------------------------------------------
#
# Create a dated Markdown file with the messages between myself and the person.
#  
# Doesn't create/append to existing file as it's not smart enough to look 
# inside the file to see what is already there.
#
# Only create files for messages after `config.from_date` if there's a date set
#
# Parameters:
#
#   - entity - a Person or a Group object
#   - folder - folder where the markdown file is to be created
#   - config - config settings
# 
# -----------------------------------------------------------------------------
def create_markdown_file(entity, folder, the_config):

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

# -----------------------------------------------------------------------------
#
# Parameters:
#
#   - filename: the file to open
#   - the_config: all the settings, instance of Config
#
# Returns: a file handle
#
# -----------------------------------------------------------------------------
def open_output_file(filename, the_config):

    output_file = False

    try:
        output_file = open(filename, 'a', encoding="utf-8")

    except Exception as e:
        logging.error(f"{the_config.get_str(the_config.STR_ERROR)}. Exception '{e}'")

    return output_file

# -----------------------------------------------------------------------------
# 
# Create the metadata aka frontmatter for the Markdown file
#
# Parameters:
#
#    - the_message - the messages to be added
#    - the_config - the configuration, an instance of Config
#
# Notes:
#
#    `service` is what was used to send/receive message e.g. YAML_SERVICE_SMS
#
# -----------------------------------------------------------------------------
def get_frontmatter(the_message, the_config):

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

# -----------------------------------------------------------------------------
#
# Format a Message object in Markdown.
#
# Parameters:
#
#    - the_message - the message being converted to Markdown
#    - the_config - for settings
#    - people - array of Persons
#
# -----------------------------------------------------------------------------
def format_markdown(the_message, the_config, people):

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

# -----------------------------------------------------------------------------
#
# Create folders for the daily notes. 
#
# Parameters:
#
#    - the_config - all of the Config(uration)
#
# Notes:
#
#    - this is for notes-to-self that are stored in a separate folder from all
#      of the other messages
# 
# -----------------------------------------------------------------------------
def create_daily_notes_folders(the_config):

    daily_notes_folder = os.path.join(the_config.output_folder, the_config.daily_notes_subfolder)
    create_folder(daily_notes_folder)
    media_subfolder = os.path.join(daily_notes_folder, the_config.media_subfolder)
    create_folder(media_subfolder)

    return daily_notes_folder

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
#   - people_folder: root folder where the subfolder per-person / files created
#   - the_message: the current message being processed
#   - the_config - all of the Config(uration)
#
# -----------------------------------------------------------------------------
def get_media_folder_name(entity, people_folder, the_message, the_config):

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
#   - output_folder: root folder where the subfolder per-person / files created
#   - the_message: the current message being processed
#   - the_config: the configuration
#
# -----------------------------------------------------------------------------
def get_markdown_folder_name(entity, output_folder, the_message, the_config):

    folder = ""

    # if the daily notes folder is defined, put the notes-to-self in there
    if isinstance(entity, group.Group):
        folder = os.path.join(output_folder, entity.slug)
    elif the_message.is_note_to_self() and len(the_config.daily_notes_subfolder):
        folder = the_config.daily_notes_subfolder
    else:
        folder = os.path.join(output_folder, entity.slug)

    return folder
