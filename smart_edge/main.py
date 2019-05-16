#!/usr/bin/env python3
import json
import sys
from openssl_utils import OpenSSL


class App:
    def __init__(self):
        self.openssl = OpenSSL()

    def process(self, message):
        result = {
            "message": message,
            "signature": self.openssl.sign_string(message).decode("utf-8"),
            "pubkey": self.openssl.public_key_contents,
        }
        return json.dumps(result, indent=4)


if __name__ == "__main__":
    args = dict(zip(["filename", "message"], sys.argv))
    app = App()
    if not args.get("message") or len(sys.argv) > 2:
        sys.exit("Usage: main.py '<some message>'")
    message = args["message"]
    if len(message) > 250:
        sys.exit("Message must be under 250 characters")
    print(app.process(message))
