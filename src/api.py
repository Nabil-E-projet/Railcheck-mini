from flask import Flask, jsonify
import csv
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response

app = Flask(__name__)

# Metriques Prometheus
mesures_total = Gauge('railcheck_mesures_total', 'Nombre total de mesures')
distance_km = Gauge('railcheck_distance_km', 'Distance inspectee en km')
anomalies_total = Gauge('railcheck_anomalies_total', 'Nombre total anomalies')
conformite_taux = Gauge('railcheck_conformite_taux', 'Taux de conformite en pourcentage')

@app.route('/stats')
def get_stats():
    fichier = open('data/raw/mesures_ufm160.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(fichier)
    
    total = 0
    anomalies = 0
    pk_min = 999999
    pk_max = 0
    
    for ligne in reader:
        total = total + 1
        if ligne['defaut_type']:
            anomalies = anomalies + 1
        
        pk = float(ligne['pk_position'])
        if pk < pk_min:
            pk_min = pk
        if pk > pk_max:
            pk_max = pk
    
    fichier.close()
    
    distance = (pk_max - pk_min) / 1000
    conformite = (total - anomalies) / total * 100
    
    # Mettre a jour les metriques Prometheus
    mesures_total.set(total)
    distance_km.set(round(distance, 2))
    anomalies_total.set(anomalies)
    conformite_taux.set(round(conformite, 2))
    
    return jsonify({
        'total_mesures': total,
        'distance_km': round(distance, 2),
        'anomalies': anomalies,
        'conformite': round(conformite, 2)
    })

@app.route('/anomalies')
def get_anomalies():
    fichier = open('data/raw/mesures_ufm160.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(fichier)
    
    compteur = {}
    
    for ligne in reader:
        if ligne['defaut_type']:
            type_anomalie = ligne['defaut_type']
            if type_anomalie in compteur:
                compteur[type_anomalie] = compteur[type_anomalie] + 1
            else:
                compteur[type_anomalie] = 1
    
    fichier.close()
    
    return jsonify(compteur)

@app.route('/hauteurs')
def get_hauteurs():
    fichier = open('data/raw/mesures_ufm160.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(fichier)
    
    hauteurs = []
    for ligne in reader:
        hauteurs.append(float(ligne['hauteur_catenaire']))
    
    fichier.close()
    
    somme = 0
    for h in hauteurs:
        somme = somme + h
    moyenne = somme / len(hauteurs)
    
    hauteur_min = min(hauteurs)
    hauteur_max = max(hauteurs)
    
    return jsonify({
        'moyenne': round(moyenne, 2),
        'min': round(hauteur_min, 2),
        'max': round(hauteur_max, 2),
        'total_mesures': len(hauteurs)
    })

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

