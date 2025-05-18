from enum import Enum
from typing import Any, Dict, Optional

class EventType(Enum):
    MARKET = 1          # New market data (e.g., bar, tick)
    SIGNAL = 2          # Strategy generated signal (e.g., BUY, SELL, HOLD)
    ORDER = 3           # Order request to the broker (e.g., MARKET, LIMIT)
    FILL = 4            # Order execution confirmation
    PORTFOLIO_UPDATE = 5 # Change in portfolio state (e.g., after a fill)
    RISK_ASSESSMENT = 6 # Request for risk assessment or its result
    SYSTEM_HEARTBEAT = 7 # Periodic event for time-based actions
    BACKTEST_COMPLETE = 8 # Signals end of backtest
    STRATEGY_PARAM_UPDATE = 9 # For dynamic strategy adjustments

class Event:
    def __init__(self, event_type: EventType, data: Optional[Dict[str, Any]] = None):
        self.type: EventType = event_type
        self.data: Dict[str, Any] = data if data is not None else {}
 
    def __str__(self) -> str:
        return f"Event(type={self.type.name}, data={self.data})"

# Example Usage (typically not here, but for understanding)
# if __name__ == '__main__':
#     market_event_data = {'ticker': 'AAPL', 'price': 150.00, 'volume': 100000}
#     market_event = Event(EventType.MARKET, market_event_data)
#     print(market_event)

#     signal_event_data = {'ticker': 'AAPL', 'signal_type': 'BUY', 'strength': 0.75}
#     signal_event = Event(EventType.SIGNAL, signal_event_data)
#     print(signal_event)
