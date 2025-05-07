import json
from datetime import datetime
from threading import Thread

from pika import BlockingConnection, ConnectionParameters


DEFAULT_HOST = "sf-daq"
STATUS_EXCHANGE = "status"


class RequestStatus:

    ENTRIES = (
        "announced",
        "started",
        "success",
        "failure",
        "ghosts"
    )


    def __init__(self, instrument=None, host=DEFAULT_HOST, **kwargs):
        self.instrument = instrument
        self.host = host
        self.kwargs = kwargs

        for i in self.ENTRIES:
            setattr(self, i, {})

        self.thread = thread = Thread(target=self._run)
        thread.daemon = True
        thread.start()


    def clear(self):
        for i in self.ENTRIES:
            getattr(self, i).clear()


    def _run(self):
        try:
            connection = BlockingConnection(ConnectionParameters(self.host, **self.kwargs))
        except Exception as e:
            raise ConnectionError(f"cannot connect to request status on {self.host}") from e

        channel = connection.channel()
        channel.exchange_declare(exchange=STATUS_EXCHANGE, exchange_type="fanout")

        queue = channel.queue_declare(queue="", exclusive=True).method.queue
        channel.queue_bind(queue=queue, exchange=STATUS_EXCHANGE)
        channel.basic_consume(queue, self._on_status, auto_ack=True)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()


    def _on_status(self, _channel, _method_frame, header_frame, body):
        correlation_id = header_frame.correlation_id
        headers        = header_frame.headers
        timestamp      = header_frame.timestamp

        body = body.decode()
        request = json.loads(body)

        instrument = request.get("metadata", {}).get("general/instrument")
        if instrument is not None and self.instrument is not None and instrument != self.instrument:
            return

        action = headers["action"]

        #TODO: insert current time if there is no timestamp?
        if timestamp is not None:
            timestamp = datetime.fromtimestamp(timestamp / 1e9)

        key = correlation_id.split("-", 1)[0]

        #TODO: nicely pack the information
        data = {
            "timestamp": timestamp,
            "headers": headers,
            "request": request
        }

        if action == "write_request":
            self.announced[key] = data
        elif action == "write_start":
            if key in self.announced:
                self.announced.pop(key)
                self.started[key] = data
            else:
                self.ghosts[key] = data
        elif action == "write_finished":
            if key in self.started:
                self.started.pop(key)
                self.success[key] = data
            else:
                self.ghosts[key] = data
        elif  action == "write_rejected":
            if key in self.started:
                self.started.pop(key)
                self.failure[key] = data
            else:
                self.ghosts[key] = data


    def __repr__(self):
        header = "Request Status:"
        underline = "-" * len(header)
        res = [header, underline]

        maxlen = max(len(i) for i in self.ENTRIES)
        entries = {f"{i}:".ljust(maxlen+1): len(getattr(self, i)) for i in self.ENTRIES}
        res += [f"{k} {v}" for k, v in entries.items()]

        res = "\n".join(res)
        return res





if __name__ == "__main__":
    rs = RequestStatus()


