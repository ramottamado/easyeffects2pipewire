import json
from decimal import Decimal
from math import log10


def db_to_linear(db: float) -> float:
    """
    Convert decibels to linear scale.

    :param db: decibel value
    :type db: float
    :return: linear scale value
    :rtype: float
    """
    return 10 ** (db / 20)


def linear_to_db(linear: float) -> float:
    """
    Convert linear scale to decibels.

    :param linear: linear scale value
    :type linear: float
    :return: decibel value
    :rtype: float
    """
    if linear <= 0:
        return float("-inf")
    return 20 * log10(linear)


def load_config(filepath: str) -> dict:
    """
    Load configuration file.

    :param filepath: path to configuration file
    :type filepath: str
    :return: parsed configuration data as dictionary
    :rtype: dict
    """
    with open(filepath, "r") as f:
        data = f.read()
    return json.loads(data)


def format_6f(value: float) -> float:
    return float(format(Decimal(value), ".6f"))
