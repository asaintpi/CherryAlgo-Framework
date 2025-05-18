# CherryAlgo-Framework Core Package
# This file makes 'cherry_algo_framework' a Python package.

__version__ = "0.2.0" 

from .utils.config_loader import app_config
from .utils.logging_setup import logger # Assuming logger is exposed from logging_setup

# Example: Make key components easily accessible (optional, once they are defined)
# from .core.event import Event, EventType
# from .backtester.engine import BacktestEngine # Placeholder
