# Functions to format message.Message objects into Markdown including 
# reactions and embedded ![[wikilinks]] to any attachments.

import os
import shutil
import logging

import pathlib
from pathlib import Path

from datetime import datetime
import config
import markdown
import attachment
import message

def setup(the_config, service):

    result = the_config.setup(service)
    
    return result

def setup_folders(the_config):
    """
    Creates an archive subfolder and then either copies or moves - depending on
    configuration - the message file there, names the file with date/time, and
    returns the file path.
    
    Args:
        the_config (Config): Configuration object containing settings, paths, 
        and collections of Groups of Persons   
    
    Returns:
        str: The path to the destination file where the messages are archived.
    """

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
        logging.error(the_config.get_str(the_config.STR_COULD_CREATE_ARCHIVE_SUBFOLDER) + ": " + messages_file + ". Error: " + str(e))
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
            logging.error(f"{the_config.get_str(the_config.STR_COULD_NOT_MOVE_MESSAGES_FILE)}: {messages_file} -> {dest_file}. Error: {e}")
        else:
            logging.error(f"{the_config.get_str(the_config.STR_COULD_NOT_COPY_MESSAGES_FILE)}: {messages_file} -> {dest_file}. Error: {e}")
        pass

    return dest_file

def get_markdown(the_config, load_messages, messages, reactions):
    """
    Set up all of the folders and then call back to load_messages() from the
    client of this library to do specific message type (e.g. SMS) loading of
    the messages. 
    
    Args:
        the_config(Config): Configuration object containing settings, paths, 
            and collections of Groups of Persons
        load_messages(function): Function to load messages into `messages[]`
        messages(list): List to hold all of the Message objects
        reactions(list): List to hold all of the Reaction objects
         
    Returns:   
        bool: True if the Markdown generation was successful, False otherwise.
    """

    dest_file = ""

    # email doesn't have a messages file to parse
    if the_config.service != markdown.YAML_SERVICE_EMAIL:
        dest_file = setup_folders(the_config)

    if the_config.service == markdown.YAML_SERVICE_EMAIL or os.path.exists(dest_file): 
        
        if load_messages(dest_file, messages, reactions, the_config):
            
            # add the reactions to the corresponding messages
            message.add_reactions(messages, reactions)

            # sort them by their timestamp
            messages = sorted(messages, key=lambda msg: msg.timestamp)

            # add messages to the corresponding groups and people
            message.add_messages(messages, the_config)

            # for email service, the attachments are put in the right folder 
            # as each email attachment is processed. No need to move them 
            if the_config.service != markdown.YAML_SERVICE_EMAIL:
                attachment.move_attachments(the_config.people, the_config.people_folder, the_config)
                attachment.move_attachments(the_config.groups, the_config.groups_folder, the_config)

            # generate the Markdown for each person
            for the_person in the_config.people:
                if not the_person.ignore:
                    folder = os.path.join(the_config.people_folder, the_person.slug)
                    markdown.create_markdown_file(the_person, folder, the_config)

            # generate the Markdown for each group
            for the_group in the_config.groups:
                folder = os.path.join(the_config.groups_folder, the_group.slug)
                markdown.create_markdown_file(the_group, folder, the_config)

    return True