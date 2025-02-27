# --- Bibliotheken laden ---
import streamlit as st  # Streamlit für die Web-App
import pandas as pd  # Pandas für Datenverarbeitung
import plotly.express as px  # Plotly für interaktive Visualisierungen
from sklearn.cluster import DBSCAN  # DBSCAN-Clustering für geografische Daten
from collections import Counter  # Zählen der häufigsten Elemente (z. B. Küchentypen)
import os  # Betriebssystemfunktionen für Dateipfade

# --- APP KONFIGURATION ---
# Setzt die Konfiguration der Streamlit-App
st.set_page_config(page_title="Yelp Data Explorer", layout="wide")

# Dynamischer Dateipfad basierend auf dem aktuellen Skriptverzeichnis
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Verzeichnis des aktuellen Skripts
DATA_PATH = os.path.join(BASE_DIR, "JSON_Input", "yelp_academic_dataset_business.json")  # Pfad zur JSON-Datei

# --- DATENLADEN MIT CACHE ---
@st.cache_data  # Streamlit-Caching zur Optimierung der Ladegeschwindigkeit
def load_data():
    df = pd.read_json(DATA_PATH, lines=True, nrows=100000)
    return df

# Daten in den Haupt-DataFrame laden
df = load_data()

# --- NAVIGATIONSBEREICH ---
# Sidebar-Titel für die Navigation
st.sidebar.title("🔍 Navigation")

# Erstellen einer Seiten-Navigation mit verschiedenen Analyseoptionen
page = st.sidebar.radio(
    "Seite auswählen", 
    ["📍 Yelp-Karte", "📊 Statistiken", "⏰ Öffnungszeiten", "⚡ Insights & KPIs"]
)

# --- FILTER IN SIDEBAR ---
st.sidebar.subheader("Filter")

# Filter für minimale Sternebewertung
min_stars = st.sidebar.slider(
    "Min Sternebewertung je Unternehmen", 
    min_value=0.0, 
    max_value=5.0, 
    step=0.5, 
    value=0.0
)

# Filter für maximale Anzahl an Bewertungen 
max_reviews = st.sidebar.slider(
    "Max Anzahl an Bewertungen je Unternehmen", 
    min_value=1, 
    max_value=int(df["review_count"].max()), 
    value=7568  
)

# Anwenden der Filter auf den DataFrame
filtered_df = df[
    (df["stars"] >= min_stars) & 
    (df["review_count"] <= max_reviews)
]

# --- CLUSTERING (DBSCAN) ---
# Extrahieren der Koordinaten für das Clustering
coords = filtered_df[["latitude", "longitude"]].dropna().values

# Anwenden des DBSCAN-Clustering-Algorithmus:
# - `eps=0.1`: Maximale Entfernung zwischen zwei Punkten, um als ein Cluster zu gelten
# - `min_samples=5`: Mindestens 5 Punkte müssen sich in der Umgebung befinden, um als Cluster erkannt zu werden
clustering = DBSCAN(eps=0.1, min_samples=5).fit(coords)

# Cluster-Labels dem DataFrame hinzufügen 
filtered_df["cluster"] = clustering.labels_

# --- CLUSTER-DATEN ZUSAMMENFASSEN ---
# Gruppieren der Cluster, um für jedes Cluster folgende Werte zu berechnen:
# - Durchschnittliche geografische Position (Latitude, Longitude)
# - Durchschnittliche Sternebewertung
# - Gesamtzahl der Bewertungen innerhalb des Clusters
df_clusters = filtered_df.groupby("cluster").agg({
    "latitude": "mean",
    "longitude": "mean",
    "stars": "mean",
    "review_count": "sum"
}).reset_index()

# Entfernen von Noise-Punkten (-1 sind nicht zugewiesene Punkte, die nicht in Clustern liegen)
df_clusters = df_clusters[df_clusters["cluster"] != -1]


# --- SEITE 1: KARTENANSICHT ---
if page == "📍 Yelp-Karte":
    # Titel der Seite
    st.title("📍 Yelp geclusterte Unternehmenskarte")
    
    # Bestimmen der dominierenden Stadt pro Cluster:
    cluster_city_mapping = filtered_df.groupby("cluster")["city"].agg(
        lambda x: x.mode()[0] if not x.mode().empty else "Unbekannt"
    ).to_dict()
    
    # Erstellen der Cluster-Labels mit Stadtname:
    # - Ordnet jedem Cluster einen Städtenamen zu, um die Auswahl verständlicher zu machen.
    df_clusters["cluster_name"] = df_clusters["cluster"].map(lambda c: f"{cluster_city_mapping.get(c, 'Unbekannt')}")

    # Dictionary mit Cluster-IDs als Schlüssel und Städtenamen als Werte
    cluster_labels = df_clusters.set_index("cluster")["cluster_name"].to_dict()
    cluster_ids = list(cluster_labels.keys())  # Liste aller verfügbaren Cluster-IDs

    # Erstellen der Einzelauswahl für Cluster:
    selected_cluster = st.pills("🔎 Wähle ein Cluster", 
                                options=cluster_ids, 
                                format_func=lambda x: cluster_labels[x],  # Anzeigen des Städtenamens
                                selection_mode="single")

    # Setzen eines Standard-Clusters, falls kein Cluster ausgewählt wurde:
    if not selected_cluster:
        selected_cluster = cluster_ids[0]

    # Filtern der Daten für das ausgewählte Cluster
    df_cluster = filtered_df[filtered_df["cluster"] == selected_cluster]
    
    # Erstellen der Karte mit Yelp-Unternehmen im gewählten Cluster:
    fig = px.scatter_mapbox(df_cluster, 
                            lat="latitude",  # Latitude für Kartenpositionierung
                            lon="longitude",  # Longitude für Kartenpositionierung
                            color=df_cluster["stars"],  # Sternebewertung als Farbskala
                            hover_name="name",  # Name des Unternehmens in Tooltip
                            hover_data=["state", "city", "stars", "review_count"],  # Weitere Infos im Tooltip
                            zoom=8,  # Zoom-Level der Karte
                            height=600)  # Höhe der Karte

    # Layout-Anpassung für eine bessere Darstellung
    fig.update_layout(mapbox_style="open-street-map", width=900, height=600)

    # Karte in Streamlit anzeigen
    st.plotly_chart(fig)

# --- SEITE 2: STATISTISCHE ANALYSEN ---
elif page == "📊 Statistiken":
    # Titel der Seite
    st.title("📊 Yelp Business Statistiken")

    # --- Histogramm Sternebewertungen ---
    fig1 = px.histogram(filtered_df, 
                        x="stars",  # Sternebewertung als x-Achse
                        nbins=10,  # Anzahl der Balken im Histogramm
                        labels={'stars': "Sternebewertung", 'count': "Anzahl"},  
                        title="⭐ Verteilung der Sternebewertungen")  # Diagrammtitel
    st.plotly_chart(fig1)  # Diagramm in Streamlit anzeigen

    # --- Boxplot Sternebewertungen ---
    fig2 = px.box(filtered_df, 
                  x="stars",  # Sternebewertung als x-Achse
                  labels={'stars': "Sternebewertung"},  
                  title="📦 Boxplot der Sternebewertungen")  # Diagrammtitel
    st.plotly_chart(fig2)  # Diagramm in Streamlit anzeigen

    # --- Säulendiagramm der Küchentypen ---
    st.subheader("🌍 Top 10 Küchentypen in Restaurants")

    # Filtert Restaurants aus dem Datensatz (Unternehmen mit "Restaurant" in der Kategorie)
    restaurants = filtered_df[filtered_df["categories"].str.contains("Restaurant", na=False)]
    
    # Zählt die häufigsten Küchentypen 
    top_cuisines = Counter(restaurants["categories"].str.split(", ").explode()).most_common(10)
    
    # Erstellt ein Balkendiagramm mit den 10 häufigsten Küchentypen
    fig = px.bar(x=[c[0] for c in top_cuisines],  
                 y=[c[1] for c in top_cuisines],  
                 labels={'x': "Küchentyp", 'y': "Anzahl"})  
    
    # Diagramm in Streamlit anzeigen
    st.plotly_chart(fig)

# --- SEITE 3: ÖFFNUNGSZEITEN ---
elif page == "⏰ Öffnungszeiten":
    # Titel der Seite
    st.title("⏰ Analyse der Öffnungszeiten")

    # Funktion zum Extrahieren der Öffnungszeiten aus dem `hours`-Dictionary
    def extract_opening_times(hours, stars):
        # Falls `hours` kein Dictionary ist (z. B. NaN-Werte), gibt die Funktion `None` zurück
        if not isinstance(hours, dict):
            return None
        data = []
        for day, time_range in hours.items():
            if "-" in time_range:  # Prüft, ob ein Zeitbereich angegeben ist
                try:
                    # Trennt die Öffnungszeit (z. B. "08:00-20:00" → "08:00")
                    open_time = time_range.split("-")[0]
                    open_hour = int(open_time.split(":")[0])  # Extrahiert die Stunde als Integer
                    # Erstellt ein Dictionary mit Wochentag, Öffnungsstunde und Sternebewertung
                    data.append({"weekday": day, "opening_hour": open_hour, "stars": stars})
                except ValueError:
                    continue  # Falls ein Wert nicht geparst werden kann, wird er übersprungen
        return pd.DataFrame(data)  # Gibt die Daten als DataFrame zurück

    # 💡 Nutze `filtered_df`, damit Filter in der Sidebar berücksichtigt werden
    df_opening = df.apply(lambda row: extract_opening_times(row["hours"], row["stars"]), axis=1)
    df_opening = pd.concat(df_opening.dropna().tolist(), ignore_index=True)  # Kombiniert alle extrahierten Daten

    # Englische Wochentage in deutsche Wochentage umwandeln
    day_mapping = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag"
    }
    df_opening["weekday"] = df_opening["weekday"].map(day_mapping)  # Mapping anwenden

    # Sternebewertungen in 5 Gruppen einteilen (1-5), aufsteigend
    df_opening["stars_group"] = pd.cut(df_opening["stars"], 
                                       bins=[0, 2, 3, 4, 4.5, 5],  # Definiert die Kategorien
                                       labels=["1", "2", "3", "4", "5"],  # Bezeichnet die Gruppen mit Zahlen (Sterne)
                                       include_lowest=True, 
                                       ordered=True)

    # Farbzuordnung für Sterne-Gruppen (1 → 5 in aufsteigender Reihenfolge)
    color_map = {
        "1": "#1f77b4",  # Blau
        "2": "#2ca02c",  # Grün
        "3": "#ff7f0e",  # Orange
        "4": "#d62728",  # Rot
        "5": "#9467bd"   # Lila
    }

    # Boxplot der Öffnungszeiten pro Wochentag mit Farben nach Sterne-Gruppen
    fig3 = px.box(df_opening, 
                  x="weekday",  # Wochentag auf der x-Achse (jetzt auf Deutsch)
                  y="opening_hour",  # Öffnungsstunde auf der y-Achse
                  color="stars_group",  # Farbzuordnung nach Sterne-Gruppen
                  title="📅 Öffnungszeiten nach Wochentag (Farbe = Sternebewertung)",  
                  labels={"weekday": "Wochentag", "opening_hour": "Öffnungsstunde", "stars_group": "Sternebewertung"},  
                  category_orders={"stars_group": ["1", "2", "3", "4", "5"],  # Sortierung der Sternebewertung
                                   "weekday": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]},  # Reihenfolge der deutschen Wochentage
                  color_discrete_map=color_map)  # Farbzuordnung für die Sterne-Gruppen

    # Boxplot in der Streamlit-App anzeigen
    st.plotly_chart(fig3)

# --- SEITE 4: KPIs & INSIGHTS ---
elif page == "⚡ Insights & KPIs":
    # Titel der Seite
    st.title("⚡ Wichtige KPIs & Business Insights")

    # --- KPI-Anzeige ---
    # Erstellt drei Spalten für die Anzeige wichtiger Kennzahlen (KPIs)
    col1, col2, col3 = st.columns(3)

    # KPI 1: Gesamtzahl der gefilterten Unternehmen
    col1.metric("📍 Gesamtzahl der Unternehmen", len(filtered_df))

    # KPI 2: Durchschnittliche Sternebewertung aller gefilterten Unternehmen, auf 2 Dezimalstellen gerundet
    col2.metric("⭐ Durchschnittliche Sternebewertung", round(filtered_df["stars"].mean(), 2))

    # KPI 3: Gesamtzahl aller Bewertungen in den gefilterten Unternehmen
    col3.metric("💬 Gesamtzahl der Bewertungen", filtered_df["review_count"].sum())

    # --- Diagramm: Sternebewertung vs. Anzahl der Bewertungen ---
    st.subheader("📌 Verhältnis von Sternebewertung zu Anzahl der Bewertungen")

    # Scatterplot zur Darstellung des Zusammenhangs zwischen der Anzahl der Bewertungen und der Sternebewertung
    fig4 = px.scatter(
        filtered_df, 
        x="review_count", 
        y="stars", 
        labels={'stars': "Sternebewertung", 'review_count': "Anzahl Bewertungen"}, 
        title="📈 Anzahl der Bewertungen vs. Sternebewertung"
    )
    st.plotly_chart(fig4)

    # --- Diagramm: Unternehmen mit den meisten Bewertungen ---
    st.subheader("🔍 Unternehmen mit den meisten Bewertungen")

    # Sortiert die Unternehmen nach der Anzahl der Bewertungen in absteigender Reihenfolge und nimmt die Top 10
    df_top_reviews = df.sort_values(by="review_count", ascending=False).head(10)

    # Balkendiagramm zur Visualisierung der Unternehmen mit den meisten Bewertungen
    fig5 = px.bar(
        df_top_reviews, 
        x="name", 
        y="review_count", 
        labels={'name': "Name", 'review_count': "Anzahl Bewertungen"}, 
        title="🏆 Unternehmen mit den meisten Yelp-Bewertungen"
    )
    st.plotly_chart(fig5)


# --- FAZIT ---
st.sidebar.markdown("**Erstellt von Maximilian van Lienden**")
