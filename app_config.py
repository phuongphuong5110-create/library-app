import configparser
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent / "config.ini"


def load_database_config():
    if not _CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {_CONFIG_PATH}. Copy config.example.ini to config.ini and edit."
        )
    parser = configparser.ConfigParser()
    parser.read(_CONFIG_PATH, encoding="utf-8")
    if "database" not in parser:
        raise ValueError("config.ini must contain a [database] section")
    db = parser["database"]
    return {
        "host": db.get("host", "localhost"),
        "port": db.getint("port", 3306),
        "user": db["user"],
        "password": db.get("password", ""),
        "database": db["database"],
        "charset": db.get("charset", "utf8mb4"),
    }
