-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: queries.sql
-- Description: 15 Documented SQL Demonstration Queries showcasing relational
--              algebra, joins, aggregations, set operations, subqueries,
--              analytical functions, and views.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Selection and Filtering
-- Concept: Simple Projection and Selection with Comparison and Pattern Matching
-- Finds all specialized computer and electronics laboratories with capacity >= 35.
-- ----------------------------------------------------------------------------
SELECT room_id, room_number, building, floor, room_type, capacity
FROM ROOM
WHERE room_type = 'LAB'
  AND capacity >= 35
ORDER BY capacity DESC, room_number ASC;

-- ----------------------------------------------------------------------------
-- Query 2: Two-Table Equi-Join
-- Concept: Inner Join between Parent and Child Entity (FACULTY and DEPARTMENT)
-- Lists all faculty members with their department names and designations.
-- ----------------------------------------------------------------------------
SELECT 
    f.faculty_code,
    f.first_name || ' ' || f.last_name AS faculty_name,
    f.email,
    f.designation,
    d.dept_name,
    d.office_location
FROM FACULTY f
JOIN DEPARTMENT d ON f.dept_id = d.dept_id
ORDER BY d.dept_name, f.last_name;

-- ----------------------------------------------------------------------------
-- Query 3: Multi-Table Join
-- Concept: 3-way Inner Join linking Courses, Departments, and Faculty
-- Displays each course along with its offering department and department head/professors.
-- ----------------------------------------------------------------------------
SELECT 
    c.course_code,
    c.course_title,
    c.credits,
    d.dept_code,
    d.dept_name,
    f.first_name || ' ' || f.last_name AS faculty_member
FROM COURSE c
JOIN DEPARTMENT d ON c.dept_id = d.dept_id
JOIN FACULTY f ON d.dept_id = f.dept_id
WHERE f.designation = 'Professor'
ORDER BY c.course_code, f.last_name;

-- ----------------------------------------------------------------------------
-- Query 4: Left Outer Join with String Aggregation
-- Concept: LEFT OUTER JOIN preserving all rooms and LISTAGG() for M:N mapping
-- Shows all rooms and their installed facilities (even rooms with no added facilities).
-- ----------------------------------------------------------------------------
SELECT 
    r.room_number,
    r.building,
    r.capacity,
    NVL(LISTAGG(f.facility_name, '; ') WITHIN GROUP (ORDER BY f.facility_name), 'Standard Classroom Setup') AS installed_facilities
FROM ROOM r
LEFT JOIN ROOM_FACILITY rf ON r.room_id = rf.room_id
LEFT JOIN FACILITY f ON rf.facility_id = f.facility_id
GROUP BY r.room_number, r.building, r.capacity
ORDER BY r.capacity DESC;

-- ----------------------------------------------------------------------------
-- Query 5: Grouping and Aggregate Metrics
-- Concept: GROUP BY with COUNT, AVG, MIN, MAX aggregations
-- Computes faculty headcount and average course credits per department.
-- ----------------------------------------------------------------------------
SELECT 
    d.dept_code,
    d.dept_name,
    COUNT(DISTINCT f.faculty_id) AS total_faculty,
    COUNT(DISTINCT c.course_id) AS total_courses_offered,
    ROUND(AVG(c.credits), 2) AS avg_course_credits
FROM DEPARTMENT d
LEFT JOIN FACULTY f ON d.dept_id = f.dept_id
LEFT JOIN COURSE c ON d.dept_id = c.dept_id
GROUP BY d.dept_code, d.dept_name
ORDER BY total_faculty DESC;

-- ----------------------------------------------------------------------------
-- Query 6: Post-Aggregation Filtering
-- Concept: GROUP BY with HAVING Clause
-- Finds rooms that have been scheduled for more than 10 total active lectures.
-- ----------------------------------------------------------------------------
SELECT 
    r.room_number,
    r.building,
    r.room_type,
    r.capacity,
    COUNT(bo.occurrence_id) AS active_session_count
FROM ROOM r
JOIN BOOKING_OCCURRENCE bo ON r.room_id = bo.room_id
WHERE bo.status = 'ACTIVE'
GROUP BY r.room_number, r.building, r.room_type, r.capacity
HAVING COUNT(bo.occurrence_id) >= 10
ORDER BY active_session_count DESC;

-- ----------------------------------------------------------------------------
-- Query 7: Set Operation - MINUS
-- Concept: Set Difference (MINUS) for Free Room Detection
-- Identifies large rooms (capacity >= 60) that have NO active booking on 2026-08-10 at Slot 1.
-- ----------------------------------------------------------------------------
SELECT room_id, room_number, building, capacity
FROM ROOM
WHERE capacity >= 60
MINUS
SELECT r.room_id, r.room_number, r.building, r.capacity
FROM ROOM r
JOIN BOOKING_OCCURRENCE bo ON r.room_id = bo.room_id
WHERE bo.occurrence_date = TO_DATE('2026-08-10', 'YYYY-MM-DD')
  AND bo.slot_id = 1
  AND bo.status = 'ACTIVE'
ORDER BY capacity DESC;

-- ----------------------------------------------------------------------------
-- Query 8: Set Operation - INTERSECT
-- Concept: Set Intersection (INTERSECT)
-- Identifies rooms that possess BOTH a '4K Laser Projector' AND 'Central Air Conditioning'.
-- ----------------------------------------------------------------------------
SELECT r.room_id, r.room_number, r.building, r.capacity
FROM ROOM r
JOIN ROOM_FACILITY rf ON r.room_id = rf.room_id
JOIN FACILITY f ON rf.facility_id = f.facility_id
WHERE f.facility_name = '4K Laser Projector'
INTERSECT
SELECT r.room_id, r.room_number, r.building, r.capacity
FROM ROOM r
JOIN ROOM_FACILITY rf ON r.room_id = rf.room_id
JOIN FACILITY f ON rf.facility_id = f.facility_id
WHERE f.facility_name = 'Central Air Conditioning'
ORDER BY room_number;

-- ----------------------------------------------------------------------------
-- Query 9: Set Operation - UNION ALL
-- Concept: Set Union combining disparate event streams
-- Consolidates all regular periodic lectures and one-off special events in October 2026.
-- ----------------------------------------------------------------------------
SELECT 
    'Periodic Lecture' AS event_category,
    b.title_purpose AS description,
    bo.occurrence_date,
    ts.slot_name,
    r.room_number
FROM BOOKING b
JOIN BOOKING_OCCURRENCE bo ON b.booking_id = bo.booking_id
JOIN TIME_SLOT ts ON bo.slot_id = ts.slot_id
JOIN ROOM r ON bo.room_id = r.room_id
WHERE b.booking_type = 'PERIODIC'
  AND bo.status = 'ACTIVE'
  AND bo.occurrence_date BETWEEN TO_DATE('2026-10-01', 'YYYY-MM-DD') AND TO_DATE('2026-10-07', 'YYYY-MM-DD')
UNION ALL
SELECT 
    'Special One-Off Event' AS event_category,
    b.title_purpose AS description,
    bo.occurrence_date,
    ts.slot_name,
    r.room_number
FROM BOOKING b
JOIN BOOKING_OCCURRENCE bo ON b.booking_id = bo.booking_id
JOIN TIME_SLOT ts ON bo.slot_id = ts.slot_id
JOIN ROOM r ON bo.room_id = r.room_id
WHERE b.booking_type = 'ONEOFF'
  AND bo.status = 'ACTIVE'
ORDER BY occurrence_date, slot_name;

-- ----------------------------------------------------------------------------
-- Query 10: Correlated Subquery with EXISTS
-- Concept: Correlated Subquery with EXISTS
-- Retrieves faculty members who have at least one booking in a Seminar Hall or Auditorium.
-- ----------------------------------------------------------------------------
SELECT f.faculty_id, f.first_name || ' ' || f.last_name AS faculty_name, f.email, d.dept_name
FROM FACULTY f
JOIN DEPARTMENT d ON f.dept_id = d.dept_id
WHERE EXISTS (
    SELECT 1 
    FROM BOOKING_OCCURRENCE bo
    JOIN ROOM r ON bo.room_id = r.room_id
    WHERE bo.faculty_id = f.faculty_id
      AND r.room_type = 'SEMINAR_HALL'
      AND bo.status = 'ACTIVE'
)
ORDER BY f.last_name;

-- ----------------------------------------------------------------------------
-- Query 11: Subquery with NOT IN
-- Concept: Uncorrelated Subquery with NOT IN
-- Identifies time slots that currently have no bookings scheduled across any room on Saturdays.
-- ----------------------------------------------------------------------------
SELECT ts.slot_id, ts.slot_name, ts.start_time, ts.end_time
FROM TIME_SLOT ts
WHERE ts.slot_id NOT IN (
    SELECT DISTINCT bo.slot_id
    FROM BOOKING_OCCURRENCE bo
    WHERE TRIM(TO_CHAR(bo.occurrence_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH')) = 'Saturday'
      AND bo.status = 'ACTIVE'
)
ORDER BY ts.slot_order;

-- ----------------------------------------------------------------------------
-- Query 12: Analytical Query using View
-- Concept: Analytical query utilizing room_utilization_vw
-- Highlights room utilization metrics sorted by active booking volume and completion rate.
-- ----------------------------------------------------------------------------
SELECT 
    room_number,
    building,
    room_type,
    capacity,
    active_bookings_count,
    cancelled_bookings_count,
    active_days_utilized,
    active_success_rate_pct
FROM room_utilization_vw
WHERE active_bookings_count > 0
ORDER BY active_bookings_count DESC, active_success_rate_pct DESC;

-- ----------------------------------------------------------------------------
-- Query 13: Timetable View Query
-- Concept: Timetable Extraction using faculty_timetable_vw
-- Retrieves full timetable for Dr. Alan Turing ordered chronologically.
-- ----------------------------------------------------------------------------
SELECT 
    faculty_name,
    occurrence_date,
    day_of_week,
    slot_name,
    start_time,
    room_number,
    course_code,
    session_title
FROM faculty_timetable_vw
WHERE faculty_name LIKE '%Alan Turing%'
ORDER BY occurrence_date, slot_order;

-- ----------------------------------------------------------------------------
-- Query 14: Analytical Window Function (DENSE_RANK)
-- Concept: Window / Analytic Function (DENSE_RANK() OVER PARTITION BY)
-- Ranks rooms by capacity within each academic building.
-- ----------------------------------------------------------------------------
SELECT 
    building,
    room_number,
    room_type,
    capacity,
    DENSE_RANK() OVER (PARTITION BY building ORDER BY capacity DESC) AS capacity_rank_in_building
FROM ROOM
ORDER BY building, capacity_rank_in_building;

-- ----------------------------------------------------------------------------
-- Query 15: Historical Audit Trail Query
-- Concept: Comprehensive Audit query using booking_history_vw
-- Inspects all cancelled occurrences with reasons and timestamps.
-- ----------------------------------------------------------------------------
SELECT 
    booking_id,
    booking_type,
    title_purpose,
    occurrence_date,
    day_of_week,
    slot_name,
    room_number,
    faculty_name,
    cancellation_reason,
    updated_at AS cancelled_timestamp
FROM booking_history_vw
WHERE status = 'CANCELLED'
ORDER BY updated_at DESC;
