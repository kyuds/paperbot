import boto3
import json
from datetime import datetime

from errors import *
from models import Summary
from settings import FILE_PREFIX, FILE_POSTFIX

class S3Retriever:
    def __init__(self, bucket_name, prefix):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.s3 = boto3.client("s3")

    def get_summaries(self):
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
        
        fnames = S3Retriever.__process_filenames([obj["Key"] for obj in response["Contents"]])
        return fnames[max(fnames.keys())]

    @staticmethod
    def __process_filenames(fnames):
        processed = {}
        for name in fnames:
            if not name.startswith(FILE_PREFIX) or not name.endswith(FILE_POSTFIX):
                raise ScraperError(f"Invalid filename format. Got filename: {name}")
            stripped = name.removeprefix(FILE_PREFIX).removesuffix(FILE_POSTFIX)
            try:
                parsed_date = datetime.strptime(stripped, "%y%m%d")
                processed[parsed_date] = name
            except ValueError as e:
                raise ScraperError(f"Invalid filename date format. {e}")
        return processed

if __name__ == "__main__":
    # Testing
    def make_name(datestring):
        return FILE_PREFIX + datestring + FILE_POSTFIX
    
    names = [make_name("250607"), make_name("250608"), make_name("250808")]
    processed = S3Retriever._S3Retriever__process_filenames(names)
    recent = processed[max(processed.keys())]
    assert recent == names[-1]
    
    print("All tests pass!")
