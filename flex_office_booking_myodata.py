#####################################################################
# =========================== LIBRAIRIES ========================== #
#####################################################################

import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import os


#####################################################################
# =========================== CONSTANTS =========================== #
#####################################################################

GENERAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
IMG_PATH = os.path.join(GENERAL_PATH, "images/")
PASSWORD = st.secrets["APP_MDP"]
LOCAL_FOLDER = "flexoffice"

#####################################################################
# ========================= GENERAL INFO ========================== #
#####################################################################

#####################################################################
# ===================== ASSISTANCE FUNCTIONS ====================== #
#####################################################################

# ========================================================================================================================================
# DATA LOADING
def load_file_from_local(folder_name, file_name):
    """
    Loads a local Excel file from a specific folder.

    Parameters:
    - folder_name (str): Name of the local subfolder (e.g., "flexoffice")
    - file_name (str): Name of the Excel file to load (e.g., "FlexIMA.xlsx")

    Returns:
    - pandas.DataFrame: Data loaded from the Excel file

    Raises:
    - FileNotFoundError: If the file does not exist
    """
    file_path = os.path.join(GENERAL_PATH, folder_name, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    return pd.read_excel(file_path)

def load_image(img_name):
    """
    Load and display an image from the images folder, adjusting its size.

    Parameters:
    - img_name (str): The name of the image to load and display.

    Returns:
    None

    Notes:
    Displays a warning if the specified image does not exist in the images folder.
    """
    img_path = os.path.join(IMG_PATH, img_name)  # Construct the full path to the image
    if os.path.exists(img_path):
        image = Image.open(img_path)  # Open the image file
        
        # Get the original dimensions of the image
        width, height = image.size
        
        # Calculate the new height
        new_height = int(height * 0.67)  # Reduce height by 33% which is equivalent to multiplying by 0.67
        
        # Resize the image
        image_resized = image.resize((width, new_height))
        
        # Display the resized image using Streamlit
        st.image(image_resized, use_column_width=True)
    else:
        # Display a warning if the image does not exist
        st.warning(f"The image {img_name} does not exist in the folder {IMG_PATH}.")

def load_image_sidebar(img_name):
    """
    Load and display an image in the sidebar of the Streamlit application.

    Parameters:
    - img_name (str): The name of the image to load and display in the sidebar.

    Returns:
    None

    Notes:
    Displays a warning if the specified image does not exist in the images folder.
    """
    img_path = os.path.join(IMG_PATH, img_name)  # Construct the full path to the image
    if os.path.exists(img_path):
        image = Image.open(img_path)  # Open the image file
        st.sidebar.image(image, use_column_width=True)  # Display the image in the sidebar using Streamlit
    else:
        st.warning(f"The image {img_name} does not exist in the folder {IMG_PATH}.")  # Display a warning if the image does not exist

# ========================================================================================================================================
# SAVE
def save_file_to_local(df, folder_name, file_name):
    """
    Saves a DataFrame to an Excel file in a specific local folder.

    Parameters:
    - df (pandas.DataFrame): Data to save
    - folder_name (str): Name of the local subfolder (e.g., "flexoffice")
    - file_name (str): Name of the Excel file to create

    Returns:
    None
    """
    folder_path = os.path.join(GENERAL_PATH, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    df.to_excel(file_path, index=False)

# ========================================================================================================================================
# GRAPH AND DISPLAY
def apply_custom_styles(cell_contents, available_color='#29AB87'):
    """
    Apply custom styles to each cell in a DataFrame based on its content.

    Parameters:
    - cell_contents (various): The content of the cell to which the style will be applied.
    - available_color (str, optional): The color to use for cells marked as 'Available'. Defaults to '#29AB87'.

    Returns:
    - str: A CSS string describing the style to apply to the cell.
    """
    if cell_contents == 'Disponible':  # 'Disponible' means 'Available'
        return f'background-color: {available_color}'
    elif cell_contents in ["Matin", "Après-midi"]:  # 'Morning' or 'Afternoon' slots
        return ''  # No specific style for these cells
    elif any(year in str(cell_contents) for year in ["2023", "2024", "2025"]):  # Check for specific years in the content
        return ''  # No style for these cases, could specify further if needed
    else:
        return f'background-color: #ff8C00'  # Orange background for other cells

def display_selected_data(df, start_date, days_count, period='Journée'):
    """
    Display data for a selected period and slot type, with custom styles.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data to display.
    - start_date (datetime.date): The start date of the period to display.
    - days_count (int): The number of days from the start date to include in the display.
    - period (str, optional): The type of slot to display ('Matin' (Morning), 'Après-midi' (Afternoon), 'Journée' (Day)). Defaults to 'Journée' (Day).

    Returns:
    None

    Notes:
    Displays an error if the start date is in the past or if no data is available for the selected period.
    """
    try:
        # Check if the start date is in the past
        if start_date < datetime.datetime.today().date():
            st.error("La date de début ne peut pas être dans le passé. Veuillez sélectionner une date valide.")
            return

        # Calculate the end date based on the number of days
        end_date = start_date + datetime.timedelta(days=days_count)

        # Filter data for the selected days
        mask = (df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] < pd.Timestamp(end_date))
        data_period = df.loc[mask]

        # Filter out weekends
        data_period = data_period[~data_period['Date'].dt.weekday.isin([5, 6])]

        # Filter for the specific time of day, if specified
        if period != 'Journée':  # 'Day' includes both 'Morning' and 'Afternoon'
            data_period = data_period[data_period['Créneau'] == period]

        # Format dates in the DataFrame for display
        data_period['Date'] = data_period['Date'].dt.strftime('%A %d %B %Y')

        if not data_period.empty:
            # Apply specific styles to cells based on their content
            styled_data = data_period.style.applymap(apply_custom_styles)
            # Hide the index and display the styled DataFrame
            st.table(styled_data)
        else:
            st.warning("Aucune donnée disponible pour la période sélectionnée.")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de l'affichage des données: {e}")


def visualize_data(df, today):
    """
    Allows the user to choose a data visualization period and displays the corresponding data.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data to visualize.
    - today (datetime.date): The current date, used as a starting point for date selections.

    Returns:
    None

    Notes:
    Offers the user the choice between visualizing data for a specific day or for the next 15 days.
    """
    option = st.radio(
        "Choisissez une période de visualisation des données",  # User chooses the data visualization period
        ("Dans les 15 jours", "1 jour spécifique")  # Options for 15 days or a specific day
    )
    st.write("---")  # Visual separator

    if option == "1 jour spécifique":
        sel_period, _ = st.columns([1, 4])  # Set up a column for user input
        with sel_period:
            selected_date = st.date_input("Sélectionnez une date", value=today)  # Date picker for a specific day
        if selected_date:
            display_selected_data(df, selected_date, 1)  # Display data for the chosen day
    elif option == "Dans les 15 jours":
        display_selected_data(df, today, 15)  # Display data for the next 15 days

# ========================================================================================================================================
# CALCULATIONS
def is_weekend(date):
    """
    Determines if a given date is a weekend.

    Parameters:
    - date (datetime.date): The date to check.

    Returns:
    - bool: True if the date is a Saturday or Sunday, False otherwise.
    """
    return date.weekday() >= 5  # 5 for Saturday, 6 for Sunday

# ========================================================================================================================================
# CREATION AND MODIFICATION     
def reserve_office(df, today, offices, excel):
    """
    Allows the user to reserve an office for a specific date or within the current month.
    The user can choose a date, a period (morning, afternoon, full day), and a specific office for the reservation.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the office booking data.
    - today (datetime.date): The current date, used as a reference for reservations.
    - offices ([str]): List of offices available for reservation.
    - excel (str): The name of the Excel file in the folder where booking data is stored.

    Returns:
    None

    Notes:
    After the user submits the reservation form, the function checks the availability of the selected office
    for the given period and updates the DataFrame and the Excel file on the folder accordingly.
    """
    option = st.radio(
        "Choisissez une période de visualisation des données",
            ("1 jour spécifique", "Dans le mois"))
            
    if option == "1 jour spécifique":
        with st.form(key='reservation_form1'):
            col_date, col_slot, col_office = st.columns([1, 1, 1])
            with col_date:
                selected_date = st.date_input("Sélectionnez une date", value=today)
            with col_slot:
                period = st.radio("Quel créneau souhaitez-vous ?", 
                              ("Matin", "Après-midi", "Journée"), index=2
                              )
            with col_office:
                office = st.radio("Quel bureau préférez vous ?", tuple(offices))

            display_selected_data(df, selected_date, 1, period)
                    
            # Input for the name under which the reservation will be made
            col_name, _ = st.columns([1,3])
            with col_name:
                name = st.text_input("Entrez votre nom pour la réservation")

            submitted = st.form_submit_button("Réserver")

            # Button to confirm reservation and trigger backup logic
            if submitted:
                if name:  # Check that the name is not empty
                    try:
                        # Create a mask for the rows corresponding to the selected date and period.
                        mask = (df['Date'] == pd.Timestamp(selected_date))
            
                        if period != 'Journée':
                            mask &= (df['Créneau'] == period)
                        
                        # Find lines that match our criteria
                        matching_rows = df.loc[mask]
            
                        if not matching_rows.empty:
                            # If the period is "Journée", we want to check availability for each segment of the day.
                            if period == 'Journée':
                                periods_to_check = ['Matin', 'Après-midi']
                            else:
                                periods_to_check = [period]  # # Otherwise, we only check the specific period selected.
            
                            for period_segment in periods_to_check:
                                specific_mask = (matching_rows['Créneau'] == period_segment)
                                # Check if the office is available for reservations
                                if 'Disponible' in matching_rows.loc[specific_mask, office].values:
                                    # Office available, so updated to indicate it is now reserved.
                                    df.loc[mask & specific_mask, office] = name
                                else:
                                    # If the desktop is not available (i.e. the value is not "Disponible"), we display an error.
                                    st.error(f"Le bureau {office} n'est pas disponible pour {period_segment} le {selected_date.strftime('%d/%m/%Y')}.")
                                    return  # We return here to avoid trying to save changes or other operations.
                            
                            # If we are here, this means that all the necessary reservations are available and have been updated.
                            # We'll now save the updated DataFrame.
                            save_file_to_local(df, LOCAL_FOLDER, excel)
                            st.success("Réservation effectuée avec succès.")
                            st.experimental_rerun()
                        else:
                            st.warning("Aucune case disponible ne correspond à vos critères de sélection.")
            
                    except Exception as e:
                        st.error(f"Une erreur s'est produite lors de la mise à jour de la réservation : {e}")
                else:
                    st.warning("Veuillez entrer votre nom pour effectuer une réservation.")
        
    if option == "Dans le mois":
                       
        # Define column names corresponding to offices
        office_columns = offices
        
        # Create a form to submit reservations
        with st.form(key='reservation_form2'):
            st.write("Veuillez sélectionner les créneaux de réservation")
            
            start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=30)  # or any other logic to define the period
        
            # You must ensure that the dates selected are valid (the end date must come after the start date).
            if start_date > end_date:
                st.error("La date de fin doit venir après la date de début.")
            else:
                # Filter reservation data for selected dates
                mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
                filtered_data = df.loc[mask]
        
                # If no data is available for the selected period, display a message.
                if filtered_data.empty:
                    st.write("Aucune donnée de réservation disponible pour la période sélectionnée.")
                else:
                    # Create a row for column headers
                    header_cols = st.columns(len(office_columns)+2)
                    header_cols[0].write("Date")
                    header_cols[1].write("Créneau")
                    for i, office in enumerate(office_columns, start=2):
                        header_cols[i].write(office)
                            
                    # Create a dictionary to store user selections
                    user_selections = {}
        
                    for index, row in filtered_data.iterrows():
                        current_date = row['Date']  # Make sure 'Date' is a datetime object
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
                                    # If the desktop is available, create a checkbox and save the status in the dictionary
                                    checkbox_checked = cols[i].checkbox('', key=f"{date_str}-{period}-{office}")
                                    user_selections[f"{date_str}-{period}"][office] = checkbox_checked
                                else:
                                    # If the desktop is not available, deactivate the checkbox
                                    cols[i].write(' -')
                                    user_selections[f"{date_str}-{period}"][office] = False  # Non disponible ou non sélectionné
                            
                            if period == "Après-midi":
                                st.write("---")

                    # Submit form button
                    col_name, _ = st.columns([1,3])
                    with col_name:
                        name = st.text_input("Entrez votre nom pour la réservation")
                    submitted = st.form_submit_button("Soumettre les réservations")
                    
                # After submitting the form, display the user's selections or process them as required                      
                if submitted:
                    if name:  # Check that the name is not empty
                        # Iterate over all user selections and update the DataFrame
                        for date_period, reservations in user_selections.items():
                            try:
                                # Check whether "Après-midi" is in the chain and adjust the division logic accordingly
                                if "Après-midi" in date_period:
                                    parts = date_period.split('-')
                                    if len(parts) > 2:  # This means that "Après-midi" was part of the chain
                                        # Rebuild 'selected_date_str' and 'period' taking into account the "Après-midi" anomaly
                                        selected_date_str = parts[0]  # The date remains the first part
                                        period = "Après-midi"  # Assign "Après-midi" value manually
                                    else:
                                        # If the length is not greater than 2, the division is normal.
                                        selected_date_str, period = parts
                                else:
                                    # For all other strings, normal division logic applies
                                    selected_date_str, period = date_period.split('-')
                        
                                # Convert formatted date string to datetime object
                                selected_date = datetime.datetime.strptime(selected_date_str, '%A %d %B %Y')
                             
                            except ValueError:
                                continue  # Goes to the next iteration, ignoring the rest of the code in the loop
                            
                            # Convert formatted date string to datetime object
                            try:
                                selected_date = datetime.datetime.strptime(selected_date_str, '%A %d %B %Y')
                            except ValueError:
                                st.error(f"Le format de la date est incorrect : {selected_date_str}")
                                return
                    
                            # Create a mask for the rows corresponding to the selected date and period.
                            mask = (df['Date'] == selected_date) & (df['Créneau'] == period)
                    
                            # Iterate over the reservations in the dictionary for the given date and period
                            for office, is_booked in reservations.items():
                                if is_booked:
                                    # If the user has checked the box, we update the DataFrame.
                                    # Check if the office is available for booking
                                    if 'Disponible' in df.loc[mask, office].values:
                                        # Office available, so updated to indicate it is now reserved.
                                        df.loc[mask, office] = name  # Enter the name of the person who made the reservation
                                    else:
                                        # If the desktop is not available (i.e. the value is not "Disponible"), we display an error.
                                        st.error(f"Le {office} n'est pas disponible pour {period} le {selected_date_str}.")
                                        return  # We return here to avoid trying to save changes or other operations.
                    
                        # If we are here, this means that all the necessary reservations are available and have been updated.
                        # We'll now save the updated DataFrame.
                        save_file_to_local(df, LOCAL_FOLDER, excel)
                        st.success("Réservation effectuée avec succès.")
                        st.rerun()
                    else:
                        st.warning("Veuillez entrer votre nom pour effectuer une réservation.")

def cancel_reservation(df, today, offices, excel):
    """
    Allows the user to cancel a previously made office reservation. The user can select
    a date, a period (morning, afternoon, full day), and a specific office whose reservation needs to be canceled.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the office booking data.
    - today (datetime.date): The current date, used as a reference for cancellations.
    - offices ([str]): List of offices available for cancellation.
    - excel (str): The name of the Excel file in the folder where booking data is stored.

    Returns:
    None

    Notes:
    The function displays booking data for the selected period and allows the user to cancel 
    one or more reservations. After confirmation, the DataFrame and the Excel file on folder are updated to reflect the cancellation.
    """
    col_date, col_slot, col_office = st.columns([1, 1, 1])
    with col_date:
        selected_date = st.date_input("Sélectionnez une date", value=today)
    with col_slot:
        period = st.radio("Quel créneau souhaitez-vous ?", 
                          ("Matin", "Après-midi", "Journée"), index=2)
    with col_office:
        office = st.radio("Quel bureau préférez-vous ?", tuple(offices))

    with st.form(key="cancel"):
        display_selected_data(df, selected_date, 1, period)
        
        cancel = st.form_submit_button("Annuler le créneau")
        
        if cancel:
            mask = (df['Date'] == pd.Timestamp(selected_date))
            
            if period != 'Journée':
                mask &= (df['Créneau'] == period)
            
            matching_rows = df.loc[mask]
            
            if not matching_rows.empty:
                periods_to_check = ['Matin', 'Après-midi'] if period == 'Journée' else [period]
                
                for period_segment in periods_to_check:
                    specific_mask = (matching_rows['Créneau'] == period_segment)
                    period_rows = df.loc[mask & specific_mask]
                    
                    for index, row in period_rows.iterrows():
                        if row[office] != 'Disponible':  # The office is currently reserved
                            df.at[index, office] = 'Disponible'  # Make the office available
                            st.success(f"Le bureau {office} est maintenant disponible pour {period_segment} le {selected_date.strftime('%d/%m/%Y')}.")
            
                save_file_to_local(df, LOCAL_FOLDER, excel)
                st.rerun()
            else:
                st.warning("Aucune réservation ne correspond à vos critères de sélection.")


#####################################################################
# ========================= MAIN FUNCTION ========================= #
#####################################################################

def main():
    """
    Main function running the Streamlit application for office reservations.
    It configures the page, manages user authentication, and enables viewing,
    booking, and cancellation of office reservations.

    Returns:
    None

    Notes:
    The application provides a user interface to choose a 'flex office', view availability,
    reserve or cancel offices. Users must authenticate with a password before accessing the features.
    """
    st.set_page_config(layout="wide", page_icon=":clock3:", page_title="Flex Offices")

    today = datetime.date.today()

    # Configuration for each flex office
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

    # Initialize st.session_state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # User authentication
    if not st.session_state.authenticated:
        _, col_password, _ = st.columns([2, 3, 2])
        with col_password:
            entered_password = st.text_input("Entrez le mot de passe", type="password").upper()

            if entered_password == PASSWORD:  # Assume "CORRECT_PASSWORD" is your predefined password
                st.session_state.authenticated = True
            else:
                st.error("Mot de passe incorrect. Veuillez réessayer.")

    # Display options once authenticated
    if st.session_state.authenticated:
        flex = st.sidebar.selectbox("Choisissez votre flex office", list(flex_config.keys()), index=0)

        # Apply the configuration based on the chosen office
        office_details = flex_config[flex]
        load_image(office_details["image"])
        df = load_file_from_local(LOCAL_FOLDER, office_details["excel"])
        load_image_sidebar(office_details["sidebar_image"])

        tab_selection = st.sidebar.selectbox("Que souhaitez-vous faire ?", ["Visualisation", "Réservation", "Annulation"])
        st.write("---")
        load_image_sidebar(office_details["plan"])

        if tab_selection == "Visualisation":
            visualize_data(df, today)
        elif tab_selection == "Réservation":
            reserve_office(df, today, office_details["offices"], office_details["excel"])
        elif tab_selection == "Annulation":
            cancel_reservation(df, today, office_details["offices"], office_details["excel"])


#####################################################################
# ========================== ALGO LAUNCH ========================== #
#####################################################################

if __name__ == "__main__":
    main()
