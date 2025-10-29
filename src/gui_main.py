import sys
import csv
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QTextEdit, QScrollArea,
                             QDialog, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import data_generator

class DialogAnomalies(QDialog):
    def __init__(self, type_anomalie, positions, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Positions - {type_anomalie}")
        self.setGeometry(200, 200, 600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        
        titre = QLabel(f"Localisation des anomalies: {type_anomalie}")
        titre.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titre)
        
        info = QLabel(f"Total: {len(positions)} anomalies detectees")
        info.setFont(QFont("Arial", 11))
        layout.addWidget(info)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Position PK (m)", "Distance depuis debut (km)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self.table.setRowCount(len(positions))
        for row, pk in enumerate(sorted(positions)):
            self.table.setItem(row, 0, QTableWidgetItem(f"{pk:.2f}"))
            km = pk / 1000
            self.table.setItem(row, 1, QTableWidgetItem(f"{km:.3f}"))
        
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

class RailCheckApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RailCheck Mini - Eurailscout")
        self.setGeometry(100, 100, 1200, 800)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.onglet_generation = QWidget()
        self.onglet_analyse = QWidget()
        self.onglet_visualisation = QWidget()
        
        self.tabs.addTab(self.onglet_generation, "Generation")
        self.tabs.addTab(self.onglet_analyse, "Analyse")
        self.tabs.addTab(self.onglet_visualisation, "Visualisation")
        
        self.setup_onglet_generation()
        self.setup_onglet_analyse()
        self.setup_onglet_visualisation()
    
    def setup_onglet_generation(self):
        layout = QVBoxLayout()
        
        titre = QLabel("Generation de donnees UFM 160")
        titre.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(titre)
        
        self.btn_generer = QPushButton("Generer donnees")
        self.btn_generer.setFixedSize(200, 50)
        self.btn_generer.clicked.connect(self.generer_donnees)
        layout.addWidget(self.btn_generer)
        
        self.label_resultat = QLabel("")
        self.label_resultat.setFont(QFont("Arial", 14))
        layout.addWidget(self.label_resultat)
        
        self.log_generation = QTextEdit()
        self.log_generation.setReadOnly(True)
        layout.addWidget(self.log_generation)
        
        layout.addStretch()
        self.onglet_generation.setLayout(layout)
    
    def setup_onglet_analyse(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        titre = QLabel("Analyse des KPIs")
        titre.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(titre)
        
        self.btn_analyser = QPushButton("Analyser donnees")
        self.btn_analyser.setFixedSize(200, 50)
        self.btn_analyser.clicked.connect(self.analyser_donnees)
        layout.addWidget(self.btn_analyser)
        
        # KPIs en cartes simples
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(10)
        
        # Distance
        distance_widget = QWidget()
        distance_widget.setStyleSheet("background-color: #e8f5e9; border: 1px solid #4caf50; border-radius: 5px;")
        distance_layout = QVBoxLayout()
        distance_titre = QLabel("Distance inspectee")
        distance_titre.setFont(QFont("Arial", 11))
        distance_titre.setStyleSheet("color: #2e7d32; font-weight: bold;")
        self.label_distance = QLabel("-")
        self.label_distance.setFont(QFont("Arial", 24, QFont.Bold))
        self.label_distance.setStyleSheet("color: #1b5e20;")
        distance_layout.addWidget(distance_titre)
        distance_layout.addWidget(self.label_distance)
        distance_widget.setLayout(distance_layout)
        kpi_layout.addWidget(distance_widget)
        
        # Conformite
        conformite_widget = QWidget()
        conformite_widget.setStyleSheet("background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 5px;")
        conformite_layout = QVBoxLayout()
        conformite_titre = QLabel("Taux conformite")
        conformite_titre.setFont(QFont("Arial", 11))
        conformite_titre.setStyleSheet("color: #1976d2; font-weight: bold;")
        self.label_conformite = QLabel("-")
        self.label_conformite.setFont(QFont("Arial", 24, QFont.Bold))
        self.label_conformite.setStyleSheet("color: #0d47a1;")
        conformite_layout.addWidget(conformite_titre)
        conformite_layout.addWidget(self.label_conformite)
        conformite_widget.setLayout(conformite_layout)
        kpi_layout.addWidget(conformite_widget)
        
        # Anomalies
        anomalies_widget = QWidget()
        anomalies_widget.setStyleSheet("background-color: #ffebee; border: 1px solid #f44336; border-radius: 5px;")
        anomalies_layout = QVBoxLayout()
        anomalies_titre = QLabel("Anomalies detectees")
        anomalies_titre.setFont(QFont("Arial", 11))
        anomalies_titre.setStyleSheet("color: #c62828; font-weight: bold;")
        self.label_anomalies = QLabel("-")
        self.label_anomalies.setFont(QFont("Arial", 24, QFont.Bold))
        self.label_anomalies.setStyleSheet("color: #b71c1c;")
        anomalies_layout.addWidget(anomalies_titre)
        anomalies_layout.addWidget(self.label_anomalies)
        anomalies_widget.setLayout(anomalies_layout)
        kpi_layout.addWidget(anomalies_widget)
        
        layout.addLayout(kpi_layout)
        
        # Tableau
        table_titre = QLabel("Detail des anomalies:")
        table_titre.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(table_titre)
        
        hint = QLabel("Double-cliquez sur une ligne pour voir toutes les positions")
        hint.setFont(QFont("Arial", 9))
        hint.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(hint)
        
        self.table_anomalies = QTableWidget()
        self.table_anomalies.setColumnCount(2)
        self.table_anomalies.setHorizontalHeaderLabels(["Type anomalie", "Nombre"])
        self.table_anomalies.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_anomalies.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_anomalies.doubleClicked.connect(self.voir_positions_anomalie)
        layout.addWidget(self.table_anomalies)
        
        # Stocker les positions pour chaque type d'anomalie
        self.positions_anomalies = {}
        
        layout.addStretch()
        self.onglet_analyse.setLayout(layout)
    
    def setup_onglet_visualisation(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        titre = QLabel("Visualisations")
        titre.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(titre)
        
        self.btn_visualiser = QPushButton("Generer graphiques")
        self.btn_visualiser.setFixedSize(200, 50)
        self.btn_visualiser.clicked.connect(self.visualiser_donnees)
        layout.addWidget(self.btn_visualiser)
        
        # Zone de scroll pour les graphiques
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(15)
        scroll_widget.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.onglet_visualisation.setLayout(layout)
    
    def generer_donnees(self):
        self.log_generation.append("Debut generation...")
        
        data_generator.generer_donnees_ufm160(
            debut=datetime(2024, 1, 15, 8, 0),
            duree_heures=0.1,
            nom_fichier="data/raw/mesures_ufm160.csv"
        )
        
        fichier = open('data/raw/mesures_ufm160.csv', 'r', encoding='utf-8')
        reader = csv.DictReader(fichier)
        
        total = 0
        for ligne in reader:
            total = total + 1
        
        fichier.close()
        
        self.log_generation.append(f"Fichier genere : {total} lignes")
        self.label_resultat.setText(f"Generation terminee : {total} mesures")
    
    def analyser_donnees(self):
        fichier = open('data/raw/mesures_ufm160.csv', 'r', encoding='utf-8')
        reader = csv.DictReader(fichier)
        
        total = 0
        anomalies = 0
        pk_min = 999999
        pk_max = 0
        compteur_anomalies = {}
        self.positions_anomalies = {}
        
        for ligne in reader:
            total = total + 1
            
            pk = float(ligne['pk_position'])
            if pk < pk_min:
                pk_min = pk
            if pk > pk_max:
                pk_max = pk
            
            if ligne['defaut_type']:
                anomalies = anomalies + 1
                type_anomalie = ligne['defaut_type']
                pk_anomalie = pk
                
                if type_anomalie in compteur_anomalies:
                    compteur_anomalies[type_anomalie] = compteur_anomalies[type_anomalie] + 1
                else:
                    compteur_anomalies[type_anomalie] = 1
                    self.positions_anomalies[type_anomalie] = []
                
                self.positions_anomalies[type_anomalie].append(round(pk_anomalie, 2))
        
        fichier.close()
        
        distance = (pk_max - pk_min) / 1000
        conformite = (total - anomalies) / total * 100
        
        self.label_distance.setText(f"{round(distance, 2)} km")
        self.label_conformite.setText(f"{round(conformite, 2)}%")
        self.label_anomalies.setText(f"{anomalies}")
        
        self.table_anomalies.setRowCount(len(compteur_anomalies))
        row = 0
        for type_anomalie, count in compteur_anomalies.items():
            self.table_anomalies.setItem(row, 0, QTableWidgetItem(type_anomalie))
            self.table_anomalies.setItem(row, 1, QTableWidgetItem(str(count)))
            row = row + 1
    
    def voir_positions_anomalie(self, index):
        row = index.row()
        type_anomalie = self.table_anomalies.item(row, 0).text()
        
        if type_anomalie in self.positions_anomalies:
            positions = self.positions_anomalies[type_anomalie]
            dialog = DialogAnomalies(type_anomalie, positions, self)
            dialog.exec_()
    
    def visualiser_donnees(self):
        fichier = open('data/raw/mesures_ufm160.csv', 'r', encoding='utf-8')
        reader = csv.DictReader(fichier)
        
        hauteurs = []
        positions = []
        compteur_anomalies = {}
        
        count = 0
        for ligne in reader:
            if count < 500:
                hauteurs.append(float(ligne['hauteur_catenaire']))
                positions.append(float(ligne['pk_position']))
            
            if ligne['defaut_type']:
                type_anomalie = ligne['defaut_type']
                if type_anomalie in compteur_anomalies:
                    compteur_anomalies[type_anomalie] = compteur_anomalies[type_anomalie] + 1
                else:
                    compteur_anomalies[type_anomalie] = 1
            
            count = count + 1
        
        fichier.close()
        
        # Nettoyer les anciens graphiques
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Graphique 1: Hauteur catenaire
        titre1 = QLabel("Evolution hauteur catenaire (norme EN 13848)")
        titre1.setFont(QFont("Arial", 13, QFont.Bold))
        titre1.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 3px;")
        self.scroll_layout.addWidget(titre1)
        
        fig1, ax1 = plt.subplots(figsize=(11, 4.5))
        ax1.plot(positions, hauteurs, linewidth=1, color='#2196f3', alpha=0.8)
        ax1.axhline(y=5.5, color='#4caf50', linestyle='--', linewidth=1.5, label='Hauteur standard (5.5m)')
        ax1.axhline(y=4.0, color='#f44336', linestyle='--', linewidth=1, alpha=0.6, label='Limite min (4.0m)')
        ax1.axhline(y=7.0, color='#f44336', linestyle='--', linewidth=1, alpha=0.6, label='Limite max (7.0m)')
        ax1.fill_between(positions, 4.0, 7.0, alpha=0.05, color='#4caf50')
        ax1.set_xlabel('Position (m)', fontsize=11)
        ax1.set_ylabel('Hauteur catenaire (m)', fontsize=11)
        ax1.set_title('Mesures UFM 160', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle=':')
        ax1.legend(fontsize=9)
        plt.tight_layout()
        plt.savefig('data/graph_hauteurs.png', dpi=100, bbox_inches='tight')
        plt.close(fig1)
        
        label_hauteurs = QLabel()
        pixmap_hauteurs = QPixmap('data/graph_hauteurs.png')
        label_hauteurs.setPixmap(pixmap_hauteurs)
        label_hauteurs.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        self.scroll_layout.addWidget(label_hauteurs)
        
        # Graphique 2: Anomalies
        titre2 = QLabel("Repartition des anomalies detectees")
        titre2.setFont(QFont("Arial", 13, QFont.Bold))
        titre2.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 3px;")
        self.scroll_layout.addWidget(titre2)
        
        fig2, ax2 = plt.subplots(figsize=(11, 4.5))
        types = list(compteur_anomalies.keys())
        counts = list(compteur_anomalies.values())
        colors = ['#f44336', '#ff9800', '#ffc107']
        bars = ax2.bar(types, counts, color=colors, edgecolor='#333', linewidth=1.2, alpha=0.85)
        ax2.set_xlabel('Type anomalie', fontsize=11)
        ax2.set_ylabel('Nombre', fontsize=11)
        ax2.set_title('Inspection ferroviaire', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle=':', axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('data/graph_anomalies.png', dpi=100, bbox_inches='tight')
        plt.close(fig2)
        
        label_anomalies = QLabel()
        pixmap_anomalies = QPixmap('data/graph_anomalies.png')
        label_anomalies.setPixmap(pixmap_anomalies)
        label_anomalies.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        self.scroll_layout.addWidget(label_anomalies)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RailCheckApp()
    window.show()
    sys.exit(app.exec_())

