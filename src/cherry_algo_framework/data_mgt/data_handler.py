from datetime import datetime, timezone
from typing import Generator, Dict, Any, List, Union, Optional
import pandas as pd
from pathlib import Path

from ..core.event import Event, EventType
from .market_data_feed import MarketDataFeed
from ..utils.config_loader import app_config
from ..utils.logging_setup import logger  

class CSVDataHandler(MarketDataFeed):
    def __init__(self, csv_file_path: Union[str, Path], 
                 symbol_list: List[str], 
                 start_date: Optional[Union[str, datetime]] = None,
                 end_date: Optional[Union[str, datetime]] = None,
                 timeframe_column: str = 'datetime',
                 symbol_column: Optional[str] = None, # If CSV contains multiple symbols
                 price_column: str = 'close', # Default, but can be other columns
                 open_col: str = 'open', 
                 high_col: str = 'high', 
                 low_col: str = 'low', 
                 close_col: str = 'close', 
                 volume_col: str = 'volume'):
        
        super().__init__()
        self.csv_file_path = Path(csv_file_path)
        self.symbol_list = [s.upper() for s in symbol_list]  
        self.data_frames: Dict[str, pd.DataFrame] = {}
        self.data_iterators: Dict[str, Generator[pd.Series, None, None]] = {}
        
        self.timeframe_column = timeframe_column
        self.symbol_column = symbol_column
        self.price_column = price_column # 
        
        self.column_map = {
            'open': open_col,
            'high': high_col,
            'low': low_col,
            'close': close_col,
            'volume': volume_col
        }

        self.start_dt: Optional[datetime] = None
        if start_date:
            self.start_dt = pd.to_datetime(start_date, utc=True).to_pydatetime() if not isinstance(start_date, datetime) else start_date
            if self.start_dt.tzinfo is None: self.start_dt = self.start_dt.replace(tzinfo=timezone.utc)

        self.end_dt: Optional[datetime] = None
        if end_date:
            self.end_dt = pd.to_datetime(end_date, utc=True).to_pydatetime() if not isinstance(end_date, datetime) else end_date
            if self.end_dt.tzinfo is None: self.end_dt = self.end_dt.replace(tzinfo=timezone.utc)

        self._load_and_prepare_data()

    def _load_and_prepare_data(self):
        if not self.csv_file_path.exists():
            logger.error(f"CSV file not found: {self.csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")

        try:
            full_df = pd.read_csv(self.csv_file_path, header=0, parse_dates=[self.timeframe_column])
            
            if not isinstance(full_df[self.timeframe_column].dtype, pd.DatetimeTZDtype):
                 full_df[self.timeframe_column] = pd.to_datetime(full_df[self.timeframe_column], errors='coerce').dt.tz_localize('UTC')
            else:  
                 full_df[self.timeframe_column] = full_df[self.timeframe_column].dt.tz_convert('UTC')


            full_df.dropna(subset=[self.timeframe_column], inplace=True)
            full_df.set_index(self.timeframe_column, inplace=True)
            full_df.sort_index(inplace=True)

            if self.start_dt:
                full_df = full_df[full_df.index >= self.start_dt]
            if self.end_dt:
                full_df = full_df[full_df.index <= self.end_dt]
            
            if self.symbol_column:  
                if self.symbol_column not in full_df.columns:
                    raise ValueError(f"Symbol column '{self.symbol_column}' not found in CSV.")
                full_df[self.symbol_column] = full_df[self.symbol_column].str.upper()
                for symbol in self.symbol_list:
                    symbol_df = full_df[full_df[self.symbol_column] == symbol].copy()
                    if not symbol_df.empty:
                        self.data_frames[symbol] = symbol_df
                        self.data_iterators[symbol] = self._dataframe_to_generator(symbol_df)
                    else:
                        logger.warning(f"No data found for symbol '{symbol}' in {self.csv_file_path}")
            else:  
                if not self.symbol_list:
                    raise ValueError("Symbol list cannot be empty for single-symbol CSV.")
                symbol = self.symbol_list[0] 
                self.data_frames[symbol] = full_df.copy()
                self.data_iterators[symbol] = self._dataframe_to_generator(full_df)
                if len(self.symbol_list) > 1:
                    logger.warning(f"CSV '{self.csv_file_path}' treated as single-symbol data for '{symbol}'. Other symbols in list ignored for this file.")

        except Exception as e:
            logger.exception(f"Error loading or processing CSV file {self.csv_file_path}: {e}")
            raise

    def _dataframe_to_generator(self, df: pd.DataFrame) -> Generator[pd.Series, None, None]:
        for timestamp, row in df.iterrows():
            yield row  

    def stream_next(self) -> Generator[Event, None, None]:
        active_symbols = list(self.data_iterators.keys())
        
        current_bars: Dict[str, Optional[pd.Series]] = {symbol: None for symbol in active_symbols}
        current_timestamps: Dict[str, Optional[datetime]] = {symbol: None for symbol in active_symbols}

         
        for symbol in active_symbols:
            try:
                bar = next(self.data_iterators[symbol])
                current_bars[symbol] = bar
                current_timestamps[symbol] = bar.name.to_pydatetime() #  x
            except StopIteration:
                self.data_iterators.pop(symbol) # 
                logger.info(f"Data stream ended for symbol {symbol}.")
            except Exception as e:
                logger.exception(f"Error getting first bar for {symbol}: {e}")
                self.data_iterators.pop(symbol)

        while self.continue_backtest and self.data_iterators:
            #  
            earliest_symbol = None
            earliest_timestamp = None

            valid_timestamps = {s: ts for s, ts in current_timestamps.items() if ts is not None and s in self.data_iterators}
            if not valid_timestamps:  
                break

            earliest_symbol = min(valid_timestamps, key=valid_timestamps.get)
            earliest_timestamp = valid_timestamps[earliest_symbol]
            
            if earliest_symbol is None or earliest_timestamp is None:  
                break 

            bar_to_yield = current_bars[earliest_symbol]
            
            if bar_to_yield is None:  
                break

            event_data = {
                'symbol': earliest_symbol,
                'datetime': earliest_timestamp,  
                'open': bar_to_yield.get(self.column_map['open']),
                'high': bar_to_yield.get(self.column_map['high']),
                'low': bar_to_yield.get(self.column_map['low']),
                'close': bar_to_yield.get(self.column_map['close']),
                'volume': bar_to_yield.get(self.column_map['volume']),
                 
                **{col: bar_to_yield.get(col) for col in bar_to_yield.index if col not in self.column_map.values() and col != self.symbol_column}
            }
            
            self.update_latest_symbol_data(earliest_symbol, event_data)
            yield Event(EventType.MARKET, event_data)

            
            try:
                next_bar = next(self.data_iterators[earliest_symbol])
                current_bars[earliest_symbol] = next_bar
                current_timestamps[earliest_symbol] = next_bar.name.to_pydatetime()
            except StopIteration:
                self.data_iterators.pop(earliest_symbol)
                current_timestamps.pop(earliest_symbol, None)  
                logger.info(f"Data stream completed for symbol {earliest_symbol}.")
            except Exception as e:
                logger.exception(f"Error advancing iterator for {earliest_symbol}: {e}")
                self.data_iterators.pop(earliest_symbol)
                current_timestamps.pop(earliest_symbol, None)

        self.continue_backtest = False  
        logger.info("Market data stream finished for all symbols.")

    def get_historical_data(self, 
                              symbols: List[str], 
                              start_date: Union[str, datetime], 
                              end_date: Union[str, datetime],
                              timeframe: str = '1d') -> Dict[str, pd.DataFrame]:
         
        results = {}
        _start_dt = pd.to_datetime(start_date, utc=True) if not isinstance(start_date, datetime) else start_date
        if _start_dt.tzinfo is None: _start_dt = _start_dt.tz_localize('UTC')
        
        _end_dt = pd.to_datetime(end_date, utc=True) if not isinstance(end_date, datetime) else end_date
        if _end_dt.tzinfo is None: _end_dt = _end_dt.tz_localize('UTC')

        for symbol in symbols:
            symbol_upper = symbol.upper()
            if symbol_upper in self.data_frames:
                df_slice = self.data_frames[symbol_upper].loc[_start_dt:_end_dt]
                results[symbol_upper] = df_slice
            else:
                logger.warning(f"No historical data loaded for symbol '{symbol_upper}' to fulfill get_historical_data request.")
        return results
