import logging
import logging.handlers

import os

import asyncio
import json

from datetime import datetime

# environ for app
environ = {}


# config
class Config:
    def __init__(self) -> None:
        super(Config,self).__init__()

        # load config
        with open("config.json","r") as config_json:
            self.config = json.load(config_json)
        environ["CONFIG"] = self.config


        # get logger
        self.logger = logging.getLogger()

        filename = datetime.now().strftime("%Y-%m-%d")
        len_logs = len([log for log in os.listdir("./logs") if filename in log])


        handler = logging.handlers.RotatingFileHandler(filename = f"./logs/{filename} {len_logs+1}.txt", mode = "a", maxBytes = 5000000, backupCount = 5,)


        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        environ["LOGGER"] = self.logger
        environ["LOGGER_HANDLER"] = handler

        self.logger.info("Config has succesfully loaded")


    # laod and update config
    async def updateConfigFile(self):
        while True:
            with open("config.json","r") as config_json:
                self.config = json.load(config_json)
            environ["CONFIG"] = self.config

            await asyncio.sleep(0.1)
        