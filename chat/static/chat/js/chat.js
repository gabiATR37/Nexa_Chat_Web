const socket = new WebSocket(
    "ws://" +
    window.location.host +
    "/ws/chat/" +
    conversationId +
    "/"
);

// ==========================
// ELEMENTOS
// ==========================

const messages = document.getElementById("messages");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

const emojiBtn = document.getElementById("emoji-btn");
const attachBtn = document.getElementById("attach-btn");
const attachMenu = document.getElementById("attach-menu");
const audioBtn = document.getElementById("audio-btn");
// ==========================
// GRABACIÓN DE AUDIO
// ==========================

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

const imageInput = document.getElementById("image-input");
const videoInput = document.getElementById("video-input");
const documentInput = document.getElementById("document-input");

// ==========================
// RECIBIR MENSAJES
// ==========================

socket.onmessage = function (e) {

    console.log("Mensaje recibido:", e.data);

    const data = JSON.parse(e.data);

    console.log("currentUser:", currentUser);
    console.log("username recibido:", data.username);
    console.log("isMe:", data.username === currentUser);

    const isMe = data.username === currentUser;

    const hora = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    const avatar = isMe
        ? ""
        : `<img src="${data.image}" class="chat-avatar">`;

    let contenido = data.message;

    if (data.image_file) {

        contenido = `<img src="${data.image_file}" class="chat-image">`;

    } else if (data.video_file) {

        contenido = `
            <video controls class="chat-video">
                <source src="${data.video_file}">
            </video>
        `;

    } else if (data.document_file) {

        contenido = `
            <a href="${data.document_file}" target="_blank" class="chat-document">
                📄 Documento
            </a>
        `;

    } else if (data.audio_file) {

        contenido = `
            <audio
                controls
                class="chat-audio"
                preload="metadata"
                src="${data.audio_file}">
                Tu navegador no soporta audio.
            </audio>
        `;
    }

    const html = `
        <div class="message ${isMe ? "me" : "other"}">

            ${avatar}

            <div class="message-content">

                <div class="sender">
                    ${isMe ? "Tú" : data.display_name}
                </div>

                <div class="bubble">
                    ${contenido}
                </div>

                <div class="time">
                    ${hora}
                </div>

            </div>

        </div>
    `;
    messages.insertAdjacentHTML("beforeend", html);
    messages.scrollTop = messages.scrollHeight;

};

// ==========================
// INPUT
// ==========================

input.addEventListener("input", function () {

    if (input.value.trim() === "") {

        audioBtn.classList.remove("hidden");
        sendBtn.classList.add("hidden");

    } else {

        audioBtn.classList.add("hidden");
        sendBtn.classList.remove("hidden");

    }

});

// ==========================
// BOTÓN +
// ==========================

attachBtn.onclick = function (e) {

    e.stopPropagation();
    attachMenu.classList.toggle("show");

};

document.addEventListener("click", function () {

    attachMenu.classList.remove("show");

});

attachMenu.addEventListener("click", function (e) {

    e.stopPropagation();

});

// ==========================
// EMOJIS
// ==========================

emojiBtn.onclick = function () {

    console.log("Emoji");

};

// ==========================
// AUDIO (NOTAS DE VOZ)
// ==========================

audioBtn.onclick = async function () {

    // Si todavía no está grabando, comenzar
    if (!isRecording) {

        try {
            console.log(window.navigator.mediaDevices);
            console.log("mediaDevices:", window.navigator.mediaDevices);
            console.log("getUserMedia:", window.navigator.mediaDevices?.getUserMedia);
            console.log("Protocolo:", window.location.protocol);
            console.log("Host:", window.location.host);
            console.log(typeof MediaRecorder);

            const stream = await window.navigator.mediaDevices.getUserMedia({
                audio: true
            });

            mediaRecorder = new MediaRecorder(stream);

            audioChunks = [];

            mediaRecorder.ondataavailable = function (event) {

                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }

            };

            mediaRecorder.onstop = async function () {

                const audioBlob = new Blob(audioChunks, {
                    type: "audio/webm"
                });

                const formData = new FormData();
                formData.append("audio", audioBlob, "audio.webm");

                try {

                    const response = await fetch(
                        `/chat/${conversationId}/upload/`,
                        {
                            method: "POST",
                            headers: {
                                "X-CSRFToken": getCookie("csrftoken")
                            },
                            body: formData
                        }
                    );

                    const data = await response.json();

                    console.log("Respuesta completa:", data);
                    console.log("URL del audio:", data.audio);

                    if (!data.success) {
                        alert("Error al subir el audio");
                        return;
                    }

                } catch (error) {

                    console.error(error);

                }

                stream.getTracks().forEach(track => track.stop());

            };

            mediaRecorder.start();

            isRecording = true;

            audioBtn.innerHTML =
                '<i class="fa-solid fa-stop"></i>';

            audioBtn.classList.add("recording");

            console.log("Grabando...");

        }catch (error) {
            console.error("ERROR COMPLETO:", error);
            console.log(error.name);
            console.log(error.message);
            alert(error.name + " - " + error.message);
        }

    } else {

        mediaRecorder.stop();

        isRecording = false;

        audioBtn.innerHTML =
            '<i class="fa-solid fa-microphone"></i>';

        audioBtn.classList.remove("recording");

        console.log("Grabación finalizada.");

    }

};

// ==========================
// WEBSOCKET
// ==========================

socket.onopen = function () {

    console.log("WebSocket conectado");

};

socket.onclose = function () {

    console.log("WebSocket desconectado");

};

socket.onerror = function (e) {

    console.error(e);

};

// ==========================
// ENVIAR TEXTO
// ==========================

sendBtn.onclick = function () {

    const message = input.value.trim();

    if (!message) return;

    socket.send(JSON.stringify({
        message: message
    }));

    input.value = "";
    input.focus();

    sendBtn.classList.add("hidden");
    audioBtn.classList.remove("hidden");

};

input.addEventListener("keypress", function (e) {

    if (e.key === "Enter") {

        e.preventDefault();
        sendBtn.click();

    }

});

// ==========================
// SUBIR IMAGEN
// ==========================

imageInput.addEventListener("change", async function () {

    if (this.files.length === 0) return;

    const file = this.files[0];

    console.log("Imagen seleccionada:", file);

    const formData = new FormData();
    formData.append("image", file);

    try {

        const response = await fetch(`/chat/${conversationId}/upload/`, {

            method: "POST",

            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },

            body: formData

        });

        const data = await response.json();

        console.log("Respuesta:", data);

        if (data.success) {

            const html = `
                <div class="message me">

                    <div class="message-content">

                        <div class="sender">
                            Tú
                        </div>

                        <div class="bubble">
                            <img src="${data.image}" class="chat-image">
                        </div>

                        <div class="time">
                            ${new Date().toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit"
                            })}
                        </div>

                    </div>

                </div>
            `;


        } else {

            console.error(data.error);

        }

    } catch (error) {

        console.error(error);

    }
    messages.insertAdjacentHTML("beforeend", html);
    messages.scrollTop = messages.scrollHeight;

});

// ==========================
// VIDEO
// ==========================

videoInput.addEventListener("change", async function () {

    if (this.files.length === 0) return;

    const file = this.files[0];

    const formData = new FormData();
    formData.append("video", file);

    try {

        const response = await fetch(`/chat/${conversationId}/upload/`, {

            method: "POST",

            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },

            body: formData

        });

        const data = await response.json();

        console.log(data);

        if (data.success) {

            const html = `
                <div class="message me">

                    <div class="message-content">

                        <div class="sender">
                            Tú
                        </div>

                        <div class="bubble">

                            <video controls class="chat-video">
                                <source src="${data.video}">
                            </video>

                        </div>

                        <div class="time">
                            ${new Date().toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit"
                            })}
                        </div>

                    </div>

                </div>
            `;

            

        }

    } catch (error) {

        console.error(error);

    }
    messages.insertAdjacentHTML("beforeend", html);
    messages.scrollTop = messages.scrollHeight;

});

// ==========================
// DOCUMENTO
// ==========================

documentInput.addEventListener("change", async function () {

    if (this.files.length === 0) return;

    const file = this.files[0];

    const formData = new FormData();
    formData.append("document", file);

    try {

        const response = await fetch(`/chat/${conversationId}/upload/`, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });

        const data = await response.json();

        console.log("Respuesta:", data);

        if (data.success && data.document) {

            const html = `
                <div class="message me">
                    <div class="message-content">

                        <div class="sender">
                            Tú
                        </div>

                        <div class="bubble">
                            <a href="${data.document}"
                            target="_blank"
                            class="chat-document">
                                📄 ${file.name}
                            </a>
                        </div>

                        <div class="time">
                            ${new Date().toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit"
                            })}
                        </div>

                    </div>
                </div>
            `;

        }

    } catch (error) {
        console.error(error);
    }
    messages.insertAdjacentHTML("beforeend", html);
    messages.scrollTop = messages.scrollHeight;

});
// ==========================
// CSRF
// ==========================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }

        }

    }

    return cookieValue;

}