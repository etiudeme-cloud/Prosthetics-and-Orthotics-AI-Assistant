import os
import sqlite3
from contextlib import closing
from datetime import datetime

import pandas as pd
import streamlit as st

DB_PATH = "leads.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            interest TEXT,
            created_at TEXT NOT NULL
        )
    """)
    return conn

def insert_lead(conn, name, email, phone, interest):
    with closing(conn.cursor()) as cur:
        cur.execute(
            "INSERT INTO leads (name, email, phone, interest, created_at) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), phone.strip(), interest.strip(), datetime.utcnow().isoformat())
        )
        conn.commit()

def get_leads_df(conn, interest_filter=None):
    q = "SELECT id, name, email, phone, interest, created_at FROM leads ORDER BY id DESC"
    df = pd.read_sql_query(q, conn)
    if interest_filter and interest_filter != "All":
        df = df[df["interest"] == interest_filter]
    return df

st.set_page_config(page_title="Prosthetics & Orthotics AI Assistant — Waitlist", page_icon="🦾", layout="centered")

st.title("Prosthetics & Orthotics AI Assistant 🦾")
st.subheader("Join the waitlist")
st.write("Sign up to be among the first to try our AI-powered prosthetics & orthotics assistant.")

conn = get_conn()

with st.form("waitlist_form", clear_on_submit=True):
    name = st.text_input("Full name")
    email = st.text_input("Email")
    phone = st.text_input("Phone (optional)")
    interest = st.selectbox("What best describes your interest?", ["General", "Investor", "Partner", "Pilot customer"])
    submitted = st.form_submit_button("Join the waitlist")

if submitted:
    if not name or not email or "@" not in email:
        st.error("Please enter a valid name and email.")
    else:
        try:
            insert_lead(conn, name, email, phone, interest)
            st.success("You're on the waitlist! We'll be in touch.")
        except sqlite3.IntegrityError:
            st.info("You're already on the list. Thanks for your interest!")

st.divider()
st.caption("For admin access, open the sidebar.")

with st.sidebar:
    st.header("Admin")
    if "authed" not in st.session_state:
        st.session_state.authed = False

    if not st.session_state.authed:
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.authed = True
                st.success("Logged in")
            else:
                st.error("Wrong password")
    else:
        if st.button("Logout"):
            st.session_state.authed = False
            st.experimental_rerun()

if st.session_state.authed:
    st.subheader("Leads")
    interest_filter = st.selectbox("Filter by interest", ["All", "General", "Investor", "Partner", "Pilot customer"])
    df = get_leads_df(conn, interest_filter)
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="leads.csv", mime="text/csv")

    st.caption("Tip: set an environment variable ADMIN_PASSWORD to secure this.")
else:
    st.info("Admin view locked. Use the sidebar to log in.")
