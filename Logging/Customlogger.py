import inspect
import logging

class class_customlogger:

    def __init__(self):
        pass

    def custom_logger_fn(logger_name,logLevel=logging.DEBUG,log_filename="scrap.log",):
        #set class or method name from where it is called. inspect module helps to log the class/method from where the Utilities is called
        # logger_name = __name__
        # 1. create Utilities and set its level
        logger = logging.getLogger(logger_name)
        logger.setLevel(logLevel)
        # 2. create console handler or file handler and set loglevel
        file_handler = logging.FileHandler(filename=log_filename,mode='w')
        # 3. create formatter to show how the logs have to be displayed
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s : %(message)s', datefmt = '%m/%d/%Y %I:%M:%S %p')
        # 4. add formatter to file or console
        file_handler.setFormatter(formatter)
        # 5. add file handler to Utilities
        logger.addHandler(file_handler)
        return logger