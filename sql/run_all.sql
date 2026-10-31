-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: run_all.sql
-- Description: Master execution script for SQL*Plus and Oracle SQL Developer.
-- ============================================================================

SET ECHO ON
SET SERVEROUTPUT ON
SET FEEDBACK ON
WHENEVER SQLERROR CONTINUE

PROMPT ===================================================
PROMPT 1. DROPPING EXISTING OBJECTS...
PROMPT ===================================================
@@drop_all.sql

PROMPT ===================================================
PROMPT 2. CREATING TABLES AND CORE CONSTRAINTS...
PROMPT ===================================================
@@create_tables.sql

PROMPT ===================================================
PROMPT 3. CREATING INDEXES AND CONFLICT TRIGGERS...
PROMPT ===================================================
@@constraints_triggers.sql

PROMPT ===================================================
PROMPT 4. COMPILING STORED PROCEDURES AND FUNCTIONS...
PROMPT ===================================================
@@procedures.sql

PROMPT ===================================================
PROMPT 5. COMPILING ANALYTICAL AND OPERATIONAL VIEWS...
PROMPT ===================================================
@@views.sql

PROMPT ===================================================
PROMPT 6. LOADING SAMPLE DATASET...
PROMPT ===================================================
@@sample_data.sql

PROMPT ===================================================
PROMPT 7. EXECUTING SAMPLE DEMONSTRATION QUERIES...
PROMPT ===================================================
@@queries.sql

PROMPT ===================================================
PROMPT MASTER SCRIPT COMPLETED SUCCESSFULLY!
PROMPT ===================================================
