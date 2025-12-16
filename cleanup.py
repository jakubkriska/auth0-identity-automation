import os
import warnings
from dotenv import load_dotenv
from auth0.authentication import GetToken
from auth0.management import Auth0

# 1. Setup & Konfiguration
load_dotenv()
warnings.filterwarnings("ignore") # Fjerner SSL advarsler

def get_auth0_client():
    """Logger ind og returnerer klienten (samme som i main.py)"""
    try:
        domain = os.getenv('AUTH0_DOMAIN')
        client_id = os.getenv('AUTH0_CLIENT_ID')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        
        get_token = GetToken(domain, client_id, client_secret=client_secret)
        token = get_token.client_credentials(audience=f'https://{domain}/api/v2/')
        return Auth0(domain, token['access_token'])
    except Exception as e:
        print(f" [CRITICAL] Login failed: {e}")
        return None

def run_cleanup():
    print("\n--- Starting Offboarding (Cleanup) ---")
    
    client = get_auth0_client()
    if not client:
        return

    # 2. Find målgruppen
    # SIKKERHED: Vi søger KUN efter test-brugere (@revai-test.com)
    # Dette forhindrer at du sletter dig selv eller forkerte brugere.
    target_domain = "@revai-test.com"
    print(f"Searching for users with email ending in: '{target_domain}'...")
    
    try:
        # Auth0 søgesyntaks: 'email:*@domæne.com'
        users = client.users.list(q=f'email:*{target_domain}', per_page=50)
        user_list = users.get('users', [])

        if not user_list:
            print(" -> No users found to delete. System is clean.")
            return

        print(f" -> Found {len(user_list)} users. Deleting now...\n")

        # 3. Slet dem én efter én
        for user in user_list:
            name = user.get('name', 'Unknown')
            email = user.get('email', 'Unknown')
            user_id = user.get('user_id') # VIGTIGT: Man sletter på ID, ikke email

            print(f" -> Offboarding: {name} ({email})...")
            
            try:
                client.users.delete(user_id)
                print(f"    [DELETED] User removed access.")
            except Exception as e:
                print(f"    [ERROR] Could not delete: {e}")

    except Exception as e:
        print(f" [ERROR] Search failed: {e}")

    print("\n--- Cleanup Complete ---")

if __name__ == '__main__':
    run_cleanup()