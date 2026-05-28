import streamlit as st
import re

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PropVal AU — Free Australian Property Valuation",
    page_icon="🏠",
    layout="centered",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Font & base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #1a1714 0%, #2d1f17 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-tag {
    display: inline-block;
    background: rgba(45,106,58,0.3);
    color: #7ece8a;
    border: 1px solid rgba(45,106,58,0.4);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: .04em;
}
.hero h1 {
    color: #f5f0e8;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 0 0 .75rem;
}
.hero h1 span { color: #e07050; }
.hero p { color: #888; font-size: .95rem; margin: 0; line-height: 1.6; }

/* Value card */
.val-card {
    background: #1a1714;
    border-radius: 14px;
    padding: 1.75rem 2rem;
    margin-bottom: 1rem;
    color: #f5f0e8;
}
.val-label { font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: #666; margin-bottom: 8px; }
.val-amount { font-size: 3rem; font-weight: 700; line-height: 1; margin-bottom: 6px; letter-spacing: -.02em; }
.val-range { font-size: .9rem; color: #888; margin-bottom: 1.25rem; }
.conf-high   { display:inline-block; background:rgba(45,106,58,.25); color:#7ece8a; border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600; }
.conf-medium { display:inline-block; background:rgba(154,122,42,.25); color:#d4b46a; border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600; }
.conf-low    { display:inline-block; background:rgba(184,92,56,.25);  color:#e08060; border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600; }

/* Tile grid */
.tile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 1rem; }
.tile {
    background: #f5f0e8;
    border: 1px solid rgba(26,23,20,.1);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
.tile-label { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: #9c9489; margin-bottom: 5px; }
.tile-value { font-size: 1.15rem; font-weight: 700; color: #1a1714; line-height: 1.3; }
.tile-sub   { font-size: 12px; color: #6b6358; margin-top: 2px; }

/* Source card */
.src-card {
    background: #d4eaea;
    border: 1px solid rgba(45,106,106,.2);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.src-title { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #2d6a6a; margin-bottom: .75rem; font-weight: 600; }
.src-link { display: block; color: #2d6a6a; text-decoration: none; font-size: 13px; margin-bottom: 6px; line-height: 1.4; }
.src-meta { color: #6b9f9f; font-size: 11px; }

/* Analysis card */
.analysis-card {
    background: #ede8df;
    border: 1px solid rgba(26,23,20,.1);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    font-size: 14px;
    color: #3a342d;
    line-height: 1.7;
    margin-bottom: 1rem;
}
.analysis-title { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #9c9489; margin-bottom: .6rem; font-weight: 600; }

/* Disclaimer */
.disclaimer {
    font-size: 12px;
    color: #9c9489;
    line-height: 1.6;
    border-top: 1px solid rgba(26,23,20,.08);
    padding-top: .75rem;
    margin-top: .5rem;
}

/* Example chips */
.eg-chip {
    display: inline-block;
    background: #ede8df;
    border: 1px solid rgba(26,23,20,.1);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #3a342d;
    margin: 3px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ─── Suburb database ──────────────────────────────────────────────────────────
# Real 2025/26 median prices — Domain, Cotality, REIWA, REISA, state bodies
SUBURBS = {
    # SYDNEY
    "mosman nsw":           {"h": 5600000,  "u": 1550000, "g": "+3.2%",  "src": "Domain 2025"},
    "bellevue hill nsw":    {"h": 10000000, "u": 2800000, "g": "+3.2%",  "src": "Domain 2025"},
    "vaucluse nsw":         {"h": 8050000,  "u": 2200000, "g": "+4.1%",  "src": "Domain 2025"},
    "paddington nsw":       {"h": 3750000,  "u": 1050000, "g": "+15.1%", "src": "Domain 2025"},
    "bondi nsw":            {"h": 3100000,  "u": 1400000, "g": "+8.2%",  "src": "Cotality 2025"},
    "bondi beach nsw":      {"h": 3200000,  "u": 1450000, "g": "+8.5%",  "src": "Cotality 2025"},
    "double bay nsw":       {"h": 5200000,  "u": 1600000, "g": "+5.1%",  "src": "Domain 2025"},
    "rose bay nsw":         {"h": 4700000,  "u": 1350000, "g": "+4.8%",  "src": "Domain 2025"},
    "neutral bay nsw":      {"h": 2800000,  "u": 1050000, "g": "+6.2%",  "src": "Domain 2025"},
    "cremorne nsw":         {"h": 2650000,  "u": 950000,  "g": "+5.8%",  "src": "Domain 2025"},
    "cammeray nsw":         {"h": 3750000,  "u": 980000,  "g": "+29.0%", "src": "Domain 2025"},
    "north sydney nsw":     {"h": 2400000,  "u": 880000,  "g": "+6.5%",  "src": "Cotality 2025"},
    "balmain nsw":          {"h": 2150000,  "u": 920000,  "g": "+9.1%",  "src": "Domain 2025"},
    "birchgrove nsw":       {"h": 2400000,  "u": 1050000, "g": "+10.2%", "src": "Domain 2025"},
    "glebe nsw":            {"h": 1950000,  "u": 820000,  "g": "+7.8%",  "src": "Domain 2025"},
    "newtown nsw":          {"h": 1750000,  "u": 780000,  "g": "+8.5%",  "src": "Domain 2025"},
    "surry hills nsw":      {"h": 1850000,  "u": 820000,  "g": "+7.2%",  "src": "Domain 2025"},
    "manly nsw":            {"h": 3100000,  "u": 1150000, "g": "+9.3%",  "src": "Domain 2025"},
    "dee why nsw":          {"h": 1800000,  "u": 820000,  "g": "+11.2%", "src": "Domain 2025"},
    "avalon beach nsw":     {"h": 2450000,  "u": 980000,  "g": "+10.8%", "src": "Domain 2025"},
    "chatswood nsw":        {"h": 2650000,  "u": 980000,  "g": "+7.3%",  "src": "Cotality 2025"},
    "randwick nsw":         {"h": 2600000,  "u": 980000,  "g": "+8.1%",  "src": "Domain 2025"},
    "coogee nsw":           {"h": 2850000,  "u": 1100000, "g": "+8.8%",  "src": "Domain 2025"},
    "clovelly nsw":         {"h": 2900000,  "u": 1050000, "g": "+15.9%", "src": "Domain 2025"},
    "kensington nsw":       {"h": 2200000,  "u": 780000,  "g": "+6.5%",  "src": "Domain 2025"},
    "alexandria nsw":       {"h": 1800000,  "u": 820000,  "g": "+7.9%",  "src": "Domain 2025"},
    "redfern nsw":          {"h": 1650000,  "u": 770000,  "g": "+6.2%",  "src": "Cotality 2025"},
    "woollahra nsw":        {"h": 3500000,  "u": 1100000, "g": "+6.3%",  "src": "Domain 2025"},
    "parramatta nsw":       {"h": 1350000,  "u": 650000,  "g": "+5.4%",  "src": "Cotality 2025"},
    "penrith nsw":          {"h": 920000,   "u": 550000,  "g": "+4.2%",  "src": "Cotality 2025"},
    "liverpool nsw":        {"h": 950000,   "u": 560000,  "g": "+4.8%",  "src": "Cotality 2025"},
    "blacktown nsw":        {"h": 950000,   "u": 560000,  "g": "+5.2%",  "src": "Cotality 2025"},
    "bankstown nsw":        {"h": 1200000,  "u": 620000,  "g": "+21.0%", "src": "Domain 2025"},
    "castle hill nsw":      {"h": 1650000,  "u": 750000,  "g": "+5.4%",  "src": "Cotality 2025"},
    "hornsby nsw":          {"h": 1650000,  "u": 720000,  "g": "+5.8%",  "src": "Cotality 2025"},
    "epping nsw":           {"h": 1800000,  "u": 780000,  "g": "+6.1%",  "src": "Domain 2025"},
    # MELBOURNE
    "toorak vic":           {"h": 4125000,  "u": 1100000, "g": "+3.8%",  "src": "Domain 2025"},
    "south yarra vic":      {"h": 1800000,  "u": 720000,  "g": "+5.2%",  "src": "Domain 2025"},
    "st kilda vic":         {"h": 1650000,  "u": 620000,  "g": "+4.8%",  "src": "Cotality 2025"},
    "brighton vic":         {"h": 2650000,  "u": 850000,  "g": "+4.1%",  "src": "Domain 2025"},
    "hawthorn vic":         {"h": 2100000,  "u": 700000,  "g": "+4.6%",  "src": "Domain 2025"},
    "camberwell vic":       {"h": 2000000,  "u": 680000,  "g": "+4.2%",  "src": "Domain 2025"},
    "kew vic":              {"h": 2150000,  "u": 720000,  "g": "+4.5%",  "src": "Domain 2025"},
    "malvern vic":          {"h": 2200000,  "u": 730000,  "g": "+4.8%",  "src": "Domain 2025"},
    "richmond vic":         {"h": 1450000,  "u": 620000,  "g": "+5.1%",  "src": "Domain 2025"},
    "fitzroy vic":          {"h": 1500000,  "u": 650000,  "g": "+5.4%",  "src": "Domain 2025"},
    "carlton vic":          {"h": 1400000,  "u": 600000,  "g": "+4.9%",  "src": "Domain 2025"},
    "collingwood vic":      {"h": 1400000,  "u": 620000,  "g": "+5.2%",  "src": "Domain 2025"},
    "prahran vic":          {"h": 1550000,  "u": 650000,  "g": "+4.7%",  "src": "Domain 2025"},
    "armadale vic":         {"h": 1800000,  "u": 680000,  "g": "+4.3%",  "src": "Domain 2025"},
    "glen waverley vic":    {"h": 1350000,  "u": 600000,  "g": "+5.0%",  "src": "Cotality 2025"},
    "box hill vic":         {"h": 1200000,  "u": 580000,  "g": "+5.8%",  "src": "Cotality 2025"},
    "northcote vic":        {"h": 1350000,  "u": 600000,  "g": "+5.5%",  "src": "Domain 2025"},
    "brunswick vic":        {"h": 1300000,  "u": 580000,  "g": "+5.8%",  "src": "Domain 2025"},
    "essendon vic":         {"h": 1250000,  "u": 570000,  "g": "+4.9%",  "src": "Cotality 2025"},
    "footscray vic":        {"h": 900000,   "u": 480000,  "g": "+6.2%",  "src": "Domain 2025"},
    "williamstown vic":     {"h": 1350000,  "u": 590000,  "g": "+5.2%",  "src": "Domain 2025"},
    "frankston vic":        {"h": 750000,   "u": 420000,  "g": "+4.5%",  "src": "Cotality 2025"},
    "werribee vic":         {"h": 620000,   "u": 390000,  "g": "+5.8%",  "src": "Cotality 2025"},
    # BRISBANE
    "paddington qld":       {"h": 1400000,  "u": 620000,  "g": "+19.9%", "src": "Cotality 2025"},
    "hamilton qld":         {"h": 2100000,  "u": 800000,  "g": "+22.1%", "src": "Domain 2025"},
    "ascot qld":            {"h": 2250000,  "u": 820000,  "g": "+21.3%", "src": "Domain 2025"},
    "new farm qld":         {"h": 2000000,  "u": 750000,  "g": "+19.5%", "src": "Domain 2025"},
    "teneriffe qld":        {"h": 2200000,  "u": 900000,  "g": "+20.8%", "src": "Domain 2025"},
    "west end qld":         {"h": 1500000,  "u": 650000,  "g": "+17.4%", "src": "Domain 2025"},
    "coorparoo qld":        {"h": 1100000,  "u": 550000,  "g": "+18.9%", "src": "Domain 2025"},
    "bulimba qld":          {"h": 1500000,  "u": 650000,  "g": "+19.1%", "src": "Domain 2025"},
    "birkdale qld":         {"h": 1050000,  "u": 520000,  "g": "+25.0%", "src": "Domain 2025"},
    "springwood qld":       {"h": 750000,   "u": 420000,  "g": "+23.9%", "src": "Cotality 2026"},
    "indooroopilly qld":    {"h": 1250000,  "u": 580000,  "g": "+18.5%", "src": "Domain 2025"},
    "gold coast qld":       {"h": 1100000,  "u": 680000,  "g": "+14.2%", "src": "Cotality 2025"},
    "sunshine coast qld":   {"h": 1050000,  "u": 640000,  "g": "+12.8%", "src": "Cotality 2025"},
    "ipswich qld":          {"h": 620000,   "u": 380000,  "g": "+10.5%", "src": "Cotality 2025"},
    # PERTH
    "cottesloe wa":         {"h": 2800000,  "u": 950000,  "g": "+28.0%", "src": "REIWA 2025"},
    "dalkeith wa":          {"h": 3200000,  "u": 1100000, "g": "+26.5%", "src": "REIWA 2025"},
    "nedlands wa":          {"h": 2400000,  "u": 900000,  "g": "+25.8%", "src": "REIWA 2025"},
    "claremont wa":         {"h": 2100000,  "u": 820000,  "g": "+25.2%", "src": "REIWA 2025"},
    "peppermint grove wa":  {"h": 3500000,  "u": 1200000, "g": "+26.0%", "src": "REIWA 2025"},
    "subiaco wa":           {"h": 1750000,  "u": 720000,  "g": "+24.5%", "src": "REIWA 2025"},
    "fremantle wa":         {"h": 1350000,  "u": 600000,  "g": "+22.5%", "src": "REIWA 2025"},
    "scarborough wa":       {"h": 1200000,  "u": 580000,  "g": "+25.8%", "src": "REIWA 2025"},
    "mount lawley wa":      {"h": 1300000,  "u": 600000,  "g": "+24.2%", "src": "REIWA 2025"},
    "joondalup wa":         {"h": 820000,   "u": 450000,  "g": "+21.8%", "src": "REIWA 2025"},
    "mandurah wa":          {"h": 620000,   "u": 380000,  "g": "+18.5%", "src": "REIWA 2025"},
    # ADELAIDE
    "medindie sa":          {"h": 2200000,  "u": 800000,  "g": "+14.3%", "src": "REISA 2025"},
    "north adelaide sa":    {"h": 1800000,  "u": 700000,  "g": "+13.8%", "src": "REISA 2025"},
    "unley sa":             {"h": 1400000,  "u": 620000,  "g": "+13.5%", "src": "REISA 2025"},
    "rose park sa":         {"h": 1500000,  "u": 650000,  "g": "+13.9%", "src": "REISA 2025"},
    "glenelg sa":           {"h": 1250000,  "u": 590000,  "g": "+12.8%", "src": "REISA 2025"},
    "burnside sa":          {"h": 1350000,  "u": 600000,  "g": "+13.1%", "src": "REISA 2025"},
    "prospect sa":          {"h": 1000000,  "u": 510000,  "g": "+13.5%", "src": "Cotality 2025"},
    "salisbury sa":         {"h": 620000,   "u": 370000,  "g": "+15.7%", "src": "Cotality 2026"},
    "tea tree gully sa":    {"h": 680000,   "u": 400000,  "g": "+13.6%", "src": "Cotality 2026"},
    # CANBERRA
    "barton act":           {"h": 1650000,  "u": 750000,  "g": "+4.2%",  "src": "REIA ACT 2025"},
    "forrest act":          {"h": 2200000,  "u": 900000,  "g": "+4.8%",  "src": "REIA ACT 2025"},
    "manuka act":           {"h": 1800000,  "u": 750000,  "g": "+4.5%",  "src": "REIA ACT 2025"},
    "braddon act":          {"h": 1200000,  "u": 620000,  "g": "+3.8%",  "src": "REIA ACT 2025"},
    "belconnen act":        {"h": 850000,   "u": 480000,  "g": "+3.5%",  "src": "Cotality 2025"},
    # HOBART
    "battery point tas":    {"h": 1350000,  "u": 620000,  "g": "+2.1%",  "src": "REITAS 2025"},
    "sandy bay tas":        {"h": 1100000,  "u": 520000,  "g": "+1.8%",  "src": "REITAS 2025"},
    "north hobart tas":     {"h": 780000,   "u": 430000,  "g": "+1.5%",  "src": "REITAS 2025"},
    "west hobart tas":      {"h": 850000,   "u": 460000,  "g": "+1.7%",  "src": "REITAS 2025"},
    # DARWIN
    "larrakeyah nt":        {"h": 950000,   "u": 480000,  "g": "+22.8%", "src": "REINT 2025"},
    "fannie bay nt":        {"h": 1050000,  "u": 520000,  "g": "+22.5%", "src": "REINT 2025"},
    "nightcliff nt":        {"h": 780000,   "u": 420000,  "g": "+20.5%", "src": "REINT 2025"},
}

CITY_MEDIANS = {
    "nsw": {"h": 1450000, "u": 820000,  "city": "Sydney",    "g": "+5.2%"},
    "vic": {"h": 805000,  "u": 620000,  "city": "Melbourne", "g": "+2.1%"},
    "qld": {"h": 970000,  "u": 650000,  "city": "Brisbane",  "g": "+19.9%"},
    "wa":  {"h": 1032000, "u": 726000,  "city": "Perth",     "g": "+26.0%"},
    "sa":  {"h": 981000,  "u": 676000,  "city": "Adelaide",  "g": "+14.3%"},
    "act": {"h": 1100000, "u": 600000,  "city": "Canberra",  "g": "+4.5%"},
    "tas": {"h": 683000,  "u": 480000,  "city": "Hobart",    "g": "+1.8%"},
    "nt":  {"h": 680000,  "u": 420000,  "city": "Darwin",    "g": "+22.8%"},
}

MARKET_CONTEXT = {
    "nsw": "Sydney has softened slightly from its 2025 peak, though premium suburbs remain highly resilient.",
    "vic": "Melbourne is currently underperforming other capitals with modest growth, offering relative value.",
    "qld": "Brisbane continues its extraordinary run, with many suburbs posting 15–25% annual growth in 2025.",
    "wa":  "Perth has been the standout national performer, driven by strong wages, mining demand and low stock.",
    "sa":  "Adelaide remains Australia's affordability story, with consistent double-digit growth since 2022.",
    "act": "Canberra has stabilised after strong post-COVID gains, with modest growth across most suburbs.",
    "tas": "Hobart is experiencing a mild softening after years of rapid price appreciation.",
    "nt":  "Darwin has delivered surprising growth driven by infrastructure and defence investment.",
}

# ─── Helper functions ─────────────────────────────────────────────────────────
def fmt_price(n):
    if n >= 1_000_000:
        val = n / 1_000_000
        return f"${val:.2f}m".rstrip('0').rstrip('.') + 'm' if val != int(val) else f"${int(val)}m"
    return f"${n:,.0f}"

def parse_address(raw):
    s = raw.strip()
    is_unit = bool(re.match(r'^\d+\/|^unit\s|^apt\s|^apartment\s|^flat\s', s, re.I))
    pc_match = re.search(r'\b(\d{4})\b', s)
    postcode = pc_match.group(1) if pc_match else ""
    state_match = re.search(r'\b(NSW|VIC|QLD|WA|SA|ACT|TAS|NT)\b', s, re.I)
    state = state_match.group(1).lower() if state_match else None
    suburb = None
    if state_match:
        before = s[:state_match.start()].strip().rstrip(',').strip()
        words = before.split()
        for length in range(min(3, len(words)), 0, -1):
            candidate = ' '.join(words[-length:]).lower()
            if f"{candidate} {state}" in SUBURBS:
                suburb = candidate
                break
        if not suburb and words:
            suburb = words[-1].lower()
    return {"raw": s, "suburb": suburb, "state": state, "postcode": postcode, "is_unit": is_unit}

def valuate(parsed):
    suburb, state, is_unit = parsed["suburb"], parsed["state"], parsed["is_unit"]
    key = f"{suburb} {state}" if suburb and state else None
    data = SUBURBS.get(key)
    city = CITY_MEDIANS.get(state) if state else None

    if data:
        median = data["u"] if is_unit else data["h"]
        source = data["src"]
        confidence = "high"
        suburb_display = suburb.title() if suburb else ""
        growth = data["g"]
    elif city:
        median = city["u"] if is_unit else city["h"]
        source = "Cotality/Domain 2025–26 (city median)"
        confidence = "medium"
        suburb_display = suburb.title() if suburb else city["city"]
        growth = city["g"]
    else:
        median = 728000 if is_unit else 1005000
        source = "Cotality national median 2026"
        confidence = "low"
        suburb_display = suburb.title() if suburb else "Unknown"
        growth = "+5%"

    spread = 0.15 if is_unit else 0.18
    lo = round(median * (1 - spread) / 25000) * 25000
    hi = round(median * (1 + spread) / 25000) * 25000

    return {
        "estimate": fmt_price(median),
        "lo": fmt_price(lo), "hi": fmt_price(hi),
        "median": median,
        "confidence": confidence,
        "source": source,
        "suburb_display": suburb_display,
        "state": state.upper() if state else "",
        "growth": growth,
        "prop_type": "Unit / Apartment" if is_unit else "House",
    }

def make_links(parsed, val):
    suburb_slug = val["suburb_display"].lower().replace(" ", "-")
    state_lc = parsed["state"].lower() if parsed["state"] else ""
    pc = parsed["postcode"]
    ptype = "unit+apartment" if parsed["is_unit"] else "house"
    return [
        {"label": f"Domain — {val['suburb_display']} for sale",
         "url": f"https://www.domain.com.au/sale/?suburb={val['suburb_display']}+{val['state']}&ptype={ptype}",
         "meta": "Current listings and sold prices"},
        {"label": f"Domain — {val['suburb_display']} suburb profile",
         "url": f"https://www.domain.com.au/suburb-profile/{suburb_slug}-{state_lc}-{pc}",
         "meta": "Median prices, auction results, market trends"},
        {"label": f"realestate.com.au — {val['suburb_display']} listings",
         "url": f"https://www.realestate.com.au/buy/in-{suburb_slug},+{state_lc}/list-1",
         "meta": "Current listings and sales history"},
        {"label": "PropertyValue.com.au — Free AVM estimate",
         "url": "https://propertyvalue.com.au/",
         "meta": "Enter the exact address for a free automated estimate"},
        {"label": f"SQM Research — {pc} weekly prices",
         "url": f"https://sqmresearch.com.au/weekly-residential-property-prices.php?postcode={pc}&t=1",
         "meta": "Weekly asking prices and vacancy rates"},
        {"label": "CoreLogic — Property analytics",
         "url": "https://www.corelogic.com.au/",
         "meta": "Institutional-grade property data"},
    ]

# ─── UI ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag">✓ 100% Free · No sign-up · No API costs</div>
  <h1>What is your property <span>worth?</span></h1>
  <p>Instant market valuation for any Australian address using real 2025/26 suburb median data,
  with direct links to Domain, realestate.com.au and CoreLogic.</p>
</div>
""", unsafe_allow_html=True)

# Search
addr = st.text_input(
    "Enter an Australian address",
    placeholder="e.g. 14 Bay Street, Mosman NSW 2088",
    label_visibility="collapsed",
)

col1, col2 = st.columns([3, 1])
with col2:
    go = st.button("Value this →", use_container_width=True, type="primary")

# Examples
st.markdown("**Try an example:**")
examples = [
    "22 The Crescent, Toorak VIC 3142",
    "5/14 Marine Parade, Bondi NSW 2026",
    "9 Riverview Terrace, Hamilton QLD 4007",
    "3 Circe Jones Drive, Cottesloe WA 6011",
    "18 Dutton Terrace, Medindie SA 5081",
    "7 Salamanca Place, Battery Point TAS 7004",
]
eg_cols = st.columns(3)
for i, eg in enumerate(examples):
    with eg_cols[i % 3]:
        if st.button(eg, key=f"eg{i}", use_container_width=True):
            addr = eg
            go = True

st.divider()

# ─── Result ───────────────────────────────────────────────────────────────────
if (go or addr) and addr.strip():
    parsed = parse_address(addr)
    val = valuate(parsed)
    links = make_links(parsed, val)

    conf_labels = {
        "high":   ("✓ High confidence — suburb data matched", "conf-high"),
        "medium": ("~ Medium confidence — city median used", "conf-medium"),
        "low":    ("⚠ Low confidence — check address format", "conf-low"),
    }
    conf_text, conf_class = conf_labels[val["confidence"]]

    # Big valuation card
    st.markdown(f"""
    <div class="val-card">
      <div class="val-label">Estimated Market Value</div>
      <div class="val-amount">{val['estimate']}</div>
      <div class="val-range">Indicative range: {val['lo']} – {val['hi']}</div>
      <span class="{conf_class}">{conf_text}</span>
    </div>
    """, unsafe_allow_html=True)

    # Metric tiles
    st.markdown(f"""
    <div class="tile-grid">
      <div class="tile">
        <div class="tile-label">Property Type</div>
        <div class="tile-value">{val['prop_type']}</div>
        <div class="tile-sub">Detected from address</div>
      </div>
      <div class="tile">
        <div class="tile-label">Suburb Median</div>
        <div class="tile-value">{val['estimate']}</div>
        <div class="tile-sub">{val['suburb_display']} · {val['source']}</div>
      </div>
      <div class="tile">
        <div class="tile-label">12-Month Growth</div>
        <div class="tile-value">{val['growth']}</div>
        <div class="tile-sub">{val['suburb_display']} · {val['state']}</div>
      </div>
      <div class="tile">
        <div class="tile-label">Price Range</div>
        <div class="tile-value">{val['lo']} – {val['hi']}</div>
        <div class="tile-sub">±{'15' if val['prop_type'] == 'Unit / Apartment' else '18'}% of median</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Analysis
    mkt = MARKET_CONTEXT.get(parsed["state"], "The national market continues to be supported by supply shortages and population growth.")
    conf_note = {
        "high":   f"This estimate is based on real suburb-level median data for {val['suburb_display']} from {val['source']}.",
        "medium": f"This estimate uses the {val['state']} city-wide median — suburb-specific data was not available for {val['suburb_display']}.",
        "low":    "No suburb data matched. Try including suburb and state in your address, e.g. '14 Main St, Suburb NSW 2000'.",
    }[val["confidence"]]

    st.markdown(f"""
    <div class="analysis-card">
      <div class="analysis-title">Valuation Analysis</div>
      {conf_note} The estimated value of {val['estimate']} (range: {val['lo']} – {val['hi']}) reflects current
      {val['suburb_display']} {val['prop_type'].lower()} market conditions, with the suburb recording
      {val['growth']} growth over the past 12 months. {mkt}
      Use the source links below to verify against recent comparable sales.
    </div>
    """, unsafe_allow_html=True)

    # Sources
    src_html = "".join([
        f'<a class="src-link" href="{l["url"]}" target="_blank">↗ {l["label"]}<br><span class="src-meta">{l["meta"]}</span></a>'
        for l in links
    ])
    st.markdown(f"""
    <div class="src-card">
      <div class="src-title">Sources &amp; Further Research</div>
      {src_html}
    </div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
    <strong>Disclaimer:</strong> This is a free informational estimate based on publicly available suburb
    median data. It is not a formal property valuation and should not be relied upon for mortgage, legal,
    or financial decisions. For a certified valuation, engage a licensed <strong>Certified Practising Valuer (CPV)</strong>.
    </div>
    """, unsafe_allow_html=True)

elif not addr:
    st.info("💡 Enter any Australian address above, or click one of the examples to get started.")
