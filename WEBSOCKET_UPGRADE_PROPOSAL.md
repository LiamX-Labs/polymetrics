# WebSocket Upgrade Proposal

## Current Implementation ✅
The tracker now works correctly using:
- **Endpoint:** `GET /events` (Gamma API)
- **Method:** HTTP polling every 15 seconds
- **Filtering:** Slug pattern matching (`btc-updown-{timeframe}-{timestamp}`)

## Proposed Upgrade: WebSocket Integration

### WebSocket Endpoint
```
wss://ws-live-data.polymarket.com
```

### Benefits

#### 1. Real-Time Market Detection
- **Current:** Polls every 15 seconds, could miss markets or detect them late
- **With WebSocket:** Instant notification when new BTC updown markets are created

#### 2. Precise 80% Trigger Timing
- **Current:** Check market progress every 15 seconds (may miss exact 80% mark)
- **With WebSocket:** Subscribe to market time updates or price feeds for precise timing

#### 3. Lower API Usage
- **Current:** 4 API calls per minute (240/hour) even when no markets exist
- **With WebSocket:** Single persistent connection, only receive data when events occur

#### 4. Better Position Tracking
- **Current:** Must poll CLOB API at 80% mark for positions
- **With WebSocket:** Could track positions in real-time throughout market lifecycle

### Implementation Plan

#### Phase 1: WebSocket Client
Create `scripts/tracker/websocket_client.py`:
```python
import asyncio
import websockets
import json

class PolymarketWebSocket:
    def __init__(self, url="wss://ws-live-data.polymarket.com"):
        self.url = url
        self.connection = None

    async def connect(self):
        self.connection = await websockets.connect(self.url)

    async def subscribe_to_markets(self):
        # Subscribe to market creation events
        # Subscribe to BTC updown markets specifically
        pass

    async def listen(self, callback):
        async for message in self.connection:
            data = json.loads(message)
            await callback(data)
```

#### Phase 2: Hybrid Approach
Combine WebSocket with polling:
1. **WebSocket:** Listen for new market creations
2. **Polling:** Continue checking market progress for 80% trigger
3. **CLOB API:** Fetch positions at trigger time (unchanged)

#### Phase 3: Full WebSocket
Replace all polling with WebSocket subscriptions:
1. Market creation events
2. Market time progress
3. Position updates (if available)

### Documentation Needed

From Polymarket docs, we need to understand:
- [ ] WebSocket authentication requirements
- [ ] Available subscription channels
- [ ] Message format for market events
- [ ] Rate limits for WebSocket connections
- [ ] Reconnection handling

### Next Steps

1. **Research WebSocket API:**
   ```bash
   # Check Polymarket docs
   curl https://docs.polymarket.com/llms.txt | grep -i websocket
   ```

2. **Test Connection:**
   ```python
   import websockets
   import asyncio

   async def test():
       async with websockets.connect("wss://ws-live-data.polymarket.com") as ws:
           message = await ws.recv()
           print(f"Received: {message}")

   asyncio.run(test())
   ```

3. **Implement Basic WebSocket Client**

4. **Integrate with Existing Tracker**

5. **Compare Performance**
   - Polling: 15s average detection delay
   - WebSocket: <1s detection delay

### Compatibility Note

Current slug-based optimization will still be useful for:
- Initial market loading on startup
- Fallback if WebSocket connection fails
- Historical market analysis

## Recommendation

Implement **Phase 2 (Hybrid Approach)** first:
- Keep the working REST API polling as fallback
- Add WebSocket for instant new market detection
- Maintain current 80% trigger logic
- Easy to roll back if issues occur

This gives us the best of both worlds while minimizing risk.
