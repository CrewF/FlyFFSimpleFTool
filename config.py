from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class KeyPressConfig:
    min_interval: int
    max_interval: int
    key: str
    key_code: int
    key_name: str

# Define available keys and their codes
DIGIT_KEYS: List[Tuple[str, int, str]] = [
    ('0', 48, 'Digit0'),
    ('1', 49, 'Digit1'),
    ('2', 50, 'Digit2'),
    ('3', 51, 'Digit3'),
    ('4', 52, 'Digit4'),
    ('5', 53, 'Digit5'),
    ('6', 54, 'Digit6'),
    ('7', 55, 'Digit7'),
    ('8', 56, 'Digit8'),
    ('9', 57, 'Digit9'),
]

FUNCTION_KEYS: List[Tuple[str, int, str]] = [
    ('F1', 112, 'F1'),
    ('F2', 113, 'F2'),
    ('F3', 114, 'F3'),
    ('F4', 115, 'F4'),
    ('F5', 116, 'F5'),
    ('F6', 117, 'F6'),
    ('F7', 118, 'F7'),
    ('F8', 119, 'F8'),
    ('F9', 120, 'F9'),
    ('F10', 121, 'F10'),
    ('F11', 122, 'F11'),
    ('F12', 123, 'F12'),
]

# Combine all available keys
AVAILABLE_KEYS = DIGIT_KEYS + FUNCTION_KEYS

def get_key_config(key_name: str) -> KeyPressConfig:
    """Get the key configuration for a given key name."""
    for key, code, name in AVAILABLE_KEYS:
        if key == key_name:
            return KeyPressConfig(
                min_interval=3,  # Default values
                max_interval=6,
                key=key,
                key_code=code,
                key_name=name
            )
    raise ValueError(f"Invalid key name: {key_name}") 