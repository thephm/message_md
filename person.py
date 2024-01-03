NEW_LINE = "\n"

class Person:
    def __init__(self):
        self.slug = ""
        self.firstName = ""
        self.lastName = ""
        self.mobile = ""
        self.linkedInId = ""
        self.emailAddresses = [] # collection of email addresses
        self.conversationId = ""
        self.folderCreated = False
        self.messages = []  # collection of messages by day

    def __str__(self):
        output = "slug: " + self.slug + NEW_LINE
        output += "mobile: " + self.mobile + NEW_LINE
        output += "firstName: " + self.firstName + NEW_LINE
        output += "lastName: " + self.lastName + NEW_LINE
        output += "conversationId: " + self.conversationId + NEW_LINE
        output += "emailAddresses: " + str(self.emailAddresses)
        return output
        