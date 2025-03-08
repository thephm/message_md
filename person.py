NEW_LINE = "\n"

class Person:
    def __init__(self):
        self.slug = ""
        self.first_name = ""
        self.last_name = ""
        self.full_name = "" # for signal `profileFullName`
        self.ignore = False
        self.mobile = ""
        self.linkedin_id = ""
        self.email_addresses = [] # collection of email addresses
        self.conversation_id = "" # needed for Signal only
        self.service_id = "" # needed for Signal only
        self.folder_created = False
        self.messages = []  # collection of messages by day

    def __str__(self):
        output = "slug: " + self.slug + NEW_LINE
        output += "mobile: " + self.mobile + NEW_LINE
        output += "first_name: " + self.first_name + NEW_LINE
        output += "last_name: " + self.last_name + NEW_LINE
        output += "full_name: " + self.full_name + NEW_LINE
        output += "ignore: " + str(self.ignore) + NEW_LINE
        output += "mobile: " + str(self.mobile) + NEW_LINE
        output += "linkedin_id: " + self.linkedin_id + NEW_LINE
        output += "email_addresses: " + str(self.email_addresses) + NEW_LINE
        output += "service_id: " + self.service_id + NEW_LINE
        return output
        