// ==========================================
// BOUTON FLOTTANT DE DÉCONNEXION DRAGGABLE
// ==========================================

(function() {
    const bubble = document.getElementById('logoutBubble');
    
    if (!bubble) {
        console.warn('Bouton de déconnexion non trouvé');
        return;
    }
    
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;
    
    // Charger la position sauvegardée (si elle existe)
    const savedPosition = localStorage.getItem('logoutBubblePosition');
    if (savedPosition) {
        const { x, y } = JSON.parse(savedPosition);
        bubble.style.right = 'auto';
        bubble.style.bottom = 'auto';
        bubble.style.left = x + 'px';
        bubble.style.top = y + 'px';
        xOffset = x;
        yOffset = y;
    }
    
    // Événements pour le drag
    bubble.addEventListener('mousedown', dragStart);
    bubble.addEventListener('touchstart', dragStart);
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag);
    
    document.addEventListener('mouseup', dragEnd);
    document.addEventListener('touchend', dragEnd);
    
    function dragStart(e) {
        bubble.dataset.clickTime = Date.now();
        
        if (e.type === 'touchstart') {
            initialX = e.touches[0].clientX - xOffset;
            initialY = e.touches[0].clientY - yOffset;
        } else {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
        }
        
        if (e.target === bubble || bubble.contains(e.target)) {
            isDragging = true;
            bubble.classList.add('dragging');
        }
    }
    
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            
            if (e.type === 'touchmove') {
                currentX = e.touches[0].clientX - initialX;
                currentY = e.touches[0].clientY - initialY;
            } else {
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
            }
            
            xOffset = currentX;
            yOffset = currentY;
            
            // Appliquer la position
            bubble.style.right = 'auto';
            bubble.style.bottom = 'auto';
            bubble.style.left = currentX + 'px';
            bubble.style.top = currentY + 'px';
        }
    }
    
    function dragEnd(e) {
        if (isDragging) {
            const clickDuration = Date.now() - parseInt(bubble.dataset.clickTime || '0');
            
            // Si c'était un vrai drag (pas juste un clic)
            if (clickDuration > 150) {
                // Sauvegarder la position
                localStorage.setItem('logoutBubblePosition', JSON.stringify({
                    x: xOffset,
                    y: yOffset
                }));
                
                // Empêcher le clic de déconnexion
                bubble.dataset.wasDragged = 'true';
                setTimeout(() => {
                    delete bubble.dataset.wasDragged;
                }, 100);
            }
            
            isDragging = false;
            bubble.classList.remove('dragging');
        }
    }
    
    // ✅ GESTION DU CLIC POUR DÉCONNEXION (CORRIGÉ)
    bubble.addEventListener('click', function(e) {
        // Si c'était un drag, on ignore le clic
        if (bubble.dataset.wasDragged === 'true') {
            return;
        }
        
        // Confirmation avant déconnexion
        if (confirm('Voulez-vous vraiment vous déconnecter ?')) {
            // ✅ Redirection vers la vue de déconnexion avec le bon chemin
            window.location.href = "/deconnexion/";
        }
    });
    
    // Animation pulse au survol (optionnel)
    bubble.addEventListener('mouseenter', function() {
        if (!isDragging) {
            this.classList.add('pulse');
        }
    });
    
    bubble.addEventListener('mouseleave', function() {
        this.classList.remove('pulse');
    });
    
})();