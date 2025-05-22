#!/usr/bin/env python3
"""filter logger
    Notes in case of confusion:
    1) Message however edited is passed to the format specified

    2) The format() method (different from format) of the class overrides the
    initial format() method that every logger.Formatter object has
    the format() is always called  every time a record is logged.
    In the logging system, when a log message is emitted
    using a logger, it is passed to a LogRecord object.

    3) LogRecord object contains information about the log message,
    such as the message itself, whatever message is passed is logged
    and the super format() (from parent) is called on it
    before our custom format occurs.
    When you do customlogger.INFO(message), that message is
    passed as the log record message.
    So clarifying the argument in the format method,
    when customlogger.INFO(message) is done,
    the message is passed to the LogRecord object
    and passed to the format method."""

import logging
import os
import re
from typing import List, Tuple

import mysql.connector

PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def splitter(message: str, separator: str) -> List:
    """splits message for easy iteration"""
    splitted = message.split(separator)
    return splitted


def pattern_rplc(field, redaction) -> Tuple:
    """sets pattern and replacement to
    be used with re.sub"""
    pattern = field + ".*"
    replacement = field + "=" + redaction
    return pattern, replacement


def filter_datum(fields: List[str],
                 redaction: str,
                 message: str,
                 separator: str) -> str:
    """returns the log message obfuscated
    with personal data protected"""
    new_list = splitter(message, separator)
    for field in fields:
        pattern, replacement = pattern_rplc(field, redaction)
        for idx, val in enumerate(new_list):
            new_list[idx] = re.sub(pattern, replacement, val)
    return ";".join(new_list)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        # call to logging.Formatter, FORMAT is passed to
        # tell logging.Formatter how records will be printed
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """returns a formatted and filtered record/message
        which is logged when desired.
        - implemented call to the format method
          of logging.Formatter, the parent class
        - filter_datum performed on the message to censor
        personal details

        the censored details are returned
        remember, format() method of logging.Formatter
        is different from format passed to logging.Formatter
        """
        message: str = super().format(record)
        # filter the returned record using the custom
        # desired format
        filtered_message: str = filter_datum(self.fields,
                                             self.REDACTION,
                                             message,
                                             self.SEPARATOR)
        return filtered_message


def get_logger() -> logging.Logger:
    """gets logger object"""
    this_logger = logging.Logger("user_data", level=logging.INFO)
    this_logger.propagate = False

    # set the streamhandler
    stream_handler = logging.StreamHandler(stream=None)
    # use RedactingFormatter as format
    log_formatter = RedactingFormatter(PII_FIELDS)
    stream_handler.setFormatter(log_formatter)
    # add the stream handler as a handler for this logger
    this_logger.addHandler(stream_handler)
    return this_logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """gets database"""
    username = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "root")
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    data_base = os.getenv("PERSONAL_DATA_DB_NAME")
    conn = mysql.connector.connect(host=db_host,
                                   database=data_base,
                                   user=username,
                                   password=password)
    return conn


def main() -> None:
    """main function"""
    db = get_db()
    logger = get_logger()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    fields = cursor.column_names
    for row in cursor:
        message = ";".join("{}={}".format(k, v) for k, v in zip(fields, row))
        message = message.strip()
        logger.info(message)
        """
        zip(fields, row) creates an iterator that pairs up each field name
        with the corresponding value from the current row. So, for the first
        row we could get ('id', 1), ('name', 'John Doe'), etc.
        "{}={}; ".format(k, v) creates a string with the field name and its
        corresponding value, separated by an equals sign and a semicolon.
        So for the first row, we'd get 'id=1 ', 'name=John Doe ', etc.
        "".join(...) concatenates all of the formatted strings into a
        single string with each field-value pair separated by a semicolon
        and a space.
        So for the first row, we'd get 'id=1; name=John Doe;
        email=john.doe@example.com;phone=555-123-4567; password=p@ssw0rd; '."""
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
