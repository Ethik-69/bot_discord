import json
import time
import asyncio
import logging
import feedparser
from bs4 import BeautifulSoup

import aiohttp
import discord
from discord.ext import commands

from rethinkdb import RethinkDB
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


# Initialise logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='log/main.log',
    encoding='utf-8',
    mode='w'
)

handler.setFormatter(
    logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
    )
)

#logger.addHandler(handler)


# Get config from config file
with open('config.json', 'r') as file:
    config = json.load(file)

db_name = config["data_base"]['db_name']
rdb = RethinkDB()

# Create DB connection
try:
    connection = rdb.connect(
        host=config["data_base"]['host'],
        port=config["data_base"]['port'],
        db=db_name
    )
except RqlDriverError:
    logging.exception("No database connection could be established.")
    exit(1)


# Extension load at startup
startup_extensions = [
    #'lib.flux'
]


# Initialise discord lib
bot = commands.Bot(command_prefix=config['prefix'])

bot.remove_command('help')


@bot.event
async def on_ready():
    # Print info when the bot is fully loaded
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)


@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    await bot.process_commands(message)


def check_author(message):
    if message.author.id not in config["authorized_users"].values():
        return False
    return True


@bot.command(pass_context=True)
async def help(context):
    """ Create help message """
    logger.info("[*] Command called: Help")
    embed = discord.Embed(
        title="BotyBota =D",
        description="This is a fucking bot. Oh yeah !\nCommand list:",
        color=0x2B7D63
    )

    embed.add_field(
        name="$help",
        value="Give this message.",
        inline=False
    )

    embed.add_field(
        name="$say [text]",
        value="Make the bot says what you want !",
        inline=False
    )

    embed.add_field(
        name="$purge [x]",
        value="[Authorization Needed] Del the last x message.",
        inline=False
    )

    embed.add_field(
        name="$silent_purge [x]",
        value="[Authorization Needed] Del the last x message. Without notifying it.",
        inline=False
    )

    embed.add_field(
        name="$add_site [site_name] [channel_name] [flux_rss_url]",
        value="[Authorization Needed] Add site into DB.",
        inline=False
    )

    embed.add_field(
        name="$remove_site [site_name]",
        value="[Authorization Needed] Remove site from DB.",
        inline=False
    )

    embed.add_field(
        name="$remove_all_articles",
        value="[Authorization Needed][Debug] Remove site from DB.",
        inline=False
    )

    await context.send(embed=embed)


@bot.command(pass_context=True)
async def say(context, *message):
    """ Make bot say message """
    logger.info("[*] Command called: Say")
    await context.channel.purge(limit=1)
    await context.send(" ".join(message))


@bot.command(pass_context=True)
async def purge(context, number: int):
    """ Clear a specified number of messages in the chat """
    if not check_author(context.message):
        return None

    logger.info("[*] Command called: Purge")
    deleted = await context.channel.purge(limit=number + 1)
    await context.send(f'Deleted {len(deleted) - 1} message(s)')


@bot.command(pass_context=True)
async def silent_purge(context, number: int):
    """ Clear a specified number of messages in the chat (silently)"""
    if not check_author(context.message):
        return None

    logger.info("[*] Command called: Silent purge")
    await context.channel.purge(limit=number + 1)


@bot.command(pass_context=True)
async def add_site(context, site_name, channel_name, url):
    """ Add site into DB """
    if not check_author(context.message):
        return None

    logger.info("[*] Command called: Add site")
    site_table_name = config["data_base"]['sites_table_name']

    try:
        # Check if site already is in DB
        result = rdb.db(db_name).table(site_table_name).filter(
            rdb.row["site_name"] == site_name
        ).count().run(connection)

        if result == 0:
            # Check if given url is well formed
            if not url.startswith("https://"):
                await context.send("ERROR: Site not added, url must start with https://")
                return None

            # Check if given channel is already created
            channel = get_channel(channel_name)
            if channel is None:
                await context.send("ERROR: You need to create channel first.")

            rdb.db(db_name).table(
                site_table_name
            ).insert(
                {
                    "site_name": site_name,
                    "channel_name": channel_name,
                    "rss_url": url
                }
            ).run(connection)

            logger.info(f"[*] Site added: {site_name} in channel {channel_name}")
            await context.send(f"Site added: {site_name} in channel {channel_name}")

        elif result > 1:
            logger.error("More than one of this site in DB")
            await context.send("ERROR: More than one of this site in DB")

        else:
            logger.info("[x] Site already in DB")
            await context.send("Site already in DB")

    except Exception as err:
        logger.exception(f"{err}")
        await context.send(f"Error: {err}")


@bot.command(pass_context=True)
async def remove_site(context, site_name):
    """ Remove site from DB """
    if not check_author(context.message):
        return None

    logger.info("[*] Command called: Remove site")
    site_table_name = config["data_base"]['sites_table_name']

    try:
        # Check if site is in DB
        result = rdb.db(db_name).table(site_table_name).filter(
            rdb.row["site_name"] == site_name
        ).count().run(connection)

        if result > 1:
            logger.error("More than one of this site in DB")
            await context.send("ERROR: More than one of this site in DB")

        elif result == 1:
            # If site is in DB get field and use ID to remove it
            result = rdb.db(db_name).table(site_table_name).filter(
                rdb.row["site_name"] == site_name
            ).run(connection)

            rdb.db(db_name).table(site_table_name).get(
                list(result)[0]["id"]
            ).delete().run(connection)

            logger.info(f"[*] {site_name} removed from DB")
            await context.send(f"{site_name} removed from DB.")

        else:
            logger.info("[*] Site not in db so not removed")
            await context.send("Site not in db so not removed.")

    except Exception as err:
        logger.exception(f"{err}")
        await context.send(f"Error: {err}")


@bot.command(pass_context=True)
async def remove_all_articles(context):
    """ Remove from DB articles older than x """
    if not check_author(context.message):
        return None

    logger.info("[*] Remove all articles.")
    article_table_name = config["data_base"]['article_table_name']

    try:
        connection = rdb.connect(
            host=config["data_base"]['host'],
            port=config["data_base"]['port'],
            db=db_name
        )

    except RqlDriverError:
        logger.exception("No database connection could be established.")

    result = list(rdb.db(db_name).table(article_table_name).run(connection))

    for article in result:
        logger.info(f"[*] Remove old {article['title']}")
        rdb.db(db_name).table(article_table_name).get(article['id']).delete().run(connection)

    await context.send(f"All articles removed")


def get_channel(channel_name):
    """ Return channel object """
    for channel in bot.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None


def setup_db(config):
    """ DB config """
    logger.info('[*] DB Setup')
    # DB connection
    connection = rdb.connect(
        host=config["data_base"]['host'],
        port=config["data_base"]['port']
    )

    # Check if db already exist
    db_list = rdb.db_list().run(connection)

    if db_name not in db_list:
        try:
            # Create DB
            rdb.db_create(db_name).run(connection)

            # Create tables
            rdb.db(db_name).table_create(
                config["data_base"]['article_table_name']
            ).run(connection)

            rdb.db(db_name).table_create(
                config["data_base"]['sites_table_name']
            ).run(connection)

            logger.info('[*] Database setup completed')

        except RqlRuntimeError as err:
            logger.exception(f"{err}")

        connection.close()


if __name__ == '__main__':
    setup_db(config)

    # Load extensions
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(config['token'])


"""
$add_site korben korben https://korben.info/feed
$add_site zataz zataz https://www.zataz.com/feed/
$add_site hackernews hacker_news https://news.ycombinator.com/rss
$add_site github_trending github_trending https://github.com/trending
$add_site sebsauvage sebsauvage https://sebsauvage.net/rhaa/rss_fulltext.php
$add_site journal_du_hacker journal_du_hacker https://www.journalduhacker.net/rss
$add_site hollandais_volant hollandais_volant https://lehollandaisvolant.net/rss.php
"""
