# RailCheck Mini - Eurailscout

Application Python simulant la chaine complete de mesure ferroviaire : generation de donnees UFM 160, analyse de KPIs, et monitoring temps reel.

## Description

Projet simulant le workflow d'Eurailscout France :

- Generation de donnees ferroviaires realistes (hauteur catenaire, ecartement voie selon EN 13848)
- API Flask avec endpoints statistiques et instrumentation Prometheus
- Interface PyQt avec 3 onglets : generation, analyse, visualisation
- Stack Docker : API + Prometheus + Grafana
- Fonctionnalite interactive : double-clic sur anomalie pour voir toutes ses positions

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Interface PyQt (Demo principale)

```bash
python src/gui_main.py
```

**Fonctionnalites :**
1. **Onglet Generation** : Generer des donnees CSV (3600 mesures)
2. **Onglet Analyse** : KPIs en temps reel (Distance, Conformite, Anomalies)
   - Double-clic sur une anomalie pour voir toutes ses positions PK
3. **Onglet Visualisation** : Graphiques (hauteur catenaire, repartition anomalies)

### Stack Docker avec Monitoring (Demo avancee)

```bash
cd docker
docker-compose up
```

**Acces :**
- API Flask : http://localhost:5000/stats
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin/admin)

**Arreter :**
```bash
docker-compose down
```

## Structure du projet

```
src/
  data_generator.py    - Generation donnees UFM 160 (CSV)
  api.py               - API Flask + Prometheus metrics
  gui_main.py          - Interface PyQt (3 onglets)
data/
  raw/                 - Fichiers CSV generes
docker/
  docker-compose.yml   - Orchestration (API + Prometheus + Grafana)
  Dockerfile           - Image container API
  prometheus.yml       - Configuration scraping
```

## Fonctionnalites cles

### Generation de donnees
- Simulation train UFM 160 a 140 km/h
- 3600 mesures par defaut (6 minutes)
- Hauteur catenaire selon EN 13848 (4.0-7.0m)
- 4% d'anomalies aleatoires : boulon_manquant, signalisation_defaillante, rail_fissure

### Analyse interactive
- KPIs en cartes colorees : Distance inspectee, Taux conformite, Anomalies detectees
- Tableau des anomalies par type
- Double-clic sur anomalie : fenetre avec toutes les positions PK

### Visualisations
- Evolution hauteur catenaire avec limites normatives
- Repartition anomalies par type avec valeurs affichees

### Monitoring Prometheus
- Metriques exposees : railcheck_mesures_total, railcheck_conformite_taux, railcheck_anomalies_total
- Scraping toutes les 15 secondes
- Dashboards Grafana configurables

## Endpoints API

- **GET /stats** - Statistiques globales (mesures, distance, conformite, anomalies)
- **GET /anomalies** - Liste anomalies avec positions
- **GET /hauteurs** - Statistiques hauteur catenaire
- **GET /metrics** - Metriques Prometheus

## Stack technique

- Python 3.10+
- Flask (API REST)
- PyQt5 (Interface desktop)
- Matplotlib (Graphiques)
- Prometheus client (Instrumentation)
- Docker / docker-compose
- Prometheus (Collecte metriques)
- Grafana (Dashboards)

## Auteur

Projet de demonstration pour poste Software & Data Engineer chez Eurailscout France.
