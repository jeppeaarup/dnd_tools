# main.py
import streamlit as st

attack_page = st.Page("pages/weapon_calc.py", title="Attack calculator", icon="⚔️")
ability_page = st.Page("pages/ability_calc.py", title="Ability score calculator", icon="📖")

pg = st.navigation([ability_page, attack_page])
pg.run()