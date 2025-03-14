from enum import Enum, auto
from letta_client import Letta, CreateBlock, MessageCreate
from typing import List

from settings import *
from s3utils import S3Utils
from models import Summary
from retriever import HybridRetriever

AGENT_PERSONA="""
You are an agent responsible for recommending machine learning papers to the user based on their submitted, 
and historical perferences. You will be given tools to submit a query and receive machine learning papers 
that match the query that came out that day. Your job is to construct a query to meet the user's preference 
and when you receive the queried paper response, filter the papers down to return just the most relevant 
papers to the user. Finally, when the user provides feedback about the recent suggestions, please also include 
that into your memory system so that you can create more personalized feedback in the future.
"""

USER_PREFERENCE="""
Name: Daniel. Daniel is interested in machine learning topics such as LLM agent systems and information retrieval. 
He is NOT interested in computational biology or physics. Also, he has interests in systems architectures for 
machine learning. 
"""

QUERY_PROMPT="""
Construct a query string that will be used to search a database of recent machine learning papers. Make sure that 
the query string is aligned with the user's interests and historic feedback (if any). Your output query will be used 
with a sentence embedding model to find semantically similar paragraphs. This is NOT a keyword search or SQL database, 
the database of papers is searched by using vector similarity in embedding space. 

To generate an effective query, follow the guidelines:
- Relevant synonyms
- Related concepts
- Alternative phrasings
- Specific aspects of the topic
- Contextually relevant terms

For the returned user message, respond with the query string ONLY. You are free to reason about creating the query string. 
"""

SUMMARY_PROMPT="""
Your generated query was used to retrieve {k_papers} paper candidates for recommendation. As the final step, look at 
the {k_papers} paper titles and abstracts and determine the {n_papers} MOST RELEVANT paper to the user's interest and preference. 
For the returned user message, respond with {n_papers} numbers, each corresponding to the paper's ID, separated by a single space.
You are free to reason about the selection process.

Format:
ID: (this will contain the paper's ID)
Title: (this will contain the paper's title)
Abstract: (this will contain the paper's abstract)

Papers:
"""

FEEDBACK_PROMPT="""
Below is the feedback for your most recent paper suggestions. Please incorporate the feedback and update information 
on the user's interest and preferences. This feedback will be used in the future to provide more personalized 
recommendations.

Feedback: 
"""

class PaperBot:
    """
    LLM Agent created by Letta to provide user-personalized queries and 
    personalized LLM reranking.
    """
    def __init__(self, name: str, verbose: bool = False):
        assert len(name) > 0, "name of agent should not be empty"
        name = "PAPERBOT_" + name
        self.verbose = verbose
        self.client = Letta(base_url=LETTA_URL)
        self.agent_id = self.__get_agent_id(name)
        self.retriever = HybridRetriever(S3Utils().get_summaries())

    def __get_agent_id(self, name: str) -> str:
        # find agent if it exists in the current database
        found = self.client.agents.list(name=name)
        assert len(found) <= 1, "there are more than two agents of the same name found"
        if len(found) == 1:
            id = found[0].id
            if self.verbose:
                print(f"Successfully found agent: {id}")
            return id
        
        # create agent and return id if the agent name was not found
        created = self.client.agents.create(
            name=name,
            memory_blocks=[
                CreateBlock(
                    label="persona",
                    value=AGENT_PERSONA
                ),
                CreateBlock(
                    label="human",
                    value=USER_PREFERENCE
                ),
            ],
            model="openai/gpt-4o-mini",
            embedding="openai/text-embedding-ada-002",
        )
        if self.verbose:
            print(f"Successfully created agent: {created.id}")
        return created.id
    
    def suggest(self, n: int = 5, top_k: int = 15) -> List[Summary]:
        """
        Make the Letta agent query relevant papers can conduct a final reranking of papers to
        suggest the most relevant machine learning papers for the user.

        Parameters:
        - n: number of papers to output
        - top_k: number of papers for the output of the retrieval process.
        """
        assert n <= top_k, "requesting more documents than preliminary filter"

        # step 1: generate query
        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[
                MessageCreate(
                    role="user",
                    content=QUERY_PROMPT
                ),
            ],
        )
        if self.verbose:
            for message in response.messages:
                print(f"Query Response: {message}\n")
        query = response.messages[-1].content

        # step 2: query
        filtered = self.retriever.retrieve(query, top_k=top_k)
        formatted = PaperBot.__format(filtered)

        # step 3: prompt the agent to return top 5
        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[
                MessageCreate(
                    role="user",
                    content=f"{SUMMARY_PROMPT.format(k_papers=top_k, n_papers=n)}" + "\n\n" + formatted
                ),
            ],
        )
        if self.verbose:
            for message in response.messages:
                print(f"Top 5 Response: {message}\n")
        results = response.messages[-1].content

        # step 4: return results
        ret = []
        for i in results.split():
            try:
                id = int(i)
                if id < len(filtered):
                    ret.append(filtered[id])
                else:
                    print("Out of range:", id)
            except ValueError:
                print("Invalid number:", i)
        
        return ret

    def feedback(self, feedback: str):
        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[
                MessageCreate(
                    role="user",
                    content=FEEDBACK_PROMPT + feedback
                ),
            ],
        )
        if self.verbose:
            for message in response.messages:
                print(f"Feedback Response: {message}\n")

    @staticmethod
    def __format(summaries: List[Summary]) -> str:
        return "\n".join([
            f"ID: {i}\nTitle: {summary.title}\nAbstract: {summary.original}\n"
            for i, summary in enumerate(summaries)
        ])
