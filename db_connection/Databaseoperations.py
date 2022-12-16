import logging
from Logging.Customlogger import class_customlogger
from db_connection.CreateDBConnections import Mongodb_connection


class Mongodb_operations(Mongodb_connection):
    def __init__(self, db_name):
        self.log_crud = class_customlogger.custom_logger_fn(logger_name=__name__, logLevel=logging.DEBUG,
                                                            log_filename="CRUDoperations.log")
        self.collection = None
        self.connection_url = "mongodb://mongodb:mongodb@ac-rdwzeeq-shard-00-00.ffsxijb.mongodb.net:27017," \
                              "ac-rdwzeeq-shard-00-01.ffsxijb.mongodb.net:27017," \
                              "ac-rdwzeeq-shard-00-02.ffsxijb.mongodb.net:27017/?ssl=true&replicaSet=atlas-1n8oe5" \
                              "-shard-0" \
                              "&authSource=admin&retryWrites=true "
        self.db_name = db_name
        super().__init__(self.connection_url, self.db_name)

    def check_if_collection_exists(self, collection_name):
        try:
            self.log_crud.info("Executing check if collection exists")
            if collection_name in self.connect_to_db(self.db_name).list_collection_names():
                self.log_crud.info(f"{collection_name} collection exists")
                return True
            else:
                self.log_crud.info(f"{collection_name} collection doesnt exists")
                return False
        except Exception as e:
            self.log_crud.error(e)

    def get_or_create_collection(self, collection_name):
        try:
            self.log_crud.info("Executing get_or_create_collection method")
            if not self.check_if_collection_exists(collection_name):
                self.collection = self.connect_to_db(self.db_name)[collection_name]
            else:
                self.log_crud.info(f"{collection_name} already exists")
                self.collection = self.connect_to_db(self.db_name).get_collection(name=collection_name)

        except Exception as e:
            self.log_crud.error(e)

    def insert_data(self, data):
        """
        :param data: Dictionary or list of dictionaries
        :return: None
        """
        try:
            self.log_crud.info("Executing insert_data function")
            if type(data) == dict:
                self.collection.insert_one(data)
                self.log_crud.info("One Data insertion Completed!!")
            elif type(data) == list:
                self.collection.insert_many(data)
                self.log_crud.info("Bulk Data insertion Completed!!")
        except Exception as e:
            self.log_crud.error('Exception occurred in insert_data.Exception message:' + str(e))

    def get_all_data_from_db(self):
        try:
            self.log_crud.info("Executing get_all_data_from_db method")
            self.log_crud.info("Retrieving data..")
            data = self.collection.find()
            return data
        except Exception as e:
            self.log_crud.error(e)
        else:
            self.log_crud.info("retrieved all data")

    def filter_data_from_db(self, condition: dict):
        try:
            self.log_crud.info("Executing filter_data_from_db method")
            self.log_crud.info("Retrieving data...")
            data = self.collection.find(condition)
            return data
        except Exception as e:
            self.log_crud.error(e)
        else:
            self.log_crud.info("filtered all data based on query")

    def delete_data(self, query, many=False):
        """
        :param query: filter criterion
        :param many: True/False to delete one or many
        :return: None
        """
        try:
            self.log_crud.info("Executing delete_data function")
            if not many:
                d = self.collection.delete_one(query)
                self.log_crud.info("One record Data deletion Completed!!")
                self.log_crud.info("Deleted {} record".format(d.deleted_count))
            else:
                d = self.collection.delete_many(query)
                self.log_crud.info("Many records Data deletion Completed!!")
                self.log_crud.info("Deleted {} record".format(d.deleted_count))
        except Exception as e:
            self.log_crud.error('Exception occurred in delete_data.Exception message:' + str(e))

    def drop_current_collection(self):
        """drop current collection"""
        try:
            self.log_crud.info("Executing delete current collection method")
            data = self.connect_db(self.db_name).drop_collection(self.collection)
            self.log_crud.info("Successfully deleted collection " + str(data))
        except Exception as e:
            self.log_crud.error(e, exc_info=True)
