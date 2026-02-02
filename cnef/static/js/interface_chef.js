// Fonction pour soumettre le formulaire et rester sur le même onglet
        function submitFormAndStay() {
            localStorage.setItem('activeTab', 'submissions');
            document.getElementById('filterForm').submit();
        }

        // Fonction pour filtrer par statut
        function filterByStatut(statut) {
            document.getElementById('statut').value = statut;
            submitFormAndStay();
        }

        // Restaurer l'onglet actif au chargement
        document.addEventListener('DOMContentLoaded', function() {
            const activeTab = localStorage.getItem('activeTab');
            if (activeTab === 'submissions') {
                switchToSubmissionsTab();
            }
            // Charger les données dynamiques
            loadFiles();
            loadUsers();
        })

        function switchToSubmissionsTab() {
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            const submissionsTab = document.querySelector('.nav-tab[onclick="switchTab(\'submissions\')"]');
            const submissionsPane = document.getElementById('submissions');
            if (submissionsTab && submissionsPane) {
                submissionsTab.classList.add('active');
                submissionsPane.classList.add('active');
            }
        }

        // Charger les fichiers pour l'onglet Téléchargements
        function loadFiles() {
            fetch('/chef/api/fichiers/')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const filesTable = document.getElementById('filesTable');
                        filesTable.innerHTML = '';
                        data.fichiers.forEach(file => {
                            const row = document.createElement('tr');
                            row.id = `file-${file.id}`;
                            row.innerHTML = `
                                <td>${file.name}</td>
                                <td>${file.user}</td>
                                <td>${new Date(file.date).toLocaleString('fr-FR', {
                                    day: '2-digit',
                                    month: '2-digit',
                                    year: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    hour12: false
                                })}</td>
                                <td>${file.size}</td>
                                <td>
                                    <button class="btn btn-delete" onclick="supprimerFichier(${file.id}, '${file.name}')">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <polyline points="3 6 5 6 21 6"/>
                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                        <line x1="10" y1="11" x2="10" y2="17"/>
                                        <line x1="14" y1="11" x2="14" y2="17"/>
                                    </svg>
                                    </button>
                                    <button class="btn btn-telecharger" onclick="telechargerFichier(${file.id})">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                                            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <circle cx="12" cy="12" r="9"/>
                                            <line x1="12" y1="6" x2="12" y2="14"/>
                                            <polyline points="9 11 12 14 15 11"/>
                                        </svg>

                                    </button>
                                </td>
                            `;
                            filesTable.appendChild(row);
                        });
                        if (data.fichiers.length === 0) {
                            filesTable.innerHTML = '<tr><td colspan="5">Aucun fichier disponible</td></tr>';
                        }
                    } else {
                        document.getElementById('filesTable').innerHTML = '<tr><td colspan="5">Erreur lors du chargement des fichiers</td></tr>';
                    }
                })
                .catch(error => {
                    document.getElementById('filesTable').innerHTML = '<tr><td colspan="5">Erreur réseau: ' + error.message + '</td></tr>';
                });
        }

        // Fonction pour télécharger un fichier original
        function telechargerFichier(fichierId) {
            showLoading(true);
            
            // Créer un lien de téléchargement temporaire
            const downloadLink = document.createElement('a');
            downloadLink.href = `/chef/telecharger-fichier/${fichierId}/`;
            downloadLink.style.display = 'none';
            document.body.appendChild(downloadLink);
            
            // Simuler le clic sur le lien
            downloadLink.click();
            
            // Nettoyer
            document.body.removeChild(downloadLink);
            showLoading(false);
            
            // Optionnel: afficher un message de confirmation
            showAlert('Téléchargement démarré', 'success');
        }
      
        // Charger les utilisateurs pour l'onglet Gestion Utilisateurs
        function loadUsers() {
            fetch('/chef/api/etablissements/')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const usersTable = document.getElementById('usersTable');
                        usersTable.innerHTML = '';
                        data.utilisateurs.forEach(user => {
                            const row = document.createElement('tr');
                            row.id = `user-${user.id}`;
                            row.innerHTML = `
                                <td>${user.name}</td>
                                <td>${user.email}</td>
                                <td>${new Date(user.signup).toLocaleDateString('fr-FR')}</td>
                                <td>${user.lastUpload ? new Date(user.lastUpload).toLocaleDateString('fr-FR') : 'Aucun'}</td>
                                <td><span class="status-badge ${user.status === 'Actif' ? 'status-success' : 'status-pending'}">${user.status}</span></td>
                                <td>
                                    <button class="btn btn-delete" onclick="supprimerEtablissement(${user.id}, '${user.name}')">bannir</button>
                                </td>
                            `;
                            usersTable.appendChild(row);
                        });
                        if (data.utilisateurs.length === 0) {
                            usersTable.innerHTML = '<tr><td colspan="6">Aucun utilisateur disponible</td></tr>';
                        }
                    } else {
                        document.getElementById('usersTable').innerHTML = '<tr><td colspan="6">Erreur lors du chargement des utilisateurs</td></tr>';
                    }
                })
                .catch(error => {
                    document.getElementById('usersTable').innerHTML = '<tr><td colspan="6">Erreur réseau: ' + error.message + '</td></tr>';
                });
        }

        // Fonction pour supprimer un fichier
        function supprimerFichier(fichierId, nomFichier) {
            if (!confirm(`Voulez-vous vraiment supprimer le fichier "${nomFichier}" ? Cette action est irréversible.`)) {
                return;
            }
            
            showLoading(true);
            
            fetch(`/chef/api/supprimer-fichier/${fichierId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                if (data.success) {
                    showAlert(data.message, 'success');
                    // Supprimer la ligne du tableau
                    const row = document.getElementById(`file-${fichierId}`);
                    if (row) {
                        row.remove();
                    }
                    // Recharger les stats si nécessaire
                    refreshStats();
                } else {
                    showAlert(data.message, 'error');
                }
            })
            .catch(error => {
                showLoading(false);
                showAlert('Erreur réseau: ' + error.message, 'error');
            });
        }

        // Fonction pour supprimer un établissement
        function supprimerEtablissement(etablissementId, nomEtablissement) {
            if (!confirm(`Voulez-vous vraiment supprimer l'établissement "${nomEtablissement}" ? Cette action est irréversible.`)) {
                return;
            }
            
            showLoading(true);
            
            fetch(`/chef/api/supprimer-etablissement/${etablissementId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                if (data.success) {
                    showAlert(data.message, 'success');
                    // Supprimer la ligne du tableau
                    const row = document.getElementById(`user-${etablissementId}`);
                    if (row) {
                        row.remove();
                    }
                } else {
                    showAlert(data.message, 'error');
                }
            })
            .catch(error => {
                showLoading(false);
                showAlert('Erreur réseau: ' + error.message, 'error');
            });
        }

        // Fonction utilitaire pour récupérer le token CSRF
        function getCSRFToken() {
            // Méthode 1 : Chercher dans le DOM (input hidden)
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput && csrfInput.value) {
                console.log('CSRF token trouvé dans le DOM:', csrfInput.value.substring(0, 10) + '...');
                return csrfInput.value;
            }
            
            // Méthode 2 : Chercher dans les cookies
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    console.log('CSRF token trouvé dans les cookies:', value.substring(0, 10) + '...');
                    return decodeURIComponent(value);
                }
            }
            
            // Méthode 3 : Chercher dans les meta tags
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta && csrfMeta.content) {
                console.log('CSRF token trouvé dans meta:', csrfMeta.content.substring(0, 10) + '...');
                return csrfMeta.content;
            }
            
            console.error('⚠️ AUCUN CSRF TOKEN TROUVÉ !');
            // Tentative de dernière chance : vérifier la variable globale
            if (typeof csrfToken !== 'undefined' && csrfToken) {
                console.log('CSRF token trouvé dans variable globale');
                return csrfToken;
            }
            
            return '';
        }

        const csrfToken = '{{ csrf_token }}';

        function refreshStats() {
            fetch('/chef/stats/')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.querySelector('.stat-card-soumission.total .stat-number-soumission').textContent = data.stats.total;
                        document.querySelector('.stat-card-soumission.en-attente .stat-number-soumission').textContent = data.stats.en_attente;
                        document.querySelector('.stat-card-soumission.reussi .stat-number-soumission').textContent = data.stats.reussis;
                        // NOUVEAU: Ajouter les stats de rejet
                        const rejeteCard = document.querySelector('.stat-card-soumission.rejete .stat-number-soumission');
                        if (rejeteCard && data.stats.rejetes !== undefined) {
                            rejeteCard.textContent = data.stats.rejetes;
                        }
                    }
                });
        }

        function validerSoumission(fichierId) {
            showLoading(true);
            
            // 🔥 CORRECTION : Utiliser getCSRFToken() au lieu de getCookie()
            const csrfToken = getCSRFToken();
            
            console.log('CSRF Token:', csrfToken); // DEBUG
            
            fetch(`/chef/valider/${fichierId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,  // ✅ Bon format
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                if (data.success) {
                    showAlert('✓ ' + data.message, 'success');
                    updateSoumissionUI(fichierId, data);
                    refreshStats();  // Rafraîchir les stats
                } else {
                    showAlert('✗ ' + data.message, 'error');
                }
            })
            .catch(error => {
                showLoading(false);
                showAlert('✗ Erreur réseau: ' + error.message, 'error');
            });
        }
        

        function ouvrirModalRejet(fichierId) {
            document.getElementById('fichierIdRejet').value = fichierId;
            document.getElementById('modalRejet').style.display = 'block';
        }

        function fermerModalRejet() {
            document.getElementById('modalRejet').style.display = 'none';
            document.getElementById('raisonRejet').value = '';
        }
       // Fonction pour rejeter un fichier
       // Variable globale pour stocker les données du rejet
        let rejetDataFichier = {};

        // Fonction pour rejeter un fichier - Ouvre le modal
        function rejeterFichier(fichierId, nomFichier) {
            // Stocker les données
            rejetDataFichier = { fichierId, nomFichier };
            
            // Afficher le nom du fichier dans le modal
            document.getElementById('nomFichierARejeter').textContent = nomFichier || 'Fichier sans nom';
            
            // Réinitialiser le textarea et cacher l'erreur
            document.getElementById('motifRejet').value = '';
            document.getElementById('motifError').style.display = 'none';
            
            // Ouvrir le modal
            document.getElementById('modalRejetSoumission').style.display = 'block';
        }

        // Fonction pour fermer le modal de rejet
        function fermerModalRejetSoumission() {
            document.getElementById('modalRejetSoumission').style.display = 'none';
            document.getElementById('motifRejet').value = '';
            document.getElementById('motifError').style.display = 'none';
        }


        // Fonction pour exécuter le rejet 
        function executerRejetSoumission() {
            const motif = document.getElementById('motifRejet').value.trim();
            const errorElement = document.getElementById('motifError');
            
            // Validation du motif
            if (!motif) {
                errorElement.style.display = 'block';
                document.getElementById('motifRejet').focus();
                return;
            }
            
            const { fichierId } = rejetDataFichier;

            // Désactiver le bouton de confirmation pendant le traitement
            const btnConfirm = document.querySelector('#modalRejetSoumission .btn-confirm-suppression');
            btnConfirm.disabled = true;
            btnConfirm.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 8px;"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>⏳ Traitement en cours...';

            // ✅ CORRECTION : Utiliser getCSRFToken() au lieu de getCookie()
            fetch(`/chef/rejeter/${fichierId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),  // ✅ CORRIGÉ ICI
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ raison: motif })
            })
            .then(response => response.json())
            .then(data => {
                // Fermer le modal
                fermerModalRejetSoumission();
                
                if (data.success) {
                    // Afficher une notification plus élégante
                    showAlert(`✅ ${data.message}`, 'success');
                    
                    // Mettre à jour l'interface
                    const soumissionElement = document.getElementById(`soumission-${fichierId}`);
                    if (soumissionElement) {
                        const statutBadge = soumissionElement.querySelector('.statut-badge');
                        statutBadge.className = 'statut-badge statut-rejete';
                        statutBadge.textContent = 'Rejeté';
                        
                        const actionButtons = soumissionElement.querySelector('.action-buttons');
                        actionButtons.innerHTML = `
                            <a href="/chef/detail/${fichierId}/" class="btn btn-details">Détails</a>
                            <button class="btn" disabled>Traité</button>
                        `;
                    }
                    
                    // Rafraîchir les statistiques
                    refreshStats();
                    
                    // Recharger après un court délai
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    showAlert(`❌ Erreur: ${data.message}`, 'error');
                    btnConfirm.disabled = false;
                    btnConfirm.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 8px;"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>Confirmer le rejet';
                }
            })
            .catch(error => {
                fermerModalRejetSoumission();
                showAlert(`❌ Erreur réseau lors du rejet: ${error.message}`, 'error');
                btnConfirm.disabled = false;
                btnConfirm.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 8px;"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>Confirmer le rejet';
            });
        }


        function updateSoumissionUI(fichierId, data) {
            const soumissionElement = document.getElementById(`soumission-${fichierId}`);
            if (soumissionElement) {
                const statutBadge = soumissionElement.querySelector('.statut-badge');
                const statutClass = data.statut.toLowerCase().replace(/\s+/g, '_');
                statutBadge.className = `statut-badge statut-${statutClass}`;
                statutBadge.textContent = data.statut;
                
                const actionButtons = soumissionElement.querySelector('.action-buttons');
                actionButtons.innerHTML = `
                    <a href="/chef/detail/${fichierId}/" class="btn btn-details">Détails</a>
                    <button class="btn" disabled>Traité</button>
                `;
                
                if (data.total_lignes !== undefined) {
                    const lignesElement = soumissionElement.children[3];
                    lignesElement.textContent = data.total_lignes;
                }
            }
        }               
        
        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }

        function showAlert(message, type) {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alert.style.position = 'fixed';
            alert.style.top = '20px';
            alert.style.right = '20px';
            alert.style.zIndex = '1001';
            alert.style.minWidth = '300px';
            document.body.appendChild(alert);
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }

        // Gestion des bases de données
        let modeleActuel = null;
        let donneesActuelles = [];
        let pageActuelle = 1;
        let totalPages = 1;

        // Fonction pour charger un modèle
        function chargerModele(nomModele) {
            modeleActuel = nomModele;
            pageActuelle = 1; // Réinitialiser la page
            
            // Mettre à jour les boutons actifs
            document.querySelectorAll('.modele-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Afficher l'en-tête
            document.getElementById('donnees-header').style.display = 'block';
            
            // Mettre à jour le titre
            const titres = {
                'Credit_Amortissables': 'Crédits Amortissables',
                'Decouverts': 'Découverts', 
                'Affacturage': 'Affacturage',
                'Cautions': 'Cautions',
                'Effets_commerces': 'Effets de Commerce',
                'Spots' : 'Spots'
            };
            document.getElementById('titre-modele').textContent = titres[nomModele];
            
            // Réinitialiser les filtres
            document.getElementById('filtre-sigle').value = '';
            document.getElementById('filtre-mois').value = '';
            
            // Charger les données
            chargerDonnees();
        }

        // Fonction pour charger les données avec filtres
        function chargerDonnees() {
            if (!modeleActuel) return;
            
            // Afficher le chargement
            document.getElementById('donnees-content').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Chargement des données...</p>
                </div>
            `;
            
            // Récupérer les valeurs des filtres
            const filtreSigle = document.getElementById('filtre-sigle').value;
            const filtreMois = document.getElementById('filtre-mois').value;
            const filtreAnnee = document.getElementById('filtre-annee').value;
            
            // Construire l'URL avec les paramètres
            let url = `/chef/bases-donnees/${modeleActuel}/?page=${pageActuelle}&page_size=25`;
            
            if (filtreSigle) {
                url += `&sigle=${encodeURIComponent(filtreSigle)}`;
            }
            
            if (filtreMois) {
                url += `&mois=${encodeURIComponent(filtreMois)}`;
            }


            // Le filtre année
            if (filtreAnnee) {
                url += `&annee=${encodeURIComponent(filtreAnnee)}`;
            }
            
            // Charger les données depuis le backend
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        donneesActuelles = data.donnees;
                        afficherDonnees(donneesActuelles);
                        
                        // Mettre à jour la pagination
                        const total = data.total;
                        const pageSize = data.page_size;
                        totalPages = Math.ceil(total / pageSize);
                        afficherPagination(total, pageSize);
                        
                        // Peupler le filtre des sigles (seulement au premier chargement)
                        if (!filtreSigle) {
                            peuplerFiltreSigles(data.sigles_distincts || []);
                        }
                        // NOUVEAU: Peupler le filtre années
                        if (!filtreAnnee) {
                            peuplerFiltreAnnees(data.annees_distinctes || []);
                        }
                    } else {
                        throw new Error(data.message);
                    }
                })
                .catch(error => {
                    document.getElementById('donnees-content').innerHTML = `
                        <div class="alert alert-error">
                            Erreur lors du chargement: ${error.message}
                        </div>
                    `;
                });
        }

        // Fonction pour peupler le filtre des sigles
        function peuplerFiltreSigles(sigles_distincts) {
            const filtreSigle = document.getElementById('filtre-sigle');
            
            // Vider et remplir le filtre
            filtreSigle.innerHTML = '<option value="">Tous les établissement</option>';
            
            if (sigles_distincts && sigles_distincts.length > 0) {
                sigles_distincts.forEach(sigle => {
                    if (sigle) {  // Ignorer les valeurs null/vides
                        const option = document.createElement('option');
                        option.value = sigle;
                        option.textContent = sigle;
                        filtreSigle.appendChild(option);
                    }
                });
            }
        }

        // Peupler le filtre des années
        function peuplerFiltreAnnees(annees_distinctes) {
            const filtreAnnee = document.getElementById('filtre-annee');
            
            // Vider et remplir le filtre
            filtreAnnee.innerHTML = '<option value="">Toutes les années</option>';
            
            if (annees_distinctes && annees_distinctes.length > 0) {
                annees_distinctes.forEach(annee => {
                    if (annee) {
                        const option = document.createElement('option');
                        option.value = annee;
                        option.textContent = annee;
                        filtreAnnee.appendChild(option);
                    }
                });
            }
        }

        // Fonction pour appliquer les filtres (appelée lors du changement)
        function appliquerFiltres() {
            pageActuelle = 1; // Réinitialiser à la page 1 lors du filtrage
            chargerDonnees();
        }

        // Fonction pour afficher les données dans un tableau
        function afficherDonnees(donnees) {
            if (donnees.length === 0) {
                document.getElementById('donnees-content').innerHTML = `
                    <div class="placeholder-message">
                        <p>Aucune donnée trouvée pour cette base avec les filtres sélectionnés.</p>
                    </div>
                `;
                return;
            }
            
            // Créer le tableau
            let html = `
                <div class="table-responsive">
                    <table class="donnees-table">
                        <thead>
                            <tr>
            `;
            
            // En-têtes de colonnes (basés sur le premier élément)
            const premierItem = donnees[0];
            for (const key in premierItem) {
                if (premierItem.hasOwnProperty(key)) {
                    html += `<th>${key}</th>`;
                }
            }
            
            html += `</tr></thead><tbody>`;
            
            // Données
            donnees.forEach(item => {
                html += `<tr>`;
                for (const key in item) {
                    if (item.hasOwnProperty(key)) {
                        let valeur = item[key];
                        // Formater les dates
                        if (valeur && typeof valeur === 'string' && valeur.includes('T')) {
                            valeur = new Date(valeur).toLocaleDateString('fr-FR');
                        }
                        html += `<td>${valeur !== null && valeur !== undefined ? valeur : ''}</td>`;
                    }
                }
                html += `</tr>`;
            });
            
            html += `</tbody></table></div>`;
            
            document.getElementById('donnees-content').innerHTML = html;
        }

        // Fonction pour afficher la pagination
        function afficherPagination(total, pageSize) {
            const paginationHTML = `
                <div class="pagination">
                    <div class="pagination-info">
                        Affichage de ${((pageActuelle - 1) * pageSize) + 1} à ${Math.min(pageActuelle * pageSize, total)} sur ${total} enregistrements
                    </div>
                    <div class="pagination-controls">
                        <button class="pagination-btn" onclick="changerPage(1)" ${pageActuelle === 1 ? 'disabled' : ''}>
                            ««
                        </button>
                        <button class="pagination-btn" onclick="changerPage(${pageActuelle - 1})" ${pageActuelle === 1 ? 'disabled' : ''}>
                            «
                        </button>
                        <span style="margin: 0 10px;">Page ${pageActuelle} sur ${totalPages}</span>
                        <button class="pagination-btn" onclick="changerPage(${pageActuelle + 1})" ${pageActuelle === totalPages ? 'disabled' : ''}>
                            »
                        </button>
                        <button class="pagination-btn" onclick="changerPage(${totalPages})" ${pageActuelle === totalPages ? 'disabled' : ''}>
                            »»
                        </button>
                    </div>
                </div>
            `;
            
            document.getElementById('donnees-content').innerHTML += paginationHTML;
        }

        function telechargerExcel() {
            if (!modeleActuel) {
                alert('Veuillez sélectionner un modèle d\'abord.');
                return;
            }
            const filtreSigle = document.getElementById('filtre-sigle').value;
            const filtreMois = document.getElementById('filtre-mois').value;
            const filtreAnnee = document.getElementById('filtre-annee').value;
            
            
            let url = `/chef/bases-donnees/${modeleActuel}/?format=xlsx`;
        
            if (filtreSigle) {
                url += `&sigle=${encodeURIComponent(filtreSigle)}`;
            }
            if (filtreMois) {
                url += `&mois=${encodeURIComponent(filtreMois)}`;
            }

            if (filtreAnnee) {
                url += `&annee=${encodeURIComponent(filtreAnnee)}`;
            }
            window.location.href = url;
        }

        // Fonction pour télécharger les données en Excel
        function telechargerDonneesExcel() {
            if (!modeleActuel) {
                alert('Veuillez d\'abord sélectionner un modèle de données.');
                return;
            }

            // Récupérer les filtres actuels
            const filtreSigle = document.getElementById('filtre-sigle').value;
            const filtreMois = document.getElementById('filtre-mois').value;
            const filtreAnnee = document.getElementById('filtre-annee').value;
            // Construire l'URL avec les paramètres de filtre
            let url = `/chef/bases-donnees/${modeleActuel}/?format=xlsx`;
            
            if (filtreSigle) {
                url += `&sigle=${encodeURIComponent(filtreSigle)}`;
            }
            
            if (filtreMois) {
                url += `&mois=${encodeURIComponent(filtreMois)}`;
            }
            if (filtreAnnee) {
                url += `&annee=${encodeURIComponent(filtreAnnee)}`;
            }

            
            // Télécharger le fichier
            window.location.href = url;
        }

        // Fonction pour changer de page
        function changerPage(nouvellePage) {
            if (nouvellePage < 1 || nouvellePage > totalPages) return;
            pageActuelle = nouvellePage;
            chargerDonnees();
        }

        // ==========================================
        // GESTION DES ONGLETS
        // ==========================================

        function switchTab(tabName) {
            // Retirer la classe active de tous les onglets
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            
            // Retirer la classe active de tous les contenus d'onglets
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            // Trouver le bouton cliqué et lui ajouter la classe active
            const clickedTab = document.querySelector(`button[onclick*="${tabName}"]`);
            if (clickedTab) {
                clickedTab.classList.add('active');
            }
            
            // Afficher l'onglet sélectionné
            const selectedTab = document.getElementById(tabName);
            if (selectedTab) {
                selectedTab.classList.add('active');
            }
            
            // Sauvegarder l'onglet actif
            localStorage.setItem('activeTab', tabName);
            
            // Charger les données selon l'onglet
            if (tabName === 'etablissements') {
                chargerEtablissements();
            } else if (tabName === 'downloads') {
                loadFiles();
            } else if (tabName === 'bases_donnees') {
                loadDatabases();
            } else if (tabName === 'utilisateurs') {
                chargerUtilisateurs();
            } else if (tabName === 'journalisation') {
                chargerJournalisation();
            } else if (tabName === 'historique-emails') {
                chargerHistoriqueEmails();
            }
        }

       

        // Fermer les modals en cliquant en dehors
        window.addEventListener('click', function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        });

        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        };

        // ==========================================
        // GESTION DES ÉTABLISSEMENTS
        // ==========================================

        // Charger la liste au démarrage
        document.addEventListener('DOMContentLoaded', function() {
            chargerEtablissements();
        });

        // Fonction pour afficher les alertes
        function afficherAlerte(message, type = 'success') {
            const container = document.getElementById('alertContainer');
            const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
            container.innerHTML = `
                <div class="alert ${alertClass}">
                    ${message}
                </div>
            `;
            setTimeout(() => {
                container.innerHTML = '';
            }, 5000);
        }

        // Toggle catégorie EMF
        function toggleCategorieEMF() {
            const type = document.getElementById('type_etablissement').value;
            const categorieGroup = document.getElementById('categorieGroup');
            const categorieSelect = document.getElementById('categorie_emf');
            
            if (type === 'EMF') {
                categorieGroup.style.display = 'block';
                categorieSelect.required = true;
            } else {
                categorieGroup.style.display = 'none';
                categorieSelect.required = false;
                categorieSelect.value = '';
            }
        }

        // Ouvrir modal de création
        function ouvrirModalCreation() {
            document.getElementById('modalCreation').style.display = 'block';
        }

        // Fermer modal de création
        function fermerModalCreation() {
            document.getElementById('modalCreation').style.display = 'none';
            document.getElementById('formCreation').reset();
            document.getElementById('categorieGroup').style.display = 'none';
        }

        // Créer un établissement
        function creerEtablissement(event) {
            event.preventDefault();
            
            const data = {
                Nom_etablissement: document.getElementById('Nom_etablissement').value,
                code_etablissement: document.getElementById('code_etablissement').value,
                type_etablissement: document.getElementById('type_etablissement').value,
                categorie_emf: document.getElementById('categorie_emf').value || null
            };
            
            fetch('/chef/api/etablissements/creer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    afficherAlerte(data.message, 'success');
                    fermerModalCreation();
                    chargerEtablissements();
                } else {
                    afficherAlerte(data.message, 'error');
                }
            })
            .catch(error => {
                afficherAlerte('Erreur lors de la création', 'error');
                console.error('Erreur:', error);
            });
        }

        // Charger tous les établissements
        // ==========================================
        // GESTION DES ÉTABLISSEMENTS - AVEC STATISTIQUES ET FILTRES
        // ==========================================

        // Variable globale pour stocker tous les établissements
        let tousLesEtablissements = [];

        // Fonction pour charger les établissements avec filtres
        function chargerEtablissements() {
            // Récupérer les valeurs des filtres
            const typeFiltre = document.getElementById('filtre-type-etablissement')?.value || '';
            const categorieFiltre = document.getElementById('filtre-categorie-emf')?.value || '';
            const statutFiltre = document.getElementById('filtre-statut-etablissement')?.value || '';
            
            // Construire l'URL avec les paramètres de filtre
            let url = '/chef/api/etablissements/liste/?';
            
            if (typeFiltre) {
                url += `type_etablissement=${encodeURIComponent(typeFiltre)}&`;
            }
            
            if (categorieFiltre) {
                url += `categorie_emf=${encodeURIComponent(categorieFiltre)}&`;
            }
            
            if (statutFiltre) {
                url += `is_active=${encodeURIComponent(statutFiltre)}&`;
            }
            
            fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    tousLesEtablissements = data.etablissements;
                    afficherEtablissements(data.etablissements);
                    
                    // Mettre à jour les statistiques
                    const stats = data.stats || calculerStatistiques(data.etablissements);
                    mettreAJourStatistiquesEtablissements(stats);
                } else {
                    afficherAlerte(data.message || 'Erreur lors du chargement des établissements', 'error');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                afficherAlerte('Erreur réseau lors du chargement des établissements', 'error');
            });
        }

        // Fonction pour calculer les statistiques côté client
        function calculerStatistiques(etablissements) {
            const stats = {
                total: etablissements.length,
                banques: 0,
                emf: 0,
                actifs: 0
            };
            
            etablissements.forEach(etab => {
                if (etab.type_etablissement === 'BANQUE' || etab.type === 'BANQUE') {
                    stats.banques++;
                } else if (etab.type_etablissement === 'EMF' || etab.type === 'EMF') {
                    stats.emf++;
                }
                
                if (etab.is_active) {
                    stats.actifs++;
                }
            });
            
            return stats;
        }

        // Fonction pour mettre à jour les statistiques
        function mettreAJourStatistiquesEtablissements(stats) {
            const totalElem = document.getElementById('stats-total-etablissements');
            const banquesElem = document.getElementById('stats-total-banques');
            const emfElem = document.getElementById('stats-total-emf');
            const actifsElem = document.getElementById('stats-etablissements-actifs');
            
            if (totalElem) totalElem.textContent = stats.total || 0;
            if (banquesElem) banquesElem.textContent = stats.banques || 0;
            if (emfElem) emfElem.textContent = stats.emf || 0;
            if (actifsElem) actifsElem.textContent = stats.actifs || 0;
        }

        // Afficher les établissements dans le tableau
        function afficherEtablissements(etablissements) {
            const tbody = document.getElementById('listeEtablissements');
            
            if (!tbody) return;
            
            if (etablissements.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 40px; color: #7f8c8d;">
                            <i class="fas fa-inbox" style="font-size: 3em; margin-bottom: 10px; display: block;"></i>
                            Aucun établissement trouvé
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = '';
            
            etablissements.forEach(etab => {
                const row = document.createElement('tr');
                row.id = `etab-${etab.id}`;
                
                // Déterminer l'affichage de la catégorie
                let categorieDisplay = '-';
                const typeEtab = etab.type_etablissement || etab.type;
                const categorieEMF = etab.categorie_emf || etab.categorie;
                
                if (typeEtab === 'EMF' && categorieEMF) {
                    categorieDisplay = categorieEMF === 'PREMIERE_CATEGORIE' ? '1ère Catégorie' : '2ème Catégorie';
                }
                
                // Nom de l'établissement
                const nomEtab = etab.Nom_etablissement || etab.nom;
                const codeEtab = etab.code_etablissement || etab.code;
                const nbUsers = etab.nombre_utilisateurs || etab.nb_total_utilisateurs || 0;
                const dateCreation = etab.date_creation ? new Date(etab.date_creation).toLocaleDateString('fr-FR') : '-';
                
                row.innerHTML = `
                    <td><strong>${codeEtab}</strong></td>
                    <td>${nomEtab}</td>
                    <td>
                        <span style="background: ${typeEtab === 'BANQUE' ? '#3498db' : '#9b59b6'}; 
                                     color: white; 
                                     padding: 4px 12px; 
                                     border-radius: 15px; 
                                     font-size: 0.85em;">
                            ${typeEtab}
                        </span>
                    </td>
                    <td>${categorieDisplay}</td>
                    <td>${nbUsers}</td>
                    <td>
                        <span class="badge ${etab.is_active ? 'badge-success' : 'badge-danger'}">
                            ${etab.is_active ? '✓ Actif' : '✗ Inactif'}
                        </span>
                    </td>
                    <td>${dateCreation}</td>
                    <td>
                        <button onclick="voirDetails(${etab.id})" 
                                style="background: #3498db; color: white; border: none; padding: 8px 12px; 
                                       border-radius: 6px; cursor: pointer; margin-right: 5px;">
                            <i class="fas fa-eye"></i> Détails
                        </button>
                        <button onclick="supprimerEtablissement(${etab.id}, '${nomEtab}')" 
                                style="background: #e74c3c; color: white; border: none; padding: 8px 12px; 
                                       border-radius: 6px; cursor: pointer;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }

        // Fonction de recherche
        function rechercherEtablissement() {
            const recherche = document.getElementById('recherche-etablissement')?.value.toLowerCase() || '';
            
            if (!recherche) {
                afficherEtablissements(tousLesEtablissements);
                return;
            }
            
            const etablissementsFiltres = tousLesEtablissements.filter(etab => {
                const nom = etab.Nom_etablissement || etab.nom || '';
                const code = etab.code_etablissement || etab.code || '';
                return nom.toLowerCase().includes(recherche) || code.toLowerCase().includes(recherche);
            });
            
            afficherEtablissements(etablissementsFiltres);
        }

        // Voir les détails d'un établissement
        function voirDetails(id) {
            fetch(`/chef/api/etablissements/${id}/details/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    afficherDetails(data);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                afficherAlerte('Erreur lors du chargement des détails', 'error');
            });
        }
        // Afficher les détails dans le modal
        function afficherDetails(data) {
            const etab = data.etablissement;
            const stats = data.statistiques;
            const users = data.utilisateurs;
            
            document.getElementById('detailsNom').textContent = etab.nom;
            
            const content = `
                <div>
                    <h3>Informations</h3>
                    <p><strong>Code:</strong> ${etab.code}</p>
                    <p><strong>Type:</strong> ${etab.type}</p>
                    <p><strong>Catégorie:</strong> ${etab.categorie}</p>
                    <p><strong>Statut:</strong> 
                        <span class="badge ${etab.is_active ? 'badge-success' : 'badge-danger'}">
                            ${etab.is_active ? 'Actif' : 'Inactif'}
                        </span>
                    </p>
                    <p><strong>Créé le:</strong> ${etab.date_creation}</p>
                    <p><strong>Modifié le:</strong> ${etab.date_modification}</p>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>${stats.nb_total}</h3>
                        <p>Total Utilisateurs</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.nb_aef}</h3>
                        <p>Admins (AEF)</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.nb_uef}</h3>
                        <p>Utilisateurs (UEF)</p>
                    </div>
                    <div class="stat-card">
                        <h3>${stats.nb_actifs}</h3>
                        <p>Comptes Actifs</p>
                    </div>
                </div>

                <div class="users-table">
                    <h3>Utilisateurs Associés (${users.length})</h3>
                    ${users.length > 0 ? `
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Nom</th>
                                    <th>Email</th>
                                    <th>Rôle</th>
                                    <th>Statut</th>
                                    <th>Dernière connexion</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${users.map(user => `
                                    <tr>
                                        <td>${user.prenom} ${user.nom}</td>
                                        <td>${user.email}</td>
                                        <td><span class="badge badge-info">${user.role}</span></td>
                                        <td>
                                            <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                                                ${user.is_active ? 'Actif' : 'Inactif'}
                                            </span>
                                        </td>
                                        <td>${user.derniere_connexion}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    ` : '<p class="empty-state">Aucun utilisateur associé</p>'}
                </div>
            `;
            
            document.getElementById('detailsContent').innerHTML = content;
            document.getElementById('modalDetails').style.display = 'block';
        }

        // Fermer modal détails
        function fermerModalDetails() {
            document.getElementById('modalDetails').style.display = 'none';
        }

        // Supprimer un établissement
        // Variables globales pour stocker les infos de suppression
        let etablissementASupprimer = { id: null, nom: '' };

        // Supprimer un établissement - Ouvre le modal de confirmation
        function supprimerEtablissement(id, nom) {
            etablissementASupprimer = { id: id, nom: nom };
            document.getElementById('nomEtablissementSuppr').textContent = nom;
            document.getElementById('modalConfirmationSuppression').style.display = 'block';
        }

        // Fermer le modal de confirmation
        function fermerModalConfirmationSuppression() {
            document.getElementById('modalConfirmationSuppression').style.display = 'none';
            etablissementASupprimer = { id: null, nom: '' };
        }

        // Confirmer la suppression définitive
        function confirmerSuppressionEtablissement() {
            const id = etablissementASupprimer.id;
            const nom = etablissementASupprimer.nom;
            
            if (!id) {
                return;
            }

            // Fermer le modal
            fermerModalConfirmationSuppression();
            
            // Effectuer la suppression
            fetch(`/chef/api/etablissements/${id}/supprimer/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    afficherAlerte(data.message, 'success');
                    chargerEtablissements();
                } else {
                    afficherAlerte(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                afficherAlerte('Erreur lors de la suppression', 'error');
            });
        }

        // Fermer le modal si on clique en dehors
        window.onclick = function(event) {
            const modal = document.getElementById('modalConfirmationSuppression');
            if (event.target === modal) {
                fermerModalConfirmationSuppression();
            }
        }

        

        // Fermer les modals en cliquant en dehors
        window.onclick = function(event) {
            const modalCreation = document.getElementById('modalCreation');
            const modalDetails = document.getElementById('modalDetails');
            
            if (event.target == modalCreation) {
                fermerModalCreation();
            }
            if (event.target == modalDetails) {
                fermerModalDetails();
            }
        }

        // ==========================================
        // JAVASCRIPT : GESTION DES UTILISATEURS ET JOURNALISATION
        // À ajouter dans interface_chef.html dans une balise <script>
        // ==========================================

        // Variables globales
        let paginationUtilisateurs = { page: 1, per_page: 20 };
        let paginationJournalisation = { page: 1, per_page: 50 };
        let rechercheUtilisateurTimeout;
        let rechercheJournalisationTimeout;

        // ==========================================
        // GESTION DES UTILISATEURS
        // ==========================================

        /**
        * Charge la liste des utilisateurs avec filtres et pagination
        */
        async function chargerUtilisateurs(page = 1) {
            paginationUtilisateurs.page = page;
            
            const tbody = document.getElementById('tbody-utilisateurs');
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 2em; color: #3498db;"></i>
                        <p style="margin-top: 10px; color: #7f8c8d;">Chargement...</p>
                    </td>
                </tr>
            `;

            try {
                // Construction des paramètres
                const params = new URLSearchParams({
                    page: paginationUtilisateurs.page,
                    per_page: paginationUtilisateurs.per_page
                });

                // Ajouter les filtres
                const role = document.getElementById('filtre-role-utilisateur')?.value;
                if (role) params.append('role', role);

                const etablissement = document.getElementById('filtre-etablissement-utilisateur')?.value;
                if (etablissement) params.append('etablissement', etablissement);

                const actif = document.getElementById('filtre-actif-utilisateur')?.value;
                if (actif) params.append('actif', actif);

                const search = document.getElementById('recherche-utilisateur')?.value;
                if (search) params.append('search', search);

                // Appel API
                const response = await fetch(`/chef/api/utilisateurs/?${params.toString()}`, {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();

                if (data.success) {
                    afficherUtilisateurs(data.utilisateurs);
                    afficherPaginationUtilisateurs(data.pagination);
                    afficherStatistiquesUtilisateurs(data.stats);
                } else {
                    throw new Error(data.message || 'Erreur lors du chargement');
                }
            } catch (error) {
                console.error('Erreur:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 40px; color: #e74c3c;">
                            <i class="fas fa-exclamation-circle" style="font-size: 2em;"></i>
                            <p style="margin-top: 10px;">Erreur : ${error.message}</p>
                        </td>
                    </tr>
                `;
            }
        }

        /**
        * Affiche les utilisateurs dans le tableau
        */
        function afficherUtilisateurs(utilisateurs) {
            const tbody = document.getElementById('tbody-utilisateurs');
            
            // ===== REMPLIR LE SELECT DES ÉTABLISSEMENTS =====
            const selectEtab = document.getElementById('filtre-etablissement-utilisateur');
            selectEtab.innerHTML = '<option value="">Tous les établissements</option>';
            
            const etablissementsMap = new Map();
            utilisateurs.forEach(user => {
                if (user.etablissement && user.etablissement.id) {
                    etablissementsMap.set(user.etablissement.id, user.etablissement);
                }
            });
            
            etablissementsMap.forEach(etab => {
                const option = document.createElement('option');
                option.value = etab.id;
                option.textContent = `${etab.nom} (${etab.code})`;
                selectEtab.appendChild(option);
            });
            // ===== FIN REMPLISSAGE SELECT =====
            
            if (!utilisateurs || utilisateurs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 40px;">
                            <i class="fas fa-users" style="font-size: 2em; color: #95a5a6;"></i>
                            <p style="margin-top: 10px; color: #7f8c8d;">Aucun utilisateur trouvé</p>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = utilisateurs.map(user => `
                <tr>
                    <td><strong>${user.prenom} ${user.nom}</strong></td>
                    <td>${user.email}</td>
                    <td>
                        <span class="badge badge-primary">${user.role_display}</span>
                    </td>
                    <td>
                        ${user.etablissement ? `
                            <div style="font-size: 13px;">
                                <strong>${user.etablissement.nom}</strong><br>
                                <span style="color: #7f8c8d;">${user.etablissement.code}</span>
                            </div>
                        ` : '<span style="color: #95a5a6;">N/A</span>'}
                    </td>
                    <td>${user.telephone || '<span style="color: #95a5a6;">N/A</span>'}</td>
                    <td>
                        <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                            ${user.is_active ? '✓ Actif' : '✗ Inactif'}
                        </span>
                    </td>
                    <td>${new Date(user.date_joined).toLocaleDateString('fr-FR')}</td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="bannirUtilisateur(${user.id}, '${user.prenom} ${user.nom}')" style="background: #e74c3c; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; margin-left: 5px;">
                                <i class="fas fa-ban"></i>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="8" r="4"/>
                                    <path d="M2 20c2-4 6-6 10-6s8 2 10 6"/>
                                    <line x1="18" y1="6" x2="22" y2="10"/>
                                    <line x1="22" y1="6" x2="18" y2="10"/>
                                </svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        /**
        * Affiche la pagination
        */
        function afficherPaginationUtilisateurs(pagination) {
            const container = document.getElementById('pagination-utilisateurs');
            
            if (!pagination || pagination.total_pages <= 1) {
                container.innerHTML = '';
                return;
            }

            let html = '<div style="display: flex; justify-content: center; align-items: center; gap: 10px;">';
            
            // Bouton précédent
            if (pagination.has_previous) {
                html += `<button class="btn-icon btn-view" onclick="chargerUtilisateurs(${pagination.page - 1})">
                    <i class="fas fa-chevron-left"></i>
                </button>`;
            }

            // Numéros de page
            for (let i = 1; i <= pagination.total_pages; i++) {
                if (i === pagination.page) {
                    html += `<button class="btn-primary" style="min-width: 40px;">${i}</button>`;
                } else if (Math.abs(i - pagination.page) <= 2 || i === 1 || i === pagination.total_pages) {
                    html += `<button class="btn-icon btn-view" onclick="chargerUtilisateurs(${i})" style="min-width: 40px;">${i}</button>`;
                } else if (Math.abs(i - pagination.page) === 3) {
                    html += '<span>...</span>';
                }
            }

            // Bouton suivant
            if (pagination.has_next) {
                html += `<button class="btn-icon btn-view" onclick="chargerUtilisateurs(${pagination.page + 1})">
                    <i class="fas fa-chevron-right"></i>
                </button>`;
            }

            html += `<span style="margin-left: 20px; color: #7f8c8d;">
                Page ${pagination.page} sur ${pagination.total_pages} (${pagination.total} utilisateurs)
            </span></div>`;

            container.innerHTML = html;
        }

        /**
        * Affiche les statistiques
        */
        function afficherStatistiquesUtilisateurs(stats) {
            if (!stats) return;
            
            document.getElementById('stats-total-utilisateurs').textContent = stats.total || 0;
            document.getElementById('stats-utilisateurs-actifs').textContent = stats.actifs || 0;
            document.getElementById('stats-utilisateurs-inactifs').textContent = stats.inactifs || 0;
            document.getElementById('stats-utilisateurs-etablissement').textContent = 
                (stats.par_role?.AEF || 0) + (stats.par_role?.UEF || 0);
        }

        /**
        * Recherche utilisateur avec debounce
        */
        function rechercherUtilisateur() {
            clearTimeout(rechercheUtilisateurTimeout);
            rechercheUtilisateurTimeout = setTimeout(() => {
                chargerUtilisateurs(1);
            }, 500);
        }

        /**
        * Ouvre le modal d'ajout d'utilisateur
        */
        function ouvrirModalAjoutUtilisateur() {
            document.getElementById('modal-ajout-utilisateur').style.display = 'flex';
            document.getElementById('form-ajout-utilisateur').reset();
            chargerEtablissementsPourSelect();
        }

        /**
        * Ferme le modal d'ajout
        */
        function fermerModalAjoutUtilisateur() {
            document.getElementById('modal-ajout-utilisateur').style.display = 'none';
        }

        /**
        * Toggle du champ établissement selon le rôle
        */
        function toggleEtablissementField() {
            const role = document.getElementById('input-role').value;
            const groupEtablissement = document.getElementById('group-etablissement');
            const inputEtablissement = document.getElementById('input-etablissement');
            const infoLien = document.getElementById('info-lien-inscription');
            
            if (role === 'AEF' || role === 'UEF') {
                groupEtablissement.style.display = 'block';
                inputEtablissement.required = true;
                infoLien.style.display = 'block';
            } else {
                groupEtablissement.style.display = 'none';
                inputEtablissement.required = false;
                infoLien.style.display = 'none';
            }
        }

        /**
        * Charge les établissements pour le select
        */
        async function chargerEtablissementsPourSelect() {
            try {
                const response = await fetch('/chef/api/etablissements/liste/');
                const data = await response.json();
                
                if (data.success) {
                    const selects = [
                        document.getElementById('input-etablissement'),
                        document.getElementById('filtre-etablissement-utilisateur'),
                        document.getElementById('input-etablissement-lien')
                    ];
                    
                    selects.forEach(select => {
                        if (select) {
                            const currentValue = select.value;
                            const firstOption = select.options[0];
                            
                            select.innerHTML = '';
                            select.appendChild(firstOption);
                            
                            data.etablissements.forEach(etab => {
                                const option = document.createElement('option');
                                option.value = etab.id;
                                option.textContent = `${etab.Nom_etablissement} (${etab.code_etablissement})`;
                                select.appendChild(option);
                            });
                            
                            if (currentValue) select.value = currentValue;
                        }
                    });
                }
            } catch (error) {
                console.error('Erreur lors du chargement des établissements:', error);
            }
        }

        /**
        * Ajoute un nouvel utilisateur
        */
        async function ajouterUtilisateur(event) {
            event.preventDefault();
            
            const form = event.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création...';
            
            try {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                const response = await fetch('/chef/api/utilisateurs/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    afficherNotification('success', result.message);
                    
                    // Afficher le lien d'inscription si disponible
                    if (result.lien_inscription) {
                        afficherLienGenere(result.lien_inscription, result.token_expiration);
                    }
                    
                    // Afficher le mot de passe temporaire pour ACNEF/UCNEF
                    if (result.mot_de_passe_temporaire) {
                        afficherNotification('info', 
                            `Mot de passe temporaire : <strong>${result.mot_de_passe_temporaire}</strong>`, 
                            10000
                        );
                    }
                    
                    fermerModalAjoutUtilisateur();
                    chargerUtilisateurs();
                } else {
                    afficherNotification('error', result.message);
                }
            } catch (error) {
                console.error('Erreur:', error);
                afficherNotification('error', 'Erreur lors de la création de l\'utilisateur');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }

        /**
        * Affiche les détails d'un utilisateur
        */
        async function afficherDetailsUtilisateur(userId) {
            const modal = document.getElementById('modal-details-utilisateur');
            const contenu = document.getElementById('contenu-details-utilisateur');
            
            modal.style.display = 'flex';
            contenu.innerHTML = '<p style="text-align: center; padding: 40px;"><i class="fas fa-spinner fa-spin"></i> Chargement...</p>';
            
            try {
                const response = await fetch(`/chef/api/utilisateurs/${userId}/`);
                const data = await response.json();
                
                if (data.success) {
                    const user = data.utilisateur;
                    
                    contenu.innerHTML = `
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div class="info-block">
                                <label>Prénom</label>
                                <p><strong>${user.prenom}</strong></p>
                            </div>
                            <div class="info-block">
                                <label>Nom</label>
                                <p><strong>${user.nom}</strong></p>
                            </div>
                            <div class="info-block">
                                <label>Email</label>
                                <p>${user.email}</p>
                            </div>
                            <div class="info-block">
                                <label>Téléphone</label>
                                <p>${user.telephone || 'N/A'}</p>
                            </div>
                            <div class="info-block">
                                <label>Rôle</label>
                                <p><span class="badge badge-primary">${user.role_display}</span></p>
                            </div>
                            <div class="info-block">
                                <label>Statut</label>
                                <p><span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                                    ${user.is_active ? '✓ Actif' : '✗ Inactif'}
                                </span></p>
                            </div>
                            ${user.etablissement ? `
                                <div class="info-block" style="grid-column: 1 / -1;">
                                    <label>Établissement</label>
                                    <p><strong>${user.etablissement.nom}</strong> (${user.etablissement.code})</p>
                                </div>
                            ` : ''}
                            <div class="info-block">
                                <label>Date de création</label>
                                <p>${new Date(user.date_joined).toLocaleString('fr-FR')}</p>
                            </div>
                            <div class="info-block">
                                <label>Dernière connexion</label>
                                <p>${user.derniere_connexion ? new Date(user.derniere_connexion).toLocaleString('fr-FR') : 'Jamais connecté'}</p>
                            </div>
                            ${user.cree_par ? `
                                <div class="info-block">
                                    <label>Créé par</label>
                                    <p>${user.cree_par.nom}</p>
                                </div>
                            ` : ''}
                            <div class="info-block">
                                <label>Nombre d'actions</label>
                                <p><strong>${user.nb_actions}</strong></p>
                            </div>
                        </div>
                        
                        <div style="margin-top: 30px; text-align: center;">
                            <button class="btn-danger" onclick="confirmerSuppressionUtilisateur(${user.id}, '${user.prenom} ${user.nom}')">
                                <i class="fas fa-trash"></i> Supprimer cet utilisateur
                            </button>
                        </div>
                    `;
                    
                    // Ajouter les styles pour info-block
                    if (!document.getElementById('style-info-block')) {
                        const style = document.createElement('style');
                        style.id = 'style-info-block';
                        style.textContent = `
                            .info-block label {
                                display: block;
                                font-size: 12px;
                                color: #7f8c8d;
                                text-transform: uppercase;
                                margin-bottom: 5px;
                                font-weight: 600;
                            }
                            .info-block p {
                                margin: 0;
                                font-size: 15px;
                                color: #2c3e50;
                            }
                        `;
                        document.head.appendChild(style);
                    }
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error('Erreur:', error);
                contenu.innerHTML = `
                    <p style="text-align: center; color: #e74c3c; padding: 40px;">
                        <i class="fas fa-exclamation-circle"></i><br>
                        Erreur : ${error.message}
                    </p>
                `;
            }
        }

        /**
        * Ferme le modal de détails
        */
        function fermerModalDetailsUtilisateur() {
            document.getElementById('modal-details-utilisateur').style.display = 'none';
        }

        /**
        * Confirme et supprime un utilisateur
        */
        async function confirmerSuppressionUtilisateur(userId, userName) {
            if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${userName}" ?\n\nCette action est irréversible.`)) {
                return;
            }
            
            try {
                const response = await fetch(`/chef/api/utilisateurs/${userId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    afficherNotification('success', data.message);
                    fermerModalDetailsUtilisateur();
                    chargerUtilisateurs();
                } else {
                    afficherNotification('error', data.message);
                }
            } catch (error) {
                console.error('Erreur:', error);
                afficherNotification('error', 'Erreur lors de la suppression');
            }
        }

        // ==========================================
        // GÉNÉRATION DE LIENS D'INSCRIPTION
        // ==========================================

        /**
        * Ouvre le modal de génération de lien
        */
        function ouvrirModalGenerationLien() {
            document.getElementById('modal-generation-lien').style.display = 'flex';
            document.getElementById('form-generation-lien').reset();
            chargerEtablissementsPourSelect();
        }

        /**
        * Ferme le modal de génération de lien
        */
        function fermerModalGenerationLien() {
            document.getElementById('modal-generation-lien').style.display = 'none';
        }

        /**
        * Toggle du champ nom utilisateur pour UEF
        */
        function toggleNomUserField() {
            const role = document.getElementById('input-role-lien').value;
            const groupNomUser = document.getElementById('group-nom-user');
            const inputNomUser = document.getElementById('input-nom-user');
            
            if (role === 'UEF') {
                groupNomUser.style.display = 'block';
                inputNomUser.required = true;
            } else {
                groupNomUser.style.display = 'none';
                inputNomUser.required = false;
            }
        }

        /**
        * Génère un lien d'inscription
        */
        async function genererLienInscription(event) {
            event.preventDefault();
            
            const form = event.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Génération...';
            
            try {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                const response = await fetch('/chef/api/generer-lien-inscription/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    afficherNotification('success', result.message);
                    fermerModalGenerationLien();
                    afficherLienGenere(result.token.lien, result.token.temps_restant_minutes);
                } else {
                    afficherNotification('error', result.message);
                }
            } catch (error) {
                console.error('Erreur:', error);
                afficherNotification('error', 'Erreur lors de la génération du lien');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }

        /**
        * Affiche le lien généré
        */
        function afficherLienGenere(lien, tempsRestantMinutes) {
            document.getElementById('lien-inscription-genere').value = lien;
            document.getElementById('temps-expiration').value = `${tempsRestantMinutes} minutes`;
            document.getElementById('modal-lien-genere').style.display = 'flex';
        }

        /**
        * Ferme le modal du lien généré
        */
        function fermerModalLienGenere() {
            document.getElementById('modal-lien-genere').style.display = 'none';
        }

        /**
        * Copie le lien dans le presse-papiers
        */
        function copierLien() {
            const input = document.getElementById('lien-inscription-genere');
            input.select();
            document.execCommand('copy');
            afficherNotification('success', 'Lien copié dans le presse-papiers !');
        }

        // ==========================================
        // JOURNALISATION
        // ==========================================

        /**
        * Charge les logs avec filtres
        */
        async function chargerJournalisation(page = 1) {
            paginationJournalisation.page = page;
            
            const tbody = document.getElementById('tbody-journalisation');
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 2em; color: #3498db;"></i>
                        <p style="margin-top: 10px; color: #7f8c8d;">Chargement...</p>
                    </td>
                </tr>
            `;

            try {
                // Construction des paramètres
                const params = new URLSearchParams({
                    page: paginationJournalisation.page,
                    per_page: paginationJournalisation.per_page
                });

                // Ajouter les filtres
                const typeAction = document.getElementById('filtre-type-action')?.value;
                if (typeAction) params.append('type_action', typeAction);

                const dateDebut = document.getElementById('filtre-date-debut')?.value;
                if (dateDebut) params.append('date_debut', new Date(dateDebut).toISOString());

                const dateFin = document.getElementById('filtre-date-fin')?.value;
                if (dateFin) params.append('date_fin', new Date(dateFin).toISOString());

                const search = document.getElementById('recherche-journalisation')?.value;
                if (search) params.append('search', search);

                // Appel API
                const response = await fetch(`/chef/api/journalisation/?${params.toString()}`, {
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
                        <td colspan="6" style="text-align: center; padding: 40px; color: #e74c3c;">
                            <i class="fas fa-exclamation-circle" style="font-size: 2em;"></i>
                            <p style="margin-top: 10px;">Erreur : ${error.message}</p>
                        </td>
                    </tr>
                `;
            }
        }

        /**
        * Affiche les logs dans le tableau
        */
        function afficherJournalisation(actions) {
            const tbody = document.getElementById('tbody-journalisation');
            
            if (!actions || actions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 40px;">
                            <i class="fas fa-clipboard-list" style="font-size: 2em; color: #95a5a6;"></i>
                            <p style="margin-top: 10px; color: #7f8c8d;">Aucune action trouvée</p>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = actions.map(action => `
                <tr>
                    <td style="white-space: nowrap;">
                        ${new Date(action.date_action).toLocaleString('fr-FR')}
                    </td>
                    <td>
                        <span class="badge badge-primary">${action.type_action_display}</span>
                    </td>
                    <td>
                        ${action.utilisateur ? `
                            <div style="font-size: 13px;">
                                <strong>${action.utilisateur.nom}</strong><br>
                                <span style="color: #7f8c8d;">${action.utilisateur.email}</span>
                            </div>
                        ` : '<span style="color: #95a5a6;">N/A</span>'}
                    </td>
                    <td>
                        ${action.etablissement ? 
                            `<strong>${action.etablissement.nom}</strong>` : 
                            '<span style="color: #95a5a6;">N/A</span>'}
                    </td>
                    <td style="max-width: 300px; white-space: normal;">${action.description}</td>
                    <td>${action.adresse_ip || '<span style="color: #95a5a6;">N/A</span>'}</td>
                </tr>
            `).join('');
        }

        /**
        * Affiche la pagination de la journalisation
        */
        function afficherPaginationJournalisation(pagination) {
            const container = document.getElementById('pagination-journalisation');
            
            if (!pagination || pagination.total_pages <= 1) {
                container.innerHTML = '';
                return;
            }

            let html = '<div style="display: flex; justify-content: center; align-items: center; gap: 10px;">';
            
            // Bouton précédent
            if (pagination.has_previous) {
                html += `<button class="btn-icon btn-view" onclick="chargerJournalisation(${pagination.page - 1})">
                    <i class="fas fa-chevron-left"></i>
                </button>`;
            }

            // Numéros de page
            for (let i = 1; i <= pagination.total_pages; i++) {
                if (i === pagination.page) {
                    html += `<button class="btn-primary" style="min-width: 40px;">${i}</button>`;
                } else if (Math.abs(i - pagination.page) <= 2 || i === 1 || i === pagination.total_pages) {
                    html += `<button class="btn-icon btn-view" onclick="chargerJournalisation(${i})" style="min-width: 40px;">${i}</button>`;
                } else if (Math.abs(i - pagination.page) === 3) {
                    html += '<span>...</span>';
                }
            }

            // Bouton suivant
            if (pagination.has_next) {
                html += `<button class="btn-icon btn-view" onclick="chargerJournalisation(${pagination.page + 1})">
                    <i class="fas fa-chevron-right"></i>
                </button>`;
            }

            html += `<span style="margin-left: 20px; color: #7f8c8d;">
                Page ${pagination.page} sur ${pagination.total_pages} (${pagination.total} actions)
            </span></div>`;

            container.innerHTML = html;
        }

        /**
        * Affiche les statistiques de journalisation
        */
        function afficherStatistiquesJournalisation(stats) {
            if (!stats) return;
            
            document.getElementById('stats-total-actions').textContent = stats.total || 0;
            document.getElementById('stats-connexions').textContent = stats.par_type?.CONNEXION || 0;
            document.getElementById('stats-uploads').textContent = stats.par_type?.UPLOAD_FICHIER || 0;
            document.getElementById('stats-modifications').textContent = 
                (stats.par_type?.MODIFICATION_UTILISATEUR || 0) + (stats.par_type?.MODIFICATION_ETABLISSEMENT || 0);
        }

        /**
        * Recherche dans la journalisation avec debounce
        */
        function rechercherJournalisation() {
            clearTimeout(rechercheJournalisationTimeout);
            rechercheJournalisationTimeout = setTimeout(() => {
                chargerJournalisation(1);
            }, 500);
        }

        /**
        * Exporte la journalisation en CSV
        */
        function exporterJournalisationCSV() {
            // Construction des paramètres (mêmes filtres que l'API)
            const params = new URLSearchParams();

            const typeAction = document.getElementById('filtre-type-action')?.value;
            if (typeAction) params.append('type_action', typeAction);

            const dateDebut = document.getElementById('filtre-date-debut')?.value;
            if (dateDebut) params.append('date_debut', new Date(dateDebut).toISOString());

            const dateFin = document.getElementById('filtre-date-fin')?.value;
            if (dateFin) params.append('date_fin', new Date(dateFin).toISOString());

            const search = document.getElementById('recherche-journalisation')?.value;
            if (search) params.append('search', search);

            // Télécharger le fichier
            window.location.href = `/chef/api/journalisation/export-csv/?${params.toString()}`;
            
            afficherNotification('success', 'Export CSV en cours de téléchargement...');
        }

        // ==========================================
        // FONCTIONS UTILITAIRES
        // ==========================================
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

        /**
        * Affiche une notification
        */
        function afficherNotification(type, message, duration = 5000) {
            // Créer la notification
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 10001;
                animation: slideInRight 0.3s;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                max-width: 400px;
            `;
            
            // Couleur selon le type
            if (type === 'success') {
                notification.style.background = 'linear-gradient(135deg, #27ae60, #229954)';
            } else if (type === 'error') {
                notification.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
            } else if (type === 'info') {
                notification.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
            }
            
            notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
            
            // Ajouter au DOM
            document.body.appendChild(notification);
            
            // Supprimer après durée
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s';
                setTimeout(() => notification.remove(), 300);
            }, duration);
            
            // Ajouter les animations si pas déjà présentes
            if (!document.getElementById('notification-animations')) {
                const style = document.createElement('style');
                style.id = 'notification-animations';
                style.textContent = `
                    @keyframes slideInRight {
                        from {
                            opacity: 0;
                            transform: translateX(100px);
                        }
                        to {
                            opacity: 1;
                            transform: translateX(0);
                        }
                    }
                    @keyframes slideOutRight {
                        from {
                            opacity: 1;
                            transform: translateX(0);
                        }
                        to {
                            opacity: 0;
                            transform: translateX(100px);
                        }
                    }
                `;
                document.head.appendChild(style);
            }
        }

        // ==========================================
        // INITIALISATION
        // ==========================================

        // Charger les données au changement d'onglet
        document.addEventListener('DOMContentLoaded', function() {
            // Observer les changements d'onglet
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.target.classList.contains('tab-pane') && 
                        mutation.target.classList.contains('active')) {
                        
                        if (mutation.target.id === 'utilisateurs') {
                            chargerUtilisateurs();
                            chargerEtablissementsPourSelect();
                        } else if (mutation.target.id === 'journalisation') {
                            chargerJournalisation();
                        }
                    }
                });
            });
            
            // Observer tous les tab-panes
            document.querySelectorAll('.tab-pane').forEach(function(tabPane) {
                observer.observe(tabPane, { attributes: true, attributeFilter: ['class'] });
            });
        });
        // ==========================================
        // GESTION DES INVITATIONS
        // ==========================================

        let roleSelectionne = null;
        let lienGenere = null;
        let emailDestinataire = null;

        // Ouvrir le modal
        function ouvrirModalInvitation() {
            document.getElementById('modalInvitation').style.display = 'block';
            resetFormulaire();
        }

        // Fermer le modal
        function fermerModalInvitation() {
            document.getElementById('modalInvitation').style.display = 'none';
            resetFormulaire();
        }

        // Reset du formulaire
        function resetFormulaire() {
            document.getElementById('formInvitation').reset();
            document.getElementById('lienContainer').classList.remove('show');
            document.getElementById('etablissementGroup').style.display = 'none';
            
            // Désélectionner tous les rôles
            document.querySelectorAll('.role-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            roleSelectionne = null;
            lienGenere = null;
            document.getElementById('btnGenerer').disabled = true;
        }

        // charger la liste des établissements pour le select AEF
        function chargerEtablissementsPourSelect1() {
            const select = document.getElementById('etablissementSelect');
            select.innerHTML = '<option value="">Chargement en cours...</option>';

            fetch('/chef/api/etablissements/select/')
                .then(response => {
                    if (!response.ok) throw new Error('Erreur réseau');
                    return response.json();
                })
                .then(data => {
                    select.innerHTML = '<option value="">Sélectionner un établissement</option>';
                    if (data.etablissements && data.etablissements.length > 0) {
                        data.etablissements.forEach(etab => {
                            const option = document.createElement('option');
                            option.value = etab.id;
                            option.textContent = `${etab.nom} (${etab.code})`;
                            select.appendChild(option);
                        });
                    } else {
                        select.innerHTML = '<option value="">Aucun établissement disponible</option>';
                    }
                })
                .catch(err => {
                    console.error('Erreur chargement établissements:', err);
                    select.innerHTML = '<option value="">Erreur de chargement</option>';
                    afficherNotification('error', 'Impossible de charger les établissements');
                });
        }
        // Sélectionner un rôle
        function selectionnerRole(role) {
            // Désélectionner tous les rôles
            document.querySelectorAll('.role-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Sélectionner le rôle cliqué
            document.querySelector(`[data-role="${role}"]`).classList.add('selected');
            roleSelectionne = role;
            
            // Afficher/masquer le champ établissement selon le rôle
            const etablissementGroup = document.getElementById('etablissementGroup');
            const etablissementSelect = document.getElementById('etablissementSelect');
            
            if (role === 'AEF') {
                etablissementGroup.style.display = 'block';
                etablissementSelect.required = true;
                chargerEtablissementsPourSelect1();
            } else {
                etablissementGroup.style.display = 'none';
                etablissementSelect.required = false;
                etablissementSelect.value = '';
            }
            
            // Activer le bouton
            document.getElementById('btnGenerer').disabled = false;
        }

        // Charger la liste des établissements
 

        // Générer l'invitation
        function genererInvitation(event) {
            event.preventDefault();
            
            if (!roleSelectionne) {
                alert('Veuillez sélectionner un rôle');
                return;
            }
            
            emailDestinataire = document.getElementById('emailDestinataire').value;
            const etablissementId = document.getElementById('etablissementSelect').value;
            
            // Validation pour AEF
            if (roleSelectionne === 'AEF' && !etablissementId) {
                alert('Veuillez sélectionner un établissement pour le rôle AEF');
                return;
            }
            
            // Préparer les données
            const data = {
                email: emailDestinataire,
                role: roleSelectionne,
                etablissement_id: etablissementId || null
            };
            
            // Désactiver le bouton
            const btnGenerer = document.getElementById('btnGenerer');
            btnGenerer.disabled = true;
            btnGenerer.textContent = '⏳ Génération en cours...';
            
            // Appel API
            fetch('/chef/api/invitations/generer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    afficherLienGenere(data.invitation);
                } else {
                    alert('Erreur : ' + data.message);
                    btnGenerer.disabled = false;
                    btnGenerer.textContent = '🔗 Générer le lien d\'invitation';
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de la génération du lien');
                btnGenerer.disabled = false;
                btnGenerer.textContent = '🔗 Générer le lien d\'invitation';
            });
        }

        // Afficher le lien généré
        function afficherLienGenere(invitation) {
            lienGenere = invitation.lien;
            
            document.getElementById('displayEmail').textContent = invitation.email;
            document.getElementById('displayRole').textContent = invitation.role;
            
            if (invitation.etablissement) {
                document.getElementById('displayEtablissement').innerHTML = 
                    `<strong>Établissement :</strong> ${invitation.etablissement}`;
            } else {
                document.getElementById('displayEtablissement').innerHTML = '';
            }
            
            document.getElementById('lienDisplay').textContent = invitation.lien;
            document.getElementById('tempsRestant').textContent = invitation.temps_restant_minutes;
            
            document.getElementById('lienContainer').classList.add('show');
            
            // Scroll vers le lien
            document.getElementById('lienContainer').scrollIntoView({ behavior: 'smooth' });
        }

        // Copier le lien
        function copierLien() {
            const lienDisplay = document.getElementById('lienDisplay');
            const textArea = document.createElement('textarea');
            textArea.value = lienGenere;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            alert('✅ Lien copié dans le presse-papiers !');
        }

        // Envoyer via WhatsApp
        function envoyerViaWhatsApp() {
            const message = `Bonjour,\n\nVous êtes invité(e) à créer votre compte sur la plateforme CNEF.\n\nCliquez sur ce lien pour vous inscrire :\n${lienGenere}\n\n⚠️ Ce lien expire dans ${document.getElementById('tempsRestant').textContent} minutes.`;
            
            const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
            window.open(whatsappUrl, '_blank');
        }



        // Fermer le modal en cliquant en dehors
        window.onclick = function(event) {
            const modal = document.getElementById('modalInvitation');
            if (event.target == modal) {
                fermerModalInvitation();
            }
        }

        // Invitations
        async function chargerInvitationsEnAttente() {
            try {
                const response = await fetch('/chef/api/invitations/liste/');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('count-invitations').textContent = data.total;
                    const tbody = document.getElementById('tbody-invitations');
                    if (data.invitations.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:40px;">Aucune invitation</td></tr>';
                    } else {
                        tbody.innerHTML = data.invitations.map(inv => `
                            <tr>
                                <td><span style="background: #3498db; color: white; padding: 4px 12px; border-radius: 15px;">${inv.role}</span></td>
                                <td>${inv.email || '-'}</td>
                                <td>${inv.etablissement}</td>
                                <td>${inv.date_creation}</td>
                                <td>${inv.expiration}</td>
                                <td>
                                    <button onclick="copierLien('${inv.lien}')" style="background: #3498db; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; margin-right: 5px;">
                                        <i class="fas fa-copy"></i>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                        </svg>

                                    </button>
                                    <button onclick="revoquerInvitation(${inv.id})" style="background: #e74c3c; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer;">
                                        <i class="fas fa-trash"></i>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M9 14l-4-4 4-4"/>
                                            <path d="M20 20v-5a4 4 0 0 0-4-4H5"/>
                                        </svg>

                                    </button>
                                </td>
                            </tr>
                        `).join('');
                    }
                }
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        async function copierLien(lien) {
            try {
                await navigator.clipboard.writeText(lien);
                alert('Lien copié !');
            } catch {
                const textarea = document.createElement('textarea');
                textarea.value = lien;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('Lien copié !');
            }
        }

        async function revoquerInvitation(id) {
            if (!confirm('Révoquer cette invitation ?')) return;
            try {
                const response = await fetch(`/chef/api/invitations/${id}/revoquer/`, {
                    method: 'DELETE',
                    headers: {'X-CSRFToken': getCookie('csrftoken')}
                });
                const data = await response.json();
                alert(data.message);
                if (data.success) chargerInvitationsEnAttente();
            } catch (error) {
                alert('Erreur lors de la révocation');
            }
        }


        // Modal suppression journal
        /**
         * Ouvre le modal de suppression des journaux
         */
        function ouvrirModalSupprimerJournal() {
            document.getElementById('modalSupprimerJournal').style.display = 'flex';
            
            // Réinitialiser le formulaire
            document.getElementById('dateDebutSuppression').value = '';
            document.getElementById('dateFinSuppression').value = '';
            document.getElementById('previewSuppression').style.display = 'none';
            document.getElementById('btnConfirmerSuppression').disabled = true;
            
            // Sélectionner "intervalle" par défaut
            const radioIntervalle = document.querySelector('input[name="modeSuppression"][value="intervalle"]');
            if (radioIntervalle) radioIntervalle.checked = true;
        }

        function fermerModalSupprimerJournal() {
            document.getElementById('modalSupprimerJournal').style.display = 'none';
        }

        /**
         * Calcule le nombre d'entrées à supprimer
         */
        async function calculerNombreSupprimer() {
            const mode = document.querySelector('input[name="modeSuppression"]:checked')?.value;
            const dateDebut = document.getElementById('dateDebutSuppression').value;
            const dateFin = document.getElementById('dateFinSuppression').value;
            
            console.log("DEBUG - Calcul:", { mode, dateDebut, dateFin });
            
            // Validation
            if (!mode || !dateDebut) {
                document.getElementById('previewSuppression').style.display = 'none';
                document.getElementById('btnConfirmerSuppression').disabled = true;
                return;
            }
            
            if (mode === 'intervalle' && !dateFin) {
                document.getElementById('previewSuppression').style.display = 'none';
                document.getElementById('btnConfirmerSuppression').disabled = true;
                return;
            }
            
            // Formater les dates
            const dateDebutFormatted = formatDateToISO(dateDebut);
            const dateFinFormatted = dateFin ? formatDateToISO(dateFin) : null;
            
            console.log("DEBUG - Dates formatées:", { dateDebutFormatted, dateFinFormatted });
            
            try {
                const response = await fetch('/chef/api/journalisation/compter/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        mode: mode,
                        date_debut: dateDebutFormatted,
                        date_fin: dateFinFormatted
                    })
                });
                
                const data = await response.json();
                console.log("DEBUG - Réponse API:", data);
                
                if (data.success) {
                    // Afficher le nombre
                    document.getElementById('nombreSupprimer').textContent = data.nombre;
                    document.getElementById('previewSuppression').style.display = 'block';
                    
                    // Activer/désactiver le bouton selon le nombre
                    document.getElementById('btnConfirmerSuppression').disabled = data.nombre === 0;
                } else {
                    alert('Erreur: ' + data.message);
                    document.getElementById('previewSuppression').style.display = 'none';
                    document.getElementById('btnConfirmerSuppression').disabled = true;
                }
            } catch (error) {
                console.error('Erreur réseau:', error);
                alert('Erreur réseau lors du calcul: ' + error.message);
                document.getElementById('previewSuppression').style.display = 'none';
                document.getElementById('btnConfirmerSuppression').disabled = true;
            }
        }

        // Appel au chargement
        document.addEventListener('DOMContentLoaded', function() {
            chargerInvitationsEnAttente();
        });

        // ==========================================
        // FONCTION PRINCIPALE : Charger l'historique des emails
        // ==========================================
        function chargerHistoriqueEmails() {
            // Récupérer les valeurs des filtres
            const typeFilter = document.getElementById('filter-type-email').value;
            const objetFilter = document.getElementById('filter-objet-email').value;
            
            // Construire l'URL avec les paramètres de filtre
            let url = '/chef/historique-emails/?ajax=1';
            if (typeFilter) url += `&type=${typeFilter}`;
            if (objetFilter) url += `&objet=${encodeURIComponent(objetFilter)}`;
            
            // Faire la requête AJAX vers le serveur
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    // ========== NOUVEAU: Mettre à jour les statistiques ==========
                    if (data.stats) {
                        document.getElementById('stats-total-emails').textContent = data.stats.total;
                        document.getElementById('stats-emails-envoyes').textContent = data.stats.envoyes;
                        document.getElementById('stats-emails-echec').textContent = data.stats.echec;
                        document.getElementById('stats-emails-today').textContent = data.stats.aujourdhui;
                    }
                    // ==============================================================
                    
                    const tbody = document.getElementById('historique-emails-tbody');
                    tbody.innerHTML = '';
                    
                    // Si aucun email trouvé
                    if (data.emails.length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="6" style="text-align: center; padding: 40px; color: #6c757d;">
                                    <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 10px; opacity: 0.3;"></i><br>
                                    <strong>Aucun email trouvé</strong>
                                </td>
                            </tr>
                        `;
                        return;
                    }
                    
                    // Construire chaque ligne du tableau
                    data.emails.forEach(email => {
                        const badgeColor = getBadgeColor(email.type_email);
                        const statutBadge = email.statut === 'ENVOYE' 
                            ? '<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">Envoyé</span>' 
                            : '<span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">Échec</span>';
                        
                        const row = `
                            <tr style="border-bottom: 1px solid #dee2e6;">
                                <td style="padding: 12px; white-space: nowrap;">
                                    ${email.date_envoi}
                                </td>
                                <td style="padding: 12px;">
                                    <span style="background-color: ${badgeColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                                        ${email.type_display}
                                    </span>
                                </td>
                                <td style="padding: 12px;">
                                    <div style="font-weight: 600;">${email.destinataire_nom || email.destinataire_email}</div>
                                    <div style="font-size: 12px; color: #6c757d;">${email.destinataire_email}</div>
                                </td>
                                <td style="padding: 12px;">${email.objet}</td>
                                <td style="padding: 12px;">${statutBadge}</td>
                                <td style="padding: 12px; text-align: center;">
                                    <button class="btn btn-sm btn-primary" 
                                            onclick="renvoyerEmail(${email.id})" 
                                            style="background-color: #3498db; border: none; padding: 6px 12px; border-radius: 4px;">
                                        <i class="fas fa-redo"></i> Renvoyer
                                    </button>
                                </td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                    });
                })
                .catch(error => {
                    console.error('Erreur lors du chargement:', error);
                    document.getElementById('historique-emails-tbody').innerHTML = `
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 40px; color: #dc3545;">
                                <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 10px;"></i><br>
                                <strong>Erreur de chargement</strong><br>
                                <small>${error.message}</small>
                            </td>
                        </tr>
                    `;
                });
        }


        // ==========================================
        // FONCTION : Obtenir la couleur du badge selon le type
        // ==========================================
        function getBadgeColor(type) {
            const colors = {
                'INVITATION': '#0d6efd',      // Bleu
                'VALIDATION': '#28a745',      // Vert
                'REJET': '#dc3545',           // Rouge
                'NOTIFICATION_ACNEF': '#ffc107'  // Orange/Jaune
            };
            return colors[type] || '#6c757d';  // Gris par défaut
        }


        // ==========================================
        // FONCTION : Filtrer l'historique
        // ==========================================
        function filtrerHistoriqueEmails() {
            chargerHistoriqueEmails();
        }


        // ==========================================
        // FONCTION : Renvoyer un email
        // ==========================================
        function renvoyerEmail(emailId) {
            // Demander confirmation
            if (!confirm('Êtes-vous sûr de vouloir renvoyer cet email ?')) {
                return;
            }
            
            // Envoyer la requête au serveur
            fetch(`/chef/api/renvoyer-email/${emailId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Afficher le message de succès
                    alert('✅ ' + data.message);
                    // Recharger la liste pour voir le nouvel envoi
                    chargerHistoriqueEmails();
                } else {
                    // Afficher le message d'erreur
                    alert('❌ ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('❌ Erreur lors du renvoi de l\'email');
            });
        }

        // ==========================================
        // CHARGER AUTOMATIQUEMENT QUAND L'ONGLET S'OUVRE
        // ==========================================

        // Observer les changements d'onglets (plus robuste)
        document.addEventListener('DOMContentLoaded', function() {
            // Observer quand l'onglet historique-emails devient visible
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    const target = mutation.target;
                    if (target.id === 'historique-emails' && 
                        target.style.display === 'block') {
                        // L'onglet est maintenant visible, charger les emails
                        chargerHistoriqueEmails();
                    }
                });
            });
            
            // Observer l'onglet historique-emails
            const emailsTab = document.getElementById('historique-emails');
            if (emailsTab) {
                observer.observe(emailsTab, { 
                    attributes: true, 
                    attributeFilter: ['style'] 
                });
            }
        });
        


        // ==========================================
        // CHARGEMENT AUTOMATIQUE DE L'HISTORIQUE DES EMAILS
        // ==========================================
        document.addEventListener('DOMContentLoaded', function() {
            // Observer pour détecter quand l'onglet historique-emails devient visible
            const emailsTab = document.getElementById('historique-emails');
            if (emailsTab) {
                // Créer un observateur qui surveille les changements de classe
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                            // Si l'onglet devient actif, charger les emails
                            if (emailsTab.classList.contains('active')) {
                                chargerHistoriqueEmails();
                            }
                        }
                    });
                });
                
                // Commencer à observer
                observer.observe(emailsTab, {
                    attributes: true,
                    attributeFilter: ['class']
                });
                
                // Charger aussi au début si l'onglet est déjà actif
                if (emailsTab.classList.contains('active')) {
                    chargerHistoriqueEmails();
                }
            }
        });

        // ==========================================
        // MISE À JOUR DU BADGE DES SOUMISSIONS
        // ==========================================
        function mettreAJourBadgeSoumissions(nombreEnAttente) {
            const badge = document.getElementById('badge-soumissions-attente');
            if (badge) {
                badge.textContent = nombreEnAttente;
                badge.style.display = nombreEnAttente > 0 ? 'inline-block' : 'none';
            }
        }

        // ==========================================
        // GESTION DU MODE DE SUPPRESSION DES JOURNAUX
        // ==========================================
        document.addEventListener('DOMContentLoaded', function() {
            const radios = document.querySelectorAll('input[name="modeSuppression"]');
            radios.forEach(radio => {
                radio.addEventListener('change', function() {
                    const dateFinContainer = document.getElementById('dateFinContainer');
                    if (this.value === 'avant') {
                        dateFinContainer.style.display = 'none';
                        document.getElementById('dateFinSuppression').value = '';
                    } else {
                        dateFinContainer.style.display = 'block';
                    }
                    // Recalculer automatiquement
                    calculerNombreSupprimer();
                });
            });
        });

        // ==========================================
        // VARIABLES GLOBALES POUR LES SUPPRESSIONS
        // ==========================================
        let journalDataSuppr = {};
        let fichierDataSuppr = {};
        let utilisateurDataBannir = {};

        // ==========================================
        // SUPPRESSION DE JOURNAL
        // ==========================================

                // ==========================================
        // CORRECTION DES FONCTIONS DE SUPPRESSION JOURNAL
        // ==========================================

        /**
         * Ouvre le modal de suppression des journaux
         */
        function ouvrirModalSupprimerJournal() {
            document.getElementById('modalSupprimerJournal').style.display = 'flex';
            
            // Réinitialiser le formulaire
            document.getElementById('dateDebutSuppression').value = '';
            document.getElementById('dateFinSuppression').value = '';
            document.getElementById('previewSuppression').style.display = 'none';
            document.getElementById('btnConfirmerSuppressionJournal').disabled = true;
            
            // Sélectionner "intervalle" par défaut
            const radioIntervalle = document.querySelector('input[name="modeSuppression"][value="intervalle"]');
            if (radioIntervalle) radioIntervalle.checked = true;
            
            // Afficher le conteneur date fin
            document.getElementById('dateFinContainer').style.display = 'block';
        }

        function fermerModalSupprimerJournal() {
            document.getElementById('modalSupprimerJournal').style.display = 'none';
        }

        /**
         * Ferme le modal de confirmation de suppression des journaux
         */
        function fermerModalConfirmationSuppressionJournal() {
            const modal = document.getElementById('modalConfirmationSuppressionJournal');
            if (modal) {
                modal.style.display = 'none';
            }
        }

        /**
         * Ferme le modal de suppression des journaux
         */
        function fermerModalSupprimerJournal() {
            const modal = document.getElementById('modalSupprimerJournal');
            if (modal) {
                modal.style.display = 'none';
            }
        }
        /**
         * Calcule le nombre d'entrées à supprimer
         */
        async function calculerNombreSupprimer() {
            const mode = document.querySelector('input[name="modeSuppression"]:checked')?.value;
            const dateDebut = document.getElementById('dateDebutSuppression').value;
            const dateFin = document.getElementById('dateFinSuppression').value;
            
            console.log("DEBUG - Calcul:", { mode, dateDebut, dateFin });
            
            // Validation
            if (!mode || !dateDebut) {
                document.getElementById('previewSuppression').style.display = 'none';
                document.getElementById('btnConfirmerSuppressionJournal').disabled = true;
                return;
            }
            
            if (mode === 'intervalle' && !dateFin) {
                document.getElementById('previewSuppression').style.display = 'none';
                document.getElementById('btnConfirmerSuppressionJournal').disabled = true;
                return;
            }
            
            // Formater les dates
            const dateDebutFormatted = formatDateToISO(dateDebut);
            const dateFinFormatted = dateFin ? formatDateToISO(dateFin) : null;
            
            console.log("DEBUG - Dates formatées:", { dateDebutFormatted, dateFinFormatted });
            
            try {
                const response = await fetch('/chef/api/journalisation/compter/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        mode: mode,
                        date_debut: dateDebutFormatted,
                        date_fin: dateFinFormatted
                    })
                });
                
                const data = await response.json();
                console.log("DEBUG - Réponse API:", data);
                
                if (data.success) {
                    // Afficher le nombre
                    document.getElementById('nombreSupprimer').textContent = data.nombre;
                    document.getElementById('previewSuppression').style.display = 'block';
                    
                    // Activer/désactiver le bouton selon le nombre
                    document.getElementById('btnConfirmerSuppressionJournal').disabled = data.nombre === 0;
                } else {
                    alert('Erreur: ' + data.message);
                    document.getElementById('previewSuppression').style.display = 'none';
                    document.getElementById('btnConfirmerSuppressionJournal').disabled = true;
                }
            } catch (error) {
                console.error('Erreur réseau:', error);
                alert('Erreur réseau lors du calcul: ' + error.message);
                document.getElementById('previewSuppression').style.display = 'none';
                document.getElementById('btnConfirmerSuppressionJournal').disabled = true;
            }
        }

        /**
         * Valide et prépare la suppression (ouvre le modal de confirmation)
         */
        async function validerSuppressionJournal() {
            const mode = document.querySelector('input[name="modeSuppression"]:checked')?.value;
            const dateDebut = document.getElementById('dateDebutSuppression').value;
            const dateFin = document.getElementById('dateFinSuppression').value;
            
            console.log("DEBUG - Validation:", { mode, dateDebut, dateFin });
            
            // Validation
            if (!mode || !dateDebut) {
                alert('Veuillez remplir tous les champs requis');
                return;
            }
            
            if (mode === 'intervalle' && !dateFin) {
                alert('Veuillez sélectionner une date de fin pour le mode intervalle');
                return;
            }
            
            // Formater les dates
            const dateDebutFormatted = formatDateToISO(dateDebut);
            const dateFinFormatted = dateFin ? formatDateToISO(dateFin) : null;
            
            console.log("DEBUG - Dates formatées:", { dateDebutFormatted, dateFinFormatted });
            
            // Stocker les données pour la suppression définitive
            journalDataSuppr = {
                mode: mode,
                dateDebut: dateDebutFormatted,
                dateFin: dateFinFormatted
            };
            
            try {
                const response = await fetch('/chef/api/journalisation/compter/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        mode: mode,
                        date_debut: dateDebutFormatted,
                        date_fin: dateFinFormatted
                    })
                });
                
                const data = await response.json();
                console.log("DEBUG - Réponse API compter:", data);
                
                if (data.success) {
                    // Afficher le nombre dans le modal de confirmation
                    document.getElementById('nombreJournauxASupprimer').textContent = 
                        `${data.nombre} entrée(s) de journal`;
                    
                    // Afficher la période
                    let periode = '';
                    if (mode === 'intervalle') {
                        const dateDebutObj = new Date(dateDebut);
                        const dateFinObj = new Date(dateFin);
                        periode = `Entre le ${dateDebutObj.toLocaleDateString('fr-FR')} et le ${dateFinObj.toLocaleDateString('fr-FR')}`;
                    } else {
                        const dateDebutObj = new Date(dateDebut);
                        periode = `Avant le ${dateDebutObj.toLocaleDateString('fr-FR')}`;
                    }
                    document.getElementById('periodeSuppressionJournal').textContent = periode;
                    
                    // Fermer la première modal et ouvrir la confirmation
                    fermerModalSupprimerJournal();
                    document.getElementById('modalConfirmationSuppressionJournal').style.display = 'flex';
                } else {
                    alert('Erreur: ' + data.message);
                }
            } catch (error) {
                console.error('Erreur réseau:', error);
                alert('Erreur réseau lors du calcul: ' + error.message);
            }
        }

        // Fonction pour formater une date au format ISO
        function formatDateToISO(dateStr) {
            // Si la date contient déjà 'T', c'est un datetime-local (YYYY-MM-DDTHH:MM)
            if (dateStr.includes('T')) {
                return dateStr;
            }
            // Sinon, c'est une date simple (YYYY-MM-DD), ajouter le temps par défaut
            return dateStr + 'T00:00';
        }

        // Exécuter la suppression définitive
        async function executerSuppressionJournal() {
            const { mode, dateDebut, dateFin } = journalDataSuppr;
            
            console.log("DEBUG - Exécution suppression:", { mode, dateDebut, dateFin });
            
            // Validation
            if (!mode || !dateDebut) {
                alert('Erreur: données de suppression manquantes');
                return;
            }
            
            try {
                const response = await fetch('/chef/api/journalisation/supprimer/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        mode: mode,
                        date_debut: dateDebut,
                        date_fin: dateFin
                    })
                });
                
                const data = await response.json();
                console.log("DEBUG - Réponse suppression:", data);
                
                if (data.success) {
                    fermerModalConfirmationSuppressionJournal();
                    
                    // Afficher un message de succès
                    if (typeof afficherAlerte === 'function') {
                        afficherAlerte(`${data.nombre_lignes} entrée(s) supprimée(s) avec succès`, 'success');
                    } else if (typeof afficherNotification === 'function') {
                        afficherNotification('success', `${data.nombre_lignes} entrée(s) supprimée(s) avec succès`);
                    } else {
                        alert(`✅ ${data.nombre_lignes} entrée(s) supprimée(s) avec succès`);
                    }
                    
                    // Recharger le tableau de journalisation
                    if (typeof chargerJournalisation === 'function') {
                        chargerJournalisation();
                    }
                } else {
                    alert('Erreur lors de la suppression: ' + data.message);
                }
            } catch (error) {
                console.error('Erreur:', error);
                alert('Erreur lors de la suppression: ' + error.message);
            }
        } 

        // Gestion du changement de mode de suppression
        document.addEventListener('DOMContentLoaded', function() {
            const radios = document.querySelectorAll('input[name="modeSuppression"]');
            radios.forEach(radio => {
                radio.addEventListener('change', function() {
                    const dateFinContainer = document.getElementById('dateFinContainer');
                    if (this.value === 'avant') {
                        dateFinContainer.style.display = 'none';
                        document.getElementById('dateFinSuppression').value = '';
                    } else {
                        dateFinContainer.style.display = 'block';
                    }
                    // Recalculer automatiquement
                    calculerNombreSupprimer();
                });
            });
        });

        // ==========================================
        // SUPPRESSION DE FICHIER
        // ==========================================
        function supprimerFichier(fichierId, nomFichier) {
            fichierDataSuppr = { fichierId, nomFichier };
            document.getElementById('nomFichierASupprimer').textContent = nomFichier;
            document.getElementById('modalConfirmationSuppressionFichier').style.display = 'block';
        }

        function fermerModalConfirmationSuppressionFichier() {
            document.getElementById('modalConfirmationSuppressionFichier').style.display = 'none';
        }

        function executerSuppressionFichier() {
            const { fichierId, nomFichier } = fichierDataSuppr;
            
            showLoading(true);
            
            fetch(`/chef/api/supprimer-fichier/${fichierId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                fermerModalConfirmationSuppressionFichier();
                
                if (data.success) {
                    showAlert(data.message, 'success');
                    const row = document.getElementById(`file-${fichierId}`);
                    if (row) row.remove();
                    refreshStats();
                } else {
                    showAlert(data.message, 'error');
                }
            })
            .catch(error => {
                showLoading(false);
                showAlert('Erreur lors de la suppression', 'error');
            });
        }

        // ==========================================
        // BANNISSEMENT D'UTILISATEUR
        // ==========================================
        async function bannirUtilisateur(userId, nom) {
            utilisateurDataBannir = { userId, nom };
            document.getElementById('nomUtilisateurABannir').textContent = nom;
            document.getElementById('modalConfirmationBannissement').style.display = 'block';
        }

        function fermerModalConfirmationBannissement() {
            document.getElementById('modalConfirmationBannissement').style.display = 'none';
        }

        async function executerBannissement() {
            const { userId, nom } = utilisateurDataBannir;
            
            try {
                const response = await fetch(`/chef/api/utilisateurs/${userId}/bannir/`, {
                    method: 'POST',
                    headers: {'X-CSRFToken': getCookie('csrftoken')}
                });
                const data = await response.json();
                
                fermerModalConfirmationBannissement();
                
                if (data.success) {
                    afficherAlerte(data.message, 'success');
                    chargerUtilisateurs();
                } else {
                    afficherAlerte(data.message, 'error');
                }
            } catch (error) {
                afficherAlerte('Erreur lors du bannissement', 'error');
            }
        }

        // Fermer les modaux en cliquant dehors
        window.addEventListener('click', function(event) {
            const modalJournal = document.getElementById('modalConfirmationSuppressionJournal');
            const modalFichier = document.getElementById('modalConfirmationSuppressionFichier');
            const modalBannir = document.getElementById('modalConfirmationBannissement');
            const modalRejet = document.getElementById('modalRejetSoumission');
            
            if (event.target === modalJournal) fermerModalConfirmationSuppressionJournal();
            if (event.target === modalFichier) fermerModalConfirmationSuppressionFichier();
            if (event.target === modalBannir) fermerModalConfirmationBannissement();
            if (event.target === modalRejet) fermerModalRejetSoumission();
        });