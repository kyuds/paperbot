class Summary:
    def __init__(self, id, title, original, summary, authors, published, link):
        self.id = id
        self.title = title
        self.original = original
        self.summary = summary
        self.authors = authors
        self.published = published
        self.link = link

    def __repr__(self):
        return self.title
