# file: vision_watcher.py
import feedparser
import requests
from datetime import datetime
from huggingface_hub import InferenceClient
import feedparser, os, requests

HF_TOKEN = os.getenv("HF_TOKEN")
USE_HF = bool(HF_TOKEN)
SUMMARY_ERROR_LOGGED = False
client = InferenceClient("facebook/bart-large-cnn", token=HF_TOKEN) if USE_HF else None

def summarize_text(text):
    try:
        if not USE_HF or client is None:
            return (text or "")[:300] + "..."

        summary = client.summarization(text)
        # Le résultat peut être sous forme de liste ou de dict selon le backend
        if isinstance(summary, list) and "summary_text" in summary[0]:
            return summary[0]["summary_text"]
        elif isinstance(summary, dict) and "summary_text" in summary:
            return summary["summary_text"]
        elif isinstance(summary, str):
            return summary
        else:
            return str(summary)
    except Exception as e:
        global SUMMARY_ERROR_LOGGED
        if not SUMMARY_ERROR_LOGGED:
            print("⚠️ Résumé désactivé (HF Inference indisponible). Cause:", e)
            print("ℹ️ Astuce: définissez la variable d'environnement HF_TOKEN avec un jeton Hugging Face valide.")
            SUMMARY_ERROR_LOGGED = True
        return (text or "")[:300] + "..."


# === 1️⃣ PARAMÈTRES ===
QUERY = "computer vision"
MAX_RESULTS = 5
DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1432377669961519265/PL-ANiNzsaCFWHfVTNIeOWQkE-4ifzhnrrV6vfdtHDVGxd0Htr2zA0QJiDx1yvg32ikD"

# === 2️⃣ RÉCUPÉRATION DES ARTICLES ARXIV ===
def fetch_arxiv(query="computer vision", max_results=5):
    base_url = f"http://export.arxiv.org/api/query?search_query=all:{query.replace(' ','+')}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    feed = feedparser.parse(base_url)
    entries = []
    for e in feed.entries:
        summary = summarize_text(e.summary)
        entries.append({
            "title": e.title,
            "summary": summary.strip(),
            "url": e.link
        })
    return entries


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

if __name__ == "__main__":
    main()
