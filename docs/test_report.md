# Automated Verification and Test Report
## Classroom Booking and Timetable Management System
**Verification Date:** 2026-10-31  
**Status:** ALL 20 AUTOMATED TESTS PASSED (100% SUCCESS)

---

## 1. Executive Summary
The system was verified end-to-end across database business logic, compound triggers, stored procedures, analytical SQL views, set operations, interactive query execution, and web routes.

### Test Execution Overview
| Test Suite | Total Tests | Passed | Failed | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Database Rules & Trigger Suite** | 4 | 4 | 0 | **PASSED (100%)** |
| **Web Application & Interactive Labs Suite** | 16 | 16 | 0 | **PASSED (100%)** |
| **Total Automated Tests** | **20** | **20** | **0** | **100% PASSED** |

---

## 2. Core Database Integrity Test Results (`test_database_rules.py`)

### Test (a): Conflicting Room Reservation Rejected
- **Description:** Attempts to book `Room CR-A101` on Monday Slot 1 when Dr. Alan Turing is already lecturing in that space.
- **Expected Outcome:** Database rejects transaction and raises `RAISE_APPLICATION_ERROR(-20001, ...)`.
- **Observed Result:** `[PASS] Test (a): Conflicting Room reservation successfully rejected by database: ORA-20001: Room Clash: Room CR-A101 is already booked on 2026-08-03 during Slot 1 (08:30 - 09:30).`

### Test (b): Faculty Clash Rejected
- **Description:** Attempts to schedule `Dr. Alan Turing` in `Room CR-A201` during Monday Slot 1 while he is actively assigned to `Room CR-A101`.
- **Expected Outcome:** Compound trigger `TRG_PREVENT_BOOKING_CONFLICTS` detects schedule overlap and raises application error `-20002`.
- **Observed Result:** `[PASS] Test (b): Faculty Clash successfully rejected by compound trigger: ORA-20002: Faculty Clash: Faculty member Alan Turing is already scheduled in room CR-A101 on 2026-08-03 during this time slot.`

### Test (c): Periodic Booking Atomicity & Weekly Generation
- **Description:** Calls `book_periodic` for a semester spanning `2026-08-03` to `2026-11-28` on Thursdays.
- **Expected Outcome:** Exactly 17 weekly lecture occurrences generated atomically under parent booking.
- **Observed Result:** `[PASS] Test (c): Periodic booking created 17 weekly occurrences across full semester (Booking #20).`

### Tests (d) & (e): Cancellation Frees Only That Slot & Appears in `find_free_rooms`
- **Description:** Calls `cancel_occurrence` for lecture date `2026-08-24` Slot 1.
- **Expected Outcome:** 
  1. Only the target occurrence changes to `CANCELLED`.
  2. The remaining 15 weekly occurrences in the semester remain `ACTIVE`.
  3. `Room 1` immediately appears as available in `find_free_rooms` for `2026-08-24 Slot 1`.
  4. Next week (`2026-08-31`) remains actively booked.
- **Observed Result:** `[PASS] Tests (d) & (e): Cancelled occurrence on 2026-08-24 Slot 1 freed ONLY that slot (verified in find_free_rooms), while preserving all remaining 15 active lectures in the series.`

---

## 3. Web & HTTP Route Test Results (`test_web_routes.py`)

1. **Dashboard Route (`/`):** Status 200 OK. Metric cards, today's schedule, and top utilized rooms rendered.
2. **Rooms Master (`/rooms`):** Status 200 OK. 20 rooms listed with capacity, building, and facility tags.
3. **Departments (`/departments`):** Status 200 OK. 5 departments rendered with faculty and course counts.
4. **Faculty (`/faculty`):** Status 200 OK. 15 faculty listed with designations and email contacts.
5. **Courses (`/courses`):** Status 200 OK. 25 courses rendered with credit hours and offering department.
6. **Time Slots (`/timeslots`):** Status 200 OK. 8 daily time slots rendered in chronological order.
7. **Bookings Log (`/bookings`):** Status 200 OK. All active and cancelled booking occurrences displayed with badges.
8. **New Booking Form (`/bookings/new`):** Status 200 OK. Dynamic toggle between Periodic and One-Off fields.
9. **One-Off Booking Submission:** Status 302 Redirect -> 200 OK with success flash notification.
10. **Conflict Feedback in UI:** Status 302 Redirect -> 200 OK with red danger toast displaying exact Oracle error message.
11. **Timetable Matrix Grid (`/timetable`):** Status 200 OK. Monday-Saturday x 8 slots weekly grid rendered for rooms, faculty, and departments with "Cancel Lecture" buttons.
12. **Free-Room Finder (`/free-rooms`):** Status 200 OK. Set operation procedure `find_free_rooms` successfully executed.
13. **Reports & Analytics (`/reports`):** Status 200 OK. Analytical views rendered; `/api/charts/room-utilization` and `/api/charts/dept-distribution` returned valid JSON datasets.
14. **Interactive SQL Console & Live Query Runner (`/sql-console`, `/api/run-sql`):** Status 200 OK. Queries execute with syntax safety, timing metrics, and tabular rendering.
15. **Conflict & Concurrency Simulator (`/conflict-simulator`, `/api/simulate-scenario`):** Status 200 OK. Simulates real-time room clash (`ORA-20001`), faculty clash (`ORA-20002`), and slot liberation.
16. **2D Occupancy Map & 3NF Schema Explorer (`/occupancy-map`, `/schema-explorer`):** Status 200 OK. Live spatial heatmap by day/slot and dynamic interactive data dictionary render cleanly.

---

## 4. UI Screenshots Verified
The following screenshots were automatically captured by headless browser automation and saved in `docs/screenshots/`:
- `dashboard.png`: Executive dashboard with quick metrics and today's schedule.
- `timetable.png`: Full weekly timetable matrix grid with cancel actions.
- `free_rooms.png`: Available classroom search with capacity and equipment filters.
- `new_booking.png`: New reservation form with conflict prevention.
- `reports.png`: Space utilization analytics and interactive charts.
- `rooms.png`: Classrooms and laboratories master data.
- `bookings.png`: Complete booking occurrences audit log.
- `heatmap.png`: 2D Interactive campus building & floor heatmap.
- `sql_console.png`: Interactive SQL laboratory with pre-loaded demonstration queries.
- `conflict_simulator.png`: Real-time conflict laboratory illustrating constraint enforcement.
- `schema_explorer.png`: Relational schema and column dictionary explorer.
