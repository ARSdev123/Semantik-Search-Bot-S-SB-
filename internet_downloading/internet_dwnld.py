# Gestion des imports avec gestion d'erreurs
try:
    import yt_dlp
except ImportError:
    print("Erreur: yt-dlp non disponible")
    print("Installez-le avec: pip install yt-dlp")
    yt_dlp = None

def telecharger_video(url):
    """Télécharge une vidéo depuis une URL YouTube."""
    if yt_dlp is None:
        print("Erreur: yt-dlp non disponible")
        return False

    options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'best',  # qualité vidéo maximale
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Erreur lors du téléchargement: {e}")
        return False

if __name__ == "__main__":
    if yt_dlp is None:
        print("Impossible de continuer sans yt-dlp.")
        exit(1)

    url = input("Entrez l'URL de la vidéo YouTube à télécharger : ")
    if telecharger_video(url):
        print("Téléchargement terminé avec succès.")
    else:
        print("Échec du téléchargement.")

