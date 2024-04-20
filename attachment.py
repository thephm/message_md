import os
import shutil
import markdown

# constants
NEW_LINE = "\n"

# depends on Config

class Attachment:
    def __init__(self):
        self.id = ""
        self.type = "" # contentType
        self.size = 0
        self.filename = ""
        self.custom_filename = ""
        self.width = 0
        self.height = 0
        self.voice_note = False

    def __str__(self):
        output = "id: " + self.id + NEW_LINE
        output += "type: " + self.type + NEW_LINE
        output += "size: " + str(self.size) + NEW_LINE
        output += "filename: " + self.filename + NEW_LINE
        output += "custom_filename: " + self.custom_filename + NEW_LINE
        output += "width: " + str(self.width) + NEW_LINE
        output += "height: " + str(self.height) + NEW_LINE
        output += "voice_note: " + str(self.voice_note)
        return output
    
    def is_image(self):
        is_image = False

        if self.type[:5] == "image":
            is_image = True

        return is_image

    # Get the file name with suffix based on it's content type
    def add_suffix(self, the_config):
        filename = self.id
        try:
            suffix = the_config.MIMETypes[self.type]
            if len(suffix):
                filename += "." + suffix

        except Exception as e:
            print(the_config.getStr(the_config.STR_UNKNOWN_MIME_TYPE) + ": '" + self.type + "' (" + self.id + ')')
            print(e)
            pass

        return filename

    # Generates the Markdown for media links e.g. [[photo.jpg]]
    def generate_link(self, the_config):
        link = ""

        # @todo this should be part of the Signal code not here! 
        # originally, I included 'media/file.jpg' but since Obsidian
        # finds any file in the vault, no need to tell it where it is
        if the_config.service == markdown.YAML_SERVICE_SIGNAL:
            filename = self.add_suffix(the_config)
        else:
            filename = self.id

        if len(filename):
            if self.is_image() and the_config.image_embed:
                link = "!"
            link += "[[" + filename
            if self.is_image() and the_config.image_width:
                link += "|" + str(the_config.image_width)
            link += "]]" + NEW_LINE

        return link

# -----------------------------------------------------------------------------
#
# Move the attachments from the attachments folder to the folder of the
# specific person that shared them. If it's a group message, move the 
# attachments under the `group` folder.
#
# Parameters
# 
#   - entities - either a collection of Person or Group objects
#   - folder - top-level folder where the files will go
#   - the_config - all the configuration
# 
# -----------------------------------------------------------------------------
def moveAttachments(entities, folder, the_config):

    source_file = ""
    dest_file = ""

    for entity in entities:
        for dated_messages in entity.messages:
            for the_message in dated_messages.messages:
                dest_folder = markdown.getMediaFolderName(entity, folder, the_message, the_config)
                dest_folder = os.path.join(dest_folder, the_config.media_subfolder)

                # create the `media` subfolder if it doesn't exist
                if len(the_message.attachments) and not os.path.exists(dest_folder):
                    markdown.createFolder(dest_folder)

                for the_attachment in the_message.attachments:
                    
                    if len(the_attachment.id):
                        source_file = os.path.join(the_config.sourceFolder, the_config.attachments_subfolder)
                        source_file = os.path.join(source_file, the_attachment.id)
                        
                        # Signal doesn't add a file suffix, so we add it here
                        if the_config.service == markdown.YAML_SERVICE_SIGNAL:
                            dest_file = os.path.join(dest_folder, the_attachment.add_suffix(the_config))
                        else:
                            dest_file = os.path.join(dest_folder, the_attachment.id)

                        if the_config.debug:
                            print(source_file + ' -> ' + dest_file)
                        
                        if os.path.exists(source_file) and not os.path.exists(dest_file):
                            try: 
                                if the_config.debug:
                                    shutil.copy(source_file, dest_file)
                                    print('copied')
                                else:
                                    shutil.move(source_file, dest_file)
                            except Exception as e:
                                print(the_config.getStr(the_config.STR_COULD_NOT_MOVE_THE_ATTACHMENT) + ": " + source_file + " -> " + dest_file)
                                print(e)
