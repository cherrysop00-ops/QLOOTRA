# QLOOTRA
QLOOTRA is your AI travel companion powered by Gemini and Qloo. Plan smart trips across 5 phases — PLAN, PACK, JOURNEY, DESTINY, RETURN — with tailored suggestions for outfits, music, food, and destinations based on your unique tastes. Switch between casual chat and immersive travel planning anytime.
# QLOOTRA – AI Travel Companion ✈️🌍

🔗 **Live App**: [Click to Open](https://qlootra-abjb7stfdzwt4ozg4nmzll.streamlit.app/)

# 🌍 QLOOTRA – AI Travel Companion (v1.0)

**QLOOTRA** (short for **Qloo Travel Recommender Assistant**) is an intelligent travel chatbot that blends *casual AI chat* with *cultural recommendations*. Powered by **Google Gemini** and **Qloo**, it creates personalized travel plans across **5 gamified trip phases** — using your tastes in music, movies, fashion, food, and more.

> 🔮 "Chat like a friend, plan like a pro."

---

## ✨ Core Features

### 🧠 NORMAL Mode – Taste-Aware AI Chat  
Chat freely with QLOOTRA. As you mention your interests (e.g., “I love K-pop” or “I enjoy Marvel movies”), it builds a memory of your preferences across music, food, fashion, and more.

---

### ✈️ PLAN A TRIP Mode – 5-Phase Travel Planner  
Choose this mode to go step-by-step through your trip:

1. **PLAN** – Set your destination, duration, and budget  
2. **PACK** – Outfit & fashion suggestions (via Qloo) based on your tastes and location  
3. **JOURNEY** – Personalized music, movies, podcasts, books for your trip  
4. **DESTINY** – Discover food & local spots based on cross-domain taste inference  
5. **RETURN** – Share your experience and rate the trip

---

### ⚡ SPARK Mode – One-Line Trip Generator  
Just say something like:  
> `"I'm going to Japan for 7 days and I love Justin Bieber."`  
And get a full 5-phase trip plan auto-generated!

---

### 🔄 Gemini Key Rotation  
Efficient key rotation system to balance load and avoid API exhaustion. Supports multiple Gemini keys.

---

### 🔗 Cross-Domain Taste Prediction  
QLOOTRA uses **Qloo's AI** to predict taste connections like:  
> Music → Food → Fashion → Places

---

## 🧱 Tech Stack

| Layer | Details |
|-------|---------|
| **Frontend** | Streamlit (chat + interactive dashboard) |
| **AI Chat** | Google Gemini (`gemini-1.5-flash`) |
| **Taste Intelligence** | Qloo API (music, food, fashion, movies, etc.) |
| **Backend** | Python |
| **Persistence** | JSON-based trip saving + session memory |
| **Deployment** | Streamlit Cloud |

---

## 🛣️ Roadmap

### 🔜 Upcoming Versions

- **v1.1 – Spotify-Powered Personalization**  
  Automatically generate cross-domain recommendations (movies, outfits, food) from your *Spotify* listening habits.

- **v1.2 – Season & Weather-Aware Planning**  
  Recommend trips, experiences, and packing lists *based on seasonal conditions and weather forecasts* at your destination.

---

## 💻 How to Run Locally

```bash
git clone https://github.com/cherrysop00-ops/QLOOTRA.git
cd QLOOTRA

# Create and activate virtual environment (optional)
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

pip install -r requirements.txt

# Add your API keys:
# .gemini_key1 to .gemini_key10 (Gemini API keys)
# .qloo_key (Qloo API key)

streamlit run qlootra.py
