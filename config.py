"""
Configuration module for the Autonomous Trading System.
Centralizes all configurable parameters with type hints and validation.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

class TradingMode(Enum):
    """Defines the operational modes of the trading system."""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"

@dataclass
class TradingConfig:
    """Main configuration container with validation."""
    
    # Exchange Configuration
    exchange_id: str = "binance"
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    
    # RL Training Parameters
    initial_balance: float = 10000.0
    position_size: float = 0.1  # 10% of balance per trade
    max_position_size: float = 0.3  # Max 30% of balance
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.05  # 5% take profit
    commission_pct: float = 0.001  # 0.1% trading fee
    
    # Environment Parameters
    window_size: int = 50  # Lookback window for state
    observation_features: List[str] = field(default_factory=lambda: [
        'close', 'volume', 'rsi', 'macd', 'bb_upper', 'bb_lower',
        'atr', 'vwap', 'ema_20', 'ema_50'
    ])
    
    # Agent Training
    total_timesteps: int = 100000
    learning_rate: float = 0.0003
    gamma: float = 0.99  # Discount factor
    batch_size: int = 64
    buffer_size: int = 100000
    
    # System
    mode: TradingMode = TradingMode.PAPER
    log_level: int = logging.INFO
    checkpoint_freq: int = 10000  # Save model every N steps
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.initial_balance <= 0:
            raise ValueError("Initial balance must be positive")
        if not 0 < self.position_size <= self.max_position_size <= 1:
            raise ValueError("Invalid position size constraints")
        if self.stop_loss_pct <= 0:
            raise ValueError("Stop loss percentage must be positive")
        if self.window_size < 10:
            raise ValueError("Window size too small for meaningful analysis")
            
    def get_firebase_collections(self) -> Dict[str, str]:
        """Return Firebase collection names."""
        return {
            'trades': f"{self.exchange_id}_{self.symbol.replace('/', '_')}_trades",
            'metrics': f"{self.exchange_id}_{self.symbol.replace('/', '_')}_metrics",
            'models': f"{self.exchange_id}_{self.symbol.replace('/', '_')}_models",
            'errors': f"{self.exchange_id}_{self.symbol.replace('/', '_')}_errors"
        }

# Global configuration instance
config = TradingConfig()

def load_env_config() -> None:
    """Load configuration from environment variables."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if os.getenv('TRADING_MODE'):
        config.mode = TradingMode(os.getenv('TRADING_MODE').lower())
    if os.getenv('INITIAL_BALANCE'):
        config.initial_balance = float(os.getenv('INITIAL_BALANCE'))
    if os.getenv('LOG_LEVEL'):
        config.log_level = getattr(logging, os.getenv('LOG_LEVEL').upper())