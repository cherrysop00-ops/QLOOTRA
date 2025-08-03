import streamlit as st
from datetime import datetime
import concurrent.futures
def do_rerun():
    st.experimental_rerun()


# --- Assumes these real functions are imported or defined elsewhere ---
# Example import (replace with your actual imports):
# from qlootra_gemini import (
#     generate_with_gemini as real_generate_with_gemini,
#     cached_qloo_recs as real_cached_qloo_recs,
#     extract_tastes_from_text as real_extract_tastes_from_text,
#     load_saved_trips as real_load_saved_trips,
#     save_trips as real_save_trips,
# )

# --- Initialize real backend function refs into session_state once ---
if "shared_functions_loaded" not in st.session_state:
    st.session_state.shared_functions_loaded = True
    # Assign your real imported functions here, for example:
    # st.session_state.generate_with_gemini_func = real_generate_with_gemini
    # st.session_state.cached_qloo_recs_func = real_cached_qloo_recs
    # st.session_state.extract_tastes_from_text_func = real_extract_tastes_from_text
    # st.session_state.load_saved_trips_func = real_load_saved_trips
    # st.session_state.save_trips_func = real_save_trips

# --- Wrapper functions that call session state functions safely ---
def call_generate_with_gemini(prompt):
    return st.session_state.generate_with_gemini_func(prompt)

def call_cached_qloo_recs(taste):
    if "cached_qloo_recs_func" not in st.session_state:
        st.error("❌ cached_qloo_recs_func not initialized.")
        return {}
    return st.session_state.cached_qloo_recs_func(taste)

def call_extract_tastes_from_text(text):
    return st.session_state.extract_tastes_from_text_func(text)

def call_load_saved_trips():
    return st.session_state.load_saved_trips_func()

def call_save_trips(trips):
    return st.session_state.save_trips_func(trips)

# --- Utility helpers ---
def clean_items(items):
    seen = set()
    cleaned = []
    for i in items:
        s = str(i).strip()
        if s and s.lower() not in seen:
            cleaned.append(s)
            seen.add(s.lower())
    return cleaned

def get_qloo_recs_threaded(taste, domains):
    results = {}

    def fetch(domain):
        return domain, list(call_cached_qloo_recs(taste).get(domain, []))

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(domains)) as executor:
        futures = [executor.submit(fetch, domain) for domain in domains]
        for future in concurrent.futures.as_completed(futures):
            domain, items = future.result()
            results[domain] = items or []
    return results

def get_batched_gemini_recommendations(taste_domain_pairs):
    results = {}
    taste_to_domains = {}
    for taste, domain in taste_domain_pairs:
        taste_to_domains.setdefault(taste, []).append(domain)

    for taste, domains in taste_to_domains.items():
        prompt = (
            f"A person likes '{taste}'. Suggest up to 3 popular {', '.join(domains)} items for a traveler.\n"
            + "\n".join([f"{dom}: item1, item2, item3" for dom in domains])
            + "\n\nOnly respond with domain names followed by items separated by commas."
        )
        gemini_response = call_generate_with_gemini(prompt)
        for line in gemini_response.splitlines():
            if ':' in line:
                dom, items_str = line.split(':', 1)
                dom = dom.strip().lower()
                if dom in domains:
                    items = [i.strip() for i in items_str.split(',') if i.strip()]
                    results[(taste, dom)] = items[:5]
    return results

def get_recommendations_with_batched_fallback(taste, needed_domains=None):
    if not taste:
        return {}

    if needed_domains is None:
        needed_domains = ["music", "food", "fashion", "movie", "travel", "place"]

    qloo_recs = get_qloo_recs_threaded(taste, needed_domains)

    final_recs = {}
    missing_domains = []

    for domain in needed_domains:
        items = qloo_recs.get(domain, [])
        cleaned = clean_items(items)[:5]
        final_recs[domain] = cleaned
        if len(cleaned) < 2:
            missing_domains.append(domain)

    if missing_domains:
        pairs = [(taste, domain) for domain in missing_domains]
        gemini_results = get_batched_gemini_recommendations(pairs)
        for (taste_key, domain), items in gemini_results.items():
            if domain in missing_domains:
                merged = clean_items(final_recs.get(domain, []) + items)[:5]
                final_recs[domain] = merged

    return final_recs

# --- Main plan trip UI ---
def plan_trip_mode():
    st.subheader("✈️ Plan a Trip (Game Mode)")

    if "chat_trip" not in st.session_state:
        st.session_state.chat_trip = []
    if "greeted_trip" not in st.session_state:
        st.session_state.greeted_trip = False
    if "greeted_trip_done" not in st.session_state:
        st.session_state.greeted_trip_done = False
    if "trip" not in st.session_state:
        st.session_state.trip = {}
    if "tastes" not in st.session_state:
        st.session_state.tastes = []

    trip_phase = st.radio(
        "Which phase are you in?",
        ("PLAN", "PACK", "JOURNEY", "DESTINY", "RETURN"),
        key="trip_phase",
        horizontal=True,
    )

    if not st.session_state.greeted_trip_done:
        if not st.session_state.greeted_trip:
            st.session_state.chat_trip.append((
                "assistant",
                "Welcome! Progress through the phases: PLAN, PACK, JOURNEY, DESTINY, RETURN — each step adapts based on your tastes."
            ))
            st.session_state.greeted_trip = True
        st.session_state.greeted_trip_done = True
        do_rerun()

    for sender, msg in st.session_state.chat_trip:
        role = "user" if sender == "user" else "assistant"
        st.chat_message(role).markdown(msg)

    def gather_tastes():
        combined = st.session_state.tastes + [
            st.session_state.get("tastes_music", ""),
            st.session_state.get("tastes_food", ""),
            st.session_state.get("tastes_fashion", ""),
        ]
        filtered = list(set(filter(None, combined)))
        return [t for t in filtered if len(t) >= 3][:5]

    if trip_phase == "PLAN":
        dest = st.text_input("Destination", value=st.session_state.trip.get("destination", ""))
        days = st.number_input("Days", min_value=1, max_value=60, value=st.session_state.trip.get("days", 3))
        budget = st.text_input("Budget (optional)", value=st.session_state.trip.get("budget", ""))

        if st.button("🚀 Lock Plan"):
            st.session_state.trip = {
                "destination": dest,
                "days": days,
                "budget": budget,
                "timestamp": datetime.now().isoformat(),
            }
            trips = call_load_saved_trips()
            trips.append(st.session_state.trip)
            call_save_trips(trips)
            msg = f"Your trip to **{dest}** for **{days} days** is locked in! (Budget: {budget or 'N/A'})"
            st.session_state.chat_trip.append(("assistant", msg))
            st.success(msg)
            do_rerun()

    elif trip_phase == "PACK":
        rec_tastes = gather_tastes()
        outfits = set()
        brands = set()
        max_outfits = min(st.session_state.trip.get("days", 3), 10)

        if st.button("🎒 Generate Packing List"):
            with st.spinner("Generating packing recommendations..."):
                for taste in rec_tastes:
                    recs = get_recommendations_with_batched_fallback(taste, ["fashion", "brand"])
                    outfits.update(recs.get("fashion", []))
                    brands.update(recs.get("brand", []))
                    if len(outfits) >= max_outfits:
                        break

            outfits_list = clean_items(list(outfits))[:max_outfits]
            brands_list = clean_items(list(brands))[:5]

            msg = ""
            if outfits_list:
                msg += f"🧳 Pack these outfits: {', '.join(outfits_list)}\n"
            if brands_list:
                msg += f"🏷️ Brands to try: {', '.join(brands_list)}"
            if not msg.strip():
                msg = "No fashion/brand suggestions yet. Add more tastes!"
            st.session_state.chat_trip.append(("assistant", msg))
            st.markdown(msg)

    elif trip_phase == "JOURNEY":
        rec_tastes = gather_tastes()
        entertainment_items = set()
        journey_foods_items = set()
        journey_domains = ["music", "tv", "movie", "podcast", "book", "game"]

        if st.button("🚌 Generate Journey Entertainment & Snacks"):
            with st.spinner("Finding travel entertainment and snacks..."):
                for taste in rec_tastes:
                    recs = get_recommendations_with_batched_fallback(taste, journey_domains + ["food"])
                    for dom in journey_domains:
                        entertainment_items.update(recs.get(dom, []))
                    journey_foods_items.update(recs.get("food", []))

            entertainment = clean_items(list(entertainment_items))[:10]
            journey_foods = clean_items(list(journey_foods_items))[:5]

            msg = ""
            if entertainment:
                msg += f"🎬 Entertainment: {', '.join(entertainment)}\n"
            if journey_foods:
                msg += f"🍔 Travel foods: {', '.join(journey_foods)}"
            if not msg.strip():
                msg = "No travel recommendations yet. Add your tastes to get suggestions!"
            st.session_state.chat_trip.append(("assistant", msg))
            st.markdown(msg)

    elif trip_phase == "DESTINY":
        dest = st.session_state.trip.get("destination", "")
        taste_seeds = list(set(filter(None, st.session_state.tastes + [
            st.session_state.get("tastes_music", ""),
            st.session_state.get("tastes_food", ""),
        ])))

        destiny_foods_items = set()
        destiny_places_items = set()

        if st.button(f"🌍 Discover {dest} Highlights"):
            with st.spinner(f"Discovering {dest}'s highlights..."):
                for taste in taste_seeds:
                    recs = get_recommendations_with_batched_fallback(taste, ["food", "travel", "place"])
                    destiny_foods_items.update(recs.get("food", []))
                    destiny_places_items.update(recs.get("travel", []))
                    destiny_places_items.update(recs.get("place", []))

            destiny_foods = clean_items(list(destiny_foods_items))[:5]
            shown_places = clean_items(list(destiny_places_items))[:5]
            if dest and dest not in shown_places:
                shown_places.insert(0, dest)
                shown_places = shown_places[:5]

            msg = ""
            if destiny_foods:
                msg += f"🍲 Try local foods: {', '.join(destiny_foods)}\n"
            if shown_places:
                msg += f"🗺️ Must-visit places: {', '.join(shown_places)}"
            if not msg.strip():
                msg = "Tell me about your food or place tastes to get better recommendations!"
            st.session_state.chat_trip.append(("assistant", msg))
            st.markdown(msg)

    elif trip_phase == "RETURN":
        rating = st.slider("Rate your trip:", 1, 10)
        feedback = st.text_area("Share your experience:")

        if st.button("📩 Submit Feedback"):
            thank_msg = "Thanks for your feedback! Glad you travelled with QLOOTRA. 🚀"
            st.session_state.chat_trip.append(("assistant", thank_msg))
            st.success(thank_msg)

    trip_input = st.chat_input("Chat during your trip...", key="trip_input")
    if trip_input:
        st.session_state.chat_trip.append(("user", trip_input))
        with st.spinner("Processing your travel thoughts..."):
            tastes = call_extract_tastes_from_text(trip_input)
            rec_reply = ""
            for t in tastes:
                cr = get_recommendations_with_batched_fallback(t)
                if cr:
                    rec_reply += f"🌍 Tips for **{t}**: "
                    for dom, items in cr.items():
                        rec_reply += f"{dom.title()}: {', '.join(clean_items(items))}; "
                else:
                    rec_reply += f"I'll remember {t} for the next phases! "
            if not rec_reply:
                rec_reply = "Enjoy your trip!"
        st.session_state.chat_trip.append(("assistant", rec_reply))
        st.chat_message("assistant").markdown(rec_reply)

# In your Streamlit app main:
if st.session_state.get("mode") == "Plan a Trip":
    plan_trip_mode()
