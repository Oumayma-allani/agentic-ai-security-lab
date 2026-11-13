
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# TEST 1: Alice accesses her own promotion
def test_alice_own_promotion():
    response = client.get(
        "/promotions/P-101",
        headers=auth("alice-demo-token")
    )
    assert response.status_code == 200
    assert response.json()["tenant_id"] == "tenant-a"


# TEST 2: Alice cannot access Bob's promotion
def test_cross_tenant_access_blocked():
    response = client.get(
        "/promotions/P-201",
        headers=auth("alice-demo-token")
    )
    assert response.status_code == 403


# TEST 3: Bob accesses his own promotion
def test_bob_own_promotion():
    response = client.get(
        "/promotions/P-201",
        headers=auth("bob-demo-token")
    )
    assert response.status_code == 200


# TEST 4: Alice only sees her tenant's promotions
def test_tenant_isolation():
    response = client.get(
        "/promotions",
        headers=auth("alice-demo-token")
    )
    assert response.status_code == 200

    promotions = response.json()
    assert len(promotions) == 2
    assert all(
        p["tenant_id"] == "tenant-a"
        for p in promotions
    )


# TEST 5: Unauthenticated requests are rejected
def test_missing_authentication():
    response = client.get("/promotions")
    assert response.status_code == 401


# TEST 6: Invalid token is rejected
def test_invalid_token():
    response = client.get(
        "/promotions",
        headers=auth("invalid-demo-token")
    )
    assert response.status_code == 401


# TEST 7: Demonstrate the known BOLA vulnerability
@pytest.mark.xfail(
    reason="Known BOLA in intentionally vulnerable lab endpoint",
    strict=True
)
def test_vulnerable_endpoint_should_block_cross_tenant():
    response = client.get(
        "/lab/insecure/promotions/P-201",
        headers=auth("alice-demo-token")
    )

    # Desired secure behavior: 403
    # Actual vulnerable behavior: 200
    assert response.status_code == 403


from app.main import PROMOTIONS


def test_analyst_cannot_approve():
    original_status = PROMOTIONS["P-102"]["status"]

    response = client.post(
        "/promotions/P-102/approve",
        headers=auth("alice-demo-token")
    )

    assert response.status_code == 403
    assert PROMOTIONS["P-102"]["status"] == original_status


def test_admin_can_approve():
    original_status = PROMOTIONS["P-102"]["status"]

    try:
        response = client.post(
            "/promotions/P-102/approve",
            headers=auth("admin-demo-token")
        )

        assert response.status_code == 200
        assert PROMOTIONS["P-102"]["status"] == "approved"

    finally:
        PROMOTIONS["P-102"]["status"] = original_status


def test_admin_cannot_approve_other_tenant():
    original_status = PROMOTIONS["P-201"]["status"]

    response = client.post(
        "/promotions/P-201/approve",
        headers=auth("admin-demo-token")
    )

    assert response.status_code == 403
    assert PROMOTIONS["P-201"]["status"] == original_status

from types import SimpleNamespace
from unittest.mock import patch

from app.agent import AuthContext, approve_promotion


def test_approval_without_confirmation_is_blocked():
    runtime = SimpleNamespace(
        context=AuthContext(token="admin-demo-token")
    )

    with patch("app.agent.httpx.post") as mocked_post:
        result = approve_promotion.func(
            promotion_id="P-101",
            runtime=runtime
        )

        mocked_post.assert_not_called()

    assert "Approval blocked" in result


def test_confirmation_for_another_promotion_is_blocked():
    runtime = SimpleNamespace(
        context=AuthContext(
            token="admin-demo-token",
            approved_promotion_id="P-102"
        )
    )

    with patch("app.agent.httpx.post") as mocked_post:
        result = approve_promotion.func(
            promotion_id="P-101",
            runtime=runtime
        )

        mocked_post.assert_not_called()

    assert "Approval blocked" in result


def test_confirmed_approval_reaches_api():
    runtime = SimpleNamespace(
        context=AuthContext(
            token="admin-demo-token",
            approved_promotion_id="P-101"
        )
    )

    with patch("app.agent.httpx.post") as mocked_post:
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.json.return_value = {
            "message": "Promotion approved"
        }

        result = approve_promotion.func(
            promotion_id="P-101",
            runtime=runtime
        )

        mocked_post.assert_called_once()

    assert "Promotion approved" in result
