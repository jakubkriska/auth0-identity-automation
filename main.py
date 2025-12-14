import csv
from auth0.authentication import GetToken
from auth0.management import Auth0

# ==========================================
# KONFIGURATION (Indsæt dine nøgler her)
# ==========================================
AUTH0_DOMAIN = 'dev-g6p3dg6sgue48ytl.us.auth0.com'  # Husk at fjerne 'https://' hvis du kopierede det med
CLIENT_ID = 'rL3GKeGg7r6Cqkf9WwiChaYtEG191Yjz'
CLIENT_SECRET = '7i32iX3LOLB1HcN82cUcHDy1f4VSYaIc3O2mxOM-2dPWIU95hZoJszYnW_fu2W-l'

def run_onboarding():
    print("--- Starter Onboarding Engine ---")
    
    # 1. FÅ ADGANG (Login som maskine)
    print("1. Forbinder til Auth0...")
    try:
        get_token = GetToken(AUTH0_DOMAIN, CLIENT_ID, client_secret=CLIENT_SECRET)
        token = get_token.client_credentials(audience=f'https://{AUTH0_DOMAIN}/api/v2/')
        mgmt_api_token = token['access_token']
        
        # Opret forbindelsen til Management API'en
        auth0 = Auth0(AUTH0_DOMAIN, mgmt_api_token)
        print("   [OK] Forbindelse oprettet.")
    except Exception as e:
        print(f"   [FEJL] Kunne ikke logge ind. Tjek dine nøgler! Fejl: {e}")
        return

    # 2. LÆS OG OPRET BRUGERE
    print("2. Behandler CSV fil...")
    try:
        with open('new_hires.csv', mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                first_name = row['FirstName']
                last_name = row['LastName']
                
                # Generer unik data
                email = f"{first_name}.{last_name}@revai-test.com".lower()
                password = "Start123!Password" # Midlertidigt kodeord
                
                print(f" -> Behandler: {first_name} {last_name} ({email})")

                # Byg bruger-objektet til Auth0
                user_data = {
                    "email": email,
                    "password": password,
                    "connection": "Username-Password-Authentication", # Standard databasen
                    "user_metadata": {
                        "department": row['Department'],
                        "title": row['JobTitle']
                    },
                    "email_verified": False
                }

                # Send til API
                try:
                    auth0.users.create(user_data)
                    print(f"    [SUCCES] Bruger oprettet i skyen!")
                except Exception as api_error:
                    # Tjek om fejlen skyldes at brugeren allerede findes
                    if "The user already exists" in str(api_error):
                        print(f"    [SKIP] Bruger findes allerede.")
                    else:
                        print(f"    [FEJL] {api_error}")
                        
    except FileNotFoundError:
        print("   [FEJL] Fandt ikke filen 'new_hires.csv'. Er du i rigtig mappe?")

if __name__ == '__main__':
    run_onboarding()