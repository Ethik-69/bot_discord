import json
import logging
import requests
from rethinkdb import RethinkDB
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


class FeedChecker:
    def __init__(self):
        # Get config from config file
        with open('config.json', 'r') as file:
            self.config = json.load(file)

        self.logger = None
        self._init_logger()

        self.rdb = None
        self.connection = None
        self._init_db_connection()

    def _init_logger(self):
        # Initialise logger
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()

        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s:%(filename)s:%(name)s:%(lineno)d:%(levelname)s:%(message)s'
            )
        )

        self.logger.addHandler(handler)

    def _init_db_connection(self):
        self.rdb = RethinkDB()

        # Create DB connection
        try:
            self.connection = self.rdb.connect(
                host=self.config["data_base"]['host'],
                port=self.config["data_base"]['port'],
                db=self.config["data_base"]['db_name']
            )
        except RqlDriverError:
            self.logger.exception("No database connection could be established.")
            exit(1)

    def run(self):
        self.logger.info("Start: Create Feed")

        feed = self.rdb.db(
            self.config["data_base"]['db_name']
        ).table(
            self.config["data_base"]['article_table_name']
        ).changes().run(self.connection)

        self.logger.info("Start: Start loop")

        for change in feed:
            self.logger.info("New entrys")
            baseURL = "https://discordapp.com/api/channels/{}/messages".format(
                change["new_val"]["channel_id"]
            )

            headers = {
                "Authorization": f"Bot {self.config['token']}",
                "User-Agent": "BotyBota (http://some.url, v0.1)",
                "Content-Type": "application/json"
            }

            message = change["new_val"]

            data = json.dumps(
                {
                    "content": message
                }
            )

            req = requests.post(
                baseURL,
                headers=headers,
                data=data
            )

            if not str(req.status_code).startswith("2"):
                self.logger.error(f"{req.status_code}")
                self.logger.error(f"{req.text}")


if __name__ == "__main__":
    feed_checker = FeedChecker()
    feed_checker.run()
