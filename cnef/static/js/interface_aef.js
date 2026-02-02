        // ==================== GESTION DES ONGLETS ====================
        function switchTab(tabId) {
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            if (tabId === 'dashboard') {
                chargerDashboard();
            } else if (tabId === 'historique') {
                chargerHistorique();
            } else if (tabId === 'utilisateurs') {
                chargerUtilisateursUEF();
                chargerInvitationsEnAttente();
            } else if (tabId === 'journalisation') {
                chargerJournalisation();
            }
        }

        // ==================== CHARGEMENT DES DONNÉES ====================
        async function chargerDashboard() {
            try {
                const response = await fetch('/aef/api/dashboard/');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('stat-total-soumissions').textContent = data.stats.total;
                    document.getElementById('stat-en-attente').textContent = data.stats.en_attente;
                    document.getElementById('stat-validees').textContent = data.stats.validees;
                    document.getElementById('stat-rejetees').textContent = data.stats.rejetees;
                    document.getElementById('stat-utilisateurs').textContent = data.stats.utilisateurs_actifs;
                    
                    afficherDernieresSoumissions(data.dernieres_soumissions);
                }
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        function afficherDernieresSoumissions(soumissions) {
            const tbody = document.querySelector('#table-dernieres-soumissions tbody');
            
            if (soumissions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune soumission</td></tr>';
                return;
            }
            
            tbody.innerHTML = soumissions.map(s => `
                <tr>
                    <td>${s.nom_fichier}</td>
                    <td>${new Date(s.date_import).toLocaleString('fr-FR')}</td>
                    <td><span class="badge badge-${s.statut_class}">${s.statut_display}</span></td>
                    <td>${s.total_lignes}</td>
                    <td>
                        <button class="btn btn-primary" onclick="voirDetailsSoumission(${s.id})">
                            👁️ Voir
                        </button>
                    </td>
                </tr>
            `).join('');
        }

        async function chargerHistorique() {
            const statut = document.getElementById('filtre-statut').value;
            
            try {
                const response = await fetch(`/aef/api/historique/?statut=${statut}`);
                const data = await response.json();
                
                if (data.success) {
                    afficherHistorique(data.soumissions);
                }
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        function afficherHistorique(soumissions) {
            const tbody = document.querySelector('#table-historique tbody');
            
            if (soumissions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Aucune soumission trouvée</td></tr>';
                return;
            }
            
            tbody.innerHTML = soumissions.map(s => `
                <tr>
                    <td>${s.nom_fichier}</td>
                    <td>${new Date(s.date_import).toLocaleString('fr-FR')}</td>
                    <td><span class="badge badge-${s.statut_class}">${s.statut_display}</span></td>
                    <td>${s.total_lignes}</td>
                    <td>${s.commentaire || '-'}</td>
                    <td>
                        <button class="btn btn-primary" onclick="voirDetailsSoumission(${s.id})">
                            👁️ Détails
                        </button>
                    </td>
                </tr>
            `).join('');
        }

        async function chargerUtilisateursUEF() {
            try {
                const response = await fetch('/aef/api/utilisateurs-uef/');
                const data = await response.json();
                
                if (data.success) {
                    afficherUtilisateursUEF(data.utilisateurs);
                }
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        function afficherUtilisateursUEF(utilisateurs) {
            const tbody = document.querySelector('#table-utilisateurs-uef tbody');
            
            if (utilisateurs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Aucun utilisateur</td></tr>';
                return;
            }
            
            tbody.innerHTML = utilisateurs.map(u => `
                <tr>
                    <td>${u.prenom} ${u.nom}</td>
                    <td>${u.email}</td>
                    <td>${u.telephone || '-'}</td>
                    <td><span class="badge badge-${u.is_active ? 'success' : 'danger'}">${u.is_active ? 'Actif' : 'Inactif'}</span></td>
                    <td>${new Date(u.date_joined).toLocaleDateString('fr-FR')}</td>
                    <td>${u.derniere_connexion ? new Date(u.derniere_connexion).toLocaleDateString('fr-FR') : 'Jamais'}</td>
                    <td>
                        
                    </td>
                </tr>
            `).join('');
        }

        async function chargerInvitationsEnAttente() {
            try {
                const response = await fetch('/aef/api/invitations-attente/');
                const data = await response.json();
                
                if (data.success) {
                    afficherInvitationsEnAttente(data.invitations);
                }
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        function afficherInvitationsEnAttente(invitations) {
            const tbody = document.querySelector('#table-invitations-attente tbody');
            
            if (invitations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune invitation en attente</td></tr>';
                return;
            }
            
            tbody.innerHTML = invitations.map(inv => `
                <tr>
                    <td>${inv.email}</td>
                    <td>${new Date(inv.date_creation).toLocaleString('fr-FR')}</td>
                    <td>${new Date(inv.expiration).toLocaleString('fr-FR')}</td>
                    <td>${inv.temps_restant_minutes} min</td>
                    <td>
                        <button class="btn btn-primary" onclick="copierLienInvitation('${inv.lien}')">
                            📋 Copier le lien
                        </button>
                        <button class="btn btn-danger" onclick="revoquerInvitation(${inv.id})">
                            🗑️ Révoquer
                        </button>
                    </td>
                </tr>
            `).join('');
        }

        // ==================== UPLOAD DE FICHIER ====================
        document.getElementById('form-upload-fichier').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const resultDiv = document.getElementById('upload-result');
            
            resultDiv.innerHTML = '<div class="alert alert-info">📤 Upload en cours...</div>';
            
            try {
                const response = await fetch('/aef/upload-fichier/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
                    this.reset();
                    // On reste sur le même onglet (upload)
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">' + data.message + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="alert alert-danger">Erreur : ' + error.message + '</div>';
            }
        });

        // ==================== GESTION INVITATIONS UEF ====================
        function ouvrirModalInviterUEF() {
            document.getElementById('modal-inviter-uef').style.display = 'block';
        }

        function fermerModalInviterUEF() {
            document.getElementById('modal-inviter-uef').style.display = 'none';
            document.getElementById('form-inviter-uef').reset();
            document.getElementById('resultat-invitation').innerHTML = '';
        }

        document.getElementById('form-inviter-uef').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email-uef').value;
            const resultDiv = document.getElementById('resultat-invitation');
            
            resultDiv.innerHTML = '<div class="alert alert-info">📧 Génération du lien en cours...</div>';
            
            try {
                const response = await fetch('/aef/api/generer-invitation-uef/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ email: email })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h3>✅ Invitation générée avec succès !</h3>
                            <p><strong>Destinataire :</strong> ${data.invitation.email}</p>
                            <p><strong>Expiration :</strong> ${data.invitation.expiration}</p>
                            <p><strong>Temps restant :</strong> ${data.invitation.temps_restant_minutes} minutes</p>
                            
                            <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0; word-break: break-all; border: 1px solid #ddd;">
                                ${data.invitation.lien}
                            </div>
                            
                            <button class="btn btn-primary" onclick="copierLienInvitation('${data.invitation.lien}')">
                                📋 Copier le lien
                            </button>
                            <button class="btn btn-success" onclick="envoyerViaWhatsApp('${data.invitation.lien}', '${email}')">
                                💬 Envoyer via WhatsApp
                            </button>
                        </div>
                    `;
                    
                    chargerInvitationsEnAttente();
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">❌ ' + data.message + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="alert alert-danger">❌ Erreur : ' + error.message + '</div>';
            }
        });

        function copierLienInvitation(lien) {
            navigator.clipboard.writeText(lien).then(() => {
                alert('✅ Lien copié dans le presse-papiers !');
            });
        }

        function envoyerViaWhatsApp(lien, email) {
            const message = `Bonjour,\n\nVous êtes invité(e) à créer votre compte sur la plateforme CNEF.\n\nCliquez sur ce lien pour vous inscrire :\n${lien}\n\n⚠️ Ce lien expire dans quelques heures.`;
            const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
            window.open(whatsappUrl, '_blank');
        }

        async function revoquerInvitation(invitationId) {
            if (!confirm('Voulez-vous vraiment révoquer cette invitation ?')) {
                return;
            }
            
            try {
                const response = await fetch(`/aef/api/revoquer-invitation/${invitationId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    chargerInvitationsEnAttente();
                } else {
                    alert('❌ ' + data.message);
                }
            } catch (error) {
                alert('❌ Erreur : ' + error.message);
            }
        }

        // ==================== GESTION PROFIL ====================
        function ouvrirModalModifierProfil() {
            document.getElementById('modal-modifier-profil').style.display = 'block';
        }

        function fermerModalModifierProfil() {
            document.getElementById('modal-modifier-profil').style.display = 'none';
        }

        document.getElementById('form-modifier-profil').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                prenom: document.getElementById('edit-prenom').value,
                nom: document.getElementById('edit-nom').value,
                telephone: document.getElementById('edit-telephone').value
            };
            
            try {
                const response = await fetch('/aef/api/modifier-profil/', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ ' + result.message);
                    fermerModalModifierProfil();
                    location.reload();
                } else {
                    alert('❌ ' + result.message);
                }
            } catch (error) {
                alert('❌ Erreur : ' + error.message);
            }
        });

        function deconnexion() {
            if (confirm('Voulez-vous vraiment vous déconnecter ?')) {
                window.location.href = '/deconnexion/';
            }
        }

        // ==================== DÉTAILS ====================
        function voirDetailsSoumission(id) {
            window.location.href = `/aef/soumission/${id}/`;
        }

    
        // ==================== PRÉVISUALISATION ====================
        let currentWorkbook = null;

        function handleFileSelectForPreview(files) {
            if (files.length > 0) {
                const file = files[0];
                readFilePreview(file);
            }
        }

        function readFilePreview(file) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const data = e.target.result;
                
                if (file.name.endsWith('.csv')) {
                    Papa.parse(data, {
                        header: true,
                        skipEmptyLines: true,
                        complete: function(results) {
                            displayCSVPreview(results.data, results.meta.fields);
                        },
                        error: function(error) {
                            displayErrorPreview("Erreur lors de la lecture du fichier CSV");
                        }
                    });
                } else {
                    try {
                        const workbook = XLSX.read(data, { type: 'binary' });
                        currentWorkbook = workbook;
                        displayExcelPreview(workbook);
                    } catch (error) {
                        displayErrorPreview("Erreur lors de la lecture du fichier Excel");
                    }
                }
            };
            
            reader.onerror = function() {
                displayErrorPreview("Erreur lors de la lecture du fichier");
            };
            
            if (file.name.endsWith('.csv')) {
                reader.readAsText(file);
            } else {
                reader.readAsBinaryString(file);
            }
        }

        function displayExcelPreview(workbook) {
            const previewSection = document.getElementById('previewSection');
            const sheetSelector = document.getElementById('sheetSelector');
            const sheetSelect = document.getElementById('sheetSelect');
            
            previewSection.classList.add('active');
            
            sheetSelect.innerHTML = '';
            workbook.SheetNames.forEach((sheetName, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = sheetName;
                sheetSelect.appendChild(option);
            });
            
            sheetSelector.style.display = 'block';
            changeSheet();
        }

        function changeSheet() {
            if (!currentWorkbook) return;
            
            const sheetSelect = document.getElementById('sheetSelect');
            const selectedIndex = sheetSelect.value;
            const sheetName = currentWorkbook.SheetNames[selectedIndex];
            const worksheet = currentWorkbook.Sheets[sheetName];
            
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            displayTablePreview(jsonData, sheetName);
        }

        function displayCSVPreview(data, headers) {
            const previewSection = document.getElementById('previewSection');
            const sheetSelector = document.getElementById('sheetSelector');
            
            previewSection.classList.add('active');
            sheetSelector.style.display = 'none';
            
            const nonEmptyRows = data.filter(row => {
                return Object.values(row).some(value => value !== null && value !== undefined && value !== '');
            });
            
            displayTablePreview([headers, ...nonEmptyRows], "Données CSV", nonEmptyRows.length);
        }

        function displayTablePreview(data, title, nonEmptyRowCount = null) {
            const previewContent = document.getElementById('previewContent');
            
            if (!data || data.length === 0) {
                previewContent.innerHTML = '<div class="preview-info">Aucune donnée trouvée dans le fichier</div>';
                return;
            }
            
            const headers = data[0];
            
            if (nonEmptyRowCount === null) {
                nonEmptyRowCount = data.slice(1).filter(row => {
                    return row.some(cell => cell !== null && cell !== undefined && cell !== '');
                }).length;
            }
            
            const rowsToShow = data.slice(1).filter(row => {
                return row.some(cell => cell !== null && cell !== undefined && cell !== '');
            }).slice(0, 50);
            
            let tableHTML = `
                <div class="preview-info">
                    <strong>Feuille:</strong> ${title} | 
                    <strong>Lignes:</strong> ${nonEmptyRowCount} | 
                    <strong>Colonnes:</strong> ${headers.length}
                </div>
                <table class="preview-table">
                    <thead>
                        <tr>
            `;
                        
            headers.forEach(header => {
                tableHTML += `<th>${header || 'Colonne'}</th>`;
            });
            
            tableHTML += `</tr></thead><tbody>`;
            
            rowsToShow.forEach(row => {
                tableHTML += '<tr>';
                headers.forEach((header, index) => {
                    const value = row[index] !== undefined ? row[index] : '';
                    tableHTML += `<td title="${value}">${value}</td>`;
                });
                tableHTML += '</tr>';
            });
            
            tableHTML += `</tbody></table>`;
            
            let scrollInfo = '';
            if (nonEmptyRowCount > 50) {
                scrollInfo = `Affichage des 50 premières lignes non vides sur ${nonEmptyRowCount} au total`;
            } else if (rowsToShow.length === 0) {
                scrollInfo = 'Aucune ligne de données non vide trouvée';
            } else {
                scrollInfo = `Affichage de ${rowsToShow.length} ligne(s)`;
            }
            
            tableHTML += `
                <div style="margin-top: 10px; color: #7f8c8d; font-size: 0.9em;">
                    ${scrollInfo}
                </div>
            `;
            
            previewContent.innerHTML = tableHTML;
        }

        function displayErrorPreview(message) {
            const previewContent = document.getElementById('previewContent');
            previewContent.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #e74c3c;">
                    <div style="font-size: 48px; margin-bottom: 15px;">⚠️</div>
                    <h4>${message}</h4>
                    <p>Veuillez vérifier le format du fichier et réessayer.</p>
                </div>
            `;
        }

        // ==================== JOURNALISATION ====================
        let paginationJournalisation = { page: 1, per_page: 50 };
        let rechercheJournalisationTimeout;

        async function chargerJournalisation(page = 1) {
            paginationJournalisation.page = page;
            
            const tbody = document.querySelector('#table-journalisation tbody');
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Chargement...</td></tr>';

            try {
                const params = new URLSearchParams({
                    page: paginationJournalisation.page,
                    per_page: paginationJournalisation.per_page
                });

                const typeAction = document.getElementById('filtre-type-action')?.value;
                if (typeAction) params.append('type_action', typeAction);

                const dateDebut = document.getElementById('filtre-date-debut')?.value;
                if (dateDebut) params.append('date_debut', new Date(dateDebut).toISOString());

                const dateFin = document.getElementById('filtre-date-fin')?.value;
                if (dateFin) params.append('date_fin', new Date(dateFin).toISOString());

                const search = document.getElementById('recherche-journalisation')?.value;
                if (search) params.append('search', search);

                const response = await fetch(`/aef/api/journalisation/?${params.toString()}`, {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();

                if (data.success) {
                    afficherJournalisation(data.actions);
                    afficherPaginationJournalisation(data.pagination);
                    afficherStatistiquesJournalisation(data.stats);
                } else {
                    throw new Error(data.message || 'Erreur lors du chargement');
                }
            } catch (error) {
                console.error('Erreur:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: #e74c3c;">
                            ❌ Erreur : ${error.message}
                        </td>
                    </tr>
                `;
            }
        }

        function afficherJournalisation(actions) {
            const tbody = document.querySelector('#table-journalisation tbody');
            
            if (!actions || actions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune action trouvée</td></tr>';
                return;
            }

            tbody.innerHTML = actions.map(action => `
                <tr>
                    <td style="white-space: nowrap;">
                        ${new Date(action.date_action).toLocaleString('fr-FR')}
                    </td>
                    <td>
                        <span class="badge badge-${getBadgeClassForAction(action.type_action)}">
                            ${action.type_action_display}
                        </span>
                    </td>
                    <td>
                        ${action.utilisateur ? `
                            <div style="font-size: 13px;">
                                <strong>${action.utilisateur.nom}</strong><br>
                                <span style="color: #7f8c8d;">${action.utilisateur.email}</span>
                            </div>
                        ` : '<span style="color: #95a5a6;">N/A</span>'}
                    </td>
                    <td style="max-width: 400px;">${action.description}</td>
                    <td>${action.adresse_ip || '<span style="color: #95a5a6;">N/A</span>'}</td>
                </tr>
            `).join('');
        }

        function afficherPaginationJournalisation(pagination) {
            const container = document.getElementById('pagination-journalisation');
            
            if (!pagination || pagination.total_pages <= 1) {
                container.innerHTML = '';
                return;
            }

            let html = '<div style="display: flex; justify-content: center; align-items: center; gap: 10px;">';
            
            if (pagination.has_previous) {
                html += `<button class="btn btn-primary" onclick="chargerJournalisation(${pagination.page - 1})">
                    Précédent
                </button>`;
            }

            for (let i = 1; i <= pagination.total_pages; i++) {
                if (i === pagination.page) {
                    html += `<button class="btn btn-primary" style="font-weight: bold;">${i}</button>`;
                } else if (Math.abs(i - pagination.page) <= 2 || i === 1 || i === pagination.total_pages) {
                    html += `<button class="btn" style="background: #ecf0f1;" onclick="chargerJournalisation(${i})">${i}</button>`;
                } else if (Math.abs(i - pagination.page) === 3) {
                    html += '<span>...</span>';
                }
            }

            if (pagination.has_next) {
                html += `<button class="btn btn-primary" onclick="chargerJournalisation(${pagination.page + 1})">
                    Suivant
                </button>`;
            }

            html += `<span style="margin-left: 20px; color: #7f8c8d;">
                Page ${pagination.page} sur ${pagination.total_pages} (${pagination.total} actions)
            </span></div>`;

            container.innerHTML = html;
        }

        function afficherStatistiquesJournalisation(stats) {
            if (!stats) return;
            
            document.getElementById('stat-total-actions').textContent = stats.total || 0;
            document.getElementById('stat-connexions').textContent = stats.par_type?.CONNEXION || 0;
            document.getElementById('stat-uploads').textContent = stats.par_type?.UPLOAD_FICHIER || 0;
            document.getElementById('stat-invitations').textContent = stats.par_type?.GENERATION_LIEN || 0;
        }

        function rechercherJournalisation() {
            clearTimeout(rechercheJournalisationTimeout);
            rechercheJournalisationTimeout = setTimeout(() => {
                chargerJournalisation(1);
            }, 500);
        }

        function exporterJournalisationCSV() {
            const params = new URLSearchParams();

            const typeAction = document.getElementById('filtre-type-action')?.value;
            if (typeAction) params.append('type_action', typeAction);

            const dateDebut = document.getElementById('filtre-date-debut')?.value;
            if (dateDebut) params.append('date_debut', new Date(dateDebut).toISOString());

            const dateFin = document.getElementById('filtre-date-fin')?.value;
            if (dateFin) params.append('date_fin', new Date(dateFin).toISOString());

            const search = document.getElementById('recherche-journalisation')?.value;
            if (search) params.append('search', search);

            window.location.href = `/aef/api/journalisation/export-csv/?${params.toString()}`;
            
            alert('📥 Export CSV en cours de téléchargement...');
        }

        function getBadgeClassForAction(typeAction) {
            const mapping = {
                'CONNEXION': 'success',
                'DECONNEXION': 'secondary',
                'UPLOAD_FICHIER': 'primary',
                'GENERATION_LIEN': 'warning',
                'MODIFICATION_UTILISATEUR': 'info',
                'AUTRE': 'secondary'
            };
            return mapping[typeAction] || 'secondary';
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

        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            chargerDashboard();
        });

// ==========================================
// GESTION DES UTILISATEURS UEF - ACTIVATION/DÉSACTIVATION
// ==========================================

/**
 * Activer un utilisateur UEF
 */
async function activerUtilisateurUEF(userId) {
    if (!confirm('Êtes-vous sûr de vouloir activer cet utilisateur ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/aef/api/utilisateur-uef/${userId}/activer/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Recharger la liste des utilisateurs
            chargerUtilisateursUEF();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Une erreur est survenue lors de l\'activation de l\'utilisateur.');
    }
}

/**
 * Désactiver un utilisateur UEF
 */
async function desactiverUtilisateurUEF(userId) {
    if (!confirm('⚠️ Êtes-vous sûr de vouloir désactiver cet utilisateur ? Il ne pourra plus se connecter.')) {
        return;
    }
    
    try {
        const response = await fetch(`/aef/api/utilisateur-uef/${userId}/desactiver/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Recharger la liste des utilisateurs
            chargerUtilisateursUEF();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Une erreur est survenue lors de la désactivation de l\'utilisateur.');
    }
}

// ==========================================
// MODIFICATION DE LA FONCTION afficherUtilisateursUEF
// ==========================================
// Remplacer la fonction existante par celle-ci :

function afficherUtilisateursUEF(utilisateurs) {
    const tbody = document.querySelector('#table-utilisateurs-uef tbody');
    
    if (utilisateurs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Aucun utilisateur</td></tr>';
        return;
    }
    
    tbody.innerHTML = utilisateurs.map(u => {
        // Formater la dernière connexion
        let derniereConnexion = 'Jamais';
        if (u.derniere_connexion) {
            const date = new Date(u.derniere_connexion);
            derniereConnexion = date.toLocaleString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // Bouton d'action selon le statut
        const boutonAction = u.is_active 
            ? `<button class="btn btn-danger" onclick="desactiverUtilisateurUEF(${u.id})" title="Désactiver cet utilisateur">
                   🔒 Désactiver
               </button>`
            : `<button class="btn btn-success" onclick="activerUtilisateurUEF(${u.id})" title="Activer cet utilisateur">
                   🔓 Activer
               </button>`;
        
        return `
            <tr>
                <td>${u.prenom} ${u.nom}</td>
                <td>${u.email}</td>
                <td>${u.telephone || '-'}</td>
                <td><span class="badge badge-${u.is_active ? 'success' : 'danger'}">${u.is_active ? 'Actif' : 'Inactif'}</span></td>
                <td>${new Date(u.date_joined).toLocaleDateString('fr-FR')}</td>
                <td>${derniereConnexion}</td>
                <td>
                    ${boutonAction}
                </td>
            </tr>
        `;
    }).join('');
}


// ==========================================
// GESTION DES SOUMISSIONS - SUPPRESSION
// ==========================================

/**
 * Supprimer une soumission (seulement si EN_COURS)
 */
async function supprimerSoumission(fichierId) {
    if (!confirm('⚠️ Êtes-vous sûr de vouloir supprimer cette soumission ? Cette action est irréversible !')) {
        return;
    }
    
    try {
        const response = await fetch(`/aef/api/soumission/${fichierId}/supprimer/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Recharger l'historique
            chargerHistorique();
            // Recharger le dashboard pour mettre à jour les stats
            chargerDashboard();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Une erreur est survenue lors de la suppression de la soumission.');
    }
}

// ==========================================
// MODIFICATION DE LA FONCTION afficherHistorique
// ==========================================
// Remplacer la fonction existante par celle-ci :

function afficherHistorique(soumissions) {
    const tbody = document.querySelector('#table-historique tbody');
    
    if (soumissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Aucune soumission trouvée</td></tr>';
        return;
    }
    
    tbody.innerHTML = soumissions.map(s => {
        // Définir le bouton de suppression (seulement si EN_COURS)
        let boutonSuppression = '';
        if (s.statut === 'EN_COURS') {
            boutonSuppression = `
                <button class="btn btn-danger" onclick="supprimerSoumission(${s.id})" title="Supprimer cette soumission">
                    🗑️ Supprimer
                </button>
            `;
        }
        
        return `
            <tr>
                <td>${s.nom_fichier}</td>
                <td>${new Date(s.date_import).toLocaleString('fr-FR')}</td>
                <td><span class="badge badge-${s.statut_class}">${s.statut_display}</span></td>
                <td>${s.total_lignes}</td>
                <td>${s.commentaire || '-'}</td>
                <td>
                    <button class="btn btn-primary" onclick="voirDetailsSoumission(${s.id})">
                        👁️ Détails
                    </button>
                    ${boutonSuppression}
                </td>
            </tr>
        `;
    }).join('');
}


// ==========================================
// MODIFICATION DE LA FONCTION afficherDernieresSoumissions (DASHBOARD)
// ==========================================
// Remplacer la fonction existante par celle-ci :

function afficherDernieresSoumissions(soumissions) {
    const tbody = document.querySelector('#table-dernieres-soumissions tbody');
    
    if (soumissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune soumission</td></tr>';
        return;
    }
    
    tbody.innerHTML = soumissions.map(s => {
        // Définir le bouton de suppression (seulement si EN_COURS)
        let boutonSuppression = '';
        if (s.statut === 'EN_COURS') {
            boutonSuppression = `
                <button class="btn btn-danger" onclick="supprimerSoumission(${s.id})" title="Supprimer cette soumission">
                    🗑️
                </button>
            `;
        }
        
        return `
            <tr>
                <td>${s.nom_fichier}</td>
                <td>${new Date(s.date_import).toLocaleString('fr-FR')}</td>
                <td><span class="badge badge-${s.statut_class}">${s.statut_display}</span></td>
                <td>${s.total_lignes}</td>
                <td>
                    <button class="btn btn-primary" onclick="voirDetailsSoumission(${s.id})">
                        👁️ Voir
                    </button>
                    ${boutonSuppression}
                </td>
            </tr>
        `;
    }).join('');
}

// ==================== GESTION DU DRAG AND DROP ====================
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('dragover');
            }, false);
        });

        dropZone.addEventListener('drop', function(e) {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('fichier').files = files;
                handleFileSelectForPreview(files);
            }
        }, false);

        // Rendre toute la zone cliquable
        dropZone.addEventListener('click', function(e) {
            if (e.target === dropZone || e.target.closest('.upload-icon') || e.target.closest('.upload-zone-title') || e.target.closest('.upload-zone-text') || e.target.closest('.upload-zone-info')) {
                document.getElementById('fichier').click();
            }
        });
    }
});

// ==================== FONCTION POUR RETIRER LE FICHIER ====================
function removeFile() {
    document.getElementById('fichier').value = '';
    document.getElementById('fileSelected').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('submitBtn').style.display = 'none';
    document.getElementById('previewSection').classList.remove('active');
}

// ==================== PRÉVISUALISATION DU FICHIER ====================

let currentSheetNames = [];

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
    const maxRows = Math.min(jsonData.length, 101); // 1 pour l'en-tête + 100 lignes
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

// ==================== FORMATER LA TAILLE DU FICHIER ====================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}