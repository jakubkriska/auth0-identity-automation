import csv
import os
import time
import warnings

warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from auth0.authentication import GetToken
from auth0.management import Auth0

# 1. Configuration & Setup
load_dotenv()

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')

def get_auth0_client():
    """Helper function to handle authentication once."""
    try:
        get_token = GetToken(AUTH0_DOMAIN, CLIENT_ID, client_secret=CLIENT_SECRET)
        token = get_token.client_credentials(audience=f'https://{AUTH0_DOMAIN}/api/v2/')
        mgmt_api_token = token['access_token']
        return Auth0(AUTH0_DOMAIN, mgmt_api_token)
    except Exception as e:
        print(f" [CRITICAL] Login failed: {e}")
        return None

def run_onboarding(auth0):
    """Reads CSV and creates users."""
    print("\n--- Phase 1: Onboarding Users ---")
    
    try:
        with open('new_hires.csv', mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                first_name = row['FirstName']
                last_name = row['LastName']
                email = f"{first_name}.{last_name}@revai-test.com".lower()
                password = "Welcome123!ChangeMe" 

                print(f" -> Processing: {first_name} {last_name}...")

                user_data = {
                    "email": email,
                    "password": password,
                    "connection": "Username-Password-Authentication",
                    "user_metadata": {
                        "department": row['Department'],
                        "title": row['JobTitle']
                    },
                    "email_verified": False
                }

                try:
                    auth0.users.create(user_data)
                    print(f"    [SUCCESS] Created.")
                except Exception as api_error:
                    if "The user already exists" in str(api_error):
                        print(f"    [SKIP] Already exists.")
                    else:
                        print(f"    [ERROR] {api_error}")
    except FileNotFoundError:
        print("   [ERROR] 'new_hires.csv' not found.")

def run_verification(auth0):
    """Fetches users from cloud to verify data."""
    print("\n--- Phase 2: Verification (Live Data) ---")
    # Small pause to ensure the cloud index has updated (Eventual Consistency)
    time.sleep(5) 

    print(f"{'NAME':<20} | {'EMAIL':<30} | {'DEPT':<15} | {'TITLE'}")
    print("-" * 85)

    try:
        # Get all users (no filter)
        users = auth0.users.list(per_page=10)
        
        for user in users['users']:
            name = user.get('name', 'N/A')
            email = user.get('email', 'N/A')
            metadata = user.get('user_metadata', {})
            dept = metadata.get('department', '-')
            title = metadata.get('title', '-')
            
            print(f"{name:<20} | {email:<30} | {dept:<15} | {title}")
            
    except Exception as e:
        print(f" [ERROR] Could not fetch users: {e}")

if __name__ == '__main__':
    # Main Orchestrator
    print("Initializing Identity Engine...")
    
    # 1. Connect Once
    client = get_auth0_client()
    
    if client:
        # 2. Run Onboarding
        run_onboarding(client)
        
        # 3. Run Verification
        run_verification(client)
        
    print("\n--- Pipeline Complete ---")