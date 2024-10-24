document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('enterBtn').addEventListener('click', function () {
        var playlistLink = document.getElementById('playlistLink').value;
        console.log(playlistLink);
        if (playlistLink) {
            fetch('/playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ playlist: playlistLink }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    console.log('Erro:', data.error);
                }
            })
            .catch((error) => {
                console.error('Erro:', error);
            });
        } else {
            alert('Please enter a valid playlist URL.');
        }
    });
});
