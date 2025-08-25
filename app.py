import streamlit as st
import os

st.set_page_config(page_title="Prosthetics & Orthotics AI Assistant", page_icon="🦿")

st.title("Prosthetics & Orthotics AI Assistant 🦿")
st.write("Welcome! This is a prototype AI assistant for prosthetics and orthotics support.")

# Password protection
password_input = st.text_input("Enter admin password:", type="password")
correct_password = os.getenv("MORBIS", "changeme")

if password_input == correct_password:
    st.success("Access granted ✅")
    st.write("Here’s your admin dashboard.")
else:
    st.warning("Wrong password ❌")