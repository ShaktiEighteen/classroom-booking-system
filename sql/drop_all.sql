-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: drop_all.sql
-- Description: Cleanly drops all triggers, procedures, views, and tables
--              in reverse order of dependencies.
-- ============================================================================

-- Drop Views
DROP VIEW IF EXISTS booking_history_vw;
DROP VIEW IF EXISTS department_timetable_vw;
DROP VIEW IF EXISTS faculty_timetable_vw;
DROP VIEW IF EXISTS room_utilization_vw;

-- Drop Triggers
DROP TRIGGER IF EXISTS trg_prevent_booking_conflicts;

-- Drop Procedures
DROP PROCEDURE IF EXISTS book_periodic;
DROP PROCEDURE IF EXISTS book_oneoff;
DROP PROCEDURE IF EXISTS cancel_occurrence;
DROP PROCEDURE IF EXISTS cancel_series;
DROP PROCEDURE IF EXISTS find_free_rooms;
DROP PROCEDURE IF EXISTS cursor_utilization_report;

-- Drop Tables (with CASCADE CONSTRAINTS)
BEGIN
    FOR t IN (
        SELECT table_name FROM user_tables 
        WHERE table_name IN (
            'BOOKING_OCCURRENCE', 'BOOKING', 'ROOM_FACILITY', 
            'FACILITY', 'ROOM', 'COURSE', 'FACULTY', 
            'DEPARTMENT', 'TIME_SLOT', 'SEMESTER'
        )
    ) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
    END LOOP;
END;
/
