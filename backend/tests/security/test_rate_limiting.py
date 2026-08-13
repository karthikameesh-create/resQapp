from unittest.mock import MagicMock

import pytest
from slowapi import Limiter
from slowapi.util import get_remote_address


def test_rate_limiter_can_be_configured():
    limiter = Limiter(
        key_func=get_remote_address,
    )

    assert limiter is not None
    assert callable(limiter._key_func)