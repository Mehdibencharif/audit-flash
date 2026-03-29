# ==== IMPORTS ====
import streamlit as st
from datetime import date
from fpdf import FPDF
import io, re, os, json, hashlib, uuid, smtplib
import pandas as pd
from email.message import EmailMessage
import matplotlib.pyplot as plt
import requests
import urllib.parse
from io import BytesIO

# ==== CONFIG GLOBALE ====
st.set_page_config(
    page_title="Audit Flash – Soteck Clauger",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SUPABASE
# ─────────────────────────────────────────────
try:
    from supabase import create_client, Client

    @st.cache_resource
    def supabase_client() -> Client:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

    sb = supabase_client()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False
    sb = None


def _df_to_dict(key: str):
    val = st.session_state.get(key)
    if isinstance(val, pd.DataFrame):
        return val.to_dict("records")
    if isinstance(val, dict):
        rows = []
        rows.extend(val.get("added_rows", []) or [])
        edited = val.get("edited_rows")
        if isinstance(edited, dict):
            rows.extend(edited.values())
        return rows
    if isinstance(val, list):
        return val
    return []


def collecter_donnees_formulaire():
    return {
        "client_nom": st.session_state.get("client_nom", ""),
        "site_nom": st.session_state.get("site_nom", ""),
        "adresse": st.session_state.get("adresse", ""),
        "ville": st.session_state.get("ville", ""),
        "province": st.session_state.get("province", ""),
        "code_postal": st.session_state.get("code_postal", ""),
        "neq": st.session_state.get("neq_clean", ""),
        "contact_ee_nom": st.session_state.get("contact_ee_nom", ""),
        "contact_ee_mail": st.session_state.get("contact_ee_mail", ""),
        "contact_ee_tel": st.session_state.get("contact_ee_tel", ""),
        "contact_ee_ext": st.session_state.get("contact_ee_ext", ""),
        "contact_maint_nom": st.session_state.get("contact_maint_nom", ""),
        "contact_maint_mail": st.session_state.get("contact_maint_mail", ""),
        "contact_maint_tel": st.session_state.get("contact_maint_tel", ""),
        "contact_maint_ext": st.session_state.get("contact_maint_ext", ""),
        "rempli_nom": st.session_state.get("rempli_nom", ""),
        "rempli_date": str(st.session_state.get("rempli_date", "")),
        "rempli_mail": st.session_state.get("rempli_mail", ""),
        "rempli_tel": st.session_state.get("rempli_tel", ""),
        "rempli_ext": st.session_state.get("rempli_ext", ""),
        "sign_nom": st.session_state.get("sign_nom", ""),
        "sign_mail": st.session_state.get("sign_mail", ""),
        "sauver_ges": st.session_state.get("sauver_ges", ""),
        "economie_energie": st.session_state.get("economie_energie", False),
        "gain_productivite": st.session_state.get("gain_productivite", False),
        "roi_vise": st.session_state.get("roi_vise", ""),
        "remplacement_equipement": st.session_state.get("remplacement_equipement", False),
        "investissement_prevu": st.session_state.get("investissement_prevu", ""),
        "autres_objectifs": st.session_state.get("autres_objectifs", ""),
        "priorite_energie": st.session_state.get("priorite_energie", 5),
        "priorite_roi": st.session_state.get("priorite_roi", 5),
        "priorite_ges": st.session_state.get("priorite_ges", 5),
        "priorite_prod": st.session_state.get("priorite_prod", 5),
        "priorite_maintenance": st.session_state.get("priorite_maintenance", 5),
        "controle": st.session_state.get("controle", False),
        "maintenance": st.session_state.get("maintenance", False),
        "ventilation_service": st.session_state.get("ventilation_service", False),
        "autres_services": st.session_state.get("autres_services", ""),
        "temps_fonctionnement": st.session_state.get("temps_fonctionnement", ""),
        "chaudieres": _df_to_dict("chaudieres"),
        "frigo": _df_to_dict("frigo"),
        "compresseur": _df_to_dict("compresseur"),
        "pompes": _df_to_dict("pompes"),
        "ventilation_eq": _df_to_dict("ventilation_eq"),
        "machines": _df_to_dict("machines"),
        "eclairage": _df_to_dict("eclairage"),
        "depoussieur": _df_to_dict("depoussieur"),
    }


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
                    st.session_state["formulaire_charge"] = True
            except Exception as e:
                st.warning("⚠️ Supabase indisponible (chargement ignoré).")
        return fid
    new_id = str(uuid.uuid4())
    st.session_state["form_id"] = new_id
    st.query_params["form_id"] = new_id
    if SUPABASE_OK:
        try:
            sb.table("forms").upsert(
                {"form_id": new_id, "data": {}, "email_contact": "", "status": "en_cours"}
            ).execute()
        except Exception:
            pass
    return new_id


def save_form(form_id: str):
    if not SUPABASE_OK:
        return False
    data = collecter_donnees_formulaire()
    email = data.get("contact_ee_mail", "")
    try:
        sb.table("forms").upsert(
            {"form_id": form_id, "data": data, "email_contact": email, "status": "en_cours"}
        ).execute()
        return True
    except Exception as e:
        st.session_state["supabase_error"] = str(e)
        return False


def autosave_if_changed(form_id: str):
    payload = collecter_donnees_formulaire()
    digest = hashlib.md5(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    if st.session_state.get("_last_digest") != digest:
        ok = save_form(form_id)
        st.session_state["_last_digest"] = digest


form_id = get_or_create_form_id()

# ─────────────────────────────────────────────
# HELPERS GÉNÉRIQUES
# ─────────────────────────────────────────────
def _one_line(s: str) -> str:
    return re.sub(r"[\r\n]+", " ", (s or "").strip())


def _slug(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", (x or "").strip())


def _val(x, suffix: str = "") -> str:
    if isinstance(x, (int, float)) and not pd.isna(x):
        return f"{x:g}{suffix}"
    s = (str(x) if x is not None else "").strip()
    return s + suffix if s else "n/d"


def _yn(x) -> str:
    if isinstance(x, bool):
        return "Oui" if x else "Non"
    s = (str(x) if x is not None else "").strip().lower()
    if s in {"oui", "yes", "y", "true", "vrai", "1"}:
        return "Oui"
    if s in {"non", "no", "n", "false", "faux", "0"}:
        return "Non"
    return "n/d"


def _df_depuis_editor(key: str) -> pd.DataFrame:
    val = st.session_state.get(key, None)
    if isinstance(val, pd.DataFrame):
        return val.copy()
    if isinstance(val, dict):
        rows = []
        if isinstance(val.get("added_rows"), list):
            rows.extend(val["added_rows"])
        if isinstance(val.get("edited_rows"), dict):
            rows.extend(val["edited_rows"].values())
        return pd.DataFrame(rows)
    if isinstance(val, list) and all(isinstance(x, dict) for x in val):
        return pd.DataFrame(val)
    return pd.DataFrame()


def _EQ():
    return st.session_state.get("_EQ", {})


# ─────────────────────────────────────────────
# HELPERS DÉTAILS ÉQUIPEMENTS
# ─────────────────────────────────────────────
def _chaudieres_detaille() -> list:
    df = _df_depuis_editor("chaudieres")
    if df.empty:
        return []
    t = _EQ()
    c_type = t.get("label_type_chaudiere", "Type de chaudière")
    c_rend = t.get("label_rendement_chaudiere", "Rendement chaudière (%)")
    c_taille = t.get("label_taille_chaudiere", "Taille de la chaudière (BHP ou BTU)")
    c_app = t.get("label_appoint_eau", "Appoint d'eau (volume)")
    c_micro = t.get("label_micro_modulation", "Micro modulation ?")
    c_eco = t.get("label_economiseur_chaudiere", "Économiseur installé ?")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(
            f"{nom} – {_val(r.get(c_type))} – Rend: {_val(r.get(c_rend),'%')} – "
            f"Taille: {_val(r.get(c_taille))} – Appoint: {_val(r.get(c_app))} – "
            f"Micro-mod: {_yn(r.get(c_micro))} – Éco: {_yn(r.get(c_eco))}"
        )
    return L


def _frigo_detaille() -> list:
    df = _df_depuis_editor("frigo")
    if df.empty:
        return []
    t = _EQ()
    c_cap = t.get("label_capacite_frigo", "Capacité frigorifique")
    c_ref = t.get("label_nom_frigorigenes", "Nom du frigorigène")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(f"{nom} – Cap: {_val(r.get(c_cap))} – Réfrigérant: {_val(r.get(c_ref))}")
    return L


def _compresseurs_detaille() -> list:
    df = _df_depuis_editor("compresseur")
    if df.empty:
        return []
    t = _EQ()
    c_hp = t.get("label_puissance_comp", "Puissance compresseur (HP)")
    c_vfd = t.get("label_variation_vitesse", "Variation de vitesse compresseur")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(f"{nom} – {_val(r.get(c_hp),' HP')} – VFD: {_yn(r.get(c_vfd))}")
    return L


def _depoussieurs_detaille() -> list:
    """Unique définition — pas de doublon."""
    df = _df_depuis_editor("depoussieur")
    if df.empty:
        return []
    t = _EQ()
    hp_label = t.get("label_puissance_dep_hp", "Puissance (HP)")
    vfd_label = t.get("label_vfd_dep", "Variateur de vitesse (VFD)")
    marque_label = t.get("label_marque_dep", "Marque")
    for c in ["Nom", hp_label, vfd_label, marque_label]:
        if c not in df.columns:
            df[c] = ""
    lignes = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip()
        if not nom:
            continue
        hp = r[hp_label]
        vfd = r[vfd_label]
        marque = r[marque_label]
        hp_txt = f"{hp} HP" if (pd.notna(hp) and str(hp).strip() != "") else "HP n/d"
        vfd_txt = "Oui" if _yn(vfd) == "Oui" else "Non"
        marque_txt = f" – {marque}" if isinstance(marque, str) and marque.strip() else ""
        lignes.append(f"{nom} – {hp_txt} – VFD: {vfd_txt}{marque_txt}")
    return lignes


def _pompes_detaille() -> list:
    df = _df_depuis_editor("pompes")
    if df.empty:
        return []
    t = _EQ()
    c_type = t.get("label_type_pompe", "Type de pompe")
    c_pow = t.get("label_puissance_pompe", "Puissance pompe (kW ou HP)")
    c_rend = t.get("label_rendement_pompe", "Rendement pompe (%)")
    c_vfd = t.get("label_vitesse_variable_pompe", "Variateur de vitesse pompe")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(
            f"{nom} – {_val(r.get(c_type))} – {_val(r.get(c_pow))} – "
            f"Rend: {_val(r.get(c_rend),'%')} – VFD: {_yn(r.get(c_vfd))}"
        )
    return L


def _ventilation_detaille() -> list:
    df = _df_depuis_editor("ventilation_eq")
    if df.empty:
        return []
    t = _EQ()
    c_type = t.get("label_type_ventilation", "Type de ventilation")
    c_pow = t.get("label_puissance_ventilation", "Puissance ventilation (kWh)")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(f"{nom} – {_val(r.get(c_type))} – {_val(r.get(c_pow))}")
    return L


def _machines_detaille() -> list:
    df = _df_depuis_editor("machines")
    if df.empty:
        return []
    t = _EQ()
    c_pow = t.get("label_puissance_machine", "Puissance machine (kW)")
    c_tu = t.get("label_taux_utilisation", "Taux d'utilisation (%)")
    c_rend = t.get("label_rendement_machine", "Rendement machine (%)")
    c_src = t.get("label_source_energie_machine", "Source d'énergie")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(
            f"{nom} – {_val(r.get(c_pow),' kW')} – Tu: {_val(r.get(c_tu),'%')} – "
            f"Rend: {_val(r.get(c_rend),'%')} – {_val(r.get(c_src))}"
        )
    return L


def _eclairage_detaille() -> list:
    df = _df_depuis_editor("eclairage")
    if df.empty:
        return []
    t = _EQ()
    c_type = t.get("label_type_eclairage", "Type d'éclairage")
    c_pow = t.get("label_puissance_totale_eclairage", "Puissance totale installée (kW)")
    c_h = t.get("label_heures_utilisation", "Heures/jour")
    L = []
    for _, r in df.iterrows():
        nom = str(r.get("Nom", "")).strip() or "Sans nom"
        L.append(f"{nom} – {_val(r.get(c_type))} – {_val(r.get(c_pow),' kW')} – {_val(r.get(c_h),'h/j')}")
    return L


def _safe_details(fn):
    try:
        return fn() if callable(fn) else fn
    except Exception:
        return []


# ─────────────────────────────────────────────
# GROQ CHATBOT
# ─────────────────────────────────────────────
def _get_groq_key():
    key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_APIKEY")
    try:
        key = key or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_APIKEY")
    except Exception:
        pass
    if not key:
        return None
    return str(key).strip().strip('"').strip("'")


def repondre_a_question(question: str, langue: str = "fr") -> str:
    q = (question or "").strip()
    if not q:
        return "⚠️ Aucune question fournie."
    api_key = _get_groq_key()
    if not api_key:
        return "⚠️ Clé GROQ_API_KEY manquante dans Secrets."
    system_msg = (
        "Tu es un assistant concis en efficacité énergétique industrielle. "
        "Réponds en {langue} avec définitions claires, formules simples, "
        "règles de pouce et un mini-exemple si utile. Sois bref et précis."
    ).format(langue="français" if langue.lower().startswith("fr") else "English")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": q},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=45)
        if r.status_code != 200:
            return f"⚠️ Erreur Groq ({r.status_code}) : {r.json()}"
        return (r.json()["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        return f"⚠️ Erreur : {e}"


# ─────────────────────────────────────────────
# LANGUE (avant tout le reste)
# ─────────────────────────────────────────────
# Initialise la langue dans session_state pour éviter le reset au rerun
if "langue" not in st.session_state:
    st.session_state["langue"] = "Français"

# ─────────────────────────────────────────────
# THÈME
# ─────────────────────────────────────────────
if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = "Mode clair"

couleur_primaire = "#cddc39"

if st.session_state["ui_theme"] == "Mode clair":
    couleur_fond = "#f5f7fa"
    texte_couleur = "#1e2a38"
    carte_fond = "#ffffff"
    bordure = "#dde3ec"
    primaire_hover = "#afb42b"
    sidebar_bg = "#ffffff"
    input_bg = "#ffffff"
    section_text = "#1e2a38"
else:
    couleur_fond = "#0d1b2e"
    texte_couleur = "#e8edf5"
    carte_fond = "#152036"
    bordure = "#1e3356"
    primaire_hover = "#9bd400"
    sidebar_bg = "#0b1628"
    input_bg = "#1a2d47"
    section_text = "#e8edf5"

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=Space+Grotesk:wght@400;600;700&display=swap');

/* ── Base ── */
.stApp {{
    background-color: {couleur_fond} !important;
    color: {texte_couleur} !important;
    font-family: 'DM Sans', sans-serif;
}}
.stApp p, .stApp li, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {{
    color: {texte_couleur} !important;
    font-family: 'DM Sans', sans-serif;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    width: 400px !important;
    background: {sidebar_bg} !important;
    border-right: 2px solid {bordure};
}}
@media (max-width: 1200px) {{
    section[data-testid="stSidebar"] {{ width: 340px !important; }}
}}

/* ── Header principal ── */
.app-header {{
    display: flex;
    align-items: center;
    gap: 18px;
    background: linear-gradient(135deg, {carte_fond} 0%, {couleur_fond} 100%);
    border: 1px solid {bordure};
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}}
.app-header-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: {texte_couleur} !important;
    line-height: 1.2;
}}
.app-header-sub {{
    font-size: 13px;
    color: {texte_couleur};
    opacity: 0.6;
    margin-top: 4px;
}}
.accent-dot {{
    display: inline-block;
    width: 10px; height: 10px;
    background: {couleur_primaire};
    border-radius: 50%;
    margin-right: 6px;
}}

/* ── Titres de section ── */
.section-title {{
    background: linear-gradient(90deg, {couleur_primaire}22 0%, {couleur_primaire}08 100%);
    border-left: 4px solid {couleur_primaire};
    color: {texte_couleur} !important;
    padding: 10px 16px;
    border-radius: 0 8px 8px 0;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 16px;
    margin: 20px 0 12px 0;
}}

/* ── Badges de section ── */
.section-badge {{
    display: inline-block;
    background: {couleur_primaire};
    color: #1a1a1a;
    font-weight: 700;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 999px;
    margin-right: 8px;
    vertical-align: middle;
}}

/* ── Expander ── */
details summary {{
    font-weight: 500 !important;
    color: {texte_couleur} !important;
}}
.stExpander {{
    border: 1px solid {bordure} !important;
    border-radius: 10px !important;
    background: {carte_fond} !important;
    margin-bottom: 8px;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {{
    background: {input_bg} !important;
    border: 1px solid {bordure} !important;
    border-radius: 8px !important;
    color: {texte_couleur} !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {couleur_primaire} !important;
    box-shadow: 0 0 0 3px {couleur_primaire}33 !important;
}}

/* ── Boutons ── */
div.stButton > button {{
    background: {couleur_primaire} !important;
    color: #1a1a1a !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 600 !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.2s ease;
}}
div.stButton > button:hover {{
    background: {primaire_hover} !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px {couleur_primaire}55;
}}

/* ── Download button ── */
div.stDownloadButton > button {{
    background: {carte_fond} !important;
    color: {texte_couleur} !important;
    border: 2px solid {couleur_primaire} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
div.stDownloadButton > button:hover {{
    background: {couleur_primaire}22 !important;
}}

/* ── Sidebar chatbot ── */
.chat-hero {{
    background: linear-gradient(135deg, {couleur_primaire} 0%, #8bc34a 100%);
    color: #1a1a1a;
    padding: 14px 16px;
    border-radius: 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px {couleur_primaire}44;
}}
.chat-card {{
    background: {carte_fond};
    border: 1px solid {bordure};
    border-radius: 12px;
    padding: 14px;
}}
.chat-response {{
    background: {couleur_fond};
    border: 1px solid {bordure};
    border-left: 3px solid {couleur_primaire};
    border-radius: 8px;
    padding: 12px;
    font-size: 13px;
    line-height: 1.6;
    color: {texte_couleur};
    margin-top: 10px;
}}

/* ── Liens ── */
a, a:visited {{ color: {couleur_primaire} !important; }}
a:hover {{ color: {primaire_hover} !important; }}

/* ── Divider ── */
hr {{ border-color: {bordure} !important; opacity: 0.5; }}

/* ── Progress / Slider ── */
.stSlider > div > div > div {{ background: {couleur_primaire} !important; }}

/* ── Tableaux data_editor ── */
.stDataFrame, .stDataEditor {{
    border: 1px solid {bordure} !important;
    border-radius: 8px !important;
}}

/* ── Barre de langue/thème ── */
.top-controls {{
    display: flex;
    gap: 20px;
    align-items: center;
    background: {carte_fond};
    border: 1px solid {bordure};
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 16px;
}}

/* ── Sommaire ── */
.sommaire-card {{
    background: {carte_fond};
    border: 1px solid {bordure};
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
}}
.sommaire-card a {{
    text-decoration: none;
    color: {texte_couleur} !important;
    font-size: 14px;
    opacity: 0.85;
}}
.sommaire-card a:hover {{ color: {couleur_primaire} !important; opacity: 1; }}

/* ── Share card ── */
.share-card {{
    background: {carte_fond};
    border: 1px solid {bordure};
    border-radius: 12px;
    padding: 14px 16px;
    margin: 8px 0;
}}
.share-pill {{
    display: inline-block;
    background: {couleur_primaire};
    color: #1a1a1a;
    font-weight: 700;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 999px;
    margin-right: 8px;
}}
.share-link {{
    font-family: monospace;
    font-size: 12px;
    background: {couleur_fond};
    color: {texte_couleur};
    padding: 4px 8px;
    border-radius: 6px;
    border: 1px solid {bordure};
    word-break: break-all;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR — Langue + Thème + Chatbot
# ─────────────────────────────────────────────
with st.sidebar:
    # Langue
    langue = st.radio(
        "🌐 Langue / Language",
        ("Français", "English"),
        horizontal=True,
        key="langue",
    )
    lang = "fr" if langue == "Français" else "en"

    # Thème
    st.radio(
        "🎨 Apparence",
        ("Mode clair", "Mode sombre"),
        horizontal=True,
        key="ui_theme",
    )

    st.divider()

    # Chatbot
    st.markdown("<div class='chat-hero'>⚡ Assistant Audit Flash</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='chat-card'>", unsafe_allow_html=True)

        user_question = st.text_area(
            "💬 Votre question :",
            key="chatbot_input",
            placeholder="Ex : C'est quoi un VFD ? Comment calculer le ROI ?",
            height=85,
        )

        col_send, col_clear = st.columns([3, 1])
        with col_send:
            envoyer = st.button("Envoyer ➤", key="chatbot_button", use_container_width=True)
        with col_clear:
            if st.button("✕", key="chatbot_clear", help="Effacer"):
                st.session_state["chatbot_response"] = ""

        if envoyer:
            if user_question.strip():
                with st.spinner("Réflexion en cours…"):
                    reponse = repondre_a_question(user_question, langue="en" if lang == "en" else "fr")
                st.session_state["chatbot_response"] = reponse
            else:
                st.warning("Veuillez écrire une question.")

        if st.session_state.get("chatbot_response"):
            r = st.session_state["chatbot_response"]
            if r.startswith("⚠️"):
                st.error(r)
            else:
                st.markdown(f"<div class='chat-response'>{r}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Lien de reprise
    public_base = ""
    try:
        public_base = st.secrets.get("PUBLIC_BASE_URL", "").rstrip("/")
    except Exception:
        pass
    resume_url = f"{public_base}?form_id={form_id}" if public_base else f"?form_id={form_id}"
    resume_url_encoded = urllib.parse.quote_plus(resume_url)

    st.markdown("<div class='share-card'>", unsafe_allow_html=True)
    st.markdown(f"<span class='share-pill'>🔗 Lien de reprise</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='share-link'>{resume_url}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📧 E-mail", f"mailto:?subject=Reprendre%20le%20formulaire&body={resume_url_encoded}", use_container_width=True)
    with col2:
        st.link_button("💬 WhatsApp", f"https://wa.me/?text={resume_url_encoded}", use_container_width=True)

    try:
        import qrcode
        img = qrcode.make(resume_url)
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        st.image(buf, caption="Scanner pour reprendre", width=140)
    except Exception:
        pass

# ─────────────────────────────────────────────
# MAIN — Déterminer lang (déjà dans session_state)
# ─────────────────────────────────────────────
lang = "fr" if st.session_state.get("langue", "Français") == "Français" else "en"

# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────
logo_path = "Image/Logo Soteck.jpg"
logo_exists = os.path.exists(logo_path)

col_title, col_logo = st.columns([4, 1])
with col_title:
    subtitle = (
        "Formulaire de prise de besoin – Audit énergétique industriel"
        if lang == "fr"
        else "Needs Assessment Form – Industrial Energy Audit"
    )
    st.markdown(f"""
    <div class="app-header">
        <div>
            <div class="app-header-title">
                <span class="accent-dot"></span>Audit Flash
            </div>
            <div class="app-header-sub">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_logo:
    if logo_exists:
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown(
            "<div style='text-align:right;font-size:12px;opacity:0.5;'>Soteck Clauger</div>",
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────
# MESSAGE DE BIENVENUE
# ─────────────────────────────────────────────
if lang == "fr":
    st.info(
        "Bienvenue. Remplissez toutes les sections ci-dessous pour que nous puissions préparer "
        "votre audit de manière efficace. Vos données sont sauvegardées automatiquement."
    )
    st.markdown("🔗 **[Soteck Clauger](https://www.soteck.com/fr)** — En savoir plus sur nos services")
else:
    st.info(
        "Welcome. Please fill out all sections below so that we can efficiently prepare your audit. "
        "Your data is automatically saved."
    )
    st.markdown("🔗 **[Soteck Clauger](https://www.soteck.com/en)** — Learn more about our services")

# ─────────────────────────────────────────────
# SOMMAIRE
# ─────────────────────────────────────────────
if lang == "fr":
    sommaire_items = [
        ("1", "Informations générales", "infos"),
        ("2", "Personnes contacts", "contacts"),
        ("3", "Documents à fournir", "docs"),
        ("4", "Objectifs du client", "objectifs"),
        ("5", "Liste des équipements", "equipements"),
        ("6", "Priorités stratégiques", "priorites"),
        ("7", "Services complémentaires", "services"),
        ("8", "Récapitulatif & PDF", "pdf"),
    ]
else:
    sommaire_items = [
        ("1", "General Information", "infos"),
        ("2", "Contact Persons", "contacts"),
        ("3", "Documents to Provide", "docs"),
        ("4", "Client Objectives", "objectifs"),
        ("5", "Equipment List", "equipements"),
        ("6", "Strategic Priorities", "priorites"),
        ("7", "Additional Services", "services"),
        ("8", "Summary & PDF", "pdf"),
    ]

sommaire_html = "".join(
    f'<a href="#{anchor}"><span class="section-badge">{num}</span>{label}</a> &nbsp;|&nbsp; '
    for num, label, anchor in sommaire_items
).rstrip(" &nbsp;|&nbsp; ")

st.markdown(
    f"<div class='sommaire-card'><strong>{'Sommaire' if lang=='fr' else 'Contents'}</strong><br><br>{sommaire_html}</div>",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════
# TRADUCTIONS UNIFIÉES
# ═══════════════════════════════════════════════
T = {
    "fr": {
        # Section 1
        "titre_infos": "📄 1. Informations générales",
        "exp_infos": "Remplir les informations générales",
        "label_client_nom": "Nom du client *",
        "aide_client_nom": "Ex: Biscuits Leclerc",
        "label_site_nom": "Nom du site *",
        "label_adresse": "Adresse",
        "label_ville": "Ville",
        "label_province": "Province",
        "label_code_postal": "Code postal",
        "label_neq": "NEQ (Québec)",
        "help_neq": "10 chiffres, ex : 1140007365",
        # Section 2
        "titre_contacts": "👥 2. Personnes contacts",
        "exp_contacts": "Remplir les contacts",
        "sous_titre_ee": "🔌 Contact Efficacité Énergétique",
        "sous_titre_maint": "🛠️ Contact Maintenance (externe)",
        "titre_remplisseur": "👤 Personne ayant rempli le formulaire",
        "sous_titre_sign": "✍️ Signataire autorisé",
        "label_nom": "Prénom et Nom",
        "label_mail": "Courriel",
        "label_tel": "Téléphone",
        "label_ext": "Extension",
        "label_date": "Date de remplissage",
        "help_mail": "Format : exemple@domaine.com",
        "help_tel": "10 chiffres recommandés",
        # Section 3
        "titre_docs": "📑 3. Documents à fournir",
        "exp_docs": "Téléverser les documents",
        "label_facture_elec": "Factures électricité (1 à 3 ans)",
        "label_facture_comb": "Factures Gaz / Mazout / Propane / Bois",
        "label_facture_autres": "Autres consommables (azote, eau, CO2…)",
        "label_plans_pid": "Plans d'aménagement et P&ID",
        "label_temps_fonct": "Temps de fonctionnement de l'usine (heures/an)",
        "fichiers_tele": "📂 Fichiers téléversés",
        # Section 4
        "titre_obj": "🎯 4. Objectifs du client",
        "exp_obj": "Remplir les objectifs",
        "label_ges": "Objectif de réduction GES (%)",
        "help_ges": "Ex : 20",
        "label_eco_ener": "Économie d'énergie",
        "label_prod": "Productivité accrue (coûts, temps)",
        "label_roi": "Retour sur investissement visé",
        "label_remplacement": "Remplacement d'équipement prévu",
        "label_invest": "Investissement prévu (montant et date)",
        "label_autres_obj": "Autres objectifs",
        # Section 5
        "titre_eq": "⚙️ 5. Liste des équipements",
        "exp_eq": "Remplir les équipements",
        "sous_chaudieres": "🔥 Chaudières",
        "sous_frigo": "❄️ Équipements frigorifiques",
        "sous_comp": "💨 Compresseurs d'air",
        "sous_dep": "🧹 Dépoussiéreurs",
        "sous_pompes": "🚰 Pompes industrielles",
        "sous_vent": "🌬️ Ventilation / HVAC",
        "sous_machines": "🛠️ Autres machines de production",
        "sous_ecl": "💡 Éclairage",
        "apercu": "Aperçu :",
        "label_type_chaudiere": "Type de chaudière",
        "label_rendement_chaudiere": "Rendement (%)",
        "label_taille_chaudiere": "Taille (BHP ou BTU)",
        "label_appoint_eau": "Appoint d'eau (volume)",
        "label_micro_modulation": "Micro modulation ?",
        "label_economiseur_chaudiere": "Économiseur installé ?",
        "label_capacite_frigo": "Capacité frigorifique",
        "label_nom_frigorigenes": "Réfrigérant",
        "label_puissance_comp": "Puissance (HP)",
        "label_variation_vitesse": "VFD (variateur) ?",
        "label_puissance_dep_hp": "Puissance (HP)",
        "label_vfd_dep": "VFD ?",
        "label_marque_dep": "Marque",
        "label_type_pompe": "Type (centrifuge, volumétrique…)",
        "label_puissance_pompe": "Puissance (kW ou HP)",
        "label_rendement_pompe": "Rendement (%)",
        "label_vitesse_variable_pompe": "VFD pompe ?",
        "label_type_ventilation": "Type (naturelle, mécanique…)",
        "label_puissance_ventilation": "Puissance (kWh)",
        "label_nom_machine": "Nom machine",
        "label_puissance_machine": "Puissance (kW)",
        "label_taux_utilisation": "Taux d'utilisation (%)",
        "label_rendement_machine": "Rendement (%)",
        "label_source_energie_machine": "Source d'énergie",
        "label_type_eclairage": "Type (LED, fluorescent…)",
        "label_puissance_totale_eclairage": "Puissance totale (kW)",
        "label_heures_utilisation": "Heures/jour",
        # Section 6
        "titre_prio": "🎯 6. Vos priorités stratégiques",
        "exp_prio": "Indiquer vos priorités",
        "intro_prio": "Notez de 0 (pas important) à 10 (très important).",
        "label_p_ener": "Réduction de la consommation énergétique",
        "help_p_ener": "Économies d'énergie globales pour votre site.",
        "label_p_roi": "Retour sur investissement",
        "help_p_roi": "1 an = retour rapide, 10 ans = retour lent.",
        "label_p_ges": "Réduction des émissions de GES",
        "help_p_ges": "Conformité réglementaire et impact environnemental.",
        "label_p_prod": "Productivité et fiabilité",
        "help_p_prod": "Optimisation des performances et disponibilité.",
        "label_p_maint": "Maintenance et durabilité",
        "help_p_maint": "Facilité d'entretien et durée de vie des équipements.",
        "titre_analyse": "📊 Analyse de vos priorités",
        "warning_prio": "⚠️ Indiquez vos priorités pour générer l'analyse.",
        "r_ener": "Énergie",
        "r_roi": "ROI",
        "r_ges": "GES",
        "r_prod": "Productivité",
        "r_maint": "Maintenance",
        # Section 7
        "titre_services": "🛠️ 7. Services complémentaires",
        "exp_services": "Indiquer les services souhaités",
        "label_controle": "Contrôle et automatisation",
        "label_maintenance": "Maintenance préventive et corrective",
        "label_ventilation": "Ventilation industrielle et gestion de l'air",
        "label_autres_services": "Autres services (précisez)",
        # Section 8
        "titre_pdf": "📝 8. Récapitulatif et génération PDF",
        "info_note": (
            "ℹ️ Vos données sont sauvegardées automatiquement. "
            "Utilisez le lien de reprise dans la barre latérale pour revenir plus tard."
        ),
        "btn_gen": "📥 Générer le PDF",
        "btn_dl": "📥 Télécharger le PDF",
        "err_missing": "Veuillez remplir ou corriger :",
        "ok_pdf": "✅ PDF généré avec succès !",
        "f_client": "Nom du client",
        "f_site": "Nom du site",
        "f_mail": "Courriel EE",
        "obj_titre": "Objectifs du client :",
        "svc_titre": "Services souhaités :",
        "prio_titre": "Priorités stratégiques :",
        "eq_titre": "Équipements identifiés :",
        "aucun_eq": "Aucun équipement saisi",
        "ctrl": "Contrôle & automatisation",
        "maint_lbl": "Maintenance",
        "vent_lbl": "Ventilation",
        "btn_soumettre": "📤 Soumettre le formulaire",
        "err_pdf_manquant": "⚠️ Veuillez d'abord cliquer sur « Générer le PDF ».",
        "ok_envoi": "✅ Formulaire soumis : résumé + PDF + pièces jointes envoyés avec succès.",
        "lbl_excel": "Exporter les données en Excel",
        "btn_excel": "📥 Télécharger Excel",
    },
    "en": {
        "titre_infos": "📄 1. General Information",
        "exp_infos": "Fill in general information",
        "label_client_nom": "Client name *",
        "aide_client_nom": "E.g., Acme Corp",
        "label_site_nom": "Site name *",
        "label_adresse": "Address",
        "label_ville": "City",
        "label_province": "Province",
        "label_code_postal": "Postal code",
        "label_neq": "NEQ (Québec)",
        "help_neq": "10 digits, e.g., 1140007365",
        "titre_contacts": "👥 2. Contact Persons",
        "exp_contacts": "Fill in contacts",
        "sous_titre_ee": "🔌 Energy Efficiency Contact",
        "sous_titre_maint": "🛠️ Maintenance Contact (external)",
        "titre_remplisseur": "👤 Person who filled out this form",
        "sous_titre_sign": "✍️ Authorized signatory",
        "label_nom": "First and Last Name",
        "label_mail": "Email",
        "label_tel": "Phone",
        "label_ext": "Extension",
        "label_date": "Date of completion",
        "help_mail": "Format: example@domain.com",
        "help_tel": "10 digits recommended",
        "titre_docs": "📑 3. Documents to Provide",
        "exp_docs": "Upload documents",
        "label_facture_elec": "Electricity bills (1 to 3 years)",
        "label_facture_comb": "Gas / Fuel Oil / Propane / Wood bills",
        "label_facture_autres": "Other consumables (nitrogen, water, CO2…)",
        "label_plans_pid": "Site layout plans and P&ID",
        "label_temps_fonct": "Plant operating time (hours/year)",
        "fichiers_tele": "📂 Uploaded Files",
        "titre_obj": "🎯 4. Client Objectives",
        "exp_obj": "Fill in objectives",
        "label_ges": "GHG reduction target (%)",
        "help_ges": "Example: 20",
        "label_eco_ener": "Energy savings",
        "label_prod": "Increased productivity (costs, time)",
        "label_roi": "Target return on investment",
        "label_remplacement": "Planned equipment replacement",
        "label_invest": "Planned investment (amount and date)",
        "label_autres_obj": "Other objectives",
        "titre_eq": "⚙️ 5. Equipment List",
        "exp_eq": "Fill in equipment",
        "sous_chaudieres": "🔥 Boilers",
        "sous_frigo": "❄️ Refrigeration Equipment",
        "sous_comp": "💨 Air Compressors",
        "sous_dep": "🧹 Dust Collectors",
        "sous_pompes": "🚰 Industrial Pumps",
        "sous_vent": "🌬️ Ventilation / HVAC",
        "sous_machines": "🛠️ Other Production Machines",
        "sous_ecl": "💡 Lighting Systems",
        "apercu": "Preview:",
        "label_type_chaudiere": "Boiler type",
        "label_rendement_chaudiere": "Efficiency (%)",
        "label_taille_chaudiere": "Size (BHP or BTU)",
        "label_appoint_eau": "Make-up water (volume)",
        "label_micro_modulation": "Micro modulation?",
        "label_economiseur_chaudiere": "Economizer installed?",
        "label_capacite_frigo": "Refrigeration capacity",
        "label_nom_frigorigenes": "Refrigerant",
        "label_puissance_comp": "Power (HP)",
        "label_variation_vitesse": "VFD?",
        "label_puissance_dep_hp": "Power (HP)",
        "label_vfd_dep": "VFD?",
        "label_marque_dep": "Brand",
        "label_type_pompe": "Type (centrifugal, volumetric…)",
        "label_puissance_pompe": "Power (kW or HP)",
        "label_rendement_pompe": "Efficiency (%)",
        "label_vitesse_variable_pompe": "Pump VFD?",
        "label_type_ventilation": "Type (natural, mechanical…)",
        "label_puissance_ventilation": "Power (kWh)",
        "label_nom_machine": "Machine name",
        "label_puissance_machine": "Power (kW)",
        "label_taux_utilisation": "Utilization rate (%)",
        "label_rendement_machine": "Efficiency (%)",
        "label_source_energie_machine": "Energy source",
        "label_type_eclairage": "Type (LED, fluorescent…)",
        "label_puissance_totale_eclairage": "Total installed power (kW)",
        "label_heures_utilisation": "Hours/day",
        "titre_prio": "🎯 6. Your Strategic Priorities",
        "exp_prio": "Indicate your priorities",
        "intro_prio": "Rate from 0 (not important) to 10 (very important).",
        "label_p_ener": "Energy consumption reduction",
        "help_p_ener": "Overall energy savings for your site.",
        "label_p_roi": "Return on investment",
        "help_p_roi": "1 year = fast payback, 10 years = slow payback.",
        "label_p_ges": "GHG emissions reduction",
        "help_p_ges": "Regulatory compliance and environmental impact.",
        "label_p_prod": "Productivity and reliability",
        "help_p_prod": "Performance optimization and equipment availability.",
        "label_p_maint": "Maintenance and durability",
        "help_p_maint": "Ease of maintenance and equipment longevity.",
        "titre_analyse": "📊 Priority Analysis",
        "warning_prio": "⚠️ Please set your priorities to generate the analysis.",
        "r_ener": "Energy",
        "r_roi": "ROI",
        "r_ges": "GHG",
        "r_prod": "Productivity",
        "r_maint": "Maintenance",
        "titre_services": "🛠️ 7. Additional Services",
        "exp_services": "Select desired services",
        "label_controle": "Control and automation",
        "label_maintenance": "Preventive and corrective maintenance",
        "label_ventilation": "Industrial ventilation and air management",
        "label_autres_services": "Other desired services (please specify)",
        "titre_pdf": "📝 8. Summary and PDF Generation",
        "info_note": (
            "ℹ️ Your data is automatically saved. "
            "Use the resume link in the sidebar to come back later."
        ),
        "btn_gen": "📥 Generate PDF",
        "btn_dl": "📥 Download PDF",
        "err_missing": "Please fill or correct:",
        "ok_pdf": "✅ PDF successfully generated!",
        "f_client": "Client Name",
        "f_site": "Site Name",
        "f_mail": "EE Email",
        "obj_titre": "Client objectives:",
        "svc_titre": "Additional desired services:",
        "prio_titre": "Client strategic priorities:",
        "eq_titre": "Equipment identified:",
        "aucun_eq": "No equipment provided",
        "ctrl": "Control & automation",
        "maint_lbl": "Maintenance",
        "vent_lbl": "Ventilation",
        "btn_soumettre": "📤 Submit Form",
        "err_pdf_manquant": "⚠️ Please generate the PDF first.",
        "ok_envoi": "✅ Form submitted: summary + PDF + attachments sent successfully.",
        "lbl_excel": "Export data to Excel",
        "btn_excel": "📥 Download Excel",
    },
}

t = T[lang]

# Mettre à jour les libellés équipements dans session_state
st.session_state["_EQ"] = {k: v for k, v in t.items() if k.startswith("label_")}

# ═══════════════════════════════════════════════
# SECTION 1 — INFORMATIONS GÉNÉRALES
# ═══════════════════════════════════════════════
st.markdown("<div id='infos'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_infos']}</div>", unsafe_allow_html=True)

with st.expander(t["exp_infos"], expanded=False):
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
        st.warning("Format NEQ invalide : exactement 10 chiffres requis.")

# ═══════════════════════════════════════════════
# SECTION 2 — CONTACTS
# ═══════════════════════════════════════════════
st.markdown("<div id='contacts'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_contacts']}</div>", unsafe_allow_html=True)

with st.expander(t["exp_contacts"], expanded=False):
    # Contact EE
    st.markdown(f"**{t['sous_titre_ee']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_nom"], key="contact_ee_nom")
        st.text_input(t["label_mail"], help=t["help_mail"], key="contact_ee_mail")
    with c2:
        st.text_input(t["label_tel"], help=t["help_tel"], key="contact_ee_tel")
        st.text_input(t["label_ext"], key="contact_ee_ext")

    ee_mail = st.session_state.get("contact_ee_mail", "")
    if ee_mail and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", ee_mail.strip()):
        st.warning("Courriel EE : format invalide.")

    st.markdown("---")

    # Contact Maintenance
    st.markdown(f"**{t['sous_titre_maint']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_nom"], key="contact_maint_nom")
        st.text_input(t["label_mail"], key="contact_maint_mail")
    with c2:
        st.text_input(t["label_tel"], key="contact_maint_tel")
        st.text_input(t["label_ext"], key="contact_maint_ext")

    st.markdown("---")

    # Remplisseur
    st.markdown(f"**{t['titre_remplisseur']}**")
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

    # Signataire
    st.markdown(f"**{t['sous_titre_sign']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_nom"], key="sign_nom")
    with c2:
        st.text_input(t["label_mail"], help=t["help_mail"], key="sign_mail")

    sign_mail = st.session_state.get("sign_mail", "")
    if sign_mail and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", sign_mail.strip()):
        st.warning("Courriel signataire : format invalide.")

# ═══════════════════════════════════════════════
# SECTION 3 — DOCUMENTS
# ═══════════════════════════════════════════════
st.markdown("<div id='docs'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_docs']}</div>", unsafe_allow_html=True)

with st.expander(t["exp_docs"], expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        facture_elec = st.file_uploader(t["label_facture_elec"], type="pdf", accept_multiple_files=True, key="fu_elec")
        facture_combustibles = st.file_uploader(t["label_facture_comb"], type="pdf", accept_multiple_files=True, key="fu_comb")
    with c2:
        facture_autres = st.file_uploader(t["label_facture_autres"], type="pdf", accept_multiple_files=True, key="fu_autres")
        plans_pid = st.file_uploader(t["label_plans_pid"], type="pdf", accept_multiple_files=True, key="fu_pid")

    st.text_input(t["label_temps_fonct"], key="temps_fonctionnement")

    # Récapitulatif des fichiers
    all_files = {
        t["label_facture_elec"]: facture_elec or [],
        t["label_facture_comb"]: facture_combustibles or [],
        t["label_facture_autres"]: facture_autres or [],
        t["label_plans_pid"]: plans_pid or [],
    }
    any_file = any(all_files.values())
    if any_file:
        st.markdown(f"**{t['fichiers_tele']}**")
        for label, files in all_files.items():
            if files:
                for f in files:
                    st.markdown(f"- 📄 `{f.name}` ({label})")

# Persist file lists
st.session_state["facture_elec_files"] = facture_elec or []
st.session_state["facture_combustibles_files"] = facture_combustibles or []
st.session_state["facture_autres_files"] = facture_autres or []
st.session_state["plans_pid_files"] = plans_pid or []

# ═══════════════════════════════════════════════
# SECTION 4 — OBJECTIFS
# ═══════════════════════════════════════════════
st.markdown("<div id='objectifs'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_obj']}</div>", unsafe_allow_html=True)

with st.expander(t["exp_obj"], expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t["label_ges"], help=t["help_ges"], key="sauver_ges")
        st.checkbox(t["label_eco_ener"], key="economie_energie")
        st.checkbox(t["label_prod"], key="gain_productivite")
    with c2:
        st.text_input(t["label_roi"], key="roi_vise")
        st.checkbox(t["label_remplacement"], key="remplacement_equipement")
        st.text_input(t["label_invest"], key="investissement_prevu")

    st.text_area(t["label_autres_obj"], key="autres_objectifs")

# ═══════════════════════════════════════════════
# SECTION 5 — ÉQUIPEMENTS
# ═══════════════════════════════════════════════
st.markdown("<div id='equipements'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_eq']}</div>", unsafe_allow_html=True)


def _make_editor(key, columns, column_config=None):
    """Créé un data_editor avec aperçu compact."""
    df = st.data_editor(
        pd.DataFrame(columns=columns),
        num_rows="dynamic",
        key=key,
        column_config=column_config or {},
        use_container_width=True,
    )
    preview = _df_depuis_editor(key)
    if not preview.empty:
        st.caption(t["apercu"])
        st.dataframe(preview, use_container_width=True, hide_index=True)
    return df


with st.expander(t["exp_eq"], expanded=False):
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        t["sous_chaudieres"],
        t["sous_frigo"],
        t["sous_comp"],
        t["sous_dep"],
        t["sous_pompes"],
        t["sous_vent"],
        t["sous_machines"],
        t["sous_ecl"],
    ])

    with tab1:
        _make_editor("chaudieres", [
            "Nom",
            t["label_type_chaudiere"],
            t["label_rendement_chaudiere"],
            t["label_taille_chaudiere"],
            t["label_appoint_eau"],
            t["label_micro_modulation"],
            t["label_economiseur_chaudiere"],
        ])

    with tab2:
        _make_editor("frigo", [
            "Nom",
            t["label_capacite_frigo"],
            t["label_nom_frigorigenes"],
        ])

    with tab3:
        _make_editor("compresseur", [
            "Nom",
            t["label_puissance_comp"],
            t["label_variation_vitesse"],
        ], column_config={
            t["label_variation_vitesse"]: st.column_config.CheckboxColumn(default=False),
        })

    with tab4:
        _make_editor("depoussieur", [
            "Nom",
            t["label_puissance_dep_hp"],
            t["label_vfd_dep"],
            t["label_marque_dep"],
        ], column_config={
            t["label_puissance_dep_hp"]: st.column_config.NumberColumn(step=0.5, min_value=0.0),
            t["label_vfd_dep"]: st.column_config.CheckboxColumn(default=False),
        })

    with tab5:
        _make_editor("pompes", [
            "Nom",
            t["label_type_pompe"],
            t["label_puissance_pompe"],
            t["label_rendement_pompe"],
            t["label_vitesse_variable_pompe"],
        ], column_config={
            t["label_vitesse_variable_pompe"]: st.column_config.CheckboxColumn(default=False),
        })

    with tab6:
        _make_editor("ventilation_eq", [
            "Nom",
            t["label_type_ventilation"],
            t["label_puissance_ventilation"],
        ])

    with tab7:
        _make_editor("machines", [
            "Nom",
            t["label_puissance_machine"],
            t["label_taux_utilisation"],
            t["label_rendement_machine"],
            t["label_source_energie_machine"],
        ])

    with tab8:
        _make_editor("eclairage", [
            "Nom",
            t["label_type_eclairage"],
            t["label_puissance_totale_eclairage"],
            t["label_heures_utilisation"],
        ])

# ═══════════════════════════════════════════════
# SECTION 6 — PRIORITÉS
# ═══════════════════════════════════════════════
st.markdown("<div id='priorites'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_prio']}</div>", unsafe_allow_html=True)

with st.expander(t["exp_prio"], expanded=False):
    st.caption(t["intro_prio"])

    c1, c2 = st.columns(2)
    with c1:
        p_ener = st.slider(t["label_p_ener"], 0, 10, st.session_state.get("priorite_energie", 5), help=t["help_p_ener"], key="priorite_energie")
        p_roi = st.slider(t["label_p_roi"], 1, 10, st.session_state.get("priorite_roi", 5), help=t["help_p_roi"], key="priorite_roi")
        p_ges = st.slider(t["label_p_ges"], 0, 10, st.session_state.get("priorite_ges", 5), help=t["help_p_ges"], key="priorite_ges")
    with c2:
        p_prod = st.slider(t["label_p_prod"], 0, 10, st.session_state.get("priorite_prod", 5), help=t["help_p_prod"], key="priorite_prod")
        p_maint = st.slider(t["label_p_maint"], 0, 10, st.session_state.get("priorite_maintenance", 5), help=t["help_p_maint"], key="priorite_maintenance")

    total = p_ener + p_roi + p_ges + p_prod + p_maint

    if total > 0:
        # Sauvegarder les poids dans session_state
        st.session_state["poids_energie"] = p_ener / total
        st.session_state["poids_roi"] = p_roi / total
        st.session_state["poids_ges"] = p_ges / total
        st.session_state["poids_prod"] = p_prod / total
        st.session_state["poids_maintenance"] = p_maint / total

        st.markdown(f"**{t['titre_analyse']}**")

        labels = [t["r_ener"], t["r_roi"], t["r_ges"], t["r_prod"], t["r_maint"]]
        vals = [
            st.session_state["poids_energie"] * 100,
            st.session_state["poids_roi"] * 100,
            st.session_state["poids_ges"] * 100,
            st.session_state["poids_prod"] * 100,
            st.session_state["poids_maintenance"] * 100,
        ]

        c1, c2 = st.columns([1, 2])
        with c1:
            for lbl, val in zip(labels, vals):
                st.markdown(f"- **{lbl}** : {val:.0f}%")
        with c2:
            fig, ax = plt.subplots(figsize=(4, 2.5))
            colors = [couleur_primaire] * len(labels)
            ax.barh(labels, vals, color=colors, edgecolor="none", height=0.55)
            ax.set_xlabel("%", fontsize=8)
            ax.set_xlim(0, 100)
            ax.tick_params(axis="both", labelsize=8)
            ax.set_facecolor("none")
            fig.patch.set_alpha(0)
            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.warning(t["warning_prio"])

# ═══════════════════════════════════════════════
# SECTION 7 — SERVICES
# ═══════════════════════════════════════════════
st.markdown("<div id='services'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_services']}</div>", unsafe_allow_html=True)

with st.expander(t["exp_services"], expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.checkbox(t["label_controle"], key="controle")
    with c2:
        st.checkbox(t["label_maintenance"], key="maintenance")
    with c3:
        # Clé différente de l'éditeur ventilation_eq pour éviter les conflits
        st.checkbox(t["label_ventilation"], key="ventilation_service")
    st.text_area(t["label_autres_services"], key="autres_services")

# ═══════════════════════════════════════════════
# SECTION 8 — PDF + EXPORT + SOUMISSION
# ═══════════════════════════════════════════════
st.markdown("<div id='pdf'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{t['titre_pdf']}</div>", unsafe_allow_html=True)
st.info(t["info_note"])


# ──────────────────────────────────────────────
# GÉNÉRATION PDF
# ──────────────────────────────────────────────
def generer_pdf(
    *,
    client_nom: str,
    site_nom: str,
    adresse: str,
    ville: str,
    province: str,
    code_postal: str,
    neq_val: str,
    contact_ee_nom: str,
    contact_ee_mail: str,
    contact_ee_tel: str,
    contact_maint_nom: str,
    rempli_nom: str,
    rempli_date_str: str,
    sign_nom: str,
    temps_fonctionnement: str,
    sauver_ges: str,
    economie_energie: bool,
    gain_productivite: bool,
    roi_vise: str,
    investissement_prevu: str,
    autres_objectifs: str,
    priorites: dict,
    equipements: dict,
    controle: bool,
    maintenance: bool,
    ventilation_svc: bool,
    autres_services: str,
    lang_pdf: str = "fr",
) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Polices
    try:
        pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
        FR, FB = "DejaVu", "DejaVu"
    except Exception:
        FR = FB = "Arial"

    BULLET = "-"

    def titre_section(txt):
        pdf.set_fill_color(205, 220, 57)
        pdf.set_font(FB, "B", 11)
        pdf.cell(0, 8, txt, ln=True, fill=True)
        pdf.ln(1)

    def ligne(label, val, indent=0):
        pdf.set_font(FR, "", 10)
        pdf.cell(indent)
        pdf.cell(0, 7, f"{label} : {val or 'N/A'}", ln=True)

    def ligne_bullet(txt):
        pdf.set_font(FR, "", 10)
        pdf.multi_cell(0, 6, f"  {BULLET} {txt}")

    # Logo
    try:
        pdf.image("Image/Logo Soteck.jpg", x=160, y=8, w=35)
    except Exception:
        pass

    # Titre principal
    pdf.set_font(FB, "B", 16)
    pdf.cell(0, 10, "AUDIT FLASH - Résumé", ln=True, align="C")
    pdf.set_font(FR, "", 9)
    pdf.cell(0, 6, f"Généré le {date.today().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(6)

    # 1. Infos générales
    titre_section("1. Informations générales" if lang_pdf == "fr" else "1. General Information")
    ligne("Client", client_nom)
    ligne("Site", site_nom)
    if adresse or ville:
        ligne("Adresse", f"{adresse}, {ville}, {province} {code_postal}".strip(", "))
    if neq_val:
        ligne("NEQ", neq_val)
    if temps_fonctionnement:
        ligne("Heures/an", temps_fonctionnement)
    pdf.ln(2)

    # 2. Contacts
    titre_section("2. Contacts" if lang_pdf == "fr" else "2. Contacts")
    ligne("Contact EE", f"{contact_ee_nom} – {contact_ee_mail} – {contact_ee_tel}")
    ligne("Maintenance (ext.)", contact_maint_nom)
    ligne("Formulaire rempli par", f"{rempli_nom} ({rempli_date_str})")
    ligne("Signataire", sign_nom)
    pdf.ln(2)

    # 3. Objectifs
    titre_section("3. Objectifs" if lang_pdf == "fr" else "3. Objectives")
    ligne("Réduction GES cible", f"{sauver_ges}%")
    ligne("Économie d'énergie", "Oui" if economie_energie else "Non")
    ligne("Productivité accrue", "Oui" if gain_productivite else "Non")
    ligne("ROI visé", roi_vise)
    ligne("Investissement prévu", investissement_prevu)
    if autres_objectifs:
        pdf.set_font(FR, "", 10)
        pdf.multi_cell(0, 7, f"Autres : {autres_objectifs}")
    pdf.ln(2)

    # 4. Services
    titre_section("4. Services complémentaires" if lang_pdf == "fr" else "4. Additional Services")
    ligne("Contrôle & automatisation", "Oui" if controle else "Non")
    ligne("Maintenance", "Oui" if maintenance else "Non")
    ligne("Ventilation", "Oui" if ventilation_svc else "Non")
    if autres_services:
        pdf.set_font(FR, "", 10)
        pdf.multi_cell(0, 7, f"Autres : {autres_services}")
    pdf.ln(2)

    # 5. Priorités
    titre_section("5. Priorités stratégiques" if lang_pdf == "fr" else "5. Strategic Priorities")
    pdf.set_font(FR, "", 10)
    if priorites:
        for k, v in priorites.items():
            try:
                pdf.cell(0, 7, f"  {BULLET} {k} : {float(v):.0%}", ln=True)
            except Exception:
                pdf.cell(0, 7, f"  {BULLET} {k} : {v}", ln=True)
    else:
        pdf.cell(0, 7, "  Non renseignées", ln=True)
    pdf.ln(2)

    # 6. Équipements
    titre_section("6. Équipements identifiés" if lang_pdf == "fr" else "6. Equipment Identified")
    for bloc, items in equipements.items():
        pdf.set_font(FB, "B", 10)
        pdf.cell(0, 7, f"{bloc} :", ln=True)
        pdf.set_font(FR, "", 10)
        if items:
            for it in items:
                pdf.multi_cell(0, 6, f"    {BULLET} {_one_line(str(it))}")
        else:
            pdf.cell(0, 7, f"    ({T[lang_pdf]['aucun_eq']})", ln=True)

    # Pied de page
    try:
        pdf.image("Image/sous-page.jpg", x=10, y=265, w=190)
    except Exception:
        pass

    out = pdf.output(dest="S")
    return out if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")


# ─── Bouton Générer PDF ───
st.divider()
email_regex = r"[^@]+@[^@]+\.[^@]+"

col_gen, col_dl = st.columns([1, 1])

with col_gen:
    if st.button(t["btn_gen"], use_container_width=True):
        missing = []
        cn = st.session_state.get("client_nom", "").strip()
        sn = st.session_state.get("site_nom", "").strip()
        em = st.session_state.get("contact_ee_mail", "").strip()

        if not cn:
            missing.append(t["f_client"])
        if not sn:
            missing.append(t["f_site"])
        if em and not re.match(email_regex, em):
            missing.append(t["f_mail"])

        if missing:
            st.error(f"{t['err_missing']} {', '.join(missing)}")
        else:
            poids_energie = float(st.session_state.get("poids_energie", 0))
            poids_roi = float(st.session_state.get("poids_roi", 0))
            poids_ges = float(st.session_state.get("poids_ges", 0))
            poids_prod = float(st.session_state.get("poids_prod", 0))
            poids_maint = float(st.session_state.get("poids_maintenance", 0))

            priorites = {}
            if (poids_energie + poids_roi + poids_ges + poids_prod + poids_maint) > 0:
                priorites = {
                    t["r_ener"]: poids_energie,
                    t["r_roi"]: poids_roi,
                    t["r_ges"]: poids_ges,
                    t["r_prod"]: poids_prod,
                    t["r_maint"]: poids_maint,
                }

            equipements = {
                t["sous_chaudieres"].replace("🔥 ", ""): _safe_details(_chaudieres_detaille),
                t["sous_frigo"].replace("❄️ ", ""): _safe_details(_frigo_detaille),
                t["sous_comp"].replace("💨 ", ""): _safe_details(_compresseurs_detaille),
                t["sous_dep"].replace("🧹 ", ""): _safe_details(_depoussieurs_detaille),
                t["sous_pompes"].replace("🚰 ", ""): _safe_details(_pompes_detaille),
                t["sous_vent"].replace("🌬️ ", ""): _safe_details(_ventilation_detaille),
                t["sous_machines"].replace("🛠️ ", ""): _safe_details(_machines_detaille),
                t["sous_ecl"].replace("💡 ", ""): _safe_details(_eclairage_detaille),
            }

            pdf_bytes = generer_pdf(
                client_nom=cn,
                site_nom=sn,
                adresse=st.session_state.get("adresse", ""),
                ville=st.session_state.get("ville", ""),
                province=st.session_state.get("province", ""),
                code_postal=st.session_state.get("code_postal", ""),
                neq_val=st.session_state.get("neq_clean", ""),
                contact_ee_nom=st.session_state.get("contact_ee_nom", ""),
                contact_ee_mail=st.session_state.get("contact_ee_mail", ""),
                contact_ee_tel=st.session_state.get("contact_ee_tel", ""),
                contact_maint_nom=st.session_state.get("contact_maint_nom", ""),
                rempli_nom=st.session_state.get("rempli_nom", ""),
                rempli_date_str=str(st.session_state.get("rempli_date", date.today())),
                sign_nom=st.session_state.get("sign_nom", ""),
                temps_fonctionnement=st.session_state.get("temps_fonctionnement", ""),
                sauver_ges=str(st.session_state.get("sauver_ges", "")),
                economie_energie=bool(st.session_state.get("economie_energie", False)),
                gain_productivite=bool(st.session_state.get("gain_productivite", False)),
                roi_vise=str(st.session_state.get("roi_vise", "")),
                investissement_prevu=str(st.session_state.get("investissement_prevu", "")),
                autres_objectifs=str(st.session_state.get("autres_objectifs", "")),
                priorites=priorites,
                equipements=equipements,
                controle=bool(st.session_state.get("controle", False)),
                maintenance=bool(st.session_state.get("maintenance", False)),
                ventilation_svc=bool(st.session_state.get("ventilation_service", False)),
                autres_services=str(st.session_state.get("autres_services", "")),
                lang_pdf=lang,
            )
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["pdf_client"] = cn
            st.session_state["pdf_site"] = sn
            st.success(t["ok_pdf"])

with col_dl:
    if "pdf_bytes" in st.session_state:
        cn = st.session_state.get("pdf_client", "client")
        sn = st.session_state.get("pdf_site", "site")
        st.download_button(
            label=t["btn_dl"],
            data=st.session_state["pdf_bytes"],
            file_name=f"audit_flash_{_slug(sn)}_{_slug(cn)}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ─── Export Excel ───
st.divider()
if st.checkbox(t["lbl_excel"]):
    cn = st.session_state.get("client_nom", "N/A")
    sn = st.session_state.get("site_nom", "N/A")
    ges = st.session_state.get("sauver_ges", "N/A")
    roi = st.session_state.get("roi_vise", "N/A")

    p_e = float(st.session_state.get("poids_energie", 0))
    p_r = float(st.session_state.get("poids_roi", 0))
    p_g = float(st.session_state.get("poids_ges", 0))
    p_p = float(st.session_state.get("poids_prod", 0))
    p_m = float(st.session_state.get("poids_maintenance", 0))

    data_excel = {
        "Client": [cn],
        "Site": [sn],
        "GES (%)": [ges],
        "ROI visé": [roi],
        "Contrôle": ["Oui" if st.session_state.get("controle") else "Non"],
        "Maintenance": ["Oui" if st.session_state.get("maintenance") else "Non"],
        "Ventilation": ["Oui" if st.session_state.get("ventilation_service") else "Non"],
        "Poids Énergie": [f"{p_e:.0%}"],
        "Poids ROI": [f"{p_r:.0%}"],
        "Poids GES": [f"{p_g:.0%}"],
        "Poids Productivité": [f"{p_p:.0%}"],
        "Poids Maintenance": [f"{p_m:.0%}"],
    }
    df_export = pd.DataFrame(data_excel)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Audit Flash")
    excel_buffer.seek(0)
    st.download_button(
        label=t["btn_excel"],
        data=excel_buffer,
        file_name=f"audit_flash_{_slug(st.session_state.get('site_nom','site'))}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ─── Soumission par e-mail ───
st.divider()
if st.button(t["btn_soumettre"], use_container_width=True):
    pdf_bytes = st.session_state.get("pdf_bytes")
    if not pdf_bytes:
        st.error(t["err_pdf_manquant"])
    else:
        # Récupérer toutes les variables depuis session_state
        cn = st.session_state.get("client_nom", "")
        sn = st.session_state.get("site_nom", "")
        adresse_v = st.session_state.get("adresse", "")
        ville_v = st.session_state.get("ville", "")
        province_v = st.session_state.get("province", "")
        code_postal_v = st.session_state.get("code_postal", "")
        contact_ee_nom_v = st.session_state.get("contact_ee_nom", "")
        contact_ee_mail_v = st.session_state.get("contact_ee_mail", "")
        contact_ee_tel_v = st.session_state.get("contact_ee_tel", "")
        contact_ee_ext_v = st.session_state.get("contact_ee_ext", "")
        contact_maint_nom_v = st.session_state.get("contact_maint_nom", "")
        contact_maint_mail_v = st.session_state.get("contact_maint_mail", "")
        contact_maint_tel_v = st.session_state.get("contact_maint_tel", "")
        rempli_nom_v = st.session_state.get("rempli_nom", "")
        rempli_mail_v = st.session_state.get("rempli_mail", "")
        rempli_tel_v = st.session_state.get("rempli_tel", "")
        rempli_date_v = str(st.session_state.get("rempli_date", ""))
        sign_nom_v = st.session_state.get("sign_nom", "")
        sauver_ges_v = st.session_state.get("sauver_ges", "")
        roi_vise_v = st.session_state.get("roi_vise", "")
        investissement_prevu_v = st.session_state.get("investissement_prevu", "")
        autres_objectifs_v = st.session_state.get("autres_objectifs", "")
        economie_energie_v = st.session_state.get("economie_energie", False)
        gain_productivite_v = st.session_state.get("gain_productivite", False)
        controle_v = st.session_state.get("controle", False)
        maintenance_v = st.session_state.get("maintenance", False)
        ventilation_svc_v = st.session_state.get("ventilation_service", False)

        facture_elec = st.session_state.get("facture_elec_files", [])
        facture_combustibles = st.session_state.get("facture_combustibles_files", [])
        facture_autres_f = st.session_state.get("facture_autres_files", [])
        plans_pid_f = st.session_state.get("plans_pid_files", [])

        def _names(lst):
            return ", ".join([f.name for f in (lst or [])]) or "—"

        resume_lignes = [
            "Bonjour,\n",
            "Ci-joint le résumé de l'Audit Flash (PDF) ainsi que les documents fournis.\n",
            "——— INFORMATIONS GÉNÉRALES ———",
            f"- Client  : {cn or 'N/A'}",
            f"- Site    : {sn or 'N/A'}",
            f"- Adresse : {adresse_v}, {ville_v}, {province_v} {code_postal_v}".rstrip(),
            "",
            "——— CONTACTS ———",
            f"- EE      : {contact_ee_nom_v} – {contact_ee_mail_v} – {contact_ee_tel_v} ext {contact_ee_ext_v}".rstrip(),
            f"- Maint.  : {contact_maint_nom_v} – {contact_maint_mail_v} – {contact_maint_tel_v}",
            f"- Rempli  : {rempli_nom_v} – {rempli_mail_v} – {rempli_tel_v} (le {rempli_date_v})",
            f"- Signat. : {sign_nom_v}",
            "",
            "——— OBJECTIFS ———",
            f"- Cible GES          : {sauver_ges_v}%",
            f"- Économie énergie   : {'Oui' if economie_energie_v else 'Non'}",
            f"- Productivité accrue: {'Oui' if gain_productivite_v else 'Non'}",
            f"- ROI visé           : {roi_vise_v or 'N/A'}",
            f"- Investissement     : {investissement_prevu_v or 'N/A'}",
            f"- Autres objectifs   : {autres_objectifs_v or '—'}",
            "",
            "——— ÉQUIPEMENTS ———",
        ]

        for titre_eq, fn in [
            ("Chaudières", _chaudieres_detaille),
            ("Systèmes frigorifiques", _frigo_detaille),
            ("Compresseurs", _compresseurs_detaille),
            ("Dépoussiéreurs", _depoussieurs_detaille),
            ("Pompes", _pompes_detaille),
            ("Ventilation", _ventilation_detaille),
            ("Machines", _machines_detaille),
            ("Éclairage", _eclairage_detaille),
        ]:
            L = _safe_details(fn)
            if L:
                resume_lignes.append(f"- {titre_eq} :")
                for s in L:
                    resume_lignes.append(f"    • {s}")
            else:
                resume_lignes.append(f"- {titre_eq} : —")

        resume_lignes += [
            "",
            "——— PIÈCES JOINTES ———",
            f"- Factures élec.     : {_names(facture_elec)}",
            f"- Factures combust.  : {_names(facture_combustibles)}",
            f"- Autres consommab.  : {_names(facture_autres_f)}",
            f"- Plans & P&ID       : {_names(plans_pid_f)}",
            "",
            "Cordialement,",
            "Soteck",
        ]
        resume = "\n".join(resume_lignes)
        pdf_filename = f"Resume_AuditFlash_{_slug(sn or 'site')}_{_slug(cn or 'client')}.pdf"

        try:
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            EMAIL_SENDER = "elmehdi.bencharif@gmail.com"
            EMAIL_PASSWORD = str(st.secrets["email_password"]).strip()
            EMAIL_DESTINATAIRES = ["mbencharif@soteck.com", "pdelorme@soteck.com"]

            subject_label = "Audit Flash" if lang == "fr" else "Flash Audit"
            msg_subject = f"{subject_label} – {_one_line(sn or 'N/A')} – {_one_line(cn or 'N/A')}"

            msg = EmailMessage()
            msg["Subject"] = msg_subject
            msg["From"] = EMAIL_SENDER
            msg.set_content(resume)
            msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=pdf_filename)

            def _attach_files(group):
                for file in group or []:
                    try:
                        blob = file.getvalue()
                        msg.add_attachment(blob, maintype="application", subtype="octet-stream", filename=file.name)
                    except Exception as e:
                        st.warning(f"⚠️ Fichier {getattr(file,'name','?')} non attaché : {e}")

            _attach_files(facture_elec)
            _attach_files(facture_combustibles)
            _attach_files(facture_autres_f)
            _attach_files(plans_pid_f)

            def _is_mail(x):
                return isinstance(x, str) and re.match(r"[^@]+@[^@]+\.[^@]+", x.strip())

            cc_list = []
            for addr in [rempli_mail_v, contact_ee_mail_v]:
                if _is_mail(addr) and addr not in EMAIL_DESTINATAIRES and addr not in cc_list:
                    cc_list.append(addr)

            msg["To"] = ", ".join(EMAIL_DESTINATAIRES)
            if cc_list:
                msg["Cc"] = ", ".join(cc_list)
            if _is_mail(rempli_mail_v):
                msg["Reply-To"] = rempli_mail_v

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)

            st.success(t["ok_envoi"])

        except smtplib.SMTPAuthenticationError as e:
            st.error(f"⛔ Auth SMTP refusée ({e.smtp_code}) : {e.smtp_error}.")
        except Exception as e:
            st.error(f"⛔ Erreur envoi e-mail : {e}")

# ─────────────────────────────────────────────
# AUTOSAVE
# ─────────────────────────────────────────────
autosave_if_changed(form_id)
