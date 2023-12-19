# **FlexOfficeReservationStreamlitApp**

## *Description Brève*
**FlexOfficeReservationStreamlitApp** est une application Streamlit pour la réservation de bureaux en mode flex office. Elle permet aux utilisateurs de visualiser, réserver et annuler des bureaux dans différents environnements de travail, en intégrant des fonctionnalités comme l'interaction avec AWS S3 pour le stockage des données de réservation.

### Fonctionnalités
- **Visualisation des Disponibilités**: Permet de voir les bureaux disponibles sur une période donnée.
- **Réservation de Bureaux**: Interface utilisateur pour réserver un bureau pour des créneaux spécifiques.
- **Annulation de Réservation**: Fonctionnalité pour annuler une réservation existante.
- **Intégration avec AWS S3**: Gestion des données de réservation stockées sur AWS S3.
- **Sécurité d'Accès**: Accès à l'application protégé par mot de passe.

### Installation
Pour installer et exécuter ce projet localement :

1. *Clonez le dépôt* :
   ```bash
   git clone https://github.com/IDMDataHub/FlexOfficeReservationStreamlitApp.git
   ```
2. *Installez Streamlit et les autres dépendances* :
   ```bash
   pip install streamlit pandas boto3 Pillow
   ```

### Utilisation
Lancez l'application Streamlit :
```bash
streamlit run app.py
```
L'application sera accessible via votre navigateur à l'adresse indiquée par Streamlit.

### Interface Streamlit
- **Sélection du Flex Office** : Choix du bureau flexible à visualiser ou réserver.
- **Visualisation** : Affichage des disponibilités des bureaux.
- **Réservation et Annulation** : Formulaires pour la réservation et l'annulation des créneaux de bureau.

### Bibliothèques Utilisées
- `streamlit` : Pour créer l'interface utilisateur et gérer les interactions.
- `pandas` : Pour la manipulation de DataFrame.
- `boto3` : Pour l'intégration avec AWS S3.
- `Pillow` : Pour le traitement des images.

### Contribution
Les contributions à ce projet sont les bienvenues. Pour proposer des améliorations ou des corrections, veuillez ouvrir une issue ou une pull request.

### Licence
Ce projet est sous licence [MIT](https://choosealicense.com/licenses/mit/).

### Auteur
*Maxime Jacoupy*
