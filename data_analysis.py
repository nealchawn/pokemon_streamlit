import pandas as pd
import streamlit as st
import plotly.express as px

# statstic 1: display pokemon stats
pokemon_df = pd.read_csv("./pokemon_gen1_to_gen4.csv")
# print(pokemon_df.head())

# statistic 2: total pokemon per generation vs generation
total_pokemon_by_generation = (
    pokemon_df
    .groupby("generation")["national_dex"]
    .nunique()
    .reset_index(name="total_pokemon")
)

# print(total_pokemon_by_generation)

# statstic 3: frequency of pokemon type
# Note slices represent type appearances rather than *unique Pokémon
# considering pokemon can have two types
pokemon_types = sorted(
    set(pokemon_df["type_1"].dropna()) |
    set(pokemon_df["type_2"].dropna())
)

rows = []

for pokemon_type in pokemon_types:
    type_filter = (
        (pokemon_df["type_1"] == pokemon_type) |
        (pokemon_df["type_2"] == pokemon_type)
    )

    type_df = pokemon_df[type_filter]

    frequency = len(type_df)

    rows.append({
        "type": pokemon_type,
        "frequency": frequency
    })

type_frequency = pd.DataFrame(rows)

type_frequency = type_frequency.sort_values(
    "frequency",
    ascending=False
)

# print(type_frequency)



# statistic 4: average base_stat_total for each type,
# note for double types it counts for both.
pokemon_types = sorted(
    set(pokemon_df["type_1"].dropna()) |
    set(pokemon_df["type_2"].dropna())
)

rows = []

for pokemon_type in pokemon_types:
    type_df = pokemon_df[
        (pokemon_df["type_1"] == pokemon_type) |
        (pokemon_df["type_2"] == pokemon_type)
    ]

    average_base_stat_total = type_df["Total"].mean()

    rows.append({
        "type": pokemon_type,
        "average_base_stat_total": average_base_stat_total
    })

average_bst_by_type = pd.DataFrame(rows)

# (average_bst_by_type)




# Visualization 1: Pokémon base stats by selected Pokémon — bar chart

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    pokemon_df = pd.read_csv("./pokemon_gen1_to_gen4.csv")

    pokemon_df.columns = pokemon_df.columns.str.strip()

    stat_cols = ["HP", "Atk", "Def", "SpA", "SpD", "Spe", "Total", "generation", "national_dex"]

    pokemon_df[stat_cols] = pokemon_df[stat_cols].apply(
        pd.to_numeric,
        errors="coerce"
    )

    return pokemon_df


pokemon_df = load_data()


# -----------------------------
# Page title
# -----------------------------
st.title("Pokémon Base Stats Explorer")


# -----------------------------
# Pokémon selector
# -----------------------------
pokemon_options = (
    pokemon_df
    .sort_values("national_dex")["pokemon"]
    .tolist()
)

selected_pokemon = st.selectbox(
    "Choose a Pokémon",
    pokemon_options,
    format_func=lambda name: name.replace("-", " ").title()
)


# -----------------------------
# Filter selected Pokémon
# -----------------------------
selected_row = pokemon_df[
    pokemon_df["pokemon"] == selected_pokemon
].iloc[0]


# -----------------------------
# Display basic info
# -----------------------------
st.subheader(selected_pokemon.replace("-", " ").title())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("National Dex", int(selected_row["national_dex"]))

with col2:
    st.metric("Generation", int(selected_row["generation"]))

with col3:
    st.metric("Type 1", selected_row["type_1"].title())

with col4:
    type_2 = selected_row["type_2"]

    if pd.isna(type_2):
        type_2 = "None"
    else:
        type_2 = type_2.title()

    st.metric("Type 2", type_2)


# -----------------------------
# Create stats dataframe
# -----------------------------
base_stat_cols = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]

pokemon_stats_df = pd.DataFrame({
    "stat": base_stat_cols,
    "base_stat": [selected_row[col] for col in base_stat_cols]
})

st.dataframe(pokemon_stats_df)


# -----------------------------
# Plot base stats
# -----------------------------
fig = px.bar(
    pokemon_stats_df,
    x="stat",
    y="base_stat",
    title=f"Base Stats for {selected_pokemon.replace('-', ' ').title()}",
    labels={
        "stat": "Base Stat",
        "base_stat": "Value"
    },
    text="base_stat"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    yaxis_range=[0, max(160, pokemon_stats_df["base_stat"].max() + 20)]
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Optional: show total base stat
# -----------------------------
st.metric("Base Stat Total", int(selected_row["Total"]))


# Visualization 2: Total Pokémon per generation — line chart
st.subheader("Total Pokémon by Generation")

total_pokemon_by_generation = (
    pokemon_df
    .groupby("generation")["national_dex"]
    .nunique()
    .reset_index(name="total_pokemon")
    .sort_values("generation")
)

fig_generation = px.line(
    total_pokemon_by_generation,
    x="generation",
    y="total_pokemon",
    markers=True,
    text="total_pokemon",
    title="Total Pokémon Introduced by Generation",
    labels={
        "generation": "Generation",
        "total_pokemon": "Total Pokémon"
    }
)

fig_generation.update_traces(
    textposition="top center"
)

fig_generation.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1
    ),
    yaxis_range=[
        0,
        total_pokemon_by_generation["total_pokemon"].max() + 25
    ]
)

st.plotly_chart(fig_generation, use_container_width=True)

st.dataframe(total_pokemon_by_generation)


# Visualization 3: Pokémon type frequency — donut/pie chart
st.subheader("Pokémon Type Frequency")

type_frequency_display = type_frequency.copy()
type_frequency_display["type"] = type_frequency_display["type"].str.title()

fig_type_frequency = px.pie(
    type_frequency_display,
    names="type",
    values="frequency",
    title="Frequency of Pokémon Types",
    hole=0.35
)

fig_type_frequency.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

st.plotly_chart(fig_type_frequency, use_container_width=True)

st.dataframe(type_frequency_display)


# Visualization 4: Average base stat total by type — horizontal bar chart
st.subheader("Average Base Stat Total by Pokémon Type")

average_bst_display = average_bst_by_type.copy()
average_bst_display["type"] = average_bst_display["type"].str.title()

fig_average_bst = px.bar(
    average_bst_display,
    x="average_base_stat_total",
    y="type",
    orientation="h",
    text="average_base_stat_total",
    title="Average Base Stat Total by Pokémon Type",
    labels={
        "average_base_stat_total": "Average Base Stat Total",
        "type": "Pokémon Type"
    }
)

fig_average_bst.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    ),
    xaxis_range=[
        0,
        average_bst_display["average_base_stat_total"].max() + 50
    ]
)

fig_average_bst.update_traces(
    textposition="outside"
)

st.plotly_chart(fig_average_bst, use_container_width=True)

st.caption(
    "Dual-type Pokémon are counted once for each of their types. "
    "For example, Charizard contributes its base stat total to both Fire and Flying."
)

st.dataframe(average_bst_display)