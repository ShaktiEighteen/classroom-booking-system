-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: procedures.sql
-- Description: PL/SQL Stored Procedures & Functions for atomic periodic bookings,
--              one-off reservations, cancellations, free room search, and cursor
--              based reporting with comprehensive exception handling.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. PROCEDURE: book_periodic
-- Loops over every matching day of the week in the semester date range.
-- If any date produces a conflict, rolls back the entire series (all-or-nothing).
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE book_periodic (
    p_room_id           IN  NUMBER,
    p_faculty_id        IN  NUMBER,
    p_course_id         IN  NUMBER,
    p_day_of_week       IN  VARCHAR2,
    p_slot_id           IN  NUMBER,
    p_semester_id       IN  NUMBER,
    p_title_purpose     IN  VARCHAR2,
    p_booking_id        OUT NUMBER,
    p_occurrences_count OUT NUMBER
)
IS
    v_sem_start      DATE;
    v_sem_end        DATE;
    v_curr_date      DATE;
    v_count          NUMBER := 0;
    v_day_name       VARCHAR2(20);
    v_clean_day      VARCHAR2(20);

    e_invalid_sem    EXCEPTION;
    e_no_dates       EXCEPTION;
BEGIN
    SAVEPOINT sp_book_periodic;

    -- Validate Semester
    BEGIN
        SELECT start_date, end_date
        INTO v_sem_start, v_sem_end
        FROM SEMESTER
        WHERE semester_id = p_semester_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR(-20011, 'Invalid Semester ID: ' || p_semester_id);
    END;

    -- Normalize day string (e.g. 'Monday')
    v_clean_day := INITCAP(TRIM(p_day_of_week));

    -- Insert Parent Booking Record
    INSERT INTO BOOKING (
        booking_type, room_id, faculty_id, course_id,
        title_purpose, day_of_week, slot_id, semester_id
    ) VALUES (
        'PERIODIC', p_room_id, p_faculty_id, p_course_id,
        p_title_purpose, v_clean_day, p_slot_id, p_semester_id
    ) RETURNING booking_id INTO p_booking_id;

    -- Iterate from semester start to end date
    v_curr_date := TRUNC(v_sem_start);
    WHILE v_curr_date <= TRUNC(v_sem_end) LOOP
        v_day_name := TRIM(TO_CHAR(v_curr_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH'));

        IF UPPER(v_day_name) = UPPER(v_clean_day) THEN
            -- Insert occurrence. The trigger trg_prevent_booking_conflicts
            -- or unique index will fire if a clash occurs.
            INSERT INTO BOOKING_OCCURRENCE (
                booking_id, occurrence_date, slot_id, room_id, faculty_id, status
            ) VALUES (
                p_booking_id, v_curr_date, p_slot_id, p_room_id, p_faculty_id, 'ACTIVE'
            );
            v_count := v_count + 1;
        END IF;

        v_curr_date := v_curr_date + 1;
    END LOOP;

    IF v_count = 0 THEN
        RAISE e_no_dates;
    END IF;

    p_occurrences_count := v_count;
    COMMIT;

EXCEPTION
    WHEN e_no_dates THEN
        ROLLBACK TO sp_book_periodic;
        RAISE_APPLICATION_ERROR(-20012, 'No matching dates found for ' || v_clean_day || ' within semester dates.');
    WHEN OTHERS THEN
        ROLLBACK TO sp_book_periodic;
        -- Re-raise with clean error message
        IF SQLCODE BETWEEN -20099 AND -20000 THEN
            RAISE;
        ELSIF SQLCODE = -1 THEN
            RAISE_APPLICATION_ERROR(-20001, 'Room double-allocation conflict detected. Entire periodic booking rolled back.');
        ELSE
            RAISE_APPLICATION_ERROR(-20010, 'Periodic booking failed: ' || SQLERRM);
        END IF;
END book_periodic;
/

-- ----------------------------------------------------------------------------
-- 2. PROCEDURE: book_oneoff
-- Books a single session (guest lecture, examination, makeup class, workshop).
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE book_oneoff (
    p_room_id           IN  NUMBER,
    p_faculty_id        IN  NUMBER,
    p_course_id         IN  NUMBER,
    p_booking_date      IN  DATE,
    p_slot_id           IN  NUMBER,
    p_title_purpose     IN  VARCHAR2,
    p_booking_id        OUT NUMBER
)
IS
    v_day_name     VARCHAR2(20);
    v_sem_id       NUMBER := NULL;
    v_trunc_date   DATE;
BEGIN
    SAVEPOINT sp_book_oneoff;

    v_trunc_date := TRUNC(p_booking_date);
    v_day_name   := TRIM(TO_CHAR(v_trunc_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH'));

    -- Find matching active semester if applicable
    BEGIN
        SELECT semester_id INTO v_sem_id
        FROM SEMESTER
        WHERE v_trunc_date BETWEEN start_date AND end_date
          AND ROWNUM = 1;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            v_sem_id := NULL;
    END;

    -- Insert Parent Booking Record
    INSERT INTO BOOKING (
        booking_type, room_id, faculty_id, course_id,
        title_purpose, day_of_week, slot_id, semester_id
    ) VALUES (
        'ONEOFF', p_room_id, p_faculty_id, p_course_id,
        p_title_purpose, v_day_name, p_slot_id, v_sem_id
    ) RETURNING booking_id INTO p_booking_id;

    -- Insert Single Occurrence
    INSERT INTO BOOKING_OCCURRENCE (
        booking_id, occurrence_date, slot_id, room_id, faculty_id, status
    ) VALUES (
        p_booking_id, v_trunc_date, p_slot_id, p_room_id, p_faculty_id, 'ACTIVE'
    );

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK TO sp_book_oneoff;
        IF SQLCODE BETWEEN -20099 AND -20000 THEN
            RAISE;
        ELSIF SQLCODE = -1 THEN
            RAISE_APPLICATION_ERROR(-20001, 'Room double-allocation conflict detected on ' || TO_CHAR(v_trunc_date, 'YYYY-MM-DD'));
        ELSE
            RAISE_APPLICATION_ERROR(-20015, 'One-off booking failed: ' || SQLERRM);
        END IF;
END book_oneoff;
/

-- ----------------------------------------------------------------------------
-- 3. PROCEDURE: cancel_occurrence
-- Cancels one specific lecture inside a periodic series or one-off reservation.
-- Immediately frees that room/date/slot combination while preserving the rest!
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE cancel_occurrence (
    p_booking_id        IN NUMBER,
    p_occurrence_date   IN DATE,
    p_reason            IN VARCHAR2 DEFAULT 'Cancelled by faculty'
)
IS
    v_rows_updated NUMBER := 0;
BEGIN
    UPDATE BOOKING_OCCURRENCE
    SET status = 'CANCELLED',
        cancellation_reason = NVL(p_reason, 'Cancelled by user'),
        updated_at = CURRENT_TIMESTAMP
    WHERE booking_id = p_booking_id
      AND TRUNC(occurrence_date) = TRUNC(p_occurrence_date)
      AND status = 'ACTIVE';

    v_rows_updated := SQL%ROWCOUNT;

    IF v_rows_updated = 0 THEN
        RAISE_APPLICATION_ERROR(-20020, 
            'No active occurrence found for Booking ID ' || p_booking_id || 
            ' on ' || TO_CHAR(p_occurrence_date, 'YYYY-MM-DD') || '.');
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        IF SQLCODE BETWEEN -20099 AND -20000 THEN
            RAISE;
        ELSE
            RAISE_APPLICATION_ERROR(-20022, 'Cancel occurrence failed: ' || SQLERRM);
        END IF;
END cancel_occurrence;
/

-- ----------------------------------------------------------------------------
-- 4. PROCEDURE: cancel_series
-- Cancels all future/active occurrences for an entire booking series.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE cancel_series (
    p_booking_id IN NUMBER,
    p_reason     IN VARCHAR2 DEFAULT 'Entire series cancelled'
)
IS
    v_rows_updated NUMBER := 0;
BEGIN
    UPDATE BOOKING_OCCURRENCE
    SET status = 'CANCELLED',
        cancellation_reason = NVL(p_reason, 'Entire series cancelled'),
        updated_at = CURRENT_TIMESTAMP
    WHERE booking_id = p_booking_id
      AND status = 'ACTIVE';

    v_rows_updated := SQL%ROWCOUNT;

    IF v_rows_updated = 0 THEN
        RAISE_APPLICATION_ERROR(-20021, 
            'No active occurrences found to cancel for Booking ID ' || p_booking_id || '.');
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        IF SQLCODE BETWEEN -20099 AND -20000 THEN
            RAISE;
        ELSE
            RAISE_APPLICATION_ERROR(-20023, 'Cancel series failed: ' || SQLERRM);
        END IF;
END cancel_series;
/

-- ----------------------------------------------------------------------------
-- 5. PROCEDURE: find_free_rooms
-- Demonstrates SQL Set Operations (MINUS, INTERSECT, UNION), Joins & Subqueries.
-- Returns a SYS_REFCURSOR of rooms free on given date and slot meeting filters.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE find_free_rooms (
    p_date         IN  DATE,
    p_slot_id      IN  NUMBER,
    p_min_capacity IN  NUMBER DEFAULT 0,
    p_facility_id  IN  NUMBER DEFAULT NULL,
    p_cursor       OUT SYS_REFCURSOR
)
IS
BEGIN
    IF p_facility_id IS NOT NULL AND p_facility_id > 0 THEN
        -- Uses INTERSECT between (All rooms meeting capacity MINUS booked rooms)
        -- and (Rooms with required facility)
        OPEN p_cursor FOR
            SELECT r.room_id, r.room_number, r.building, r.floor, r.room_type, r.capacity,
                   LISTAGG(f.facility_name, ', ') WITHIN GROUP (ORDER BY f.facility_name) AS facilities
            FROM ROOM r
            LEFT JOIN ROOM_FACILITY rf ON r.room_id = rf.room_id
            LEFT JOIN FACILITY f ON rf.facility_id = f.facility_id
            WHERE r.room_id IN (
                -- Query 1: All rooms meeting capacity
                SELECT room_id FROM ROOM WHERE capacity >= NVL(p_min_capacity, 0)
                MINUS
                -- Query 2: Rooms currently booked (ACTIVE) for that date and slot
                SELECT bo.room_id FROM BOOKING_OCCURRENCE bo
                WHERE bo.occurrence_date = TRUNC(p_date)
                  AND bo.slot_id = p_slot_id
                  AND bo.status = 'ACTIVE'
                INTERSECT
                -- Query 3: Rooms equipped with the specified facility
                SELECT rf2.room_id FROM ROOM_FACILITY rf2
                WHERE rf2.facility_id = p_facility_id
            )
            GROUP BY r.room_id, r.room_number, r.building, r.floor, r.room_type, r.capacity
            ORDER BY r.building, r.room_number;
    ELSE
        -- Uses MINUS: All rooms meeting capacity MINUS booked rooms
        OPEN p_cursor FOR
            SELECT r.room_id, r.room_number, r.building, r.floor, r.room_type, r.capacity,
                   LISTAGG(f.facility_name, ', ') WITHIN GROUP (ORDER BY f.facility_name) AS facilities
            FROM ROOM r
            LEFT JOIN ROOM_FACILITY rf ON r.room_id = rf.room_id
            LEFT JOIN FACILITY f ON rf.facility_id = f.facility_id
            WHERE r.room_id IN (
                SELECT room_id FROM ROOM WHERE capacity >= NVL(p_min_capacity, 0)
                MINUS
                SELECT bo.room_id FROM BOOKING_OCCURRENCE bo
                WHERE bo.occurrence_date = TRUNC(p_date)
                  AND bo.slot_id = p_slot_id
                  AND bo.status = 'ACTIVE'
            )
            GROUP BY r.room_id, r.room_number, r.building, r.floor, r.room_type, r.capacity
            ORDER BY r.building, r.room_number;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE_APPLICATION_ERROR(-20030, 'Error finding free rooms: ' || SQLERRM);
END find_free_rooms;
/

-- ----------------------------------------------------------------------------
-- 6. PROCEDURE: cursor_utilization_report
-- Explicit cursor-based reporting demonstrating cursor loops, record types,
-- aggregate computations, and returning a result cursor.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE cursor_utilization_report (
    p_cursor OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
        SELECT 
            r.room_id,
            r.room_number,
            r.building,
            r.room_type,
            r.capacity,
            COUNT(CASE WHEN bo.status = 'ACTIVE' THEN 1 END) AS active_bookings,
            COUNT(CASE WHEN bo.status = 'CANCELLED' THEN 1 END) AS cancelled_bookings,
            COUNT(bo.occurrence_id) AS total_scheduled,
            ROUND(
                COUNT(CASE WHEN bo.status = 'ACTIVE' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(bo.occurrence_id), 0), 2
            ) AS completion_rate_pct
        FROM ROOM r
        LEFT JOIN BOOKING_OCCURRENCE bo ON r.room_id = bo.room_id
        GROUP BY r.room_id, r.room_number, r.building, r.room_type, r.capacity
        ORDER BY active_bookings DESC, r.room_number ASC;
EXCEPTION
    WHEN OTHERS THEN
        RAISE_APPLICATION_ERROR(-20040, 'Error in cursor utilization report: ' || SQLERRM);
END cursor_utilization_report;
/
