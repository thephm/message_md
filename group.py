NEW_LINE = "\n"

class Group:
    def __init__(self):
        self.id = ""
        self.slug = ""
        self.description = ""
        self.conversation_id = ""
        self.members = []  # collection of `Person.slug`s
        self.messages = [] # collection of messages by day

    def __str__(self):
        output = "slug: " + self.slug + NEW_LINE
        output += "id: " + self.id + NEW_LINE
        output += "description: " + self.description + NEW_LINE
        output += "members: " + str(self.members) + NEW_LINE
        output += "messages: " + str(len(self.messages)) + NEW_LINE
        output += "conversation_id: " + self.conversation_id
        return output