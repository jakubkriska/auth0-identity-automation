import csv
import os
from dotenv import load_dotenv
from auth0.authentication import GetToken
from auth0.management import Auth0

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Securely fetch configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')

def run_onboarding():
    print("\n--- Starting Identity Onboarding Engine ---")

    # Check if keys are loaded correctly
    if not all([AUTH0_DOMAIN, CLIENT_ID, CLIENT_SECRET]):
        print(" [ERROR] Missing configuration. Please check your .env file.")
        return

    # 3. Authenticate against Auth0 (Machine-to-Machine)
    print("1. Connecting to Auth0...")
    try:
        # Request an access token
        get_token = GetToken(AUTH0_DOMAIN, CLIENT_ID, client_secret=CLIENT_SECRET)
        token = get_token.client_credentials(audience=f'https://{AUTH0_DOMAIN}/api/v2/')
        mgmt_api_token = token['access_token']
        
        # Initialize the Management API client
        auth0 = Auth0(AUTH0_DOMAIN, mgmt_api_token)
        print("   [OK] Connection established.")
    except Exception as e:
        print(f"   [ERROR] Failed to connect. Check your credentials. Details: {e}")
        return

    # 4. Process the CSV file
    print("2. Processing CSV data...")
    try:
        with open('new_hires.csv', mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                first_name = row['FirstName']
                last_name = row['LastName']
                
                # Generate a work email
                email = f"{first_name}.{last_name}@revai-demo.com".lower()
                
                # In production, use a random password generator. 
                # For this demo, we use a static initial password.
                password = "Welcome123!ChangeMe" 

                print(f" -> Processing: {first_name} {last_name} ({email})")

                # Construct the User Object for Auth0
                user_data = {
                    "email": email,
                    "password": password,
                    "connection": "Username-Password-Authentication", # Default DB connection
                    "user_metadata": {
                        "department": row['Department'],
                        "title": row['JobTitle']
                    },
                    "email_verified": False
                }

                # Send request to the API
                try:
                    auth0.users.create(user_data)
                    print(f"    [SUCCESS] User created in cloud directory.")
                except Exception as api_error:
                    # Handle duplicate users gracefully
                    if "The user already exists" in str(api_error):
                        print(f"    [SKIP] User already exists.")
                    else:
                        print(f"    [ERROR] API request failed: {api_error}")
                        
    except FileNotFoundError:
        print("   [ERROR] File 'new_hires.csv' not found. Is it in the correct folder?")
    except KeyError as e:
        print(f"   [ERROR] CSV Header missing: {e}. Check your CSV column names.")

if __name__ == '__main__':
    run_onboarding()