# ability_calc.py
import streamlit as st
import pandas as pd

# Constants
SCORE_BUY_MIN = 8
SCORE_BUY_MAX = 15
POINT_BUY_MAX = 27
ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

BACKGROUND_ABILITIES = {
    "Acolyte": ["Intelligence", "Wisdom", "Charisma"],
    "Artisan": ["Strength", "Dexterity", "Intelligence"],
    "Charlatan": ["Dexterity", "Constitution", "Charisma"],
    "Criminal": ["Dexterity", "Constitution", "Intelligence"],
    "Entertainer": ["Strength", "Dexterity", "Charisma"],
    "Farmer": ["Strength", "Constitution", "Wisdom"],
    "Guard": ["Strength", "Intelligence", "Wisdom"],
    "Guide": ["Dexterity", "Constitution", "Wisdom"],
    "Hermit": ["Constitution", "Wisdom", "Charisma"],
    "Merchant": ["Constitution", "Intelligence", "Charisma"],
    "Noble": ["Strength", "Intelligence", "Charisma"],
    "Sage": ["Constitution", "Intelligence", "Wisdom"],
    "Sailor": ["Strength", "Dexterity", "Wisdom"],
    "Scribe": ["Dexterity", "Intelligence", "Wisdom"],
    "Soldier": ["Strength", "Dexterity", "Constitution"],
    "Wayfarer": ["Dexterity", "Wisdom", "Charisma"],
}

# Helper functions
def score_cost_function(score):
    return score - 8 + max(score - 13, 0)

def ability_modifier(score):
    return (score - 10) // 2

def buy_score_table():

    scores = {}

    header_cols = st.columns([3, 2, 2, 2], vertical_alignment="center")
    header_cols[0].write("**Ability**")
    header_cols[1].write("**Score**")
    header_cols[2].markdown("<div style='text-align: center'><b>Modifier</b></div>", unsafe_allow_html=True)
    header_cols[3].markdown("<div style='text-align: center'><b>Cost</b></div>", unsafe_allow_html=True)

    for ability in ABILITIES:
        cols = st.columns([3, 2, 2, 2], vertical_alignment="center")
        cols[0].write(ability)
        score = cols[1].number_input(
            "Score", min_value=SCORE_BUY_MIN, max_value=SCORE_BUY_MAX, value=8,
            key=f"score_{ability}", label_visibility="collapsed"
        )
        scores[ability] = score
        cols[2].markdown(f"<div style='text-align: center'>{ability_modifier(score):+d}</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div style='text-align: center'>{score_cost_function(score)}</div>", unsafe_allow_html=True)

    total_cost = sum(score_cost_function(s) for s in scores.values())
    remaining = POINT_BUY_MAX - total_cost
    return scores, total_cost, remaining

# Inputs 
st.title("Point buy calculator")

st.subheader("Step 1: Point buy")

st.markdown("You have 27 points to spend on your ability scores. The scores are capped in the interval 8 to 15.")

scores, total_cost, remaining = buy_score_table()

over_budget = total_cost > POINT_BUY_MAX

if over_budget:
    st.error(f"Total cost: {total_cost} / {POINT_BUY_MAX} - over budget by {total_cost - POINT_BUY_MAX} points")
else:
    st.success(f"Total cost: {total_cost} / {POINT_BUY_MAX} - {remaining} points remaining")

st.session_state["ability_scores"] = scores

# --- Background bonus ---
st.divider()
st.subheader("Step 2: Adjust ability scores")
st.markdown("After assigning your ability scores, adjust them according to your background. Your background lists three abilities; increase one of those scores by 2 and a different one by 1, or increase all three by 1")

if over_budget:
    st.warning("Fix your point buy total before choosing a background.")
else:
    background = st.selectbox("Choose a background", list(BACKGROUND_ABILITIES.keys()))
    bg_abilities = BACKGROUND_ABILITIES[background]

    bonus_style = st.segmented_control(
        "Bonus distribution",
        ["+2 / +1", "+1 / +1 / +1"],
        required=True,
        default="+2 / +1"
    )

    bonuses = {a: 0 for a in bg_abilities}

    if bonus_style == "+2 / +1":
        col1, col2 = st.columns(2)
        plus_two = col1.segmented_control("+2 to", bg_abilities, key="plus_two")
        remaining_choices = [a for a in bg_abilities if a != plus_two]
        plus_one = col2.segmented_control("+1 to", remaining_choices, key="plus_one")
        bonuses[plus_two] = 2
        bonuses[plus_one] = 1
    else:
        for a in bg_abilities:
            bonuses[a] = 1
        st.text(f"+1 applied to {', '.join(bg_abilities)}")

# --- Final scores ---
st.divider()
st.subheader("Step 3: Final scores and modifiers")
st.markdown("Your final ability scores and modifiers are given below.")

if over_budget:
    st.warning("Final scores will appear once your point buy total is within budget.")
else:
    final_cols = st.columns([3, 2, 2], vertical_alignment="center")
    final_cols[0].write("**Ability**")
    final_cols[1].markdown("<div style='text-align: center'><b>Final Score</b></div>", unsafe_allow_html=True)
    final_cols[2].markdown("<div style='text-align: center'><b>Modifier</b></div>", unsafe_allow_html=True)

    final_scores = {}

    for ability in ABILITIES:
        bonus = bonuses.get(ability, 0)
        final_score = scores[ability] + bonus
        final_scores[ability] = final_score

        cols = st.columns([3, 2, 2], vertical_alignment="center")
        label = f"{ability} (+{bonus})" if bonus else ability
        cols[0].write(label)
        cols[1].markdown(f"<div style='text-align: center'>{final_score}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='text-align: center'>{ability_modifier(final_score):+d}</div>", unsafe_allow_html=True)

    st.session_state["final_ability_scores"] = final_scores