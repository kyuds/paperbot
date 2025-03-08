import boto3
import json
from datetime import datetime
from typing import List

from errors import *
from models import Summary
from settings import *

# please refer to another repo (paperscraper) for the data formats.
# a lambda function runs everyday and places new paper summaries into
# an S3 bucket (bucket name defined in settings.py)

class S3Utils:
    def __init__(self, 
                 bucket_name: str = BUCKET_NAME, 
                 prefix: str = BUCKET_PREFIX):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.s3 = boto3.client("s3")

    def get_summaries(self) -> List[Summary]:
        # we assume that the key is present as it is retrieved by list_objects_v2
        key = self.__most_recent_filename()
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        contents = response["Body"].read().decode("utf-8")
        
        summaries = []
        for line in contents.splitlines():
            try:
                obj = json.loads(line)
                summaries.append(
                    Summary(
                        obj["id"],
                        obj["title"],
                        obj["original"],
                        obj["summary"],
                        obj["authors"],
                        obj["published"],
                        obj["link"]
                    )
                )
            except json.JSONDecodeError as e:
                raise ScraperError(f"Invalid file contents. {e}")
            
        return summaries
    
    def __most_recent_filename(self):
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix)
        if "Contents" not in response:
            raise S3Error("Contents not in response", 500)
        
        fnames = S3Utils.__process_filenames([obj["Key"] for obj in response["Contents"]])
        return fnames[max(fnames.keys())]

    @staticmethod
    def __process_filenames(fnames: List[str]):
        processed = {}
        for name in fnames:
            if not name.startswith(FILE_PREFIX) or not name.endswith(FILE_POSTFIX):
                raise ScraperError(f"Invalid filename format. Got filename: {name}")
            stripped = name.removeprefix(FILE_PREFIX).removesuffix(FILE_POSTFIX)
            try:
                parsed_date = datetime.strptime(stripped, "%y%m%d%H%M%S")
                processed[parsed_date] = name
            except ValueError as e:
                raise ScraperError(f"Invalid filename date format. {e}")
        return processed

if __name__ == "__main__":
    # Testing
    s3 = S3Utils(BUCKET_NAME, BUCKET_PREFIX)
    summaries = s3.get_summaries()
    print("Number of documents:", len(summaries))
    print(summaries[0])
