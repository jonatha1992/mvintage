"""Tests de seguridad: cierre de endpoints de debug públicos y rate limiting."""

from app.core.rate_limit import InMemoryRateLimiter


def test_public_debug_endpoints_return_404(client):
    for path in (
        "/debug/auth",
        "/debug/dump",
        "/api/v1/users/test-auth",
        "/api/v1/users/test-firebase",
    ):
        response = client.get(path)
        assert response.status_code == 404, f"{path} respondió {response.status_code}"


def test_rate_limiter_sliding_window():
    now = [100.0]
    limiter = InMemoryRateLimiter(clock=lambda: now[0])

    assert limiter.check("scope", "1.2.3.4", limit=2, window_seconds=60) == (True, 0)
    assert limiter.check("scope", "1.2.3.4", limit=2, window_seconds=60) == (True, 0)
    allowed, retry_after = limiter.check("scope", "1.2.3.4", limit=2, window_seconds=60)
    assert allowed is False
    assert retry_after == 60

    # Otra IP no se ve afectada
    assert limiter.check("scope", "5.6.7.8", limit=2, window_seconds=60) == (True, 0)

    # Al vencer la ventana vuelve a permitir
    now[0] += 61.0
    assert limiter.check("scope", "1.2.3.4", limit=2, window_seconds=60) == (True, 0)


def test_rate_limit_on_auth_me_returns_429_in_spanish(client, auth_cookie):
    headers = {**auth_cookie, "X-Forwarded-For": "203.0.113.10"}
    for _ in range(30):
        resp = client.get("/api/v1/users/me", headers=headers)
        assert resp.status_code == 200

    blocked = client.get("/api/v1/users/me", headers=headers)
    assert blocked.status_code == 429
    assert "Demasiadas solicitudes" in blocked.json()["detail"]
    assert int(blocked.headers["Retry-After"]) >= 1


def test_rate_limit_on_create_order_returns_429_in_spanish(client, auth_cookie):
    headers = {**auth_cookie, "X-Forwarded-For": "203.0.113.11"}
    payload = {"customer_id": 999999, "total": 100.0, "delivery_method": "retiro_local"}
    for _ in range(10):
        resp = client.post("/api/v1/orders/", json=payload, headers=headers)
        assert resp.status_code != 429

    blocked = client.post("/api/v1/orders/", json=payload, headers=headers)
    assert blocked.status_code == 429
    assert "Demasiadas solicitudes" in blocked.json()["detail"]
    assert int(blocked.headers["Retry-After"]) >= 1


def test_rate_limit_on_notify_created_returns_429_in_spanish(client, auth_cookie):
    headers = {**auth_cookie, "X-Forwarded-For": "203.0.113.12"}
    for _ in range(10):
        resp = client.post("/api/v1/orders/999999/notify-created", headers=headers)
        assert resp.status_code != 429

    blocked = client.post("/api/v1/orders/999999/notify-created", headers=headers)
    assert blocked.status_code == 429
    assert "Demasiadas solicitudes" in blocked.json()["detail"]
    assert int(blocked.headers["Retry-After"]) >= 1
