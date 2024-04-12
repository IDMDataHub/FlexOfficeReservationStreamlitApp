#####################################################################
# =========================== LIBRAIRIES ========================== #
#####################################################################

import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import os
import boto3
from io import BytesIO


#####################################################################
# =========================== CONSTANTES ========================== #
#####################################################################

GENERAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
IMG_PATH = os.path.join(GENERAL_PATH, "images/")
BUCKET_NAME = "bucketidb"
MOT_DE_PASSE = st.secrets["APP_MDP"]


#####################################################################
# ========================= INFO GENERALES========================= #
#####################################################################

s3 = boto3.resource('s3',
                  aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'])


#####################################################################
# ==================== FONCTIONS D'ASSISTANCES ==================== #
#####################################################################

# ========================================================================================================================================
# CHARGEMENT DE DONNEES
def load_file_from_s3(bucket_name, file_name):
    """
    Charge un fichier depuis un bucket S3 spécifié et le convertit en un DataFrame pandas.

    Parameters:
    - bucket_name (str): Le nom du bucket S3 où le fichier est stocké.
    - file_name (str): Le nom du fichier à charger.

    Returns:
    - pandas.DataFrame: Un DataFrame contenant les données du fichier chargé.

    Raises:
    - FileNotFoundError: Si le fichier spécifié n'existe pas dans le bucket S3.
    - Exception: Pour toute autre erreur rencontrée lors de l'accès au fichier S3.
    """
    # Vérifiez si l'objet existe dans le bucket
    obj = s3.Object(bucket_name, file_name)
    try:
        # Essayez de récupérer l'objet
        obj.load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # L'objet n'existe pas.
            raise FileNotFoundError(f"File {file_name} not found in S3 bucket {bucket_name}")
        else:
            # Quelque chose d'autre s'est mal passé.
            raise

    # Lisez le fichier Excel dans un DataFrame
    with BytesIO(obj.get()['Body'].read()) as bIO:
        df = pd.read_excel(bIO)

    return df

def load_image(img_name):
    """
    Charge et affiche une image depuis le dossier des images, en ajustant sa taille.

    Parameters:
    - img_name (str): Le nom de l'image à charger et à afficher.

    Returns:
    None

    Notes:
    Affiche un avertissement si l'image spécifiée n'existe pas dans le dossier des images.
    """
    img_path = os.path.join(IMG_PATH, img_name)
    if os.path.exists(img_path):
        image = Image.open(img_path)
        
        # Obtenez les dimensions originales de l'image
        width, height = image.size
        
        # Calculez la nouvelle hauteur
        new_height = int(height * 0.67)  # Réduire de 33% équivant à multiplier par 0.67
        
        # Redimensionnez l'image
        image_resized = image.resize((width, new_height))
        
        st.image(image_resized, use_column_width=True)
    else:
        st.warning(f"L'image {img_name} n'existe pas dans le dossier {IMG_PATH}.")

def load_image_sidebar(img_name):
    """
    Charge et affiche une image dans la barre latérale de l'application Streamlit.

    Parameters:
    - img_name (str): Le nom de l'image à charger et à afficher dans la barre latérale.

    Returns:
    None

    Notes:
    Affiche un avertissement si l'image spécifiée n'existe pas dans le dossier des images.
    """
    img_path = os.path.join(IMG_PATH, img_name)
    if os.path.exists(img_path):
        image = Image.open(img_path)
        st.sidebar.image(image, use_column_width=True)
    else:
        st.warning(f"L'image {img_name} n'existe pas dans le dossier {IMG_PATH}.")    

# ========================================================================================================================================
# SAUVEGARDE
def save_df_to_s3(df, bucket_name, file_name):
    """
    Sauvegarde un DataFrame pandas dans un fichier Excel et le stocke dans un bucket S3.

    Parameters:
    - df (pandas.DataFrame): Le DataFrame à sauvegarder.
    - bucket_name (str): Le nom du bucket S3 où le fichier sera enregistré.
    - file_name (str): Le nom sous lequel le fichier sera enregistré dans le bucket S3.

    Returns:
    None

    Notes:
    Le fichier est sauvegardé au format Excel (xlsx).
    """
    # Créez un buffer pour stocker le fichier Excel
    excel_buffer = BytesIO()

    # Écrivez le DataFrame dans le buffer
    with pd.ExcelWriter(excel_buffer) as writer:
        df.to_excel(writer, index=False)

    # Réinitialisez la position du buffer à 0
    excel_buffer.seek(0)

    # Obtenez l'objet bucket
    bucket = s3.Bucket(bucket_name)

    # Stockez le fichier Excel dans S3
    bucket.put_object(
        Key=file_name,
        Body=excel_buffer.read(),
        ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# ========================================================================================================================================
# GRAPH ET AFFICHAGE
def apply_custom_styles(cell_contents, available_color='#29AB87'):
    """
    Applique des styles personnalisés à chaque cellule d'un DataFrame en fonction de son contenu.

    Parameters:
    - cell_contents (various): Le contenu de la cellule à laquelle appliquer le style.
    - available_color (str, optional): La couleur à utiliser pour les cellules marquées comme 'Disponible'. Par défaut à '#29AB87'.

    Returns:
    - str: Une chaîne CSS décrivant le style à appliquer à la cellule.
    """
    if cell_contents == 'Disponible':
        return f'background-color: {available_color}'
    elif cell_contents in ["Matin", "Après-midi"]:  # Si vous voulez ignorer ces valeurs
        return ''  # Pas de style particulier pour ces cellules
    elif "2023" in str(cell_contents) or "2024" in str(cell_contents) or "2025" in str(cell_contents):  # Combinaison des conditions pour 2023, 2024 et 2025
        return ''  # Pas de style pour cela, vous pourriez vouloir préciser ce cas
    else:
        return f'background-color: #ff8C00'  # Pour les autres cellules, pas 'Disponible' ou les valeurs spécifiques ignorées

# Affichage des données
def display_selected_data(df, start_date, days_count, period='Journée'):
    """
    Affiche les données pour une période et un type de créneau sélectionnés, avec des styles personnalisés.

    Parameters:
    - df (pandas.DataFrame): Le DataFrame contenant les données à afficher.
    - start_date (datetime.date): La date de début de la période à afficher.
    - days_count (int): Le nombre de jours à partir de la date de début à inclure dans l'affichage.
    - period (str, optional): Le type de créneau à afficher ('Matin', 'Après-midi', 'Journée'). Par défaut à 'Journée'.

    Returns:
    None
    """
    try:
        # Vérifiez si la date de début est dans le passé
        if start_date < datetime.datetime.today().date():
            st.error("La date de début ne peut pas être dans le passé. Veuillez sélectionner une date valide.")
            return

        # Calcul de la date de fin basée sur le nombre de jours (chaque jour ayant deux entrées, matin et après-midi).
        end_date = start_date + datetime.timedelta(days=days_count)

        # Filtrage des données pour les jours choisis.
        mask = (df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] < pd.Timestamp(end_date))
        data_period = df.loc[mask]
        
        # Filtrage pour exclure les week-ends
        data_period = data_period[~data_period['Date'].apply(is_weekend)]
        
        # Filtrage sur la période spécifique de la journée, si spécifié
        if period != 'Journée':  # Si la période est spécifiée (i.e., pas 'All')
            # Nous filtrons sur la colonne 'Période' pour inclure uniquement les entrées correspondantes
            data_period = data_period[data_period['Créneau'] == period]
        
        # Formatter les dates dans le DataFrame pour l'affichage
        data_period['Date'] = data_period['Date'].dt.strftime('%A %d %B %Y')
        
        if not data_period.empty:
            # Nous appliquons un style spécifique aux cellules en fonction de leur contenu.
            styled_data = data_period.style.map(apply_custom_styles)
            # Cachez l'index et affichez le DataFrame stylisé.
            st.table(styled_data)
        else:
            st.warning("Aucune donnée disponible pour la période sélectionnée.")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de l'affichage des données : {e}")

def visualize_data(df, today):
    """
    Permet à l'utilisateur de choisir une période de visualisation des données et affiche les données correspondantes.

    Parameters:
    - df (pandas.DataFrame): Le DataFrame contenant les données à visualiser.
    - today (datetime.date): La date actuelle, utilisée comme point de départ pour les sélections de dates.

    Returns:
    None

    Notes:
    Propose à l'utilisateur de choisir entre visualiser les données pour un jour spécifique ou pour les 15 prochains jours.
    """
    option = st.radio(
        "Choisissez une période de visualisation des données",
        ("Dans les 15 jours", "1 jour spécifique")
    )
    st.write("---")

    if option == "1 jour spécifique":
        sel_periode, _ = st.columns([1, 4])
        with sel_periode:
            selected_date = st.date_input("Sélectionnez une date", value=today)
        if selected_date:
            display_selected_data(df, selected_date, 1)
    elif option == "Dans les 15 jours":
        display_selected_data(df, today, 15)

# ========================================================================================================================================
# CALCULS
def is_weekend(date):
    """
    Détermine si une date donnée correspond à un week-end.

    Parameters:
    - date (datetime.date): La date à vérifier.

    Returns:
    - bool: True si la date est un samedi ou un dimanche, False sinon.
    """
    return date.weekday() >= 5  # 5 pour samedi, 6 pour dimanche

# ========================================================================================================================================
# CREATION ET MODIFICATION      
def reserve_office(df, today, offices, excel):
    """
    Permet à l'utilisateur de réserver un bureau pour une date spécifique ou dans le mois en cours. 
    L'utilisateur peut choisir une date, une période (matin, après-midi, journée) et un bureau spécifique pour la réservation.

    Parameters:
    - df (pandas.DataFrame): DataFrame contenant les données de réservation des bureaux.
    - today (datetime.date): La date actuelle, utilisée comme référence pour les réservations.
    - offices ([str]): Liste des bureaux disponibles pour la réservation.
    - excel (str): Le nom du fichier Excel dans le bucket S3 où les données de réservation sont stockées.

    Returns:
    None

    Notes:
    Après la soumission du formulaire de réservation par l'utilisateur, la fonction vérifie la disponibilité du bureau sélectionné
    pour la période donnée et met à jour le DataFrame et le fichier Excel sur S3 en conséquence.
    """
    option = st.radio(
        "Choisissez une période de visualisation des données",
            ("1 jour spécifique", "Dans le mois"))
            
    if option == "1 jour spécifique":
        with st.form(key='reservation_form1'):
            col_date, col_creneau, col_bureau = st.columns([1, 1, 1])
            with col_date:
                selected_date = st.date_input("Sélectionnez une date", value=today)
            with col_creneau:
                period = st.radio("Quel créneau souhaitez-vous ?", 
                              ("Matin", "Après-midi", "Journée"), index=2
                              )
            with col_bureau:
                office = st.radio("Quel bureau préférez vous ?", tuple(offices))

            display_selected_data(df, selected_date, 1, period)
                    
            # Input pour le nom sous lequel la réservation sera faite
            col_name, _ = st.columns([1,3])
            with col_name:
                name = st.text_input("Entrez votre nom pour la réservation")

            submitted = st.form_submit_button("Réserver")

            # Bouton pour confirmer la réservation et déclencher la logique de sauvegarde
            if submitted:
                if name:  # Vérifiez si le nom n'est pas vide
                    try:
                        # Créez un masque pour les lignes correspondant à la date sélectionnée et à la période.
                        mask = (df['Date'] == pd.Timestamp(selected_date))
            
                        if period != 'Journée':
                            mask &= (df['Créneau'] == period)
                        
                        # Trouver les lignes qui correspondent à nos critères
                        matching_rows = df.loc[mask]
            
                        if not matching_rows.empty:
                            # Si la période est "Journée", nous voulons vérifier la disponibilité pour chaque segment de la journée.
                            if period == 'Journée':
                                periods_to_check = ['Matin', 'Après-midi']
                            else:
                                periods_to_check = [period]  # sinon, nous ne vérifions que la période spécifique sélectionnée.
            
                            for period_segment in periods_to_check:
                                specific_mask = (matching_rows['Créneau'] == period_segment)
                                # Vérifier si le bureau est disponible pour la réservation
                                if 'Disponible' in matching_rows.loc[specific_mask, office].values:
                                    # Bureau disponible, donc mise à jour pour indiquer qu'il est maintenant réservé.
                                    df.loc[mask & specific_mask, office] = name
                                else:
                                    # Si le bureau n'est pas disponible (c'est-à-dire que la valeur n'est pas "Disponible"), nous affichons une erreur.
                                    st.error(f"Le bureau {office} n'est pas disponible pour {period_segment} le {selected_date.strftime('%d/%m/%Y')}.")
                                    return  # Nous retournons ici pour éviter d'essayer de sauvegarder des modifications ou d'autres opérations.
                            
                            # Si nous sommes ici, cela signifie que toutes les réservations nécessaires sont disponibles et ont été mises à jour.
                            # Nous allons maintenant sauvegarder le DataFrame mis à jour.
                            save_df_to_s3(df, BUCKET_NAME, excel)
                            st.success("Réservation effectuée avec succès.")
                            st.experimental_rerun()
                        else:
                            st.warning("Aucune case disponible ne correspond à vos critères de sélection.")
            
                    except Exception as e:
                        st.error(f"Une erreur s'est produite lors de la mise à jour de la réservation : {e}")
                else:
                    st.warning("Veuillez entrer votre nom pour effectuer une réservation.")
        
    if option == "Dans le mois":
        
                  
        # Définir les noms des colonnes qui correspondent aux bureaux
        office_columns = offices
        
        # Création d'un formulaire pour soumettre les réservations
        with st.form(key='reservation_form2'):
            st.write("Veuillez sélectionner les créneaux de réservation")
            
            start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=60)  # ou toute autre logique pour définir la période
        
            # Vous devez vous assurer que les dates sélectionnées sont valides (la date de fin doit venir après la date de début)
            if start_date > end_date:
                st.error("La date de fin doit venir après la date de début.")
            else:
                # Filtrer les données de réservation pour les dates sélectionnées
                mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
                filtered_data = df.loc[mask]
        
                # Si aucune donnée n'est disponible pour la période sélectionnée, affichez un message.
                if filtered_data.empty:
                    st.write("Aucune donnée de réservation disponible pour la période sélectionnée.")
                else:
                    # Créer une rangée pour les en-têtes de colonne
                    header_cols = st.columns(len(office_columns)+2)
                    header_cols[0].write("Date")
                    header_cols[1].write("Créneau")
                    for i, office in enumerate(office_columns, start=2):
                        header_cols[i].write(office)
                            
                    # Création d'un dictionnaire pour stocker les sélections des utilisateurs
                    user_selections = {}
        
                    for index, row in filtered_data.iterrows():
                        current_date = row['Date']  # Assurez-vous que 'Date' est un objet datetime
                        if not is_weekend(current_date):
                            date_str = current_date.strftime('%A %d %B %Y')
                            period = row['Créneau']
                            user_selections[f"{date_str}-{period}"] = {}
                            
                            cols = st.columns(len(office_columns)+2)
                            cols[0].write(date_str)
                            cols[1].write(period)
                
                            for i, office in enumerate(office_columns, start=2):
                                is_available = row[office] == 'Disponible'
                                if is_available:
                                    # Si le bureau est disponible, créez une checkbox et enregistrez l'état dans le dictionnaire
                                    checkbox_checked = cols[i].checkbox('', key=f"{date_str}-{period}-{office}")
                                    user_selections[f"{date_str}-{period}"][office] = checkbox_checked
                                else:
                                    # Si le bureau n'est pas disponible, désactivez la checkbox
                                    cols[i].write(' -')
                                    user_selections[f"{date_str}-{period}"][office] = False  # Non disponible ou non sélectionné
                            
                            if period == "Après-midi":
                                st.write("---")

                    # Bouton de soumission du formulaire
                    col_name, _ = st.columns([1,3])
                    with col_name:
                        name = st.text_input("Entrez votre nom pour la réservation")
                    submitted = st.form_submit_button("Soumettre les réservations")
                    
                # Après la soumission du formulaire, affichez les sélections de l'utilisateur ou traitez-les selon vos besoins                      
                if submitted:
                    if name:  # Vérifiez si le nom n'est pas vide
                        # Itérer sur toutes les sélections de l'utilisateur et mettre à jour le DataFrame
                        for date_period, reservations in user_selections.items():
                            try:
                                # Vérifiez si "Après-midi" est dans la chaîne et ajustez la logique de division en conséquence
                                if "Après-midi" in date_period:
                                    parts = date_period.split('-')
                                    if len(parts) > 2:  # Cela signifie que "Après-midi" était une partie de la chaîne
                                        # Reconstruire 'selected_date_str' et 'period' en tenant compte de l'anomalie "Après-midi"
                                        selected_date_str = parts[0]  # La date reste la première partie
                                        period = "Après-midi"  # Attribuer manuellement la valeur "Après-midi"
                                    else:
                                        # Si la longueur n'est pas supérieure à 2, cela signifie que la division est normale
                                        selected_date_str, period = parts
                                else:
                                    # Pour toutes les autres chaînes, la logique de division normale s'applique
                                    selected_date_str, period = date_period.split('-')
                        
                                # Convertir la chaîne de date formatée en objet datetime
                                selected_date = datetime.datetime.strptime(selected_date_str, '%A %d %B %Y')
                             
                            except ValueError:
                                continue  # Passe à la prochaine itération, en ignorant le reste du code dans la boucle
                            
                            # Convertir la chaîne de date formatée en objet datetime
                            try:
                                selected_date = datetime.datetime.strptime(selected_date_str, '%A %d %B %Y')
                            except ValueError:
                                st.error(f"Le format de la date est incorrect : {selected_date_str}")
                                return
                    
                            # Créez un masque pour les lignes correspondant à la date sélectionnée et à la période.
                            mask = (df['Date'] == selected_date) & (df['Créneau'] == period)
                    
                            # Itérer sur les réservations dans le dictionnaire pour la date et la période données
                            for office, is_booked in reservations.items():
                                if is_booked:
                                    # Si l'utilisateur a coché la case, nous mettons à jour le DataFrame.
                                    # Vérifiez si le bureau est disponible pour la réservation
                                    if 'Disponible' in df.loc[mask, office].values:
                                        # Bureau disponible, donc mise à jour pour indiquer qu'il est maintenant réservé.
                                        df.loc[mask, office] = name  # Mettre le nom de la personne qui a réservé
                                    else:
                                        # Si le bureau n'est pas disponible (c'est-à-dire que la valeur n'est pas "Disponible"), nous affichons une erreur.
                                        st.error(f"Le {office} n'est pas disponible pour {period} le {selected_date_str}.")
                                        return  # Nous retournons ici pour éviter d'essayer de sauvegarder des modifications ou d'autres opérations.
                    
                        # Si nous sommes ici, cela signifie que toutes les réservations nécessaires sont disponibles et ont été mises à jour.
                        # Nous allons maintenant sauvegarder le DataFrame mis à jour.
                        save_df_to_s3(df, BUCKET_NAME, excel)
                        st.success("Réservation effectuée avec succès.")
                        st.experimental_rerun()
                    else:
                        st.warning("Veuillez entrer votre nom pour effectuer une réservation.")

def cancel_reservation(df, today, offices, excel):
    """
    Permet à l'utilisateur d'annuler une réservation de bureau précédemment effectuée. L'utilisateur peut sélectionner
    une date, une période (matin, après-midi, journée) et un bureau spécifique dont la réservation doit être annulée.

    Parameters:
    - df (pandas.DataFrame): DataFrame contenant les données de réservation des bureaux.
    - today (datetime.date): La date actuelle, utilisée comme référence pour les annulations.
    - offices ([str]): Liste des bureaux disponibles pour l'annulation de réservations.
    - excel (str): Le nom du fichier Excel dans le bucket S3 où les données de réservation sont stockées.

    Returns:
    None

    Notes:
    La fonction affiche les données de réservation pour la période sélectionnée et permet à l'utilisateur d'annuler 
    une ou plusieurs réservations. Après confirmation, le DataFrame et le fichier Excel sur S3 sont mis à jour pour refléter l'annulation.
    """
    col_date, col_creneau, col_bureau = st.columns([1, 1, 1])
    with col_date:
        selected_date = st.date_input("Sélectionnez une date", value=today)
    with col_creneau:
        period = st.radio("Quel créneau souhaitez-vous ?", 
                      ("Matin", "Après-midi", "Journée"), index=2)
    with col_bureau:
        office = st.radio("Quel bureau préférez vous ?", tuple(offices))

    with st.form(key="cancel"):
        display_selected_data(df, selected_date, 1, period)
        
       
        cancel = st.form_submit_button("Annuler le créneau")
        # Bouton pour confirmer la réservation et déclencher la logique de sauvegarde
        if cancel:
            mask = (df['Date'] == pd.Timestamp(selected_date))
            
            if period != 'Journée':
                mask &= (df['Créneau'] == period)
            
            # Trouver les lignes qui correspondent à nos critères
            matching_rows = df.loc[mask]
            
            if not matching_rows.empty:
                # Si la période est "Journée", nous voulons vérifier la disponibilité pour chaque segment de la journée.
                if period == 'Journée':
                    periods_to_check = ['Matin', 'Après-midi']
                else:
                    periods_to_check = [period]  # sinon, nous ne vérifions que la période spécifique sélectionnée.
            
                for period_segment in periods_to_check:
                    specific_mask = (matching_rows['Créneau'] == period_segment)
                    # Obtenez les lignes spécifiques pour cette période
                    period_rows = df.loc[mask & specific_mask]
            
                    # Vérifiez chaque bureau dans les lignes sélectionnées pour cette période
                    for index, row in period_rows.iterrows():
                        if row[office] != 'Disponible':  # Si le bureau n'est pas disponible
                            # Mettre à jour le statut du bureau pour le rendre disponible
                            df.at[index, office] = 'Disponible'
                            st.success(f"Le bureau {office} est maintenant disponible pour {period_segment} le {selected_date.strftime('%d/%m/%Y')}.")
            
                # Sauvegarder les modifications dans le DataFrame
                save_df_to_s3(df, BUCKET_NAME, excel)
                st.experimental_rerun()
            else:
                st.warning("Aucune case disponible ne correspond à vos critères de sélection.")


#####################################################################
# ====================== FONCTION PRINCIPALE ====================== #
#####################################################################

def main():
    """
    Fonction principale exécutant l'application Streamlit pour la réservation de bureaux. 
    Configure la page, gère l'authentification des utilisateurs, et permet la visualisation, la réservation,
    et l'annulation des réservations de bureaux.

    Returns:
    None

    Notes:
    L'application offre une interface utilisateur pour choisir un 'flex office', visualiser les disponibilités,
    réserver ou annuler des bureaux. Les utilisateurs doivent s'authentifier avec un mot de passe avant d'accéder aux fonctionnalités.
    """
    st.set_page_config(layout="wide", page_icon=":clock3:", page_title="Flex Offices")

    today = datetime.date.today()

    # Configuration pour chaque flex office
    flex_config = {
        "Aquarium": {
            "image": "aquarium.jpg",
            "excel": "FlexAqua.xlsx",
            "sidebar_image": "aqua.png",
            "plan": "plan_aqua.png",
            "offices": ["Aquali", "Carapuce", "Hank", "Némo", "Polochon", "Tamatoa"]
            },
        "Jungle": {
            "image": "serre.jpg",
            "excel": "FlexSerre.xlsx",
            "sidebar_image": "jungle.png",
            "plan": "plan_jungle.png",
            "offices": ["Baloo", "Stitch", "Rajah", "Meeko"]
            },
        "IMA": {
            "image": "clinicaltrial.jpg",
            "excel": "FlexIMA.xlsx",
            "sidebar_image": "clinicaltrial.png",
            "plan": "plan_ima.png",
            "offices": ["Bureau 1", "Bureau 2", "Bureau 3"]
            }    
    }

    # Initialisation de st.session_state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        _, col_mdp, _ = st.columns([2, 3, 2])
        with col_mdp:
            mot_de_passe_saisi = st.text_input("Entrez le mot de passe", type="password").upper()

            if mot_de_passe_saisi == MOT_DE_PASSE:
                st.session_state.authenticated = True
            else:
                st.write("Mot de passe incorrect. Veuillez réessayer.")

    if st.session_state.authenticated:
        flex = st.sidebar.selectbox("Choisissez votre flex office", list(flex_config.keys()), index=0)

        # Appliquer la configuration en fonction du choix
        load_image(flex_config[flex]["image"])
        df = load_file_from_s3(BUCKET_NAME, flex_config[flex]["excel"])
        load_image_sidebar(flex_config[flex]["sidebar_image"])

        tab_selection = st.sidebar.selectbox("Que souhaitez-vous faire ?", ["Visualisation", "Réservation", "Annulation"])
        st.write("---")
        load_image_sidebar(flex_config[flex]["plan"])
        if tab_selection == "Visualisation":
            visualize_data(df, today)
        elif tab_selection == "Réservation":
            reserve_office(df, today, flex_config[flex]["offices"], flex_config[flex]["excel"])
        elif tab_selection == "Annulation":
            cancel_reservation(df, today, flex_config[flex]["offices"], flex_config[flex]["excel"])

if __name__ == "__main__":
    main()