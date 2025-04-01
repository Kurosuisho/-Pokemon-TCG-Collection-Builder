# Pokémon TCG Collection Builder

The Pokémon TCG Collection Builder is a web application designed to help users manage their Pokémon Trading Card Game (TCG) collections and decks. It provides functionalities to organize cards, create decks, and track collection progress.​ Features.

## Features

Card Management: Add, view, and organize Pokémon TCG cards within your personal collection.​

Deck Building: Construct and manage decks using the cards from your collection.​

Ai Chatbot powered by Googles Gemini for deck building or collecting assistance


## Folder Structure

app.py: Main application script that initializes and runs the web server.​

app/: Directory containing the main frame of the project

data/: Directory containing data files related to the project.

scripts/: Directory containing script to set up the database schema.​

requirements.txt: List of Python dependencies required for the project.​


## Installation

Clone the Repository:

```bash
git clone https://github.com/Kurosuisho/Pokemon-TCG-Collection-Builder.git
```

Open a Terminal window and navigate to the Project Directory:

```bash
cd 'Folder/Where/You/Saved/The/Program/Pokémon TCG Collection Builder'
```

Install Dependencies:

```bash
pip install -r requirements.txt
```

Navigate to the Project Directory:

```bash
cd 'Folder/Where/You/Saved/The/Program/Pokémon TCG Collection Builder'
```
Set Up the Database:

        Ensure you have PostgreSQL installed and running.​

        Create a new PostgreSQL database.​

        Configure the database connection settings in the application as needed.​

        Initialize the database: python create_database.py

## Usage

Run the Application:

    python app.py

Access the application in your web browser at http://localhost:5000