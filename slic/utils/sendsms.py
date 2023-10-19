from .sendmail import sendmail


SMS_GATEWAY_ADDRESS = "swissphone-gateway.com"


def sendsms(phone_number, text):
    to_addr = f"{phone_number}@{SMS_GATEWAY_ADDRESS}"
    return sendmail(to_addr, body=text)



