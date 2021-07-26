import json
import logging

from logstash_formatter import LogstashFormatterV1


class Helpers(object):
    def __init__(self):
        pass

    def _set_console_logger(self, lvl, logger, format):
        ch = logging.StreamHandler()
        ch.setLevel(lvl)
        fr = format()
        ch.setFormatter(fr)
        logger.addHandler(ch)
        return logger

    def set_logger(self, lvl):
        """
        Sets logger.
        :param lvl: logging level (DEBUG, INFO, WARNING, ERROR)
        :return: logger
        """
        logger = logging.getLogger()
        logger.setLevel(lvl)
        logger = self._set_console_logger(lvl=lvl, logger=logger, format=LogstashFormatterV1)
        return logger

    def get_config(self, config_path):
        try:
            with open(config_path) as f:
                cnf = json.load(f)
                return cnf
        except Exception as ex:
            raise

    def iterate_dictionary(self, dictionary, key):
        """
        Function to iterate through the arbitrary dictionary and return the path and value.
        :param dictionary: json object.
        :param key: empty array for keeping track of keys and values.
        :return: returns generator of keys and values.
        """
        if isinstance(dictionary, dict):
            for k in dictionary.keys():
                local_key = key[:]
                local_key.append(k)
                for el in self.iterate_dictionary(dictionary=dictionary[k], key=local_key):
                    yield el
        else:
            yield key, dictionary
