#!/usr/bin/env python3
"""
K6 Options Configuration Script
"""

import json

def generate_k6_options():
    """Generate K6 options configuration"""
    
    options = {
        "vus": 10,
        "duration": "30s",
        "thresholds": {
            "http_req_duration": ["p(95)<500"],
            "http_req_failed": ["rate<0.1"]
        },
        "ext": {
            "loadimpact": {
                "distribution": {
                    "amazon:us:ashburn": {"loadZone": "amazon:us:ashburn", "percent": 100}
                }
            }
        }
    }
    
    return options

if __name__ == "__main__":
    options = generate_k6_options()
    print(json.dumps(options, indent=2))
