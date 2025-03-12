## Projet ETL, source 1 : Récupération de fichiers mensuel des décès, avec beautifulsoup

### --- choix de la solution de scraping ---

| Critère          | BeautifulSoup                         | Scrapy                                   | Selenium                               |
|-----------------|------------------------------------|----------------------------------------|----------------------------------------|
| **Type**        | Parsing HTML/XML                   | Framework de scraping                  | Automatisation navigateur (WebDriver) |
| **Utilisation principale** | Extraction de données simples depuis du HTML statique | Scraping avancé, avec gestion d’URLs et pipelines | Interaction avec des pages dynamiques (JavaScript, formulaires, etc.) |
| **Performance** | Rapide pour du HTML statique      | Très performant pour du scraping à grande échelle | Lourd et lent (dû à l'exécution d'un navigateur) |
| **Facilité d'utilisation** | Facile, syntaxe simple | Complexe mais puissant | Facile à utiliser mais demande plus de ressources |
| **Gestion JavaScript** | ❌ (Ne supporte pas JS) | ❌ (Ne supporte pas JS nativement) | ✅ (Exécute le JS via le navigateur) |
| **Multithreading / Async** | ❌ (Non natif) | ✅ (Asynchrone avec Twisted) | ❌ (Non adapté au multi-threading) |
| **Utilisation des proxies** | ✅ (Mais manuel) | ✅ (Facile à intégrer) | ✅ (Mais consomme plus de ressources) |
| **Cas d’usage idéal** | Scraping simple de pages statiques | Scraping de gros volumes, crawling de sites | Scraping de sites interactifs nécessitant du JS |
| **Exemples d'utilisation** | Extraire des titres d’articles | Scraper un e-commerce en profondeur | Récupérer des infos d’une page nécessitant une connexion |
| **Consommation des ressources** | Faible | Moyenne | Élevée (démarrage de navigateur) |

Pour ce projet mon choix s'est orienté vers beautifulsoup pour sa simplicité et sa rapidité.

### --- Inventaire des fichiers ---
* ```pipeline_deces.py``` est le programme qui va lire et transformer les données en csv
* ```script_deces.py``` contient le scraper qui va récupérer le fichier txt des décès s'il n'existe pas déjà dans le fichier ```processed_files.txt```
* ```processed_files.txt``` contient la liste des fichiers déjà traités
* ```deces.csv``` contient les données transformées en csv
* ```downloaded_files``` contient les fichiers téléchargés au format .txt
* 

### --- Scraping page décès---
Le scraping contenu dans ```script_deces.py``` de ce projet se déroule de la manière suivante :

L'url principale de téléchargement des fichiers mensuels de décès est ouverte et la page ouverte est inspectée,
et pour le premier lien de fichier le programme :

> * trouve toutes les urls de fichiers des décès grâce à son xpath,
> * vérifie s'il est déjà présent dans la liste des fichiers traités,
> * si non, récupère le contenu du fichier txt,
> * écrit le contenu du fichier dans le dossier ```downloaded_files```,
> * écrit le nom du fichier dans le fichier ```processed_files.txt```.

### --- Pipeline ---
Le pipeline contenu dans ```pipeline_deces.py``` dans ce projet se déroule de la manière suivante :
le fichier ```deces.txt``` est lu ligne par ligne, où une ligne correspond aux données d'un 
décès, et pour chacun le programme :

> * récupère les informations (noms et prénoms, etc.) grâce à des expressions régulières,
> * nettoie les données (suppression des caractères spéciaux, etc.),
> * transforme les données en un dictionnaire,
> * écrit le dictionnaire dans un fichier csv. ```deces.json```,
> * écrit le dictionnaire dans un fichier json. ```deces.csv```,

| Noms      | Prenoms           | Sexe  |Date_naiss| CP_naiss | commune_naissance | Pays_naiss|Date_deces | Lieu_deces |
|-----------|-------------------|-------|----------|----------|-------------------|------------|------|------|
| HUCHARD   | JEAN CLAUDE ANDRE | 1     | 19410420 |01053| BOURG-EN-BRESSE   |France|20240816|

### TODO :
> - ✅ script de scraping du (des) fichier(s) décès
> - ✅ pipeline pour récupérer les données brutes, et transformer les données nettoyées en .json
> - ❌ pipeline ou script pour nettoyer les données brutes et les transformer en données structurées
> - ✅ pipeline ou script pour créer une BDD {à tester}
> - ❌ script d'insertion des données dans la base de données {à tester}
> - 🔄 requirements.txt à créer ($ pip freeze > requirements.txt)
> - 🔄 README.md à compléter
> - ❌ tests unitaires à écrire
> - ❌ tests fonctionnels à écrire
> - ❌ tests d'intégration à écrire
> - ❌ tests de performance à écrire
> - ❌ améliorer le pipeline

### --- Schéma de la table (projet) ---


| Nom du champ  | Type SQL                                                                       | Détails                              | 
|---------------|--------------------------------------------------------------------------------|--------------------------------------|
| id            | 	SERIAL (PostgreSQL) / INT AUTO_INCREMENT (MySQL) / IDENTITY(1,1) (SQL Server) | 	Clé primaire unique auto-incrémentée |
| Noms          | 	VARCHAR(255)                                                                  | 	Noms de famille                     |
| Prénoms       | 	VARCHAR(255)                                                                  | 	Prénoms                             |
| Sexe          | 	INTEGER (1)                                                                   | 	1 pour masculin 2 pour féminin      |
| Date_naiss    | 	Date                                                                          | 	Date de naissance                   |
| CP_naiss      | 	VARCHAR(255)                                                                  | 	Code postal de naissance            |
| commune_naiss | 	VARCHAR(255)                                                                  | 	Commune de naissance                |
| Pays_naiss    | 	VARCHAR(255)                                                                  | 	Pays de naissance                   |
| Date_deces    | 	Date                                                                          | 	Date de décès                       |
| Lieu_deces    | 	VARCHAR(255)                                                                  | 	Lieu de décès                       |   
| Acte_deces    | 	Date                                                                          | 	Acte de décès si applicable         |
