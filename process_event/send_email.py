from botocore.exceptions import ClientError


class SendEmail(object):
    def __init__(self, logger, correlation_id, email_client):
        self._logger = logger
        self._correlation_id = correlation_id
        self._email_client = email_client

    def send_email(self, email_to, message, email_from):
        self._logger.info({"x-raw-correlation-id": self._correlation_id, "msg": "Sending email notification."})
        try:
            self._logger.debug(
                {"x-raw-correlation-id": self._correlation_id, "msg": "Inside email notification try section"})
            response = self._email_client.send_email(Destination=email_to, Message=message, Source=email_from, )
            self._logger.debug({"x-raw-correlation-id": self._correlation_id, "msg": "Send the notification email!"})
        except ClientError as cr:
            self._logger.error({"x-raw-correlation-id": self._correlation_id, "msg": f"Encountered a client error "
            f"{cr.response['Error']['Message']}"})
        except Exception as ex:
            self._logger.error({"x-raw-correlation-id": self._correlation_id, "msg": f"Encountered unexpected"
            f" error: {ex}"})
