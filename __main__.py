"""Main file for Terminal project"""

import logging
import os

from logging.handlers import RotatingFileHandler
from alor.downloader import AlorDownloader
from terminal.terminal import Terminal
from t_terminal import T_Terminal
from myLib.strategies import PriceChanelGrid
from myLib.brokers import Tinkoff

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
    MAIN_MESSAGE = """Choose mode:
1 - launch Alor terminal;
2 - launch T terminal
0 - exit;
                        
Please, enter mode:"""

    STRATEGY_MESSAGE = """Choose strategy:
1 - Strategy PriceChanelGrid
0 - back to main menu;
                        
Please, enter strategy:"""

    prepare_logs()  # Prepare logging system
    logger.info("Program start")

    while True:
        # Choose main mode
        mode = int(input(MAIN_MESSAGE))

        if mode == 1:
            # Step 1 - download the data
            downloader = AlorDownloader()
            downloader.prepare()
            print("All quotes files have been updated")

            # Step 2 - download new data to terminal
            terminal = Terminal()
            terminal.prepare()
            print("Terminal prepared")

            # Step 3 - show the terminal
            terminal.show()
            break

        elif mode == 2:
            while True:
                # Choose strategy
                strategy = int(input(STRATEGY_MESSAGE))

                if strategy == 0:
                    break  # Return to main menu
                elif strategy == 1:
                    # Create terminal with selected strategy
                    broker = Tinkoff()
                    strategy = PriceChanelGrid(broker)
                    terminal = T_Terminal(strategy, broker)

                    terminal.prepare()
                    terminal.run()
                    break
                else:
                    print("Invalid strategy selected. Please try again.")
            break
        elif mode == 0:
            print("Goodbye!")
            logger.info("Program end")
            break

        else:
            print("Invalid mode selected. Please try again.")
