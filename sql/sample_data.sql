-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: sample_data.sql
-- Description: Comprehensive realistic sample dataset:
--              5 Departments, 15 Faculty, 25 Courses, 6 Facilities, 20 Rooms
--              (with facility mappings), 8 Time Slots, Semester,
--              Full semester of periodic bookings, one-off bookings & cancellations.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. DEPARTMENTS (5)
-- ----------------------------------------------------------------------------
INSERT INTO DEPARTMENT (dept_id, dept_code, dept_name, office_location) VALUES (1, 'CSE', 'Computer Science and Engineering', 'Block A, Floor 3');
INSERT INTO DEPARTMENT (dept_id, dept_code, dept_name, office_location) VALUES (2, 'ECE', 'Electronics and Communication Engineering', 'Block B, Floor 2');
INSERT INTO DEPARTMENT (dept_id, dept_code, dept_name, office_location) VALUES (3, 'MECH', 'Mechanical Engineering', 'Block C, Floor 1');
INSERT INTO DEPARTMENT (dept_id, dept_code, dept_name, office_location) VALUES (4, 'CIVIL', 'Civil Engineering', 'Block D, Floor 1');
INSERT INTO DEPARTMENT (dept_id, dept_code, dept_name, office_location) VALUES (5, 'MATH', 'Mathematics and Computing', 'Block A, Floor 4');

-- ----------------------------------------------------------------------------
-- 2. FACULTY (15 - 3 per department)
-- ----------------------------------------------------------------------------
-- CSE Faculty
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (1, 'FAC_CS01', 'Alan', 'Turing', 'a.turing@university.edu', 1, 'Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (2, 'FAC_CS02', 'Ada', 'Lovelace', 'a.lovelace@university.edu', 1, 'Associate Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (3, 'FAC_CS03', 'Donald', 'Knuth', 'd.knuth@university.edu', 1, 'Assistant Professor');

-- ECE Faculty
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (4, 'FAC_EC01', 'Claude', 'Shannon', 'c.shannon@university.edu', 2, 'Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (5, 'FAC_EC02', 'John', 'Bardeen', 'j.bardeen@university.edu', 2, 'Associate Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (6, 'FAC_EC03', 'Robert', 'Noyce', 'r.noyce@university.edu', 2, 'Assistant Professor');

-- MECH Faculty
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (7, 'FAC_ME01', 'James', 'Watt', 'j.watt@university.edu', 3, 'Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (8, 'FAC_ME02', 'Nikola', 'Tesla', 'n.tesla@university.edu', 3, 'Associate Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (9, 'FAC_ME03', 'Rudolf', 'Diesel', 'r.diesel@university.edu', 3, 'Assistant Professor');

-- CIVIL Faculty
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (10, 'FAC_CE01', 'Thomas', 'Telford', 't.telford@university.edu', 4, 'Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (11, 'FAC_CE02', 'Isambard', 'Brunel', 'i.brunel@university.edu', 4, 'Associate Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (12, 'FAC_CE03', 'Gustave', 'Eiffel', 'g.eiffel@university.edu', 4, 'Assistant Professor');

-- MATH Faculty
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (13, 'FAC_MA01', 'Carl', 'Gauss', 'c.gauss@university.edu', 5, 'Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (14, 'FAC_MA02', 'Leonhard', 'Euler', 'l.euler@university.edu', 5, 'Associate Professor');
INSERT INTO FACULTY (faculty_id, faculty_code, first_name, last_name, email, dept_id, designation)
VALUES (15, 'FAC_MA03', 'Emmy', 'Noether', 'e.noether@university.edu', 5, 'Assistant Professor');

-- ----------------------------------------------------------------------------
-- 3. COURSES (25 - 5 per department)
-- ----------------------------------------------------------------------------
-- CSE Courses
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (1, 'CS101', 'Data Structures and Algorithms', 4, 1);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (2, 'CS201', 'Database Management Systems', 4, 1);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (3, 'CS301', 'Operating Systems', 4, 1);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (4, 'CS401', 'Computer Networks', 3, 1);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (5, 'CS501', 'Artificial Intelligence', 3, 1);

-- ECE Courses
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (6, 'EC101', 'Digital Signal Processing', 4, 2);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (7, 'EC201', 'VLSI Circuit Design', 4, 2);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (8, 'EC301', 'Microprocessors and Microcontrollers', 3, 2);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (9, 'EC401', 'Analog and Digital Communication', 4, 2);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (10, 'EC501', 'Embedded Real-Time Systems', 3, 2);

-- MECH Courses
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (11, 'ME101', 'Applied Thermodynamics', 4, 3);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (12, 'ME201', 'Fluid Mechanics and Dynamics', 4, 3);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (13, 'ME301', 'Kinematics of Machinery', 3, 3);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (14, 'ME401', 'Robotics and Industrial Automation', 4, 3);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (15, 'ME501', 'Heat and Mass Transfer', 3, 3);

-- CIVIL Courses
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (16, 'CE101', 'Structural Mechanics and Design', 4, 4);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (17, 'CE201', 'Geotechnical and Soil Engineering', 4, 4);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (18, 'CE301', 'Transportation Infrastructure', 3, 4);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (19, 'CE401', 'Hydraulics and Water Resources', 4, 4);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (20, 'CE501', 'Environmental Engineering', 3, 4);

-- MATH Courses
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (21, 'MA101', 'Linear Algebra and Matrix Analysis', 4, 5);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (22, 'MA201', 'Multivariable Calculus and ODEs', 4, 5);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (23, 'MA301', 'Discrete Mathematics and Graph Theory', 3, 5);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (24, 'MA401', 'Numerical Computation Techniques', 3, 5);
INSERT INTO COURSE (course_id, course_code, course_title, credits, dept_id) VALUES (25, 'MA501', 'Probability and Applied Statistics', 4, 5);

-- ----------------------------------------------------------------------------
-- 4. FACILITIES (6)
-- ----------------------------------------------------------------------------
INSERT INTO FACILITY (facility_id, facility_name, description) VALUES (1, '4K Laser Projector', 'Ultra-HD roof projector with wireless HDMI casting');
INSERT INTO FACILITY (facility_id, facility_name, description) VALUES (2, 'Central Air Conditioning', 'Climate control HVAC system');
INSERT INTO FACILITY (facility_id, facility_name, description) VALUES (3, 'High-End Workstations', 'Core i7 / 32GB RAM developer machines');
INSERT INTO FACILITY (facility_id, facility_name, description) VALUES (4, 'Smart Interactive Board', '86-inch 4K touchscreen digital interactive display');
INSERT INTO FACILITY (facility_id, facility_name, description) VALUES (5, 'Surround Audio & Lapel Mic', 'Studio sound system with cordless collar microphones');
INSERT INTO FACILITY (facility_id, facility_name, description) VALUES (6, 'Hardware Test Benches', 'Oscilloscopes, function generators, and power supplies');

-- ----------------------------------------------------------------------------
-- 5. ROOMS (20 - Classrooms, Lecture Halls, Laboratories, Seminar Halls)
-- ----------------------------------------------------------------------------
-- Building A (Main Academic Block)
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (1, 'CR-A101', 'Block A', 1, 'CLASSROOM', 60);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (2, 'CR-A102', 'Block A', 1, 'CLASSROOM', 60);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (3, 'CR-A201', 'Block A', 2, 'CLASSROOM', 60);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (4, 'CR-A202', 'Block A', 2, 'CLASSROOM', 60);

-- Building B (Science & Engineering Block)
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (5, 'CR-B101', 'Block B', 1, 'CLASSROOM', 75);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (6, 'CR-B102', 'Block B', 1, 'CLASSROOM', 75);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (7, 'CR-B201', 'Block B', 2, 'CLASSROOM', 75);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (8, 'CR-B202', 'Block B', 2, 'CLASSROOM', 75);

-- Building C (Auditorium & Large Lecture Theatres)
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (9,  'LT-C001', 'Block C', 0, 'SEMINAR_HALL', 150);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (10, 'LT-C002', 'Block C', 0, 'SEMINAR_HALL', 150);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (11, 'AUD-MAIN', 'Block C', 0, 'SEMINAR_HALL', 300);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (12, 'CR-C101', 'Block C', 1, 'CLASSROOM', 80);

-- Building D (Computing & Electronics Laboratories)
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (13, 'LAB-CS-01', 'Block D', 1, 'LAB', 45);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (14, 'LAB-CS-02', 'Block D', 1, 'LAB', 45);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (15, 'LAB-AI-01', 'Block D', 2, 'LAB', 40);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (16, 'LAB-EC-01', 'Block D', 2, 'LAB', 35);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (17, 'LAB-EC-02', 'Block D', 3, 'LAB', 35);

-- Building E (Mechanical & Civil Engineering Labs / Classrooms)
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (18, 'LAB-ME-01', 'Block E', 1, 'LAB', 30);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (19, 'LAB-CE-01', 'Block E', 1, 'LAB', 30);
INSERT INTO ROOM (room_id, room_number, building, floor, room_type, capacity) VALUES (20, 'CR-E201',   'Block E', 2, 'CLASSROOM', 50);

-- ----------------------------------------------------------------------------
-- 6. ROOM_FACILITY MAPPINGS
-- ----------------------------------------------------------------------------
-- CR-A101: Projector, AC
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (1, 1, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (1, 2, 2);
-- CR-A102: Projector, AC, Smart Board
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (2, 1, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (2, 2, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (2, 4, 1);
-- CR-A201: Projector
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (3, 1, 1);
-- CR-A202: Projector, AC
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (4, 1, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (4, 2, 2);
-- Large Lecture Theatres: Projector, AC, Audio System
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (9, 1, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (9, 2, 4);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (9, 5, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (10, 1, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (10, 2, 4);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (10, 5, 1);
-- Auditorium: Projector, AC, Smart Board, Audio System
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (11, 1, 3);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (11, 2, 6);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (11, 4, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (11, 5, 1);
-- Computer Labs: AC, Workstations, Projector
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (13, 1, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (13, 2, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (13, 3, 45);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (14, 1, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (14, 2, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (14, 3, 45);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (15, 1, 1);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (15, 2, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (15, 3, 40);
-- Electronics Labs: AC, Hardware Test Benches
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (16, 2, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (16, 6, 20);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (17, 2, 2);
INSERT INTO ROOM_FACILITY (room_id, facility_id, quantity) VALUES (17, 6, 20);

-- ----------------------------------------------------------------------------
-- 7. SEMESTER
-- ----------------------------------------------------------------------------
INSERT INTO SEMESTER (semester_id, semester_name, start_date, end_date, is_active)
VALUES (1, 'Fall Semester 2026', TO_DATE('2026-08-03', 'YYYY-MM-DD'), TO_DATE('2026-11-28', 'YYYY-MM-DD'), 1);

INSERT INTO SEMESTER (semester_id, semester_name, start_date, end_date, is_active)
VALUES (2, 'Spring Semester 2027', TO_DATE('2027-01-04', 'YYYY-MM-DD'), TO_DATE('2027-05-15', 'YYYY-MM-DD'), 0);

-- ----------------------------------------------------------------------------
-- 8. TIME_SLOTS (8 per day)
-- ----------------------------------------------------------------------------
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (1, 'Slot 1 (08:30 - 09:30)', '08:30', '09:30', 1);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (2, 'Slot 2 (09:30 - 10:30)', '09:30', '10:30', 2);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (3, 'Slot 3 (10:45 - 11:45)', '10:45', '11:45', 3);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (4, 'Slot 4 (11:45 - 12:45)', '11:45', '12:45', 4);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (5, 'Slot 5 (13:30 - 14:30)', '13:30', '14:30', 5);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (6, 'Slot 6 (14:30 - 15:30)', '14:30', '15:30', 6);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (7, 'Slot 7 (15:45 - 16:45)', '15:45', '16:45', 7);
INSERT INTO TIME_SLOT (slot_id, slot_name, start_time, end_time, slot_order) VALUES (8, 'Slot 8 (16:45 - 17:45)', '16:45', '17:45', 8);

COMMIT;

-- ----------------------------------------------------------------------------
-- 9. PERIODIC BOOKINGS (Created via PL/SQL book_periodic)
-- ----------------------------------------------------------------------------
DECLARE
    v_bid NUMBER;
    v_cnt NUMBER;
BEGIN
    -- CSE: CS101 by Dr. Alan Turing, Mondays Slot 1 in Room CR-A101
    book_periodic(1, 1, 1, 'Monday', 1, 1, 'CS101: Data Structures Lecture', v_bid, v_cnt);

    -- CSE: CS201 by Dr. Ada Lovelace, Mondays Slot 2 in Room CR-A102
    book_periodic(2, 2, 2, 'Monday', 2, 1, 'CS201: DBMS Lecture', v_bid, v_cnt);

    -- CSE: CS301 by Dr. Donald Knuth, Tuesdays Slot 3 in Room CR-A201
    book_periodic(3, 3, 3, 'Tuesday', 3, 1, 'CS301: Operating Systems Lecture', v_bid, v_cnt);

    -- CSE: CS501 by Dr. Alan Turing, Wednesdays Slot 4 in Room LT-C001
    book_periodic(9, 1, 5, 'Wednesday', 4, 1, 'CS501: AI Large Lecture', v_bid, v_cnt);

    -- CSE Lab: CS101 Lab by Dr. Ada Lovelace, Thursdays Slot 5 in LAB-CS-01
    book_periodic(13, 2, 1, 'Thursday', 5, 1, 'CS101: Practical Programming Lab', v_bid, v_cnt);

    -- ECE: EC101 by Dr. Claude Shannon, Mondays Slot 3 in Room CR-B101
    book_periodic(5, 4, 6, 'Monday', 3, 1, 'EC101: DSP Foundations', v_bid, v_cnt);

    -- ECE: EC201 by Dr. John Bardeen, Tuesdays Slot 2 in Room CR-B102
    book_periodic(6, 5, 7, 'Tuesday', 2, 1, 'EC201: VLSI Design Lecture', v_bid, v_cnt);

    -- ECE Lab: EC201 Lab by Dr. Robert Noyce, Fridays Slot 6 in LAB-EC-01
    book_periodic(16, 6, 7, 'Friday', 6, 1, 'EC201: Hardware Lab', v_bid, v_cnt);

    -- MECH: ME101 by Dr. James Watt, Wednesdays Slot 1 in Room CR-B201
    book_periodic(7, 7, 11, 'Wednesday', 1, 1, 'ME101: Thermodynamics', v_bid, v_cnt);

    -- MECH: ME401 by Dr. Nikola Tesla, Thursdays Slot 4 in Room LT-C002
    book_periodic(10, 8, 14, 'Thursday', 4, 1, 'ME401: Robotics Lecture', v_bid, v_cnt);

    -- CIVIL: CE101 by Dr. Thomas Telford, Tuesdays Slot 1 in Room CR-B202
    book_periodic(8, 10, 16, 'Tuesday', 1, 1, 'CE101: Structural Mechanics', v_bid, v_cnt);

    -- CIVIL: CE301 by Dr. Isambard Brunel, Fridays Slot 3 in Room CR-C101
    book_periodic(12, 11, 18, 'Friday', 3, 1, 'CE301: Transportation Infrastructure', v_bid, v_cnt);

    -- MATH: MA101 by Dr. Carl Gauss, Mondays Slot 4 in Room CR-A202
    book_periodic(4, 13, 21, 'Monday', 4, 1, 'MA101: Linear Algebra Core', v_bid, v_cnt);

    -- MATH: MA201 by Dr. Leonhard Euler, Thursdays Slot 2 in Room CR-A101
    book_periodic(1, 14, 22, 'Thursday', 2, 1, 'MA201: Calculus and ODEs', v_bid, v_cnt);

    -- MATH: MA501 by Dr. Emmy Noether, Saturdays Slot 2 in Room CR-A102
    book_periodic(2, 15, 25, 'Saturday', 2, 1, 'MA501: Applied Probability', v_bid, v_cnt);
END;
/

-- ----------------------------------------------------------------------------
-- 10. ONE-OFF BOOKINGS (Created via PL/SQL book_oneoff)
-- ----------------------------------------------------------------------------
DECLARE
    v_bid NUMBER;
BEGIN
    -- Guest Lecture by Alan Turing on Cryptography
    book_oneoff(11, 1, NULL, TO_DATE('2026-09-15', 'YYYY-MM-DD'), 5, 'Distinguished Guest Lecture on Modern Cryptography', v_bid);

    -- Midterm Exam for Database Systems
    book_oneoff(9, 2, 2, TO_DATE('2026-10-14', 'YYYY-MM-DD'), 3, 'CS201 Midterm Examination', v_bid);

    -- Robotics Workshop
    book_oneoff(10, 8, 14, TO_DATE('2026-10-24', 'YYYY-MM-DD'), 7, 'Autonomous Robotics Hands-on Workshop', v_bid);

    -- Project Presentation in Main Auditorium
    book_oneoff(11, 4, NULL, TO_DATE('2026-11-05', 'YYYY-MM-DD'), 6, 'Annual Engineering Capstone Project Showcase', v_bid);
END;
/

-- ----------------------------------------------------------------------------
-- 11. CANCELLATIONS (Demonstrates single occurrence cancellation freeing slot)
-- ----------------------------------------------------------------------------
DECLARE
    v_first_bid NUMBER;
BEGIN
    -- Cancel Alan Turing's CS101 class on 2026-08-17 (e.g. University holiday / Conference)
    SELECT MIN(booking_id) INTO v_first_bid FROM BOOKING WHERE booking_type = 'PERIODIC' AND room_id = 1;
    cancel_occurrence(v_first_bid, TO_DATE('2026-08-17', 'YYYY-MM-DD'), 'Faculty attending IEEE International Conference');

    -- Cancel Ada Lovelace's CS201 class on 2026-09-07
    SELECT MIN(booking_id) INTO v_first_bid FROM BOOKING WHERE booking_type = 'PERIODIC' AND room_id = 2;
    cancel_occurrence(v_first_bid, TO_DATE('2026-09-07', 'YYYY-MM-DD'), 'Departmental Faculty Meeting');
END;
/
