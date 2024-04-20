NEW_LINE = "\n"

class Person:
    def __init__(self):
        self.slug = ""
        self.first_name = ""
        self.last_name = ""
        self.mobile = ""
        self.linkedIn_id = ""
        self.email_addresses = [] # collection of email addresses
        self.conversation_id = ""
        self.folder_created = False
        self.messages = []  # collection of messages by day

    def __str__(self):
        output = "slug: " + self.slug + NEW_LINE
        output += "mobile: " + self.mobile + NEW_LINE
        output += "first_name: " + self.first_name + NEW_LINE
        output += "last_name: " + self.last_name + NEW_LINE
        output += "conversation_id: " + self.conversation_id + NEW_LINE
        output += "email_addresses: " + str(self.email_addresses)
        return output
        