from typing import List

class Summary:
    """
    id:         id of the paper (not associated with arXiv)
    title:      title of paper
    original:   original, raw abstract
    summary:    a gpt4o-mini summarization of the abstract
    authors:    list of authors
    published:  published date (as recorded on arXiv)
    link:       link to paper
    """
    
    def __init__(self, 
                 id: int, 
                 title: str, 
                 original: str, 
                 summary: str, 
                 authors: List[str], 
                 published: str, 
                 link: str):
        self.id = id
        self.title = title
        self.original = original
        self.summary = summary
        self.authors = authors
        self.published = published
        self.link = link

    def __repr__(self):
        return self.title + "\n\n" + self.original + "\n\n" + self.link
