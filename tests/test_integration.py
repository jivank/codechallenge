import os
import json
from subprocess import check_output, CalledProcessError, STDOUT


dir_path = os.path.dirname(os.path.realpath(__file__))
process_path = os.path.realpath(os.path.join(dir_path, "..", "smart_edge", "main.py"))


def test_no_arguments():
    try:
        check_output(["python", process_path], stderr=STDOUT, timeout=3)
    except CalledProcessError as cpe:
        assert cpe.output == b"Usage: main.py '<some message>'\n"


def test_too_many_arguments():
    try:
        check_output(
            ["python", process_path, "one", "too many"], stderr=STDOUT, timeout=3
        )
    except CalledProcessError as cpe:
        assert cpe.output == b"Usage: main.py '<some message>'\n"


def test_message():
    output = check_output(["python", process_path, "hello world"])
    response = json.loads(output.decode("utf-8"))
    assert "message" in response
    assert "signature" in response
    assert "pubkey" in response

    assert response["message"] == "hello world"


def test_public_private_keypair_generated():
    output = check_output(["python", process_path, "hello world"])

    home = os.path.expanduser("~")
    conf_dir = os.path.join(home, ".smart-edge-app")
    public = os.path.join(conf_dir, "public.pem")
    private = os.path.join(conf_dir, "private.pem")

    assert os.path.isfile(public)
    assert os.path.isfile(private)

def test_reject_over_character_limit():
    message_251_chars = ''.join(['0' for i in range(251)])
    try:
        check_output(["python", process_path, message_251_chars], stderr=STDOUT, timeout=3)
    except CalledProcessError as cpe:
        assert cpe.output == b"Message must be under 250 characters\n"