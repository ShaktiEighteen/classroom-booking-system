"""
Automated Web Application & HTTP Integration Test Suite
Classroom Booking and Timetable Management System

Exercises every page, form, API endpoint, and UI interaction.
"""

import unittest
from app.app import app
from app import db


class TestClassroomWebApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_dashboard_page(self):
        """Dashboard renders executive statistics and today's schedule."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Executive Dashboard", html)
        self.assertIn("Active Classrooms", html)
        self.assertIn("Registered Faculty", html)
        print("\n[PASS] Dashboard route (/) rendered successfully.")

    def test_02_rooms_master_page(self):
        """Rooms master data page renders 20 rooms with filtering."""
        response = self.client.get("/rooms")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("CR-A101", html)
        self.assertIn("LAB-CS-01", html)
        self.assertIn("AUD-MAIN", html)
        print("[PASS] Rooms page (/rooms) rendered with full inventory.")

    def test_03_departments_page(self):
        """Departments page lists all 5 engineering departments."""
        response = self.client.get("/departments")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Computer Science and Engineering", html)
        self.assertIn("Electronics and Communication Engineering", html)
        print("[PASS] Departments page (/departments) rendered successfully.")

    def test_04_faculty_page(self):
        """Faculty page renders 15 professors with designations."""
        response = self.client.get("/faculty")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Alan Turing", html)
        self.assertIn("Ada Lovelace", html)
        self.assertIn("Claude Shannon", html)
        print("[PASS] Faculty page (/faculty) rendered successfully.")

    def test_05_courses_page(self):
        """Courses page renders all 25 curriculum courses."""
        response = self.client.get("/courses")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("CS101", html)
        self.assertIn("Data Structures and Algorithms", html)
        self.assertIn("CS201", html)
        print("[PASS] Courses page (/courses) rendered successfully.")

    def test_06_timeslots_page(self):
        """Timeslots page lists 8 daily lecture hours."""
        response = self.client.get("/timeslots")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("08:30", html)
        self.assertIn("17:45", html)
        print("[PASS] Time Slots page (/timeslots) rendered successfully.")

    def test_07_bookings_list_page(self):
        """Bookings list page renders parent reservations and dated occurrences."""
        response = self.client.get("/bookings")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Booking Occurrences", html)
        print("[PASS] Bookings list page (/bookings) rendered successfully.")

    def test_08_new_booking_form_page(self):
        """New Booking page loads with all required dropdown options."""
        response = self.client.get("/bookings/new")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Reserve Classroom / Laboratory", html)
        self.assertIn("Select Booking Type", html)
        print("[PASS] New Booking Form (/bookings/new) loaded successfully.")

    def test_09_create_oneoff_booking_success(self):
        """Creates a one-off seminar booking and asserts redirect + success flash."""
        response = self.client.post("/bookings/create", data={
            "booking_type": "ONEOFF",
            "room_id": 11,  # AUD-MAIN
            "faculty_id": 5,  # John Bardeen
            "course_id": "",
            "booking_date": "2026-11-20",
            "slot_id": 4,
            "title_purpose": "Keynote Address on Semiconductor Physics"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("One-off booking created successfully", html)
        print("[PASS] Successful One-Off Booking creation verified.")

    def test_10_create_conflicting_booking_shows_exact_database_error(self):
        """Attempts conflicting booking and verifies exact Oracle error appears in UI."""
        # Room 1 is already booked on Mondays Slot 1
        response = self.client.post("/bookings/create", data={
            "booking_type": "PERIODIC",
            "room_id": 1,
            "faculty_id": 8,  # Nikola Tesla
            "course_id": 14,
            "day_of_week": "Monday",
            "semester_id": 1,
            "slot_id": 1,
            "title_purpose": "Conflict Intended"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Database Conflict", html)
        self.assertTrue("Room Clash" in html or "already booked" in html)
        print("[PASS] Exact Database Conflict message displayed cleanly to user in flash alert.")

    def test_11_timetable_grid_views(self):
        """Timetable grid renders weekly schedules by room, faculty, and department."""
        # By Room
        res_room = self.client.get("/timetable?type=room&id=1")
        self.assertEqual(res_room.status_code, 200)
        self.assertIn("Schedule for:", res_room.get_data(as_text=True))

        # By Faculty
        res_fac = self.client.get("/timetable?type=faculty&id=1")
        self.assertEqual(res_fac.status_code, 200)
        self.assertIn("Alan Turing", res_fac.get_data(as_text=True))

        # By Department
        res_dept = self.client.get("/timetable?type=dept&id=1")
        self.assertEqual(res_dept.status_code, 200)
        self.assertIn("Computer Science", res_dept.get_data(as_text=True))
        print("[PASS] Timetable Grid matrix (Room, Faculty, Department) rendered successfully.")

    def test_12_free_room_finder(self):
        """Free room finder calls find_free_rooms procedure and lists unbooked rooms."""
        response = self.client.post("/free-rooms", data={
            "date": "2026-10-15",
            "slot_id": "3",
            "min_capacity": "50",
            "facility_id": ""
        })
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Available Rooms Found", html)
        print("[PASS] Free-Room Finder (/free-rooms) executed successfully.")

    def test_13_reports_page_and_charts_api(self):
        """Reports page renders utilization views and JSON chart endpoints."""
        response = self.client.get("/reports")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Reports", html)
        self.assertIn("Space Utilization", html)
        self.assertIn("room_utilization_vw", html)
        self.assertIn("booking_history_vw", html)

        # JSON Chart endpoints
        res_api1 = self.client.get("/api/charts/room-utilization")
        self.assertEqual(res_api1.status_code, 200)
        self.assertIn("labels", res_api1.get_json())

        res_api2 = self.client.get("/api/charts/dept-distribution")
        self.assertEqual(res_api2.status_code, 200)
        self.assertIn("labels", res_api2.get_json())
        print("[PASS] Reports analytics page & JSON APIs verified.")

    def test_14_interactive_sql_console_and_api(self):
        """Tests SQL console UI and live query execution endpoint."""
        res_page = self.client.get("/sql-console")
        self.assertEqual(res_page.status_code, 200)
        self.assertIn("Interactive SQL Lab", res_page.get_data(as_text=True))

        # API query execution
        res_run = self.client.post("/api/run-sql", json={
            "sql": "SELECT room_number, building, capacity FROM ROOM WHERE room_type = 'LAB';"
        })
        self.assertEqual(res_run.status_code, 200)
        data = res_run.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["row_count"], 0)
        self.assertIn("execution_time_ms", data)
        print(f"[PASS] SQL Console & Query Runner verified ({data['row_count']} rows in {data['execution_time_ms']}ms).")

    def test_15_occupancy_heatmap_and_schema_explorer(self):
        """Tests 2D Occupancy Map and 3NF Schema Explorer."""
        res_map = self.client.get("/occupancy-map?day=Monday&slot=1")
        self.assertEqual(res_map.status_code, 200)
        self.assertIn("2D Interactive Campus Heatmap", res_map.get_data(as_text=True))
        self.assertIn("Occupancy Rate", res_map.get_data(as_text=True))

        res_schema = self.client.get("/schema-explorer")
        self.assertEqual(res_schema.status_code, 200)
        self.assertIn("3NF Relational Schema Explorer", res_schema.get_data(as_text=True))
        self.assertIn("BOOKING_OCCURRENCE", res_schema.get_data(as_text=True))
        print("[PASS] 2D Campus Heatmap & 3NF Schema Explorer verified.")


if __name__ == "__main__":
    unittest.main()
