import logging
from Logging.Customlogger import class_customlogger
from db_connection.Databaseoperations import Mongodb_operations
from scrapper.image_scrapper import scrapper
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])  # route to display the home page
def homePage():
    # when the app runs the application executes the connection to database and checks if the
    # specified collection exits
    # if the collection exists the data is fetched from the database
    db_name = "google_images"
    db_operation = Mongodb_operations(db_name)
    sc = scrapper(db_operation)
    log_main = class_customlogger.custom_logger_fn(logger_name=__name__, logLevel=logging.DEBUG,
                                                   log_filename="main.log")
    # POST method expects a query/condition to filter the data from db
    if request.method == 'POST':
        try:
            log_main.info(f"Home page searching results based on the {request.json['search_string']}")
            keyword = request.json['search_string']
            num_images = request.json['img_count']
            msg = sc.search_image_in_google(keyword, num_images)
            return msg

        except Exception as e:
            log_main.error(e)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
