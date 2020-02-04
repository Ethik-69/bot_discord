import json
import time
import logging
import feedparser
from bs4 import BeautifulSoup
from rethinkdb import RethinkDB
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


class Flux:
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
        handler = logging.FileHandler(
            filename='log/flux.log',
            encoding='utf-8',
            mode='w'
        )

        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
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
        self.flux_rss()

    def flux_rss(self):
        """ Check rss flux from DB and send new articles into right channel """

        self.logger.info("[*] Background task started: RSS Flux.")
        site_table_name = self.config["data_base"]['sites_table_name']
        article_table_name = self.config["data_base"]['article_table_name']

        while True:
            self.logger.info("[*] Start checking for new articles.")
            result = list(self.rdb.db(self.config["data_base"]['db_name']).table(site_table_name).run(self.connection))

            self.logger.info(result)
            for site in result:
                # Parse rss flux
                self.logger.info(f"[*] Current site checked: {site['site_name']}")
                self.logger.info(f"[*] Site data: {site}")
                rss_feed = feedparser.parse(site["rss_url"])
                self.logger.debug(f"[*] Feed entry count: {len(rss_feed['entries'])}")

                for entrie in rss_feed["entries"]:
                    # Check if entry (article) is already in DB
                    result = self.rdb.db(self.config["data_base"]['db_name']).table(article_table_name).filter(
                        self.rdb.row["title"] == entrie["title"]
                    ).count().run(self.connection)

                    self.logger.debug(f"[*] Checked article: {entrie['title']}")
                    self.logger.debug(f"[*] Count: {result}")

                    if result == 0:
                        # Add article into DB
                        self.logger.info(f"[*] New article from {site['site_name']}]: {entrie['title']}")

                        # Parse html to remove tags
                        clean_summary = BeautifulSoup(entrie['summary'], "html.parser").text
                        if len(clean_summary) > 500:
                            clean_summary = clean_summary[:500]

                        self.rdb.db(self.config["data_base"]['db_name']).table(
                            article_table_name
                        ).insert(
                            {
                                "title": entrie["title"],
                                "link": entrie["link"],
                                "summary": entrie["summary"],
                                "timestamp": round(time.time())
                            }
                        ).run(self.connection)

            self.remove_old_article()
            time.sleep(3600)

    def remove_old_article(self):
        """ Remove from DB articles older than x """
        self.logger.info("[*] Background task started: Remove old articles.")
        article_table_name = self.config["data_base"]['article_table_name']

        result = list(self.rdb.db(self.config["data_base"]['db_name']).table(article_table_name).run(self.connection))

        for article in result:
            # 7776000 = 90 Jours
            if article["timestamp"] < round(time.time()) - 7776000:
                self.logger.info(f"[*] Remove old {article['title']}")
                self.rdb.db(self.config["data_base"]['db_name']).table(article_table_name).get(article['id']).delete().run(self.connection)


if __name__ == "__main__":
    flux = Flux()
    flux.run()