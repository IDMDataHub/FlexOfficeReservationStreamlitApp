
# FlexOfficeReservationStreamlitApp

## Brief Description
**FlexOfficeReservationStreamlitApp** is a Streamlit application for reserving flex office spaces. It allows users to view, book, and cancel office spaces in various work environments, incorporating features like interaction with AWS S3 for storing reservation data.

### Features
- **Availability Viewing**: Enables viewing available offices over a selected period.
- **Office Booking**: User interface to book an office for specific time slots.
- **Booking Cancellation**: Functionality to cancel an existing reservation.
- **Integration with AWS S3**: Manages reservation data stored on AWS S3.
- **Access Security**: Password-protected access to the application.

### Installation
To install and run this project locally:

1. *Clone the repository*:
   ```bash
   git clone https://github.com/IDMDataHub/FlexOfficeReservationStreamlitApp.git
   ```
2. *Install Streamlit and other dependencies*:
   ```bash
   pip install streamlit pandas boto3 Pillow
   ```

### Usage
Launch the Streamlit application:
```bash
streamlit run app.py
```
The application will be accessible via your browser at the address provided by Streamlit.

### Streamlit Interface
- **Flex Office Selection**: Choose the flex office to view or book.
- **Viewing**: Displays the availability of office spaces.
- **Booking and Cancellation**: Forms for booking and cancelling office slots.

### Libraries Used
- `streamlit`: For creating the user interface and managing interactions.
- `pandas`: For DataFrame manipulation.
- `boto3`: For integration with AWS S3.
- `Pillow`: For image processing.

### Contribution
Contributions to this project are welcome. To suggest improvements or corrections, please open an issue or a pull request.

### License
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

### Author
*Maxime Jacoupy*
