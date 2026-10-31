# Relational Schema & 3NF Normalization Analysis
## Classroom Booking and Timetable Management System
**DBMS:** Oracle Database 21c Express Edition (XE)

---

## 1. Relational Schema Definition

1. **DEPARTMENT** (<ins>dept_id</ins>, dept_code, dept_name, office_location)
   - *Primary Key:* `dept_id`
   - *Alternate Key:* `dept_code`

2. **FACULTY** (<ins>faculty_id</ins>, faculty_code, first_name, last_name, email, dept_id, designation)
   - *Primary Key:* `faculty_id`
   - *Alternate Keys:* `faculty_code`, `email`
   - *Foreign Key:* `dept_id` references `DEPARTMENT(dept_id)`

3. **COURSE** (<ins>course_id</ins>, course_code, course_title, credits, dept_id)
   - *Primary Key:* `course_id`
   - *Alternate Key:* `course_code`
   - *Foreign Key:* `dept_id` references `DEPARTMENT(dept_id)`

4. **ROOM** (<ins>room_id</ins>, room_number, building, floor, room_type, capacity)
   - *Primary Key:* `room_id`
   - *Alternate Key:* `room_number`
   - *Check Constraints:* `capacity > 0`, `room_type IN ('CLASSROOM', 'LAB', 'SEMINAR_HALL')`

5. **FACILITY** (<ins>facility_id</ins>, facility_name, description)
   - *Primary Key:* `facility_id`
   - *Alternate Key:* `facility_name`

6. **ROOM_FACILITY** (<ins>room_id, facility_id</ins>, quantity)
   - *Composite Primary Key:* `(room_id, facility_id)`
   - *Foreign Keys:* `room_id` references `ROOM(room_id)`, `facility_id` references `FACILITY(facility_id)`
   - *Check Constraint:* `quantity > 0`

7. **SEMESTER** (<ins>semester_id</ins>, semester_name, start_date, end_date, is_active)
   - *Primary Key:* `semester_id`
   - *Alternate Key:* `semester_name`
   - *Check Constraint:* `end_date > start_date`, `is_active IN (0, 1)`

8. **TIME_SLOT** (<ins>slot_id</ins>, slot_name, start_time, end_time, slot_order)
   - *Primary Key:* `slot_id`
   - *Alternate Key:* `slot_order`
   - *Check Constraint:* `end_time > start_time`

9. **BOOKING** (<ins>booking_id</ins>, booking_type, room_id, faculty_id, course_id, title_purpose, day_of_week, slot_id, semester_id, created_at)
   - *Primary Key:* `booking_id`
   - *Foreign Keys:*
     - `room_id` references `ROOM(room_id)`
     - `faculty_id` references `FACULTY(faculty_id)`
     - `course_id` references `COURSE(course_id)` (nullable for special events)
     - `slot_id` references `TIME_SLOT(slot_id)`
     - `semester_id` references `SEMESTER(semester_id)`
   - *Check Constraints:* `booking_type IN ('PERIODIC', 'ONEOFF')`

10. **BOOKING_OCCURRENCE** (<ins>occurrence_id</ins>, booking_id, occurrence_date, slot_id, room_id, faculty_id, status, cancellation_reason, updated_at)
    - *Primary Key:* `occurrence_id`
    - *Foreign Keys:*
      - `booking_id` references `BOOKING(booking_id)` ON DELETE CASCADE
      - `slot_id` references `TIME_SLOT(slot_id)`
      - `room_id` references `ROOM(room_id)`
      - `faculty_id` references `FACULTY(faculty_id)`
    - *Unique Function-Based Index:*
      `(CASE WHEN status='ACTIVE' THEN room_id END, CASE WHEN status='ACTIVE' THEN occurrence_date END, CASE WHEN status='ACTIVE' THEN slot_id END)`
    - *Check Constraint:* `status IN ('ACTIVE', 'CANCELLED')`

---

## 2. Functional Dependencies & Normalization Proofs

### First Normal Form (1NF)
- All attribute domains contain only atomic, indivisible scalar values.
- No repeating groups or multivalued columns exist (e.g., room facilities are normalized into the associative table `ROOM_FACILITY`).

### Second Normal Form (2NF)
- The relations are in 1NF.
- Every non-prime attribute is fully functionally dependent on the entire primary key:
  - In `ROOM_FACILITY(room_id, facility_id)`, `quantity` depends on the composite key `{room_id, facility_id}`.
  - In all single-attribute PK relations (`DEPARTMENT`, `FACULTY`, `COURSE`, `ROOM`, `TIME_SLOT`, `SEMESTER`, `BOOKING`, `BOOKING_OCCURRENCE`), partial dependencies are impossible.

### Third Normal Form (3NF)
- The relations are in 2NF.
- There are no transitive dependencies $X \to Y$ and $Y \to Z$ where $Z$ is a non-prime attribute:
  - In `FACULTY`, `{faculty_id} -> dept_id` and `{dept_id} -> dept_name`. To preserve 3NF, `dept_name` and `office_location` are factored out into `DEPARTMENT`.
  - In `COURSE`, `{course_id} -> dept_id`, preventing departmental transitive attributes.
  - In `BOOKING_OCCURRENCE`, the occurrence maintains atomic pointers to `slot_id`, `room_id`, and `faculty_id` for instant index evaluation and foreign key validation without duplicating facility or faculty department metadata.
- Therefore, the relational schema is strictly in **Third Normal Form (3NF)**.
