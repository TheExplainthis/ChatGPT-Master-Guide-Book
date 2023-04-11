import os

from pymongo import MongoClient


class MongoDB():
    """
    Environment Variables:
        MONGODB_PATH
        MONGODB_DBNAME
    """
    client: None
    db: None

    def connect_to_database(self, mongo_path=None, db_name=None):
        mongo_path = mongo_path or os.getenv('MONGODB_PATH')
        db_name = db_name or os.getenv('MONGODB_DBNAME')
        self.client = MongoClient(mongo_path)
        self.db = self.client[db_name]


mongodb = MongoDB()
