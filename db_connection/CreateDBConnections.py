import logging
import pymongo

from Logging.Customlogger import class_customlogger


class Mongodb_connection:
    def __init__(self, connection_url, db_name):
        self.log_db = class_customlogger.custom_logger_fn(logger_name=__name__, logLevel=logging.DEBUG,
                                                            log_filename="Database_operations.log")
        self.client = None
        self.db = None
        self.establish_connection(connection_url)
        self.create_database(db_name)

    def check_if_db_exists(self, db_name):
        try:
            self.log_db.info("Executing Check if a db exists method")

            if db_name in self.client.list_database_names():
                self.log_db.info(f"Database {db_name} exists")
                return True
            else:
                self.log_db.info(f"Database {db_name} doesnt exists")
                return False
        except Exception as e:
            self.log_db.error(str(e))

    def establish_connection(self, connection_url):
        try:
            self.client = pymongo.MongoClient(connection_url)
        except Exception as e:
            self.log_db.error(str(e), exc_info=True)
            self.log_db.info("Please retry connecting to mongo db")
            self.establish_connection(connection_url)
        else:
            self.log_db.info("Successfully connected with mongodb")

    def create_database(self, db_name):
        try:
            self.log_db.info("Executing Creating a Database method")
            if not self.check_if_db_exists(db_name):
                self.db = self.client[db_name]
                self.log_db.info(f"Created a Database {db_name}")
            else:
                self.connect_to_db(db_name)
        except Exception as e:
            self.log_db.error(e, exc_info=True)

    def connect_to_db(self, db_name):
        try:
            self.db = self.client[db_name]
            return self.db
        except Exception as e:
            self.log_db.error(str(e))

    def close_connection(self):
        self.client.close()

    def drop_present_database(self):
        try:
            self.log_db.info("Executing the drop_present_database method")
            if self.check_if_db_exists(self.db.name):
                self.log_db.info(f"The {self.db} exists")
                self.client.drop_database(self.db.name)
            else:
                self.log_db.info(f"No db_connection exists with name:{self.db.name}")
        except Exception as e:
            self.log_db.error(e)
