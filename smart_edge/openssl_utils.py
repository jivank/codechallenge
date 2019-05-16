import base64
import os
import tempfile
from subprocess import Popen, PIPE, STDOUT, DEVNULL, check_output, CalledProcessError


class OpenSSL:
    def __init__(self, path="~"):
        self.path = os.path.expanduser(path)
        self._generate_rsa_pair()
        with open(self.public_key_path) as pubkey:
            self.public_key_contents = "\n".join(pubkey.readlines())

    def _generate_rsa_pair(self):
        """Generates RSA public-private keypair in an application subfolder of the given path (defaults to user's home)"""
        config_dir = os.path.join(self.path, ".smart-edge-app")
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)

        self.public_key_path = os.path.join(config_dir, "public.pem")
        self.private_key_path = os.path.join(config_dir, "private.pem")

        if os.path.isfile(self.private_key_path) and os.path.isfile(
            self.public_key_path
        ):
            return

        generate_private_key_cmd = [
            "openssl",
            "genrsa",
            "-out",
            self.private_key_path,
            "4096",
        ]
        generate_public_key_cmd = [
            "openssl",
            "rsa",
            "-in",
            self.private_key_path,
            "-pubout",
            "-out",
            self.public_key_path,
        ]

        check_output(generate_private_key_cmd, stderr=DEVNULL)
        check_output(generate_public_key_cmd, stderr=DEVNULL)

    def sign_string(self, message):
        """Returns a base64 signature for a given message"""
        sign_process = Popen(
            ["openssl", "dgst", "-sha256", "-sign", self.private_key_path],
            stdout=PIPE,
            stdin=PIPE,
            stderr=STDOUT,
        )
        sign_process_output = sign_process.communicate(input=message.encode("utf-8"))[0]
        return base64.b64encode(sign_process_output)

    def verify_signature(self, message, signature):
        """Verifies if a base64 signature matches local keypair"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            signature_file = os.path.join(tmpdirname, "signature")
            with open(signature_file, "wb") as sf:
                sf.write(base64.b64decode(signature))

            message_file = os.path.join(tmpdirname, "message")
            with open(message_file, "w") as mf:
                mf.write(message)

            verify_process_cmd = [
                "openssl",
                "dgst",
                "-sha256",
                "-verify",
                self.public_key_path,
                "-signature",
                signature_file,
                message_file,
            ]
            try:
                verify_output = check_output(verify_process_cmd)
                return b"OK" in verify_output
            except CalledProcessError as cpe:
                if b"Failure" in cpe.output:
                    return False
                raise cpe
