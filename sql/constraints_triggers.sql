-- ============================================================================
-- Classroom Booking and Timetable Management System
-- File: constraints_triggers.sql
-- Description: Unique function-based indexes and PL/SQL triggers for conflict
--              prevention (double allocation and faculty clash detection).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. UNIQUE FUNCTION-BASED INDEX FOR ACTIVE ROOM OCCURRENCES
-- Only ACTIVE bookings are indexed. When status = 'CANCELLED', the expression
-- evaluates to NULL, and Oracle B-tree indexes omit entries where all columns
-- are NULL. This immediately frees the (room, date, slot) upon cancellation!
-- ----------------------------------------------------------------------------
CREATE UNIQUE INDEX uq_active_room_date_slot ON BOOKING_OCCURRENCE (
    CASE WHEN status = 'ACTIVE' THEN room_id ELSE NULL END,
    CASE WHEN status = 'ACTIVE' THEN occurrence_date ELSE NULL END,
    CASE WHEN status = 'ACTIVE' THEN slot_id ELSE NULL END
);

-- ----------------------------------------------------------------------------
-- 2. UNIQUE FUNCTION-BASED INDEX FOR ACTIVE FACULTY OCCURRENCES
-- Ensures a faculty member cannot be double-booked at the structural index level.
-- ----------------------------------------------------------------------------
CREATE UNIQUE INDEX uq_active_fac_date_slot ON BOOKING_OCCURRENCE (
    CASE WHEN status = 'ACTIVE' THEN faculty_id ELSE NULL END,
    CASE WHEN status = 'ACTIVE' THEN occurrence_date ELSE NULL END,
    CASE WHEN status = 'ACTIVE' THEN slot_id ELSE NULL END
);

-- ----------------------------------------------------------------------------
-- 3. COMPOUND TRIGGER: trg_prevent_booking_conflicts
-- Rejects double bookings for rooms and faculty clashes with user-friendly
-- RAISE_APPLICATION_ERROR messages. Uses COMPOUND TRIGGER to completely avoid
-- ORA-04091 mutating table errors on bulk or periodic inserts.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_prevent_booking_conflicts
FOR INSERT OR UPDATE ON BOOKING_OCCURRENCE
COMPOUND TRIGGER

    TYPE r_occurrence IS RECORD (
        occurrence_id   NUMBER,
        room_id         NUMBER,
        faculty_id      NUMBER,
        slot_id         NUMBER,
        occurrence_date DATE,
        status          VARCHAR2(20)
    );

    TYPE t_occurrences IS TABLE OF r_occurrence;
    g_occurrences t_occurrences := t_occurrences();

    BEFORE STATEMENT IS
    BEGIN
        g_occurrences.DELETE;
    END BEFORE STATEMENT;

    BEFORE EACH ROW IS
    BEGIN
        IF :NEW.status = 'ACTIVE' THEN
            g_occurrences.EXTEND;
            g_occurrences(g_occurrences.LAST).occurrence_id   := :NEW.occurrence_id;
            g_occurrences(g_occurrences.LAST).room_id         := :NEW.room_id;
            g_occurrences(g_occurrences.LAST).faculty_id      := :NEW.faculty_id;
            g_occurrences(g_occurrences.LAST).slot_id         := :NEW.slot_id;
            g_occurrences(g_occurrences.LAST).occurrence_date := TRUNC(:NEW.occurrence_date);
            g_occurrences(g_occurrences.LAST).status          := :NEW.status;
        END IF;
    END BEFORE EACH ROW;

    AFTER STATEMENT IS
        v_room_clash_count    NUMBER;
        v_fac_clash_count     NUMBER;
        v_room_num            VARCHAR2(50);
        v_fac_name            VARCHAR2(100);
        v_slot_name           VARCHAR2(100);
        v_date_str            VARCHAR2(20);
    BEGIN
        FOR i IN 1..g_occurrences.COUNT LOOP
            v_date_str := TO_CHAR(g_occurrences(i).occurrence_date, 'YYYY-MM-DD');

            -- 1. Check for Room Double Allocation
            SELECT COUNT(*), MAX(r.room_number), MAX(ts.slot_name)
            INTO v_room_clash_count, v_room_num, v_slot_name
            FROM BOOKING_OCCURRENCE bo
            JOIN ROOM r ON bo.room_id = r.room_id
            JOIN TIME_SLOT ts ON bo.slot_id = ts.slot_id
            WHERE bo.room_id = g_occurrences(i).room_id
              AND bo.occurrence_date = g_occurrences(i).occurrence_date
              AND bo.slot_id = g_occurrences(i).slot_id
              AND bo.status = 'ACTIVE'
              AND (g_occurrences(i).occurrence_id IS NULL OR bo.occurrence_id <> g_occurrences(i).occurrence_id);

            IF v_room_clash_count > 0 THEN
                RAISE_APPLICATION_ERROR(-20001,
                    'Room Clash: Room ' || v_room_num || ' is already booked on ' ||
                    v_date_str || ' during ' || v_slot_name || '.');
            END IF;

            -- 2. Check for Faculty Clash (same faculty in two rooms at the same time)
            SELECT COUNT(*), MAX(f.first_name || ' ' || f.last_name), MAX(r.room_number)
            INTO v_fac_clash_count, v_fac_name, v_room_num
            FROM BOOKING_OCCURRENCE bo
            JOIN FACULTY f ON bo.faculty_id = f.faculty_id
            JOIN ROOM r ON bo.room_id = r.room_id
            WHERE bo.faculty_id = g_occurrences(i).faculty_id
              AND bo.occurrence_date = g_occurrences(i).occurrence_date
              AND bo.slot_id = g_occurrences(i).slot_id
              AND bo.status = 'ACTIVE'
              AND (g_occurrences(i).occurrence_id IS NULL OR bo.occurrence_id <> g_occurrences(i).occurrence_id);

            IF v_fac_clash_count > 0 THEN
                RAISE_APPLICATION_ERROR(-20002,
                    'Faculty Clash: Faculty member ' || v_fac_name || ' is already scheduled in room ' ||
                    v_room_num || ' on ' || v_date_str || ' during this time slot.');
            END IF;
        END LOOP;
    END AFTER STATEMENT;

END trg_prevent_booking_conflicts;
/
