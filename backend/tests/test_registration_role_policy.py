"""Regression tests for public signup privilege boundaries.

These tests are run with the backend's pytest environment.
"""
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_public_signup_defaults_to_no_client_selectable_role():
    user = UserCreate(
        email="citizen@example.com",
        username="citizen1",
        full_name="Example Citizen",
        password="valid-test-password",
    )
    assert not hasattr(user, "role_name")


def test_public_signup_rejects_privileged_role_field():
    try:
        UserCreate(
            email="officer@example.com",
            username="officer1",
            full_name="Example Officer",
            password="valid-test-password",
            role_name="ADMIN",
        )
    except ValidationError:
        return
    raise AssertionError("Public registration must reject caller-supplied roles")
