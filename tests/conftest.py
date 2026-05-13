"""
pytest fixtures shared across the test suite.
"""

import pytest
from self_healing.driver import SelfHealingDriver


@pytest.fixture(scope="session")
def driver():
    """
    One SelfHealingDriver instance for the whole test session.
    scope="session" means Chrome opens once and closes once,
    which is faster than opening a new browser per test.
    """
    d = SelfHealingDriver(headless=True)
    yield d
    d.quit()
