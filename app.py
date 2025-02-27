import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import DBSCAN
from collections import Counter

# --- APP KONFIGURATION ---
st.set_page_config(page_title="Yelp Data Explorer", layout="wide")

# --- DATENLADEN MIT CACHE ---
@st.cache_data
def load_data():
    df = pd.read_json('/Users/maxi/Data Analytics/Angewannte Programmierung/JSON_Input/yelp_academic_dataset_business.json', lines=True)
    return df

df = load_data()

# --- NAVIGATIONSBEREICH ---
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Seite auswählen", ["📍 Yelp-Karte", "📊 Statistiken", "⏰ Öffnungszeiten", "⚡ Insights & KPIs"])

# --- FILTER IN SIDEBAR ---
st.sidebar.subheader("Filter")
min_stars = st.sidebar.slider("Minimale Sternebewertung", min_value=0.0, max_value=5.0, step=0.5, value=3.0)
max_reviews = st.sidebar.slider("Maximale Anzahl an Bewertungen", min_value=1, max_value=int(df["review_count"].max()), value=3000)
filtered_df = df[(df["stars"] >= min_stars) & (df["review_count"] <= max_reviews)]

# --- CLUSTERING (DBSCAN) ---
coords = filtered_df[["latitude", "longitude"]].dropna().values
clustering = DBSCAN(eps=0.1, min_samples=5).fit(coords)
filtered_df["cluster"] = clustering.labels_

df_clusters = filtered_df.groupby("cluster").agg({
    "latitude": "mean",
    "longitude": "mean",
    "stars": "mean",
    "review_count": "sum"
}).reset_index()

df_clusters = df_clusters[df_clusters["cluster"] != -1]

# --- SEITE 1: KARTENANSICHT ---
if page == "📍 Yelp-Karte":
    st.title("📍 Yelp Unternehmenskarte mit Clustering")
    
    # 1️⃣ Bestimme die dominierende Stadt pro Cluster
    cluster_city_mapping = filtered_df.groupby("cluster")["city"].agg(lambda x: x.mode()[0] if not x.mode().empty else "Unbekannt").to_dict()
    
    # 2️⃣ Erstelle Cluster-Labels mit Stadtname
    df_clusters["cluster_name"] = df_clusters["cluster"].map(lambda c: f"{cluster_city_mapping.get(c, 'Unbekannt')}")
    
    # 3️⃣ Erstelle Liste mit Cluster-Labels für die Auswahl
    cluster_labels = df_clusters.set_index("cluster")["cluster_name"].to_dict()
    cluster_ids = list(cluster_labels.keys())

    # 4️⃣ `st.pills()` mit Cluster-Namen (Einzelauswahl)
    selected_cluster = st.pills("🔎 Wähle ein Cluster", options=cluster_ids, format_func=lambda x: cluster_labels[x], selection_mode="single")

    # 5️⃣ Falls keine Auswahl getroffen wurde, setze den ersten Cluster als Standard
    if not selected_cluster:
        selected_cluster = cluster_ids[0]

    # 6️⃣ Filterung der Daten basierend auf dem ausgewählten Cluster
    df_cluster = filtered_df[filtered_df["cluster"] == selected_cluster]
    
    # 7️⃣ Karte mit Yelp-Unternehmen im ausgewählten Cluster anzeigen
    fig = px.scatter_mapbox(df_cluster, 
                            lat="latitude", 
                            lon="longitude", 
                            color=df_cluster["stars"],
                            hover_name="name", 
                            hover_data=["state", "city", "stars", "review_count"],
                            zoom=8, 
                            height=600)
    
    fig.update_layout(mapbox_style="open-street-map", width=900, height=600)
    
    st.plotly_chart(fig)

# --- SEITE 2: STATISTISCHE ANALYSEN ---
elif page == "📊 Statistiken":
    st.title("📊 Yelp Business Statistiken")

    # Histogramm Sternebewertungen
    fig1 = px.histogram(filtered_df, x="stars", nbins=10, title="⭐ Verteilung der Sternebewertungen")
    st.plotly_chart(fig1)

    # Boxplot Sternebewertungen
    fig2 = px.box(filtered_df, x="stars", title="📦 Boxplot der Sternebewertungen (horizontal)")
    st.plotly_chart(fig2)

    # Heatmap der Unternehmensdichte
    st.subheader("🌍 Top 10 Küchentypen in Restaurants")
    restaurants = filtered_df[filtered_df["categories"].str.contains("Restaurant", na=False)]
    top_cuisines = Counter(restaurants["categories"].str.split(", ").explode()).most_common(10)
    fig = px.bar(x=[c[0] for c in top_cuisines], y=[c[1] for c in top_cuisines],
             labels={'x': "Küchentyp", 'y': "Anzahl"}, title="Top 10 Küchentypen in Restaurants")
    st.plotly_chart(fig)
    
# --- SEITE 3: ÖFFNUNGSZEITEN ---
elif page == "⏰ Öffnungszeiten":
    st.title("⏰ Analyse der Öffnungszeiten")

    def extract_opening_times(hours, stars):
        if not isinstance(hours, dict):
            return None
        data = []
        for day, time_range in hours.items():
            if "-" in time_range:
                try:
                    open_time = time_range.split("-")[0]
                    open_hour = int(open_time.split(":")[0])
                    data.append({"weekday": day, "opening_hour": open_hour, "stars": stars})
                except ValueError:
                    continue
        return pd.DataFrame(data)

    # 💡 Nutze `filtered_df`, damit Filter in Sidebar berücksichtigt werden
    df_opening = df.apply(lambda row: extract_opening_times(row["hours"], row["stars"]), axis=1)
    df_opening = pd.concat(df_opening.dropna().tolist(), ignore_index=True)

    # 🔹 Sternebewertungen in 5 Gruppen einteilen (1-5), aufsteigend
    df_opening["stars_group"] = pd.cut(df_opening["stars"], 
                                       bins=[0, 2, 3, 4, 4.5, 5],  # 🟢 Aufsteigend
                                       labels=["1", "2", "3", "4", "5"], 
                                       include_lowest=True, 
                                       ordered=True)

    # 🔹 Farbzuordnung für Sterne-Gruppen (1 → 5 in aufsteigender Reihenfolge)
    color_map = {
        "1": "#1f77b4",  # Blau
        "2": "#2ca02c",  # Grün
        "3": "#ff7f0e",  # Orange
        "4": "#d62728",  # Rot
        "5": "#9467bd"   # Lila
    }

    # 🔹 Boxplot der Öffnungszeiten pro Wochentag mit Farben nach Sterne-Gruppen
    fig3 = px.box(df_opening, x="weekday", y="opening_hour", color="stars_group",
                  title="📅 Öffnungszeiten nach Wochentag (Farbe = Sternebewertung)",
                  labels={"weekday": "Wochentag", "opening_hour": "Öffnungsstunde", "stars_group": "Sterne-Gruppe"},
                  category_orders={"stars_group": ["1", "2", "3", "4", "5"],  # 🔥 Sicherstellen, dass es aufsteigend sortiert wird
                                   "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                  color_discrete_map=color_map)

    st.plotly_chart(fig3)

# --- SEITE 4: KPIs & INSIGHTS ---
elif page == "⚡ Insights & KPIs":
    st.title("⚡ Wichtige KPIs & Business Insights")

    col1, col2, col3 = st.columns(3)
    col1.metric("📍 Gesamtzahl der Unternehmen", len(filtered_df))
    col2.metric("⭐ Durchschnittliche Sternebewertung", round(filtered_df["stars"].mean(), 2))
    col3.metric("💬 Gesamtzahl der Bewertungen", filtered_df["review_count"].sum())

    st.subheader("📌 Verhältnis von Sternebewertung zu Anzahl der Bewertungen")
    fig4 = px.scatter(filtered_df, x="review_count", y="stars", title="📈 Anzahl der Bewertungen vs. Sternebewertung")
    st.plotly_chart(fig4)

    st.subheader("🔍 Unternehmen mit den meisten Bewertungen")
    df_top_reviews = df.sort_values(by="review_count", ascending=False).head(10)
    fig5 = px.bar(df_top_reviews, x="name", y="review_count", title="🏆 Unternehmen mit den meisten Yelp-Bewertungen")
    st.plotly_chart(fig5)

# --- FAZIT ---
st.sidebar.markdown("**Erstellt von Maximilian van Lienden**")