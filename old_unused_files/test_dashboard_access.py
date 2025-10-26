#!/usr/bin/env python3
"""
Test Dashboard Access
Verify all dashboard URLs are working
"""

import requests
import time

def test_dashboard_access():
    """Test all dashboard access URLs"""
    print("🧪 Testing Dashboard Access")
    print("=" * 40)
    
    urls = [
        "http://localhost:5000",
        "http://127.0.0.1:5000", 
        "http://192.168.1.183:5000"
    ]
    
    for url in urls:
        print(f"\n🔍 Testing: {url}")
        try:
            # Test health endpoint
            health_response = requests.get(f"{url}/api/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health API: {health_data}")
            else:
                print(f"❌ Health API: Status {health_response.status_code}")
                
            # Test signals endpoint
            signals_response = requests.get(f"{url}/api/signals", timeout=5)
            if signals_response.status_code == 200:
                signals_data = signals_response.json()
                print(f"✅ Signals API: {len(signals_data)} signals loaded")
            else:
                print(f"❌ Signals API: Status {signals_response.status_code}")
                
            # Test main page
            main_response = requests.get(url, timeout=5)
            if main_response.status_code == 200:
                if "Yahoo Finance Trading Dashboard" in main_response.text:
                    print(f"✅ Main Page: Dashboard loaded correctly")
                else:
                    print(f"❌ Main Page: Wrong content")
            else:
                print(f"❌ Main Page: Status {main_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Cannot reach {url}")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout: {url} not responding")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📱 Dashboard Access URLs:")
    print(f"   • Local: http://localhost:5000")
    print(f"   • Network: http://192.168.1.183:5000")
    print(f"   • Alternative: http://127.0.0.1:5000")

if __name__ == "__main__":
    test_dashboard_access()
