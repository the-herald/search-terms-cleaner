import json
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# === Load allowed account IDs ===
with open("allowed_accounts.txt", "r") as f:
    allowed_accounts = [line.strip().replace("-", "") for line in f if line.strip()]

# === Load OAuth token data ===
with open("google_ads_token.json", "r") as f:
    token_data = json.load(f)

# === Load OAuth client config ===
with open("client_secret.json", "r") as f:
    client_config = json.load(f)

# === Set up Google Ads API config ===
config = {
    "developer_token": "5dgO8PwWUCrkFzmgY1b_YA",
    "refresh_token": token_data["refresh_token"],
    "client_id": client_config["web"]["client_id"],
    "client_secret": client_config["web"]["client_secret"],
    "login_customer_id": "7297816540",  # Your MCC ID without dashes
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config)

# === List of auto-disqualified terms ===
AUTO_EXCLUDE_TERMS = set([
    "cheap", "affordable", "diy", "asmallworld", "badoo", "bebo", "blackplanet", "buzznet", "cafemom", "care2",
    "caringbridge", "cellufun", "classmates", "couchsurfing", "cross.tv", "delicious", "deviantart", "douban", "faq",
    "flickr", "flixter", "focus", "fotki", "fotolog", "foursquare", "friendster", "funnyordie", "gaiaonline", "geni",
    "habbo", "hi5", "hyves", "itsmy", "kiwibox", "last.fm", "link", "linkedin", "meetup", "mixi", "mocospace",
    "multiply", "myheritage", "mylife", "myopera", "myyearbook", "nk", "netlog", "ning", "odnoklassniki", "opendiary",
    "orkut", "qzone", "ravelry", "renren", "reverbnation", "ryze", "skyrock", "sonico", "stickam", "studivz",
    "stumbleupon", "tagged", "travbuddy", "tuenti", "tumblr", "twitter", "vkontakte", "vampirefreaks", "viadeo", "wayn",
    "weread", "weeworld", "wordpress", "xing", "xanga", "youtube", "about", "academia serrant", "act", "ad", "ads",
    "advertisement", "advertising", "advice", "advisory", "affiliate marketing", "agencies", "agency", "airbnb",
    "aliexpress", "alo family counseling", "alo", "alpha m underwear", "alpha", "amazon", "animal", "animals", "answer",
    "antique", "antiques", "architecture", "article", "articles", "association", "associations", "astrology", "atm",
    "avalon nail school", "aveda institute", "aveda", "ballsy underwear", "ballsy", "bank", "bitcoin",
    "black cosmetology school", "blog", "blogs", "book", "books", "budget", "bulletin", "bulletins", "cancel", "cannes",
    "career", "careers", "carpet turn albuquerque", "case studies", "case study", "cat", "cats", "cd", "certification",
    "channel", "charity", "city of sacramento fire department billing", "ck", "class", "classes", "classified",
    "classifieds", "clip art", "club", "clubs", "clásico", "code", "collectible", "collectibles", "college", "colleges",
    "community", "comparison", "complaints", "compliance", "conference", "conferences", "consignment", "consulting",
    "consumer", "cool rental st barth", "cornerstone taxi", "cornerstone", "costco", "council", "councils",
    "counseling", "county court", "course", "courses", "craft", "crafts", "craigslist", "create", "creating", "crypto",
    "curso de maderoterapia en puerto rico", "cursos cortos en puerto rico", "cursos de maderoterapia",
    "cursos sabatinos en puerto rico", "cursos sabatinos puerto rico", "customer service", "cv", "data", "dating",
    "day trading", "define", "definition", "degree", "department", "dept", "desktop", "developer", "developers",
    "diagnose", "diagram", "diploma", "direct hire", "direct placement", "directions", "disk", "do it yourself",
    "do it yourselfer", "dog", "dogs", "download", "downloads", "drop shipping", "dzd", "dvd", "ebay", "education",
    "employer", "employers", "employment", "error", "ethereum", "etsy", "example", "examples", "export", "exporter",
    "exporters", "facebook", "festival", "file", "files", "financial", "firm", "firms",
    "fire alarm acceptance test checklist", "fire department bill after accident", "fire department outreach programs",
    "fire department record keeping", "fire department scheduling", "fire hydrant flow test",
    "fire officer development program", "first due software", "forex", "forum", "forums", "foundations", "free sample",
    "free", "freeware", "full time", "full-time", "game", "games", "gas station", "get rich", "going", "guide", "guides",
    "hack", "hacks", "hand crafted", "hand made", "handmade", "head hunter", "hiring", "history", "hobbies", "hobby",
    "home based business", "homemade", "house flipping", "how to", "image", "images", "import", "importer", "importers",
    "info", "information", "institutes", "intern", "interns", "internship", "internships", "job", "jobs", "journal",
    "journals", "law", "learning", "legal", "library", "list of", "location", "logo", "logos", "low cost", "lyrics",
    "magazine", "magazines", "make money online", "management", "map", "maps", "mba", "meaning of",
    "medical esthetician school", "microsoft", "model", "models", "music", "newsletter", "newsletters", "nursing",
    "online business", "online course", "open source", "opinion", "passive income", "pet", "pets", "photo", "photos",
    "picture", "pictures", "police", "porn", "program", "programs", "public domain", "real estate", "recipe",
    "recruiting", "reddit", "refund", "research", "resource", "resources", "resume", "reviews", "school", "schools",
    "seminar", "seminars", "sex", "shortcut", "shortcuts", "side hustle", "simulator", "social media", "stocks",
    "store", "success stories", "success story", "training", "tutorial", "tutorials", "university", "used", "video",
    "weather", "what is", "wiki", "wikipedia", "walmart", "warped tour", "warranties", "warranty", "what i", "what are",
    "when i", "when can", "where can", "white paper", "white papers", "work from home", "workshop", "workshops",
    "yard sale", "you tube", "zodiac"
])

# === Get list of enabled Search campaigns ===
def get_campaigns(customer_id):
    service = client.get_service("GoogleAdsService")
    query = """
        SELECT campaign.id, campaign.name
        FROM campaign
        WHERE campaign.status = 'ENABLED'
        AND campaign.advertising_channel_type = 'SEARCH'
    """
    return service.search(customer_id=customer_id, query=query)

# === Main scanning logic ===
def scan_accounts():
    print("🔎 Starting Search Terms Cleaner")

    for account_id in allowed_accounts:
        print(f"\n📂 Scanning account: {account_id}")

        try:
            campaigns = get_campaigns(account_id)
            for row in campaigns:
                campaign_id = row.campaign.id
                campaign_name = row.campaign.name
                print(f"  ➤ Campaign: {campaign_name} ({campaign_id})")

                # Placeholder: This is where you’ll pull and analyze search terms

        except GoogleAdsException as e:
            print(f"❌ Failed to process account {account_id}")
            print(e)

if __name__ == "__main__":
    scan_accounts()
