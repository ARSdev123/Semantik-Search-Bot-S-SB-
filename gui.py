import customtkinter
import fitz
from chatbotcol import Chatbot
import PyPDF2
from tkinter import filedialog
import random

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (default), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.chatbot = Chatbot()
        self._setup_ui()
        self.afficher_msg("Bot", self.message_acceuil(), "bot")

    def _setup_ui(self):
        self.root.title("ARS-Chatbot v2.1.1")
        self.root.iconbitmap("favicon.ico")
        self.root.geometry("400x500")
        self.root.maxsize(400, 500)

        # Configuration de la grille
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)

        # --- Widgets ---
        # Zone de conversation
        self.zone_conversation = customtkinter.CTkTextbox(self.root, font=("Segoe UI", 13), state="disabled", wrap="word")
        self.zone_conversation.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Frame pour la saisie utilisateur
        frame_saisie = customtkinter.CTkFrame(self.root, fg_color="transparent")
        frame_saisie.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        frame_saisie.grid_columnconfigure(0, weight=1)

        # Champ de saisie
        self.champ_quest = customtkinter.CTkEntry(frame_saisie, placeholder_text="Que puis-je faire pour vous ?", font=("Segoe UI", 13), height=35)
        self.champ_quest.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.champ_quest.bind("<Return>", lambda event: self.envoyer_message())

        # Bouton d'envoi
        bouton_envoyer = customtkinter.CTkButton(frame_saisie, text="Envoyer", font=("Segoe UI", 13, "bold"), command=self.envoyer_message, height=35, width=90)
        bouton_envoyer.grid(row=0, column=1, sticky="e")

    def message_acceuil(self):
        return random.choice([
            "Bonjour ! Je suis votre assistant virtuel. Comment puis-je vous aider aujourd'hui ?",
            "Salut ! Je suis là pour répondre à vos questions. Que voulez-vous savoir ?",
            "Bonjour, comment puis-je vous assister aujourd'hui ?",
            "Salut, je suis prêt à vous aider. Quelle est votre question ?"
        ])
    
    def envoyer_message(self):
        message = self.champ_quest.get()

        if not message.strip():
            return
        
        # Afficher le message utilisateur en bleu
        self.afficher_msg("Vous", message, "user")
        self.champ_quest.delete(0, "end")

        # Obtenir et afficher la réponse du bot en vert
        reponse = self.chatbot.repondre(message)  # Correction : enlever ('red')
        self.afficher_msg("Bot", reponse, "bot")

    def afficher_msg(self, expediteur, contenu, type_message="user"):
        self.zone_conversation.configure(state="normal")
        
        # Ajouter le message avec une couleur différente selon le type
        if type_message == "user":
            # Message utilisateur (bleu)
            self.zone_conversation.insert("end", f"{expediteur}: ", "user_tag")
            self.zone_conversation.insert("end", f"{contenu}\n\n")
        else:
            # Message bot (vert)
            self.zone_conversation.insert("end", f"{expediteur}: ", "bot_tag")
            self.zone_conversation.insert("end", f"{contenu}\n\n")
        
        self.zone_conversation.configure(state="disabled")
        self.zone_conversation.yview("end")
        
        # Configurer les tags de couleur
        self.zone_conversation.tag_config("user_tag", foreground="blue")
        self.zone_conversation.tag_config("bot_tag", foreground="green")

def start_chat():
    root = customtkinter.CTk()
    app = ChatGUI(root)
    root.mainloop()



# Lancer l'application
if __name__ == "__main__":
 start_chat()
 