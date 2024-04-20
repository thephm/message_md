import os
import shutil

import pathlib
from pathlib import Path

from datetime import datetime
import config
import markdown
import attachment
import message

def setup(the_config, service, reversed=False):

    result = the_config.setup(service, reversed)
    
    return result

# -----------------------------------------------------------------------------
#
# Creates an archive subfolder and then either copies or moves - depending on 
# configuration - the message file there, names the file with date/time, and
# returns the file path.
#
# Parameters
# 
#   - the_config - settings including collections of Groups of Persons
# 
# -----------------------------------------------------------------------------
def setup_folders(the_config):

    dest_file = ""
    
    if not the_config.filename:
        return False

    messages_file = the_config.filename

    suffix = pathlib.Path(messages_file).suffix

    # make a copy of the source file if in debug mode or move it so 
    # we know it's been dealt with / processed.
    try:
        Path(the_config.archive_subfolder).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(the_config.getStr(the_config.STR_COULD_CREATE_ARCHIVE_SUBFOLDER) + ": " + messages_file)
        print(e)
        return False

    now_str = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%m-%S')
    filename = the_config.service + '_' + now_str + suffix
    dest_file = os.path.join(the_config.archive_subfolder, filename)
    try:
        if the_config.debug:
            shutil.copy(messages_file, dest_file)
        elif os.path.exists(the_config.archive_subfolder):
            shutil.move(messages_file, dest_file)

    except Exception as e:
        if the_config.debug:
            print(the_config.getStr(the_config.STR_COULD_NOT_MOVE_MESSAGES_FILE) + ": " + messages_file)
        else:
            print(the_config.getStr(the_config.STR_COULD_NOT_COPY_MESSAGES_FILE) + ": " + messages_file)
            print(e)
        pass

    return dest_file

# -----------------------------------------------------------------------------
#
# Set up all of the folders and then call back to load_messages() from the 
# client of this library to do specific message type (e.g. SMS) loading of
# the messages. 
#
# Parameters:
# 
#   - the_config - settings including collections of Groups of Persons
#   - load_messages - function that loads the messages into `messages[]`
#   - messages - array containing all of the Messages
#   - reactions - array containing all of the Reactions
# 
# -----------------------------------------------------------------------------
def get_markdown(the_config, load_messages, messages, reactions):

    dest_file = ""

    # email doesn't have a messages file to parse
    if the_config.service != markdown.YAML_SERVICE_EMAIL:
        dest_file = setup_folders(the_config)

    if the_config.service == markdown.YAML_SERVICE_EMAIL or os.path.exists(dest_file): 
        
        if load_messages(dest_file, messages, reactions, the_config):
            
            # add the reactions to the corresponding messages
            message.addReactions(messages, reactions)

            # divy up messages to the groups and people they were with
            message.addMessages(messages, the_config)

            # for email service, the attachments are put in the right folder 
            # as each email attachment is processed. No need to move them 
            if the_config.service != markdown.YAML_SERVICE_EMAIL:
                attachment.moveAttachments(the_config.people, the_config.people_folder, the_config)
                attachment.moveAttachments(the_config.groups, the_config.groups_folder, the_config)

            # generate the Markdown for each person
            for the_person in the_config.people:
                folder = os.path.join(the_config.people_folder, the_person.slug)
                markdown.createMarkdownFile(the_person, folder, the_config)

            # generate the Markdown for each group
            for the_group in the_config.groups:
                folder = os.path.join(the_config.groups_folder, the_group.slug)
                markdown.createMarkdownFile(the_group, folder, the_config)

    return True