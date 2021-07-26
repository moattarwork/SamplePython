#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import operator
from functools import reduce


# TODO T1 add configuration and tests. Config file to store paths for the specific elements of the message.
# TODO T2 extract correlation id from the message payload.
class ProcessEvent(object):

    def __init__(self, event, logger, namespace, process_id):
        self._event = event["Records"][0]["Sns"]
        self._logger = logger
        self._n = namespace
        self._process_id = process_id

    def _get_payload(self):
        self._logger.info({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                           "msg": "Getting an event payload."})

        payload = json.loads(self._event["Message"])

        self._logger.debug({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                            "msg": f"Payload: {payload}"})
        return payload

    def _extract_value(self, payload, path):
        try:
            self._logger.debug({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                                "msg": f"Extracting value from the payload for the following path: {path}"})
            self._logger.debug({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                                "msg": f"Receiving payload: {payload}"})

            value = reduce(operator.getitem, path, payload)
        except Exception as ex:
            self._logger.error({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                                "msg": f"Encountered an error on the following path: {path}\nerror: {ex}"})
        else:
            return value

    def _generate_txt_body(self):
        self._logger.debug({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                            "msg": f"Generating txt body of the email!"})
        try:

            payload = self._get_payload()
            payload = json.loads(payload["default"])
            txt = self._extract_value(payload=payload, path=self._n.text)
            return txt
        except Exception as ex:
            self._logger.error({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                                "msg": f"Encountered an error: {ex}"})

    def _generate_html_body(self):
        self._logger.debug({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                            "msg": f"Generating txt body of the email!"})
        try:
            payload = self._get_payload()
            payload = json.loads(payload["default"])
            html = self._extract_value(payload=payload, path=self._n.html)
            return html
        except Exception as ex:
            self._logger.error({"msg": f"Encountered an error: {ex}"})

    def extract_message(self):
        self._logger.info({"x-process-id": self._process_id, "x-raw-correlation-id": self._n.raw_correlation_id,
                           "msg": f"Extracting message for a notification email"})
        try:
            payload_ = self._get_payload()
            val_dict = json.loads(payload_["default"])
            destination = {"ToAddresses": self._extract_value(payload=val_dict, path=self._n.email_to)}
            subject_data = self._extract_value(payload=val_dict, path=self._n.subject_path)
            message = {
                "Subject": {
                    "Charset": self._n.charset,
                    "Data": subject_data
                },
                "Body": {
                    "Html": {
                        "Charset": self._n.charset,
                        "Data": self._generate_html_body()
                    },
                    "Text": {
                        "Charset": self._n.charset,
                        "Data": self._generate_txt_body()
                    }

                }
            }
            source = self._extract_value(payload=val_dict, path=self._n.email_from)

            return destination, message, source

        except Exception as ex:
            self._logger.error({"x-process-id": self._process_id, "msg": f"Encountered an error {ex}"})
