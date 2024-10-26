import os
import yaml
import logging
import tiktoken
import dataclasses
from dataclasses import dataclass


LOG = logging.getLogger("memobase_server")
LOG.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter(
        "%(levelname)s:    %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
LOG.addHandler(console_handler)

ENCODER = tiktoken.encoding_for_model("gpt-4o")


@dataclass
class Config:
    max_chat_blob_buffer_token_size: int = 8192

    @classmethod
    def load_config(cls) -> "Config":
        default_config = cls()
        if not os.path.exists("config.yaml"):
            LOG.warning("No config file found, using default config")
            return default_config
        with open("config.yaml") as f:
            overwrite_config = yaml.safe_load(f)
            LOG.info(f"Load config: {overwrite_config}")
        return dataclasses.replace(default_config, **overwrite_config)


CONFIG = Config.load_config()
