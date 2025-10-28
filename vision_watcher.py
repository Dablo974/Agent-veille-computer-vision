# file: vision_watcher.py
import feedparser
import requests
from datetime import datetime
import os

# === 1️⃣ PARAMÈTRES ===
QUERY = "computer vision"
MAX_RESULTS = 5
DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1432377669961519265/PL-ANiNzsaCFWHfVTNIeOWQkE-4ifzhnrrV6vfdtHDVGxd0Htr2zA0QJiDx1yvg32ikD"

# === 2️⃣ RÉCUPÉRATION DES ARTICLES ARXIV ===
def fetch_arxiv(query=QUERY, max_results=MAX_RESULTS):
    base_url = "http://export.arxiv.org/api/query?search_query=all:{}&sortBy=submittedDate&sortOrder=descending&max_results={}"
    feed = feedparser.parse(base_url.format(query.replace(" ", "+"), max_results))
    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "url": entry.link,
            "summary": entry.summary[:300] + "..."
        })
    return results

# === 3️⃣ GÉNÉRATION DU MESSAGE ===
def make_summary(entries):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    message = f"**🧠 Computer Vision Watcher - {today}**\n\n"
    if not entries:
        return message + "_Aucun nouvel article trouvé._"
    for e in entries:
        message += f"**{e['title']}**\n{e['summary']}\n🔗 {e['url']}\n\n"
    return message

# === 4️⃣ ENVOI SUR DISCORD ===
def send_to_discord(message):
    webhook = os.getenv("DISCORD_WEBHOOK")
    if not webhook:
        print("❌ Aucun webhook Discord trouvé.")
        return

    if not message.strip():
        print("⚠️ Message vide, rien à envoyer.")
        return

    if len(message) > 1900:
        message = message[:1900] + "… (tronqué)"

    res = requests.post(webhook, json={"content": message})
    print(f"↩️ Code retour Discord: {res.status_code}")
    if res.status_code == 204:
        print("✅ Rapport envoyé sur Discord.")
    else:
        print("⚠️ Erreur Discord:", res.text)


# === 5️⃣ PIPELINE PRINCIPALE ===
def main():
    entries = fetch_arxiv()
    summary = make_summary(entries)
    send_to_discord(summary)
    print("✅ Rapport envoyé sur Discord.")

if __name__ == "__main__":
    main()
