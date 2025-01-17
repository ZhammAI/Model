# backend/src/utils/helpers.py

from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import json
import base64
import hashlib
import asyncio
from decimal import Decimal

# Time and Date Helpers
def parse_timeframe(timeframe: str) -> timedelta:
    """Convert string timeframe to timedelta"""
    units = {
        "m": "minutes",
        "h": "hours",
        "d": "days",
        "w": "weeks"
    }
    
    value = int(timeframe[:-1])
    unit = timeframe[-1].lower()
    
    if unit not in units:
        raise ValueError(f"Invalid timeframe unit: {unit}")
        
    return timedelta(**{units[unit]: value})

def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    return timestamp.strftime(format_str)

def get_time_ranges(timeframe: str = "24h") -> Dict[str, datetime]:
    """Get start and end times for a given timeframe"""
    now = datetime.utcnow()
    delta = parse_timeframe(timeframe)
    
    return {
        "start": now - delta,
        "end": now
    }

# Number Formatting Helpers
def format_number(number: Union[int, float, Decimal], decimals: int = 2) -> str:
    """Format number with K, M, B suffixes"""
    if number is None:
        return "0"
        
    number = float(number)
    if abs(number) < 1000:
        return f"{number:.{decimals}f}"
        
    for unit in ["", "K", "M", "B", "T"]:
        if abs(number) < 1000:
            return f"{number:.{decimals}f}{unit}"
        number /= 1000
        
    return f"{number:.{decimals}f}T"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with sign"""
    return f"{'+' if value > 0 else ''}{value:.{decimals}f}%"

def format_price(price: float, max_decimals: int = 8) -> str:
    """Format price with appropriate decimal places"""
    if price is None:
        return "0"
        
    if price == 0:
        return "0"
        
    price_str = f"{price:.{max_decimals}f}"
    return price_str.rstrip("0").rstrip(".")

# Data Processing Helpers
def calculate_change(current: float, previous: float) -> float:
    """Calculate percentage change between two values"""
    if not previous:
        return 0
    return ((current - previous) / previous) * 100

def moving_average(data: List[float], window: int = 14) -> List[float]:
    """Calculate moving average for a list of values"""
    if len(data) < window:
        return data
        
    results = []
    for i in range(len(data) - window + 1):
        window_average = sum(data[i:i+window]) / window
        results.append(window_average)
    return results

def exponential_moving_average(data: List[float], window: int = 14) -> List[float]:
    """Calculate exponential moving average"""
    if len(data) < window:
        return data
        
    ema = [sum(data[:window]) / window]
    multiplier = 2 / (window + 1)
    
    for price in data[window:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

# Token and Address Helpers
def validate_solana_address(address: str) -> bool:
    """Validate Solana address format"""
    try:
        # Basic validation for base58 encoding and length
        decoded = base64.b58decode(address)
        return len(decoded) == 32
    except:
        return False

def generate_token_id(token_data: Dict[str, Any]) -> str:
    """Generate unique token identifier"""
    data_str = json.dumps(token_data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

# Cache Helpers
async def cache_with_ttl(redis_client, key: str, data: Any, ttl: int = 300):
    """Cache data with TTL"""
    await redis_client.setex(
        key,
        ttl,
        json.dumps(data, default=str)
    )

async def get_cached_data(redis_client, key: str) -> Optional[Any]:
    """Get cached data"""
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

# WebSocket Helpers
class WSConnectionManager:
    def __init__(self):
        self.active_connections: List = []
        
    async def connect(self, websocket: Any):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: Any):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

# Rate Limiting Helpers
class RateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.requests = {}
        
    async def check_limit(self, key: str) -> bool:
        now = datetime.utcnow().timestamp()
        self._cleanup(now)
        
        if key not in self.requests:
            self.requests[key] = []
            
        self.requests[key].append(now)
        return len(self.requests[key]) <= self.limit
        
    def _cleanup(self, now: float):
        cutoff = now - self.window
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            if not self.requests[key]:
                del self.requests[key]

# Error Handling Helpers
class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def handle_api_error(error: Exception) -> Dict:
    """Format error response"""
    if isinstance(error, APIError):
        return {
            "success": False,
            "error": error.message,
            "status_code": error.status_code
        }
    return {
        "success": False,
        "error": str(error),
        "status_code": 500
    }