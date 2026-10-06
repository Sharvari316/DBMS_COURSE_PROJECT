# Research Project, Publication and Grant Management System

A Database Management System developed using MySQL and Streamlit to manage researchers, projects, publications, and grants efficiently.

## Technologies Used

- Python
- Streamlit
- MySQL
- Pandas
- mysql-connector-python

## Features

- Researcher management
- Project management
- Publication management
- Grant and funding management
- CRUD operations
- Foreign key relationships
- SQL JOIN and aggregation queries
- Streamlit dashboard

## Database Structure

The system contains four main tables:

- Researcher - stores researcher details
- Project - stores research project details
- Publication - stores publication details
- Grant - stores grant and funding information

## Project Structure

DBMS_course_project/
    database/
        schema.sql
        sample_data.sql
    app.py
    database.py
    requirements.txt
    .env.example
    .gitignore
    README.md

## Setup

### 1. Clone the Repository

git clone https://github.com/Sharvari316/DBMS_COURSE_PROJECT.git

cd DBMS_COURSE_PROJECT

### 2. Set Up MySQL

Run the following SQL files from the database folder:

- schema.sql
- sample_data.sql

This creates the ResearchManagement database and sample data.

### 3. Configure Database Connection

Create a .env file using .env.example and enter your MySQL credentials.

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ResearchManagement

Do not upload .env to GitHub.

### 4. Install Dependencies

pip install -r requirements.txt

### 5. Run the Application

python -m streamlit run app.py

The Streamlit dashboard will open in your browser.

## Author

Sharvari
