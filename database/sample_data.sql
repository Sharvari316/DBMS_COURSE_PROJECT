-- ============================================================================
-- SAMPLE DATA: ResearchManagement
-- Realistic Academic Sample Data for Simulation and Testing
-- ============================================================================

USE ResearchManagement;

-- Clear existing data if re-populating (respecting FK constraints order)
DELETE FROM `Grant`;
DELETE FROM Publication;
DELETE FROM Project;
DELETE FROM Researcher;

-- ----------------------------------------------------------------------------
-- 1. Insert Researchers
-- ----------------------------------------------------------------------------
INSERT INTO Researcher (ResearcherID, Name, Email, Department) VALUES
(101, 'Dr. Alan Turing', 'a.turing@university.edu', 'Computer Science & AI'),
(102, 'Dr. Rosalind Franklin', 'r.franklin@university.edu', 'Biotechnology & Structural Biology'),
(103, 'Dr. Ada Lovelace', 'a.lovelace@university.edu', 'Computational Mathematics'),
(104, 'Dr. Richard Feynman', 'r.feynman@university.edu', 'Quantum Physics');

-- ----------------------------------------------------------------------------
-- 2. Insert Research Projects
-- ----------------------------------------------------------------------------
INSERT INTO Project (ProjectID, ProjectName, StartDate, EndDate, ResearcherID) VALUES
(201, 'Neural Interface Architecture for Autonomous Agents', '2024-01-15', '2026-12-31', 101),
(202, 'High-Throughput Genomic Sequence Modeling', '2023-06-01', '2025-05-31', 102),
(203, 'Quantum Optimization in Combinatorial Computing', '2024-03-01', '2026-08-31', 104),
(204, 'Symbolic Reasoning and Algorithmic Complexity', '2023-09-01', '2025-08-31', 103);

-- ----------------------------------------------------------------------------
-- 3. Insert Publications
-- ----------------------------------------------------------------------------
INSERT INTO Publication (PublicationID, Title, Journal, PublicationYear, ResearcherID, ProjectID) VALUES
(301, 'Deep Graph Neural Networks for Symbolic Reasoning', 'IEEE Transactions on Neural Networks', 2024, 101, 201),
(302, 'Structural Crystallography in Macromolecular Folding', 'Nature Biotechnology', 2023, 102, 202),
(303, 'Topological Quantum Benchmarks on Dense Hypergraphs', 'Physical Review Applied', 2024, 104, 203),
(304, 'Foundations of Modern Algorithmic Computation', 'ACM Computing Surveys', 2023, 103, 204),
(305, 'Scalable Deep Architecture for Latent Manifold Discovery', 'Journal of Machine Learning Research', 2024, 101, 201);

-- ----------------------------------------------------------------------------
-- 4. Insert Grants
-- ----------------------------------------------------------------------------
INSERT INTO `Grant` (GrantID, GrantName, Amount, FundingAgency, ProjectID) VALUES
(401, 'National Science Foundation Next-Gen Computing Grant', 250000.00, 'National Science Foundation', 201),
(402, 'Biomedical Discovery and Genomics Research Award', 185000.00, 'National Institutes of Health', 202),
(403, 'Advanced Quantum Information Science Initiative', 320000.00, 'Department of Energy', 203),
(404, 'Theoretical Computing and Mathematical Foundations Grant', 140000.00, 'European Research Council', 204),
(405, 'Artificial Intelligence Frontier Exploratory Fund', 110000.00, 'Defense Advanced Research Projects Agency', 201);
