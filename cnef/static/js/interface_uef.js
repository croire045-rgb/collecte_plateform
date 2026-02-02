let selectedFile = null;
let userHistory = [];
let currentWorkbook = null;
let currentSheetData = null;
let currentSheetNames = []; // Variable manquante ajoutée

function switchTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

function handleDragOver(e) {
    e.preventDefault();
    document.getElementById('dropZone').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    document.getElementById('dropZone').classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    document.getElementById('dropZone').classList.remove('dragover');
    handleFileSelect(e.dataTransfer.files);
}

function handleFileSelect(files) {
    if (files.length > 0) {
        selectedFile = files[0];
        const fileInfo = document.getElementById('fileInfo');
        const uploadBtn = document.getElementById('uploadBtn');
        
        document.getElementById('fileName').textContent = selectedFile.name;
        document.getElementById('fileSize').textContent = formatFileSize(selectedFile.size);
        document.getElementById('fileType').textContent = selectedFile.type || 'Type inconnu';
        
        fileInfo.style.display = 'block';
        uploadBtn.disabled = false;

        // Lire et afficher l'aperçu du fichier
        readFilePreview(selectedFile);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Fonction manquante ajoutée
function readFilePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            currentWorkbook = workbook;
            displaySheetPreview(workbook);
        } catch (error) {
            displayErrorPreview('Erreur lors de la lecture du fichier');
        }
    };
    reader.readAsArrayBuffer(file);
}

// Fonction manquante ajoutée
function displaySheetPreview(workbook) {
    const sheetNames = workbook.SheetNames;
    const previewContent = document.getElementById('previewContent');
    
    if (sheetNames.length === 0) {
        displayErrorPreview('Aucune feuille trouvée dans le fichier');
        return;
    }
    
    const firstSheet = workbook.Sheets[sheetNames[0]];
    const jsonData = XLSX.utils.sheet_to_json(firstSheet, {header: 1});
    
    let tableHTML = '<table class="preview-table"><thead>';
    
    // En-têtes
    if (jsonData.length > 0) {
        tableHTML += '<tr>';
        jsonData[0].forEach(header => {
            tableHTML += `<th>${header}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';
        
        // Données (limitées aux 10 premières lignes)
        for (let i = 1; i < Math.min(jsonData.length, 11); i++) {
            tableHTML += '<tr>';
            jsonData[i].forEach(cell => {
                tableHTML += `<td>${cell || ''}</td>`;
            });
            tableHTML += '</tr>';
        }
    }
    
    tableHTML += '</tbody></table>';
    previewContent.innerHTML = tableHTML;
}

function displayErrorPreview(message) {
    const previewContent = document.getElementById('previewContent');
    previewContent.innerHTML = `
        <div style="text-align: center; padding: 20px; color: #e74c3c;">
            <div style="font-size: 48px; margin-bottom: 15px;"></div>
            <h4>${message}</h4>
            <p>Veuillez vérifier le format du fichier et réessayer.</p>
        </div>
    `;
}

function addToHistory(file) {
    const historyItem = {
        name: file.name,
        size: file.size,
        date: new Date().toISOString(),
        status: 'Terminé'
    };
    
    userHistory.unshift(historyItem);
    updateProfileHistory();
}

function updateProfileHistory() {
    const profileHistoryList = document.getElementById('profileHistoryList');
    profileHistoryList.innerHTML = '';
    
    userHistory.forEach(file => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-card';
        
        // Déterminer la classe de statut
        let statusClass = 'status-success';
        if (file.status === 'Rejeté') {
            statusClass = 'status-rejected';
        } else if (file.status === 'Erreur') {
            statusClass = 'status-error';
        } else if (file.status === 'En cours' || file.status === 'En attente') {
            statusClass = 'status-pending';
        }
        
        let historyHTML = `
            <div class="file-name">${file.name}</div>
            <div class="file-meta">
                <span>${formatFileSize(file.size)}</span>
                <span>${new Date(file.date).toLocaleDateString()}</span>
                <span class="status-badge ${statusClass}">${file.status}</span>
            </div>
        `;
        
        // Ajouter la raison du rejet si présente
        if (file.raison_rejet) {
            historyHTML += `
                <div class="raison-rejet">
                    <strong>Raison du rejet :</strong> ${file.raison_rejet}
                </div>
            `;
        }
        
        historyItem.innerHTML = historyHTML;
        profileHistoryList.appendChild(historyItem);
    });
}

function actualiserHistorique() {
    fetch('/api/historique/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                userHistory = data.historique;
                updateProfileHistory();
            }
        });
}

// ==================== UTILITAIRES ====================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ==================== PRÉVISUALISATION DU FICHIER ====================
function handleFileSelectForPreview(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Afficher les informations du fichier
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileSelected').style.display = 'flex';
    document.getElementById('dropZone').style.display = 'none';
    document.getElementById('submitBtn').style.display = 'flex';
    
    // Lire et prévisualiser le fichier
    const reader = new FileReader();
    
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            
            currentWorkbook = workbook;
            currentSheetNames = workbook.SheetNames;
            
            // Afficher le sélecteur de feuilles si plusieurs feuilles
            if (currentSheetNames.length > 1) {
                const sheetSelect = document.getElementById('sheetSelect');
                sheetSelect.innerHTML = currentSheetNames.map((name, index) => 
                    `<option value="${index}">${name}</option>`
                ).join('');
                document.getElementById('sheetSelector').style.display = 'flex';
            } else {
                document.getElementById('sheetSelector').style.display = 'none';
            }
            
            // Afficher la première feuille
            displaySheet(0);
            document.getElementById('previewSection').classList.add('active');
            
        } catch (error) {
            console.error('Erreur lors de la lecture du fichier:', error);
            alert('Erreur lors de la lecture du fichier. Assurez-vous qu\'il s\'agit d\'un fichier Excel valide.');
        }
    };
    
    reader.readAsArrayBuffer(file);
}

// ==================== SUPPRIMER LE FICHIER ====================
function removeFile() {
    document.getElementById('fichier').value = '';
    document.getElementById('fileSelected').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('submitBtn').style.display = 'none';
    document.getElementById('previewSection').classList.remove('active');
    document.getElementById('upload-result').innerHTML = '';
}

// ==================== CHANGER DE FEUILLE ====================
function changeSheet() {
    const sheetIndex = parseInt(document.getElementById('sheetSelect').value);
    displaySheet(sheetIndex);
}

// ==================== AFFICHER UNE FEUILLE SPÉCIFIQUE ====================
function displaySheet(sheetIndex) {
    if (!currentWorkbook) return;
    
    const sheetName = currentSheetNames[sheetIndex];
    const worksheet = currentWorkbook.Sheets[sheetName];
    
    // Convertir en JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet, {header: 1, defval: ''});
    
    if (jsonData.length === 0) {
        document.getElementById('previewContent').innerHTML = '<p style="text-align: center; padding: 20px;">Cette feuille est vide</p>';
        return;
    }
    
    // Afficher les informations
    const infoDiv = document.getElementById('previewInfo');
    infoDiv.innerHTML = `
        <strong>Feuille:</strong> ${sheetName} | 
        <strong>Lignes:</strong> ${jsonData.length} | 
        <strong>Colonnes:</strong> ${jsonData[0] ? jsonData[0].length : 0}
    `;
    
    // Créer le tableau HTML
    let tableHTML = '<table class="preview-table">';
    
    // En-têtes
    if (jsonData.length > 0) {
        tableHTML += '<thead><tr>';
        jsonData[0].forEach(cell => {
            tableHTML += `<th>${cell || ''}</th>`;
        });
        tableHTML += '</tr></thead>';
    }
    
    // Corps du tableau (limité aux 100 premières lignes pour la performance)
    tableHTML += '<tbody>';
    const maxRows = Math.min(jsonData.length, 101);
    for (let i = 1; i < maxRows; i++) {
        tableHTML += '<tr>';
        jsonData[i].forEach(cell => {
            tableHTML += `<td>${cell !== undefined && cell !== null ? cell : ''}</td>`;
        });
        tableHTML += '</tr>';
    }
    tableHTML += '</tbody></table>';
    
    if (jsonData.length > 101) {
        tableHTML += `<p style="text-align: center; padding: 15px; color: #7f8c8d; font-style: italic;">
            Affichage limité aux 100 premières lignes. Le fichier complet sera traité lors de la soumission.
        </p>`;
    }
    
    document.getElementById('previewContent').innerHTML = tableHTML;
}

// ==================== DRAG & DROP ====================
const dropZone = document.getElementById('dropZone');

if (dropZone) {
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = document.getElementById('fichier');
            fileInput.files = files;
            handleFileSelectForPreview(files);
        }
    });
}

// ==================== UPLOAD DE FICHIER ====================
document.addEventListener('DOMContentLoaded', function() {
    const formUpload = document.getElementById('form-upload-fichier');
    
    if (formUpload) {
        formUpload.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('fichier');
            if (!fileInput.files || fileInput.files.length === 0) {
                alert('Veuillez sélectionner un fichier');
                return;
            }
            
            const formData = new FormData(this);
            const resultDiv = document.getElementById('upload-result');
            const submitBtn = document.getElementById('submitBtn');
            
            // Désactiver le bouton pendant l'upload
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinning">
                    <circle cx="12" cy="12" r="10"></circle>
                </svg>
                <span>Envoi en cours...</span>
            `;
            
            // Afficher le message de chargement
            resultDiv.innerHTML = `
                <div class="alert alert-info">
                    <div class="loading-spinner"></div>
                    <p>📤 Upload en cours, veuillez patienter...</p>
                </div>
            `;
            
            try {
                const response = await fetch('/upload-fichier/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            ✅ ${data.message || 'Fichier uploadé avec succès!'}
                        </div>
                    `;
                    
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            ❌ ${data.message || 'Erreur lors de l\'upload'}
                        </div>
                    `;
                    
                    // Réactiver le bouton en cas d'erreur
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        <span>Soumettre le fichier</span>
                    `;
                }
            } catch (error) {
                console.error('Erreur lors de l\'upload:', error);
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        ❌ Erreur de connexion: ${error.message}
                    </div>
                `;
                
                // Réactiver le bouton en cas d'erreur
                submitBtn.disabled = false;
                submitBtn.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <span>Soumettre le fichier</span>
                `;
            }
        });
    }
    // Charger l'historique au démarrage
    actualiserHistorique();
});