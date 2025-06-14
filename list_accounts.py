import json
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Load credentials
with open("google_ads_token.json", "r") as f:
    token_data = json.load(f)

# Load OAuth client config
with open("client_secret.json", "r") as f:
    client_config = json.load(f)

# Build the Google Ads client
config = {
    "developer_token": "5dgO8PwWUCrkFzmgY1b_YA",
    "refresh_token": token_data["refresh_token"],
    "client_id": client_config["web"]["client_id"],
    "client_secret": client_config["web"]["client_secret"],
    "use_proto_plus": True,
    "login_customer_id": "7297816540",  # MCC ID (no dashes)
}

client = GoogleAdsClient.load_from_dict(config)

# Query accessible accounts
ga_service = client.get_service("GoogleAdsService")

query = """
    SELECT customer_client.client_customer, customer_client.level, customer_client.status, customer_client.descriptive_name
    FROM customer_client
    WHERE customer_client.level <= 1
"""

try:
    response = ga_service.search(customer_id=config["login_customer_id"], query=query)

    print("\n🧾 Accessible Google Ads Accounts:\n")
    for row in response:
        print(f"Account ID: {row.customer_client.client_customer}")
        print(f"Name     : {row.customer_client.descriptive_name}")
        print(f"Status   : {row.customer_client.status.name}")
        print("-" * 40)

except GoogleAdsException as ex:
    print("❌ API Error:")
    print(ex)
