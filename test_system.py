#!/usr/bin/env python3
"""
Test script to verify the e-commerce analytics system is working correctly.
"""

import psycopg2
import requests
import time

def test_database_connection():
    """Test database connection and basic queries."""
    print("🔍 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            dbname="customer_events",
            user="postgres",
            password="Rp123456",
            host="localhost",
            port="5432"
        )
        
        cur = conn.cursor()
        
        # Test basic queries
        cur.execute("SELECT COUNT(*) FROM events")
        total_events = cur.fetchone()[0]
        print(f"✅ Total events in database: {total_events:,}")
        
        cur.execute("SELECT COUNT(*) FROM customers")
        total_customers = cur.fetchone()[0]
        print(f"✅ Total customers in database: {total_customers}")
        
        cur.execute("SELECT COUNT(*) FROM products")
        total_products = cur.fetchone()[0]
        print(f"✅ Total products in database: {total_products}")
        
        # Test revenue calculation
        cur.execute("""
            SELECT 
                COUNT(DISTINCT customer_id) as customers_with_purchases,
                COUNT(*) as total_purchases
            FROM events 
            WHERE action = 'purchase_cart'
        """)
        result = cur.fetchone()
        customers_with_purchases, total_purchases = result
        print(f"✅ Customers with purchases: {customers_with_purchases}")
        print(f"✅ Total purchase events: {total_purchases}")
        
        # Test action distribution
        cur.execute("""
            SELECT action, COUNT(*) 
            FROM events 
            GROUP BY action 
            ORDER BY COUNT(*) DESC
        """)
        actions = cur.fetchall()
        print("✅ Action distribution:")
        for action, count in actions:
            print(f"   - {action}: {count:,}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_dashboard_access():
    """Test if the dashboard is accessible."""
    print("\n🔍 Testing dashboard access...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is accessible at http://localhost:8501")
            return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard is not accessible: {e}")
        return False

def test_websocket_server():
    """Test if the WebSocket server is running."""
    print("\n🔍 Testing WebSocket server...")
    
    try:
        response = requests.get("http://localhost:8765", timeout=5)
        print("✅ WebSocket server is running on port 8765")
        return True
    except requests.exceptions.RequestException:
        print("❌ WebSocket server is not accessible")
        return False

def test_data_generation():
    """Test if data is being generated in real-time."""
    print("\n🔍 Testing real-time data generation...")
    
    try:
        conn = psycopg2.connect(
            dbname="customer_events",
            user="postgres",
            password="Rp123456",
            host="localhost",
            port="5432"
        )
        
        cur = conn.cursor()
        
        # Get initial count
        cur.execute("SELECT COUNT(*) FROM events")
        initial_count = cur.fetchone()[0]
        print(f"Initial event count: {initial_count:,}")
        
        # Wait 10 seconds
        print("Waiting 10 seconds for new events...")
        time.sleep(10)
        
        # Get final count
        cur.execute("SELECT COUNT(*) FROM events")
        final_count = cur.fetchone()[0]
        print(f"Final event count: {final_count:,}")
        
        new_events = final_count - initial_count
        if new_events > 0:
            print(f"✅ {new_events:,} new events generated in 10 seconds")
            return True
        else:
            print("❌ No new events generated")
            return False
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing data generation: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting E-commerce Analytics System Tests\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Dashboard Access", test_dashboard_access),
        ("WebSocket Server", test_websocket_server),
        ("Data Generation", test_data_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main() 