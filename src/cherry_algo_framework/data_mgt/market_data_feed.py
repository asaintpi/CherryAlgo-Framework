from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Optional, Union, List, Tuple
from datetime import datetime
import pandas as pd

from ..core.event import Event, EventType

class MarketDataFeed(ABC):
    def __init__(self):
        self.latest_symbol_data: Dict[str, Dict[str, Any]] = {}
        self.continue_backtest: bool = True

    @abstractmethod
    def stream_next(self) -> Generator[Event, None, None]:
        raise NotImplementedError("Should implement stream_next()")

    def get_latest_bar_value(self, symbol: str, val_type: str = 'close') -> Optional[Union[float, int]]:
        if symbol in self.latest_symbol_data:
            return self.latest_symbol_data[symbol].get(val_type)
        return None

    def get_latest_bar_datetime(self, symbol: str) -> Optional[datetime]:
        if symbol in self.latest_symbol_data:
            dt_val = self.latest_symbol_data[symbol].get('datetime')
            if isinstance(dt_val, datetime):
                return dt_val
            elif isinstance(dt_val, (str, pd.Timestamp)): # Handle pandas Timestamp if data is from there
                try:
                    return pd.to_datetime(dt_val).to_pydatetime()
                except ValueError:
                    return None
        return None
    
    def get_latest_bar_all_values(self, symbol: str) -> Optional[Dict[str, Any]]:
        if symbol in self.latest_symbol_data:
            return self.latest_symbol_data[symbol]
        return None

    def update_latest_symbol_data(self, symbol: str, data_row: Dict[str, Any]):
        self.latest_symbol_data[symbol] = data_row

    def stop_feed(self):
        self.continue_backtest = False

    def get_historical_data(self, 
                              symbols: List[str], 
                              start_date: Union[str, datetime], 
                              end_date: Union[str, datetime],
                              timeframe: str = '1d') -> Dict[str, pd.DataFrame]:
         
        raise NotImplementedError("Concrete data feeds should implement get_historical_data()")

    def get_snapshot(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
         
        snapshot = {}
        for sym in symbols:
            if sym in self.latest_symbol_data:
                snapshot[sym] = self.latest_symbol_data[sym]
        return snapshot
