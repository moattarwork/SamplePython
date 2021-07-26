#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import boto3
from argparse import Namespace
from process_event.helpers import Helpers
from process_event.process_event import ProcessEvent
from process_event.send_email import SendEmail


path = "configuration.json"


def lambda_handler(event, context):
    """
    This is the entry point for lambda.
    :param event: The SNS event
    :param context:
    :return:
    """
    # Setting up constants for the lambda call
    process_id = str(uuid.uuid4())

    h = Helpers()
    logger = h.set_logger(get_logging_lvl())
    dictionary = h.get_config(config_path=path)
    logger.info({"x-raw-correlation-id": process_id, "msg": "Starting process"})
    logger.debug({"x-raw-correlation-id": process_id, "msg": "Initiating application"})

    namespace = init_app(dictionary=dictionary, obj_key="notification", helpers=h, logger=logger,
                         correlation_id=process_id)
    raw_correlation_id = namespace.raw_correlation_id

    # Preparing message for email.
    prep_msg = ProcessEvent(event=event, logger=logger, namespace=namespace, process_id=process_id)
    destination, message, source = prep_msg.extract_message()

    # Send email notification
    # TODO add the factory of email clients
    email_client = boto3.client('ses', region_name=os.getenv("REGION_NAME"))
    send_email = SendEmail(logger=logger, correlation_id=raw_correlation_id, email_client=email_client)
    send_email.send_email(email_to=destination, message=message, email_from=source)

def get_logging_lvl():
    """
    Gets the logging level.
    :return:
    """
    lvl = os.getenv("LOG_LVL")
    log_lvl = {
        "debug": "DEBUG",
        "info": "INFO",
        "error": "ERROR"
    }
    return log_lvl.get(lvl.lower(), "INFO")


def init_app(dictionary, obj_key, helpers, logger, correlation_id):
    """
    Function to return namespace with configuration variables.
    :param dictionary: Configuration dictionary
    :param obj_key: Key to the specific configuration node
    :param helpers:
    :param logger:
    :param correlation_id:
    :return: Namespace
    """
    logger.debug({"x-process-id": correlation_id, "msg": f"Initiating and application"})
    try:
        config = dictionary[obj_key]
        ks = []
        ls = {}
        for el in helpers.iterate_dictionary(dictionary=config, key=ks):
            ls["_".join(el[0])] = el[1]
            n = Namespace(**ls)
        return n
    except KeyError as ke:
        logger.error({"x-process-id": correlation_id, "msg": f"Key does  not exists in configuration: "
                                                                     f"{config.keys()}, error: {ke}"})
        raise
    except Exception as ex:
        logger.error({"x-process-id": correlation_id, "msg": f"Encountered an error {ex}"})
        raise


if __name__ == '__main__':
    lambda_handler(event)
