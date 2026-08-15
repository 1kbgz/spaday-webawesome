import asyncio
import logging

import transports
import uvicorn
from pydantic import BaseModel
from spaday import CallEndpoint, Sequence, SetProp, Toggle, by_id, element, field, obj
from spaday.backends.starlette import serve
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute

from spaday_webawesome import (
    Tabs,
    WaBadge,
    WaButton,
    WaCallout,
    WaCard,
    WaDivider,
    WaInput,
    WaOption,
    WaProgressRing,
    WaSelect,
    WaSwitch,
    package,
)

logger = logging.getLogger("uvicorn.error")


class OverviewFeed(BaseModel):
    active_sessions: str = "1,284"
    session_trend: str = "+8%"
    requests_today: str = "48.2k"
    capacity: int = 72
    capacity_label: str = "72%"


overview_feed = OverviewFeed()
session = transports.Session()
session.host(overview_feed)
server = transports.Server(session)


async def update_overview() -> None:
    tick = 0
    while True:
        await asyncio.sleep(2)
        tick += 1
        capacity = 62 + (tick * 7) % 29
        overview_feed.active_sessions = f"{1_284 + tick * 17:,}"
        overview_feed.session_trend = f"+{8 + tick % 5}%"
        overview_feed.requests_today = f"{48.2 + tick * 0.3:.1f}k"
        overview_feed.capacity = capacity
        overview_feed.capacity_label = f"{capacity}%"


async def preview_order(request):
    order = await request.json()
    logger.info("Preview order received from browser: %s", order)
    order_type = "limit" if order["limit_order"] else "market"
    return JSONResponse({"message": f"Previewed {order['quantity']} {order['symbol']} shares ({order['side']} {order_type} order)"})


details = element(
    "section",
    WaCallout(
        element("strong").text("All systems operational"),
        element("span").text(" Browser assets are loaded from the local WebAwesome peer package."),
        id="details",
        variant="success",
        appearance="outlined",
    ),
    WaButton(appearance="outlined").text("Toggle system details").on("click", Toggle(by_id("details"), "hidden")),
    class_="details-panel",
)

order_form = element(
    "section",
    element(
        "div",
        WaInput(label="Symbol", value="AAPL", hint="US-listed ticker", with_clear=True).bind("value", "symbol", mode="two-way"),
        WaSelect(
            WaOption(value="buy").text("Buy"),
            WaOption(value="sell").text("Sell"),
            label="Side",
            hint="Order direction",
            value="buy",
        ).bind("value", "side", mode="two-way"),
        WaInput(label="Quantity", hint="Whole shares", type="number", value="100", min=1, step=1).bind("value", "quantity", mode="two-way"),
        class_="form-grid",
    ),
    element(
        "div",
        WaSwitch(checked=True, hint="Submit as a limit order", with_hint=True).text("Limit order").bind("checked", "limit_order", mode="two-way"),
        WaButton(variant="brand", appearance="filled", size="large")
        .text("Preview order")
        .on(
            "click",
            Sequence(
                CallEndpoint(
                    "POST",
                    "/api/orders/preview",
                    obj(
                        {
                            "symbol": field("symbol"),
                            "side": field("side"),
                            "quantity": field("quantity"),
                            "limit_order": field("limit_order"),
                        }
                    ),
                    result="preview",
                ),
                SetProp(by_id("order-preview"), "hidden", False),
            ),
        ),
        class_="form-actions",
    ),
    WaCallout(id="order-preview", variant="brand", appearance="outlined", hidden=True).compute("textContent", field("preview.body.message")),
    class_="order-form",
)

overview = element(
    "section",
    element(
        "div",
        element(
            "article",
            element("span").text("Active sessions"),
            element("strong").bind("textContent", "active_sessions"),
            WaBadge(variant="success").bind("textContent", "session_trend"),
        ),
        element(
            "article",
            element("span").text("Requests today"),
            element("strong").bind("textContent", "requests_today"),
            WaBadge(variant="brand").text("Live"),
        ),
        element(
            "article",
            element("div", element("span").text("Capacity"), element("strong").bind("textContent", "capacity_label")),
            WaProgressRing(value=72, label="Capacity used").bind("value", "capacity").bind("textContent", "capacity_label"),
            class_="capacity",
        ),
        class_="metrics",
    ),
    WaDivider(),
    details,
)

page = element(
    "main",
    element("p", class_="eyebrow").text("COMPONENT SHOWCASE"),
    element("h1").text("WebAwesome operations console"),
    element("p", class_="lede").text("Typed components, polished browser assets, and serializable interactions."),
    WaCard(
        element(
            "header",
            element("div", element("h2").text("Account activity"), element("p").text("Updated a few seconds ago")),
            WaBadge(variant="success", pill=True, attention="pulse").text("Connected"),
            class_="card-header",
        ),
        Tabs(active="overview").tab("Overview", overview).tab("Order controls", order_form),
        appearance="outlined",
        class_="console-card",
    ),
    class_="page",
)

styles = """
<style>
  body { margin: 0; min-height: 100vh; background: radial-gradient(circle at top left, #dbeafe, transparent 34%), #f8fafc;
    color: #172033; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
  .page { box-sizing: border-box; max-width: 64rem; margin: 0 auto; padding: 3.5rem 1.25rem; }
  .eyebrow { margin: 0; color: #2563eb; font-size: .75rem; font-weight: 800; letter-spacing: .16em; }
  h1 { margin: .35rem 0 0; font-size: clamp(2rem, 5vw, 3.25rem); letter-spacing: -.04em; }
  .lede { margin: .6rem 0 2rem; color: #64748b; font-size: 1.05rem; }
  .console-card { display: block; --wa-border-radius-l: 1.25rem; box-shadow: 0 22px 55px rgba(15,23,42,.1); }
  .card-header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }
  .card-header h2 { margin: 0; font-size: 1.25rem; } .card-header p { margin: .25rem 0 0; color: #64748b; }
  .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: .85rem; padding-block: 1rem; }
  .metrics article { min-height: 6.25rem; box-sizing: border-box; padding: 1rem; border: 1px solid #e2e8f0; border-radius: .85rem; background: #f8fafc; }
  .metrics span { display: block; color: #64748b; font-size: .78rem; } .metrics strong { display: block; margin: .35rem 0 .65rem; font-size: 1.5rem; }
  .capacity { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
  .capacity wa-progress-ring { --size: 3.5rem; --track-width: .35rem; font-size: .7rem; font-weight: 800; }
  .details-panel { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding-top: 1.25rem; }
  .details-panel wa-callout { flex: 1; }
  .order-form { display: grid; gap: 1.5rem; padding: 1.25rem .15rem .5rem; }
  .form-grid { display: grid; grid-template-columns: 1.25fr 1fr 1fr; gap: 1.25rem; align-items: end; }
  .form-actions { display: flex; align-items: center; justify-content: space-between; gap: 2rem; padding-top: .35rem; }
  .form-actions wa-button { margin-left: auto; min-width: 10rem; }
  @media (max-width: 720px) { .page { padding: 1.5rem .75rem; } .metrics, .form-grid { grid-template-columns: 1fr; }
    .details-panel, .form-actions { align-items: stretch; flex-direction: column; } .form-actions wa-button { margin-left: 0; } }
</style>
"""

app = serve(
    page,
    packages=[package],
    wire="transports",
    routes=[
        WebSocketRoute("/ws", transports.ws_endpoint(server)),
        Route("/api/orders/preview", preview_order, methods=["POST"]),
    ],
    background=[transports.autosync(server), update_overview()],
    store={
        "symbol": "AAPL",
        "side": "buy",
        "quantity": "100",
        "limit_order": True,
        "preview": {"body": {"message": "Waiting for server preview"}},
    },
    head=styles,
    title="spaday-webawesome example",
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8012)
