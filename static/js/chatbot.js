let selectedLanguage = "";

function toggleChat() {
    const chat = document.getElementById("chatWindow");
    chat.style.display = chat.style.display === "block" ? "none" : "block";
}

function languageChosen() {
    const lang = document.getElementById("languageSelect").value;
    if (lang) {
        selectedLanguage = lang;
        document.getElementById("inputGroup").style.display = "flex";

        const chatMessages = document.getElementById("chatMessages");
        chatMessages.innerHTML += `<div class="bot-message">✅ Language set to <b>${lang}</b>. You may now ask your question.</div>`;
    }
}

function sendMessage() {
    const input = document.getElementById("userInput").value;
    if (!input || !selectedLanguage) return;

    const chatMessages = document.getElementById("chatMessages");
    chatMessages.innerHTML += `<div class="user-message">${input}</div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom after user message

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input, language: selectedLanguage })
    })
    .then(res => res.json())
    .then(data => {
        chatMessages.innerHTML += `<div class="bot-message">${data.answer}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom after bot message
        document.getElementById("userInput").value = "";  // Clear input field
    });
}


function handleKey(event) {
    if (event.key === "Enter") sendMessage();
}
