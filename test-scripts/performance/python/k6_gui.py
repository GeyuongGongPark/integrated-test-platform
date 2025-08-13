#!/usr/bin/env python3
"""
K6 GUI Configuration Script
"""

import json
import os

def generate_k6_config(test_name, vus=10, duration="30s"):
    """Generate K6 configuration for GUI mode"""
    
    config = {
        "scenarios": {
            test_name: {
                "executor": "ramping-vus",
                "startVUs": 0,
                "stages": [
                    {"duration": "10s", "target": vus},
                    {"duration": duration, "target": vus},
                    {"duration": "10s", "target": 0}
                ]
            }
        },
        "options": {
            "ext": {
                "loadimpact": {
                    "distribution": {
                        "amazon:us:ashburn": {"loadZone": "amazon:us:ashburn", "percent": 100}
                    }
                }
            }
        }
    }
    
    return config

if __name__ == "__main__":
    config = generate_k6_config("performance_test")
    print(json.dumps(config, indent=2))
