const chatButton = document.getElementById("chat-button");
const chatContainer = document.getElementById("chat-container");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");

chatButton.addEventListener("click", toggleChat);
sendButton.addEventListener("click", sendMessage);
chatInput.addEventListener("keypress", function(e){
    if (e.key === "Enter") sendMessage();
});

function toggleChat() {
    chatContainer.style.display = chatContainer.style.display === "flex" ? "none" : "flex";
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, "user-message");
    chatInput.value = "";

    try {
        // Correction : méthode POST et passage du body
        const recherche = await fetch("http://127.0.0.1:8000/recherche?q=" + encodeURIComponent(message), {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });

        const data = await recherche.json();
        addMessage(data.recherche, "bot-message");
    } catch (error) {
        addMessage("⚠️ Erreur de communication avec le serveur", "bot-message");
    }
}

function addMessage(text, className) {
    const div = document.createElement("div");
    div.classList.add("message", className);
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
 /**
     * Fonction pour supprimer l'indicateur de frappe
     */
    function removeTypingIndicator() {
        const typingIndicator = chatbox.querySelector(".typing-indicator");
        if (typingIndicator) {
            chatbox.removeChild(typingIndicator);
        }
    }