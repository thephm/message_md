class Group:
    def __init__(self):
        self.id = ""
        self.slug = ""
        self.description = ""
        self.conversationId = ""
        self.members = []  # collection of `Person.slug`s
        self.messages = [] # collection of messages by day

    def __str__(self):
        output = "id: " + self.id + NEW_LINE
        output += "slug: " + self.slug + NEW_LINE
        output += "description: " + self.description + NEW_LINE
        output += "members: " + self.members + NEW_LINE
        output += "# messages: " + str(self.messages.size) + NEW_LINE
        output += "conversationId: " + self.conversationId
        return output