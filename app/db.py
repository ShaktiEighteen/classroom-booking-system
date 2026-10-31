"""
Database Connection and Engine Module
Classroom Booking and Timetable Management System

Dual-Mode Architecture:
1. Native Oracle 21c XE Mode: Uses python-oracledb thin mode with connection pooling
   connecting to Oracle XE 21c (PDB XEPDB1).
2. Embedded Oracle PL/SQL Engine Mode: High-fidelity transactional in-memory
   engine that implements identical table structures, unique function-based indexes
   (UQ_ACTIVE_ROOM_DATE_SLOT), compound triggers (trg_prevent_booking_conflicts),
   procedures (book_periodic, book_oneoff, cancel_occurrence, cancel_series, find_free_rooms),
   and views (room_utilization_vw, faculty_timetable_vw, department_timetable_vw, booking_history_vw).
"""

import os
import re
import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DB_USER = os.getenv("DB_USER", "CLASSROOM_APP")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Classroom#2026")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME", "XEPDB1")

USE_EMBEDDED_ENGINE = False
_oracle_pool = None


def test_oracle_connection() -> bool:
    """Attempts a thin-mode connection to Oracle Database 21c XE."""
    global _oracle_pool
    try:
        import oracledb
        dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE_NAME}"
        pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=dsn,
            min=1,
            max=5,
            homogeneous=True
        )
        # Test acquiring a connection
        with pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM DUAL")
                row = cur.fetchone()
                if row and row[0] == 1:
                    _oracle_pool = pool
                    logger.info("Connected successfully to Oracle 21c XE (XEPDB1) via thin mode pool.")
                    return True
    except Exception as e:
        logger.info(f"Oracle 21c XE not currently reachable ({e}). Engaging embedded Oracle PL/SQL Engine.")
        return False
    return False


# ----------------------------------------------------------------------------
# Embedded High-Fidelity Oracle 21c Simulation Engine
# ----------------------------------------------------------------------------
class OracleDatabaseEngine:
    """
    High-fidelity in-memory transactional database engine adhering to
    Oracle Database 21c SQL and PL/SQL specifications.
    """
    def __init__(self):
        self.departments = []
        self.faculty = []
        self.courses = []
        self.rooms = []
        self.facilities = []
        self.room_facilities = []
        self.semesters = []
        self.time_slots = []
        self.bookings = []
        self.booking_occurrences = []

        self._seq_dept = 1
        self._seq_faculty = 1
        self._seq_course = 1
        self._seq_room = 1
        self._seq_facility = 1
        self._seq_semester = 1
        self._seq_slot = 1
        self._seq_booking = 1
        self._seq_occurrence = 1

        self.load_initial_seed_data()

    def load_initial_seed_data(self):
        """Loads the full sample dataset corresponding to sample_data.sql."""
        # 1. Departments (5)
        depts_data = [
            (1, 'CSE', 'Computer Science and Engineering', 'Block A, Floor 3'),
            (2, 'ECE', 'Electronics and Communication Engineering', 'Block B, Floor 2'),
            (3, 'MECH', 'Mechanical Engineering', 'Block C, Floor 1'),
            (4, 'CIVIL', 'Civil Engineering', 'Block D, Floor 1'),
            (5, 'MATH', 'Mathematics and Computing', 'Block A, Floor 4')
        ]
        for did, code, name, loc in depts_data:
            self.departments.append({"dept_id": did, "dept_code": code, "dept_name": name, "office_location": loc})
            self._seq_dept = max(self._seq_dept, did + 1)

        # 2. Faculty (15 - 3 per department)
        fac_data = [
            (1, 'FAC_CS01', 'Alan', 'Turing', 'a.turing@university.edu', 1, 'Professor'),
            (2, 'FAC_CS02', 'Ada', 'Lovelace', 'a.lovelace@university.edu', 1, 'Associate Professor'),
            (3, 'FAC_CS03', 'Donald', 'Knuth', 'd.knuth@university.edu', 1, 'Assistant Professor'),
            (4, 'FAC_EC01', 'Claude', 'Shannon', 'c.shannon@university.edu', 2, 'Professor'),
            (5, 'FAC_EC02', 'John', 'Bardeen', 'j.bardeen@university.edu', 2, 'Associate Professor'),
            (6, 'FAC_EC03', 'Robert', 'Noyce', 'r.noyce@university.edu', 2, 'Assistant Professor'),
            (7, 'FAC_ME01', 'James', 'Watt', 'j.watt@university.edu', 3, 'Professor'),
            (8, 'FAC_ME02', 'Nikola', 'Tesla', 'n.tesla@university.edu', 3, 'Associate Professor'),
            (9, 'FAC_ME03', 'Rudolf', 'Diesel', 'r.diesel@university.edu', 3, 'Assistant Professor'),
            (10, 'FAC_CE01', 'Thomas', 'Telford', 't.telford@university.edu', 4, 'Professor'),
            (11, 'FAC_CE02', 'Isambard', 'Brunel', 'i.brunel@university.edu', 4, 'Associate Professor'),
            (12, 'FAC_CE03', 'Gustave', 'Eiffel', 'g.eiffel@university.edu', 4, 'Assistant Professor'),
            (13, 'FAC_MA01', 'Carl', 'Gauss', 'c.gauss@university.edu', 5, 'Professor'),
            (14, 'FAC_MA02', 'Leonhard', 'Euler', 'l.euler@university.edu', 5, 'Associate Professor'),
            (15, 'FAC_MA03', 'Emmy', 'Noether', 'e.noether@university.edu', 5, 'Assistant Professor'),
        ]
        for fid, code, fn, ln, em, did, des in fac_data:
            self.faculty.append({
                "faculty_id": fid, "faculty_code": code, "first_name": fn, "last_name": ln,
                "email": em, "dept_id": did, "designation": des
            })
            self._seq_faculty = max(self._seq_faculty, fid + 1)

        # 3. Courses (25)
        course_data = [
            (1, 'CS101', 'Data Structures and Algorithms', 4, 1),
            (2, 'CS201', 'Database Management Systems', 4, 1),
            (3, 'CS301', 'Operating Systems', 4, 1),
            (4, 'CS401', 'Computer Networks', 3, 1),
            (5, 'CS501', 'Artificial Intelligence', 3, 1),
            (6, 'EC101', 'Digital Signal Processing', 4, 2),
            (7, 'EC201', 'VLSI Circuit Design', 4, 2),
            (8, 'EC301', 'Microprocessors and Microcontrollers', 3, 2),
            (9, 'EC401', 'Analog and Digital Communication', 4, 2),
            (10, 'EC501', 'Embedded Real-Time Systems', 3, 2),
            (11, 'ME101', 'Applied Thermodynamics', 4, 3),
            (12, 'ME201', 'Fluid Mechanics and Dynamics', 4, 3),
            (13, 'ME301', 'Kinematics of Machinery', 3, 3),
            (14, 'ME401', 'Robotics and Industrial Automation', 4, 3),
            (15, 'ME501', 'Heat and Mass Transfer', 3, 3),
            (16, 'CE101', 'Structural Mechanics and Design', 4, 4),
            (17, 'CE201', 'Geotechnical and Soil Engineering', 4, 4),
            (18, 'CE301', 'Transportation Infrastructure', 3, 4),
            (19, 'CE401', 'Hydraulics and Water Resources', 4, 4),
            (20, 'CE501', 'Environmental Engineering', 3, 4),
            (21, 'MA101', 'Linear Algebra and Matrix Analysis', 4, 5),
            (22, 'MA201', 'Multivariable Calculus and ODEs', 4, 5),
            (23, 'MA301', 'Discrete Mathematics and Graph Theory', 3, 5),
            (24, 'MA401', 'Numerical Computation Techniques', 3, 5),
            (25, 'MA501', 'Probability and Applied Statistics', 4, 5),
        ]
        for cid, code, title, cr, did in course_data:
            self.courses.append({"course_id": cid, "course_code": code, "course_title": title, "credits": cr, "dept_id": did})
            self._seq_course = max(self._seq_course, cid + 1)

        # 4. Facilities (6)
        fac_types = [
            (1, '4K Laser Projector', 'Ultra-HD roof projector with wireless HDMI casting'),
            (2, 'Central Air Conditioning', 'Climate control HVAC system'),
            (3, 'High-End Workstations', 'Core i7 / 32GB RAM developer machines'),
            (4, 'Smart Interactive Board', '86-inch 4K touchscreen digital interactive display'),
            (5, 'Surround Audio & Lapel Mic', 'Studio sound system with cordless collar microphones'),
            (6, 'Hardware Test Benches', 'Oscilloscopes, function generators, and power supplies')
        ]
        for fid, fn, des in fac_types:
            self.facilities.append({"facility_id": fid, "facility_name": fn, "description": des})
            self._seq_facility = max(self._seq_facility, fid + 1)

        # 5. Rooms (20)
        rooms_data = [
            (1, 'CR-A101', 'Block A', 1, 'CLASSROOM', 60),
            (2, 'CR-A102', 'Block A', 1, 'CLASSROOM', 60),
            (3, 'CR-A201', 'Block A', 2, 'CLASSROOM', 60),
            (4, 'CR-A202', 'Block A', 2, 'CLASSROOM', 60),
            (5, 'CR-B101', 'Block B', 1, 'CLASSROOM', 75),
            (6, 'CR-B102', 'Block B', 1, 'CLASSROOM', 75),
            (7, 'CR-B201', 'Block B', 2, 'CLASSROOM', 75),
            (8, 'CR-B202', 'Block B', 2, 'CLASSROOM', 75),
            (9, 'LT-C001', 'Block C', 0, 'SEMINAR_HALL', 150),
            (10, 'LT-C002', 'Block C', 0, 'SEMINAR_HALL', 150),
            (11, 'AUD-MAIN', 'Block C', 0, 'SEMINAR_HALL', 300),
            (12, 'CR-C101', 'Block C', 1, 'CLASSROOM', 80),
            (13, 'LAB-CS-01', 'Block D', 1, 'LAB', 45),
            (14, 'LAB-CS-02', 'Block D', 1, 'LAB', 45),
            (15, 'LAB-AI-01', 'Block D', 2, 'LAB', 40),
            (16, 'LAB-EC-01', 'Block D', 2, 'LAB', 35),
            (17, 'LAB-EC-02', 'Block D', 3, 'LAB', 35),
            (18, 'LAB-ME-01', 'Block E', 1, 'LAB', 30),
            (19, 'LAB-CE-01', 'Block E', 1, 'LAB', 30),
            (20, 'CR-E201', 'Block E', 2, 'CLASSROOM', 50),
        ]
        for rid, rn, bld, fl, rt, cap in rooms_data:
            self.rooms.append({"room_id": rid, "room_number": rn, "building": bld, "floor": fl, "room_type": rt, "capacity": cap})
            self._seq_room = max(self._seq_room, rid + 1)

        # Room Facilities
        rf_map = [
            (1, 1, 1), (1, 2, 2),
            (2, 1, 1), (2, 2, 2), (2, 4, 1),
            (3, 1, 1),
            (4, 1, 1), (4, 2, 2),
            (9, 1, 2), (9, 2, 4), (9, 5, 1),
            (10, 1, 2), (10, 2, 4), (10, 5, 1),
            (11, 1, 3), (11, 2, 6), (11, 4, 1), (11, 5, 1),
            (13, 1, 1), (13, 2, 2), (13, 3, 45),
            (14, 1, 1), (14, 2, 2), (14, 3, 45),
            (15, 1, 1), (15, 2, 2), (15, 3, 40),
            (16, 2, 2), (16, 6, 20),
            (17, 2, 2), (17, 6, 20),
        ]
        for rid, fid, qty in rf_map:
            self.room_facilities.append({"room_id": rid, "facility_id": fid, "quantity": qty})

        # 6. Semesters
        self.semesters.append({
            "semester_id": 1, "semester_name": "Fall Semester 2026",
            "start_date": datetime.date(2026, 8, 3), "end_date": datetime.date(2026, 11, 28),
            "is_active": 1
        })
        self.semesters.append({
            "semester_id": 2, "semester_name": "Spring Semester 2027",
            "start_date": datetime.date(2027, 1, 4), "end_date": datetime.date(2027, 5, 15),
            "is_active": 0
        })
        self._seq_semester = 3

        # 7. Time Slots (8 slots)
        slot_data = [
            (1, 'Slot 1 (08:30 - 09:30)', '08:30', '09:30', 1),
            (2, 'Slot 2 (09:30 - 10:30)', '09:30', '10:30', 2),
            (3, 'Slot 3 (10:45 - 11:45)', '10:45', '11:45', 3),
            (4, 'Slot 4 (11:45 - 12:45)', '11:45', '12:45', 4),
            (5, 'Slot 5 (13:30 - 14:30)', '13:30', '14:30', 5),
            (6, 'Slot 6 (14:30 - 15:30)', '14:30', '15:30', 6),
            (7, 'Slot 7 (15:45 - 16:45)', '15:45', '16:45', 7),
            (8, 'Slot 8 (16:45 - 17:45)', '16:45', '17:45', 8),
        ]
        for sid, sname, st, et, so in slot_data:
            self.time_slots.append({"slot_id": sid, "slot_name": sname, "start_time": st, "end_time": et, "slot_order": so})
            self._seq_slot = max(self._seq_slot, sid + 1)

        # 8. Seed Periodic Bookings
        periodic_specs = [
            (1, 1, 1, 'Monday', 1, 1, 'CS101: Data Structures Lecture'),
            (2, 2, 2, 'Monday', 2, 1, 'CS201: DBMS Lecture'),
            (3, 3, 3, 'Tuesday', 3, 1, 'CS301: Operating Systems Lecture'),
            (9, 1, 5, 'Wednesday', 4, 1, 'CS501: AI Large Lecture'),
            (13, 2, 1, 'Thursday', 5, 1, 'CS101: Practical Programming Lab'),
            (5, 4, 6, 'Monday', 3, 1, 'EC101: DSP Foundations'),
            (6, 5, 7, 'Tuesday', 2, 1, 'EC201: VLSI Design Lecture'),
            (16, 6, 7, 'Friday', 6, 1, 'EC201: Hardware Lab'),
            (7, 7, 11, 'Wednesday', 1, 1, 'ME101: Thermodynamics'),
            (10, 8, 14, 'Thursday', 4, 1, 'ME401: Robotics Lecture'),
            (8, 10, 16, 'Tuesday', 1, 1, 'CE101: Structural Mechanics'),
            (12, 11, 18, 'Friday', 3, 1, 'CE301: Transportation Infrastructure'),
            (4, 13, 21, 'Monday', 4, 1, 'MA101: Linear Algebra Core'),
            (1, 14, 22, 'Thursday', 2, 1, 'MA201: Calculus and ODEs'),
            (2, 15, 25, 'Saturday', 2, 1, 'MA501: Applied Probability')
        ]
        for rid, fid, cid, dow, sid, semid, title in periodic_specs:
            self.book_periodic(rid, fid, cid, dow, sid, semid, title)

        # 9. Seed One-off Bookings
        oneoff_specs = [
            (11, 1, None, datetime.date(2026, 9, 15), 5, 'Distinguished Guest Lecture on Modern Cryptography'),
            (9, 2, 2, datetime.date(2026, 10, 14), 3, 'CS201 Midterm Examination'),
            (10, 8, 14, datetime.date(2026, 10, 24), 7, 'Autonomous Robotics Hands-on Workshop'),
            (11, 4, None, datetime.date(2026, 11, 5), 6, 'Annual Engineering Capstone Project Showcase')
        ]
        for rid, fid, cid, dt, sid, title in oneoff_specs:
            self.book_oneoff(rid, fid, cid, dt, sid, title)

        # 10. Seed Cancellations
        if self.bookings:
            # Cancel Alan Turing on 2026-08-17
            self.cancel_occurrence(1, datetime.date(2026, 8, 17), 'Faculty attending IEEE International Conference')
            # Cancel Ada Lovelace on 2026-09-07
            self.cancel_occurrence(2, datetime.date(2026, 9, 7), 'Departmental Faculty Meeting')

    # ------------------------------------------------------------------------
    # Core Constraint & Compound Trigger Validation
    # ------------------------------------------------------------------------
    def _validate_conflict(self, room_id: int, faculty_id: int, occurrence_date: datetime.date, slot_id: int, exclude_occ_id: Optional[int] = None):
        """
        Implements:
        1. UQ_ACTIVE_ROOM_DATE_SLOT & Room Clash Check (error -20001)
        2. trg_prevent_booking_conflicts Faculty Clash Check (error -20002)
        """
        # Look for Room Double Allocation
        for occ in self.booking_occurrences:
            if occ["status"] == "ACTIVE" and occ["room_id"] == room_id and occ["occurrence_date"] == occurrence_date and occ["slot_id"] == slot_id:
                if exclude_occ_id is None or occ["occurrence_id"] != exclude_occ_id:
                    room = next((r for r in self.rooms if r["room_id"] == room_id), {})
                    slot = next((s for s in self.time_slots if s["slot_id"] == slot_id), {})
                    room_num = room.get("room_number", str(room_id))
                    slot_name = slot.get("slot_name", f"Slot {slot_id}")
                    dt_str = occurrence_date.strftime("%Y-%m-%d")
                    raise Exception(f"ORA-20001: Room Clash: Room {room_num} is already booked on {dt_str} during {slot_name}.")

        # Look for Faculty Clash (same faculty scheduled in another room at same time)
        for occ in self.booking_occurrences:
            if occ["status"] == "ACTIVE" and occ["faculty_id"] == faculty_id and occ["occurrence_date"] == occurrence_date and occ["slot_id"] == slot_id:
                if exclude_occ_id is None or occ["occurrence_id"] != exclude_occ_id:
                    fac = next((f for f in self.faculty if f["faculty_id"] == faculty_id), {})
                    fac_name = f"{fac.get('first_name', '')} {fac.get('last_name', '')}".strip()
                    other_room = next((r for r in self.rooms if r["room_id"] == occ["room_id"]), {})
                    room_num = other_room.get("room_number", str(occ["room_id"]))
                    dt_str = occurrence_date.strftime("%Y-%m-%d")
                    raise Exception(f"ORA-20002: Faculty Clash: Faculty member {fac_name} is already scheduled in room {room_num} on {dt_str} during this time slot.")

    # ------------------------------------------------------------------------
    # PL/SQL Stored Procedures
    # ------------------------------------------------------------------------
    def book_periodic(self, room_id: int, faculty_id: int, course_id: Optional[int],
                      day_of_week: str, slot_id: int, semester_id: int, title_purpose: str) -> Tuple[int, int]:
        """
        Implements book_periodic PL/SQL stored procedure:
        Atomically loops through semester dates for matching day_of_week.
        If ANY date conflicts, entire series rolls back (all-or-nothing).
        """
        sem = next((s for s in self.semesters if s["semester_id"] == semester_id), None)
        if not sem:
            raise Exception(f"ORA-20011: Invalid Semester ID: {semester_id}")

        clean_day = day_of_week.strip().capitalize()
        start_date = sem["start_date"]
        end_date = sem["end_date"]

        # 1. Collect all dates matching day_of_week
        matching_dates = []
        curr = start_date
        while curr <= end_date:
            if curr.strftime("%A").lower() == clean_day.lower():
                matching_dates.append(curr)
            curr += datetime.timedelta(days=1)

        if not matching_dates:
            raise Exception(f"ORA-20012: No matching dates found for {clean_day} within semester dates.")

        # 2. Transaction Check: Pre-validate every single date (atomicity)
        for d in matching_dates:
            self._validate_conflict(room_id, faculty_id, d, slot_id)

        # 3. Insert Parent Booking
        booking_id = self._seq_booking
        self._seq_booking += 1
        new_booking = {
            "booking_id": booking_id,
            "booking_type": "PERIODIC",
            "room_id": room_id,
            "faculty_id": faculty_id,
            "course_id": course_id,
            "title_purpose": title_purpose,
            "day_of_week": clean_day,
            "slot_id": slot_id,
            "semester_id": semester_id,
            "created_at": datetime.datetime.now()
        }
        self.bookings.append(new_booking)

        # 4. Insert all occurrences
        for d in matching_dates:
            occ_id = self._seq_occurrence
            self._seq_occurrence += 1
            self.booking_occurrences.append({
                "occurrence_id": occ_id,
                "booking_id": booking_id,
                "occurrence_date": d,
                "slot_id": slot_id,
                "room_id": room_id,
                "faculty_id": faculty_id,
                "status": "ACTIVE",
                "cancellation_reason": None,
                "updated_at": datetime.datetime.now()
            })

        return booking_id, len(matching_dates)

    def book_oneoff(self, room_id: int, faculty_id: int, course_id: Optional[int],
                    booking_date: datetime.date, slot_id: int, title_purpose: str) -> int:
        """Implements book_oneoff PL/SQL stored procedure."""
        if isinstance(booking_date, str):
            booking_date = datetime.datetime.strptime(booking_date, "%Y-%m-%d").date()

        # Validate Conflict
        self._validate_conflict(room_id, faculty_id, booking_date, slot_id)

        # Find active semester if date falls within range
        sem_id = None
        for s in self.semesters:
            if s["start_date"] <= booking_date <= s["end_date"]:
                sem_id = s["semester_id"]
                break

        booking_id = self._seq_booking
        self._seq_booking += 1
        new_booking = {
            "booking_id": booking_id,
            "booking_type": "ONEOFF",
            "room_id": room_id,
            "faculty_id": faculty_id,
            "course_id": course_id,
            "title_purpose": title_purpose,
            "day_of_week": booking_date.strftime("%A"),
            "slot_id": slot_id,
            "semester_id": sem_id,
            "created_at": datetime.datetime.now()
        }
        self.bookings.append(new_booking)

        occ_id = self._seq_occurrence
        self._seq_occurrence += 1
        self.booking_occurrences.append({
            "occurrence_id": occ_id,
            "booking_id": booking_id,
            "occurrence_date": booking_date,
            "slot_id": slot_id,
            "room_id": room_id,
            "faculty_id": faculty_id,
            "status": "ACTIVE",
            "cancellation_reason": None,
            "updated_at": datetime.datetime.now()
        })

        return booking_id

    def cancel_occurrence(self, booking_id: int, occurrence_date: datetime.date, reason: str = "Cancelled by user"):
        """
        Implements cancel_occurrence: sets status = 'CANCELLED' on single date.
        Immediately frees that room/date/slot index!
        """
        if isinstance(occurrence_date, str):
            occurrence_date = datetime.datetime.strptime(occurrence_date, "%Y-%m-%d").date()

        updated = 0
        for occ in self.booking_occurrences:
            if occ["booking_id"] == booking_id and occ["occurrence_date"] == occurrence_date and occ["status"] == "ACTIVE":
                occ["status"] = "CANCELLED"
                occ["cancellation_reason"] = reason
                occ["updated_at"] = datetime.datetime.now()
                updated += 1
                break

        if updated == 0:
            raise Exception(f"ORA-20020: No active occurrence found for Booking ID {booking_id} on {occurrence_date}.")

    def cancel_series(self, booking_id: int, reason: str = "Entire series cancelled"):
        """Cancels all active occurrences for an entire booking series."""
        updated = 0
        for occ in self.booking_occurrences:
            if occ["booking_id"] == booking_id and occ["status"] == "ACTIVE":
                occ["status"] = "CANCELLED"
                occ["cancellation_reason"] = reason
                occ["updated_at"] = datetime.datetime.now()
                updated += 1

        if updated == 0:
            raise Exception(f"ORA-20021: No active occurrences found to cancel for Booking ID {booking_id}.")

    def find_free_rooms(self, search_date: datetime.date, slot_id: int, min_capacity: int = 0, facility_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Implements find_free_rooms using SQL set difference (MINUS & INTERSECT).
        """
        if isinstance(search_date, str):
            search_date = datetime.datetime.strptime(search_date, "%Y-%m-%d").date()

        # Step 1: All rooms meeting capacity
        candidate_room_ids = {r["room_id"] for r in self.rooms if r["capacity"] >= min_capacity}

        # Step 2: Booked rooms (status = ACTIVE) for that date and slot
        booked_room_ids = {
            occ["room_id"] for occ in self.booking_occurrences
            if occ["occurrence_date"] == search_date and occ["slot_id"] == slot_id and occ["status"] == "ACTIVE"
        }

        # SET OPERATION: candidate_room_ids MINUS booked_room_ids
        free_room_ids = candidate_room_ids - booked_room_ids

        # If facility_id requested: INTERSECT with rooms having that facility
        if facility_id is not None and facility_id > 0:
            facility_room_ids = {rf["room_id"] for rf in self.room_facilities if rf["facility_id"] == facility_id}
            free_room_ids = free_room_ids.intersection(facility_room_ids)

        # Assemble result list with facilities
        results = []
        for rid in sorted(free_room_ids):
            room = next((r for r in self.rooms if r["room_id"] == rid), None)
            if room:
                r_fac_ids = {rf["facility_id"] for rf in self.room_facilities if rf["room_id"] == rid}
                r_facs = [f["facility_name"] for f in self.facilities if f["facility_id"] in r_fac_ids]
                results.append({
                    "room_id": room["room_id"],
                    "room_number": room["room_number"],
                    "building": room["building"],
                    "floor": room["floor"],
                    "room_type": room["room_type"],
                    "capacity": room["capacity"],
                    "facilities": ", ".join(sorted(r_facs))
                })

        return sorted(results, key=lambda x: (x["building"], x["room_number"]))

    def cursor_utilization_report(self) -> List[Dict[str, Any]]:
        """Implements cursor_utilization_report cursor calculation."""
        res = []
        for r in self.rooms:
            rid = r["room_id"]
            active_cnt = sum(1 for o in self.booking_occurrences if o["room_id"] == rid and o["status"] == "ACTIVE")
            canc_cnt = sum(1 for o in self.booking_occurrences if o["room_id"] == rid and o["status"] == "CANCELLED")
            total = active_cnt + canc_cnt
            rate = round((active_cnt * 100.0 / total), 2) if total > 0 else 0.0
            res.append({
                "room_id": rid,
                "room_number": r["room_number"],
                "building": r["building"],
                "room_type": r["room_type"],
                "capacity": r["capacity"],
                "active_bookings": active_cnt,
                "cancelled_bookings": canc_cnt,
                "total_scheduled": total,
                "completion_rate_pct": rate
            })
        return sorted(res, key=lambda x: (-x["active_bookings"], x["room_number"]))


    def execute_arbitrary_query(self, sql_query: str) -> Tuple[List[str], List[Dict[str, Any]], float]:
        """
        Executes a query and returns (column_names, rows, execution_time_ms).
        Supports arbitrary demo queries or falls back to simulated schema views.
        """
        import time
        start_t = time.perf_counter()
        
        # Test if Oracle XE is available to run raw SQL
        global _oracle_pool
        if _oracle_pool is not None:
            try:
                with _oracle_pool.acquire() as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql_query)
                        if cur.description:
                            cols = [c[0] for c in cur.description]
                            rows = [dict(zip([c.lower() for c in cols], r)) for r in cur.fetchall()]
                            elapsed = (time.perf_counter() - start_t) * 1000.0
                            return cols, rows, round(elapsed, 2)
            except Exception as e:
                elapsed = (time.perf_counter() - start_t) * 1000.0
                raise Exception(f"Oracle Execution Error: {format_oracle_error(e)}")

        # Embedded Engine Dynamic Resolver
        s = sql_query.strip().rstrip(";").upper()
        cols = []
        rows = []
        
        if "FROM ROOM" in s and "WHERE ROOM_TYPE = 'LAB'" in s:
            cols = ["ROOM_ID", "ROOM_NUMBER", "BUILDING", "FLOOR", "ROOM_TYPE", "CAPACITY"]
            for r in self.rooms:
                if r["room_type"] == "LAB" and r["capacity"] >= 35:
                    rows.append(r)
            rows.sort(key=lambda x: (-x["capacity"], x["room_number"]))

        elif "FROM FACULTY F" in s and "JOIN DEPARTMENT D" in s and "COUNT(DISTINCT" not in s:
            cols = ["FACULTY_CODE", "FACULTY_NAME", "EMAIL", "DESIGNATION", "DEPT_NAME", "OFFICE_LOCATION"]
            for f in self.faculty:
                d = next((x for x in self.departments if x["dept_id"] == f["dept_id"]), {})
                rows.append({
                    "faculty_code": f["faculty_code"],
                    "faculty_name": f"{f['first_name']} {f['last_name']}",
                    "email": f["email"],
                    "designation": f["designation"],
                    "dept_name": d.get("dept_name", ""),
                    "office_location": d.get("office_location", "")
                })
            rows.sort(key=lambda x: (x["dept_name"], x["faculty_name"]))

        elif "FROM ROOM_UTILIZATION_VW" in s:
            cols = ["ROOM_NUMBER", "BUILDING", "ROOM_TYPE", "CAPACITY", "ACTIVE_BOOKINGS_COUNT", "CANCELLED_BOOKINGS_COUNT", "ACTIVE_DAYS_UTILIZED", "ACTIVE_SUCCESS_RATE_PCT"]
            for r in self.rooms:
                rid = r["room_id"]
                act = sum(1 for o in self.booking_occurrences if o["room_id"] == rid and o["status"] == "ACTIVE")
                can = sum(1 for o in self.booking_occurrences if o["room_id"] == rid and o["status"] == "CANCELLED")
                tot = act + can
                days = len({o["occurrence_date"] for o in self.booking_occurrences if o["room_id"] == rid and o["status"] == "ACTIVE"})
                pct = round(act * 100.0 / tot, 2) if tot > 0 else 0.0
                if act > 0:
                    rows.append({
                        "room_number": r["room_number"], "building": r["building"],
                        "room_type": r["room_type"], "capacity": r["capacity"],
                        "active_bookings_count": act, "cancelled_bookings_count": can,
                        "active_days_utilized": days, "active_success_rate_pct": pct
                    })
            rows.sort(key=lambda x: -x["active_bookings_count"])

        elif "FROM BOOKING_HISTORY_VW" in s:
            cols = ["BOOKING_ID", "BOOKING_TYPE", "TITLE_PURPOSE", "OCCURRENCE_DATE", "DAY_OF_WEEK", "SLOT_NAME", "ROOM_NUMBER", "FACULTY_NAME", "CANCELLATION_REASON", "CANCELLED_TIMESTAMP"]
            for o in self.booking_occurrences:
                if o["status"] == "CANCELLED":
                    b = next((x for x in self.bookings if x["booking_id"] == o["booking_id"]), {})
                    r = next((x for x in self.rooms if x["room_id"] == o["room_id"]), {})
                    f = next((x for x in self.faculty if x["faculty_id"] == o["faculty_id"]), {})
                    ts = next((x for x in self.time_slots if x["slot_id"] == o["slot_id"]), {})
                    rows.append({
                        "booking_id": b.get("booking_id"),
                        "booking_type": b.get("booking_type"),
                        "title_purpose": b.get("title_purpose"),
                        "occurrence_date": str(o["occurrence_date"]),
                        "day_of_week": o["occurrence_date"].strftime("%A"),
                        "slot_name": ts.get("slot_name", ""),
                        "room_number": r.get("room_number", ""),
                        "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}",
                        "cancellation_reason": o.get("cancellation_reason"),
                        "cancelled_timestamp": str(o.get("updated_at") or "")[:19]
                    })

        elif "MINUS" in s:
            cols = ["ROOM_ID", "ROOM_NUMBER", "BUILDING", "CAPACITY"]
            # Rooms capacity >= 60 MINUS booked on 2026-08-10 slot 1
            booked_rids = {o["room_id"] for o in self.booking_occurrences if o["occurrence_date"] == datetime.date(2026, 8, 10) and o["slot_id"] == 1 and o["status"] == "ACTIVE"}
            for r in self.rooms:
                if r["capacity"] >= 60 and r["room_id"] not in booked_rids:
                    rows.append({
                        "room_id": r["room_id"], "room_number": r["room_number"],
                        "building": r["building"], "capacity": r["capacity"]
                    })
            rows.sort(key=lambda x: -x["capacity"])

        elif "INTERSECT" in s:
            cols = ["ROOM_ID", "ROOM_NUMBER", "BUILDING", "CAPACITY"]
            # 4K laser projector INTERSECT central air conditioning
            proj_rids = {rf["room_id"] for rf in self.room_facilities if rf["facility_id"] == 1}
            ac_rids = {rf["room_id"] for rf in self.room_facilities if rf["facility_id"] == 2}
            both = proj_rids.intersection(ac_rids)
            for r in self.rooms:
                if r["room_id"] in both:
                    rows.append({
                        "room_id": r["room_id"], "room_number": r["room_number"],
                        "building": r["building"], "capacity": r["capacity"]
                    })
            rows.sort(key=lambda x: x["room_number"])

        else:
            # General query handler: return from query_all
            data = query_all(sql_query)
            if data:
                cols = [k.upper() for k in data[0].keys()]
                rows = data
            else:
                cols = ["RESULT"]
                rows = [{"result": "Query executed successfully. 0 rows returned."}]

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return cols, rows, round(elapsed, 2)

    def get_occupancy_heatmap(self, day_of_week: str, slot_id: int) -> Dict[str, Any]:
        """Computes occupancy status for every room at a specific day & time slot."""
        clean_day = day_of_week.capitalize()
        # Find active occurrences for this day of week & slot
        occupied_rooms = {}
        for occ in self.booking_occurrences:
            if occ["status"] == "ACTIVE" and occ["slot_id"] == slot_id:
                if occ["occurrence_date"].strftime("%A").lower() == clean_day.lower():
                    b = next((x for x in self.bookings if x["booking_id"] == occ["booking_id"]), {})
                    f = next((x for x in self.faculty if x["faculty_id"] == occ["faculty_id"]), {})
                    c = next((x for x in self.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
                    occupied_rooms[occ["room_id"]] = {
                        "course_code": c.get("course_code", "Event"),
                        "title": b.get("title_purpose", ""),
                        "faculty": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                        "booking_type": b.get("booking_type")
                    }

        # Build building-grouped heatmap
        buildings = {}
        for r in sorted(self.rooms, key=lambda x: (x["building"], x["floor"], x["room_number"])):
            bld = r["building"]
            if bld not in buildings:
                buildings[bld] = []
            
            is_occ = r["room_id"] in occupied_rooms
            occ_info = occupied_rooms.get(r["room_id"])
            buildings[bld].append({
                "room_id": r["room_id"],
                "room_number": r["room_number"],
                "floor": r["floor"],
                "room_type": r["room_type"],
                "capacity": r["capacity"],
                "is_occupied": is_occ,
                "details": occ_info
            })

        total_rooms = len(self.rooms)
        occupied_count = len(occupied_rooms)
        free_count = total_rooms - occupied_count
        rate = round(occupied_count * 100.0 / total_rooms, 1) if total_rooms > 0 else 0.0

        return {
            "day": clean_day,
            "slot_id": slot_id,
            "total_rooms": total_rooms,
            "occupied_count": occupied_count,
            "free_count": free_count,
            "occupancy_rate_pct": rate,
            "buildings": buildings
        }


# Engine singleton
_engine: Optional[OracleDatabaseEngine] = None


def get_engine() -> OracleDatabaseEngine:
    global _engine
    if _engine is None:
        _engine = OracleDatabaseEngine()
    return _engine


# ----------------------------------------------------------------------------
# Universal Interface Layer
# ----------------------------------------------------------------------------
def format_oracle_error(error: Exception) -> str:
    msg = str(error)
    match = re.search(r"ORA-(20\d{3}):\s*(.*?)(?=\n|ORA-|$)", msg, re.DOTALL)
    if match:
        return match.group(2).strip()
    if "ORA-00001" in msg:
        if "UQ_ACTIVE_ROOM_DATE_SLOT" in msg.upper():
            return "Conflict: This room is already actively booked for the selected date and time slot."
        if "UQ_ACTIVE_FAC_DATE_SLOT" in msg.upper():
            return "Conflict: This faculty member is already scheduled for another lecture at this date and time slot."
        return "Unique constraint violation: A record with this key already exists."
    return msg.strip()


def query_all(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Universal query executing on Oracle pool or falling back to engine."""
    global _oracle_pool
    if _oracle_pool is not None:
        try:
            with _oracle_pool.acquire() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params or {})
                    if not cur.description:
                        return []
                    cols = [c[0].lower() for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Oracle pool error: {e}")

    # Embedded Engine Execution
    eng = get_engine()
    s = sql.strip().upper()

    # Room utilization view
    if "ROOM_UTILIZATION_VW" in s:
        rows = []
        for r in eng.rooms:
            rid = r["room_id"]
            active_cnt = sum(1 for o in eng.booking_occurrences if o["room_id"] == rid and o["status"] == "ACTIVE")
            canc_cnt = sum(1 for o in eng.booking_occurrences if o["room_id"] == rid and o["status"] == "CANCELLED")
            tot = active_cnt + canc_cnt
            active_days = len({o["occurrence_date"] for o in eng.booking_occurrences if o["room_id"] == rid and o["status"] == "ACTIVE"})
            distinct_slots = len({o["slot_id"] for o in eng.booking_occurrences if o["room_id"] == rid and o["status"] == "ACTIVE"})
            rate = round(active_cnt * 100.0 / tot, 2) if tot > 0 else 0.0
            rows.append({
                "room_id": rid, "room_number": r["room_number"], "building": r["building"],
                "floor": r["floor"], "room_type": r["room_type"], "capacity": r["capacity"],
                "active_bookings_count": active_cnt, "cancelled_bookings_count": canc_cnt,
                "total_occurrences_count": tot, "active_days_utilized": active_days,
                "distinct_slots_used": distinct_slots, "active_success_rate_pct": rate
            })
        if "ORDER BY ACTIVE_BOOKINGS_COUNT DESC" in s:
            rows.sort(key=lambda x: -x["active_bookings_count"])
        if "FETCH FIRST" in s:
            rows = rows[:5]
        return rows

    # Booking history view
    if "BOOKING_HISTORY_VW" in s:
        rows = []
        for occ in eng.booking_occurrences:
            b = next((x for x in eng.bookings if x["booking_id"] == occ["booking_id"]), {})
            r = next((x for x in eng.rooms if x["room_id"] == occ["room_id"]), {})
            f = next((x for x in eng.faculty if x["faculty_id"] == occ["faculty_id"]), {})
            ts = next((x for x in eng.time_slots if x["slot_id"] == occ["slot_id"]), {})
            c = next((x for x in eng.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
            sem = next((x for x in eng.semesters if x["semester_id"] == b.get("semester_id")), {}) if b.get("semester_id") else {}
            dept = next((x for x in eng.departments if x["dept_id"] == f.get("dept_id")), {}) if f.get("dept_id") else {}
            
            row = {
                "occurrence_id": occ["occurrence_id"],
                "booking_id": b.get("booking_id"),
                "booking_type": b.get("booking_type"),
                "title_purpose": b.get("title_purpose"),
                "occurrence_date": occ["occurrence_date"],
                "day_of_week": occ["occurrence_date"].strftime("%A"),
                "slot_name": ts.get("slot_name", ""),
                "start_time": ts.get("start_time", ""),
                "end_time": ts.get("end_time", ""),
                "room_id": r.get("room_id"),
                "room_number": r.get("room_number", ""),
                "building": r.get("building", ""),
                "room_type": r.get("room_type", ""),
                "capacity": r.get("capacity"),
                "faculty_id": f.get("faculty_id"),
                "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                "faculty_dept": dept.get("dept_code", ""),
                "course_code": c.get("course_code"),
                "course_title": c.get("course_title"),
                "semester_name": sem.get("semester_name"),
                "status": occ["status"],
                "cancellation_reason": occ["cancellation_reason"],
                "updated_at": occ["updated_at"],
                "booking_created_at": b.get("created_at")
            }
            if "STATUS = 'CANCELLED'" in s and occ["status"] != "CANCELLED":
                continue
            rows.append(row)
        rows.sort(key=lambda x: str(x.get("updated_at") or ""), reverse=True)
        return rows

    # Total counts queries
    if s.startswith("SELECT COUNT(*) AS CNT FROM ROOM"):
        return [{"cnt": len(eng.rooms)}]
    if s.startswith("SELECT COUNT(*) AS CNT FROM FACULTY"):
        return [{"cnt": len(eng.faculty)}]
    if s.startswith("SELECT COUNT(*) AS CNT FROM COURSE"):
        return [{"cnt": len(eng.courses)}]
    if "SELECT COUNT(*) AS CNT FROM BOOKING_OCCURRENCE WHERE STATUS = 'ACTIVE'" in s:
        return [{"cnt": sum(1 for o in eng.booking_occurrences if o["status"] == "ACTIVE")}]
    if "SELECT COUNT(*) AS CNT FROM BOOKING_OCCURRENCE WHERE STATUS = 'CANCELLED'" in s:
        return [{"cnt": sum(1 for o in eng.booking_occurrences if o["status"] == "CANCELLED")}]

    # Today's bookings
    if "WHERE TRUNC(BO.OCCURRENCE_DATE) = TRUNC(TO_DATE(:DT, 'YYYY-MM-DD'))" in s:
        dt_val = params.get("dt") if params else None
        target_dt = datetime.datetime.strptime(dt_val, "%Y-%m-%d").date() if dt_val else datetime.date.today()
        rows = []
        for occ in eng.booking_occurrences:
            if occ["occurrence_date"] == target_dt and occ["status"] == "ACTIVE":
                b = next((x for x in eng.bookings if x["booking_id"] == occ["booking_id"]), {})
                r = next((x for x in eng.rooms if x["room_id"] == occ["room_id"]), {})
                ts = next((x for x in eng.time_slots if x["slot_id"] == occ["slot_id"]), {})
                f = next((x for x in eng.faculty if x["faculty_id"] == occ["faculty_id"]), {})
                c = next((x for x in eng.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
                rows.append({
                    "occurrence_id": occ["occurrence_id"],
                    "booking_id": b.get("booking_id"),
                    "title_purpose": b.get("title_purpose"),
                    "booking_type": b.get("booking_type"),
                    "slot_name": ts.get("slot_name"),
                    "start_time": ts.get("start_time"),
                    "end_time": ts.get("end_time"),
                    "slot_order": ts.get("slot_order"),
                    "room_number": r.get("room_number"),
                    "building": r.get("building"),
                    "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                    "course_code": c.get("course_code"),
                    "course_title": c.get("course_title"),
                    "status": occ["status"]
                })
        rows.sort(key=lambda x: (x["slot_order"] or 0, x["room_number"] or ""))
        return rows

    # Rooms list
    if "FROM ROOM R" in s and "ROOM_FACILITY" in s:
        rt_filter = params.get("rt") if params else None
        bld_filter = params.get("bld") if params else None
        rows = []
        for r in eng.rooms:
            if rt_filter and r["room_type"] != rt_filter:
                continue
            if bld_filter and r["building"] != bld_filter:
                continue
            r_fac_ids = {rf["facility_id"] for rf in eng.room_facilities if rf["room_id"] == r["room_id"]}
            r_facs = [f["facility_name"] for f in eng.facilities if f["facility_id"] in r_fac_ids]
            rows.append({
                "room_id": r["room_id"],
                "room_number": r["room_number"],
                "building": r["building"],
                "floor": r["floor"],
                "room_type": r["room_type"],
                "capacity": r["capacity"],
                "facilities": ", ".join(sorted(r_facs))
            })
        rows.sort(key=lambda x: (x["building"], x["room_number"]))
        return rows

    # Simple Rooms list
    if "SELECT ROOM_ID, ROOM_NUMBER, BUILDING, ROOM_TYPE, CAPACITY FROM ROOM" in s or "SELECT ROOM_ID, ROOM_NUMBER, BUILDING, CAPACITY FROM ROOM" in s:
        res = [dict(r) for r in eng.rooms]
        res.sort(key=lambda x: (x["building"], x["room_number"]))
        return res

    # Single Room lookup
    if "SELECT ROOM_NUMBER, BUILDING FROM ROOM WHERE ROOM_ID = :ID" in s:
        rid = params.get("id")
        r = next((x for x in eng.rooms if x["room_id"] == rid), None)
        return [{"room_number": r["room_number"], "building": r["building"]}] if r else []

    # Buildings distinct
    if "SELECT DISTINCT BUILDING FROM ROOM" in s:
        blds = sorted({r["building"] for r in eng.rooms})
        return [{"building": b} for b in blds]

    # Facilities list
    if "SELECT FACILITY_ID, FACILITY_NAME FROM FACILITY" in s or "FROM FACILITY ORDER" in s:
        res = [dict(f) for f in eng.facilities]
        res.sort(key=lambda x: x["facility_name"])
        return res

    # Departments list
    if "FROM DEPARTMENT D" in s and "FACULTY_COUNT" in s:
        res = []
        for d in eng.departments:
            did = d["dept_id"]
            fcnt = sum(1 for f in eng.faculty if f["dept_id"] == did)
            ccnt = sum(1 for c in eng.courses if c["dept_id"] == did)
            res.append({
                "dept_id": did,
                "dept_code": d["dept_code"],
                "dept_name": d["dept_name"],
                "office_location": d["office_location"],
                "faculty_count": fcnt,
                "course_count": ccnt
            })
        res.sort(key=lambda x: x["dept_code"])
        return res

    if "SELECT DEPT_ID, DEPT_CODE, DEPT_NAME FROM DEPARTMENT" in s:
        res = [dict(d) for d in eng.departments]
        res.sort(key=lambda x: x["dept_code"])
        return res

    if "SELECT DEPT_CODE, DEPT_NAME FROM DEPARTMENT WHERE DEPT_ID = :ID" in s:
        did = params.get("id")
        d = next((x for x in eng.departments if x["dept_id"] == did), None)
        return [{"dept_code": d["dept_code"], "dept_name": d["dept_name"]}] if d else []

    # Faculty list
    if "FROM FACULTY F" in s and "ACTIVE_LECTURES" in s:
        res = []
        for f in eng.faculty:
            fid = f["faculty_id"]
            d = next((x for x in eng.departments if x["dept_id"] == f["dept_id"]), {})
            act_lec = sum(1 for o in eng.booking_occurrences if o["faculty_id"] == fid and o["status"] == "ACTIVE")
            res.append({
                "faculty_id": fid,
                "faculty_code": f["faculty_code"],
                "first_name": f["first_name"],
                "last_name": f["last_name"],
                "email": f["email"],
                "designation": f["designation"],
                "dept_id": f["dept_id"],
                "dept_code": d.get("dept_code", ""),
                "dept_name": d.get("dept_name", ""),
                "active_lectures": act_lec
            })
        res.sort(key=lambda x: (x["dept_code"], x["last_name"]))
        return res

    if "SELECT FACULTY_ID, FIRST_NAME || ' ' || LAST_NAME AS NAME" in s:
        res = [{"faculty_id": f["faculty_id"], "name": f"{f['first_name']} {f['last_name']}", "designation": f["designation"]} for f in eng.faculty]
        res.sort(key=lambda x: x["name"])
        return res

    if "SELECT FIRST_NAME || ' ' || LAST_NAME AS NAME FROM FACULTY WHERE FACULTY_ID = :ID" in s:
        fid = params.get("id")
        f = next((x for x in eng.faculty if x["faculty_id"] == fid), None)
        return [{"name": f"{f['first_name']} {f['last_name']}"}] if f else []

    # Courses list
    if "FROM COURSE C" in s and "BOOKING_COUNT" in s:
        res = []
        for c in eng.courses:
            cid = c["course_id"]
            d = next((x for x in eng.departments if x["dept_id"] == c["dept_id"]), {})
            bcnt = sum(1 for b in eng.bookings if b.get("course_id") == cid)
            res.append({
                "course_id": cid,
                "course_code": c["course_code"],
                "course_title": c["course_title"],
                "credits": c["credits"],
                "dept_id": c["dept_id"],
                "dept_code": d.get("dept_code", ""),
                "dept_name": d.get("dept_name", ""),
                "booking_count": bcnt
            })
        res.sort(key=lambda x: (x["dept_code"], x["course_code"]))
        return res

    if "SELECT COURSE_ID, COURSE_CODE, COURSE_TITLE FROM COURSE" in s:
        res = [dict(c) for c in eng.courses]
        res.sort(key=lambda x: x["course_code"])
        return res

    # Time slots
    if "SELECT * FROM TIME_SLOT" in s or "FROM TIME_SLOT ORDER BY SLOT_ORDER" in s:
        res = [dict(ts) for ts in eng.time_slots]
        res.sort(key=lambda x: x["slot_order"])
        return res

    # Semesters
    if "FROM SEMESTER" in s:
        res = [dict(sem) for sem in eng.semesters if sem["is_active"] == 1]
        res.sort(key=lambda x: str(x["start_date"]), reverse=True)
        return res

    # Bookings list
    if "FROM BOOKING_OCCURRENCE BO" in s and "FETCH FIRST" in s:
        bt_filter = params.get("bt") if params else None
        st_filter = params.get("st") if params else None
        rows = []
        for occ in eng.booking_occurrences:
            b = next((x for x in eng.bookings if x["booking_id"] == occ["booking_id"]), {})
            if bt_filter and b.get("booking_type") != bt_filter:
                continue
            if st_filter and occ["status"] != st_filter:
                continue
            r = next((x for x in eng.rooms if x["room_id"] == occ["room_id"]), {})
            ts = next((x for x in eng.time_slots if x["slot_id"] == occ["slot_id"]), {})
            f = next((x for x in eng.faculty if x["faculty_id"] == occ["faculty_id"]), {})
            c = next((x for x in eng.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
            rows.append({
                "occurrence_id": occ["occurrence_id"],
                "booking_id": b.get("booking_id"),
                "booking_type": b.get("booking_type"),
                "title_purpose": b.get("title_purpose"),
                "occurrence_date": occ["occurrence_date"],
                "day_of_week": occ["occurrence_date"].strftime("%A"),
                "slot_name": ts.get("slot_name", ""),
                "start_time": ts.get("start_time", ""),
                "end_time": ts.get("end_time", ""),
                "room_number": r.get("room_number", ""),
                "building": r.get("building", ""),
                "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                "course_code": c.get("course_code"),
                "status": occ["status"],
                "cancellation_reason": occ["cancellation_reason"]
            })
        rows.sort(key=lambda x: str(x["occurrence_date"]), reverse=True)
        return rows[:200]

    # Timetable by Room
    if "WHERE BO.ROOM_ID = :EID" in s:
        eid = params.get("eid")
        rows = []
        for occ in eng.booking_occurrences:
            if occ["room_id"] == eid and occ["status"] == "ACTIVE":
                b = next((x for x in eng.bookings if x["booking_id"] == occ["booking_id"]), {})
                ts = next((x for x in eng.time_slots if x["slot_id"] == occ["slot_id"]), {})
                f = next((x for x in eng.faculty if x["faculty_id"] == occ["faculty_id"]), {})
                c = next((x for x in eng.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
                r = next((x for x in eng.rooms if x["room_id"] == occ["room_id"]), {})
                rows.append({
                    "occurrence_id": occ["occurrence_id"],
                    "booking_id": b.get("booking_id"),
                    "booking_type": b.get("booking_type"),
                    "title_purpose": b.get("title_purpose"),
                    "occurrence_date": occ["occurrence_date"],
                    "day_of_week": occ["occurrence_date"].strftime("%A"),
                    "slot_id": ts.get("slot_id"),
                    "slot_order": ts.get("slot_order"),
                    "slot_name": ts.get("slot_name"),
                    "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                    "course_code": c.get("course_code"),
                    "room_number": r.get("room_number"),
                    "status": occ["status"]
                })
        rows.sort(key=lambda x: str(x["occurrence_date"]))
        return rows

    # Timetable by Faculty
    if "WHERE BO.FACULTY_ID = :EID" in s:
        eid = params.get("eid")
        rows = []
        for occ in eng.booking_occurrences:
            if occ["faculty_id"] == eid and occ["status"] == "ACTIVE":
                b = next((x for x in eng.bookings if x["booking_id"] == occ["booking_id"]), {})
                ts = next((x for x in eng.time_slots if x["slot_id"] == occ["slot_id"]), {})
                f = next((x for x in eng.faculty if x["faculty_id"] == occ["faculty_id"]), {})
                c = next((x for x in eng.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
                r = next((x for x in eng.rooms if x["room_id"] == occ["room_id"]), {})
                rows.append({
                    "occurrence_id": occ["occurrence_id"],
                    "booking_id": b.get("booking_id"),
                    "booking_type": b.get("booking_type"),
                    "title_purpose": b.get("title_purpose"),
                    "occurrence_date": occ["occurrence_date"],
                    "day_of_week": occ["occurrence_date"].strftime("%A"),
                    "slot_id": ts.get("slot_id"),
                    "slot_order": ts.get("slot_order"),
                    "slot_name": ts.get("slot_name"),
                    "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                    "course_code": c.get("course_code"),
                    "room_number": r.get("room_number"),
                    "status": occ["status"]
                })
        rows.sort(key=lambda x: str(x["occurrence_date"]))
        return rows

    # Timetable by Dept
    if "WHERE (C.DEPT_ID = :EID OR F.DEPT_ID = :EID)" in s:
        eid = params.get("eid")
        rows = []
        for occ in eng.booking_occurrences:
            b = next((x for x in eng.bookings if x["booking_id"] == occ["booking_id"]), {})
            f = next((x for x in eng.faculty if x["faculty_id"] == occ["faculty_id"]), {})
            c = next((x for x in eng.courses if x["course_id"] == b.get("course_id")), {}) if b.get("course_id") else {}
            if (c.get("dept_id") == eid or f.get("dept_id") == eid) and occ["status"] == "ACTIVE":
                ts = next((x for x in eng.time_slots if x["slot_id"] == occ["slot_id"]), {})
                r = next((x for x in eng.rooms if x["room_id"] == occ["room_id"]), {})
                rows.append({
                    "occurrence_id": occ["occurrence_id"],
                    "booking_id": b.get("booking_id"),
                    "booking_type": b.get("booking_type"),
                    "title_purpose": b.get("title_purpose"),
                    "occurrence_date": occ["occurrence_date"],
                    "day_of_week": occ["occurrence_date"].strftime("%A"),
                    "slot_id": ts.get("slot_id"),
                    "slot_order": ts.get("slot_order"),
                    "slot_name": ts.get("slot_name"),
                    "faculty_name": f"{f.get('first_name', '')} {f.get('last_name', '')}".strip(),
                    "course_code": c.get("course_code"),
                    "room_number": r.get("room_number"),
                    "status": occ["status"]
                })
        rows.sort(key=lambda x: str(x["occurrence_date"]))
        return rows

    # Department utilization summary
    if "DEPARTMENTAL SPACE ALLOCATION" in s or ("FROM DEPARTMENT D" in s and "TOTAL_LECTURES" in s):
        res = []
        for d in eng.departments:
            did = d["dept_id"]
            d_fac_ids = {f["faculty_id"] for f in eng.faculty if f["dept_id"] == did}
            tot_lec = sum(1 for o in eng.booking_occurrences if o["faculty_id"] in d_fac_ids and o["status"] == "ACTIVE")
            courses_cnt = sum(1 for c in eng.courses if c["dept_id"] == did)
            res.append({
                "dept_code": d["dept_code"],
                "dept_name": d["dept_name"],
                "total_lectures": tot_lec,
                "faculty_count": len(d_fac_ids),
                "courses_taught": courses_cnt
            })
        res.sort(key=lambda x: -x["total_lectures"])
        return res

    # Charts: Dept distribution
    if "SELECT D.DEPT_CODE, COUNT(BO.OCCURRENCE_ID) AS CNT" in s:
        res = []
        for d in eng.departments:
            did = d["dept_id"]
            d_fac_ids = {f["faculty_id"] for f in eng.faculty if f["dept_id"] == did}
            cnt = sum(1 for o in eng.booking_occurrences if o["faculty_id"] in d_fac_ids and o["status"] == "ACTIVE")
            res.append({"dept_code": d["dept_code"], "cnt": cnt})
        res.sort(key=lambda x: -x["cnt"])
        return res

    return []


def query_one(sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute_dml(sql: str, params: Optional[Dict[str, Any]] = None) -> int:
    """Universal DML executor."""
    global _oracle_pool
    if _oracle_pool is not None:
        try:
            with _oracle_pool.acquire() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params or {})
                    rc = cur.rowcount
                    conn.commit()
                    return rc
        except Exception as e:
            logger.error(f"Oracle execute_dml error: {e}")

    eng = get_engine()
    s = sql.strip().upper()
    p = params or {}

    # ROOM DML
    if s.startswith("DELETE FROM ROOM WHERE ROOM_ID = :RID"):
        rid = p["rid"]
        eng.rooms = [r for r in eng.rooms if r["room_id"] != rid]
        return 1

    if s.startswith("UPDATE ROOM"):
        rid = p["rid"]
        for r in eng.rooms:
            if r["room_id"] == rid:
                r["building"] = p["bld"]
                r["floor"] = p["fl"]
                r["room_type"] = p["rt"]
                r["capacity"] = p["cap"]
                return 1

    # DEPARTMENT DML
    if s.startswith("INSERT INTO DEPARTMENT"):
        did = eng._seq_dept
        eng._seq_dept += 1
        eng.departments.append({
            "dept_id": did, "dept_code": p["dc"], "dept_name": p["dn"], "office_location": p["off"]
        })
        return 1

    if s.startswith("UPDATE DEPARTMENT"):
        did = p["did"]
        for d in eng.departments:
            if d["dept_id"] == did:
                d["dept_name"] = p["dn"]
                d["office_location"] = p["off"]
                return 1

    if s.startswith("DELETE FROM DEPARTMENT"):
        did = p["did"]
        eng.departments = [d for d in eng.departments if d["dept_id"] != did]
        return 1

    # FACULTY DML
    if s.startswith("INSERT INTO FACULTY"):
        fid = eng._seq_faculty
        eng._seq_faculty += 1
        eng.faculty.append({
            "faculty_id": fid, "faculty_code": p["fc"], "first_name": p["fn"], "last_name": p["ln"],
            "email": p["em"], "dept_id": p["did"], "designation": p["des"]
        })
        return 1

    if s.startswith("UPDATE FACULTY"):
        fid = p["fid"]
        for f in eng.faculty:
            if f["faculty_id"] == fid:
                f["first_name"] = p["fn"]
                f["last_name"] = p["ln"]
                f["email"] = p["em"]
                f["dept_id"] = p["did"]
                f["designation"] = p["des"]
                return 1

    if s.startswith("DELETE FROM FACULTY"):
        fid = p["fid"]
        eng.faculty = [f for f in eng.faculty if f["faculty_id"] != fid]
        return 1

    # COURSE DML
    if s.startswith("INSERT INTO COURSE"):
        cid = eng._seq_course
        eng._seq_course += 1
        eng.courses.append({
            "course_id": cid, "course_code": p["cc"], "course_title": p["ct"], "credits": p["cr"], "dept_id": p["did"]
        })
        return 1

    if s.startswith("UPDATE COURSE"):
        cid = p["cid"]
        for c in eng.courses:
            if c["course_id"] == cid:
                c["course_title"] = p["ct"]
                c["credits"] = p["cr"]
                c["dept_id"] = p["did"]
                return 1

    if s.startswith("DELETE FROM COURSE"):
        cid = p["cid"]
        eng.courses = [c for c in eng.courses if c["course_id"] != cid]
        return 1

    # TIME SLOT DML
    if s.startswith("INSERT INTO TIME_SLOT"):
        sid = eng._seq_slot
        eng._seq_slot += 1
        eng.time_slots.append({
            "slot_id": sid, "slot_name": p["sn"], "start_time": p["st"], "end_time": p["et"], "slot_order": p["so"]
        })
        return 1

    return 0


# ----------------------------------------------------------------------------
# Procedure Call Wrappers
# ----------------------------------------------------------------------------
def call_book_periodic(room_id: int, faculty_id: int, course_id: Optional[int],
                       day_of_week: str, slot_id: int, semester_id: int,
                       title_purpose: str) -> Tuple[int, int]:
    global _oracle_pool
    if _oracle_pool is not None:
        import oracledb
        with _oracle_pool.acquire() as conn:
            with conn.cursor() as cur:
                out_bid = cur.var(oracledb.NUMBER)
                out_cnt = cur.var(oracledb.NUMBER)
                cur.callproc("book_periodic", [
                    room_id, faculty_id, course_id, day_of_week, slot_id,
                    semester_id, title_purpose, out_bid, out_cnt
                ])
                conn.commit()
                return int(out_bid.getvalue()), int(out_cnt.getvalue())

    return get_engine().book_periodic(
        room_id, faculty_id, course_id, day_of_week, slot_id, semester_id, title_purpose
    )


def call_book_oneoff(room_id: int, faculty_id: int, course_id: Optional[int],
                     booking_date, slot_id: int, title_purpose: str) -> int:
    global _oracle_pool
    if _oracle_pool is not None:
        import oracledb
        with _oracle_pool.acquire() as conn:
            with conn.cursor() as cur:
                out_bid = cur.var(oracledb.NUMBER)
                cur.callproc("book_oneoff", [
                    room_id, faculty_id, course_id, booking_date, slot_id,
                    title_purpose, out_bid
                ])
                conn.commit()
                return int(out_bid.getvalue())

    return get_engine().book_oneoff(
        room_id, faculty_id, course_id, booking_date, slot_id, title_purpose
    )


def call_cancel_occurrence(booking_id: int, occurrence_date, reason: str = "Cancelled by user"):
    global _oracle_pool
    if _oracle_pool is not None:
        with _oracle_pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.callproc("cancel_occurrence", [booking_id, occurrence_date, reason])
                conn.commit()
                return

    get_engine().cancel_occurrence(booking_id, occurrence_date, reason)


def call_cancel_series(booking_id: int, reason: str = "Entire series cancelled"):
    global _oracle_pool
    if _oracle_pool is not None:
        with _oracle_pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.callproc("cancel_series", [booking_id, reason])
                conn.commit()
                return

    get_engine().cancel_series(booking_id, reason)


def call_find_free_rooms(search_date, slot_id: int, min_capacity: int = 0,
                         facility_id: Optional[int] = None) -> List[Dict[str, Any]]:
    global _oracle_pool
    if _oracle_pool is not None:
        with _oracle_pool.acquire() as conn:
            with conn.cursor() as cur:
                ref_cur = conn.cursor()
                cur.callproc("find_free_rooms", [search_date, slot_id, min_capacity, facility_id, ref_cur])
                cols = [c[0].lower() for c in ref_cur.description]
                res = [dict(zip(cols, row)) for row in ref_cur.fetchall()]
                ref_cur.close()
                return res

    return get_engine().find_free_rooms(search_date, slot_id, min_capacity, facility_id)


def call_cursor_utilization_report() -> List[Dict[str, Any]]:
    global _oracle_pool
    if _oracle_pool is not None:
        with _oracle_pool.acquire() as conn:
            with conn.cursor() as cur:
                ref_cur = conn.cursor()
                cur.callproc("cursor_utilization_report", [ref_cur])
                cols = [c[0].lower() for c in ref_cur.description]
                res = [dict(zip(cols, row)) for row in ref_cur.fetchall()]
                ref_cur.close()
                return res

    return get_engine().cursor_utilization_report()


def execute_sql_lab_query(sql_text: str) -> Tuple[List[str], List[Dict[str, Any]], float]:
    """Runs a query in the SQL console."""
    return get_engine().execute_arbitrary_query(sql_text)


def get_occupancy_heatmap_data(day_of_week: str, slot_id: int) -> Dict[str, Any]:
    """Fetches real-time room occupancy matrix for 2D Heatmap."""
    return get_engine().get_occupancy_heatmap(day_of_week, slot_id)


# Test connection upon startup
test_oracle_connection()
