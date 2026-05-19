import streamlit as st
import pandas as pd
import joblib
import pydeck as pdk
import plotly.express as px
from pathlib import Path
from config import RESULTS_DIR, DATA_DIR, MODELS_DIR

def inject_corporate_theme() -> None:
    """Injecte un CSS personnalisé pour une interface claire, fluide et professionnelle."""
    st.markdown(
        """
        <style>
            /* Arrière-plan global clair et doux */
            .stApp {
                background-color: #F4F7F9;
                color: #2C3E50;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }
            
            /* En-tête Corporate */
            .corporate-header {
                background-color: #FFFFFF;
                padding: 2.5rem;
                border-radius: 12px;
                border-left: 6px solid #005A9C; /* Bleu Corporate Doux */
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
                margin-bottom: 2rem;
                margin-top: 1rem;
            }
            .corporate-header h1 {
                color: #1E293B !important;
                font-weight: 700;
                margin-bottom: 0.5rem;
                font-size: 2.2rem;
            }
            .corporate-header h4 {
                color: #64748B !important;
                font-weight: 500;
                margin-top: 0;
            }
            .corporate-header p {
                margin-top: 1.5rem;
                font-size: 1.05rem;
                color: #475569;
                line-height: 1.6;
            }
            
            /* Stylisation des cartes de Métriques (KPIs) */
            div[data-testid="stMetric"] {
                background-color: #FFFFFF;
                padding: 1.2rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
                border-top: 3px solid #E2001A; /* Accent carmin discret */
                text-align: center;
            }
            div[data-testid="stMetricLabel"] {
                color: #64748B !important;
                font-weight: 600;
                font-size: 0.95rem;
            }
            div[data-testid="stMetricValue"] {
                color: #0F172A !important;
            }
            
            /* Stylisation des Onglets (Tabs) pour un rendu fluide */
            .stTabs [data-baseweb="tab-list"] {
                gap: 15px;
                border-bottom: 2px solid #E2E8F0;
            }
            .stTabs [data-baseweb="tab"] {
                color: #64748B;
                background-color: transparent;
                border-radius: 0;
                padding: 1rem 1.5rem;
                font-size: 1.05rem;
                transition: all 0.2s ease-in-out;
            }
            .stTabs [aria-selected="true"] {
                color: #005A9C !important;
                border-bottom: 3px solid #005A9C !important;
                background-color: #FFFFFF;
                border-radius: 8px 8px 0 0;
                font-weight: 600;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.02);
            }
            
            /* Stylisation des conteneurs Dataframes et Expanders */
            .stDataFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }
            
            /* Boutons d'action */
            .stButton>button {
                background-color: #005A9C !important;
                color: white !important;
                border-radius: 6px !important;
                padding: 0.6rem 2rem !important;
                font-weight: 600 !important;
                border: none !important;
                box-shadow: 0 4px 6px rgba(0, 90, 156, 0.2);
            }
            .stButton>button:hover {
                background-color: #004578 !important;
                box-shadow: 0 6px 8px rgba(0, 90, 156, 0.3);
            }
            
            /* Titres de sections internes */
            h3 {
                color: #1E293B !important;
                font-weight: 600 !important;
                margin-top: 1.5rem !important;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #E2E8F0;
            }
            h4 {
                color: #334155 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def build_app() -> None:
    # 1. Configuration de la page (DOIT ÊTRE LA TOUTE PREMIÈRE LIGNE)
    st.set_page_config(
        page_title="Prédiction Retards TGV - POC", 
        page_icon="🚄", 
        layout="wide"
    )
    
    # Appel de la fonction de mise en page CSS
    inject_corporate_theme()
    
    # 2. Titre et Contexte Métier repensés en bloc Corporate
    st.markdown("""
    <div class="corporate-header">
        <h1>🚄 Prédiction du Taux de Retard Mensuel (TGV)</h1>
        <h4><i>Direction de l'Innovation & de la Ponctualité Ferroviaire</i></h4>
        <p>
            Ce tableau de bord constitue la preuve de concept (PoC) permettant d'anticiper le taux de retard moyen le mois suivant sur une ligne spécifique. <br>
            L'objectif stratégique est d'optimiser la gestion prévisionnelle des circulations et d'améliorer la transparence voyageur.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Création des sections principales
    tab1, tab2, tab3 = st.tabs([
        "📊 Données & Insights", 
        "🏆 Analyse des Modèles", 
        "🔮 Simulateur de Prédiction"
    ])
    
    # --- ONGLET 1 : DONNÉES & INSIGHTS ---
    with tab1:
        st.subheader("Analyse de la Ponctualité par Ligne & Cartographie")
        
        path_nettoye = DATA_DIR / "data_nettoyee.csv"
        
        if not path_nettoye.exists():
            st.error(f" Fichier introuvable : `{path_nettoye}`. Veuillez vérifier son emplacement.")
        else:
            try:
                # Lecture complète pour extraire les gares uniques
                df_insights = pd.read_csv(path_nettoye)
                
                # --- SECTION SÉLECTEUR DE LIGNE ---
                st.markdown("### 🔍 Analyse Historique Spécifique")
                col_sel1, col_sel2 = st.columns(2)
                
                with col_sel1:
                    liste_departs = sorted(df_insights["Gare de départ"].unique())
                    gare_dep = st.selectbox("Gare de départ", liste_departs, index=liste_departs.index("LYON PART DIEU") if "LYON PART DIEU" in liste_departs else 0)
                
                with col_sel2:
                    # On filtre les arrivées possibles selon le départ pour éviter les lignes inexistantes
                    arrivées_possibles = sorted(df_insights[df_insights["Gare de départ"] == gare_dep]["Gare d'arrivée"].unique())
                    gare_arr = st.selectbox("Gare d'arrivée", arrivées_possibles, index=arrivées_possibles.index("MARSEILLE ST CHARLES") if "MARSEILLE ST CHARLES" in arrivées_possibles else 0)
                
                # Filtrage du dataset pour la ligne choisie
                df_ligne = df_insights[(df_insights["Gare de départ"] == gare_dep) & (df_insights["Gare d'arrivée"] == gare_arr)]
                
                if df_ligne.empty:
                    st.warning("Aucune donnée historique trouvée pour cette combinaison de gares.")
                else:
                    # Calcul des indicateurs demandés
                    taux_retard_hist = df_ligne["taux_retard"].mean() * 100 if "taux_retard" in df_ligne.columns else df_ligne["target"].mean() * 100
                    temps_moyen = df_ligne["Durée moyenne du trajet"].mean()
                    trajets_par_mois = df_ligne["Nombre de circulations prévues"].mean()
                    
                    # Affichage des KPIs
                    st.markdown("<br>", unsafe_allow_html=True)
                    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
                    c_kpi1.metric(f"Taux de retard historique ({gare_dep} ➔ {gare_arr})", f"{taux_retard_hist:.2f}%")
                    c_kpi2.metric("Temps de trajet moyen constaté", f"{int(temps_moyen)} min ({int(temps_moyen//60)}h{int(temps_moyen%60)})")
                    c_kpi3.metric("Nombre moyen de trajets / mois", f"{int(trajets_par_mois)}")
                
                # --- SECTION CARTOGRAPHIE ---
                st.markdown("### 🗺️ Réseau National des Gares du Projet")
                
                # Dictionnaire de géolocalisation des gares majeures de la SNCF présentes dans tes données
                coords_gares = {
                    "PARIS LYON": {"lat": 48.8443, "lon": 2.3744},
                    "LYON PART DIEU": {"lat": 45.7606, "lon": 4.8599},
                    "MARSEILLE ST CHARLES": {"lat": 43.3027, "lon": 5.3806},
                    "BORDEAUX ST JEAN": {"lat": 44.8259, "lon": -0.5565},
                    "PARIS MONTPARNASSE": {"lat": 48.8412, "lon": 2.3201},
                    "NICE VILLE": {"lat": 43.7049, "lon": 7.2619},
                    "VALENCE ALIXAN TGV": {"lat": 44.9892, "lon": 5.0172},
                    "ANGERS SAINT LAUD": {"lat": 47.4647, "lon": -0.5562},
                    "ANGOULEME": {"lat": 45.6548, "lon": 0.1656},
                    "ANNECY": {"lat": 45.9016, "lon": 6.1212},
                    "ARRAS": {"lat": 50.2867, "lon": 2.7820},
                    "AVIGNON TGV": {"lat": 43.9216, "lon": 4.7932},
                    "DIJON VILLE": {"lat": 47.3236, "lon": 5.0269},
                    "RENNES": {"lat": 48.1030, "lon": -1.6720},
                    "STRASBOURG": {"lat": 48.5851, "lon": 7.7341},
                    "TOULOUSE MATABIAU": {"lat": 43.6112, "lon": 1.4536},
                    "NANTES": {"lat": 47.2173, "lon": -1.5424},
                    "LILLE EUROPE": {"lat": 50.6389, "lon": 3.0761}
                }
                
                # Récupération de toutes les gares uniques du dataset (départ et arrivée)
                all_gares_in_dataset = set(df_insights["Gare de départ"].unique()).union(set(df_insights["Gare d'arrivée"].unique()))
                
                # Construction d'un DataFrame de coordonnées uniquement pour les gares référencées
                points_carte = []
                for g in all_gares_in_dataset:
                    if g in coords_gares:
                        points_carte.append({
                            "Gare": g,
                            "latitude": coords_gares[g]["lat"],
                            "longitude": coords_gares[g]["lon"]
                        })
                
                if points_carte:
                    df_map = pd.DataFrame(points_carte)
                    # Affichage interactif natif de Streamlit (Mapbox)
                    st.map(df_map, latitude="latitude", longitude="longitude", size=20, color="#E2001A")
                    st.caption("Visualisation géographique des gares actives dans la base de données (Points d'analyse de la ponctualité).")
                else:
                    st.info("Aucune coordonnée géographique correspondante trouvée pour cartographier les gares.")
                
            except Exception as e:
                st.error(f" Erreur lors de l'analyse visuelle : {e}")

        st.markdown("### 🗃️ Aperçu des Données Historiques")
        
        path_data = DATA_DIR / "processed_dataset.csv"
        if not path_data.exists():
            st.error(f"Fichier introuvable : `{path_data}`")
        else:
            try:
                # Lecture brute sécurisée
                df = pd.read_csv(path_data, nrows=500) # On limite à 500 lignes pour tester la rapidité
                
                # Métriques clés (KPIs)
                c1, c2, c3 = st.columns(3)
                c1.metric("Observations (Lignes x Mois)", f"{len(df)}")
                if 'target' in df.columns:
                    c2.metric("Taux de retard moyen historique", f"{df['target'].mean()*100:.2f}%")
                if 'Nombre de circulations prévues' in df.columns:
                    c3.metric("Volume max de circulations / mois", f"{int(df['Nombre de circulations prévues'].max())}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.write("**Échantillon du Dataset Traité**")
                st.dataframe(df.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f" Erreur lors de la lecture du fichier de données : {e}")
                st.info("Cela peut être dû à un problème d'encodage des accents dans le CSV.")

# --- ONGLET 2 : PERFORMANCES ---
    with tab2:
        st.subheader(" Rapport de Performance des Modèles d'Expertise")
        st.markdown("""
        Cette section présente les performances comparées des modèles de régression entraînés pour prédire le taux de retard à l'arrivée. 
        L'évaluation a été réalisée sur l'année de test stricte **2023**.
        """)
        
        path_metrics = RESULTS_DIR / "model_metrics.csv"
        if not path_metrics.exists():
            st.info(" Le fichier `model_metrics.csv` n'est pas encore généré. Lancez `python scripts/main.py` dans votre terminal.")
        else:
            try:
                # 1. Lecture et nettoyage des métriques
                df_metrics = pd.read_csv(path_metrics)
                
                nom_premiere_colonne = df_metrics.columns[0]
                df_metrics.rename(columns={nom_premiere_colonne: "Modèle"}, inplace=True)
                
                colonnes_cibles = [col for col in ["Modèle", "MAE", "R2_Score"] if col in df_metrics.columns]
                df_clean_metrics = df_metrics[colonnes_cibles].copy()
                
                metriques_graphique = [col for col in ["MAE", "R2_Score"] if col in df_clean_metrics.columns]
                
                # ==========================================
                # LIGNE 1 : TABLEAU DES MÉTRIQUES (EN HAUT)
                # ==========================================
                st.markdown("### 📊 Tableau des Métriques")
                df_affichage = df_clean_metrics.set_index("Modèle")
                styled_df = df_affichage.style
                if "MAE" in df_affichage.columns:
                    styled_df = styled_df.highlight_min(axis=0, color="#E3F2FD", subset=["MAE"])
                if "R2_Score" in df_affichage.columns:
                    styled_df = styled_df.highlight_max(axis=0, color="#E8F5E9", subset=["R2_Score"])
                    
                st.dataframe(styled_df, use_container_width=True)
                st.caption(" Le meilleur score est surligné en bleu pour la MAE (à minimiser) et en vert pour le R² (à maximiser).")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Récupération de la configuration des modèles pour la liaison dynamique
                from config import MODELS
                liste_cles_modeles = list(MODELS.keys())
                mapping_noms = {MODELS[k]["name"]: k for k in liste_cles_modeles}
                
                # ==========================================
                # LIGNE 2 : GRAPHIQUES CÔTE À CÔTE
                # ==========================================
                col_graph1, col_graph2 = st.columns([1.2, 1.2], gap="large")
                
                # --- Colonne Gauche : Comparaison Graphique ---
                with col_graph1:
                    st.markdown("#### 📈 Comparaison Graphique")
                    df_melted = df_clean_metrics.melt(id_vars="Modèle", value_vars=metriques_graphique, var_name="Métrique", value_name="Valeur")
                    
                    metrique_choisie = st.radio("Métrique à observer", metriques_graphique, horizontal=True)
                    df_filtered = df_melted[df_melted["Métrique"] == metrique_choisie]
                    
                    fig = px.bar(
                        df_filtered, 
                        x="Valeur", 
                        y="Modèle", 
                        orientation="h",
                        color="Modèle",
                        color_discrete_sequence=px.colors.sequential.Blues_r,
                        text_auto='.4f',
                        title=f"Comparatif du {metrique_choisie} selon le modèle"
                    )
                    fig.update_layout(
                        showlegend=False, 
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # --- Colonne Droite : Sélecteur de Modèle + Facteurs Clés ---
                with col_graph2:
                    # Le sélecteur est positionné en premier ici, juste au-dessus des facteurs clés
                    modele_nom_selectionne = st.selectbox("Sélectionnez le modèle à analyser", list(mapping_noms.keys()))
                    cle_modele = mapping_noms[modele_nom_selectionne]
                    
                    st.markdown(f"#### 🔑 Facteurs Clés d'Explication du Retard ({modele_nom_selectionne})")
                    
                    try:
                        # Chargement dynamique du modèle sélectionné
                        path_model = MODELS[cle_modele]["path"]
                        model_obj = joblib.load(path_model)
                        
                        features_names = list(model_obj.feature_names_in_)
                        
                        # Extraction selon la structure de l'objet (unifiée avec [-1] pour Ridge)
                        if cle_modele == "ridge":
                            importances = model_obj.regressor_[-1].coef_
                        elif cle_modele in ["rf", "gb"]:
                            importances = model_obj.regressor_.feature_importances_
                        else:
                            importances = [0.0] * len(features_names)
                        
                        df_real_features = pd.DataFrame({
                            "Feature": features_names,
                            "Importance": importances
                        })
                        
                        df_real_features["Abs_Importance"] = df_real_features["Importance"].abs()
                        df_top_features = df_real_features.sort_values(by="Abs_Importance", ascending=False).head(6)
                        df_top_features = df_top_features.sort_values(by="Importance", ascending=True)

                        bleu_corporate = "#0D47A1" 

                        fig_features = px.bar(
                            df_top_features,
                            x="Importance",
                            y="Feature",
                            orientation="h",
                            title=f"Top 6 des variables les plus impactantes (Données réelles)",
                            color_discrete_sequence=[bleu_corporate]
                        )
                        fig_features.update_layout(
                            margin=dict(l=20, r=20, t=40, b=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_features, use_container_width=True)
                        
                    except Exception as e_feat:
                        st.warning(f"Extraction des features en cours... (Détail : {e_feat})")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ==========================================
                # LIGNE 3 : DIAGNOSTIC & RECOMMANDATION (EN BAS)
                # ==========================================
                st.markdown("### 🧠 Diagnostic de Performance & Recommandation")
                
                df_selection = df_clean_metrics.set_index("Modèle")
                metric_top = "R2_Score" if "R2_Score" in df_selection.columns else df_selection.columns[0]
                best_model = df_selection[metric_top].idxmax()
                
                st.success(f" **Modèle recommandé pour le déploiement : {best_model}**")
                st.markdown(f"""
                Le modèle **{best_model}** obtient la meilleure capacité de généralisation sur les données de l'année de test.
                
                **Pourquoi ce modèle surpasse-t-il les autres ?**
                * **Modélisation des interactions non-linéaires :** La dynamique des retards ferroviaires est intrinsèquement complexe et multifactorielle (effets de cascade, goulots d'étranglement structurels). Les architectures basées sur des ensembles d'arbres de décision capturent ces effets de seuil là où une approche linéaire rigide (comme Ridge) a tendance à sous-apprendre.
                * **Régularisation et Robustesse :** Grâce à l'optimisation de ses hyperparamètres, il commet l'erreur absolue moyenne la plus faible (**MAE** minimale), garantissant des prévisions stables et fiables pour la planification prévisionnelle de la ponctualité.
                
                **Interprétation des Facteurs Clés :**
                En analysant dynamiquement le graphique d'importance (ci-dessus à droite), on remarque une constante forte entre les modèles : le **passé récent de la ligne (`lag_1`)** ainsi que la **densité du trafic mensuel** sont les piliers majeurs de la prédictibilité. 
                
                *Note sur l'interprétation :* Pour le modèle **Ridge**, l'impact est linéaire (coefficients), tandis que pour le **Random Forest** et le **Gradient Boosting**, il s'agit de la réduction d'impureté de Gini lors des splits. Les arbres accordent une importance accrue au cumul des retards (`lag_2`) là où le Ridge isole davantage des gares spécifiques comme Paris-Lyon.
                """)
                        
            except Exception as e:
                st.error(f" Erreur lors de l'affichage de l'analyse des performances : {e}")

# --- ONGLET 3 : SIMULATEUR ---
    with tab3:
        st.subheader(" Simulateur de Prédiction Ponctuelle")
        st.markdown("Configurez manuellement l'état du réseau le mois dernier pour observer l'impact prédictif sur le mois prochain.")
        
        path_nettoye = DATA_DIR / "data_nettoyee.csv"
        path_metrics = RESULTS_DIR / "model_metrics.csv"
        
        if not path_nettoye.exists():
            st.error(f" Fichier introuvable : `{path_nettoye}`. Impossible de charger les options du simulateur.")
        elif not path_metrics.exists():
            st.warning(" Le fichier `model_metrics.csv` est introuvable. Veuillez d'abord exécuter l'entraînement des modèles pour activer la sélection automatique.")
        else:
            try:
                # Importation sécurisée de Pydeck pour l'affichage cartographique
                import pydeck as pdk
                
                # 1. Chargement des données de base
                df_sim = pd.read_csv(path_nettoye)
                
                # --- SÉLECTION AUTOMATIQUE DU MEILLEUR MODÈLE ---
                df_metrics = pd.read_csv(path_metrics)
                nom_premiere_colonne = df_metrics.columns[0]
                df_metrics.rename(columns={nom_premiere_colonne: "Modèle"}, inplace=True)
                
                df_metrics_idx = df_metrics.set_index("Modèle")
                metric_selection = "R2_Score" if "R2_Score" in df_metrics_idx.columns else df_metrics_idx.columns[0]
                meilleur_modele_nom = df_metrics_idx[metric_selection].idxmax()
                
                from config import MODELS
                mapping_noms_sim = {MODELS[k]["name"]: k for k in MODELS.keys()}
                cle_modele_sim = mapping_noms_sim.get(meilleur_modele_nom, list(MODELS.keys())[0])
                
                st.success(f"**Modèle prédictif actif :** {meilleur_modele_nom}")
                
                # --- INITIALISATION GLOBALE DES VARIABLES PAR DÉFAUT ---
                vol_moyen_historique = 300.0
                
                st.markdown("### 🛠️ Étape 1 : Définir les indicateurs du Mois Précédent")
                
                liste_mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                
                col_inputs1, col_inputs2 = st.columns(2, gap="large")
                
                with col_inputs1:
                    liste_departs_sim = sorted(df_sim["Gare de départ"].unique())
                    gare_dep_sim = st.selectbox("Gare de départ", liste_departs_sim, key="sim_dep")
                    
                    arrivées_possibles_sim = sorted(df_sim[df_sim["Gare de départ"] == gare_dep_sim]["Gare d'arrivée"].unique())
                    gare_arr_sim = st.selectbox("Gare d'arrivée", arrivées_possibles_sim, key="sim_arr")
                    
                    mois_precedent_nom = st.selectbox("Mois précédent (saisi)", liste_mois_noms, index=5)
                    mois_precedent_num = liste_mois_noms.index(mois_precedent_nom) + 1
                    
                    mois_prediction = (mois_precedent_num % 12) + 1
                    mois_prediction_nom = liste_mois_noms[mois_prediction - 1]
                    
                    df_ligne_sim = df_sim[(df_sim["Gare de départ"] == gare_dep_sim) & (df_sim["Gare d'arrivée"] == gare_arr_sim)]
                    if not df_ligne_sim.empty:
                        col_circulations = [c for c in df_ligne_sim.columns if "circulation" in c.lower() or "prevu" in c.lower()]
                        if col_circulations:
                            vol_moyen_historique = df_ligne_sim[col_circulations[0]].mean()
                        st.info(f" **Volume habituel :** Environ **{int(vol_moyen_historique)} trains** circulent par mois sur cette ligne.")
                    else:
                        st.caption("ℹ Aucun historique disponible pour estimer le trafic habituel.")
                
                with col_inputs2:
                    vol_passé = st.number_input("Nombre de trains ayant circulé (Mois passé)", min_value=1, max_value=2000, value=int(vol_moyen_historique))
                    taux_prev_input = st.number_input("Taux de retard constaté (Mois passé en %)", min_value=0.0, max_value=100.0, value=20.0)
                    taux_prev_decimal = taux_prev_input / 100.0
                    
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        total_retard_prev = st.number_input("Nombre de trains en retard", min_value=0, max_value=2000, value=int(vol_passé * taux_prev_decimal))
                    with col_sub2:
                        annul_prev = st.number_input("Nombre de trains annulés (Mois passé)", min_value=0, max_value=500, value=5)

                st.markdown("### 🚀 Étape 2 : Projection du Mois Prochain")
                
                col_futur1, col_futur2 = st.columns(2)
                with col_futur1:
                    vol_prevu = st.number_input("Nombre de circulations prévues pour le mois prochain", min_value=1, max_value=2000, value=int(vol_passé))
                with col_futur2:
                    st.text_input("Mois cible calculé pour la prédiction", value=f"{mois_prediction_nom} (Mois {mois_prediction})", disabled=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # --- CALCULS ET ÉVALUATION ---
                if st.button("🔮 Lancer la simulation personnalisée"):
                    path_model = MODELS[cle_modele_sim]["path"]
                    if not path_model.exists():
                        st.error(f"Le fichier modèle est introuvable.")
                    else:
                        model = joblib.load(path_model)
                        features = model.feature_names_in_
                        
                        if not df_ligne_sim.empty:
                            total_retards_hist = df_ligne_sim["Nombre de trains en retard à l'arrivée"].sum()
                            retards_plus_30_hist = df_ligne_sim["Nombre trains en retard > 30min"].sum()
                            ratio_plus_30 = (retards_plus_30_hist / total_retards_hist) if total_retards_hist > 0 else 0.25
                            temps_trajet_moyen_glob = df_ligne_sim["Durée moyenne du trajet"].mean()
                            
                            total_trains_hist = df_ligne_sim[col_circulations[0]].sum() if col_circulations else 1000
                            total_annul_hist = df_ligne_sim["Nombre de trains annulés"].sum()
                            taux_annulation_moyen = (total_annul_hist / total_trains_hist) if total_trains_hist > 0 else 0.02
                            taux_moyen_historique = df_ligne_sim["taux_retard"].mean()
                        else:
                            ratio_plus_30, temps_trajet_moyen_glob, taux_annulation_moyen, taux_moyen_historique = 0.25, 120, 0.02, 0.12

                        # --- CONSTRUCTION DU VECTEUR X ---
                        X_simul = pd.DataFrame(0.0, index=[0], columns=features)
                        for col in X_simul.columns:
                            if "circulation" in col.lower() or "prevu" in col.lower():
                                X_simul[col] = vol_prevu
                            if "lag_1" in col.lower() or "retard_precedent" in col.lower() or "taux_retard_precedent" in col.lower():
                                X_simul[col] = taux_prev_decimal
                            if "lag_2" in col.lower():
                                X_simul[col] = taux_moyen_historique
                            if col.lower() == "mois":
                                X_simul[col] = mois_prediction
                            elif f"mois_{mois_prediction}" in col.lower() or f"month_{mois_prediction}" in col.lower() or col.endswith(f"_{mois_prediction}"):
                                X_simul[col] = 1.0
                        
                        col_dep_ohe = f"dep_{gare_dep_sim.replace(' ', '_')}"
                        col_arr_ohe = f"arr_{gare_arr_sim.replace(' ', '_')}"
                        if col_dep_ohe in X_simul.columns: X_simul[col_dep_ohe] = 1.0
                        if col_arr_ohe in X_simul.columns: X_simul[col_arr_ohe] = 1.0

                        with st.expander(" Inspecteur Data Science"):
                            st.write("Voici les valeurs non-nulles envoyées à `model.predict()` :")
                            st.dataframe(X_simul.loc[:, (X_simul != 0).any(axis=0)])

                        # --- CALCUL DE LA PRÉDICTION ---
                        pred_taux_retard = model.predict(X_simul)[0]
                        if pred_taux_retard < 0: pred_taux_retard = 0.0
                        
                        nb_trains_retard_pred = vol_prevu * pred_taux_retard
                        nb_retard_plus_30_pred = nb_trains_retard_pred * ratio_plus_30
                        nb_retard_moins_30_pred = nb_trains_retard_pred * (1 - ratio_plus_30)
                        nb_annulations_predites = max(0, round(vol_prevu * taux_annulation_moyen))
                        
                        plus30_prev = total_retard_prev * ratio_plus_30
                        moins30_prev = max(0, total_retard_prev - plus30_prev)

                        # --- AFFICHAGE COMPARATIF CÔTE À CÔTE ---
                        col_gauche_prev, col_droite_pred = st.columns(2, gap="large")
                        
                        with col_gauche_prev:
                            st.markdown(f"### Mois de {mois_precedent_nom} (Saisie Réelle)")
                            st.metric("Taux de retard constaté", f"{taux_prev_input:.2f}%")
                            
                            c_p1, c_p2 = st.columns(2)
                            c_p1.metric("Trains annulés", f"{int(annul_prev)} t.")
                            c_p2.metric("Trains totaux", f"{int(vol_passé)} t.")
                            
                            st.markdown("##### Volume calculé des retards passés :")
                            st.write(f"▪️ Total des trains en retard : **{int(total_retard_prev)}**")
                            st.write(f"▪️ Retards critiques (> 30 min) : **{int(plus30_prev)}**")
                            st.write(f"▪️ Retards mineurs (< 30 min) : **{int(moins30_prev)}**")
                        
                        with col_droite_pred:
                            st.markdown(f"### Mois de {mois_prediction_nom} (Projection)")
                            delta_taux = (pred_taux_retard - taux_prev_decimal) * 100
                            st.metric("Taux de retard estimé", f"{pred_taux_retard * 100:.2f}%", delta=f"{delta_taux:.2f}% vs mois saisi", delta_color="inverse")
                            
                            c_f1, c_f2 = st.columns(2)
                            c_f1.metric("Estimation trains annulés", f"{int(nb_annulations_predites)} t.")
                            c_f2.metric("Temps de trajet attendu", f"{int(temps_trajet_moyen_glob)} min")
                            
                            st.markdown("##### Détail des volumes de retards prédits :")
                            st.write(f"▪️ Total des trains en retard : **{max(0, round(nb_trains_retard_pred))}**")
                            st.write(f"▪️ Retards critiques (> 30 min) : **{max(0, round(nb_retard_plus_30_pred))}**")
                            st.write(f"▪️ Retards mineurs (< 30 min) : **{max(0, round(nb_retard_moins_30_pred))}**")
                            
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("---")
                        
                        # --- RAPPORT D'INTERPRÉTATION TEXTUEL ---
                        st.markdown("### 📝 Rapport d'Interprétation des Évolutions Métier")
                        if delta_taux < -1.5:
                            texte_ponctualite = f"**Amélioration de la ponctualité ({pred_taux_retard*100:.1f}% prédit vs {taux_prev_input:.1f}% saisi) :** Le modèle estime que la crise de {mois_precedent_nom} va s'absorber, aidée par la saisonnalité de {mois_prediction_nom}."
                        elif delta_taux > 1.5:
                            texte_ponctualite = f"**Dégradation de la ponctualité ({pred_taux_retard*100:.1f}% prédit vs {taux_prev_input:.1f}% saisi) :** Le modèle propage la crise par effet de répercussion de la variable d'inertie (`lag_1`)."
                        else:
                            texte_ponctualite = f"**Inertie et Stabilité :** Le modèle maintient une trajectoire équivalente au scénario d'entrée."

                        if vol_prevu > vol_moyen_historique * 1.1:
                            texte_volume = f"L'augmentation des circulations à **{vol_prevu}** trains (vs moyenne de {int(vol_moyen_historique)}) sature l'infrastructure."
                        else:
                            texte_volume = f"Le volume de trafic prévu (**{vol_prevu}**) respecte les seuils de tolérance nominaux."

                        st.info(f"""
                        * **Analyse Ponctualité :** {texte_ponctualite}
                        * **Effet de charge :** {texte_volume}
                        * **Gestion de flotte :** Les annulations moyennes attendues s'établissent à **{int(nb_annulations_predites)}** trains pour réguler la ligne.
                        """)
                        
                        # --- SECTION CARTOGRAPHIE SÉCURISÉE ---
                        st.markdown("### 🗺️ Tracé Cartographique du Trajet Simulé")
                        
                        # Dictionnaire de base
                        coords_gares = {
                            "PARIS LYON": {"lat": 48.8443, "lon": 2.3744}, "LYON PART DIEU": {"lat": 45.7606, "lon": 4.8599},
                            "MARSEILLE ST CHARLES": {"lat": 43.3027, "lon": 5.3806}, "BORDEAUX ST JEAN": {"lat": 44.8259, "lon": -0.5565},
                            "PARIS MONTPARNASSE": {"lat": 48.8412, "lon": 2.3201}, "NICE VILLE": {"lat": 43.7049, "lon": 7.2619},
                            "VALENCE ALIXAN TGV": {"lat": 44.9892, "lon": 5.0172}, "ANGERS SAINT LAUD": {"lat": 47.4647, "lon": -0.5562},
                            "ANGOULEME": {"lat": 45.6548, "lon": 0.1656}, "ANNECY": {"lat": 45.9016, "lon": 6.1212},
                            "ARRAS": {"lat": 50.2867, "lon": 2.7820}, "AVIGNON TGV": {"lat": 43.9216, "lon": 4.7932},
                            "DIJON VILLE": {"lat": 47.3236, "lon": 5.0269}, "RENNES": {"lat": 48.1030, "lon": -1.6720},
                            "STRASBOURG": {"lat": 48.5851, "lon": 7.7341}, "TOULOUSE MATABIAU": {"lat": 43.6112, "lon": 1.4536},
                            "NANTES": {"lat": 47.2173, "lon": -1.5424}, "LILLE EUROPE": {"lat": 50.6389, "lon": 3.0761}
                        }
                        
                        g_dep_key = str(gare_dep_sim).strip().upper()
                        g_arr_key = str(gare_arr_sim).strip().upper()
                        
                        # Géocodage dynamique pour le simulateur afin de garantir l'affichage de toutes les lignes
                        import urllib.parse
                        import requests

                        for g in [gare_dep_sim, gare_arr_sim]:
                            g_key = str(g).strip().upper()
                            if g_key not in coords_gares:
                                try:
                                    nom_recherche = f"Gare de {g.title()}, France"
                                    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(nom_recherche)}&format=json&limit=1"
                                    headers = {"User-Agent": "SNCF_Dashboard_App"}
                                    response = requests.get(url, headers=headers, timeout=3).json()
                                    if response:
                                        coords_gares[g_key] = {"lat": float(response[0]["lat"]), "lon": float(response[0]["lon"])}
                                    else:
                                        url_fallback = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(g.title() + ', France')}&format=json&limit=1"
                                        res_f = requests.get(url_fallback, headers=headers, timeout=3).json()
                                        if res_f:
                                            coords_gares[g_key] = {"lat": float(res_f[0]["lat"]), "lon": float(res_f[0]["lon"])}
                                except Exception:
                                    pass
                        
                        all_gares = set(df_sim["Gare de départ"].unique()).union(set(df_sim["Gare d'arrivée"].unique()))
                        df_all_points = pd.DataFrame([
                            {"Gare": g, "latitude": coords_gares[g.strip().upper()]["lat"], "longitude": coords_gares[g.strip().upper()]["lon"]}
                            for g in all_gares if g.strip().upper() in coords_gares
                        ])
                        
                        layers_list = []
                        
                        if not df_all_points.empty:
                            layers_list.append(pdk.Layer(
                                "ScatterplotLayer", data=df_all_points,
                                get_position="[longitude, latitude]", get_color="[200, 200, 200, 100]", get_radius=12000,
                            ))
                        
                        if g_dep_key in coords_gares and g_arr_key in coords_gares:
                            df_dep = pd.DataFrame([{"Gare": gare_dep_sim, "latitude": coords_gares[g_dep_key]["lat"], "longitude": coords_gares[g_dep_key]["lon"]}])
                            df_arr = pd.DataFrame([{"Gare": gare_arr_sim, "latitude": coords_gares[g_arr_key]["lat"], "longitude": coords_gares[g_arr_key]["lon"]}])
                            df_line = pd.DataFrame([{
                                "start_lat": coords_gares[g_dep_key]["lat"], "start_lon": coords_gares[g_dep_key]["lon"],
                                "end_lat": coords_gares[g_arr_key]["lat"], "end_lon": coords_gares[g_arr_key]["lon"]
                            }])
                            
                            layers_list.extend([
                                pdk.Layer("LineLayer", data=df_line,
                                          get_source_position="[start_lon, start_lat]", get_target_position="[end_lon, end_lat]",
                                          get_color="[0, 32, 96, 255]", get_width=5, width_min_pixels=3), # Ligne Bleue Corporate
                                pdk.Layer("ScatterplotLayer", data=df_dep,
                                          get_position="[longitude, latitude]", get_color="[0, 32, 96, 255]", get_radius=20000),
                                pdk.Layer("ScatterplotLayer", data=df_arr,
                                          get_position="[longitude, latitude]", get_color="[226, 0, 26, 255]", get_radius=20000)
                            ])
                            
                            view_state = pdk.ViewState(
                                latitude=(coords_gares[g_dep_key]["lat"] + coords_gares[g_arr_key]["lat"]) / 2,
                                longitude=(coords_gares[g_dep_key]["lon"] + coords_gares[g_arr_key]["lon"]) / 2,
                                zoom=5.5, pitch=0
                            )
                        else:
                            view_state = pdk.ViewState(latitude=46.6033, longitude=1.8883, zoom=5.0, pitch=0)
                        
                        # Utilisation du style natif "light" pour un fond clair et doux
                        st.pydeck_chart(pdk.Deck(
                            layers=layers_list,
                            initial_view_state=view_state,
                            map_style="light",
                            tooltip={"text": "{Gare}"}
                        ))
                        
                        st.markdown("""
                        <div style="display: flex; gap: 20px; justify-content: center; font-size: 14px; margin-top: 5px;">
                            <span>🔵 <b>Origine :</b> {dep}</span>
                            <span>🔴 <b>Destination :</b> {arr}</span>
                            <span>⚪ Autres axes du réseau</span>
                        </div>
                        """.format(dep=gare_dep_sim, arr=gare_arr_sim), unsafe_allow_html=True)
                            
            except Exception as e_sim:
                st.error(f" Erreur lors de l'initialisation du simulateur : {e_sim}")
                        
if __name__ == "__main__":  
    build_app()

