document.getElementById('enterBtn').addEventListener('click', function () { 
    var googleAuthModal = new bootstrap.Modal(document.getElementById('googleAuthModal')).show(); 
});
  
document.getElementById('googleLoginBtn').addEventListener( 'click', function () { 
    window.location.href = 'https://accounts.google.com/o/oauth2/v2/auth'; 
} );
  