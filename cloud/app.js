/* SmartHome Cloud - App Logic */

// ==================== Utility Functions ====================

function showError(msg) {
    const el = document.getElementById('errorMsg');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
    const s = document.getElementById('successMsg');
    if (s) s.style.display = 'none';
}

function showSuccess(msg) {
    const el = document.getElementById('successMsg');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
    const e = document.getElementById('errorMsg');
    if (e) e.style.display = 'none';
}

function clearMessages() {
    const e = document.getElementById('errorMsg');
    const s = document.getElementById('successMsg');
    if (e) e.style.display = 'none';
    if (s) s.style.display = 'none';
}

// ==================== Auth Helpers ====================

function logout() {
    auth.signOut();
    localStorage.removeItem('deviceId');
    window.location.href = 'index.html';
}

function requireAuth(callback) {
    auth.onAuthStateChanged(user => {
        if (!user) {
            window.location.href = 'index.html';
            return;
        }
        if (callback) callback(user);
    });
}

// ==================== Device Control ====================

function toggleRelay(deviceId, relayKey, currentState) {
    db.ref('devices/' + deviceId + '/relays/' + relayKey + '/state').set(!currentState);
}

// ==================== Admin Helpers ====================

function isAdmin(uid) {
    return db.ref('admins/' + uid).once('value').then(snap => snap.exists());
}
