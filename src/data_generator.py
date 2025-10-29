import os
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

VITESSE_TRAIN = 140  # km/h
INTERVALLE_MESURE = 0.1  # secondes
LONGUEUR_SEGMENT = 100  # mètres
TAUX_ANOMALIES = 0.04  # 4% d'anomalies

def generer_timestamps(debut: datetime, duree_heures: float) -> List[datetime]:
    intervalle=INTERVALLE_MESURE
    nombre=int(duree_heures*3600/intervalle)
    timestamps=[]
    for i in range(nombre):
        timestamp_act=debut+timedelta(seconds=i*intervalle)
        timestamps.append(timestamp_act)
    return timestamps

def generer_position_pk(timestamps: List[datetime]) -> List[float]:
    positions = []
    vitesse_ms=VITESSE_TRAIN/3.6    
    ts_debut=timestamps[0]
    for i in timestamps:
        temps_ecoule=(i-ts_debut).total_seconds()
        position=vitesse_ms*temps_ecoule
        positions.append(position)
    return positions

def generer_hauteur_catenaire(position: float) -> float:
    hauteur = 5.5
    hauteur = hauteur + random.gauss(0, 0.2)

    if hauteur < 4.0:
        hauteur = 4.0
    if hauteur > 7.0:
        hauteur = 7.0
    
    hauteur = round(hauteur, 2)
    
    return hauteur

def generer_anomalie() -> Dict[str, Any]:

    types = ["boulon_manquant", "signalisation_defaillante", "rail_fissure"]
    type_choisi = random.choice(types)
    
    position = random.uniform(0, 100)
    
    if type_choisi == "boulon_manquant":
        gravite = "moyen"
    elif type_choisi == "signalisation_defaillante":
        gravite = "critique"
    else:  
        gravite = "élevé"
    
    anomalie = {
        "type": type_choisi,
        "position": round(position, 3),
        "gravite": gravite
    }
    
    return anomalie

def generer_donnees_ufm160(debut: datetime, duree_heures: float, nom_fichier: str) -> None:

    
    timestamps = generer_timestamps(debut, duree_heures)
    positions = generer_position_pk(timestamps)
    
    os.makedirs("data/raw", exist_ok=True)
    
    fichier = open(nom_fichier, 'w', newline='', encoding='utf-8')
    writer = csv.writer(fichier)
    
    writer.writerow(['timestamp', 'pk_position', 'vitesse', 'hauteur_catenaire', 
                    'deport_catenaire', 'ecartement_voie', 'defaut_type', 'defaut_position'])
    
    for i in range(len(timestamps)):
        timestamp = timestamps[i]
        pk = positions[i]
        vitesse = VITESSE_TRAIN
        hauteur = generer_hauteur_catenaire(pk)
        deport = round(random.uniform(-0.2, 0.2), 2)
        ecartement = round(random.uniform(1430, 1440), 1)
        
        if random.random() < TAUX_ANOMALIES:
            anomalie = generer_anomalie()
            defaut_type = anomalie['type']
            defaut_position = anomalie['position']
        else:
            defaut_type = ''
            defaut_position = ''
        
        writer.writerow([
            timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5],
            round(pk, 3),
            vitesse,
            hauteur,
            deport,
            ecartement,
            defaut_type,
            defaut_position
        ])
    
    fichier.close()
    print(f"Fichier cree : {nom_fichier}")


if __name__ == "__main__":
    generer_donnees_ufm160(
        debut=datetime(2024, 1, 15, 8, 0),
        duree_heures=0.1,
        nom_fichier="data/raw/mesures_ufm160.csv"
    )