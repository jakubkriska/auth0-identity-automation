import os
from dotenv import load_dotenv
from auth0.authentication import GetToken
from auth0.management import Auth0

load_dotenv()

def verify_users():
    # 1. Connect
    domain = os.getenv('AUTH0_DOMAIN')
    client_id = os.getenv('AUTH0_CLIENT_ID')
    client_secret = os.getenv('AUTH0_CLIENT_SECRET')
    
    get_token = GetToken(domain, client_id, client_secret=client_secret)
    token = get_token.client_credentials(audience=f'https://{domain}/api/v2/')
    auth0 = Auth0(domain, token['access_token'])

    # 2. Get all users
    print(f"{'NAME':<20} | {'EMAIL':<30} | {'DEPT':<15} | {'TITLE'}")
    print("-" * 85)

    users = auth0.users.list(per_page=10, q='email:*@revai-test.com') # Filter for our test users
    
    for user in users['users']:
        name = user.get('name', 'N/A')
        email = user.get('email', 'N/A')
        # Safely get metadata (it might be empty for admin users)
        metadata = user.get('user_metadata', {})
        dept = metadata.get('department', '-')
        title = metadata.get('title', '-')
        
        print(f"{name:<20} | {email:<30} | {dept:<15} | {title}")

if __name__ == "__main__":
    verify_users()