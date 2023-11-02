# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 15:15:28 2023
@author: m.jacoupy
"""

import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import os
import boto3
from io import BytesIO


# Constantes

GENERAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
IMG_PATH = os.path.join(GENERAL_PATH, "images/")
BUCKET_NAME = "bucketidb"
MOT_DE_PASSE = st.secrets["APP_MDP"]


s3 = boto3.resource('s3',
                  aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'])

# Chargement des données et des images
def load_file_from_s3(bucket_name, file_name):
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
    img_path = os.path.join(IMG_PATH, img_name)
    if os.path.exists(img_path):
        image = Image.open(img_path)
        st.sidebar.image(image, use_column_width=True)
    else:
        st.warning(f"L'image {img_name} n'existe pas dans le dossier {IMG_PATH}.")    

def save_df_to_s3(df, bucket_name, file_name):
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

def apply_custom_styles(cell_contents, available_color='#29AB87'):  # Ici, '#00FF00' est l'équivalent hexadécimal de 'lime'
    """
    Appliquez des styles personnalisés à chaque cellule en fonction de son contenu.
    
    Args:
    - cell_contents: Le contenu de la cellule.
    - available_color: La couleur à appliquer pour les cellules 'Disponible'. Par défaut, c'est '#00FF00' (lime).
    
    Returns:
    Le style à appliquer pour la cellule.
    """
    if cell_contents == 'Disponible':
        return f'background-color: {available_color}'
    elif cell_contents in ["Matin", "Après-midi"]:  # Si vous voulez ignorer ces valeurs
        return ''  # Pas de style particulier pour ces cellules
    elif "2023" in str(cell_contents) or "2024" in str(cell_contents) or "2025" in str(cell_contents):  # Combinaison des conditions pour 2023, 2024 et 2025
        return ''  # Pas de style pour cela, vous pourriez vouloir préciser ce cas
    else:
        return f'background-color: #ff8C00'  # Pour les autres cellules, pas 'Disponible' ou les valeurs spécifiques ignorées


 
def is_weekend(date):
    return date.weekday() >= 5  # 5 pour samedi, 6 pour dimanche


# Affichage des données
def display_selected_data(df, start_date, days_count, period='Journée'):
    """
    Affiche les données pour la période sélectionnée, en appliquant les styles nécessaires.
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
    option = st.radio(
        "Choisissez une période de visualisation des données",
        ("Aujourd'hui", "1 jour spécifique", "1 semaine glissante", "1 mois glissant")
    )
    st.write("---")

    if option == "Aujourd'hui":
        display_selected_data(df, today, 1)
    elif option == "1 jour spécifique":
        col1, col2 = st.columns([1, 4])
        with col1:
            selected_date = st.date_input("Sélectionnez une date", value=today)
        if selected_date:
            display_selected_data(df, selected_date, 1)
    elif option == "1 semaine glissante":
        display_selected_data(df, today, 7)
    elif option == "1 mois glissant":
        display_selected_data(df, today, 30)

            
def reserve_office(df, today, offices, excel):
    option = st.radio(
        "Choisissez une période de visualisation des données",
            ("1 jour spécifique", "Dans les 15 jours à venir"))
    
    # st.write("---")
            
    if option == "1 jour spécifique":
        with st.form(key='reservation_form1'):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                selected_date = st.date_input("Sélectionnez une date", value=today)
            with col2:
                period = st.radio("Quel créneau souhaitez-vous ?", 
                              ("Matin", "Après-midi", "Journée"), index=2
                              )
            with col3:
                office = st.radio("Quel bureau préférez vous ?", tuple(offices))

            display_selected_data(df, selected_date, 1, period)
                    
            # Input pour le nom sous lequel la réservation sera faite
            col1, col2 = st.columns([1,3])
            with col1:
                name = st.text_input("Entrez votre nom pour la réservation")

            # Bouton pour confirmer la réservation et déclencher la logique de sauvegarde
            if st.form_submit_button("Réserver", key=2):
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
                                    st.error(f"Le {office} n'est pas disponible pour {period_segment} le {selected_date.strftime('%d/%m/%Y')}.")
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
        
    if option == "Dans les 15 jours à venir":
        
                  
        # Définir les noms des colonnes qui correspondent aux bureaux
        office_columns = offices
        
        # Création d'un formulaire pour soumettre les réservations
        with st.form(key='reservation_form2'):
            st.write("Veuillez sélectionner les créneaux de réservation")
            
            start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=15)  # ou toute autre logique pour définir la période
        
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
                    header_cols = st.columns(6)
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
                            
                            cols = st.columns(6)
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
                    col1, col2 = st.columns([1,3])
                    with col1:
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
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_date = st.date_input("Sélectionnez une date", value=today)
    with col2:
        period = st.radio("Quel créneau souhaitez-vous ?", 
                      ("Matin", "Après-midi", "Journée"), index=2
                      )
    with col3:
        office = st.radio("Quel bureau préférez vous ?", tuple(offices))

    st.write("---")
    display_selected_data(df, selected_date, 1, period)
    
   
    # Bouton pour confirmer la réservation et déclencher la logique de sauvegarde
    if st.button("Annuler le créneau"):
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
                        st.success(f"Le {office} est maintenant disponible pour {period_segment} le {selected_date.strftime('%d/%m/%Y')}.")
        
            # Sauvegarder les modifications dans le DataFrame
            save_df_to_s3(df, BUCKET_NAME, excel)
            st.experimental_rerun()
        else:
            st.warning("Aucune case disponible ne correspond à vos critères de sélection.")



def main():
    st.set_page_config(layout="wide")
    today = datetime.date.today()

    # Configuration pour chaque flex office
    flex_config = {
        "Jungle": {
            "image": "serre.jpg",
            "excel": "FlexSerre.xlsx",
            "sidebar_image": "jungle.png",
            "offices": ["Baloo", "Stitch", "Rajah", "Meeko"]
        },
        "Aquarium": {
            "image": "aquarium.jpg",
            "excel": "FlexAqua.xlsx",
            "sidebar_image": "aqua.png",
            "offices": ["Némo", "Sébastien", "Tamatoa", "Polochon"]
        }
    }

    # Initialisation de st.session_state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        mot_de_passe_saisi = st.text_input("Entrez le mot de passe", type="password").upper()

        if mot_de_passe_saisi == MOT_DE_PASSE:
            st.session_state.authenticated = True
        else:
            st.write("Mot de passe incorrect. Veuillez réessayer.")

    if st.session_state.authenticated:
        flex = st.sidebar.selectbox("Choisissez votre flex office de rêve", list(flex_config.keys()), index=1)

        # Appliquer la configuration en fonction du choix
        load_image(flex_config[flex]["image"])
        df = load_file_from_s3(BUCKET_NAME, flex_config[flex]["excel"])
        load_image_sidebar(flex_config[flex]["sidebar_image"])

        tab_selection = st.sidebar.selectbox("Choisissez un onglet", ["Visualisation", "Réservation", "Annulation"])

        if tab_selection == "Visualisation":
            visualize_data(df, today)
        elif tab_selection == "Réservation":
            reserve_office(df, today, flex_config[flex]["offices"], flex_config[flex]["excel"])
        elif tab_selection == "Annulation":
            cancel_reservation(df, today, flex_config[flex]["offices"], flex_config[flex]["excel"])

if __name__ == "__main__":
    main()