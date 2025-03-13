import requests
from bs4 import BeautifulSoup
import os
import re
from dotenv import load_dotenv
from config import DOWNLOAD_DIR, HISTORY_FILE, CHUNK_SIZE, URL, PATTERN
import logging

load_dotenv() # Charger les variables d'environnement
logging.basicConfig(level=logging.INFO) # Configurer le logging pour afficher les messages INFO

# URL de la page contenant les fichiers
URL = URL

# Pattern regex pour reconnaître les fichiers "deces-YYYY-mMM"
PATTERN = PATTERN

# Dossiers et fichiers de suivi
DOWNLOAD_DIR = DOWNLOAD_DIR # Dossier de téléchargement
HISTORY_FILE = HISTORY_FILE # Fichier d'historisation des fichiers téléchargés
CHUNK_SIZE = CHUNK_SIZE  # Assure que c'est un nombre entier

# Créer le dossier de téléchargement s'il n'existe pas
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def read_downloaded_files():
    """Lit les fichiers déjà traités et historisés."""
    if not os.path.exists(HISTORY_FILE): # Si le fichier n'existe pas,
        return set() # retourner un ensemble vide

    with open(HISTORY_FILE, "r", encoding="utf-8") as file: # ouvrir le fichier d'historisation en mode lecture
        return set(file.read().splitlines()) # retourner un ensemble de lignes lues

def add_to_downloaded_files(url): # Ajouter une URL au fichier de suivi
    """Ajoute une URL au fichier d'historique des fichiers téléchargés."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as file: # ouvrir le fichier d'historisation en mode ajout
        file.write(url + "\n") # écrire l'URL suivie d'un retour à la ligne

def download_file(url, file_name): # Télécharger un fichier et l'enregistrer localement
    """Télécharge un fichier et l'enregistre localement."""
    response = requests.get(url, stream=True) # effectuer une requête GET en mode streaming
    file_path = os.path.join(DOWNLOAD_DIR, file_name) # définir le chemin du fichier à télécharger

    if response.status_code == 200: # Si la requête est un succès
        with open(file_path, "wb") as file: # ouvrir le fichier en mode écriture binaire
            for chunk in response.iter_content(CHUNK_SIZE): # itérer sur les chunks de 1024 octets
                file.write(chunk) # écrire chaque chunk dans le fichier
        logging.info(f"✅ Téléchargé : {file_name}") # afficher un message de succès
    else:
        logging.info(f"❌ Erreur {response.status_code} pour {url}") # afficher un message d'erreur

def extract_data(): # Fonction principale pour scraper la page et télécharger les fichiers
    """Scrape la page, télécharge les nouveaux fichiers et met à jour l'historique."""
    # Lire les fichiers déjà traités
    downloaded_files = read_downloaded_files()

    # Télécharger et parser la page HTML
    response = requests.get(URL) # effectuer une requête GET sur l'URL
    soup = BeautifulSoup(response.text, "html.parser") # parser le contenu de la réponse

    # Extraire tous les liens
    for link in soup.find_all("a", href=True): # trouver tous les liens avec une URL
        file_url = link["href"] # extraire l'URL du lien
        if re.search(PATTERN, file_url):  # Vérifier si le lien correspond au pattern
            full_url = file_url if file_url.startswith("http") else f"https://www.data.gouv.fr{file_url}" # construire l'URL complète

            if full_url in downloaded_files: # Vérifier si le fichier a déjà été traité
                logging.info(f"🔄 Déjà téléchargé : {full_url}") # afficher un message de statut
            else:
                file_name = file_url.split("/")[-1]  # Extraire le nom du fichier
                download_file(full_url, file_name) # Télécharger le fichier
                add_to_downloaded_files(full_url) # Ajouter l'URL au fichier d'historique

if __name__ == "__main__":
    extract_data() # Appeler la fonction principale
