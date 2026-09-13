import streamlit as st
import pandas as pd

# Constants
WEAPON_CLASSES = {
    "Simple Melee": ("Simple", "Melee"),
    "Martial Melee": ("Martial", "Melee"),
    "Simple Ranged": ("Simple", "Ranged"),
    "Martial Ranged": ("Martial", "Ranged"),
}

ALL_PROPERTIES = [
    "Light", "Finesse", "Thrown", "Two-Handed",
    "Versatile", "Loading", "Ammunition", "Heavy", "Reach"
    ]

ALL_CATEGORIES = ["Simple", "Martial"]
ALL_TYPES = ["Melee", "Ranged"]


# Import weapons table
weapons_table = pd.read_csv("tables/weapons_table.csv")


# Helper functions
def filter_weapon_table(table, weapon_classes, weapon_properties):

    if not weapon_classes and not weapon_properties:
        return table.iloc[0:0]  # no filters set, show nothing

    # Weapon class: OR across selected combos, each combo is Category+Type together
    if weapon_classes:
        class_mask = pd.Series(False, index=table.index)
        for class_name in weapon_classes:
            category, weapon_type = WEAPON_CLASSES[class_name]
            class_mask |= (table["Category"] == category) & (table["Type"] == weapon_type)
    else:
        class_mask = pd.Series(True, index=table.index)

    # Properties: OR within themselves
    if weapon_properties:
        property_mask = table["Property_list"].apply(
            lambda props: any(p in str(props) for p in weapon_properties)
        )
    else:
        property_mask = pd.Series(True, index=table.index)

    mask = class_mask & property_mask

    return table[mask]

def compute_attack_stats(dex_mod, strength_mod, prof_bonus, property_list, weapon_type):

    has_finesse = "Finesse" in str(property_list)

    if has_finesse:
        if dex_mod <= strength_mod:
            ability_mod = strength_mod
            ability_used = "Strength"
        else:
            ability_mod = dex_mod
            ability_used = "Dexterity"
    elif weapon_type == "Ranged":
        ability_mod = dex_mod
        ability_used = "Dexterity"
    else:
        ability_mod = strength_mod
        ability_used = "Strength"

    attack_bonus = ability_mod
    attack_bonus_proficiency = attack_bonus + prof_bonus
    damage_bonus = ability_mod

    return attack_bonus, attack_bonus_proficiency, damage_bonus, ability_used

def compute_attack_table(dex_mod, strength_mod, prof_bonus, selected_weapons):

    results = []

    for _, row in selected_weapons.iterrows():
        attack_bonus, attack_bonus_prof, damage_bonus, ability_used = compute_attack_stats(
            dex_mod, strength_mod, prof_bonus, row["Property_list"], row["Type"]
        )

        results.append({
            "Weapon": row["Weapon"],
            "Attack bonus": f"{attack_bonus:+d}",
            "Attack bonus, proficient": f"{attack_bonus_prof:+d}",
            "Damage": row["Damage"],
            "Damage bonus": f"{damage_bonus:+d}",
            "Ability used": ability_used,
        })

    return pd.DataFrame(results)


# Page title
st.title("Attack Calculator")

# Character stats in the sidebar
with st.sidebar:
    st.header("Character")
    dex_mod = st.number_input(
        "Dexterity modifier",
        min_value=-5, max_value=10,
        value=0
        )

    strength_mod = st.number_input(
        "Strength modifier",
        min_value=-5, max_value=10,
        value=0
        )

    prof_bonus = st.number_input(
        "Proficiency bonus",
        min_value=2, max_value=9,
        value=2
        )

# Filters
st.subheader("Filter weapons")
weapon_classes = st.pills("Weapon class", list(WEAPON_CLASSES.keys()), selection_mode="multi")
weapon_properties = st.pills("Properties", ALL_PROPERTIES, selection_mode="multi")

# Filter table
filtered_table = filter_weapon_table(weapons_table, weapon_classes, weapon_properties)

st.divider()

# Weapon browser
st.subheader("Choose a weapon")

if not weapon_classes and not weapon_properties:
    st.info("Choose a weapon class or property to browse weapons.")
    selected_weapons = pd.DataFrame()
elif filtered_table.empty:
    st.warning("No weapons match these filters.")
    selected_weapons = pd.DataFrame()
else:
    event = st.dataframe(
        filtered_table,
        hide_index=True,
        on_select="rerun",
        column_order=["Weapon", "Damage", "Properties", "Mastery", "Weight", "Cost"],
        width="stretch",
        row_height=40
    )

    if event.selection.rows:
        selected_weapons = filtered_table.iloc[event.selection.rows]
    else:
        selected_weapons = pd.DataFrame()

st.divider()

# Attack and damage results
st.subheader("Attack & damage")

if selected_weapons.empty and (weapon_classes or weapon_properties):
    st.info("Click a row above to select a weapon.")

if not selected_weapons.empty:
    results_table = compute_attack_table(dex_mod, strength_mod, prof_bonus, selected_weapons)
    st.dataframe(results_table, hide_index=True, width="stretch")