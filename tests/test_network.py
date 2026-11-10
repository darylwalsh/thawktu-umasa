"""Keep the default test process offline."""

import socket

import pytest
from pytest_socket import SocketBlockedError


def test_socket_creation_is_blocked() -> None:
    with (
        pytest.warns(UserWarning, match=r"A test tried to use socket\.socket"),
        pytest.raises(SocketBlockedError),
    ):
        socket.socket()
