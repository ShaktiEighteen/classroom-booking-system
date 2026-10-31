"""
Automated Database Rules & Constraint Verification Test Suite
Classroom Booking and Timetable Management System

Tests:
(a) A conflicting booking is rejected (Room Clash -20001).
(b) A faculty clash is rejected (Faculty Clash -20002).
(c) A periodic booking creates one row per week.
(d) Cancelling one occurrence frees only that slot and leaves the rest of the series intact.
(e) The freed slot appears in find_free_rooms.
"""

import datetime
import unittest
from app import db


class TestClassroomBookingRules(unittest.TestCase):

    def setUp(self):
        # Fresh isolated engine instance for each test
        db._engine = db.OracleDatabaseEngine()
        self.engine = db.get_engine()

    def test_a_conflicting_room_booking_is_rejected(self):
        """(a) Proves that a room double-booking conflict is strictly rejected."""
        # In sample data, Room 1 (CR-A101) is booked on Mondays Slot 1 by Dr. Alan Turing
        # Attempt to book Room 1 with another faculty (Dr. Ada Lovelace) on Monday Slot 1
        with self.assertRaises(Exception) as ctx:
            db.call_book_periodic(
                room_id=1,
                faculty_id=2,  # Dr. Ada Lovelace
                course_id=2,
                day_of_week="Monday",
                slot_id=1,    # Slot 1 is already taken by Alan Turing in Room 1
                semester_id=1,
                title_purpose="Conflicting Booking Attempt"
            )

        err = str(ctx.exception)
        self.assertTrue(
            "Room Clash" in err or "ORA-20001" in err or "already booked" in err,
            f"Expected Room Clash error (-20001), got: {err}"
        )
        print(f"\n[PASS] Test (a): Conflicting Room reservation successfully rejected by database: {err}")

    def test_b_faculty_clash_is_rejected(self):
        """(b) Proves that a faculty clash (same faculty in two rooms at once) is strictly rejected."""
        # In sample data, Dr. Alan Turing (Faculty 1) is booked on Mondays Slot 1 in Room 1
        # Attempt to schedule Dr. Alan Turing in Room 3 on Monday Slot 1
        with self.assertRaises(Exception) as ctx:
            db.call_book_periodic(
                room_id=3,     # Room 3 is empty at Slot 1
                faculty_id=1,  # Dr. Alan Turing (already lecturing in Room 1)
                course_id=5,
                day_of_week="Monday",
                slot_id=1,
                semester_id=1,
                title_purpose="Faculty Clash Attempt in Room 3"
            )

        err = str(ctx.exception)
        self.assertTrue(
            "Faculty Clash" in err or "ORA-20002" in err or "already scheduled" in err,
            f"Expected Faculty Clash error (-20002), got: {err}"
        )
        print(f"\n[PASS] Test (b): Faculty Clash successfully rejected by compound trigger: {err}")

    def test_c_periodic_booking_creates_one_row_per_week(self):
        """(c) Proves that a periodic booking creates exactly one row per week across the semester."""
        sem = next((s for s in self.engine.semesters if s["semester_id"] == 1), None)
        self.assertIsNotNone(sem, "Active Semester 1 must exist")

        # Count how many Thursdays exist in Semester 1 (2026-08-03 to 2026-11-28)
        expected_thursdays = 0
        curr = sem["start_date"]
        while curr <= sem["end_date"]:
            if curr.strftime("%A") == "Thursday":
                expected_thursdays += 1
            curr += datetime.timedelta(days=1)

        self.assertGreater(expected_thursdays, 0)

        # Book an available room (Room 18, LAB-ME-01) for Faculty 9 on Thursdays at Slot 7
        bid, count = db.call_book_periodic(
            room_id=18,
            faculty_id=9,
            course_id=15,
            day_of_week="Thursday",
            slot_id=7,
            semester_id=1,
            title_purpose="ME501: Heat & Mass Transfer Lab"
        )

        self.assertEqual(count, expected_thursdays, f"Periodic booking must create {expected_thursdays} rows")
        
        # Verify in database occurrences
        created_occs = [
            o for o in self.engine.booking_occurrences 
            if o["booking_id"] == bid and o["status"] == "ACTIVE"
        ]
        self.assertEqual(len(created_occs), expected_thursdays)
        print(f"\n[PASS] Test (c): Periodic booking created {count} weekly occurrences across full semester (Booking #{bid}).")

    def test_d_and_e_cancel_occurrence_frees_slot_and_preserves_series(self):
        """
        Proves:
        (d) Cancelling one occurrence frees only that slot and leaves the rest of the series intact.
        (e) The freed slot appears in find_free_rooms.
        """
        # In sample data, Booking 1 is Alan Turing's CS101 on Mondays Slot 1 in Room 1
        booking_id = 1
        all_series_occs = [o for o in self.engine.booking_occurrences if o["booking_id"] == booking_id]
        total_initial_active = sum(1 for o in all_series_occs if o["status"] == "ACTIVE")
        self.assertGreater(total_initial_active, 1)

        # Pick an active date in the series: 2026-08-24 (Monday)
        target_date = datetime.date(2026, 8, 24)

        # Before cancelling: verify Room 1 is NOT free on 2026-08-24 Slot 1
        free_before = db.call_find_free_rooms(target_date, slot_id=1)
        free_room_ids_before = [r["room_id"] for r in free_before]
        self.assertNotIn(1, free_room_ids_before, "Room 1 must NOT be free before cancellation")

        # (d) Cancel ONLY this single occurrence
        db.call_cancel_occurrence(booking_id, target_date, "Attending faculty workshop")

        # Verify that ONLY this occurrence became CANCELLED
        target_occ = next((o for o in self.engine.booking_occurrences if o["booking_id"] == booking_id and o["occurrence_date"] == target_date), None)
        self.assertIsNotNone(target_occ)
        self.assertEqual(target_occ["status"], "CANCELLED")

        # Verify that the rest of the series remains ACTIVE
        remaining_active = sum(1 for o in self.engine.booking_occurrences if o["booking_id"] == booking_id and o["status"] == "ACTIVE")
        self.assertEqual(remaining_active, total_initial_active - 1, "Exactly one occurrence must be deducted")

        # (e) Verify the freed slot now appears in find_free_rooms for target_date Slot 1!
        free_after = db.call_find_free_rooms(target_date, slot_id=1)
        free_room_ids_after = [r["room_id"] for r in free_after]
        self.assertIn(1, free_room_ids_after, "Room 1 must NOW be in free rooms list after cancellation!")

        # Verify subsequent weeks (e.g. next Monday 2026-08-31) remain BOOKED
        next_week = datetime.date(2026, 8, 31)
        free_next_week = db.call_find_free_rooms(next_week, slot_id=1)
        self.assertNotIn(1, [r["room_id"] for r in free_next_week], "Next week must remain booked!")

        print(f"\n[PASS] Tests (d) & (e): Cancelled occurrence on {target_date} Slot 1 freed ONLY that slot (verified in find_free_rooms), while preserving all remaining {remaining_active} active lectures in the series.")


if __name__ == "__main__":
    unittest.main()
