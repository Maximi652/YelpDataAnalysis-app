# YelpDataAnalysis-app
Yelp Data Analysis ist eine interaktive Streamlit-App zur explorativen Analyse des Yelp Academic Datasets. Sie bietet geografische Clusteranalysen mit DBSCAN, statistische Visualisierungen, eine Untersuchung der Öffnungszeiten sowie ein KPI-Dashboard. Implementiert mit Python, Streamlit, Plotly und Pandas.

**Sonstige Beteiligung Angewandte Programmierung**

📌 Beschreibung der Streamlit-App für die Analyse von Yelp-Daten
1. Einführung
Die entwickelte interaktive Streamlit-Anwendung dient der explorativen Datenanalyse des Yelp-Datensatzes. Sie ermöglicht eine dynamische Visualisierung und Untersuchung verschiedener Unternehmensmerkmale, insbesondere der geografischen Verteilung, Sternebewertungen und Öffnungszeiten.

Durch die Integration von Clustering-Algorithmen (DBSCAN), interaktiven Karten (Mapbox) und statistischen Visualisierungen (Plotly) wird eine fundierte Analyse der Yelp-Daten unterstützt.

2. Funktionsübersicht
Die App ist in mehrere Module unterteilt, die über eine Seiten-Navigation ausgewählt werden können:

📍 1. Yelp-Karte (Geografische Analyse & Clustering)
Die geografische Verteilung der Unternehmen wird mithilfe einer interaktiven Mapbox-Karte dargestellt.
Die Unternehmen werden mithilfe des DBSCAN-Clustering-Algorithmus gruppiert, um geografische Hotspots zu identifizieren.
Nutzer können Cluster anhand der dominierenden Stadt auswählen.

📊 2. Statistische Analysen
Histogramme und Boxplots zeigen die Verteilung der Sternebewertungen und ermöglichen eine erste explorative Analyse.
Außerdem wird die Anzahl der vertretenen Küchentypen dargestellt.

⏰ 3. Analyse der Öffnungszeiten
Die Öffnungszeiten der Unternehmen werden extrahiert und visualisiert.
Mittels Boxplots wird die Verteilung der Öffnungszeiten pro Wochentag analysiert.
Die Boxplots sind nach Sternebewertung gruppiert, um mögliche Zusammenhänge zwischen Öffnungszeiten und Kundenbewertungen zu identifizieren.
Die Farbgebung basiert auf einer geordneten Sternebewertungs-Skala (1 = Blau → 5 = Lila).

⚡ 4. Insights & KPIs
Wesentliche Key Performance Indicators (KPIs) wie Anzahl der Unternehmen, durchschnittliche Sternebewertung und Gesamtzahl der Rezensionen werden berechnet.
Unternehmen mit den meisten Rezensionen werden hervorgehoben.
Die Beziehung zwischen Bewertungsanzahl und Sternebewertung wird visuell untersucht.
3. Methodische Grundlagen & Technische Umsetzung

📌 Datensatz:
Der Yelp Academic Dataset wurde als JSON-Datei eingelesen und mit Pandas verarbeitet.
Unstrukturierte Daten wie Öffnungszeiten wurden in eine strukturierte Form überführt.
Fehlende Werte wurden gefiltert oder mittels Aggregationen ersetzt.

📌 Clustering:
Der DBSCAN-Algorithmus wurde genutzt, um Unternehmen anhand ihrer geografischen Koordinaten in Cluster zu gruppieren.
Die Cluster-Zugehörigkeit wurde durch den Modus der Städtenamen bestimmt.

📌 Visualisierung:
Plotly wurde für interaktive Grafiken genutzt (z. B. Boxplots, Histogramme, Scatterplots).
Seaborn wurde für die Heatmap der Unternehmensdichte verwendet.
Mapbox-Stil wurde für die interaktive Kartenvisualisierung integriert.

📌 Benutzerinteraktion:
Filteroptionen (Sternebewertung, Anzahl der Rezensionen) ermöglichen eine dynamische Datenanalyse.
Cluster- und Farbwahl in der Kartenansicht verbessern die Explorationsmöglichkeiten.
Dynamische Sidebar sorgt für eine intuitive Navigation zwischen den Analysemodulen.

4. Erkenntnisse & Anwendungsbereiche
Diese Anwendung zeigt auf, wie sich Yelp-Daten für wissenschaftliche Analysen und Geschäftsentscheidungen nutzen lassen. Mögliche Erkenntnisse aus der App umfassen:


✔ Geografische Clusterbildung: Identifikation von Regionen mit hoher Unternehmensdichte
✔ Zusammenhang zwischen Öffnungszeiten & Sternebewertung: Gibt es einen optimalen Zeitpunkt für hohe Bewertungen?
✔ Kundeninteraktion & Sternebewertung: Zusammenhang zwischen Anzahl der Bewertungen und Durchschnittssterne
✔ Benchmarking für Unternehmen: Vergleich von Unternehmen nach Standort und Sternebewertung


5. Fazit & Weiterentwicklung
Diese Streamlit-App bietet eine umfassende Plattform zur Analyse von Yelp-Daten. Mögliche Weiterentwicklungen umfassen:

🚀 Erweiterung des Clustering-Algorithmus: Optimierung durch alternative Verfahren wie K-Means oder HDBSCAN
📊 Erweiterte NLP-Analyse: Sentiment-Analyse der Rezensionstexte mit Machine Learning
🌍 Internationalisierung: Anpassung der App für weitere Yelp-Märkte

Datenquelle: https://business.yelp.com/data/resources/open-dataset/
