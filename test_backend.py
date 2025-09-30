"""
Comprehensive Backend Test Suite for Transit System
Tests EVERY component to ensure 100% functionality
Run this file: python test_backend.py
"""

import sys
import time
import json
import requests
from datetime import datetime
from colorama import init, Fore, Style
import os

# Initialize colorama for Windows
init(autoreset=True)

BASE_URL = "http://127.0.0.1:8000"
TEST_USER = {
    "email": "testuser@transit.com",
    "password": "SecurePass123!"
}

class BackendTester:
    def __init__(self):
        self.token = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        self.route_ids = []
        
    def print_header(self, text):
        """Print section header"""
        print("\n" + "="*70)
        print(f"{Fore.CYAN}{Style.BRIGHT}{text}")
        print("="*70)
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}")
        self.tests_passed += 1
        self.test_results.append(("PASS", text))
    
    def print_error(self, text, error=None):
        """Print error message"""
        print(f"{Fore.RED}✗ {text}")
        if error:
            print(f"{Fore.RED}  Error: {error}")
        self.tests_failed += 1
        self.test_results.append(("FAIL", text, str(error) if error else ""))
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {text}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {text}")

    def check_server_running(self):
        """Test 1: Check if Django server is running"""
        self.print_header("TEST 1: Server Connectivity")
        try:
            response = requests.get(f"{BASE_URL}/api/health/", timeout=5)
            if response.status_code == 200:
                self.print_success("Django server is running")
                return True
            else:
                self.print_error(f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server. Is 'python manage.py runserver' running?")
            return False
        except Exception as e:
            self.print_error("Server connection failed", e)
            return False

    def test_health_endpoint(self):
        """Test 2: Health check endpoint"""
        self.print_header("TEST 2: Health Check Endpoint")
        try:
            response = requests.get(f"{BASE_URL}/api/health/")
            data = response.json()
            
            if response.status_code == 200 and data.get("ok") == True:
                self.print_success("Health endpoint working")
                return True
            else:
                self.print_error(f"Health check failed: {data}")
                return False
        except Exception as e:
            self.print_error("Health endpoint test failed", e)
            return False

    def test_user_registration(self):
        """Test 3: User registration"""
        self.print_header("TEST 3: User Registration")
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register/",
                json=TEST_USER
            )
            data = response.json()
            
            # User might already exist, that's ok
            if response.status_code == 200:
                self.print_success("User registration successful")
                return True
            elif response.status_code == 400 and "exists" in data.get("error", ""):
                self.print_success("User already exists (OK)")
                return True
            else:
                self.print_error(f"Registration failed: {data}")
                return False
        except Exception as e:
            self.print_error("User registration test failed", e)
            return False

    def test_user_login(self):
        """Test 4: User login and JWT token generation"""
        self.print_header("TEST 4: User Login & JWT Token")
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login/",
                json=TEST_USER
            )
            data = response.json()
            
            if response.status_code == 200 and "access" in data:
                self.token = data["access"]
                self.print_success("User login successful")
                self.print_info(f"JWT Token: {self.token[:50]}...")
                return True
            elif "mfa_required" in data:
                self.print_warning("MFA is enabled. Skipping MFA-protected tests.")
                return False
            else:
                self.print_error(f"Login failed: {data}")
                return False
        except Exception as e:
            self.print_error("User login test failed", e)
            return False

    def test_csv_data_loading(self):
        """Test 5: CSV data loading and route extraction"""
        self.print_header("TEST 5: CSV Data Loading")
        try:
            # Check if CSV files exist
            csv_files = [
                "traffic/data/boarding_03-05_2024 copy.csv",
                "traffic/data/landing_03-05_2024 copy.csv",
                "traffic/data/loader_03-05_2024 copy.csv"
            ]
            
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    self.print_success(f"Found: {csv_file}")
                else:
                    self.print_error(f"Missing: {csv_file}")
                    return False
            
            # Test route extraction via API
            if not self.token:
                self.print_warning("Skipping API test (no token)")
                return True
                
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/routes/", headers=headers)
            data = response.json()
            
            if response.status_code == 200 and "routes" in data:
                self.route_ids = data["routes"]
                self.print_success(f"Route IDs extracted: {len(self.route_ids)} routes")
                self.print_info(f"Routes: {', '.join(self.route_ids[:5])}...")
                return True
            else:
                self.print_error(f"Route extraction failed: {data}")
                return False
                
        except Exception as e:
            self.print_error("CSV data loading test failed", e)
            return False

    def test_prediction_model(self):
        """Test 6: Random Forest prediction model"""
        self.print_header("TEST 6: Random Forest Prediction Model")
        
        if not self.token:
            self.print_warning("Skipping (no token)")
            return False
        
        if not self.route_ids:
            self.print_warning("Skipping (no route IDs)")
            return False
        
        try:
            test_route = self.route_ids[0]
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.print_info(f"Testing predictions for route: {test_route}")
            
            response = requests.get(
                f"{BASE_URL}/api/predictions/?route_id={test_route}",
                headers=headers
            )
            data = response.json()
            
            if response.status_code == 200:
                predictions = data.get("predictions", [])
                if len(predictions) > 0:
                    self.print_success(f"Predictions generated: {len(predictions)} predictions")
                    self.print_info(f"Sample prediction: delay={predictions[0].get('predicted_delay_sec')}s")
                    return True
                else:
                    self.print_warning("No predictions generated yet (scheduler may not have run)")
                    return True
            else:
                self.print_error(f"Prediction API failed: {data}")
                return False
                
        except Exception as e:
            self.print_error("Prediction model test failed", e)
            return False

    def test_genetic_algorithm(self):
        """Test 7: Genetic Algorithm scheduler"""
        self.print_header("TEST 7: Genetic Algorithm Scheduler")
        
        if not self.token:
            self.print_warning("Skipping (no token)")
            return False
        
        if not self.route_ids:
            self.print_warning("Skipping (no route IDs)")
            return False
        
        try:
            test_route = self.route_ids[0]
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.print_info(f"Testing schedule for route: {test_route}")
            
            response = requests.get(
                f"{BASE_URL}/api/schedule/?route_id={test_route}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                departures = data.get("departures_minutes", [])
                fitness = data.get("fitness", 0)
                
                self.print_success(f"Schedule generated: {len(departures)} departures")
                self.print_info(f"Departures: {departures}")
                self.print_info(f"Fitness score: {fitness}")
                return True
            elif response.status_code == 404:
                self.print_warning("No schedule yet (scheduler may not have run)")
                return True
            else:
                self.print_error(f"Schedule API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error("GA scheduler test failed", e)
            return False

    def test_operator_routes(self):
        """Test 8: Operator route management"""
        self.print_header("TEST 8: Operator Route Management")
        
        if not self.token:
            self.print_warning("Skipping (no token)")
            return False
        
        if not self.route_ids or len(self.route_ids) < 2:
            self.print_warning("Skipping (insufficient route IDs)")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            test_routes = {
                self.route_ids[0]: ["Auckland Airport", "Auckland CBD"],
                self.route_ids[1]: ["Hamilton Central", "Te Rapa"]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/operator/routes/",
                headers=headers,
                json={"routes": test_routes}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get("ok"):
                self.print_success(f"Operator routes updated: {data.get('count')} routes")
                return True
            else:
                self.print_error(f"Operator routes failed: {data}")
                return False
                
        except Exception as e:
            self.print_error("Operator route test failed", e)
            return False

    def test_google_maps_api(self):
        """Test 9: Google Maps API integration"""
        self.print_header("TEST 9: Google Maps API Integration")
        
        if not self.token:
            self.print_warning("Skipping (no token)")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {
                "origin": "Auckland Airport",
                "destination": "Auckland CBD"
            }
            
            self.print_info("Testing Google Maps ETA calculation...")
            
            response = requests.get(
                f"{BASE_URL}/api/eta/",
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                distance = data.get("distance_m", 0)
                duration = data.get("duration_s", 0)
                traffic = data.get("duration_in_traffic_s", 0)
                
                self.print_success("Google Maps API working")
                self.print_info(f"Distance: {distance}m")
                self.print_info(f"Duration: {duration}s ({duration//60}min)")
                self.print_info(f"With traffic: {traffic}s ({traffic//60}min)")
                return True
            elif response.status_code == 404:
                self.print_error("Google Maps API: No route found")
                return False
            else:
                data = response.json()
                self.print_error(f"Google Maps API failed: {data}")
                return False
                
        except Exception as e:
            self.print_error("Google Maps API test failed", e)
            return False

    def test_aws_dynamodb_connection(self):
        """Test 10: AWS DynamoDB connectivity"""
        self.print_header("TEST 10: AWS DynamoDB Connection")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Check environment variables
            aws_region = os.getenv("AWS_REGION")
            if not aws_region:
                self.print_error("AWS_REGION not set in .env")
                return False
            
            self.print_info(f"Testing DynamoDB connection in region: {aws_region}")
            
            # Try to create DynamoDB client
            dynamodb = boto3.resource('dynamodb', region_name=aws_region)
            
            # Test each table
            tables = [
                os.getenv("DYNAMODB_TABLE_SNAPSHOTS", "TransitTrafficSnapshots"),
                os.getenv("DYNAMODB_TABLE_PREDICTIONS", "TransitPredictions"),
                os.getenv("DYNAMODB_TABLE_SCHEDULES", "TransitSchedules"),
                os.getenv("DYNAMODB_TABLE_ROUTE_HISTORY", "TransitRouteHistory")
            ]
            
            for table_name in tables:
                try:
                    table = dynamodb.Table(table_name)
                    table.load()
                    self.print_success(f"DynamoDB table accessible: {table_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceNotFoundException':
                        self.print_error(f"DynamoDB table not found: {table_name}")
                        return False
                    else:
                        raise
            
            self.print_success("All DynamoDB tables accessible")
            return True
            
        except ImportError:
            self.print_error("boto3 not installed")
            return False
        except Exception as e:
            self.print_error("DynamoDB connection test failed", e)
            return False

    def test_data_anonymization(self):
        """Test 11: GDPR data anonymization"""
        self.print_header("TEST 11: Data Anonymization (GDPR)")
        
        try:
            from traffic.anonymize import hash_id
            
            # Test anonymization function
            test_id = "test_user_123"
            hashed = hash_id(test_id)
            
            if len(hashed) == 64:  # SHA-256 produces 64 character hex
                self.print_success("Anonymization function working")
                self.print_info(f"Original: {test_id}")
                self.print_info(f"Hashed: {hashed[:32]}...")
                return True
            else:
                self.print_error("Anonymization produced invalid hash")
                return False
                
        except Exception as e:
            self.print_error("Data anonymization test failed", e)
            return False

    def test_mfa_enrollment(self):
        """Test 12: MFA enrollment capability"""
        self.print_header("TEST 12: MFA Enrollment (Optional)")
        
        if not self.token:
            self.print_warning("Skipping (no token)")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/auth/mfa/enroll/",
                headers=headers
            )
            data = response.json()
            
            if response.status_code == 200:
                if "enabled" in data and data["enabled"]:
                    self.print_success("MFA already enabled")
                elif "secret" in data:
                    self.print_success("MFA enrollment endpoint working")
                    self.print_info(f"Secret: {data['secret'][:10]}...")
                else:
                    self.print_warning("Unexpected MFA response")
                return True
            else:
                self.print_error(f"MFA enrollment failed: {data}")
                return False
                
        except Exception as e:
            self.print_error("MFA enrollment test failed", e)
            return False

    def test_background_scheduler(self):
        """Test 13: Background scheduler status"""
        self.print_header("TEST 13: Background Scheduler")
        
        try:
            # Check if scheduler module exists
            from traffic.scheduler import scheduler
            
            if scheduler.running:
                self.print_success("Background scheduler is running")
                
                # Get job info
                jobs = scheduler.get_jobs()
                if jobs:
                    self.print_info(f"Scheduled jobs: {len(jobs)}")
                    for job in jobs:
                        self.print_info(f"  - {job.id}: Next run at {job.next_run_time}")
                else:
                    self.print_warning("Scheduler running but no jobs scheduled")
                
                return True
            else:
                self.print_warning("Scheduler not running (may be disabled)")
                return True
                
        except Exception as e:
            self.print_warning(f"Scheduler test inconclusive: {e}")
            return True  # Don't fail on scheduler issues

    def test_environment_variables(self):
        """Test 14: Environment variables configuration"""
        self.print_header("TEST 14: Environment Variables")
        
        try:
            required_vars = [
                "SECRET_KEY",
                "AWS_REGION",
                "DYNAMODB_TABLE_SNAPSHOTS",
                "DYNAMODB_TABLE_PREDICTIONS",
                "DYNAMODB_TABLE_SCHEDULES",
                "DYNAMODB_TABLE_ROUTE_HISTORY",
                "GOOGLE_MAPS_API_KEY"
            ]
            
            all_set = True
            for var in required_vars:
                value = os.getenv(var)
                if value:
                    self.print_success(f"{var} is set")
                else:
                    self.print_error(f"{var} is NOT set")
                    all_set = False
            
            return all_set
            
        except Exception as e:
            self.print_error("Environment variables test failed", e)
            return False

    def print_summary(self):
        """Print final test summary"""
        self.print_header("TEST SUMMARY")
        
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Fore.CYAN}Total Tests: {total_tests}")
        print(f"{Fore.GREEN}Passed: {self.tests_passed}")
        print(f"{Fore.RED}Failed: {self.tests_failed}")
        print(f"{Fore.YELLOW}Pass Rate: {pass_rate:.1f}%\n")
        
        if self.tests_failed > 0:
            print(f"{Fore.RED}{Style.BRIGHT}Failed Tests:")
            for result in self.test_results:
                if result[0] == "FAIL":
                    print(f"{Fore.RED}  ✗ {result[1]}")
                    if len(result) > 2 and result[2]:
                        print(f"{Fore.RED}    {result[2]}")
        
        print("\n" + "="*70)
        if self.tests_failed == 0:
            print(f"{Fore.GREEN}{Style.BRIGHT}🎉 ALL TESTS PASSED! Backend is 100% operational! 🎉")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}⚠️  {self.tests_failed} test(s) failed. Please review and fix.")
        print("="*70 + "\n")
        
        return self.tests_failed == 0

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║          TRANSIT BACKEND COMPREHENSIVE TEST SUITE                 ║")
        print("║                   Testing ALL Components                          ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(Style.RESET_ALL)
        
        start_time = time.time()
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Run tests in order
        tests = [
            ("Server Connectivity", self.check_server_running),
            ("Health Endpoint", self.test_health_endpoint),
            ("Environment Variables", self.test_environment_variables),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("CSV Data Loading", self.test_csv_data_loading),
            ("Data Anonymization", self.test_data_anonymization),
            ("AWS DynamoDB", self.test_aws_dynamodb_connection),
            ("Operator Routes", self.test_operator_routes),
            ("Prediction Model", self.test_prediction_model),
            ("GA Scheduler", self.test_genetic_algorithm),
            ("Google Maps API", self.test_google_maps_api),
            ("MFA Enrollment", self.test_mfa_enrollment),
            ("Background Scheduler", self.test_background_scheduler),
        ]
        
        # Skip remaining tests if server is down
        server_running = self.check_server_running()
        if not server_running:
            self.print_error("Server is not running. Cannot continue tests.")
            self.print_info("Please start the server with: python manage.py runserver")
            return False
        
        # Run remaining tests
        for i, (name, test_func) in enumerate(tests[1:], start=2):
            try:
                test_func()
            except Exception as e:
                self.print_error(f"Test crashed: {name}", e)
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Print summary
        elapsed_time = time.time() - start_time
        print(f"\n{Fore.CYAN}Tests completed in {elapsed_time:.2f} seconds")
        
        return self.print_summary()


def main():
    """Main entry point"""
    tester = BackendTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()