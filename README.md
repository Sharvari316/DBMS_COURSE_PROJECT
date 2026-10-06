# Research Project Management System

**Academic DBMS Course Project:**  
*Design and Implementation of a Database Management System for Research Project, Publication and Grant Management*

---

## 1. Project Overview

The **Research Project Management System** is a relational database management system designed to streamline and track academic research activities within university departments or research institutions. 

It provides an enterprise-style desktop simulation interface to manage:
1. **Researchers**: Faculty members and investigators leading or contributing to research.
2. **Projects**: Institutional and externally funded research initiatives.
3. **Publications**: Academic journal papers and conference proceedings linked to investigators and projects.
4. **Grants**: Monetary funding awards and sponsoring agencies financing projects.

The system is implemented strictly using **Python**, **Streamlit**, **MySQL 8.0**, and **mysql-connector-python**, adhering to normalized relational database design standards (3NF).

---

## 2. Relational Database Design

- **Database Name**: `ResearchManagement`
- **Storage Engine**: `InnoDB` (ACID compliant)
- **Character Set**: `utf8mb4`

### Relational Schema & Tables

#### 1. `Researcher` Table
Stores basic profile information of academic researchers and faculty members.
- `ResearcherID` (INT) — **PRIMARY KEY**
- `Name` (VARCHAR(50)) — **NOT NULL**
- `Email` (VARCHAR(100))
- `Department` (VARCHAR(50))

#### 2. `Project` Table
Stores details of active or completed research initiatives.
- `ProjectID` (INT) — **PRIMARY KEY**
- `ProjectName` (VARCHAR(100)) — **NOT NULL**
- `StartDate` (DATE)
- `EndDate` (DATE)
- `ResearcherID` (INT) — **FOREIGN KEY** references `Researcher(ResearcherID)`
  - `ON UPDATE CASCADE`
  - `ON DELETE RESTRICT`

#### 3. `Publication` Table
Stores research output, published papers, and proceedings.
- `PublicationID` (INT) — **PRIMARY KEY**
- `Title` (VARCHAR(150)) — **NOT NULL**
- `Journal` (VARCHAR(100))
- `PublicationYear` (INT)
- `ResearcherID` (INT) — **FOREIGN KEY** references `Researcher(ResearcherID)`
- `ProjectID` (INT) — **FOREIGN KEY** references `Project(ProjectID)`
  - `ON UPDATE CASCADE`
  - `ON DELETE RESTRICT`

#### 4. `Grant` Table *(Enclosed with backticks in MySQL as `Grant` is a reserved keyword)*
Tracks research grant financing and sponsoring agencies.
- `GrantID` (INT) — **PRIMARY KEY**
- `GrantName` (VARCHAR(100)) — **NOT NULL**
- `Amount` (DECIMAL(12,2))
- `FundingAgency` (VARCHAR(100))
- `ProjectID` (INT) — **FOREIGN KEY** references `Project(ProjectID)`
  - `ON UPDATE CASCADE`
  - `ON DELETE RESTRICT`

### Referential Integrity Constraints
- **1 : N (Researcher to Projects)**: A researcher can lead multiple projects; each project has one lead investigator.
- **1 : N (Researcher to Publications)**: A researcher can author multiple publications.
- **1 : N (Project to Publications)**: A research project can yield multiple published works.
- **1 : N (Project to Grants)**: A research project can receive multiple grants from diverse funding bodies.
- Deletion of parent rows is restricted (`ON DELETE RESTRICT`) whenever dependent child records exist, preventing orphan records and preserving database integrity.

---

## 3. Project Structure

```text
DBMS_course_project/
│
├── database/
│   ├── schema.sql          # DDL script to create database and tables
│   └── sample_data.sql     # DML script with realistic academic sample data
│
├── app.py                  # Main Streamlit application and simulation UI
├── database.py             # Centralized MySQL connection & parameterized queries
├── requirements.txt        # Python package dependencies
├── .gitignore              # Git ignore rules for virtual environments & configs
└── README.md               # Complete project documentation and guide
```

---

## 4. Prerequisites

Before running the application, ensure the following are installed:
- **Python 3.10+** (Tested on Python 3.10 - 3.14)
- **MySQL Server 8.0+** running locally (or on a network server)
- **Git** (optional, for version control)

---

## 5. Installation and Setup

### Step 1: Clone or Navigate to the Project Directory
Open PowerShell or your terminal:
```bash
cd C:\DBMS_course_project
```

### Step 2: (Optional) Create and Activate a Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on macOS / Linux
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the packages specified in `requirements.txt`:
```bash
pip install -r requirements.txt
```

This installs:
- `streamlit`: High-performance Python web application framework
- `mysql-connector-python`: Official Oracle MySQL driver for Python
- `pandas`: Tabular data processing and presentation

---

## 6. Setting Up the MySQL Database

You can set up the database using **either** Method A (Command Line / Workbench) **or** Method B (Directly from the Streamlit UI).

### Method A: Using MySQL Command Line or MySQL Workbench
Open your terminal and run:

```bash
# Log in to MySQL client
mysql -u root -p

# Within MySQL prompt or command line:
mysql -u root -p < database/schema.sql
mysql -u root -p < database/sample_data.sql
```

Alternatively, open **MySQL Workbench**, open `database/schema.sql`, execute it (⚡), then open `database/sample_data.sql` and execute it.

### Method B: One-Click Setup Inside the Streamlit Application
1. Start the Streamlit application (see Section 7).
2. In the left sidebar under **Database Connection Settings**, enter your MySQL `Host`, `Port`, `User`, and `Password`.
3. Click **Apply & Reconnect**.
4. Click **Init Schema** to automatically run the DDL schema creation.
5. Click **Seed Data** to load realistic academic sample data.

---

## 7. Running the Application

Launch the Streamlit web application:

```bash
python -m streamlit run app.py
```

Streamlit will launch local server at:
```text
Local URL: http://localhost:8501
Network URL: http://<your-ip>:8501
```

Open `http://localhost:8501` in any modern web browser.

---

## 8. Application Features

1. **Dashboard**:
   - High-level metric cards for Researchers, Projects, Publications, Grants, and Cumulative Funding.
   - Recent Projects and Publications tables.
   - Aggregated Grant Summary broken down by funding agency.

2. **Researchers Management**:
   - Tabular view with instant keyword search.
   - Add new researchers with validation.
   - Update researcher details.
   - Delete researcher (with relational constraint protection).

3. **Projects Management**:
   - Tabular overview displaying project details along with lead researcher names.
   - Add projects with date validation and dynamic dropdown of active researchers.
   - Edit existing project schedules and assignments.
   - Safe deletion handling.

4. **Publications Management**:
   - Registry of academic literature linking publications to authors and funded projects.
   - Dropdown-driven relational forms for adding and updating entries.

5. **Grants Management**:
   - View, add, update, and remove grant funding records.
   - Currency formatting and project selection dropdowns.

6. **SQL / Database Information**:
   - Complete architectural overview and 3NF explanation.
   - Relational schema tables and constraint specifications.
   - **Live Query Demonstrations**: Run predefined SQL queries:
     - `SELECT` with `ORDER BY`
     - `INNER JOIN` linking Projects with Researchers
     - `MULTI-TABLE JOIN` joining Publications, Researchers, and Projects
     - Aggregate `SUM` calculating total funding per project
     - `GROUP BY` and `COUNT` aggregating publications per researcher
     - `GROUP BY` and `HAVING` filtering funding agencies with awards $\ge \$150,000$
   - **Interactive Read-Only Console**: Run custom `SELECT` queries for presentation and evaluation.

---

## 9. How to Push the Project to GitHub

Follow these steps to push this project to your GitHub repository:

### Step 1: Initialize Git Repository
In the project root directory (`C:\DBMS_course_project`):
```bash
git init
```

### Step 2: Configure Git User (If not configured globally)
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Stage and Commit the Files
```bash
git add .
git commit -m "Initial commit: Research Project Management System with Streamlit and MySQL"
```

### Step 4: Create a New Repository on GitHub
1. Go to [GitHub](https://github.com) and sign in.
2. Click **New Repository** (`+` icon at the top right).
3. Name your repository (e.g., `research-project-management-system` or `DBMS_course_project`).
4. Keep it **Public** (or Private) and **do not** check "Initialize with README" (since we already have one).
5. Click **Create repository**.

### Step 5: Link and Push to GitHub
Copy the repository URL from GitHub and run:
```bash
# Rename branch to main
git branch -M main

# Link your local repository to GitHub (replace with your actual GitHub URL)
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# Push the code
git push -u origin main
```

---

## 10. Database Error Handling and Security

- **Parameterized Queries**: All SQL statements use `%s` parameter substitution via `mysql.connector`, eliminating SQL Injection vulnerabilities.
- **Resource Management**: Connections and cursors are properly committed, closed, and cleaned up in `try...finally` blocks to prevent connection leaks.
- **Relational Integrity Protection**: Duplicate primary keys (Error 1062) and foreign key violations (Errors 1451 & 1452) are caught and displayed as clear, constructive error messages rather than causing application crashes.
