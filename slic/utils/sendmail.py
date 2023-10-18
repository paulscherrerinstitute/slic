import getpass
import subprocess
from email.mime.text import MIMEText


OUTPUT_DIVIDER = "The message was:"
OUTPUT_DIVIDER_BAR = "=" * len(OUTPUT_DIVIDER)


def sendmail(to_addr, from_addr=None, subject=None, body=None):
    msg = Message(to_addr, from_addr=from_addr, subject=subject, body=body)
    msg.send()
    return msg



class Message:

    def __init__(self, to_addr, from_addr=None, subject=None, body=None):
        self.to_addr = to_addr
        self.from_addr = from_addr
        self.subject = subject
        self.body = body

    def send(self):
        msg = self.encode()
        _run_sendmail(msg)

    def encode(self, *args, **kwargs):
        return self.wrap().as_bytes(*args, **kwargs)

    def __repr__(self):
        return self.wrap().as_string()


    def wrap(self):
        from_addr = self.from_addr
        if from_addr is None:
            from_addr = getpass.getuser()

        body = self.body
        if body is None: # here, None does not work!
            body = ""

        msg = MIMEText(body)
        msg["To"] = self.to_addr
        msg["From"] = from_addr
        msg["Subject"] = self.subject
        return msg



def _run_sendmail(msg):
    cmd = ("sendmail", "-t", "-oi")
    res = subprocess.run(cmd, input=msg, stderr=subprocess.PIPE)
    try:
        res.check_returncode()
    except subprocess.CalledProcessError as e:
        raise SendMailError(res.returncode, res.stderr, msg) from e



class SendMailError(Exception):

    def __init__(self, err_code, err_msg, email):
        self.err_code = err_code
        self.err_msg = err_msg = err_msg.decode().strip()
        self.email = email = email.decode()
        err = [
            f"error code {err_code}: {err_msg}\n",
            OUTPUT_DIVIDER,
            OUTPUT_DIVIDER_BAR,
            email
        ]
        err = "\n".join(err)
        super().__init__(err)



