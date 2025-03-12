from script_deces import extract_data, read_downloaded_files, DOWNLOAD_DIR
from pipeline_deces import pipeline


# A revoir pour pouvoir lancer un pipeline pour chaque fichier téléchargé
def main():
    extract_data() # extraire le(s) fichier(s) txt de la page web
    pipeline() # traiter le(s) fichier(s) txt (par défaut c'est le fichier m12.txt)

if __name__ == "__main__":
    main()

# Remarques
#Il reste à variabiliser les paramètres des fichiers téléchargés :
#Le dernier fichier téléchargé doit se renseigner dans le .env pour être traité