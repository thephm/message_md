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
        self.fileName = ""
        self.customFileName = ""
        self.width = 0
        self.height = 0
        self.voiceNote = False

    def __str__(self):
        output = "id: " + self.id + NEW_LINE
        output += "type: " + self.type + NEW_LINE
        output += "size: " + str(self.size) + NEW_LINE
        output += "fileName: " + self.fileName + NEW_LINE
        output += "customFileName: " + self.customFileName + NEW_LINE
        output += "width: " + str(self.width) + NEW_LINE
        output += "height: " + str(self.height) + NEW_LINE
        output += "voiceNote: " + str(self.voiceNote)
        return output
    
    def isImage(self):
        isImage = False

        if self.type[:5] == "image":
            isImage = True

        return isImage

    # Get the file name with suffix based on it's content type
    def addSuffix(self, theConfig):
        fileName = self.id
        try:
            suffix = theConfig.MIMETypes[self.type]
            if len(suffix):
                fileName += "." + suffix

        except Exception as e:
            print(theConfig.getStr(theConfig.STR_UNKNOWN_MIME_TYPE) + ": '" + self.type + "' (" + self.id + ')')
            print(e)
            pass

        return fileName

    # Generates the Markdown for media links e.g. [[photo.jpg]]
    def generateLink(self, theConfig):
        link = ""

        # @todo this should be part of the Signal code not here! 
        # originally, I included 'media/file.jpg' but since Obsidian
        # finds any file in the vault, no need to tell it where it is
        if theConfig.service == markdown.YAML_SERVICE_SIGNAL:
            fileName = self.addSuffix(theConfig)
        else:
            fileName = self.id

        if len(fileName):
            if self.isImage() and theConfig.imageEmbed:
                link = "!"
            link += "[[" + fileName
            if self.isImage() and theConfig.imageWidth:
                link += "|" + str(theConfig.imageWidth)
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
#   - theConfig - all the configuration
# 
# -----------------------------------------------------------------------------
def moveAttachments(entities, folder, theConfig):

    sourceFile = ""
    destFile = ""

    for entity in entities:
        for datedMessages in entity.messages:
            for theMessage in datedMessages.messages:
                destFolder = markdown.getMediaFolderName(entity, folder, theMessage, theConfig)
                destFolder = os.path.join(destFolder, theConfig.mediaSubFolder)

                # create the `media` subfolder if it doesn't exist
                if len(theMessage.attachments) and not os.path.exists(destFolder):
                    markdown.createFolder(destFolder)

                for theAttachment in theMessage.attachments:
                    
                    if len(theAttachment.id):
                        sourceFile = os.path.join(theConfig.sourceFolder, theConfig.attachmentsSubFolder)
                        sourceFile = os.path.join(sourceFile, theAttachment.id)
                        
                        # Signal doesn't add a file suffix, so we add it here
                        if theConfig.service == markdown.YAML_SERVICE_SIGNAL:
                            destFile = os.path.join(destFolder, theAttachment.addSuffix(theConfig))
                        else:
                            destFile = os.path.join(destFolder, theAttachment.id)

                        if theConfig.debug:
                            print(sourceFile + ' -> ' + destFile)
                        
                        if os.path.exists(sourceFile) and not os.path.exists(destFile):
                            try: 
                                if theConfig.debug:
                                    shutil.copy(sourceFile, destFile)
                                    print('copied')
                                else:
                                    shutil.move(sourceFile, destFile)
                            except Exception as e:
                                print(theConfig.getStr(theConfig.STR_COULD_NOT_MOVE_THE_ATTACHMENT) + ": " + sourceFile + " -> " + destFile)
                                print(e)
