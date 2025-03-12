# URL de la page contenant les fichiers
URL='https://www.data.gouv.fr/fr/datasets/fichier-des-personnes-decedees/#/resources/' # URL de la page contenant les fichiers
FILE='deces-2025-m01.txt' # Nom du fichier téléchargé

# Pattern regex pour reconnaître les fichiers respectant ce pattern : "deces-YYYY-mMM"
PATTERN='deces-(\d{4})-m(0[1-9]|1[0-2])'

# Dossiers et fichiers de suivi
DOWNLOAD_DIR='downloaded_files'
PROCESSED_DIR='processed_files'

# Dossier de téléchargement
HISTORY_FILE="downloaded_files.txt" # Fichier d'historique des fichiers téléchargés
CHUNK_SIZE=1024 # Taille des chunks pour le téléchargement