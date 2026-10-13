let ytPlayer = null;
let playlist = [];
let currentIndex = -1;

// Variables globales
let playerTitle;
let playerArtist;
let playerCover;
let playPause;
let repeat = false;
let repeatButton;
let shuffle = false;

// ==========================
// REPRODUCIR CANCIÓN
// ==========================

function playSong(button) {

    if (!button || !ytPlayer) return;

    playerTitle.textContent = button.dataset.title;
    playerArtist.textContent = button.dataset.artist;
    playerCover.src = button.dataset.image;

    ytPlayer.loadVideoById(button.dataset.id);

    playPause.textContent = "⏸";
    updateActiveSong();
}

// ==========================
// API YOUTUBE
// ==========================

function onYouTubeIframeAPIReady() {

    console.log("API de YouTube cargada");

    ytPlayer = new YT.Player("music-player", {

        height: "0",
        width: "0",

        playerVars: {
            autoplay: 1,
            rel: 0
        },

        events: {

            onReady: () => {
                console.log("✅ Player listo");
            },

            onStateChange: function (event) {

                switch (event.data) {

                    case YT.PlayerState.PLAYING:
                        playPause.textContent = "⏸";
                        break;

                    case YT.PlayerState.PAUSED:
                        playPause.textContent = "▶";
                        break;

                    case YT.PlayerState.ENDED:

                        if (repeat) {
                            ytPlayer.playVideo();
                            return;
                        }

                        if (shuffle) {

                            currentIndex = Math.floor(Math.random() * playlist.length);

                        } else {

                            currentIndex++;

                            if (currentIndex >= playlist.length) {
                                currentIndex = 0;
                            }

                        }

                        playSong(playlist[currentIndex]);

                        break;
                }

            },

            onError: function (event) {

                if (event.data === 150 || event.data === 101) {

                    console.log("Video bloqueado, pasando al siguiente...");

                    currentIndex++;

                    if (currentIndex >= playlist.length) {
                        currentIndex = 0;
                    }

                    playSong(playlist[currentIndex]);
                }
            }

        }

    });

}

// ==========================
// FORMATO TIEMPO
// ==========================

function formatTime(seconds) {

    seconds = Math.floor(seconds);

    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${minutes}:${secs.toString().padStart(2, "0")}`;

}

function updateActiveSong() {

    document.querySelectorAll(".Song-Card").forEach(card => {
        card.classList.remove("Playing");
    });

    if (currentIndex >= 0) {
        playlist[currentIndex]
            .closest(".Song-Card")
            .classList.add("Playing");
    }

}

// ==========================
// DOM
// ==========================

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("music-search-form");
    const input = document.getElementById("music-search-input");

    playerTitle = document.getElementById("player-title");
    playerArtist = document.getElementById("player-artist");
    playerCover = document.getElementById("player-cover");

    playPause = document.getElementById("play-pause");

    const playButtons = document.querySelectorAll(".Play-Song");
    playlist = [...playButtons];

    const nextSong = document.getElementById("next-song");
    const previousSong = document.getElementById("previous-song");

    const progress = document.getElementById("player-progress");
    const currentTime = document.getElementById("current-time");
    const durationTime = document.getElementById("duration");

    const volume = document.getElementById("volume");
    const mute = document.getElementById("mute");
    const repeatButton = document.getElementById("repeat");
    const shuffleButton = document.getElementById("shuffle");


    // ==========================
    // BUSCADOR
    // ==========================

    if (form) {

        form.addEventListener("submit", function (e) {

            if (input.value.trim() === "") {
                e.preventDefault();
                input.focus();
            }

        });

    }

    // ==========================
    // CLICK EN CANCIÓN
    // ==========================

    playButtons.forEach((button, index) => {

        button.addEventListener("click", () => {

            if (!ytPlayer) {
                alert("El reproductor todavía está cargando.");
                return;
            }

            currentIndex = index;

            playSong(button);

        });

    });

    // ==========================
    // PLAY / PAUSE
    // ==========================

    playPause.addEventListener("click", () => {

        if (!ytPlayer) return;

        const state = ytPlayer.getPlayerState();

        if (state === YT.PlayerState.PLAYING) {

            ytPlayer.pauseVideo();

        } else {

            ytPlayer.playVideo();

        }

    });

    // ==========================
    // SIGUIENTE
    // ==========================

    nextSong.addEventListener("click", () => {

        if (playlist.length === 0) return;

        currentIndex++;

        if (currentIndex >= playlist.length) {
            currentIndex = 0;
        }

        playSong(playlist[currentIndex]);

    });

    // ==========================
    // ANTERIOR
    // ==========================

    previousSong.addEventListener("click", () => {

        if (playlist.length === 0) return;

        currentIndex--;

        if (currentIndex < 0) {
            currentIndex = playlist.length - 1;
        }

        playSong(playlist[currentIndex]);

    });

    // ==========================
    // ACTUALIZAR BARRA
    // ==========================

    setInterval(() => {

        if (!ytPlayer) return;

        if (typeof ytPlayer.getDuration !== "function") return;

        const duration = ytPlayer.getDuration();

        if (!duration) return;

        const current = ytPlayer.getCurrentTime();

        progress.value = (current / duration) * 100;

        if (currentTime)
            currentTime.textContent = formatTime(current);

        if (durationTime)
            durationTime.textContent = formatTime(duration);

    }, 500);

    // ==========================
    // CAMBIAR POSICIÓN
    // ==========================

    progress.addEventListener("input", () => {

        if (!ytPlayer) return;

        const duration = ytPlayer.getDuration();

        ytPlayer.seekTo((progress.value / 100) * duration, true);

    });

    // ==========================
    // VOLUMEN
    // ==========================

    if (volume) {

        volume.addEventListener("input", () => {

            if (!ytPlayer) return;

            ytPlayer.setVolume(volume.value);

        });

    }

    if (mute) {

        mute.addEventListener("click", () => {

            if (!ytPlayer) return;

            if (ytPlayer.isMuted()) {

                ytPlayer.unMute();
                mute.textContent = "🔊";

            } else {

                ytPlayer.mute();
                mute.textContent = "🔇";

            }

        });

    }

    if (repeatButton) {

        repeatButton.addEventListener("click", () => {

            repeat = !repeat;

            repeatButton.classList.toggle("Active", repeat);

        });

    }

    if (shuffleButton) {

        shuffleButton.addEventListener("click", () => {

            shuffle = !shuffle;

            shuffleButton.classList.toggle("Active", shuffle);

        });

    }
});