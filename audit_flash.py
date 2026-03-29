# ==== IMPORTS ====
import streamlit as st
from datetime import date
from fpdf import FPDF
import io, re, os, json, hashlib, uuid, smtplib
import pandas as pd
from email.message import EmailMessage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import urllib.parse
from io import BytesIO

# ==== CONFIG ====
st.set_page_config(
    page_title="Audit Flash – Soteck Clauger",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Forcer la sidebar toujours visible via CSS (empêche de la fermer)
st.markdown("""
<style>
/* Masquer le bouton de fermeture de la sidebar */
button[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { 
    transform: none !important; 
    visibility: visible !important;
    min-width: 280px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Supabase (optionnel) ──────────────────────
SUPABASE_OK = False
sb = None
try:
    _url = st.secrets.get("SUPABASE_URL", "")
    _key = st.secrets.get("SUPABASE_KEY", "")
    if _url and _key:
        from supabase import create_client, Client
        @st.cache_resource
        def _sb_client():
            return create_client(_url, _key)
        sb = _sb_client()
        SUPABASE_OK = True
except Exception:
    pass

# ── Init session ──────────────────────────────
for _k, _v in [("langue", "Français"), ("ui_theme", "Clair"), ("chatbot_response", "")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Palette selon thème ───────────────────────
P      = "#cddc39"
P_DARK = "#afb42b"

if st.session_state["ui_theme"] == "Clair":
    BG      = "#f5f7fa"
    SURFACE = "#ffffff"
    BORDER  = "rgba(0,0,0,0.09)"
    TEXT    = "#1e2a38"
    TEXT2   = "#5a6a7a"
    TEXT3   = "#9aaabb"
    INPUT   = "#ffffff"
    SB_BG   = "#ffffff"
    INFO_BG = "#eaf4ff"
    INFO_BD = "rgba(56,139,220,0.3)"
    INFO_TX = "#185fa5"
else:
    BG      = "#0d1b2e"
    SURFACE = "#152036"
    BORDER  = "rgba(255,255,255,0.08)"
    TEXT    = "#e8edf5"
    TEXT2   = "#8fa8c0"
    TEXT3   = "#4a6070"
    INPUT   = "#1a2d47"
    SB_BG   = "#0b1628"
    INFO_BG = "#0c2540"
    INFO_BD = "rgba(56,139,220,0.25)"
    INFO_TX = "#85b7eb"

# ── CSS global ────────────────────────────────
st.markdown(f"""
<style>
*, *::before, *::after {{ box-sizing: border-box; }}
.stApp {{
    background: {BG} !important;
    color: {TEXT} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
}}
.stApp p, .stApp li, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
    color: {TEXT} !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    width: 300px !important;
    background: {SB_BG} !important;
    border-right: 0.5px solid {BORDER};
}}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {INPUT} !important;
    border: 0.5px solid {BORDER} !important;
    border-radius: 7px !important;
    color: {TEXT} !important;
    font-size: 13px !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {P} !important;
    box-shadow: 0 0 0 3px {P}30 !important;
    outline: none !important;
}}
div[data-testid="stDateInput"] input {{
    background: {INPUT} !important;
    border: 0.5px solid {BORDER} !important;
    border-radius: 7px !important;
    color: {TEXT} !important;
}}
.stTextInput label, .stTextArea label,
.stDateInput label, .stFileUploader label,
.stCheckbox label, .stSlider label {{
    font-size: 12px !important;
    color: {TEXT2} !important;
    font-weight: 400 !important;
}}

/* Boutons principaux */
div.stButton > button {{
    background: {P} !important;
    color: #1a1a1a !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 8px 18px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}}
div.stButton > button:hover {{
    background: {P_DARK} !important;
}}
/* Boutons secondaires */
div.stButton > button[kind="secondary"],
div.stButton > button[data-testid="baseButton-secondary"] {{
    background: {SURFACE} !important;
    color: {TEXT2} !important;
    border: 0.5px solid {BORDER} !important;
}}
/* Bouton ✕ effacer (petit bouton sidebar) */
section[data-testid="stSidebar"] div.stButton > button {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    border: 0.5px solid {BORDER} !important;
    font-size: 12px !important;
    padding: 6px 10px !important;
}}
section[data-testid="stSidebar"] div.stButton > button[type="primary"],
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
    background: {P} !important;
    color: #1a1a1a !important;
    border: none !important;
}}
/* Link buttons sidebar */
section[data-testid="stSidebar"] a[data-testid="stLinkButton"] {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    border: 0.5px solid {BORDER} !important;
    border-radius: 7px !important;
    font-size: 12px !important;
    padding: 6px 10px !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
div.stDownloadButton > button {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    border: 0.5px solid {BORDER} !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
div.stDownloadButton > button:hover {{
    border-color: {P} !important;
    background: {P}15 !important;
}}

/* Expanders — flèche à gauche, zéro chevauchement */
.stExpander {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    margin-bottom: 4px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}}
/* Expander summary — flèche native Streamlit stylée, positionnée à gauche */
.stExpander summary {{
    display: flex !important;
    flex-direction: row-reverse !important;
    justify-content: flex-end !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 11px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {TEXT} !important;
    cursor: pointer !important;
}}
/* Icône SVG native — on la garde fonctionnelle, on la colore */
.stExpander summary svg {{
    color: {P} !important;
    fill: {P} !important;
    width: 14px !important;
    height: 14px !important;
    flex-shrink: 0 !important;
    order: -1 !important;
}}
.stExpander summary p,
.stExpander summary span {{
    margin: 0 !important;
    padding: 0 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {TEXT} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: {BG} !important;
    border-bottom: 0.5px solid {BORDER} !important;
    gap: 0 !important;
    padding: 0 4px;
}}
.stTabs [data-baseweb="tab"] {{
    font-size: 12px !important;
    color: {TEXT2} !important;
    padding: 8px 14px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}}
.stTabs [aria-selected="true"] {{
    color: {TEXT} !important;
    border-bottom-color: {P} !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: {SURFACE} !important;
    padding: 12px !important;
    border-radius: 0 0 8px 8px;
}}

/* Sliders */
.stSlider > div > div > div > div {{ background: {P} !important; }}

/* Data editor */
.stDataEditor, .stDataFrame {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 7px !important;
}}

/* Alertes / info */
.stAlert {{ border-radius: 8px !important; font-size: 13px !important; }}
hr {{ border-color: {BORDER} !important; }}
.stCaption {{ color: {TEXT3} !important; font-size: 11px !important; }}
a {{ color: {P} !important; }}
a:hover {{ color: {P_DARK} !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Composants custom */
.info-banner {{
    background: {INFO_BG}; border: 0.5px solid {INFO_BD};
    border-radius: 8px; padding: 10px 14px;
    font-size: 12px; color: {INFO_TX}; margin-bottom: 8px;
}}
.sommaire {{
    background: {SURFACE}; border: 0.5px solid {BORDER};
    border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;
}}
.sommaire-lbl {{
    font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.07em; color: {TEXT3}; margin-bottom: 8px;
}}
.sommaire-items {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.s-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px; border-radius: 999px;
    background: {BG}; border: 0.5px solid {BORDER};
    font-size: 12px; color: {TEXT2};
    text-decoration: none;
}}
.s-badge:hover {{ border-color: {P}; color: {TEXT}; }}
.s-num {{
    width: 16px; height: 16px; background: {P}; color: #333;
    border-radius: 50%; font-size: 9px; font-weight: 700;
    display: inline-flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}}
.page-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 14px; border-bottom: 0.5px solid {BORDER};
    margin-bottom: 14px;
}}
.page-title {{
    font-size: 18px; font-weight: 600; color: {TEXT};
    display: flex; align-items: center; gap: 9px;
}}
.page-dot {{
    width: 10px; height: 10px; background: {P}; border-radius: 50%;
    display: inline-block;
}}
.page-sub {{ font-size: 12px; color: {TEXT3}; margin-top: 3px; }}
.logo-box {{
    height: 30px; padding: 0 12px; background: {SURFACE};
    border-radius: 6px; border: 0.5px solid {BORDER};
    display: inline-flex; align-items: center;
    font-size: 11px; color: {TEXT3};
}}
.sb-link {{
    background: {SURFACE}; border: 0.5px solid {BORDER};
    border-radius: 10px; padding: 10px 12px;
    display: flex; flex-direction: column; gap: 6px;
    margin-top: 4px;
}}
.sb-link-label {{
    font-size: 10px; color: {TEXT3}; text-transform: uppercase;
    letter-spacing: 0.06em; display: flex; align-items: center; gap: 5px;
}}
.sb-link-label::before {{
    content: ""; width: 6px; height: 6px;
    background: {P}; border-radius: 50%; flex-shrink: 0;
}}
.sb-link-url {{
    font-size: 10px; font-family: monospace; color: {TEXT2};
    background: {BG}; padding: 5px 7px; border-radius: 5px;
    border: 0.5px solid {BORDER}; word-break: break-all;
}}
.sb-chat {{
    background: {SURFACE}; border: 0.5px solid {BORDER};
    border-radius: 10px; padding: 12px;
}}
.sb-chat-header {{
    font-size: 12px; font-weight: 600; color: {TEXT};
    display: flex; align-items: center; gap: 7px;
    margin-bottom: 8px;
}}
.sb-chat-header::before {{
    content: ""; width: 8px; height: 8px;
    background: {P}; border-radius: 50%; flex-shrink: 0;
}}
.chat-response {{
    background: {BG}; border: 0.5px solid {BORDER};
    border-left: 3px solid {P}; border-radius: 6px;
    padding: 10px 12px; font-size: 12px; line-height: 1.6;
    color: {TEXT}; margin-top: 6px;
}}
.sb-section-label {{
    font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.07em; color: {TEXT3};
    margin-bottom: 4px; margin-top: 2px;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS GÉNÉRIQUES
# ─────────────────────────────────────────────
def _one_line(s):
    return re.sub(r"[\r\n]+", " ", (s or "").strip())

def _slug(x):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", (x or "").strip())

def _val(x, suffix=""):
    if isinstance(x, (int, float)) and not pd.isna(x):
        return f"{x:g}{suffix}"
    s = (str(x) if x is not None else "").strip()
    return s + suffix if s else "n/d"

def _yn(x):
    if isinstance(x, bool): return "Oui" if x else "Non"
    s = (str(x) if x is not None else "").strip().lower()
    if s in {"oui","yes","y","true","vrai","1"}: return "Oui"
    if s in {"non","no","n","false","faux","0"}: return "Non"
    return "n/d"

def _df_depuis_editor(key):
    val = st.session_state.get(key)
    if isinstance(val, pd.DataFrame): return val.copy()
    if isinstance(val, dict):
        rows = []
        if isinstance(val.get("added_rows"), list): rows.extend(val["added_rows"])
        if isinstance(val.get("edited_rows"), dict): rows.extend(val["edited_rows"].values())
        return pd.DataFrame(rows)
    if isinstance(val, list) and all(isinstance(x, dict) for x in val):
        return pd.DataFrame(val)
    return pd.DataFrame()

def _EQ(): return st.session_state.get("_EQ", {})

def _df_to_dict(key):
    val = st.session_state.get(key)
    if isinstance(val, pd.DataFrame): return val.to_dict("records")
    if isinstance(val, dict):
        rows = list(val.get("added_rows") or [])
        ed = val.get("edited_rows")
        if isinstance(ed, dict): rows.extend(ed.values())
        return rows
    if isinstance(val, list): return val
    return []

def _safe_details(fn):
    try: return fn() if callable(fn) else fn
    except Exception: return []

# ── Détails équipements ──────────────────────
def _chaudieres_detaille():
    df = _df_depuis_editor("chaudieres"); t = _EQ()
    if df.empty: return []
    c = lambda k, d: t.get(k, d)
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – {_val(r.get(c('label_type_chaudiere','Type')))} – "
                 f"Rend:{_val(r.get(c('label_rendement_chaudiere','Rend')),'%')} – "
                 f"{_val(r.get(c('label_taille_chaudiere','Taille')))} – "
                 f"Micro:{_yn(r.get(c('label_micro_modulation','Micro')))} – "
                 f"Éco:{_yn(r.get(c('label_economiseur_chaudiere','Éco')))}")
    return L

def _frigo_detaille():
    df = _df_depuis_editor("frigo"); t = _EQ()
    if df.empty: return []
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – Cap:{_val(r.get(t.get('label_capacite_frigo','Cap')))} – "
                 f"Réfrigérant:{_val(r.get(t.get('label_nom_frigorigenes','Réf')))}")
    return L

def _compresseurs_detaille():
    df = _df_depuis_editor("compresseur"); t = _EQ()
    if df.empty: return []
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – {_val(r.get(t.get('label_puissance_comp','HP')),' HP')} – "
                 f"VFD:{_yn(r.get(t.get('label_variation_vitesse','VFD')))}")
    return L

def _depoussieurs_detaille():
    df = _df_depuis_editor("depoussieur"); t = _EQ()
    if df.empty: return []
    hl = t.get("label_puissance_dep_hp","Puissance (HP)")
    vl = t.get("label_vfd_dep","VFD")
    ml = t.get("label_marque_dep","Marque")
    for c in ["Nom", hl, vl, ml]:
        if c not in df.columns: df[c] = ""
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip()
        if not n: continue
        hp = r[hl]; vfd = r[vl]; marque = r[ml]
        hp_t = f"{hp} HP" if (pd.notna(hp) and str(hp).strip()) else "HP n/d"
        m_t = f" – {marque}" if isinstance(marque, str) and marque.strip() else ""
        L.append(f"{n} – {hp_t} – VFD:{_yn(vfd)}{m_t}")
    return L

def _pompes_detaille():
    df = _df_depuis_editor("pompes"); t = _EQ()
    if df.empty: return []
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – {_val(r.get(t.get('label_type_pompe','Type')))} – "
                 f"{_val(r.get(t.get('label_puissance_pompe','Puissance')))} – "
                 f"Rend:{_val(r.get(t.get('label_rendement_pompe','Rend')),'%')} – "
                 f"VFD:{_yn(r.get(t.get('label_vitesse_variable_pompe','VFD')))}")
    return L

def _ventilation_detaille():
    df = _df_depuis_editor("ventilation_eq"); t = _EQ()
    if df.empty: return []
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – {_val(r.get(t.get('label_type_ventilation','Type')))} – "
                 f"{_val(r.get(t.get('label_puissance_ventilation','Puissance')))}")
    return L

def _machines_detaille():
    df = _df_depuis_editor("machines"); t = _EQ()
    if df.empty: return []
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – {_val(r.get(t.get('label_puissance_machine','kW')),' kW')} – "
                 f"Tu:{_val(r.get(t.get('label_taux_utilisation','Tu')),'%')} – "
                 f"{_val(r.get(t.get('label_source_energie_machine','Src')))}")
    return L

def _eclairage_detaille():
    df = _df_depuis_editor("eclairage"); t = _EQ()
    if df.empty: return []
    L = []
    for _, r in df.iterrows():
        n = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{n} – {_val(r.get(t.get('label_type_eclairage','Type')))} – "
                 f"{_val(r.get(t.get('label_puissance_totale_eclairage','kW')),' kW')} – "
                 f"{_val(r.get(t.get('label_heures_utilisation','h/j')),'h/j')}")
    return L

# ── Supabase helpers ──────────────────────────
def collecter_donnees():
    d = {k: st.session_state.get(k, "") for k in [
        "client_nom","site_nom","adresse","ville","province","code_postal","neq_clean",
        "contact_ee_nom","contact_ee_mail","contact_ee_tel","contact_ee_ext",
        "contact_maint_nom","contact_maint_mail","contact_maint_tel","contact_maint_ext",
        "rempli_nom","rempli_mail","rempli_tel","rempli_ext","sign_nom","sign_mail",
        "sauver_ges","roi_vise","investissement_prevu","autres_objectifs",
        "autres_services","temps_fonctionnement",
    ]}
    d.update({k: bool(st.session_state.get(k, False)) for k in [
        "economie_energie","gain_productivite","remplacement_equipement",
        "controle","maintenance","ventilation_service",
    ]})
    d.update({k: int(st.session_state.get(k, 5)) for k in [
        "priorite_energie","priorite_roi","priorite_ges","priorite_prod","priorite_maintenance",
    ]})
    d.update({k: _df_to_dict(k) for k in [
        "chaudieres","frigo","compresseur","pompes","ventilation_eq","machines","eclairage","depoussieur",
    ]})
    d["rempli_date"] = str(st.session_state.get("rempli_date", ""))
    return d

def get_or_create_form_id():
    if "form_id" in st.session_state:
        return st.session_state["form_id"]
    fid = st.query_params.get("form_id")
    if fid:
        st.session_state["form_id"] = fid
        if SUPABASE_OK:
            try:
                res = sb.table("forms").select("data").eq("form_id", fid).execute()
                if res.data:
                    for k, v in (res.data[0].get("data") or {}).items():
                        st.session_state[k] = v
            except Exception:
                pass
        return fid
    new_id = str(uuid.uuid4())
    st.session_state["form_id"] = new_id
    st.query_params["form_id"] = new_id
    if SUPABASE_OK:
        try:
            sb.table("forms").upsert({
                "form_id": new_id, "data": {}, "email_contact": "", "status": "en_cours"
            }).execute()
        except Exception:
            pass
    return new_id

def save_form(form_id):
    if not SUPABASE_OK: return False
    data = collecter_donnees()
    try:
        sb.table("forms").upsert({
            "form_id": form_id, "data": data,
            "email_contact": data.get("contact_ee_mail",""), "status": "en_cours"
        }).execute()
        return True
    except Exception:
        return False

def autosave(form_id):
    payload = collecter_donnees()
    digest = hashlib.md5(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    if st.session_state.get("_digest") != digest:
        save_form(form_id)
        st.session_state["_digest"] = digest

form_id = get_or_create_form_id()

# ── GROQ ─────────────────────────────────────
def _groq_key():
    key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_APIKEY")
    try:
        key = key or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_APIKEY")
    except Exception:
        pass
    return str(key).strip().strip('"').strip("'") if key else None

def groq_chat(question, lang_q="fr"):
    q = (question or "").strip()
    if not q: return "Aucune question fournie."
    key = _groq_key()
    if not key: return "Clé GROQ_API_KEY manquante dans Secrets."
    sys_msg = (
        "Tu es un assistant concis en efficacité énergétique industrielle. "
        f"Réponds en {'français' if lang_q=='fr' else 'English'}. Sois bref et précis."
    )
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model":"llama-3.1-8b-instant",
                  "messages":[{"role":"system","content":sys_msg},{"role":"user","content":q}],
                  "temperature":0.2,"max_tokens":400},
            timeout=45
        )
        if r.status_code != 200: return f"Erreur Groq ({r.status_code})"
        return (r.json()["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        return f"Erreur réseau : {e}"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
lang = "fr" if st.session_state["langue"] == "Français" else "en"

with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;
                padding-bottom:12px;border-bottom:0.5px solid {BORDER};margin-bottom:4px">
      <div style="width:30px;height:30px;background:{P};border-radius:6px;
                  display:flex;align-items:center;justify-content:center;
                  font-size:13px;font-weight:600;color:#333;flex-shrink:0">AF</div>
      <div>
        <div style="font-size:13px;font-weight:600;color:{TEXT};line-height:1.2">Audit Flash</div>
        <div style="font-size:11px;color:{TEXT3}">Soteck Clauger</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Langue
    st.markdown(f'<div class="sb-section-label">{"Langue" if lang=="fr" else "Language"}</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Français", key="btn_fr",
                     type="primary" if lang=="fr" else "secondary",
                     use_container_width=True):
            st.session_state["langue"] = "Français"; st.rerun()
    with c2:
        if st.button("English", key="btn_en",
                     type="primary" if lang=="en" else "secondary",
                     use_container_width=True):
            st.session_state["langue"] = "English"; st.rerun()

    # Thème
    st.markdown(f'<div class="sb-section-label" style="margin-top:8px">{"Apparence" if lang=="fr" else "Theme"}</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clair", key="btn_clair",
                     type="primary" if st.session_state["ui_theme"]=="Clair" else "secondary",
                     use_container_width=True):
            st.session_state["ui_theme"] = "Clair"; st.rerun()
    with c2:
        if st.button("Sombre", key="btn_sombre",
                     type="primary" if st.session_state["ui_theme"]=="Sombre" else "secondary",
                     use_container_width=True):
            st.session_state["ui_theme"] = "Sombre"; st.rerun()

    st.divider()

    # Chatbot
    st.markdown('<div class="sb-chat">', unsafe_allow_html=True)
    st.markdown('<div class="sb-chat-header">Assistant Audit Flash</div>', unsafe_allow_html=True)
    q_text = st.text_area(
        "Question",
        key="chatbot_input",
        placeholder="Ex : C'est quoi un VFD ?" if lang=="fr" else "E.g.: What is a VFD?",
        height=78,
        label_visibility="collapsed"
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        if st.button("Envoyer ▶" if lang=="fr" else "Send ▶", key="btn_send", use_container_width=True):
            if q_text.strip():
                with st.spinner("..."):
                    st.session_state["chatbot_response"] = groq_chat(q_text, lang)
            else:
                st.warning("Écrivez une question." if lang=="fr" else "Write a question.")
    with c2:
        if st.button("✕", key="btn_clr", help="Effacer"):
            st.session_state["chatbot_response"] = ""
    resp = st.session_state.get("chatbot_response", "")
    if resp:
        if resp.startswith(("Erreur","Clé","⚠️")):
            st.error(resp)
        else:
            st.markdown(f'<div class="chat-response">{resp}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Lien de reprise
    base = ""
    try: base = st.secrets.get("PUBLIC_BASE_URL", "").rstrip("/")
    except Exception: pass
    resume_url = f"{base}?form_id={form_id}" if base else f"?form_id={form_id}"
    enc = urllib.parse.quote_plus(resume_url)

    st.markdown(f"""
    <div class="sb-link">
      <div class="sb-link-label">{"Lien de reprise" if lang=="fr" else "Resume link"}</div>
      <div class="sb-link-url">{resume_url}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.link_button("Email", f"mailto:?subject=Formulaire&body={enc}", use_container_width=True)
    with c2:
        st.link_button("WhatsApp", f"https://wa.me/?text={enc}", use_container_width=True)

    try:
        import qrcode
        img = qrcode.make(resume_url)
        buf = BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        st.image(buf, width=110,
                 caption="Scanner pour reprendre" if lang=="fr" else "Scan to resume")
    except Exception:
        pass

# ─────────────────────────────────────────────
# TRADUCTIONS
# ─────────────────────────────────────────────
T = {
"fr": dict(
    label_client_nom="Nom du client *", aide_client_nom="Ex: Biscuits Leclerc",
    label_site_nom="Nom du site *", label_adresse="Adresse", label_ville="Ville",
    label_province="Province", label_code_postal="Code postal",
    label_neq="NEQ (Québec)", help_neq="10 chiffres, ex : 1140007365",
    label_nom="Prénom et Nom", label_mail="Courriel", label_tel="Téléphone",
    label_ext="Extension", label_date="Date de remplissage",
    help_mail="Format : exemple@domaine.com", help_tel="10 chiffres recommandés",
    sous_ee="Contact Efficacité Énergétique",
    sous_maint="Contact Maintenance (externe)",
    titre_rempli="Personne ayant rempli le formulaire",
    sous_sign="Signataire autorisé",
    aucun_eq="Aucun équipement saisi",
    label_felec="Factures électricité (1 à 3 ans)",
    label_fcomb="Factures Gaz / Mazout / Propane / Bois",
    label_fautres="Autres consommables (azote, eau, CO2…)",
    label_fpid="Plans d'aménagement et P&ID",
    label_temps="Temps de fonctionnement (heures/an)",
    fichiers="Fichiers téléversés",
    label_ges="Objectif de réduction GES (%)", help_ges="Ex : 20",
    label_eco="Économie d'énergie", label_prod="Productivité accrue",
    label_roi="ROI visé", label_rempl="Remplacement d'équipement prévu",
    label_invest="Investissement prévu (montant et date)", label_autres_obj="Autres objectifs",
    tab_chaud="Chaudières", tab_frigo="Frigo", tab_comp="Compresseurs",
    tab_dep="Dépoussiéreurs", tab_pompes="Pompes", tab_vent="Ventilation",
    tab_mach="Machines", tab_ecl="Éclairage", apercu="Aperçu :",
    label_type_chaudiere="Type", label_rendement_chaudiere="Rendement (%)",
    label_taille_chaudiere="Taille (BHP/BTU)", label_appoint_eau="Appoint eau",
    label_micro_modulation="Micro modulation ?", label_economiseur_chaudiere="Économiseur ?",
    label_capacite_frigo="Capacité", label_nom_frigorigenes="Réfrigérant",
    label_puissance_comp="Puissance (HP)", label_variation_vitesse="VFD ?",
    label_puissance_dep_hp="Puissance (HP)", label_vfd_dep="VFD ?", label_marque_dep="Marque",
    label_type_pompe="Type", label_puissance_pompe="Puissance (kW/HP)",
    label_rendement_pompe="Rendement (%)", label_vitesse_variable_pompe="VFD ?",
    label_type_ventilation="Type", label_puissance_ventilation="Puissance (kWh)",
    label_puissance_machine="Puissance (kW)", label_taux_utilisation="Utilisation (%)",
    label_rendement_machine="Rendement (%)", label_source_energie_machine="Source énergie",
    label_type_eclairage="Type", label_puissance_totale_eclairage="Puissance totale (kW)",
    label_heures_utilisation="Heures/jour",
    intro_prio="Notez de 0 (pas important) à 10 (très important).",
    label_p_ener="Réduction énergétique", help_p_ener="Économies globales.",
    label_p_roi="Retour sur investissement", help_p_roi="1 an = rapide, 10 ans = lent.",
    label_p_ges="Réduction GES", help_p_ges="Conformité et impact environnemental.",
    label_p_prod="Productivité et fiabilité", help_p_prod="Performance et disponibilité.",
    label_p_maint="Maintenance et durabilité", help_p_maint="Entretien et durée de vie.",
    titre_analyse="Analyse des priorités", warning_prio="Indiquez vos priorités.",
    r_ener="Énergie", r_roi="ROI", r_ges="GES", r_prod="Productivité", r_maint="Maintenance",
    label_controle="Contrôle et automatisation",
    label_maintenance="Maintenance préventive et corrective",
    label_ventilation="Ventilation industrielle",
    label_autres_svc="Autres services (précisez)",
    info_note="Vos données sont sauvegardées automatiquement. Utilisez le lien de reprise pour revenir plus tard.",
    btn_gen="Générer le PDF", btn_dl="Télécharger le PDF",
    err_missing="Veuillez remplir :", f_client="Nom du client", f_site="Nom du site", f_mail="Courriel EE",
    ok_pdf="PDF généré avec succès.",
    lbl_excel="Exporter en Excel", btn_excel="Télécharger Excel",
    btn_soumettre="Soumettre le formulaire",
    err_pdf="Veuillez d'abord générer le PDF.",
    ok_envoi="Formulaire soumis avec succès.",
),
"en": dict(
    label_client_nom="Client name *", aide_client_nom="E.g.: Acme Corp",
    label_site_nom="Site name *", label_adresse="Address", label_ville="City",
    label_province="Province", label_code_postal="Postal code",
    label_neq="NEQ (Québec)", help_neq="10 digits, e.g.: 1140007365",
    label_nom="First and Last Name", label_mail="Email", label_tel="Phone",
    label_ext="Extension", label_date="Date of completion",
    help_mail="Format: example@domain.com", help_tel="10 digits recommended",
    sous_ee="Energy Efficiency Contact",
    sous_maint="Maintenance Contact (external)",
    titre_rempli="Person who filled out this form",
    sous_sign="Authorized signatory",
    aucun_eq="No equipment entered",
    label_felec="Electricity bills (1 to 3 years)",
    label_fcomb="Gas / Fuel Oil / Propane / Wood bills",
    label_fautres="Other consumables (nitrogen, water, CO2…)",
    label_fpid="Site layout plans and P&ID",
    label_temps="Plant operating time (hours/year)",
    fichiers="Uploaded files",
    label_ges="GHG reduction target (%)", help_ges="Example: 20",
    label_eco="Energy savings", label_prod="Increased productivity",
    label_roi="Target ROI", label_rempl="Planned equipment replacement",
    label_invest="Planned investment (amount and date)", label_autres_obj="Other objectives",
    tab_chaud="Boilers", tab_frigo="Refrigeration", tab_comp="Compressors",
    tab_dep="Dust collectors", tab_pompes="Pumps", tab_vent="Ventilation",
    tab_mach="Machines", tab_ecl="Lighting", apercu="Preview:",
    label_type_chaudiere="Type", label_rendement_chaudiere="Efficiency (%)",
    label_taille_chaudiere="Size (BHP/BTU)", label_appoint_eau="Make-up water",
    label_micro_modulation="Micro modulation?", label_economiseur_chaudiere="Economizer?",
    label_capacite_frigo="Capacity", label_nom_frigorigenes="Refrigerant",
    label_puissance_comp="Power (HP)", label_variation_vitesse="VFD?",
    label_puissance_dep_hp="Power (HP)", label_vfd_dep="VFD?", label_marque_dep="Brand",
    label_type_pompe="Type", label_puissance_pompe="Power (kW/HP)",
    label_rendement_pompe="Efficiency (%)", label_vitesse_variable_pompe="VFD?",
    label_type_ventilation="Type", label_puissance_ventilation="Power (kWh)",
    label_puissance_machine="Power (kW)", label_taux_utilisation="Utilization (%)",
    label_rendement_machine="Efficiency (%)", label_source_energie_machine="Energy source",
    label_type_eclairage="Type", label_puissance_totale_eclairage="Total power (kW)",
    label_heures_utilisation="Hours/day",
    intro_prio="Rate from 0 (not important) to 10 (very important).",
    label_p_ener="Energy reduction", help_p_ener="Overall energy savings.",
    label_p_roi="Return on investment", help_p_roi="1 year = fast, 10 years = slow.",
    label_p_ges="GHG reduction", help_p_ges="Compliance and environmental impact.",
    label_p_prod="Productivity and reliability", help_p_prod="Performance and availability.",
    label_p_maint="Maintenance and durability", help_p_maint="Upkeep and equipment life.",
    titre_analyse="Priority analysis", warning_prio="Please set your priorities.",
    r_ener="Energy", r_roi="ROI", r_ges="GHG", r_prod="Productivity", r_maint="Maintenance",
    label_controle="Control and automation",
    label_maintenance="Preventive and corrective maintenance",
    label_ventilation="Industrial ventilation",
    label_autres_svc="Other desired services",
    info_note="Your data is automatically saved. Use the resume link to come back later.",
    btn_gen="Generate PDF", btn_dl="Download PDF",
    err_missing="Please fill in:", f_client="Client name", f_site="Site name", f_mail="EE email",
    ok_pdf="PDF generated successfully.",
    lbl_excel="Export to Excel", btn_excel="Download Excel",
    btn_soumettre="Submit form",
    err_pdf="Please generate the PDF first.",
    ok_envoi="Form submitted successfully.",
),
}
t = T[lang]
st.session_state["_EQ"] = {k: v for k, v in t.items() if k.startswith("label_")}

# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────
logo_path = "Image/Logo Soteck.jpg"
# ── Bandeau langue + thème en haut du main (toujours accessible) ──
_col_l, _col_t, _col_sp = st.columns([2, 2, 6])
with _col_l:
    if st.button("🌐 Français" if lang=="en" else "🌐 English",
                 key="main_lang_toggle", help="Changer la langue"):
        st.session_state["langue"] = "English" if lang=="fr" else "Français"
        st.rerun()
with _col_t:
    _next_theme = "Sombre" if st.session_state["ui_theme"]=="Clair" else "Clair"
    _icon = "🌙" if st.session_state["ui_theme"]=="Clair" else "☀️"
    if st.button(f"{_icon} Mode {_next_theme}", key="main_theme_toggle"):
        st.session_state["ui_theme"] = _next_theme
        st.rerun()

# Header avec logo intégré dans un flex row
sub = ("Formulaire de prise de besoin — Audit énergétique industriel" if lang=="fr"
       else "Needs Assessment Form — Industrial Energy Audit")

logo_b64 = ""
if os.path.exists(logo_path):
    import base64
    with open(logo_path, "rb") as _f:
        logo_b64 = base64.b64encode(_f.read()).decode()

logo_html = (
    f'<img src="data:image/jpeg;base64,{logo_b64}" '
    f'style="height:72px;width:auto;max-width:200px;object-fit:contain;display:block;" />'
    if logo_b64 else
    '<span style="font-size:12px;color:#9aaabb">Soteck Clauger</span>'
)

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding-bottom:14px;border-bottom:0.5px solid {BORDER};margin-bottom:14px">
  <div>
    <div style="font-size:18px;font-weight:600;color:{TEXT};
                display:flex;align-items:center;gap:9px">
      <span style="width:10px;height:10px;background:{P};border-radius:50%;
                   display:inline-block;flex-shrink:0"></span>Audit Flash
    </div>
    <div style="font-size:12px;color:{TEXT3};margin-top:3px">{sub}</div>
  </div>
  <div style="flex-shrink:0">{logo_html}</div>
</div>""", unsafe_allow_html=True)

# Bienvenue
welcome = ("Remplissez toutes les sections ci-dessous. Vos données sont sauvegardées automatiquement."
           if lang=="fr" else
           "Fill out all sections below. Your data is automatically saved.")
st.markdown(f'<div class="info-banner">{welcome}</div>', unsafe_allow_html=True)
url_site = "https://www.soteck.com/fr" if lang=="fr" else "https://www.soteck.com/en"
st.markdown(f'🔗 **[Soteck Clauger]({url_site})**')

# Sommaire
sects = (["Informations générales","Contacts","Documents","Objectifs",
          "Équipements","Priorités","Services","PDF"]
         if lang=="fr" else
         ["General Information","Contacts","Documents","Objectives",
          "Equipment","Priorities","Services","PDF"])
anchors = ["infos","contacts","docs","objectifs","equipements","priorites","services","pdf"]
badges = "".join(
    f'<a class="s-badge" href="#{anchors[i]}">'
    f'<span class="s-num">{i+1}</span>{s}</a>'
    for i, s in enumerate(sects)
)
st.markdown(f"""
<div class="sommaire">
  <div class="sommaire-lbl">{"Sommaire" if lang=="fr" else "Contents"}</div>
  <div class="sommaire-items">{badges}</div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER éditeur
# ─────────────────────────────────────────────
def make_editor(key, columns, col_cfg=None):
    df = st.data_editor(
        pd.DataFrame(columns=columns), num_rows="dynamic",
        key=key, column_config=col_cfg or {}, use_container_width=True
    )
    prev = _df_depuis_editor(key)
    if not prev.empty:
        st.caption(t["apercu"])
        st.dataframe(prev, use_container_width=True, hide_index=True)
    return df

# ═══════════════════════════════════════════════
# SECTION 1 — INFOS GÉNÉRALES
# ═══════════════════════════════════════════════
st.markdown('<div id="infos"></div>', unsafe_allow_html=True)
with st.expander(f"1 — {'Informations générales' if lang=='fr' else 'General Information'}"):
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_client_nom"], help=t["aide_client_nom"], key="client_nom")
        st.text_input(t["label_site_nom"], key="site_nom")
        st.text_input(t["label_adresse"], key="adresse")
    with c2:
        st.text_input(t["label_ville"], key="ville")
        st.text_input(t["label_province"], key="province")
        st.text_input(t["label_code_postal"], key="code_postal")
    neq = st.text_input(t["label_neq"], key="neq", help=t["help_neq"])
    neq_clean = re.sub(r"\D", "", neq or "")
    st.session_state["neq_clean"] = neq_clean
    if neq and not re.fullmatch(r"\d{10}", neq_clean):
        st.warning("Format NEQ invalide : exactement 10 chiffres." if lang=="fr"
                   else "Invalid NEQ: exactly 10 digits required.")

# ═══════════════════════════════════════════════
# SECTION 2 — CONTACTS
# ═══════════════════════════════════════════════
st.markdown('<div id="contacts"></div>', unsafe_allow_html=True)
with st.expander(f"2 — {'Personnes contacts' if lang=='fr' else 'Contact Persons'}"):
    st.markdown(f"**{t['sous_ee']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_nom"], key="contact_ee_nom")
        st.text_input(t["label_mail"], help=t["help_mail"], key="contact_ee_mail")
    with c2:
        st.text_input(t["label_tel"], help=t["help_tel"], key="contact_ee_tel")
        st.text_input(t["label_ext"], key="contact_ee_ext")
    ee_mail = st.session_state.get("contact_ee_mail", "")
    if ee_mail and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", ee_mail.strip()):
        st.warning("Courriel EE invalide." if lang=="fr" else "Invalid EE email.")

    st.markdown("---")
    st.markdown(f"**{t['sous_maint']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_nom"], key="contact_maint_nom")
        st.text_input(t["label_mail"], key="contact_maint_mail")
    with c2:
        st.text_input(t["label_tel"], key="contact_maint_tel")
        st.text_input(t["label_ext"], key="contact_maint_ext")

    st.markdown("---")
    st.markdown(f"**{t['titre_rempli']}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input(t["label_nom"], key="rempli_nom")
        st.date_input(t["label_date"], value=date.today(), key="rempli_date")
    with c2:
        st.text_input(t["label_mail"], key="rempli_mail")
    with c3:
        st.text_input(t["label_tel"], key="rempli_tel")
        st.text_input(t["label_ext"], key="rempli_ext")

    st.markdown("---")
    st.markdown(f"**{t['sous_sign']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_nom"], key="sign_nom")
    with c2:
        st.text_input(t["label_mail"], help=t["help_mail"], key="sign_mail")
        sm = st.session_state.get("sign_mail", "")
        if sm and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", sm.strip()):
            st.warning("Courriel signataire invalide." if lang=="fr"
                       else "Invalid signatory email.")

# ═══════════════════════════════════════════════
# SECTION 3 — DOCUMENTS
# ═══════════════════════════════════════════════
st.markdown('<div id="docs"></div>', unsafe_allow_html=True)
with st.expander(f"3 — {'Documents à fournir' if lang=='fr' else 'Documents to Provide'}"):
    c1, c2 = st.columns(2)
    with c1:
        facture_elec = st.file_uploader(t["label_felec"], type="pdf",
                                        accept_multiple_files=True, key="fu_elec")
        facture_comb = st.file_uploader(t["label_fcomb"], type="pdf",
                                        accept_multiple_files=True, key="fu_comb")
    with c2:
        facture_aut  = st.file_uploader(t["label_fautres"], type="pdf",
                                        accept_multiple_files=True, key="fu_aut")
        plans_pid    = st.file_uploader(t["label_fpid"], type="pdf",
                                        accept_multiple_files=True, key="fu_pid")
    st.text_input(t["label_temps"], key="temps_fonctionnement")
    all_f = {t["label_felec"]: facture_elec or [],
             t["label_fcomb"]: facture_comb  or [],
             t["label_fautres"]: facture_aut or [],
             t["label_fpid"]: plans_pid or []}
    if any(all_f.values()):
        st.markdown(f"**{t['fichiers']}**")
        for lbl, files in all_f.items():
            for f in files:
                st.markdown(f"- `{f.name}` — {lbl}")

st.session_state["facture_elec_files"] = facture_elec or []
st.session_state["facture_comb_files"]  = facture_comb  or []
st.session_state["facture_aut_files"]   = facture_aut  or []
st.session_state["plans_pid_files"]     = plans_pid    or []

# ═══════════════════════════════════════════════
# SECTION 4 — OBJECTIFS
# ═══════════════════════════════════════════════
st.markdown('<div id="objectifs"></div>', unsafe_allow_html=True)
with st.expander(f"4 — {'Objectifs du client' if lang=='fr' else 'Client Objectives'}"):
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_ges"], help=t["help_ges"], key="sauver_ges")
        st.checkbox(t["label_eco"],  key="economie_energie")
        st.checkbox(t["label_prod"], key="gain_productivite")
    with c2:
        st.text_input(t["label_roi"], key="roi_vise")
        st.checkbox(t["label_rempl"], key="remplacement_equipement")
        st.text_input(t["label_invest"], key="investissement_prevu")
    st.text_area(t["label_autres_obj"], key="autres_objectifs")

# ═══════════════════════════════════════════════
# SECTION 5 — ÉQUIPEMENTS
# ═══════════════════════════════════════════════
st.markdown('<div id="equipements"></div>', unsafe_allow_html=True)
with st.expander(f"5 — {'Liste des équipements' if lang=='fr' else 'Equipment List'}"):
    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
        t["tab_chaud"], t["tab_frigo"], t["tab_comp"], t["tab_dep"],
        t["tab_pompes"], t["tab_vent"], t["tab_mach"], t["tab_ecl"],
    ])
    with tab1:
        make_editor("chaudieres", [
            "Nom", t["label_type_chaudiere"], t["label_rendement_chaudiere"],
            t["label_taille_chaudiere"], t["label_appoint_eau"],
            t["label_micro_modulation"], t["label_economiseur_chaudiere"],
        ])
    with tab2:
        make_editor("frigo", ["Nom", t["label_capacite_frigo"], t["label_nom_frigorigenes"]])
    with tab3:
        make_editor("compresseur", ["Nom", t["label_puissance_comp"], t["label_variation_vitesse"]],
            {t["label_variation_vitesse"]: st.column_config.CheckboxColumn(default=False)})
    with tab4:
        make_editor("depoussieur", [
            "Nom", t["label_puissance_dep_hp"], t["label_vfd_dep"], t["label_marque_dep"]
        ], {
            t["label_puissance_dep_hp"]: st.column_config.NumberColumn(step=0.5, min_value=0.0),
            t["label_vfd_dep"]: st.column_config.CheckboxColumn(default=False),
        })
    with tab5:
        make_editor("pompes", [
            "Nom", t["label_type_pompe"], t["label_puissance_pompe"],
            t["label_rendement_pompe"], t["label_vitesse_variable_pompe"],
        ], {t["label_vitesse_variable_pompe"]: st.column_config.CheckboxColumn(default=False)})
    with tab6:
        make_editor("ventilation_eq", ["Nom", t["label_type_ventilation"], t["label_puissance_ventilation"]])
    with tab7:
        make_editor("machines", [
            "Nom", t["label_puissance_machine"], t["label_taux_utilisation"],
            t["label_rendement_machine"], t["label_source_energie_machine"],
        ])
    with tab8:
        make_editor("eclairage", [
            "Nom", t["label_type_eclairage"],
            t["label_puissance_totale_eclairage"], t["label_heures_utilisation"],
        ])

# ═══════════════════════════════════════════════
# SECTION 6 — PRIORITÉS
# ═══════════════════════════════════════════════
st.markdown('<div id="priorites"></div>', unsafe_allow_html=True)
with st.expander(f"6 — {'Priorités stratégiques' if lang=='fr' else 'Strategic Priorities'}"):
    st.caption(t["intro_prio"])
    c1, c2 = st.columns(2)
    with c1:
        p_e = st.slider(t["label_p_ener"], 0, 10,
                        st.session_state.get("priorite_energie", 5),
                        help=t["help_p_ener"], key="priorite_energie")
        p_r = st.slider(t["label_p_roi"], 1, 10,
                        st.session_state.get("priorite_roi", 5),
                        help=t["help_p_roi"], key="priorite_roi")
        p_g = st.slider(t["label_p_ges"], 0, 10,
                        st.session_state.get("priorite_ges", 5),
                        help=t["help_p_ges"], key="priorite_ges")
    with c2:
        p_p = st.slider(t["label_p_prod"], 0, 10,
                        st.session_state.get("priorite_prod", 5),
                        help=t["help_p_prod"], key="priorite_prod")
        p_m = st.slider(t["label_p_maint"], 0, 10,
                        st.session_state.get("priorite_maintenance", 5),
                        help=t["help_p_maint"], key="priorite_maintenance")
    total = p_e + p_r + p_g + p_p + p_m
    if total > 0:
        w = {k: v/total for k, v in zip(
            ["poids_energie","poids_roi","poids_ges","poids_prod","poids_maintenance"],
            [p_e, p_r, p_g, p_p, p_m]
        )}
        for k, v in w.items():
            st.session_state[k] = v
        st.markdown(f"**{t['titre_analyse']}**")
        labels = [t["r_ener"], t["r_roi"], t["r_ges"], t["r_prod"], t["r_maint"]]
        vals   = [w["poids_energie"]*100, w["poids_roi"]*100, w["poids_ges"]*100,
                  w["poids_prod"]*100, w["poids_maintenance"]*100]
        c1, c2 = st.columns([1, 2])
        with c1:
            for l, v in zip(labels, vals):
                st.markdown(f"- **{l}** : {v:.0f}%")
        with c2:
            fig, ax = plt.subplots(figsize=(4, 2.5))
            ax.barh(labels, vals, color=P, edgecolor="none", height=0.55)
            ax.set_xlabel("%", fontsize=8); ax.set_xlim(0, 100)
            ax.tick_params(axis="both", labelsize=8)
            ax.set_facecolor("none"); fig.patch.set_alpha(0)
            plt.tight_layout(); st.pyplot(fig)
    else:
        st.warning(t["warning_prio"])

# ═══════════════════════════════════════════════
# SECTION 7 — SERVICES
# ═══════════════════════════════════════════════
st.markdown('<div id="services"></div>', unsafe_allow_html=True)
with st.expander(f"7 — {'Services complémentaires' if lang=='fr' else 'Additional Services'}"):
    c1, c2, c3 = st.columns(3)
    with c1: st.checkbox(t["label_controle"],   key="controle")
    with c2: st.checkbox(t["label_maintenance"], key="maintenance")
    with c3: st.checkbox(t["label_ventilation"], key="ventilation_service")
    st.text_area(t["label_autres_svc"], key="autres_services")

# ═══════════════════════════════════════════════
# SECTION 8 — PDF + EXCEL + SOUMISSION
# ═══════════════════════════════════════════════
st.markdown('<div id="pdf"></div>', unsafe_allow_html=True)
with st.expander(f"8 — {'Récapitulatif et PDF' if lang=='fr' else 'Summary and PDF'}"):
    st.markdown(f'<div class="info-banner">{t["info_note"]}</div>', unsafe_allow_html=True)
    st.markdown("")

    # ── Génération PDF ────────────────────────
    def generer_pdf(*, client_nom, site_nom, adresse, ville, province, code_postal,
                    neq_val, contact_ee_nom, contact_ee_mail, contact_ee_tel,
                    contact_maint_nom, rempli_nom, rempli_date_str, sign_nom,
                    temps_fonctionnement, sauver_ges, economie_energie, gain_productivite,
                    roi_vise, investissement_prevu, autres_objectifs,
                    priorites, equipements, controle, maintenance, ventilation_svc,
                    autres_services, lang_pdf="fr"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        try:
            pdf.add_font("DV","","fonts/DejaVuSans.ttf",uni=True)
            pdf.add_font("DV","B","fonts/DejaVuSans-Bold.ttf",uni=True)
            FR = FB = "DV"
        except Exception:
            FR = FB = "Arial"
        BL = "-"

        def sec(txt):
            pdf.set_fill_color(205, 220, 57)
            pdf.set_font(FB,"B",11)
            pdf.cell(0, 8, txt, ln=True, fill=True)
            pdf.ln(1)

        def row(lbl, val):
            pdf.set_font(FR,"",10)
            pdf.cell(0, 7, f"{lbl} : {val or 'N/A'}", ln=True)

        try: pdf.image("Image/Logo Soteck.jpg", x=160, y=8, w=35)
        except Exception: pass

        pdf.set_font(FB,"B",16)
        pdf.cell(0, 10, "AUDIT FLASH - Résumé", ln=True, align="C")
        pdf.set_font(FR,"",9)
        pdf.cell(0, 6, f"Généré le {date.today().strftime('%d/%m/%Y')}", ln=True, align="C")
        pdf.ln(6)

        sec("1. Informations générales" if lang_pdf=="fr" else "1. General Information")
        row("Client", client_nom); row("Site", site_nom)
        if adresse or ville:
            row("Adresse", f"{adresse}, {ville}, {province} {code_postal}".strip(", "))
        if neq_val: row("NEQ", neq_val)
        if temps_fonctionnement: row("Heures/an", temps_fonctionnement)
        pdf.ln(2)

        sec("2. Contacts")
        row("Contact EE", f"{contact_ee_nom} – {contact_ee_mail} – {contact_ee_tel}")
        row("Maintenance", contact_maint_nom)
        row("Rempli par", f"{rempli_nom} ({rempli_date_str})")
        row("Signataire", sign_nom)
        pdf.ln(2)

        sec("3. Objectifs" if lang_pdf=="fr" else "3. Objectives")
        row("Réduction GES", f"{sauver_ges}%")
        row("Économie énergie", "Oui" if economie_energie else "Non")
        row("Productivité", "Oui" if gain_productivite else "Non")
        row("ROI visé", roi_vise)
        row("Investissement", investissement_prevu)
        if autres_objectifs:
            pdf.set_font(FR,"",10)
            pdf.multi_cell(0, 7, f"Autres : {autres_objectifs}")
        pdf.ln(2)

        sec("4. Services" if lang_pdf=="fr" else "4. Services")
        row("Contrôle", "Oui" if controle else "Non")
        row("Maintenance", "Oui" if maintenance else "Non")
        row("Ventilation", "Oui" if ventilation_svc else "Non")
        if autres_services:
            pdf.set_font(FR,"",10)
            pdf.multi_cell(0, 7, f"Autres : {autres_services}")
        pdf.ln(2)

        sec("5. Priorités" if lang_pdf=="fr" else "5. Priorities")
        pdf.set_font(FR,"",10)
        if priorites:
            for k, v in priorites.items():
                try: pdf.cell(0, 7, f"  {BL} {k} : {float(v):.0%}", ln=True)
                except Exception: pdf.cell(0, 7, f"  {BL} {k} : {v}", ln=True)
        else:
            pdf.cell(0, 7, "  Non renseignées", ln=True)
        pdf.ln(2)

        sec("6. Équipements identifiés" if lang_pdf=="fr" else "6. Equipment Identified")
        for bloc, items in equipements.items():
            pdf.set_font(FB,"B",10); pdf.cell(0, 7, f"{bloc} :", ln=True)
            pdf.set_font(FR,"",10)
            if items:
                for it in items: pdf.multi_cell(0, 6, f"    {BL} {_one_line(str(it))}")
            else:
                pdf.cell(0, 7, f"    ({t['aucun_eq']})", ln=True)

        try: pdf.image("Image/sous-page.jpg", x=10, y=265, w=190)
        except Exception: pass

        out = pdf.output(dest="S")
        return out if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")

    # Boutons génération + téléchargement
    col_g, col_d = st.columns(2)
    with col_g:
        if st.button(t["btn_gen"], use_container_width=True):
            missing = []
            cn = st.session_state.get("client_nom","").strip()
            sn = st.session_state.get("site_nom","").strip()
            em = st.session_state.get("contact_ee_mail","").strip()
            if not cn: missing.append(t["f_client"])
            if not sn: missing.append(t["f_site"])
            if em and not re.match(r"[^@]+@[^@]+\.[^@]+", em): missing.append(t["f_mail"])
            if missing:
                st.error(f"{t['err_missing']} {', '.join(missing)}")
            else:
                p_e = float(st.session_state.get("poids_energie", 0))
                p_r = float(st.session_state.get("poids_roi", 0))
                p_g = float(st.session_state.get("poids_ges", 0))
                p_p = float(st.session_state.get("poids_prod", 0))
                p_m = float(st.session_state.get("poids_maintenance", 0))
                prio = {}
                if p_e + p_r + p_g + p_p + p_m > 0:
                    prio = {t["r_ener"]: p_e, t["r_roi"]: p_r, t["r_ges"]: p_g,
                            t["r_prod"]: p_p, t["r_maint"]: p_m}
                eqs = {
                    t["tab_chaud"]: _safe_details(_chaudieres_detaille),
                    t["tab_frigo"]: _safe_details(_frigo_detaille),
                    t["tab_comp"]:  _safe_details(_compresseurs_detaille),
                    t["tab_dep"]:   _safe_details(_depoussieurs_detaille),
                    t["tab_pompes"]:_safe_details(_pompes_detaille),
                    t["tab_vent"]:  _safe_details(_ventilation_detaille),
                    t["tab_mach"]:  _safe_details(_machines_detaille),
                    t["tab_ecl"]:   _safe_details(_eclairage_detaille),
                }
                pdf_b = generer_pdf(
                    client_nom=cn, site_nom=sn,
                    adresse=st.session_state.get("adresse",""),
                    ville=st.session_state.get("ville",""),
                    province=st.session_state.get("province",""),
                    code_postal=st.session_state.get("code_postal",""),
                    neq_val=st.session_state.get("neq_clean",""),
                    contact_ee_nom=st.session_state.get("contact_ee_nom",""),
                    contact_ee_mail=st.session_state.get("contact_ee_mail",""),
                    contact_ee_tel=st.session_state.get("contact_ee_tel",""),
                    contact_maint_nom=st.session_state.get("contact_maint_nom",""),
                    rempli_nom=st.session_state.get("rempli_nom",""),
                    rempli_date_str=str(st.session_state.get("rempli_date", date.today())),
                    sign_nom=st.session_state.get("sign_nom",""),
                    temps_fonctionnement=st.session_state.get("temps_fonctionnement",""),
                    sauver_ges=str(st.session_state.get("sauver_ges","")),
                    economie_energie=bool(st.session_state.get("economie_energie", False)),
                    gain_productivite=bool(st.session_state.get("gain_productivite", False)),
                    roi_vise=str(st.session_state.get("roi_vise","")),
                    investissement_prevu=str(st.session_state.get("investissement_prevu","")),
                    autres_objectifs=str(st.session_state.get("autres_objectifs","")),
                    priorites=prio, equipements=eqs,
                    controle=bool(st.session_state.get("controle", False)),
                    maintenance=bool(st.session_state.get("maintenance", False)),
                    ventilation_svc=bool(st.session_state.get("ventilation_service", False)),
                    autres_services=str(st.session_state.get("autres_services","")),
                    lang_pdf=lang,
                )
                st.session_state["pdf_bytes"] = pdf_b
                st.session_state["pdf_cn"] = cn
                st.session_state["pdf_sn"] = sn
                st.success(t["ok_pdf"])
    with col_d:
        if "pdf_bytes" in st.session_state:
            cn = st.session_state.get("pdf_cn","client")
            sn = st.session_state.get("pdf_sn","site")
            st.download_button(
                t["btn_dl"], data=st.session_state["pdf_bytes"],
                file_name=f"audit_flash_{_slug(sn)}_{_slug(cn)}.pdf",
                mime="application/pdf", use_container_width=True
            )

    # ── Export Excel ──────────────────────────
    st.divider()
    if st.checkbox(t["lbl_excel"]):
        data_xl = {
            "Client": [st.session_state.get("client_nom","N/A")],
            "Site":   [st.session_state.get("site_nom","N/A")],
            "GES (%)": [st.session_state.get("sauver_ges","N/A")],
            "ROI":    [st.session_state.get("roi_vise","N/A")],
            "Contrôle": ["Oui" if st.session_state.get("controle") else "Non"],
            "Maintenance": ["Oui" if st.session_state.get("maintenance") else "Non"],
            "Ventilation": ["Oui" if st.session_state.get("ventilation_service") else "Non"],
            "Poids Énergie":     [f"{float(st.session_state.get('poids_energie',0)):.0%}"],
            "Poids ROI":         [f"{float(st.session_state.get('poids_roi',0)):.0%}"],
            "Poids GES":         [f"{float(st.session_state.get('poids_ges',0)):.0%}"],
            "Poids Productivité":[f"{float(st.session_state.get('poids_prod',0)):.0%}"],
            "Poids Maintenance": [f"{float(st.session_state.get('poids_maintenance',0)):.0%}"],
        }
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
            pd.DataFrame(data_xl).to_excel(w, index=False, sheet_name="Audit Flash")
        buf.seek(0)
        st.download_button(
            t["btn_excel"], data=buf,
            file_name=f"audit_flash_{_slug(st.session_state.get('site_nom','site'))}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ── Soumission email ──────────────────────
    st.divider()
    if st.button(t["btn_soumettre"], use_container_width=True):
        pdf_b = st.session_state.get("pdf_bytes")
        if not pdf_b:
            st.error(t["err_pdf"])
        else:
            cn  = st.session_state.get("client_nom","")
            sn  = st.session_state.get("site_nom","")
            ee_m = st.session_state.get("contact_ee_mail","")
            re_m = st.session_state.get("rempli_mail","")
            facture_elec = st.session_state.get("facture_elec_files",[])
            facture_comb = st.session_state.get("facture_comb_files",[])
            facture_aut  = st.session_state.get("facture_aut_files",[])
            plans        = st.session_state.get("plans_pid_files",[])

            def _nm(lst): return ", ".join(f.name for f in (lst or [])) or "—"

            lines = [
                "Bonjour,\n",
                "Ci-joint le résumé de l'Audit Flash.\n",
                "——— INFOS GÉNÉRALES ———",
                f"Client : {cn or 'N/A'}", f"Site : {sn or 'N/A'}",
                f"Adresse : {st.session_state.get('adresse','')} "
                f"{st.session_state.get('ville','')} {st.session_state.get('province','')}".strip(),
                "", "——— CONTACTS ———",
                f"EE : {st.session_state.get('contact_ee_nom','')} – {ee_m} – "
                f"{st.session_state.get('contact_ee_tel','')}",
                f"Maint. : {st.session_state.get('contact_maint_nom','')}",
                f"Rempli : {st.session_state.get('rempli_nom','')} "
                f"({st.session_state.get('rempli_date','')}) – {re_m}",
                "", "——— OBJECTIFS ———",
                f"GES : {st.session_state.get('sauver_ges','')}%",
                f"ROI : {st.session_state.get('roi_vise','')}",
                "", "——— ÉQUIPEMENTS ———",
            ]
            for lbl, fn in [
                (t["tab_chaud"], _chaudieres_detaille),
                (t["tab_frigo"], _frigo_detaille),
                (t["tab_comp"],  _compresseurs_detaille),
                (t["tab_dep"],   _depoussieurs_detaille),
                (t["tab_pompes"],_pompes_detaille),
                (t["tab_vent"],  _ventilation_detaille),
                (t["tab_mach"],  _machines_detaille),
                (t["tab_ecl"],   _eclairage_detaille),
            ]:
                L = _safe_details(fn)
                lines.append(f"- {lbl} :")
                lines.extend([f"    • {s}" for s in L] if L else ["    —"])

            lines += [
                "", "——— PIÈCES JOINTES ———",
                f"Élec. : {_nm(facture_elec)}",
                f"Combust. : {_nm(facture_comb)}",
                f"Autres : {_nm(facture_aut)}",
                f"Plans : {_nm(plans)}",
                "", "Cordialement,\nSoteck",
            ]
            resume = "\n".join(lines)
            fname = f"AuditFlash_{_slug(sn)}_{_slug(cn)}.pdf"

            try:
                pwd  = str(st.secrets["email_password"]).strip()
                dest = ["mbencharif@soteck.com","pdelorme@soteck.com"]
                msg  = EmailMessage()
                msg["Subject"] = (f"{'Audit Flash' if lang=='fr' else 'Flash Audit'} – "
                                  f"{_one_line(sn)} – {_one_line(cn)}")
                msg["From"]    = "elmehdi.bencharif@gmail.com"
                msg["To"]      = ", ".join(dest)
                def _vm(x): return isinstance(x,str) and re.match(r"[^@]+@[^@]+\.[^@]+",x.strip())
                cc = [a for a in [re_m, ee_m] if _vm(a) and a not in dest]
                if cc: msg["Cc"] = ", ".join(cc)
                if _vm(re_m): msg["Reply-To"] = re_m
                msg.set_content(resume)
                msg.add_attachment(pdf_b, maintype="application", subtype="pdf", filename=fname)
                for grp in [facture_elec, facture_comb, facture_aut, plans]:
                    for f in (grp or []):
                        try:
                            msg.add_attachment(f.getvalue(), maintype="application",
                                               subtype="octet-stream", filename=f.name)
                        except Exception:
                            pass
                with smtplib.SMTP("smtp.gmail.com", 587) as srv:
                    srv.ehlo(); srv.starttls(); srv.ehlo()
                    srv.login("elmehdi.bencharif@gmail.com", pwd)
                    srv.send_message(msg)
                st.success(t["ok_envoi"])
            except smtplib.SMTPAuthenticationError as e:
                st.error(f"Auth SMTP refusée ({e.smtp_code}) : {e.smtp_error}")
            except Exception as e:
                st.error(f"Erreur envoi : {e}")

# ─────────────────────────────────────────────
# AUTOSAVE
# ─────────────────────────────────────────────
autosave(form_id)
