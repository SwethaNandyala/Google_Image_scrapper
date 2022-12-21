import logging
import os

import gridfs
from Logging.Customlogger import class_customlogger
from db_connection.CreateDBConnections import Mongodb_connection


class Mongodb_operations(Mongodb_connection):
    def __init__(self, db_name):
        self.log_crud = class_customlogger.custom_logger_fn(logger_name=__name__, logLevel=logging.DEBUG,
                                                            log_filename="CRUDoperations.log")

        self.connection_url = "mongodb://mongodb:mongodb@ac-rdwzeeq-shard-00-00.ffsxijb.mongodb.net:27017," \
                              "ac-rdwzeeq-shard-00-01.ffsxijb.mongodb.net:27017," \
                              "ac-rdwzeeq-shard-00-02.ffsxijb.mongodb.net:27017/?ssl=true&replicaSet=atlas-1n8oe5" \
                              "-shard-0" \
                              "&authSource=admin&retryWrites=true "
        self.db_name = db_name
        super().__init__(self.connection_url, self.db_name)
        # Create an object of GridFs for the above database.
        self.fs = gridfs.GridFS(self.connect_to_db(self.db_name))

    def insert_data(self, file_loc, img_name, keyword, url):

        try:
            self.log_crud.info("Executing insert_data function")
            f = open(os.path.join(file_loc, img_name), 'rb')
            data = f.read()
            self.fs.put(data, filename=img_name, search_string=keyword, _id=url)
            self.log_crud.info(f"inserted {img_name} to db")
        except Exception as e:
            self.log_crud.error('Exception occurred in insert_data.Exception message:' + str(e))
