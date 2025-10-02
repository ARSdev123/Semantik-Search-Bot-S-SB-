import yt_dlp


def telecharger_video(url):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'best',#"qualité video maximale"
    }

    with  yt_dlp.YoutubeDL(options) as ydl:
          ydl.download([url])

if __name__ == "__main__":
    url = input("Entrez l'URL de la vidéo YouTube à télécharger : ")
    telecharger_video(url)
    print("Téléchargement terminé.")

