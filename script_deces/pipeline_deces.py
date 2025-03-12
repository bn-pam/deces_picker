import re
import json
import pandas as pd
from dotenv import load_dotenv
from config import FILE, DOWNLOAD_DIR, PROCESSED_DIR

load_dotenv()
FILE = FILE # Nom du fichier à traiter
DOWNLOAD_DIR = DOWNLOAD_DIR # Dossier de téléchargement
FILE_PATH = DOWNLOAD_DIR + '/' + FILE # Chemin du fichier à traiter
PROCESSED_DIR = PROCESSED_DIR


# Une regex qui capture tous les champs principaux
pattern = re.compile(
    r"""
    (?P<nom>[A-Z- ']+)?\*                                                        # Noms (lettres, espaces, tirets, apostrophes), excluant l'astérisque, optionnel 
    (?P<prenoms>[A-Z- ']+)?/                                                     # Prénoms (lettres, espaces, tirets, apostrophes) excluant Délimiteur, optionnel
    \s*                                                                          # Autoriser plusieurs espaces avant le sexe
    (?P<sexe>[12])                                                               # Sexe (1 ou 2)
    \s*                                                                          # Autoriser plusieurs espaces avant la date de naissance
    (?P<date_naissance>((18|19|20)\d{2})(0[0-9]|1[0-2])(0[0-9]|[12][0-9]|3[01])) # Date de naissance (AAAAMMJJ)
    (?P<CP_naissance>(([A-Z\d]){5}))                                             # Code postal naissance (5 chiffres ou lettres)
    ((?P<pays_naissance>(?=\s*99\d{3}\s)[()A-ZÉÈÀÇa-z- ']+)?)                    # Pays de naissance, optionnel, après un espace ou une virgule, seulement si le CP commence par 99
    \s*                                                                          # Autoriser plusieurs espaces avant la date de décès
    (?P<commune_naissance>(?!\s*99\d{3}\s)([()A-ZÉÈÀÇa-z- ',.°"/\d{2}]+?)(?=([A-Z\d]){5}))     # Commune de naissance (lettres, espaces, tirets, apostrophes, slashs, double quotes et 2 chiffres), précédé du code postal de naissance
    \s*                                                                                 # Autoriser plusieurs espaces avant la date de décès
    (?P<date_deces>((19|20)\d{2})(0[0-9]|1[0-2])(0[0-9]|[12][0-9]|3[01]))               # Date de décès (AAAA-MM-JJ) avec uniquement des dates valides
    (?P<CP_deces>(?<=((19|20)\d{2})(0[0-9]|1[0-2])(0[0-9]|[12][0-9]|3[01]))(([A-Z\d]){5})) # Code postal de décès (5 chiffres ou lettre), précéde de la date de décès
    (?P<acte_deces>(\d{1,5}))?                                                               # Numéro d'acte de décès (1 à 5 chiffres), précédé du code postal de décès
    """,
    re.VERBOSE
)

def extract_data_from_file():
    data_list = []  # initialisation de la liste des données
    with open(file=FILE_PATH, mode="r", encoding="utf-8") as fichier: # ouvrir et lire le fichier
        for ligne in fichier: # pour chaque ligne dans le fichier
            ligne = re.sub(r'\t', ' ', ligne)  # Remplace les tabulations par des espaces
            ligne = re.sub(r'\s+', ' ', ligne)  # Remplace plusieurs espaces ou tabulations par un espace unique
            match = pattern.match(ligne) # appliquer la regex sur chaque ligne

            if match:  # si la ligne correspond au pattern
                cp_naissance = match.group('CP_naissance') # extraire le code postal de naissance
                commune_naissance = match.group('commune_naissance') # extraire la commune de naissance

            # cas particulier si le pays n'est pas la france
                if cp_naissance.startswith(("99", "97")):  # Si le CP commence par 99 ou 97, on attend un pays de naissance étranger sauf exceptions
                    if not commune_naissance:  # Si la commune est vide,
                        commune_naissance = "null"
                        pays_naissance = match.group('pays_naissance') if match.group('pays_naissance') else "null"
                    else : # Si la commune n'est pas vide,
                        commune_split = commune_naissance.split() # Séparer les mots de la commune dans une liste
                        if len(commune_split) > 1:  # Si plusieurs mots,
                            if commune_split[-2].upper() == "LA":  # Vérifier si l'avant-dernier mot est "LA" exemple: LA REUNION
                                pays_naissance = " ".join(commune_split[-2:])  # Pays = "LA + dernier mot"
                                commune_naissance = " ".join(commune_split[:-2])  # Retirer les deux derniers mots
                            elif commune_split[-2].upper() == "D'":  # Vérifier si l'avant-dernier mot est "D'" exemple: COTE D'IVOIRE
                                pays_naissance = " ".join(commune_split[-3:])  # Pays = "D' + dernier mot + avant-dernier mot"
                                commune_naissance = " ".join(commune_split[:-3])  # Retirer les trois derniers mots
                                print(commune_naissance, pays_naissance)
                            else:
                                pays_naissance = commune_split[-1]  # On suppose que le dernier mot est le pays
                                commune_naissance = " ".join(commune_split[:-1])  # Retirer le pays de la commune
                        else: # Si un seul mot dans la liste commune,
                            pays_naissance = commune_naissance  # Si un seul mot dans la liste commune, le pays est la commune
                            commune_naissance = "null"  # et il n'y a pas de commune
                if cp_naissance == "99312":  # Cas particulier pour le code 99312
                    match_congo = re.compile(r"""
                    (?P<commune_naissance>(?!\s*99\d{3}\s)([()A-ZÉÈÀÇa-z- ',.°"/\d{2}]+?)(?=\W*CONGO\W*))
                    """,re.VERBOSE).match(commune_naissance)  # Chercher le mot CONGO dans la commune
                    pays_naissance = "RDC CONGO"  # Le pays est la RDC CONGO
                    commune_naissance = match_congo.group('commune_naissance') if match_congo else "Null"  # Extraire la commune si pas vide, sinon Null

                else : # autre cas : Si le CP ne commence pas par 99
                    if not cp_naissance.startswith(("99", "97")):  # Si le CP ne commence par 99 ou 97
                        pays_naissance = "FRANCE" # Par défaut, le pays est la France (pour tous les CP ne commençant pas par 99 ou )
                        commune_naissance = commune_naissance.strip()  # Retirer les espaces en début et fin de la commune française

                data = { # stocker les données dans un dictionnaire
                    "nom": match.group('nom') if match.group('nom') else "Null",
                    "prénoms": match.group('prenoms') if match.group('prenoms') else "Null",
                    "sexe": match.group('sexe'),
                    "date_naissance": match.group('date_naissance'),
                    "CP_naissance": match.group('CP_naissance'),
                    "commune_naissance": commune_naissance, #if commune_naissance else "Null",
                    "pays_naissance": pays_naissance, #if pays_naissance else "Null",
                    "date_deces": match.group('date_deces'),
                    "CP_deces": match.group('CP_deces'),
                    "acte_deces": match.group('acte_deces')
                }
                data_list.append(data) # ajouter les données à la liste des données

                #print("ligne bien copiée:", ligne)  # afficher la ligne réécrite
            else:
                print(f"⚠️ Ligne non prise en charge : {ligne}") # afficher un message si la ligne ne correspond pas au pattern
        #print(f"Nombre de lignes prises en charge : {len(data_list)}") # afficher le nombre de lignes traitées
        return data_list # retourner la liste des données sous forme de liste

# Fonction pour télécharger les données dans un fichier JSON
def download_datas(data_list, source_file_name): # fonction pour télécharger les données dans un fichier JSON
    """écrit les données et les enregistre localement dans un fichier JSON."""
    # Créer un nom de fichier JSON dynamique basé sur le nom du fichier texte
    json_file_name = f"{source_file_name.split('.')[0]}.json"  # Enlève l'extension du fichier txt et ajoute .json
    json_file_path = DOWNLOAD_DIR + '/' + json_file_name  # définir le chemin du fichier JSON
    with open(json_file_path, "w", encoding="utf-8") as f:  # ouvrir le fichier en mode texte
        json.dump(data_list, f, ensure_ascii=False, indent=4)  # écrire les données au format JSON
    print(f"✅ Téléchargé : {json_file_path}")  # afficher un message de succès
    return json_file_path  # retourner le chemin du fichier JSON

def count_lines(data_list, source_file_path):
    count_data = len(data_list) # Compter le nombre de lignes traitées
    with open(source_file_path, "r", encoding="utf-8") as file:
        count = sum(1 for line in file) # Compter le nombre de lignes dans le fichier source
        lines_omit = count - count_data # Calculer le nombre de lignes non prises en charge
        count_null = sum(1 for data in data_list if any(value is None or value == "null" for value in data.values()))
        print(f"Nombre de lignes dans le fichier source {source_file_path} : {count}")
        print(f"Nombre de lignes traitées : {count_data}")
        print(f"Nombre de lignes non prises en charge : {lines_omit}")
        print(f"nombre de lignes avec une valeur null : {count_null}")
        print(f"pourcentage non pris en charge: {lines_omit/count * 100:.2f}%")


def json_to_csv(json_data, csv_file_path):
    """
    Convertit un fichier JSON en fichier CSV.

    :param json_data: Données JSON sous forme de liste de dictionnaires.
    :param csv_file_path: Chemin du fichier CSV de sortie.
    """
    csv_file_path = csv_file_path.split('/')[-1].replace(".txt", ".csv")
    csv_file_path = DOWNLOAD_DIR + '/' + csv_file_path
    df = pd.DataFrame(json_data)
    df.to_csv(csv_file_path, index=False)
    print(f"✅ Converti en CSV : {csv_file_path}")


# Exemple d'utilisation
def pipeline():
    data_list = extract_data_from_file() # extraire les données du fichier source et les stocker dans une liste
    download_datas(data_list, FILE) # télécharger les données de la liste dans un fichier JSON et retourner le chemin du fichier
    count_lines(data_list, FILE_PATH) # compter les lignes dans les fichiers source et JSON, les lignes non prises en charge et les lignes avec des valeurs nulles
    json_to_csv(data_list, FILE_PATH) # convertir le fichier JSON en fichier CSV

if __name__ == "__main__":
    pipeline() # Appeler la fonction principale

# Remarques
# les codes INSEE sont interprétés comme des codes postaux
# >>> cas particuliers :
# codes 99XXX : naissance à l'étranger
# il y a plusieurs codes 99, chaque code correspond à une situation par ex :
# code 91352 : né en Algérie mais nat. Française