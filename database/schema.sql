-- ============================================================================
-- DATABASE SCHEMA: ResearchManagement
-- Academic Course Project: Research Project, Publication and Grant Management System
-- ============================================================================

-- Create database if it does not already exist
CREATE DATABASE IF NOT EXISTS ResearchManagement;
USE ResearchManagement;

-- ----------------------------------------------------------------------------
-- Table 1: Researcher
-- Stores information regarding faculty and academic researchers.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Researcher (
    ResearcherID INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100),
    Department VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- Table 2: Project
-- Stores funded or institutional research projects.
-- Foreign Key: ResearcherID references Researcher(ResearcherID)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- Table 3: Publication
-- Stores academic publications, journal papers, and research outcomes.
-- Foreign Keys: ResearcherID references Researcher(ResearcherID),
--               ProjectID references Project(ProjectID)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- Table 4: `Grant`
-- Stores financial funding, research grants, and sponsoring organizations.
-- Note: 'Grant' is an SQL reserved keyword, enclosed with backticks in MySQL.
-- Foreign Key: ProjectID references Project(ProjectID)
-- ----------------------------------------------------------------------------
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
