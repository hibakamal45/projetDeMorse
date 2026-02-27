# EyeSpeak – Application Web d’Assistance à la Communication

EyeSpeak est une solution d'accessibilité permettant aux personnes atteintes de troubles de la parole ou de paralysie de communiquer en utilisant le clignement des yeux et le code Morse.

## Fonctionnalités

- **Détection en temps réel** : Utilise MediaPipe et OpenCV pour détecter les clignements.
- **Traduction Morse** :
  - Clignement court (< 0.4s) = Point (.)
  - Clignement long (> 0.4s) = Trait (-)
- **Synthèse Vocale (TTS)** : Convertit le texte traduit en voix.
- **Module d'Apprentissage** : Permet aux utilisateurs de s'entraîner sur des lettres spécifiques.
- **Personnalisation** : Ajustez la sensibilité et les durées via la barre latérale.

## Installation

1. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

2. Lancez l'application :
   ```bash
   streamlit run app.py
   ```

## Utilisation

1. Autorisez l'accès à votre webcam.
2. Ajustez le curseur "Sensibilité" si nécessaire (observez la valeur EAR dans le flux vidéo).
3. Clignez des yeux pour composer votre message.
4. Attendez la pause configurée pour que le caractère soit validé.
5. Utilisez le bouton "Lire le texte" pour entendre le message.
