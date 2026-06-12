"""
Regulatory Document Manager — Streamlit Frontend
"""
import streamlit as st
import requests
import os
from datetime import datetime

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RegDoc Manager",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* tone: clinical-clean, steel-blue accent */
    :root {
        --accent: #1B6CA8;
        --accent-light: #E8F1FA;
        --border: #D5DDE8;
        --muted: #6B7A8D;
        --tag-bg: #DFF0FF;
        --tag-fg: #0D4F80;
    }
.stApp { background: #F6F8FB; color: #000; }
    [data-testid="stSidebar"] { background: #1A2535 !important; }
    [data-testid="stSidebar"] * { color: #CDD8E8 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: #243348;
        color: #CBD8E8 !important;
        border: 1px solid #2E4260;
        border-radius: 6px;
    }
    label, .stTextInput label, .stFileUploader label {
        color: #000 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover { background: #1B6CA8; }

    div.doc-card {
        background: #fff;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,.04);
        transition: box-shadow .15s;
    }
    div.doc-card:hover { box-shadow: 0 3px 12px rgba(27,108,168,.12); }
    .doc-title { font-size: 1rem; font-weight: 600; color: #1A2535; margin-bottom: 4px; }
    .doc-meta  { font-size: .78rem; color: var(--muted); margin-bottom: 8px; }
    .tag-chip  {
        display: inline-block;
        background: var(--tag-bg);
        color: var(--tag-fg);
        font-size: .72rem;
        font-weight: 600;
        border-radius: 12px;
        padding: 2px 9px;
        margin: 2px 3px 2px 0;
        letter-spacing: .03em;
        text-transform: uppercase;
    }
    div.detail-box {
        background: #fff;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 24px 28px;
        font-family: 'Georgia', serif;
        font-size: .9rem;
        line-height: 1.7;
        max-height: 520px;
        overflow-y: auto;
        white-space: pre-wrap;
        color: #000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── api helpers ───────────────────────────────────────────────────────────────

def api(method, path, **kwargs):
    try:
        r = getattr(requests, method)(f"{API_BASE}{path}", timeout=30, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot reach the API server. Is the backend running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
        return None


def tag_chips(tags):
    if not tags:
        return "<span style='color:#aaa;font-size:.78rem'>no tags</span>"
    return "".join(f'<span class="tag-chip">{t["name"]}</span>' for t in tags)


def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %Y")
    except Exception:
        return iso


# ── sidebar / nav ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 RegDoc Manager")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📄 Document Library", "🔍 Search", "⬆️ Upload PDF"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # tag filter (only on library page)
    all_tags_resp = api("get", "/documents/tags/all") or []
    tag_names = [t["name"] for t in all_tags_resp]
    selected_tag = None
    if "Library" in page and tag_names:
        st.markdown("**Filter by tag**")
        selected_tag = st.selectbox("Tag", ["(all)"] + tag_names, label_visibility="collapsed")
        if selected_tag == "(all)":
            selected_tag = None

# ── session state ────────────────────────────────────────────────────────────
if "open_doc_id" not in st.session_state:
    st.session_state.open_doc_id = None

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: LIBRARY
# ═════════════════════════════════════════════════════════════════════════════
if "Library" in page:
    st.markdown("### Document Library")

    col_pg, col_size = st.columns([3, 1])
    with col_pg:
        pg = st.number_input("Page", min_value=1, value=1, step=1, label_visibility="collapsed")
    with col_size:
        sz = st.selectbox("Per page", [10, 20, 50], index=1, label_visibility="collapsed")

    params = {"page": pg, "page_size": sz}
    if selected_tag:
        params["tag"] = selected_tag

    with st.spinner("Loading documents…"):
        resp = api("get", "/documents", params=params)

    if resp is None:
        st.stop()

    total = resp["total"]
    items = resp["items"]

    st.caption(f"{total} document{'s' if total != 1 else ''} found" +
               (f" tagged **{selected_tag}**" if selected_tag else ""))

    if not items:
        st.info("No documents yet. Upload some PDFs to get started.")
    else:
        for doc in items:
            with st.container():
                st.markdown(
                    f"""<div class="doc-card">
                        <div class="doc-title">{doc['title']}</div>
                        <div class="doc-meta">📄 {doc['filename']} &nbsp;·&nbsp; 
                             🗓 {fmt_date(doc['upload_date'])} &nbsp;·&nbsp; 
                             {doc['page_count']} pages</div>
                        <div>{tag_chips(doc['tags'])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                if st.button("Open →", key=f"open_{doc['id']}"):
                    st.session_state.open_doc_id = doc["id"]
                    st.rerun()

    # pagination hint
    max_pages = max(1, -(-total // sz))
    st.caption(f"Page {pg} of {max_pages}")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ═════════════════════════════════════════════════════════════════════════════
elif "Search" in page:
    st.markdown("### Keyword Search")
    st.caption("Searches across document titles and full extracted text.")

    query = st.text_input("Search query", placeholder="e.g. pharmacokinetics, risk management…")

    if query:
        with st.spinner("Searching…"):
            resp = api("get", "/documents/search", params={"q": query, "page_size": 50})

        if resp:
            items = resp["items"]
            st.caption(f"{resp['total']} result{'s' if resp['total'] != 1 else ''} for **{query}**")
            if not items:
                st.info("No documents matched that query.")
            for doc in items:
                st.markdown(
                    f"""<div class="doc-card">
                        <div class="doc-title">{doc['title']}</div>
                        <div class="doc-meta">📄 {doc['filename']} &nbsp;·&nbsp; 
                             🗓 {fmt_date(doc['upload_date'])} &nbsp;·&nbsp; 
                             {doc['page_count']} pages</div>
                        <div>{tag_chips(doc['tags'])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                if st.button("Open →", key=f"srch_{doc['id']}"):
                    st.session_state.open_doc_id = doc["id"]
                    st.rerun()
    else:
        st.info("Enter a keyword above to search the document library.")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD
# ═════════════════════════════════════════════════════════════════════════════
elif "Upload" in page:
    st.markdown("### Upload a Regulatory PDF")

    with st.form("upload_form", clear_on_submit=True):
        uploaded = st.file_uploader("Choose a PDF", type=["pdf"])
        title_input = st.text_input("Title (optional — defaults to filename)")
        tags_input = st.text_input("Tags (comma-separated, optional)", placeholder="fda, guidance, labeling")
        submitted = st.form_submit_button("Upload")

    if submitted:
        if not uploaded:
            st.warning("Please select a PDF file.")
        else:
            with st.spinner("Uploading and extracting text…"):
                r = api(
                    "post",
                    "/documents/upload",
                    files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                    data={"title": title_input, "tags": tags_input},
                )
            if r:
                st.success(f"✅ **{r['title']}** uploaded successfully ({r['page_count']} pages extracted).")


# ═════════════════════════════════════════════════════════════════════════════
# DETAIL DRAWER (modal-style overlay via rerun flag)
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.open_doc_id:
    doc_id = st.session_state.open_doc_id
    doc = api("get", f"/documents/{doc_id}")

    if doc:
        st.markdown("---")
        hcol1, hcol2 = st.columns([6, 1])
        with hcol1:
            st.markdown(f"## {doc['title']}")
        with hcol2:
            if st.button("✕ Close", key="close_detail"):
                st.session_state.open_doc_id = None
                st.rerun()

        meta_cols = st.columns(3)
        meta_cols[0].metric("Pages", doc["page_count"])
        meta_cols[1].metric("Uploaded", fmt_date(doc["upload_date"]))
        meta_cols[2].metric("Filename", doc["filename"])

        # ── tag management ────────────────────────────────────────────────
        st.markdown("#### Tags")
        tag_col, add_col = st.columns([3, 1])

        with tag_col:
            st.markdown(tag_chips(doc["tags"]), unsafe_allow_html=True)

        # remove tags
        if doc["tags"]:
            remove_tag = st.selectbox(
                "Remove a tag",
                ["— pick to remove —"] + [t["name"] for t in doc["tags"]],
                key="remove_tag_sel",
            )
            if remove_tag != "— pick to remove —":
                if st.button(f"Remove '{remove_tag}'", key="do_remove"):
                    api("delete", f"/documents/{doc_id}/tags/{remove_tag}")
                    st.rerun()

        # add tag
        with st.form("add_tag_form"):
            new_tag = st.text_input("Add a tag", placeholder="e.g. oncology")
            if st.form_submit_button("Add tag") and new_tag.strip():
                api("post", f"/documents/{doc_id}/tags", json={"tag": new_tag.strip()})
                st.rerun()

        # ── full text ─────────────────────────────────────────────────────
        st.markdown("#### Extracted Text")
        if doc.get("full_text", "").strip():
            st.markdown(
                f'<div class="detail-box">{doc["full_text"][:20_000]}</div>',
                unsafe_allow_html=True,
            )
            if len(doc["full_text"]) > 20_000:
                st.caption("(Showing first 20 000 characters — full text stored in the database.)")
        else:
            st.warning("No text could be extracted from this PDF (may be a scanned image).")
