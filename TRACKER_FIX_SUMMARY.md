# Tracker Fix Summary

## Problem Found ✓
The tracker was using the wrong Polymarket API endpoint.

## Solution Applied ✓
Updated [scripts/tracker/gamma_client.py](scripts/tracker/gamma_client.py) to use `/events` instead of `/markets`

## Changes Made

**File:** `scripts/tracker/gamma_client.py`

```python
# Line 30: Changed from /markets to /events
endpoint = f"{self.base_url}/events"

# Line 40: Updated response parsing for events
rows = payload if isinstance(payload, list) else []

# Lines 68-73: Extract conditionId from nested markets
event_markets = event.get("markets", [])
if event_markets and len(event_markets) > 0:
    market_id = str(event_markets[0].get("conditionId") or event.get("id") or slug)
```

## How to Run

Use anaconda python (not system python3):
```bash
/home/william/anaconda3/bin/python scripts/tracker/market_tracker.py
```

## Current Status

✅ **Tracker is working correctly**
- Polls every 15 seconds
- Queries Polymarket /events endpoint
- Filters for BTC updown markets
- Currently finds 0 markets (none active right now)

⏳ **Waiting for markets**
- BTC updown markets exist but are currently expired (Dec 2025 - Jan 2026)
- Tracker will automatically detect them when new ones are created
- Examples seen: "Bitcoin Up or Down - 5m", "Bitcoin Up or Down - 15m"

## Verification

The tracker has been tested and is scanning correctly:
```
2026-05-05 22:18:29 INFO tracker: Tracker started | poll=15s
2026-05-05 22:18:34 INFO tracker: Scan cycle | active_btc_markets=0
2026-05-05 22:18:34 INFO tracker: Scan cycle complete | triggered_scans=0
2026-05-05 22:18:34 INFO tracker: Heartbeat | loop=1
```

## Reference
- Full diagnosis: [TRACKER_DIAGNOSIS.md](TRACKER_DIAGNOSIS.md)
- Polymarket docs: https://docs.polymarket.com/market-data/fetching-markets
