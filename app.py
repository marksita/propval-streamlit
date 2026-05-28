import streamlit as st
import re
import urllib.parse
import urllib.request
import json
import time

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PropVal AU — Australian Property Valuation",
    page_icon="🏠",
    layout="centered",
)

# ─── REA-style CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');

#MainMenu, footer, header { visibility: hidden; }
html, body, [class*="css"] { font-family: 'Lato', 'Helvetica Neue', Arial, sans-serif; }

/* ── Top nav bar ── */
.rea-nav {
    background: #e8172b;
    margin: -1rem -1rem 0;
    padding: .75rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.rea-logo {
    font-size: 1.35rem;
    font-weight: 900;
    color: white;
    letter-spacing: -.02em;
    line-height: 1;
}
.rea-logo span { opacity: .75; font-weight: 300; }
.rea-nav-links {
    display: flex;
    gap: 1.5rem;
    margin-left: auto;
}
.rea-nav-link {
    color: rgba(255,255,255,.85);
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    text-transform: uppercase;
    letter-spacing: .04em;
}
.rea-nav-link:hover { color: white; }

/* ── Hero search section ── */
.rea-hero {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    margin: 0 -1rem;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.rea-hero::before {
    content: '';
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.rea-hero-title {
    font-size: 2.4rem;
    font-weight: 900;
    color: white;
    margin-bottom: .5rem;
    line-height: 1.1;
    position: relative;
}
.rea-hero-title span { color: #e8172b; }
.rea-hero-sub {
    font-size: .95rem;
    color: rgba(255,255,255,.6);
    margin-bottom: 2rem;
    position: relative;
}

/* ── Search bar ── */
.search-container {
    max-width: 640px;
    margin: 0 auto;
    position: relative;
}
.search-wrap {
    display: flex;
    background: white;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,.4);
    position: relative;
    z-index: 10;
}
.search-icon {
    display: flex; align-items: center; padding: 0 14px;
    color: #aaa; font-size: 18px;
}
.search-input-styled {
    flex: 1; border: none; outline: none;
    font-family: 'Lato', sans-serif;
    font-size: 15px; color: #333;
    padding: 14px 8px; background: transparent;
}
.search-btn-red {
    background: #e8172b; color: white;
    border: none; padding: 14px 24px;
    font-family: 'Lato', sans-serif;
    font-size: 14px; font-weight: 700;
    cursor: pointer; white-space: nowrap;
    text-transform: uppercase; letter-spacing: .05em;
    transition: background .15s;
}
.search-btn-red:hover { background: #c01020; }

/* Autocomplete dropdown */
.autocomplete-dropdown {
    position: absolute; top: 100%; left: 0; right: 0;
    background: white;
    border-radius: 0 0 6px 6px;
    box-shadow: 0 8px 24px rgba(0,0,0,.15);
    z-index: 100;
    overflow: hidden;
}
.autocomplete-item {
    padding: 10px 16px;
    font-size: 14px; color: #333;
    cursor: pointer;
    display: flex; align-items: center; gap: 10px;
    border-bottom: 1px solid #f5f5f5;
    transition: background .1s;
}
.autocomplete-item:hover { background: #fff5f5; }
.autocomplete-item:last-child { border-bottom: none; }
.autocomplete-pin { color: #e8172b; font-size: 16px; flex-shrink: 0; }
.autocomplete-main { font-weight: 700; }
.autocomplete-sub { color: #888; font-size: 12px; }

/* ── Tabs ── */
.rea-tabs {
    display: flex; gap: 0;
    background: #f5f5f5;
    border-bottom: 2px solid #e0e0e0;
    margin: 0 -1rem 2rem;
    padding: 0 2rem;
}
.rea-tab {
    padding: 12px 20px;
    font-size: 13px; font-weight: 700;
    color: #666;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: .04em;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: color .15s;
}
.rea-tab.active { color: #e8172b; border-bottom-color: #e8172b; }

/* ── Result card ── */
.result-header {
    display: flex; align-items: flex-start;
    gap: 1rem; margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
}
.result-pin { font-size: 2rem; flex-shrink: 0; }
.result-address-text {
    font-size: 1.3rem; font-weight: 900;
    color: #1a1a1a; line-height: 1.2; margin-bottom: 3px;
}
.result-suburb { font-size: .9rem; color: #888; }

/* Big value */
.val-hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #2d1a3e 100%);
    border-radius: 8px; padding: 2rem;
    margin-bottom: 1rem; color: white;
    position: relative; overflow: hidden;
}
.val-hero::after {
    content: '🏠';
    position: absolute; right: 1.5rem; bottom: 1rem;
    font-size: 5rem; opacity: .07;
}
.val-hero-label {
    font-size: 11px; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase;
    color: rgba(255,255,255,.5); margin-bottom: 8px;
}
.val-hero-amount {
    font-size: 3.2rem; font-weight: 900;
    line-height: 1; margin-bottom: 6px;
    letter-spacing: -.02em;
}
.val-hero-range { font-size: .9rem; color: rgba(255,255,255,.55); margin-bottom: 1.25rem; }
.conf-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 12px; font-weight: 700;
    padding: 5px 14px; border-radius: 4px;
}
.conf-high   { background: rgba(0,180,80,.2);  color: #4ade80; }
.conf-medium { background: rgba(255,180,0,.2); color: #fbbf24; }
.conf-low    { background: rgba(232,23,43,.2); color: #f87171; }

/* ── Stats grid ── */
.stats-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 10px; margin-bottom: 1rem;
}
.stat-card {
    background: white;
    border: 1px solid #eee;
    border-top: 3px solid #e8172b;
    border-radius: 4px;
    padding: .9rem 1rem;
    text-align: center;
}
.stat-value { font-size: 1.4rem; font-weight: 900; color: #1a1a1a; line-height: 1; }
.stat-label { font-size: 11px; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: .06em; font-weight: 700; }
.stat-sub   { font-size: 11px; color: #aaa; margin-top: 2px; }

/* ── Market insights ── */
.insights-card {
    background: white; border: 1px solid #eee;
    border-radius: 6px; padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.insights-title {
    font-size: 13px; font-weight: 900;
    text-transform: uppercase; letter-spacing: .06em;
    color: #1a1a1a; margin-bottom: .9rem;
    display: flex; align-items: center; gap: 8px;
}
.insights-title::before {
    content: ''; display: block;
    width: 3px; height: 16px;
    background: #e8172b; border-radius: 2px;
}
.insights-body { font-size: 14px; color: #444; line-height: 1.7; }

/* ── Sources ── */
.sources-card {
    background: #fff8f8; border: 1px solid #fddde0;
    border-radius: 6px; padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.sources-title {
    font-size: 13px; font-weight: 900;
    text-transform: uppercase; letter-spacing: .06em;
    color: #e8172b; margin-bottom: .9rem;
    display: flex; align-items: center; gap: 8px;
}
.sources-title::before {
    content: ''; display: block;
    width: 3px; height: 16px;
    background: #e8172b; border-radius: 2px;
}
.src-item {
    display: flex; align-items: flex-start;
    gap: 8px; margin-bottom: 8px;
    font-size: 13px;
}
.src-item:last-child { margin-bottom: 0; }
.src-arrow { color: #e8172b; flex-shrink: 0; font-weight: 900; margin-top: 1px; }
.src-link-text { color: #1a6b9a; text-decoration: none; line-height: 1.4; }
.src-link-text:hover { text-decoration: underline; }
.src-meta { color: #aaa; font-size: 11px; display: block; }

/* ── Disclaimer ── */
.disclaimer {
    background: #f9f9f9; border-left: 3px solid #ddd;
    padding: .75rem 1rem; font-size: 12px;
    color: #999; line-height: 1.6; border-radius: 0 4px 4px 0;
    margin-bottom: 1rem;
}

/* ── Examples ── */
.examples-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: .75rem; }
.eg-pill {
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 20px; padding: 5px 14px;
    font-size: 12px; color: rgba(255,255,255,.8);
    cursor: pointer; transition: all .15s; white-space: nowrap;
}
.eg-pill:hover { background: rgba(255,255,255,.2); color: white; }

/* Streamlit tweaks */
.stTextInput input {
    border: none !important; outline: none !important;
    box-shadow: none !important; padding: 0 !important;
}
div[data-testid="stButton"] > button {
    border-radius: 4px !important;
    font-weight: 700 !important;
    letter-spacing: .04em !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Suburb database ───────────────────────────────────────────────────────────
SUBURBS = {
    # SYDNEY
    "mosman nsw":          {"h":5600000,  "u":1550000, "g":"+3.2%",  "src":"Domain 2025"},
    "bellevue hill nsw":   {"h":10000000, "u":2800000, "g":"+3.2%",  "src":"Domain 2025"},
    "vaucluse nsw":        {"h":8050000,  "u":2200000, "g":"+4.1%",  "src":"Domain 2025"},
    "paddington nsw":      {"h":3750000,  "u":1050000, "g":"+15.1%", "src":"Domain 2025"},
    "bondi nsw":           {"h":3100000,  "u":1400000, "g":"+8.2%",  "src":"Cotality 2025"},
    "bondi beach nsw":     {"h":3200000,  "u":1450000, "g":"+8.5%",  "src":"Cotality 2025"},
    "double bay nsw":      {"h":5200000,  "u":1600000, "g":"+5.1%",  "src":"Domain 2025"},
    "rose bay nsw":        {"h":4700000,  "u":1350000, "g":"+4.8%",  "src":"Domain 2025"},
    "neutral bay nsw":     {"h":2800000,  "u":1050000, "g":"+6.2%",  "src":"Domain 2025"},
    "cremorne nsw":        {"h":2650000,  "u":950000,  "g":"+5.8%",  "src":"Domain 2025"},
    "cammeray nsw":        {"h":3750000,  "u":980000,  "g":"+29.0%", "src":"Domain 2025"},
    "north sydney nsw":    {"h":2400000,  "u":880000,  "g":"+6.5%",  "src":"Cotality 2025"},
    "balmain nsw":         {"h":2150000,  "u":920000,  "g":"+9.1%",  "src":"Domain 2025"},
    "birchgrove nsw":      {"h":2400000,  "u":1050000, "g":"+10.2%", "src":"Domain 2025"},
    "glebe nsw":           {"h":1950000,  "u":820000,  "g":"+7.8%",  "src":"Domain 2025"},
    "newtown nsw":         {"h":1750000,  "u":780000,  "g":"+8.5%",  "src":"Domain 2025"},
    "surry hills nsw":     {"h":1850000,  "u":820000,  "g":"+7.2%",  "src":"Domain 2025"},
    "manly nsw":           {"h":3100000,  "u":1150000, "g":"+9.3%",  "src":"Domain 2025"},
    "dee why nsw":         {"h":1800000,  "u":820000,  "g":"+11.2%", "src":"Domain 2025"},
    "avalon beach nsw":    {"h":2450000,  "u":980000,  "g":"+10.8%", "src":"Domain 2025"},
    "chatswood nsw":       {"h":2650000,  "u":980000,  "g":"+7.3%",  "src":"Cotality 2025"},
    "randwick nsw":        {"h":2600000,  "u":980000,  "g":"+8.1%",  "src":"Domain 2025"},
    "coogee nsw":          {"h":2850000,  "u":1100000, "g":"+8.8%",  "src":"Domain 2025"},
    "clovelly nsw":        {"h":2900000,  "u":1050000, "g":"+15.9%", "src":"Domain 2025"},
    "kensington nsw":      {"h":2200000,  "u":780000,  "g":"+6.5%",  "src":"Domain 2025"},
    "alexandria nsw":      {"h":1800000,  "u":820000,  "g":"+7.9%",  "src":"Domain 2025"},
    "redfern nsw":         {"h":1650000,  "u":770000,  "g":"+6.2%",  "src":"Cotality 2025"},
    "woollahra nsw":       {"h":3500000,  "u":1100000, "g":"+6.3%",  "src":"Domain 2025"},
    "parramatta nsw":      {"h":1350000,  "u":650000,  "g":"+5.4%",  "src":"Cotality 2025"},
    "penrith nsw":         {"h":920000,   "u":550000,  "g":"+4.2%",  "src":"Cotality 2025"},
    "liverpool nsw":       {"h":950000,   "u":560000,  "g":"+4.8%",  "src":"Cotality 2025"},
    "blacktown nsw":       {"h":950000,   "u":560000,  "g":"+5.2%",  "src":"Cotality 2025"},
    "bankstown nsw":       {"h":1200000,  "u":620000,  "g":"+21.0%", "src":"Domain 2025"},
    "castle hill nsw":     {"h":1650000,  "u":750000,  "g":"+5.4%",  "src":"Cotality 2025"},
    "hornsby nsw":         {"h":1650000,  "u":720000,  "g":"+5.8%",  "src":"Cotality 2025"},
    "epping nsw":          {"h":1800000,  "u":780000,  "g":"+6.1%",  "src":"Domain 2025"},
    "kogarah nsw":         {"h":1400000,  "u":670000,  "g":"+5.9%",  "src":"Cotality 2025"},
    "hurstville nsw":      {"h":1350000,  "u":650000,  "g":"+5.7%",  "src":"Cotality 2025"},
    # MELBOURNE
    "toorak vic":          {"h":4125000,  "u":1100000, "g":"+3.8%",  "src":"Domain 2025"},
    "south yarra vic":     {"h":1800000,  "u":720000,  "g":"+5.2%",  "src":"Domain 2025"},
    "st kilda vic":        {"h":1650000,  "u":620000,  "g":"+4.8%",  "src":"Cotality 2025"},
    "brighton vic":        {"h":2650000,  "u":850000,  "g":"+4.1%",  "src":"Domain 2025"},
    "hawthorn vic":        {"h":2100000,  "u":700000,  "g":"+4.6%",  "src":"Domain 2025"},
    "camberwell vic":      {"h":2000000,  "u":680000,  "g":"+4.2%",  "src":"Domain 2025"},
    "kew vic":             {"h":2150000,  "u":720000,  "g":"+4.5%",  "src":"Domain 2025"},
    "malvern vic":         {"h":2200000,  "u":730000,  "g":"+4.8%",  "src":"Domain 2025"},
    "richmond vic":        {"h":1450000,  "u":620000,  "g":"+5.1%",  "src":"Domain 2025"},
    "fitzroy vic":         {"h":1500000,  "u":650000,  "g":"+5.4%",  "src":"Domain 2025"},
    "carlton vic":         {"h":1400000,  "u":600000,  "g":"+4.9%",  "src":"Domain 2025"},
    "collingwood vic":     {"h":1400000,  "u":620000,  "g":"+5.2%",  "src":"Domain 2025"},
    "prahran vic":         {"h":1550000,  "u":650000,  "g":"+4.7%",  "src":"Domain 2025"},
    "armadale vic":        {"h":1800000,  "u":680000,  "g":"+4.3%",  "src":"Domain 2025"},
    "glen waverley vic":   {"h":1350000,  "u":600000,  "g":"+5.0%",  "src":"Cotality 2025"},
    "box hill vic":        {"h":1200000,  "u":580000,  "g":"+5.8%",  "src":"Cotality 2025"},
    "northcote vic":       {"h":1350000,  "u":600000,  "g":"+5.5%",  "src":"Domain 2025"},
    "brunswick vic":       {"h":1300000,  "u":580000,  "g":"+5.8%",  "src":"Domain 2025"},
    "essendon vic":        {"h":1250000,  "u":570000,  "g":"+4.9%",  "src":"Cotality 2025"},
    "footscray vic":       {"h":900000,   "u":480000,  "g":"+6.2%",  "src":"Domain 2025"},
    "williamstown vic":    {"h":1350000,  "u":590000,  "g":"+5.2%",  "src":"Domain 2025"},
    "frankston vic":       {"h":750000,   "u":420000,  "g":"+4.5%",  "src":"Cotality 2025"},
    "werribee vic":        {"h":620000,   "u":390000,  "g":"+5.8%",  "src":"Cotality 2025"},
    "doncaster vic":       {"h":1250000,  "u":590000,  "g":"+5.1%",  "src":"Cotality 2025"},
    # BRISBANE
    "paddington qld":      {"h":1400000,  "u":620000,  "g":"+19.9%", "src":"Cotality 2025"},
    "hamilton qld":        {"h":2100000,  "u":800000,  "g":"+22.1%", "src":"Domain 2025"},
    "ascot qld":           {"h":2250000,  "u":820000,  "g":"+21.3%", "src":"Domain 2025"},
    "new farm qld":        {"h":2000000,  "u":750000,  "g":"+19.5%", "src":"Domain 2025"},
    "teneriffe qld":       {"h":2200000,  "u":900000,  "g":"+20.8%", "src":"Domain 2025"},
    "west end qld":        {"h":1500000,  "u":650000,  "g":"+17.4%", "src":"Domain 2025"},
    "coorparoo qld":       {"h":1100000,  "u":550000,  "g":"+18.9%", "src":"Domain 2025"},
    "bulimba qld":         {"h":1500000,  "u":650000,  "g":"+19.1%", "src":"Domain 2025"},
    "birkdale qld":        {"h":1050000,  "u":520000,  "g":"+25.0%", "src":"Domain 2025"},
    "springwood qld":      {"h":750000,   "u":420000,  "g":"+23.9%", "src":"Cotality 2026"},
    "indooroopilly qld":   {"h":1250000,  "u":580000,  "g":"+18.5%", "src":"Domain 2025"},
    "gold coast qld":      {"h":1100000,  "u":680000,  "g":"+14.2%", "src":"Cotality 2025"},
    "sunshine coast qld":  {"h":1050000,  "u":640000,  "g":"+12.8%", "src":"Cotality 2025"},
    "ipswich qld":         {"h":620000,   "u":380000,  "g":"+10.5%", "src":"Cotality 2025"},
    "toowoomba qld":       {"h":550000,   "u":330000,  "g":"+8.2%",  "src":"Cotality 2025"},
    # PERTH
    "cottesloe wa":        {"h":2800000,  "u":950000,  "g":"+28.0%", "src":"REIWA 2025"},
    "dalkeith wa":         {"h":3200000,  "u":1100000, "g":"+26.5%", "src":"REIWA 2025"},
    "nedlands wa":         {"h":2400000,  "u":900000,  "g":"+25.8%", "src":"REIWA 2025"},
    "claremont wa":        {"h":2100000,  "u":820000,  "g":"+25.2%", "src":"REIWA 2025"},
    "peppermint grove wa": {"h":3500000,  "u":1200000, "g":"+26.0%", "src":"REIWA 2025"},
    "subiaco wa":          {"h":1750000,  "u":720000,  "g":"+24.5%", "src":"REIWA 2025"},
    "fremantle wa":        {"h":1350000,  "u":600000,  "g":"+22.5%", "src":"REIWA 2025"},
    "scarborough wa":      {"h":1200000,  "u":580000,  "g":"+25.8%", "src":"REIWA 2025"},
    "mount lawley wa":     {"h":1300000,  "u":600000,  "g":"+24.2%", "src":"REIWA 2025"},
    "joondalup wa":        {"h":820000,   "u":450000,  "g":"+21.8%", "src":"REIWA 2025"},
    "mandurah wa":         {"h":620000,   "u":380000,  "g":"+18.5%", "src":"REIWA 2025"},
    "leederville wa":      {"h":1450000,  "u":650000,  "g":"+23.8%", "src":"REIWA 2025"},
    # ADELAIDE
    "medindie sa":         {"h":2200000,  "u":800000,  "g":"+14.3%", "src":"REISA 2025"},
    "north adelaide sa":   {"h":1800000,  "u":700000,  "g":"+13.8%", "src":"REISA 2025"},
    "unley sa":            {"h":1400000,  "u":620000,  "g":"+13.5%", "src":"REISA 2025"},
    "rose park sa":        {"h":1500000,  "u":650000,  "g":"+13.9%", "src":"REISA 2025"},
    "glenelg sa":          {"h":1250000,  "u":590000,  "g":"+12.8%", "src":"REISA 2025"},
    "burnside sa":         {"h":1350000,  "u":600000,  "g":"+13.1%", "src":"REISA 2025"},
    "prospect sa":         {"h":1000000,  "u":510000,  "g":"+13.5%", "src":"Cotality 2025"},
    "salisbury sa":        {"h":620000,   "u":370000,  "g":"+15.7%", "src":"Cotality 2026"},
    "tea tree gully sa":   {"h":680000,   "u":400000,  "g":"+13.6%", "src":"Cotality 2026"},
    # CANBERRA
    "barton act":          {"h":1650000,  "u":750000,  "g":"+4.2%",  "src":"REIA ACT 2025"},
    "forrest act":         {"h":2200000,  "u":900000,  "g":"+4.8%",  "src":"REIA ACT 2025"},
    "manuka act":          {"h":1800000,  "u":750000,  "g":"+4.5%",  "src":"REIA ACT 2025"},
    "braddon act":         {"h":1200000,  "u":620000,  "g":"+3.8%",  "src":"REIA ACT 2025"},
    "belconnen act":       {"h":850000,   "u":480000,  "g":"+3.5%",  "src":"Cotality 2025"},
    "tuggeranong act":     {"h":780000,   "u":460000,  "g":"+3.2%",  "src":"Cotality 2025"},
    # HOBART
    "battery point tas":   {"h":1350000,  "u":620000,  "g":"+2.1%",  "src":"REITAS 2025"},
    "sandy bay tas":       {"h":1100000,  "u":520000,  "g":"+1.8%",  "src":"REITAS 2025"},
    "north hobart tas":    {"h":780000,   "u":430000,  "g":"+1.5%",  "src":"REITAS 2025"},
    "west hobart tas":     {"h":850000,   "u":460000,  "g":"+1.7%",  "src":"REITAS 2025"},
    # DARWIN
    "larrakeyah nt":       {"h":950000,   "u":480000,  "g":"+22.8%", "src":"REINT 2025"},
    "fannie bay nt":       {"h":1050000,  "u":520000,  "g":"+22.5%", "src":"REINT 2025"},
    "nightcliff nt":       {"h":780000,   "u":420000,  "g":"+20.5%", "src":"REINT 2025"},
}

CITY_MEDIANS = {
    "nsw": {"h":1450000,"u":820000, "city":"Sydney",    "g":"+5.2%"},
    "vic": {"h":805000, "u":620000, "city":"Melbourne", "g":"+2.1%"},
    "qld": {"h":970000, "u":650000, "city":"Brisbane",  "g":"+19.9%"},
    "wa":  {"h":1032000,"u":726000, "city":"Perth",     "g":"+26.0%"},
    "sa":  {"h":981000, "u":676000, "city":"Adelaide",  "g":"+14.3%"},
    "act": {"h":1100000,"u":600000, "city":"Canberra",  "g":"+4.5%"},
    "tas": {"h":683000, "u":480000, "city":"Hobart",    "g":"+1.8%"},
    "nt":  {"h":680000, "u":420000, "city":"Darwin",    "g":"+22.8%"},
}

MARKET_CONTEXT = {
    "nsw": "Sydney has softened slightly from its 2025 peak, though premium suburbs remain highly resilient with strong buyer competition.",
    "vic": "Melbourne is currently the most affordable of Australia's major capitals with modest growth, offering good relative value for buyers.",
    "qld": "Brisbane continues its extraordinary run — many suburbs posted 15–25% growth in 2025, underpinned by strong interstate migration.",
    "wa":  "Perth remains the standout national performer, driven by mining sector wages, low stock levels and significant population growth.",
    "sa":  "Adelaide is Australia's affordability story with consistent double-digit annual growth since 2022, supported by lifestyle appeal.",
    "act": "Canberra has stabilised after strong post-COVID gains, with steady government employment underpinning moderate price growth.",
    "tas": "Hobart is experiencing a gentle softening after years of rapid appreciation, with stock levels gradually improving.",
    "nt":  "Darwin has surprised analysts with strong growth driven by defence investment, infrastructure projects and improving amenity.",
}

EXAMPLES = [
    "22 The Crescent, Toorak VIC 3142",
    "5/14 Marine Parade, Bondi NSW 2026",
    "9 Riverview Terrace, Hamilton QLD 4007",
    "3 Circe Jones Drive, Cottesloe WA 6011",
    "18 Dutton Terrace, Medindie SA 5081",
    "7 Salamanca Place, Battery Point TAS 7004",
]

# ─── Address autocomplete via Nominatim (free, no key) ────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_suggestions(query: str):
    if len(query) < 4:
        return []
    try:
        q = urllib.parse.quote(query + ", Australia")
        url = f"https://nominatim.openstreetmap.org/search?q={q}&countrycodes=au&addressdetails=1&limit=6&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "PropValAU/1.0 streamlit-app"})
        with urllib.request.urlopen(req, timeout=3) as r:
            results = json.loads(r.read())
        suggestions = []
        for item in results:
            addr = item.get("address", {})
            display = item.get("display_name", "")
            # Build a clean AU-style address
            parts = []
            if addr.get("house_number") and addr.get("road"):
                parts.append(f"{addr['house_number']} {addr['road'].title()}")
            elif addr.get("road"):
                parts.append(addr["road"].title())
            suburb = addr.get("suburb") or addr.get("town") or addr.get("city_district") or addr.get("village") or ""
            state = addr.get("state", "")
            postcode = addr.get("postcode", "")
            # Map state names to abbreviations
            state_map = {
                "New South Wales":"NSW","Victoria":"VIC","Queensland":"QLD",
                "Western Australia":"WA","South Australia":"SA","Tasmania":"TAS",
                "Australian Capital Territory":"ACT","Northern Territory":"NT"
            }
            state_abbr = state_map.get(state, state[:3].upper() if state else "")
            if suburb: parts.append(suburb.title())
            if state_abbr: parts.append(state_abbr)
            if postcode: parts.append(postcode)
            clean = ", ".join(parts) if parts else display.split(",")[0]
            if clean and len(clean) > 5:
                suggestions.append({"display": clean, "full": display})
        # Deduplicate
        seen = set()
        unique = []
        for s in suggestions:
            if s["display"] not in seen:
                seen.add(s["display"])
                unique.append(s)
        return unique[:5]
    except Exception:
        return []

# ─── Core logic ───────────────────────────────────────────────────────────────
def fmt_price(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return f"${s}m"
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
        before = s[:state_match.start()].strip().rstrip(",").strip()
        words = before.split()
        for length in range(min(3, len(words)), 0, -1):
            candidate = " ".join(words[-length:]).lower()
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
        source, confidence = data["src"], "high"
        suburb_display = suburb.title()
        growth = data["g"]
    elif city:
        median = city["u"] if is_unit else city["h"]
        source, confidence = "Cotality/Domain 2025–26 (city median)", "medium"
        suburb_display = suburb.title() if suburb else city["city"]
        growth = city["g"]
    else:
        median = 728000 if is_unit else 1005000
        source, confidence = "Cotality national median 2026", "low"
        suburb_display = suburb.title() if suburb else "Unknown"
        growth = "+5%"
    spread = 0.15 if is_unit else 0.18
    lo = round(median * (1 - spread) / 25000) * 25000
    hi = round(median * (1 + spread) / 25000) * 25000
    return {
        "estimate": fmt_price(median), "lo": fmt_price(lo), "hi": fmt_price(hi),
        "median": median, "confidence": confidence, "source": source,
        "suburb_display": suburb_display, "state": state.upper() if state else "",
        "growth": growth, "prop_type": "Unit / Apartment" if is_unit else "House",
    }

def make_links(parsed, val):
    slug = val["suburb_display"].lower().replace(" ", "-")
    st_lc = parsed["state"].lower() if parsed["state"] else ""
    pc = parsed["postcode"]
    ptype = "unit+apartment" if parsed["is_unit"] else "house"
    return [
        {"label": f"Domain — {val['suburb_display']} properties for sale",
         "url": f"https://www.domain.com.au/sale/?suburb={val['suburb_display']}+{val['state']}&ptype={ptype}",
         "meta": "Current listings and recent sold prices"},
        {"label": f"Domain — {val['suburb_display']} suburb profile",
         "url": f"https://www.domain.com.au/suburb-profile/{slug}-{st_lc}-{pc}",
         "meta": "Median prices, auction clearance rates, market trends"},
        {"label": f"realestate.com.au — Buy in {val['suburb_display']}",
         "url": f"https://www.realestate.com.au/buy/in-{slug},+{st_lc}/list-1",
         "meta": "Current listings, sold history and suburb insights"},
        {"label": "PropertyValue.com.au — Free automated estimate",
         "url": "https://propertyvalue.com.au/",
         "meta": "Enter the exact address for a free AVM estimate"},
        {"label": f"SQM Research — Postcode {pc} weekly prices",
         "url": f"https://sqmresearch.com.au/weekly-residential-property-prices.php?postcode={pc}&t=1",
         "meta": "Weekly asking prices and vacancy rate trends"},
        {"label": "CoreLogic — Property & market analytics",
         "url": "https://www.corelogic.com.au/",
         "meta": "Institutional-grade property data and valuations"},
    ]

# ─── Session state ────────────────────────────────────────────────────────────
if "addr" not in st.session_state:
    st.session_state.addr = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# ─── NAV BAR ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rea-nav">
  <div class="rea-logo">prop<span>val</span> <span style="font-size:.75rem;opacity:.5">AU</span></div>
  <div class="rea-nav-links">
    <span class="rea-nav-link">Buy</span>
    <span class="rea-nav-link">Rent</span>
    <span class="rea-nav-link">Sold</span>
    <span class="rea-nav-link">Value</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rea-hero">
  <div class="rea-hero-title">Find out what your property is <span>worth</span></div>
  <div class="rea-hero-sub">Instant estimates for any Australian address — free, no sign-up required</div>
</div>
""", unsafe_allow_html=True)

# ─── SEARCH BAR with autocomplete ────────────────────────────────────────────
addr_input = st.text_input(
    "Address",
    value=st.session_state.addr,
    placeholder="🔍  Start typing an address, suburb or postcode…",
    label_visibility="collapsed",
    key="addr_input_field",
)

# Fetch autocomplete suggestions
suggestions = []
if addr_input and len(addr_input) >= 4 and addr_input != st.session_state.last_query:
    st.session_state.last_query = addr_input
    suggestions = fetch_suggestions(addr_input)

# Show suggestions as clickable buttons
if suggestions and addr_input and not st.session_state.submitted:
    st.markdown("**Suggestions:**")
    for i, sug in enumerate(suggestions):
        if st.button(f"📍  {sug['display']}", key=f"sug_{i}", use_container_width=True):
            st.session_state.addr = sug["display"]
            st.session_state.submitted = True
            st.rerun()

# Search button + example pills
col_a, col_b = st.columns([4, 1])
with col_b:
    if st.button("🔍  Search", use_container_width=True, type="primary"):
        if addr_input:
            st.session_state.addr = addr_input
            st.session_state.submitted = True
            st.rerun()

# Examples
st.markdown('<div style="margin-top:.5rem;font-size:12px;color:rgba(255,255,255,.6)">Try an example:</div>', unsafe_allow_html=True)
eg_cols = st.columns(3)
for i, eg in enumerate(EXAMPLES):
    with eg_cols[i % 3]:
        if st.button(eg, key=f"eg_{i}", use_container_width=True):
            st.session_state.addr = eg
            st.session_state.submitted = True
            st.rerun()

# ─── TABS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rea-tabs">
  <div class="rea-tab active">Estimate</div>
  <div class="rea-tab">Market Trends</div>
  <div class="rea-tab">Suburb Profile</div>
  <div class="rea-tab">Comparable Sales</div>
</div>
""", unsafe_allow_html=True)

# ─── RESULT ───────────────────────────────────────────────────────────────────
final_addr = st.session_state.addr if st.session_state.submitted else addr_input

if final_addr and final_addr.strip():
    parsed = parse_address(final_addr)
    val = valuate(parsed)
    links = make_links(parsed, val)

    # Address header
    st.markdown(f"""
    <div class="result-header">
      <div class="result-pin">📍</div>
      <div>
        <div class="result-address-text">{final_addr}</div>
        <div class="result-suburb">{val['suburb_display']} · {val['state']} · {val['prop_type']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Big value card
    conf_map = {
        "high":   ("✓ High confidence — suburb data matched", "conf-high"),
        "medium": ("~ Medium confidence — city median used",  "conf-medium"),
        "low":    ("⚠ Low confidence — check address format", "conf-low"),
    }
    conf_text, conf_class = conf_map[val["confidence"]]
    st.markdown(f"""
    <div class="val-hero">
      <div class="val-hero-label">Estimated Market Value</div>
      <div class="val-hero-amount">{val['estimate']}</div>
      <div class="val-hero-range">Indicative range: {val['lo']} – {val['hi']}</div>
      <span class="conf-badge {conf_class}">{conf_text}</span>
    </div>
    """, unsafe_allow_html=True)

    # Stats grid
    spread_pct = "±15%" if val["prop_type"] == "Unit / Apartment" else "±18%"
    st.markdown(f"""
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{val['estimate']}</div>
        <div class="stat-label">Suburb Median</div>
        <div class="stat-sub">{val['source']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{val['growth']}</div>
        <div class="stat-label">12-Month Growth</div>
        <div class="stat-sub">{val['suburb_display']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{spread_pct}</div>
        <div class="stat-label">Value Range</div>
        <div class="stat-sub">{val['lo']} – {val['hi']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Market insights
    mkt = MARKET_CONTEXT.get(parsed["state"], "The national market continues to be supported by supply shortages and strong population growth.")
    conf_note = {
        "high":   f"This estimate is based on real suburb-level median data for {val['suburb_display']} ({val['source']}).",
        "medium": f"Suburb-specific data was unavailable for {val['suburb_display']} — this estimate uses the {val['state']} city-wide median as a proxy.",
        "low":    "Address not matched to suburb data. For best results, include suburb and state, e.g. '14 Main St, Suburb NSW 2000'.",
    }[val["confidence"]]

    st.markdown(f"""
    <div class="insights-card">
      <div class="insights-title">Market Insights</div>
      <div class="insights-body">
        {conf_note} The estimated value of <strong>{val['estimate']}</strong>
        (range: {val['lo']} – {val['hi']}) reflects current {val['suburb_display']}
        {val['prop_type'].lower()} market conditions, with the suburb recording
        <strong>{val['growth']}</strong> growth over the past 12 months.
        <br><br>{mkt}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Sources
    src_html = "".join([
        f'<div class="src-item"><span class="src-arrow">›</span>'
        f'<a class="src-link-text" href="{l["url"]}" target="_blank">'
        f'{l["label"]}<span class="src-meta">{l["meta"]}</span></a></div>'
        for l in links
    ])
    st.markdown(f"""
    <div class="sources-card">
      <div class="sources-title">Verify &amp; Research Further</div>
      {src_html}
    </div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
    <strong>Disclaimer:</strong> This is a free informational estimate based on publicly available suburb median
    data (Domain, Cotality, REIWA, REISA, 2025–26). It is not a formal property valuation and should not be
    relied upon for mortgage, legal, or investment decisions. For a certified valuation, engage a licensed
    <strong>Certified Practising Valuer (CPV)</strong>.
    </div>
    """, unsafe_allow_html=True)

    # Reset
    if st.button("← Search another property", key="reset"):
        st.session_state.addr = ""
        st.session_state.submitted = False
        st.session_state.last_query = ""
        st.rerun()

else:
    st.markdown("""
    <div style="text-align:center;padding:2rem 1rem;color:#aaa;font-size:14px">
      Enter any Australian street address above to get an instant market valuation estimate.
    </div>
    """, unsafe_allow_html=True)
