"""
Database Management Module for Research Project Management System
Uses mysql.connector for parameterized SQL queries and connection management.
"""

import os
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
import mysql.connector
from mysql.connector import errorcode

# Load .env file automatically if present
def _load_env_file():
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

# Default configuration settings - can be overridden via environment variables or runtime settings
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "ResearchManagement"),
}



def get_db_config() -> Dict[str, Any]:
    """Return a copy of the current database configuration."""
    return DB_CONFIG.copy()


def update_db_config(
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
) -> None:
    """Update runtime database configuration."""
    if host is not None:
        DB_CONFIG["host"] = host
    if port is not None:
        DB_CONFIG["port"] = int(port)
    if user is not None:
        DB_CONFIG["user"] = user
    if password is not None:
        DB_CONFIG["password"] = password
    if database is not None:
        DB_CONFIG["database"] = database


def get_connection(use_database: bool = True):
    """
    Establish and return a MySQL connection.
    If use_database is False, connects without specifying the database
    (useful for creating or checking database existence).
    """
    config = DB_CONFIG.copy()
    if not use_database:
        config.pop("database", None)

    return mysql.connector.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config.get("database") if use_database else None,
        autocommit=False,
    )


def parse_db_error(err: Exception) -> str:
    """Translate raw database exceptions into user-friendly messages."""
    if isinstance(err, mysql.connector.Error):
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return (
                f"Authentication failed: Access denied for user '{DB_CONFIG['user']}'. "
                "Please verify your MySQL username and password."
            )
        elif err.errno == errorcode.CR_CONN_HOST_ERROR or err.errno == 2003:
            return (
                f"Connection failed: Could not connect to MySQL server at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
                "Ensure MySQL Server is running."
            )
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return (
                f"Database '{DB_CONFIG['database']}' does not exist. "
                "Please use the 'Initialize Database' option to create it."
            )
        elif err.errno == errorcode.ER_DUP_ENTRY:
            return f"Duplicate Key Error: A record with this primary key already exists ({err.msg})."
        elif err.errno == errorcode.ER_ROW_IS_REFERENCED_2:
            return (
                "Foreign Key Constraint: Cannot delete or update this record because "
                "other related records depend on it in a child table."
            )
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            return (
                "Foreign Key Constraint: The specified foreign key does not exist in the referenced parent table."
            )
        return f"MySQL Error ({err.errno}): {err.msg}"
    return f"Database error: {str(err)}"


def test_connection() -> Tuple[bool, str]:
    """Test the database connection and return status flag and message."""
    conn = None
    try:
        conn = get_connection(use_database=True)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE(), VERSION();")
        db_name, version = cursor.fetchone()
        cursor.close()
        return True, f"Connected to MySQL {version} (Database: {db_name})"
    except Exception as e:
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def initialize_database() -> Tuple[bool, str]:
    """
    Creates the ResearchManagement database and all 4 tables if they don't exist.
    Reads SQL definitions directly to ensure exact schema compliance.
    """
    conn = None
    try:
        # Step 1: Connect to server without database to create DB
        conn = get_connection(use_database=False)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`;")
        cursor.close()
        conn.close()

        # Step 2: Connect to the newly created database and build tables
        conn = get_connection(use_database=True)
        cursor = conn.cursor()

        table_queries = [
            """
            CREATE TABLE IF NOT EXISTS Researcher (
                ResearcherID INT PRIMARY KEY,
                Name VARCHAR(50) NOT NULL,
                Email VARCHAR(100),
                Department VARCHAR(50)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Project (
                ProjectID INT PRIMARY KEY,
                ProjectName VARCHAR(100) NOT NULL,
                StartDate DATE,
                EndDate DATE,
                ResearcherID INT,
                FOREIGN KEY (ResearcherID) REFERENCES Researcher(ResearcherID)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Publication (
                PublicationID INT PRIMARY KEY,
                Title VARCHAR(150) NOT NULL,
                Journal VARCHAR(100),
                PublicationYear INT,
                ResearcherID INT,
                ProjectID INT,
                FOREIGN KEY (ResearcherID) REFERENCES Researcher(ResearcherID)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS `Grant` (
                GrantID INT PRIMARY KEY,
                GrantName VARCHAR(100) NOT NULL,
                Amount DECIMAL(12,2),
                FundingAgency VARCHAR(100),
                ProjectID INT,
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        ]

        for query in table_queries:
            cursor.execute(query)

        conn.commit()
        cursor.close()
        return True, "Database 'ResearchManagement' and all tables initialized successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def seed_sample_data() -> Tuple[bool, str]:
    """
    Inserts initial academic sample data if not already present.
    """
    conn = None
    try:
        conn = get_connection(use_database=True)
        cursor = conn.cursor()

        # Researchers
        researchers = [
            (101, "Dr. Alan Turing", "a.turing@university.edu", "Computer Science & AI"),
            (102, "Dr. Rosalind Franklin", "r.franklin@university.edu", "Biotechnology & Structural Biology"),
            (103, "Dr. Ada Lovelace", "a.lovelace@university.edu", "Computational Mathematics"),
            (104, "Dr. Richard Feynman", "r.feynman@university.edu", "Quantum Physics"),
        ]
        insert_researcher_query = """
            INSERT INTO Researcher (ResearcherID, Name, Email, Department)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Name=VALUES(Name), Email=VALUES(Email), Department=VALUES(Department);
        """
        cursor.executemany(insert_researcher_query, researchers)

        # Projects
        projects = [
            (201, "Neural Interface Architecture for Autonomous Agents", "2024-01-15", "2026-12-31", 101),
            (202, "High-Throughput Genomic Sequence Modeling", "2023-06-01", "2025-05-31", 102),
            (203, "Quantum Optimization in Combinatorial Computing", "2024-03-01", "2026-08-31", 104),
            (204, "Symbolic Reasoning and Algorithmic Complexity", "2023-09-01", "2025-08-31", 103),
        ]
        insert_project_query = """
            INSERT INTO Project (ProjectID, ProjectName, StartDate, EndDate, ResearcherID)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE ProjectName=VALUES(ProjectName), StartDate=VALUES(StartDate),
                                    EndDate=VALUES(EndDate), ResearcherID=VALUES(ResearcherID);
        """
        cursor.executemany(insert_project_query, projects)

        # Publications
        publications = [
            (301, "Deep Graph Neural Networks for Symbolic Reasoning", "IEEE Transactions on Neural Networks", 2024, 101, 201),
            (302, "Structural Crystallography in Macromolecular Folding", "Nature Biotechnology", 2023, 102, 202),
            (303, "Topological Quantum Benchmarks on Dense Hypergraphs", "Physical Review Applied", 2024, 104, 203),
            (304, "Foundations of Modern Algorithmic Computation", "ACM Computing Surveys", 2023, 103, 204),
            (305, "Scalable Deep Architecture for Latent Manifold Discovery", "Journal of Machine Learning Research", 2024, 101, 201),
        ]
        insert_publication_query = """
            INSERT INTO Publication (PublicationID, Title, Journal, PublicationYear, ResearcherID, ProjectID)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Title=VALUES(Title), Journal=VALUES(Journal),
                                    PublicationYear=VALUES(PublicationYear),
                                    ResearcherID=VALUES(ResearcherID), ProjectID=VALUES(ProjectID);
        """
        cursor.executemany(insert_publication_query, publications)

        # Grants
        grants = [
            (401, "National Science Foundation Next-Gen Computing Grant", 250000.00, "National Science Foundation", 201),
            (402, "Biomedical Discovery and Genomics Research Award", 185000.00, "National Institutes of Health", 202),
            (403, "Advanced Quantum Information Science Initiative", 320000.00, "Department of Energy", 203),
            (404, "Theoretical Computing and Mathematical Foundations Grant", 140000.00, "European Research Council", 204),
            (405, "Artificial Intelligence Frontier Exploratory Fund", 110000.00, "Defense Advanced Research Projects Agency", 201),
        ]
        insert_grant_query = """
            INSERT INTO `Grant` (GrantID, GrantName, Amount, FundingAgency, ProjectID)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE GrantName=VALUES(GrantName), Amount=VALUES(Amount),
                                    FundingAgency=VALUES(FundingAgency), ProjectID=VALUES(ProjectID);
        """
        cursor.executemany(insert_grant_query, grants)

        conn.commit()
        cursor.close()
        return True, "Sample academic dataset successfully seeded."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================================
# RESEARCHER CRUD OPERATIONS
# ============================================================================

def get_all_researchers() -> List[Dict[str, Any]]:
    """Retrieve all researcher records."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT ResearcherID, Name, Email, Department FROM Researcher ORDER BY ResearcherID ASC;"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_researcher_by_id(researcher_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single researcher by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT ResearcherID, Name, Email, Department FROM Researcher WHERE ResearcherID = %s;"
        cursor.execute(query, (researcher_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def add_researcher(researcher_id: int, name: str, email: str, department: str) -> Tuple[bool, str]:
    """Add a new researcher to the database."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Researcher (ResearcherID, Name, Email, Department)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (researcher_id, name.strip(), email.strip(), department.strip()))
        conn.commit()
        cursor.close()
        return True, f"Researcher #{researcher_id} ('{name}') added successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_researcher(researcher_id: int, name: str, email: str, department: str) -> Tuple[bool, str]:
    """Update an existing researcher's details."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE Researcher
            SET Name = %s, Email = %s, Department = %s
            WHERE ResearcherID = %s;
        """
        cursor.execute(query, (name.strip(), email.strip(), department.strip(), researcher_id))
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Researcher #{researcher_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Researcher #{researcher_id} updated successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_researcher(researcher_id: int) -> Tuple[bool, str]:
    """Delete a researcher by ID, respecting foreign key integrity."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM Researcher WHERE ResearcherID = %s;"
        cursor.execute(query, (researcher_id,))
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Researcher #{researcher_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Researcher #{researcher_id} deleted successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================================
# PROJECT CRUD OPERATIONS
# ============================================================================

def get_all_projects() -> List[Dict[str, Any]]:
    """Retrieve all projects with lead researcher information."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                p.ProjectID,
                p.ProjectName,
                p.StartDate,
                p.EndDate,
                p.ResearcherID,
                r.Name AS LeadResearcher,
                r.Department AS ResearcherDepartment
            FROM Project p
            LEFT JOIN Researcher r ON p.ResearcherID = r.ResearcherID
            ORDER BY p.ProjectID ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single project by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                p.ProjectID,
                p.ProjectName,
                p.StartDate,
                p.EndDate,
                p.ResearcherID,
                r.Name AS LeadResearcher
            FROM Project p
            LEFT JOIN Researcher r ON p.ResearcherID = r.ResearcherID
            WHERE p.ProjectID = %s;
        """
        cursor.execute(query, (project_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def add_project(
    project_id: int, project_name: str, start_date: Any, end_date: Any, researcher_id: int
) -> Tuple[bool, str]:
    """Add a new project referencing an existing researcher."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Project (ProjectID, ProjectName, StartDate, EndDate, ResearcherID)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (project_id, project_name.strip(), start_date, end_date, researcher_id))
        conn.commit()
        cursor.close()
        return True, f"Project #{project_id} ('{project_name}') added successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_project(
    project_id: int, project_name: str, start_date: Any, end_date: Any, researcher_id: int
) -> Tuple[bool, str]:
    """Update project details."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE Project
            SET ProjectName = %s, StartDate = %s, EndDate = %s, ResearcherID = %s
            WHERE ProjectID = %s;
        """
        cursor.execute(query, (project_name.strip(), start_date, end_date, researcher_id, project_id))
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Project #{project_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Project #{project_id} updated successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_project(project_id: int) -> Tuple[bool, str]:
    """Delete a project by ID, respecting foreign key dependencies."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM Project WHERE ProjectID = %s;"
        cursor.execute(query, (project_id,))
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Project #{project_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Project #{project_id} deleted successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================================
# PUBLICATION CRUD OPERATIONS
# ============================================================================

def get_all_publications() -> List[Dict[str, Any]]:
    """Retrieve all publications with author and project names."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                pub.PublicationID,
                pub.Title,
                pub.Journal,
                pub.PublicationYear,
                pub.ResearcherID,
                r.Name AS AuthorName,
                pub.ProjectID,
                p.ProjectName
            FROM Publication pub
            LEFT JOIN Researcher r ON pub.ResearcherID = r.ResearcherID
            LEFT JOIN Project p ON pub.ProjectID = p.ProjectID
            ORDER BY pub.PublicationID ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_publication_by_id(publication_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single publication by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                pub.PublicationID,
                pub.Title,
                pub.Journal,
                pub.PublicationYear,
                pub.ResearcherID,
                r.Name AS AuthorName,
                pub.ProjectID,
                p.ProjectName
            FROM Publication pub
            LEFT JOIN Researcher r ON pub.ResearcherID = r.ResearcherID
            LEFT JOIN Project p ON pub.ProjectID = p.ProjectID
            WHERE pub.PublicationID = %s;
        """
        cursor.execute(query, (publication_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def add_publication(
    publication_id: int,
    title: str,
    journal: str,
    publication_year: int,
    researcher_id: int,
    project_id: int,
) -> Tuple[bool, str]:
    """Add a new publication linking a researcher and project."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Publication (PublicationID, Title, Journal, PublicationYear, ResearcherID, ProjectID)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            query,
            (
                publication_id,
                title.strip(),
                journal.strip(),
                publication_year,
                researcher_id,
                project_id,
            ),
        )
        conn.commit()
        cursor.close()
        return True, f"Publication #{publication_id} ('{title}') added successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_publication(
    publication_id: int,
    title: str,
    journal: str,
    publication_year: int,
    researcher_id: int,
    project_id: int,
) -> Tuple[bool, str]:
    """Update publication details."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE Publication
            SET Title = %s, Journal = %s, PublicationYear = %s, ResearcherID = %s, ProjectID = %s
            WHERE PublicationID = %s;
        """
        cursor.execute(
            query,
            (
                title.strip(),
                journal.strip(),
                publication_year,
                researcher_id,
                project_id,
                publication_id,
            ),
        )
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Publication #{publication_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Publication #{publication_id} updated successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_publication(publication_id: int) -> Tuple[bool, str]:
    """Delete a publication by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM Publication WHERE PublicationID = %s;"
        cursor.execute(query, (publication_id,))
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Publication #{publication_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Publication #{publication_id} deleted successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================================
# GRANT CRUD OPERATIONS
# ============================================================================

def get_all_grants() -> List[Dict[str, Any]]:
    """Retrieve all grants with associated project name using distinct column aliases."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                g.GrantID AS `Grant ID`,
                g.GrantName AS `Grant Name`,
                g.Amount AS `Amount`,
                g.FundingAgency AS `Funding Agency`,
                g.ProjectID AS `Project ID`,
                p.ProjectName AS `Funded Project`
            FROM `Grant` g
            LEFT JOIN Project p ON g.ProjectID = p.ProjectID
            ORDER BY g.GrantID ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_grant_by_id(grant_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single grant by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                g.GrantID,
                g.GrantName,
                g.Amount,
                g.FundingAgency,
                g.ProjectID,
                p.ProjectName
            FROM `Grant` g
            LEFT JOIN Project p ON g.ProjectID = p.ProjectID
            WHERE g.GrantID = %s;
        """
        cursor.execute(query, (grant_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def add_grant(
    grant_id: int, grant_name: str, amount: float, funding_agency: str, project_id: int
) -> Tuple[bool, str]:
    """Add a new grant record."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO `Grant` (GrantID, GrantName, Amount, FundingAgency, ProjectID)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(
            query,
            (
                grant_id,
                grant_name.strip(),
                Decimal(str(amount)),
                funding_agency.strip(),
                project_id,
            ),
        )
        conn.commit()
        cursor.close()
        return True, f"Grant #{grant_id} ('{grant_name}') added successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_grant(
    grant_id: int, grant_name: str, amount: float, funding_agency: str, project_id: int
) -> Tuple[bool, str]:
    """Update grant details."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE `Grant`
            SET GrantName = %s, Amount = %s, FundingAgency = %s, ProjectID = %s
            WHERE GrantID = %s;
        """
        cursor.execute(
            query,
            (
                grant_name.strip(),
                Decimal(str(amount)),
                funding_agency.strip(),
                project_id,
                grant_id,
            ),
        )
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Grant #{grant_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Grant #{grant_id} updated successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_grant(grant_id: int) -> Tuple[bool, str]:
    """Delete a grant record by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM `Grant` WHERE GrantID = %s;"
        cursor.execute(query, (grant_id,))
        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Grant #{grant_id} not found."
        conn.commit()
        cursor.close()
        return True, f"Grant #{grant_id} deleted successfully."
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return False, parse_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================================
# DASHBOARD METRICS AND SUMMARIES
# ============================================================================

def get_dashboard_metrics() -> Dict[str, Any]:
    """Fetch count statistics and total funding for the dashboard."""
    conn = None
    metrics = {
        "total_researchers": 0,
        "total_projects": 0,
        "total_publications": 0,
        "total_grants": 0,
        "total_funding": Decimal("0.00"),
    }
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Researcher;")
        metrics["total_researchers"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Project;")
        metrics["total_projects"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Publication;")
        metrics["total_publications"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(Amount), 0) FROM `Grant`;")
        g_count, g_sum = cursor.fetchone()
        metrics["total_grants"] = g_count
        metrics["total_funding"] = Decimal(str(g_sum))

        cursor.close()
        return metrics
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_recent_projects(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent projects ordered by ProjectID descending."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                p.ProjectID,
                p.ProjectName,
                p.StartDate,
                p.EndDate,
                r.Name AS LeadResearcher
            FROM Project p
            LEFT JOIN Researcher r ON p.ResearcherID = r.ResearcherID
            ORDER BY p.ProjectID DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_recent_publications(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent publications ordered by PublicationID descending."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                pub.PublicationID,
                pub.Title,
                pub.Journal,
                pub.PublicationYear,
                r.Name AS AuthorName,
                p.ProjectName
            FROM Publication pub
            LEFT JOIN Researcher r ON pub.ResearcherID = r.ResearcherID
            LEFT JOIN Project p ON pub.ProjectID = p.ProjectID
            ORDER BY pub.PublicationID DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_grant_summary() -> List[Dict[str, Any]]:
    """Fetch grant summary aggregated by funding agency."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                FundingAgency,
                COUNT(GrantID) AS GrantCount,
                SUM(Amount) AS TotalFunding,
                AVG(Amount) AS AverageGrantAmount
            FROM `Grant`
            GROUP BY FundingAgency
            ORDER BY TotalFunding DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(parse_db_error(e))
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================================
# SQL DEMONSTRATION QUERIES
# ============================================================================

DEMO_QUERIES = [
    {
        "category": "SELECT",
        "title": "Select All Researchers in Department Order",
        "description": "Demonstrates basic projection, selection, and sorting using SELECT and ORDER BY.",
        "sql": """
SELECT ResearcherID, Name, Email, Department
FROM Researcher
ORDER BY Department ASC, Name ASC;
        """.strip(),
    },
    {
        "category": "INNER JOIN",
        "title": "Projects With Lead Researcher Information",
        "description": "Demonstrates relational navigation linking Project to Researcher via Foreign Key ResearcherID.",
        "sql": """
SELECT 
    p.ProjectID,
    p.ProjectName,
    p.StartDate,
    p.EndDate,
    r.Name AS LeadResearcher,
    r.Department
FROM Project p
INNER JOIN Researcher r ON p.ResearcherID = r.ResearcherID
ORDER BY p.ProjectID ASC;
        """.strip(),
    },
    {
        "category": "MULTI-TABLE JOIN",
        "title": "Publications with Author and Associated Research Project",
        "description": "Demonstrates joining three normalized tables (Publication, Researcher, Project) in a single query.",
        "sql": """
SELECT 
    pub.PublicationID,
    pub.Title,
    pub.Journal,
    pub.PublicationYear,
    r.Name AS AuthorName,
    p.ProjectName
FROM Publication pub
INNER JOIN Researcher r ON pub.ResearcherID = r.ResearcherID
INNER JOIN Project p ON pub.ProjectID = p.ProjectID
ORDER BY pub.PublicationYear DESC, pub.PublicationID ASC;
        """.strip(),
    },
    {
        "category": "SUM & AGGREGATE",
        "title": "Total Grant Funding Allocated Per Project",
        "description": "Demonstrates aggregate SUM with a LEFT JOIN to calculate cumulative funding awarded to each project.",
        "sql": """
SELECT 
    p.ProjectID,
    p.ProjectName,
    COUNT(g.GrantID) AS NumberOfGrants,
    COALESCE(SUM(g.Amount), 0.00) AS TotalProjectFunding
FROM Project p
LEFT JOIN `Grant` g ON p.ProjectID = g.ProjectID
GROUP BY p.ProjectID, p.ProjectName
ORDER BY TotalProjectFunding DESC;
        """.strip(),
    },
    {
        "category": "GROUP BY",
        "title": "Number of Publications Authored Per Researcher",
        "description": "Demonstrates GROUP BY with COUNT to aggregate research productivity per faculty member.",
        "sql": """
SELECT 
    r.ResearcherID,
    r.Name AS ResearcherName,
    r.Department,
    COUNT(pub.PublicationID) AS TotalPublications
FROM Researcher r
LEFT JOIN Publication pub ON r.ResearcherID = pub.ResearcherID
GROUP BY r.ResearcherID, r.Name, r.Department
ORDER BY TotalPublications DESC, r.Name ASC;
        """.strip(),
    },
    {
        "category": "GROUP BY & HAVING",
        "title": "Funding Agencies Providing Cumulative Grants Exceeding $150,000",
        "description": "Demonstrates filtering grouped aggregate records using the HAVING clause.",
        "sql": """
SELECT 
    FundingAgency,
    COUNT(GrantID) AS TotalGrants,
    SUM(Amount) AS TotalFundingAwarded
FROM `Grant`
GROUP BY FundingAgency
HAVING SUM(Amount) >= 150000.00
ORDER BY TotalFundingAwarded DESC;
        """.strip(),
    },
]


def execute_custom_query(sql_query: str) -> Tuple[bool, Any, List[str]]:
    """
    Executes a read-only query and returns (success, rows_list, column_headers).
    Protects against empty queries.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        cursor.close()
        return True, rows, columns
    except Exception as e:
        return False, parse_db_error(e), []
    finally:
        if conn and conn.is_connected():
            conn.close()
