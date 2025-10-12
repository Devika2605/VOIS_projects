import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Netflix Dataset Dashboard", layout="wide")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    df = pd.read_csv("Netflix Dataset.csv")

    # Normalize columns
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Rename columns based on your dataset structure
    df.rename(columns={
        "category": "type",          # Movie / TV Show
        "type": "listed_in",         # Genre
        "release_date": "year_added" # Year or Date
    }, inplace=True)

    # Convert release date to datetime safely
    df["year_added"] = pd.to_datetime(df["year_added"], errors="coerce").dt.year

    # Fill missing values
    for col in ["type", "listed_in", "country"]:
        if col not in df.columns:
            df[col] = "Unknown"
        else:
            df[col] = df[col].fillna("Unknown")

    return df

df = load_data()

st.title("🎬 Netflix Dashboard")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("🔍 Filter Options")

countries = ['All'] + sorted(df['country'].dropna().unique().tolist())
genres = ['All'] + sorted(set(", ".join(df['listed_in'].dropna()).split(", ")))
types = ['All'] + sorted(df['type'].dropna().unique().tolist())

selected_country = st.sidebar.selectbox("🌍 Select Country", countries)
selected_genre = st.sidebar.selectbox("🎭 Select Genre", genres)
selected_type = st.sidebar.selectbox("📺 Select Category (Movie / TV Show)", types)

# ---------- APPLY FILTERS ----------
filtered_df = df.copy()

if selected_country != "All":
    filtered_df = filtered_df[filtered_df['country'].str.contains(selected_country, case=False, na=False)]

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df['listed_in'].str.contains(selected_genre, case=False, na=False)]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == selected_type]

st.markdown(f"### Showing {len(filtered_df)} titles")

# ---------- OVERVIEW METRICS ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", len(filtered_df))
col2.metric("Movies", len(filtered_df[filtered_df["type"].str.contains("Movie", case=False)]))
col3.metric("TV Shows", len(filtered_df[filtered_df["type"].str.contains("TV", case=False)]))

# ---------- VISUALS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Type Distribution", 
    "🎬 Genre Popularity", 
    "🌎 Country Insights",
    "📈 Yearly Trend"
])

# --- Tab 1: Type Distribution ---
with tab1:
    st.subheader("Type Distribution (Movies vs TV Shows)")
    type_counts = filtered_df['type'].value_counts()
    if len(type_counts) > 0:
        fig, ax = plt.subplots(figsize=(5, 3))  # width=6 inches, height=4 inches 
        colors = ["#2A4676", "#C6954A"][:len(type_counts)]
        type_counts.plot(kind='bar', color=colors, ax=ax)
        plt.tight_layout() 
        plt.title("Movies vs TV Shows")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)
    else:
        st.warning("No titles to display for this filter combination.")

# --- Tab 2: Genre Popularity ---
with tab2:
    st.subheader("Top 10 Genres")
    all_genres = filtered_df['listed_in'].str.split(',').explode().str.strip()
    top_genres = all_genres.value_counts().head(10)
    if len(top_genres) > 0:
        fig, ax = plt.subplots(figsize=(5, 3))  # width=6 inches, height=4 inches
        top_genres.plot(kind='barh', color='#FF4B4B', ax=ax)
        plt.title("Top 10 Genres")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)
    else:
        st.warning("No genres to display for this filter combination.")

# --- Tab 3: Country Insights ---
with tab3:
    st.subheader("Top 10 Countries by Content")
    countries_data = filtered_df['country'].str.split(',').explode().str.strip().value_counts().head(10)
    if len(countries_data) > 0:
        fig, ax = plt.subplots(figsize=(5, 3))  # width=6 inches, height=4 inches
        countries_data.plot(kind='bar', color="#2A4676", ax=ax)
        plt.title("Top 10 Countries by Content")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)
    else:
        st.warning("No countries to display for this filter combination.")

# --- Tab 4: Yearly Trend ---
with tab4:
    st.subheader("Content Trend by Year")
    year_counts = filtered_df['year_added'].value_counts().sort_index()
    if len(year_counts) > 0:
        fig, ax = plt.subplots(figsize=(5, 3))  # width=6 inches, height=4 inches
        year_counts.plot(kind='line', marker='o', color='#FF4B4B', ax=ax)
        plt.title("Content Trend by Year")
        plt.xlabel("Year")
        plt.ylabel("Number of Titles")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)
    else:
        st.warning("No yearly data to display for this filter combination.")

# ---------- RAW DATA VIEW ----------
with st.expander("📋 View Raw Data"):
    st.dataframe(filtered_df)
