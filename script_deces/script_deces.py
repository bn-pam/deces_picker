import requests
from bs4 import BeautifulSoup
import os
import re
from dotenv import load_dotenv
from config import DOWNLOAD_DIR, HISTORY_FILE, CHUNK_SIZE, URL, PATTERN
import logging, datetime

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
current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month

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

def get_previous_month_and_year(current_year=current_year, current_month=current_month):
    """
    Calcule le mois et l'année précédents.

    Args:
        current_year (int): L'année actuelle.
        current_month (int): Le mois actuel (1 pour Janvier, 12 pour Décembre).

    Returns:
        tuple: Un tuple contenant l'année et le mois précédents (année, mois).
               Retourne (None, None) si les entrées sont invalides.
    """
    if not (1 <= current_month <= 12):
        return None, None  # Mois invalide

    if current_month == 1:  # Si Janvier
        previous_month = 12 # Mois précédent est Décembre
        year = current_year - 1 # Année précédente
    else:
        previous_month = current_month - 1
        year = current_year

    return year, previous_month

def check_file_matches_previous_month(filename, current_year=current_year, current_month=current_month):
    """
    Vérifie si le nom de fichier correspond au mois précédent.

    Args:
        filename (str): Le nom du fichier à vérifier.
        current_year (int): L'année actuelle
        current_month (int): Le mois actuel.

    Returns:
        bool: True si le fichier correspond au mois précédent, False sinon.
    """

    year, previous_month = get_previous_month_and_year(current_year, current_month)

    if year is None: #si erreur dans l'année
        return False

    expected_filename = f"deces-{year}-{previous_month:02d}.txt" #On veut 01, 02 etc.
    #expected_filename = "deces-{}-{:02d}.txt".format(previous_year, previous_month) # Alternative
    return filename == expected_filename


def extract_first_file_from_page(full_url_matching): # Fonction principale pour scraper la page et télécharger les fichiers
    """Scrape la page, télécharge les nouveaux fichiers et met à jour l'historique."""
    # Lire les fichiers déjà traités
    downloaded_files = read_downloaded_files()

    # Télécharger et parser la page HTML
    response = requests.get(URL) # effectuer une requête GET sur l'URL
    full_url = full_url_matching

    if full_url in downloaded_files: # Vérifier si le fichier a déjà été traité
        logging.info(f"🔄 Déjà téléchargé : {full_url}") # afficher un message de statut
    else:
        file_name = full_url_matching.split("/")[-1]  # Extraire le nom du fichier
        download_file(full_url, file_name) # Télécharger le fichier
        add_to_downloaded_files(full_url) # Ajouter l'URL au fichier d'historique


def find_first_matching_file(url=URL, pattern=PATTERN, downloaded_files=DOWNLOAD_DIR):
    """
    Trouve le premier lien correspondant au pattern et non déjà téléchargé.

    Args:
        url (str): URL de la page.
        pattern (str): Pattern regex.
        downloaded_files (set): Ensemble des fichiers déjà téléchargés.

    Returns:
        str: L'URL complète du premier fichier correspondant, ou None si aucun.
    """
    try:
        response = requests.get(url) # Effectuer une requête GET sur l'URL
        response.raise_for_status() # Lever une exception pour les codes d'erreur HTTP
        soup = BeautifulSoup(response.text, "html.parser") # Parser le contenu de la réponse

        for link in soup.find_all("a", href=True): # Trouver tous les liens avec une URL
            file_url = link["href"] # Extraire l'URL du lien
            if re.search(pattern, file_url): # Vérifier si le lien correspond au pattern
                full_url = ( # Construire l'URL complète
                    file_url
                    if file_url.startswith("http")
                    else f"https://www.data.gouv.fr{file_url}"
                )
                if full_url not in downloaded_files: # Vérifier si le fichier n'a pas déjà été téléchargé
                    return full_url, file_url  # Retourne l'url du fichier dès qu'on trouve le premier

    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur réseau: {e}")
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")

    return None  # Aucun fichier trouvé

def first_file_matching_date(url=URL, pattern=PATTERN, downloaded_files=DOWNLOAD_DIR):
    full_url, file_url = find_first_matching_file() # Trouver le premier fichier correspondant (URL complète et nom du fichier)
    if full_url is not None: # Si un fichier correspondant est trouvé
        filename = file_url.split("/")[-1] # Extraire le nom du fichier seulement
        check = check_file_matches_previous_month(filename, current_year, current_month) # Exécuter la fonction de vérification sur le nom du fichier
        if check is not None: # Si le fichier correspond au mois précédent
            return full_url # Retourner l'URL complète et le nom du fichier
        else:
            logging.info(f"Le fichier '{full_url}' NE correspond PAS au mois précédent.") # Afficher un message d'information


def extract_last_file():
    full_url_matching = first_file_matching_date() # Trouver le premier fichier correspondant au mois précédent
    file_url_name = full_url_matching.split("/")[-1] # Extraire le nom du fichier seulement
    if full_url_matching is None: # Si aucun fichier correspondant n'est trouvé
        logging.info("Aucun fichier correspondant au mois précédent n'a été trouvé.")
        return
    else:
        logging.info(f"Le fichier '{file_url_name}' correspond au mois précédent.") # Afficher un message d'information
        extract_first_file_from_page(full_url_matching) # Extraire le premier fichier correspondant
        logging.info(f"Le fichier '{file_url_name}' a été téléchargé avec succès.") # Afficher un message de succès
        return full_url_matching, file_url_name

def extract_all_files_from_page(): # Fonction principale pour scraper la page et télécharger les fichiers
    """Scrape la page, télécharge les nouveaux fichiers et met à jour l'historique."""
    # Lire les fichiers déjà traités
    downloaded_files = read_downloaded_files()

    # Télécharger et parser la page HTML
    response = requests.get(URL) # effectuer une requête GET sur l'URL
    soup = BeautifulSoup(response.text, "html.parser") # parser le contenu de la réponse

    # Extraire tous les liens remplacer les deux prochaines lignes par ces deux lignes :
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
