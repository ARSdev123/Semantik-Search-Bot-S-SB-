// S'assure que le DOM est chargé avant d'ajouter les écouteurs
document.addEventListener("DOMContentLoaded", function() {
    const chatButton = document.getElementById("chat-button");
    const chatContainer = document.getElementById("chat-container");
    const chatbox = document.getElementById("chat-messages");
    const userInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");

    chatButton.addEventListener("click", toggleChat);
    sendButton.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    function toggleChat() {
        // Affiche ou masque le chat en fonction de son état actuel
        if (chatContainer.style.display === "flex") {
            chatContainer.style.display = "none";
        } else {
            chatContainer.style.display = "flex";
        }
    }

    /**
     * Fonction pour envoyer un message de l'utilisateur
     */
    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage) {
            // Affiche le message de l'utilisateur dans le chatbox
            displayMessage(userMessage, "user");
            // Envoie le message au backend
            fetchResponse(userMessage);
            // Efface le champ de saisie
            userInput.value = "";
        }
    }

    /**
     * Fonction pour afficher un message dans le chatbox
     * @param {string} message - Le message à afficher
     * @param {string} sender - L'expéditeur du message ("user" ou "bot")
     */
    function displayMessage(message, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender);
        messageElement.textContent = message;
        chatbox.appendChild(messageElement);
        // Fait défiler le chatbox vers le bas
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    /**
     * Fonction pour envoyer le message au backend et recevoir la réponse
     * @param {string} message - Le message de l'utilisateur
     */
    function fetchResponse(message) {
        // Affiche un indicateur de frappe
        displayTypingIndicator();
        const apikey= "YOUR_API_KEY";

        // Adaptez l'URL à votre endpoint backend
    fetch("http://127.0.0.1:8000/recherche", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                 "X-API-Key": apiKey,
            },
            body: JSON.stringify({ question: message })
        })
        .then(response => {
            // Supprime l'indicateur de frappe
            removeTypingIndicator();
            if (!response.ok) {
                throw new Error("La réponse du réseau n'était pas correcte");
            }
            return response.json();
        })
        .then(data => {
            // Affiche la réponse du bot
            displayMessage(data.recherche, "bot");
        })
        .catch(error => {
            // Supprime l'indicateur de frappe
            removeTypingIndicator();
            console.error("Erreur lors de la récupération de la réponse:", error);
            displayMessage("Désolé, une erreur est survenue. Veuillez réessayer plus tard.", "bot");
        });
    }

    /**
     * Fonction pour afficher un indicateur de frappe
     */
    function displayTypingIndicator() {
        const typingIndicator = document.createElement("div");
        typingIndicator.classList.add("message", "bot", "typing-indicator");
        typingIndicator.innerHTML = "<span></span><span></span><span></span>";
        chatbox.appendChild(typingIndicator);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    // AJOUT : Fonction pour retirer l'indicateur de frappe
    function removeTypingIndicator() {
        const indicators = chatbox.getElementsByClassName("typing-indicator");
        while (indicators.length > 0) {
            indicators[0].parentNode.removeChild(indicators[0]);
        }
    }
});


