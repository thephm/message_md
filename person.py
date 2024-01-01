NEW_LINE = "\n"

class Person:
    def __init__(self):
        self.phoneNumber = ""
        self.slug = ""
        self.firstName = ""
        self.lastName = ""
        self.folderCreated = False
        self.messages = []  # collection of messages by day
        self.conversationId = ""

    def __str__(self):
        output = "phoneNumber: " + self.phoneNumber + NEW_LINE
        output += "slug: " + self.slug + NEW_LINE
        output += "firstName: " + self.firstName + NEW_LINE
        output += "lastName: " + self.lastName + NEW_LINE
        output += "conversationId: " + self.conversationId
        return output
        