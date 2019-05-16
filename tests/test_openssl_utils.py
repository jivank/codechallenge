import pytest
import tempfile
from smart_edge import openssl_utils


@pytest.yield_fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_keypair_is_reused(tmpdir):
    openssl = openssl_utils.OpenSSL(tmpdir)
    openssl2 = openssl_utils.OpenSSL(tmpdir)
    assert openssl.public_key_contents == openssl2.public_key_contents


def test_signature(tmpdir):
    openssl = openssl_utils.OpenSSL(tmpdir)
    signature = openssl.sign_string("abc")
    assert openssl.verify_signature("abc", signature)


def test_wrong_signature(tmpdir):
    openssl = openssl_utils.OpenSSL(tmpdir)
    signature = openssl.sign_string("abc")
    assert not openssl.verify_signature("123", signature)
