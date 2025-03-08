from s3utils import S3Utils
from retriever import HybridRetriever
from models import Summary
from errors import *
from settings import *

def main():
    query = "llm agent systems and information retrieval"
    summaries = S3Utils().get_summaries()
    retriever = HybridRetriever(summaries)
    filtered = retriever.retrieve(query)

    for s in filtered:
        print(s)

if __name__ == "__main__":
    main()
