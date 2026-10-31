-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: views.sql
-- Description: Analytical and Operational Views with Aggregates, GROUP BY,
--              HAVING, Outer Joins and Window Functions.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. room_utilization_vw
-- Aggregated metrics per room: active hours, cancellation counts, unique dates,
-- and capacity utilization rates with GROUP BY and aggregate functions.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW room_utilization_vw AS
SELECT 
    r.room_id,
    r.room_number,
    r.building,
    r.floor,
    r.room_type,
    r.capacity,
    COUNT(CASE WHEN bo.status = 'ACTIVE' THEN 1 END) AS active_bookings_count,
    COUNT(CASE WHEN bo.status = 'CANCELLED' THEN 1 END) AS cancelled_bookings_count,
    COUNT(bo.occurrence_id) AS total_occurrences_count,
    COUNT(DISTINCT CASE WHEN bo.status = 'ACTIVE' THEN bo.occurrence_date END) AS active_days_utilized,
    COUNT(DISTINCT CASE WHEN bo.status = 'ACTIVE' THEN bo.slot_id END) AS distinct_slots_used,
    ROUND(
        NVL(COUNT(CASE WHEN bo.status = 'ACTIVE' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(bo.occurrence_id), 0), 0), 2
    ) AS active_success_rate_pct
FROM ROOM r
LEFT JOIN BOOKING_OCCURRENCE bo ON r.room_id = bo.room_id
GROUP BY r.room_id, r.room_number, r.building, r.floor, r.room_type, r.capacity;

-- ----------------------------------------------------------------------------
-- 2. faculty_timetable_vw
-- Chronological schedule for faculty members across all active occurrences.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW faculty_timetable_vw AS
SELECT 
    f.faculty_id,
    f.faculty_code,
    f.first_name || ' ' || f.last_name AS faculty_name,
    f.email,
    f.designation,
    d.dept_code,
    d.dept_name,
    bo.occurrence_id,
    bo.booking_id,
    bo.occurrence_date,
    TRIM(TO_CHAR(bo.occurrence_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH')) AS day_of_week,
    ts.slot_id,
    ts.slot_name,
    ts.start_time,
    ts.end_time,
    ts.slot_order,
    r.room_id,
    r.room_number,
    r.building,
    r.room_type,
    c.course_id,
    NVL(c.course_code, 'N/A') AS course_code,
    NVL(c.course_title, b.title_purpose) AS session_title,
    b.booking_type,
    bo.status
FROM BOOKING_OCCURRENCE bo
JOIN BOOKING b ON bo.booking_id = b.booking_id
JOIN FACULTY f ON bo.faculty_id = f.faculty_id
JOIN DEPARTMENT d ON f.dept_id = d.dept_id
JOIN ROOM r ON bo.room_id = r.room_id
JOIN TIME_SLOT ts ON bo.slot_id = ts.slot_id
LEFT JOIN COURSE c ON b.course_id = c.course_id
WHERE bo.status = 'ACTIVE';

-- ----------------------------------------------------------------------------
-- 3. department_timetable_vw
-- Department-centric schedule combining courses offered by each department.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW department_timetable_vw AS
SELECT 
    d.dept_id,
    d.dept_code,
    d.dept_name,
    c.course_code,
    c.course_title,
    c.credits,
    f.faculty_id,
    f.first_name || ' ' || f.last_name AS faculty_name,
    r.room_id,
    r.room_number,
    r.building,
    bo.occurrence_id,
    bo.booking_id,
    bo.occurrence_date,
    TRIM(TO_CHAR(bo.occurrence_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH')) AS day_of_week,
    ts.slot_id,
    ts.slot_name,
    ts.start_time,
    ts.end_time,
    ts.slot_order,
    b.booking_type,
    bo.status
FROM BOOKING_OCCURRENCE bo
JOIN BOOKING b ON bo.booking_id = b.booking_id
JOIN ROOM r ON bo.room_id = r.room_id
JOIN TIME_SLOT ts ON bo.slot_id = ts.slot_id
JOIN FACULTY f ON bo.faculty_id = f.faculty_id
JOIN COURSE c ON b.course_id = c.course_id
JOIN DEPARTMENT d ON c.dept_id = d.dept_id
WHERE bo.status = 'ACTIVE';

-- ----------------------------------------------------------------------------
-- 4. booking_history_vw
-- Full audit trail of all parent bookings and dated occurrences (active & cancelled).
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW booking_history_vw AS
SELECT 
    bo.occurrence_id,
    b.booking_id,
    b.booking_type,
    b.title_purpose,
    bo.occurrence_date,
    TRIM(TO_CHAR(bo.occurrence_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH')) AS day_of_week,
    ts.slot_name,
    ts.start_time,
    ts.end_time,
    r.room_id,
    r.room_number,
    r.building,
    r.room_type,
    r.capacity,
    f.faculty_id,
    f.first_name || ' ' || f.last_name AS faculty_name,
    d.dept_code AS faculty_dept,
    c.course_code,
    c.course_title,
    s.semester_name,
    bo.status,
    bo.cancellation_reason,
    bo.updated_at,
    b.created_at AS booking_created_at
FROM BOOKING_OCCURRENCE bo
JOIN BOOKING b ON bo.booking_id = b.booking_id
JOIN ROOM r ON bo.room_id = r.room_id
JOIN TIME_SLOT ts ON bo.slot_id = ts.slot_id
JOIN FACULTY f ON bo.faculty_id = f.faculty_id
JOIN DEPARTMENT d ON f.dept_id = d.dept_id
LEFT JOIN COURSE c ON b.course_id = c.course_id
LEFT JOIN SEMESTER s ON b.semester_id = s.semester_id;
