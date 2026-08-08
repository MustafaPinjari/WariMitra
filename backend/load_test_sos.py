"""
Load Test for SOS Endpoint with DDoS Protections
Phase 1.2 Implementation: Load Testing

This load test uses Django's test client to simulate 1000+ requests/second
to verify the SOS endpoint can handle sustained load with DDoS protections.

Usage:
    python manage.py shell < load_test_sos.py
    
Or as a management command:
    python manage.py loadtest_sos

Test Goals:
- Simulate 1000 requests/second sustained
- Verify rate limiting works under load
- Verify geofence validation performance
- Verify device fingerprinting works at scale
- Monitor response times
"""

import time
import threading
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import connections
from rest_framework.test import APIClient
import statistics
import json

User = get_user_model()


class LoadTestRunner:
    """Load test runner for SOS endpoint"""
    
    def __init__(self, num_threads=100, requests_per_thread=10, duration_seconds=60):
        """
        Initialize load test.
        
        Args:
            num_threads: Number of concurrent threads
            requests_per_thread: Requests per thread
            duration_seconds: How long to run test
        """
        self.num_threads = num_threads
        self.requests_per_thread = requests_per_thread
        self.duration_seconds = duration_seconds
        
        # Metrics
        self.response_times = []
        self.status_codes = {}
        self.errors = []
        self.total_requests = 0
        self.total_success = 0
        self.total_rate_limited = 0
        self.total_errors = 0
        
        self.lock = threading.Lock()
    
    def setup(self):
        """Setup test environment"""
        print("\n=== SOS Load Test Setup ===")
        print(f"Threads: {self.num_threads}")
        print(f"Requests per thread: {self.requests_per_thread}")
        print(f"Total requests: {self.num_threads * self.requests_per_thread}")
        print(f"Duration: {self.duration_seconds}s")
        
        # Create test user
        try:
            self.user = User.objects.create_user(
                username='loadtest_user',
                email='loadtest@test.com',
                password='testpass123',
                user_type='pilgrim'
            )
            print(f"Created test user: {self.user.username}")
        except:
            self.user = User.objects.get(username='loadtest_user')
            print(f"Using existing test user: {self.user.username}")
        
        print("\n=== Starting Load Test ===\n")
    
    def make_request(self, thread_id, request_num):
        """Make a single SOS request"""
        try:
            client = APIClient()
            client.force_authenticate(user=self.user)
            
            # Generate unique fingerprint per thread
            fingerprint = f"loadtest_{thread_id}_{request_num}_" + "a" * 44
            
            # Use different cities for variety
            cities = [
                {"latitude": 28.6139, "longitude": 77.2090},  # Delhi
                {"latitude": 19.0760, "longitude": 72.8777},  # Mumbai
                {"latitude": 12.9716, "longitude": 77.5946},  # Bangalore
                {"latitude": 22.5726, "longitude": 88.3639},  # Kolkata
            ]
            location = cities[request_num % len(cities)]
            
            start_time = time.time()
            
            response = client.post(
                reverse('sos-list'),
                {
                    **location,
                    "radius": 1000,
                    "device_fingerprint": fingerprint,
                    "device_model": f"Device_{thread_id}",
                    "app_version": "1.0.0",
                },
                format='json'
            )
            
            elapsed = time.time() - start_time
            
            with self.lock:
                self.response_times.append(elapsed * 1000)  # Convert to ms
                
                status_code = response.status_code
                self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
                
                self.total_requests += 1
                
                if status_code == 201:
                    self.total_success += 1
                elif status_code == 429:
                    self.total_rate_limited += 1
                else:
                    self.total_errors += 1
            
            return True, status_code, elapsed
            
        except Exception as e:
            with self.lock:
                self.total_requests += 1
                self.total_errors += 1
                self.errors.append(str(e))
            return False, None, 0
    
    def worker_thread(self, thread_id):
        """Worker thread that makes multiple requests"""
        for request_num in range(self.requests_per_thread):
            self.make_request(thread_id, request_num)
            # Small delay between requests from same thread
            time.sleep(0.01)
    
    def run(self):
        """Run the load test"""
        start_time = time.time()
        
        # Create and start worker threads
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self.worker_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        self.print_results(elapsed)
    
    def print_results(self, elapsed_time):
        """Print test results"""
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        
        print(f"\nDuration: {elapsed_time:.2f} seconds")
        print(f"Total Requests: {self.total_requests}")
        print(f"Requests/Second: {self.total_requests / elapsed_time:.2f}")
        
        print(f"\nResponse Distribution:")
        print(f"  201 Created: {self.total_success} ({100*self.total_success/self.total_requests:.1f}%)")
        print(f"  429 Rate Limited: {self.total_rate_limited} ({100*self.total_rate_limited/self.total_requests:.1f}%)")
        print(f"  Other/Errors: {self.total_errors} ({100*self.total_errors/self.total_requests:.1f}%)")
        
        if self.response_times:
            print(f"\nResponse Time Statistics (ms):")
            print(f"  Min: {min(self.response_times):.2f}")
            print(f"  Max: {max(self.response_times):.2f}")
            print(f"  Mean: {statistics.mean(self.response_times):.2f}")
            print(f"  Median: {statistics.median(self.response_times):.2f}")
            print(f"  StdDev: {statistics.stdev(self.response_times):.2f}" if len(self.response_times) > 1 else "")
            
            # Calculate percentiles
            sorted_times = sorted(self.response_times)
            p50 = sorted_times[int(0.50 * len(sorted_times))]
            p95 = sorted_times[int(0.95 * len(sorted_times))]
            p99 = sorted_times[int(0.99 * len(sorted_times))]
            print(f"  P50: {p50:.2f}")
            print(f"  P95: {p95:.2f}")
            print(f"  P99: {p99:.2f}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:5]:  # Show first 5
                print(f"  - {error}")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60 + "\n")


# Run the load test
if __name__ == "__main__":
    runner = LoadTestRunner(
        num_threads=50,
        requests_per_thread=20,
        duration_seconds=60
    )
    
    runner.setup()
    runner.run()
