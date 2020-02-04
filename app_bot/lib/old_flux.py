import json
import time
import logging
import feedparser
from bs4 import BeautifulSoup
import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


class Flux:
    def __init__(self, bot):
        self.bot = bot

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

        # Get config from config file
        with open('config.json', 'r') as file:
            self.config = json.load(file)

        rdb = rdb.RethinkDB()
        db_name = config["data_base"]['db_name']


        # Create DB connection
        try:
            self.connection = rdb.connect(
                host=config["data_base"]['host'],
                port=config["data_base"]['port'],
                db=db_name
            )
        except RqlDriverError:
            logging.exception("No database connection could be established.")

        # Launch background tasks
        self.bot.loop.create_task(self.flux_rss())
        self.bot.loop.create_task(self.remove_old_article())

    async def flux_rss(self):
        """ Check rss flux from DB and send new articles into right channel """
        await self.wait_until_ready()
        channel = discord.Object(id='448106862991114241')
        channel.send("mitmut")

        logger.info("[*] Background task started: RSS Flux.")
        site_table_name = self.config["data_base"]['sites_table_name']
        article_table_name = self.config["data_base"]['article_table_name']

        try:
            self.connection = rdb.connect(
                host=self.config["data_base"]['host'],
                port=self.config["data_base"]['port'],
                db=db_name
            )

        except RqlDriverError:
            logger.exception(503, "No database self.connection could be established.")

        while not self.is_closed():
            logger.info("[*] Start checking for new articles.")
            result = list(rdb.db(db_name).table(site_table_name).run(self.connection))

            logger.info(result)
            for site in result:
                # Parse rss flux
                logger.info(f"[*] Current site checked: {site['site_name']}")
                logger.info(f"[*] Site data: {site}")
                rss_feed = feedparser.parse(site["rss_url"])
                logger.debug(f"[*] Feed entry count: {len(rss_feed['entries'])}")

                for entrie in rss_feed["entries"]:
                    # Check if entry (article) is already in DB
                    result = rdb.db(db_name).table(article_table_name).filter(
                        rdb.row["title"] == entrie["title"]
                    ).count().run(self.connection)

                    logger.debug(f"[*] Checked article: {entrie['title']}")
                    logger.debug(f"[*] Count: {result}")

                    if result == 0:
                        # Add article into DB
                        logger.info(f"[*] New article from {site['site_name']}]: {entrie['title']}")

                        rdb.db(db_name).table(
                            article_table_name
                        ).insert(
                            {
                                "title": entrie["title"],
                                "link": entrie["link"],
                                "summary": entrie["summary"],
                                "timestamp": round(time.time())
                            }
                        ).run(self.connection)

                        # Parse html to remove tags
                        clean_summary = BeautifulSoup(entrie['summary'], "html.parser").text
                        if len(clean_summary) > 500:
                            clean_summary = clean_summary[:500]

                        embed = discord.Embed(
                            title=entrie["title"],
                            description=f"Site: {site['site_name']}\nLink: {entrie['link']}\n{clean_summary}",
                            color=0x2B7D63
                        )

                        # Get right channel and send article into it
                        logger.info(f"Channel: {site['channel_name']}")
                        used_channel = None

                        for channel in bot.get_all_channels():
                            if channel.name == site["channel_name"]:
                                used_channel = channel
                                break

                        await used_channel.send(embed=embed)
                        exit()

            await asyncio.sleep(3600)  # task runs every hour

    async def remove_old_article(self):
        """ Remove from DB articles older than x """
        await self.wait_until_ready()
        logger.info("[*] Background task started: Remove old articles.")
        article_table_name = self.config["data_base"]['article_table_name']

        try:
            self.connection = rdb.connect(
                host=self.config["data_base"]['host'],
                port=self.config["data_base"]['port'],
                db=db_name
            )

        except RqlDriverError:
            logger.exception("No database self.connection could be established.")

        while not self.is_closed():
            result = list(rdb.db(db_name).table(article_table_name).run(self.connection))

            for article in result:
                # 7776000 = 90 Jours
                if article["timestamp"] < round(time.time()) - 7776000:
                    logger.info(f"[*] Remove old {article['title']}")
                    rdb.db(db_name).table(article_table_name).get(article['id']).delete().run(self.connection)

            await asyncio.sleep(86400)  # task runs every day

    def get_channel(self, channel_name):
        for channel in bot.get_all_channels():
            if channel.name == channel_name:
                return channel
        return None


if __name__ == "__main__":
    flux = Flux()
    flux.run()