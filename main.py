import logging
import os

from logging.handlers import RotatingFileHandler
from alor.downloader import AlorDownloader
from terminal.terminal import Terminal

logger = logging.getLogger(__name__)


def prepare_logs() -> None:
    """Prepare logging system for the bot.

    This function does the following:
        - Ensure "logs/" directory exists in the current working directory.
        - Set up basic configuration for the logging module.
        - Configure a rotating file handler which logs to robot.log in the logs/ directory.
    """
    # Ensure "logs/" directory exists in the current working directory
    if not os.path.exists("logs/"):
        # Create "logs/" directory
        os.makedirs("logs/")

    # Set up basic configuration for the logging module
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        handlers=[
            RotatingFileHandler(
                "logs/robot.log", maxBytes=100000000, backupCount=10, encoding="utf-8"
            )
        ],
        encoding="utf-8",
    )


if __name__ == "__main__":

    prepare_logs()  # Prepare logging system
    logger.info("Program start")

    try:
        # Step 1 - download the data
        downloader = AlorDownloader()
        downloader.prepare()
        logger.info("All quotes files have been prepared")
        print("All quotes files have been updated")

        # Step 2 - download new data to terminal
        terminal = Terminal()
        terminal.prepare()
        logger.info("Terminal prepared")
        print("Terminal prepared")

        # Step 3 - show the terminal
        terminal.show()

    except Exception as ex:
        logger.critical("Something went wrong: %s", repr(ex))
