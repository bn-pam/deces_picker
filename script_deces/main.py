from script_deces import extract_last_file
from pipeline_deces import pipeline
from config import DOWNLOAD_DIR


# A revoir pour pouvoir lancer un pipeline pour chaque fichier téléchargé
def main():
    full_url_matching, file_url_name = extract_last_file()  # extraire le dernier fichier txt de la page web en récupérant le lien et le nom du fichier
    FILE = file_url_name  # extraire le nom du fichier
    FILE_PATH = DOWNLOAD_DIR + '/' + FILE  # Chemin du fichier à traiter
    pipeline(FILE, FILE_PATH) # traiter le(s) fichier(s) txt (par défaut c'est le fichier m12.txt)

if __name__ == "__main__":
    main()

# Remarques
#Il reste à variabiliser les paramètres des fichiers téléchargés :
#Le dernier fichier téléchargé doit se renseigner dans le .env pour être traité