import asyncio

import httpx
import pytest

from spaday_webawesome import example


async def request(method: str, path: str, **kwargs):
    transport = httpx.ASGITransport(app=example.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://example") as client:
        return await client.request(method, path, **kwargs)


def test_example_serves_console_updates_metrics_and_previews_orders(monkeypatch):
    response = asyncio.run(request("GET", "/tree.json"))
    assert response.status_code == 200
    assert "wa-card" in response.text

    initial_sessions = example.overview_feed.active_sessions
    sleeps = 0

    class StreamComplete(Exception):
        pass

    async def one_tick(_delay):
        nonlocal sleeps
        sleeps += 1
        if sleeps > 1:
            raise StreamComplete

    monkeypatch.setattr(example.asyncio, "sleep", one_tick)
    with pytest.raises(StreamComplete):
        asyncio.run(example.update_overview())
    assert example.overview_feed.active_sessions != initial_sessions

    response = asyncio.run(
        request(
            "POST",
            "/api/orders/preview",
            json={"symbol": "MSFT", "side": "buy", "quantity": "25", "limit_order": True},
        )
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Previewed 25 MSFT shares (buy limit order)"}
