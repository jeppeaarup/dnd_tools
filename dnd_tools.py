# main.py
import streamlit as st

st.set_page_config(
    page_title="DnD 2024 tools",
    page_icon="⚔️"
)

attack_page = st.Page("pages/weapon_calc.py", title="Attack calculator", icon="⚔️")
ability_page = st.Page("pages/ability_calc.py", title="Ability score calculator", icon="📖")

pg = st.navigation([ability_page, attack_page])
pg.run()

with st.sidebar:
    st.caption("Based on the D&D 5e 2024 revision (SRD).")

with st.bottom:
    col1, col2 = st.columns([3, 1])
    col1.caption("Built by Jeppe Aarup Andersen · v0.1 - feedback welcome")
    col2.caption("[GitHub](https://github.com/jeppeaarup/dnd-tools)")