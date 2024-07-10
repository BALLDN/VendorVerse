import pytest
import requests
import pytest
from app import create_app
from subprocess import Popen
import time
import os


@pytest.fixture(scope="session")
def app():
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def live_server(app):
    port = 5001
    process = Popen(["flask", "run", "--port", str(port)])
    time.sleep(2)  # Give the server some time to start

    yield f"http://localhost:{port}"

    process.terminate()


def test_approve_vendor(live_server):
    """A3-1 Approve Vendor Account Registration"""
    requests.post(live_server+'/admin')
    return


def test_deny_vendor():
    """A3-2 Deny Vendor Account Registration"""
    return


def test_approve_employee():
    """A4-1 Approve Employee Account Registration"""
    return


def test_deny_employee():
    """A4-2 Deny Employee Account Registration"""
    return


def test_approve_booking():
    """A5-1 Approve Vendor Booking"""
    return


def test_deny_booking():
    """A5-2 Deny Vendor Booking"""
    return
