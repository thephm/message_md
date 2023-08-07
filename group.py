class Group:
    def __init__(self):
        self.id = ""
        self.slug = ""
        self.description = ""
        self.members = []  # collection of `Person.slug`s
        self.messages = [] # collection of messages by day
