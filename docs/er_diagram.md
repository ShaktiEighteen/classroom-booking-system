# Entity-Relationship (ER) Diagram
## Classroom Booking and Timetable Management System
**Course:** DBMS Mini Project  

---

### Conceptual Architecture
The schema is normalized to **Third Normal Form (3NF)** and strictly modeled to prevent double allocation of physical classrooms and prevent faculty scheduling clashes.

```mermaid
erDiagram
    DEPARTMENT ||--o{ FACULTY : employs
    DEPARTMENT ||--o{ COURSE : offers
    FACULTY ||--o{ BOOKING : requests
    COURSE ||--o{ BOOKING : for_course
    ROOM ||--o{ BOOKING : allocates
    ROOM ||--o{ ROOM_FACILITY : contains
    FACILITY ||--o{ ROOM_FACILITY : equipped_in
    SEMESTER ||--o{ BOOKING : scheduled_in
    TIME_SLOT ||--o{ BOOKING : occupies_slot
    BOOKING ||--|{ BOOKING_OCCURRENCE : generates_dated_sessions
    ROOM ||--o{ BOOKING_OCCURRENCE : hosts_occurrence
    FACULTY ||--o{ BOOKING_OCCURRENCE : instructs_occurrence
    TIME_SLOT ||--o{ BOOKING_OCCURRENCE : during_slot

    DEPARTMENT {
        NUMBER dept_id PK
        VARCHAR2 dept_code UK
        VARCHAR2 dept_name
        VARCHAR2 office_location
    }

    FACULTY {
        NUMBER faculty_id PK
        VARCHAR2 faculty_code UK
        VARCHAR2 first_name
        VARCHAR2 last_name
        VARCHAR2 email UK
        NUMBER dept_id FK
        VARCHAR2 designation
    }

    COURSE {
        NUMBER course_id PK
        VARCHAR2 course_code UK
        VARCHAR2 course_title
        NUMBER credits
        NUMBER dept_id FK
    }

    ROOM {
        NUMBER room_id PK
        VARCHAR2 room_number UK
        VARCHAR2 building
        NUMBER floor
        VARCHAR2 room_type
        NUMBER capacity
    }

    FACILITY {
        NUMBER facility_id PK
        VARCHAR2 facility_name UK
        VARCHAR2 description
    }

    ROOM_FACILITY {
        NUMBER room_id PK, FK
        NUMBER facility_id PK, FK
        NUMBER quantity
    }

    SEMESTER {
        NUMBER semester_id PK
        VARCHAR2 semester_name UK
        DATE start_date
        DATE end_date
        NUMBER is_active
    }

    TIME_SLOT {
        NUMBER slot_id PK
        VARCHAR2 slot_name
        VARCHAR2 start_time
        VARCHAR2 end_time
        NUMBER slot_order UK
    }

    BOOKING {
        NUMBER booking_id PK
        VARCHAR2 booking_type
        NUMBER room_id FK
        NUMBER faculty_id FK
        NUMBER course_id FK
        VARCHAR2 title_purpose
        VARCHAR2 day_of_week
        NUMBER slot_id FK
        NUMBER semester_id FK
        TIMESTAMP created_at
    }

    BOOKING_OCCURRENCE {
        NUMBER occurrence_id PK
        NUMBER booking_id FK
        DATE occurrence_date
        NUMBER slot_id FK
        NUMBER room_id FK
        NUMBER faculty_id FK
        VARCHAR2 status
        VARCHAR2 cancellation_reason
        TIMESTAMP updated_at
    }
```

### Relational Integrity & Conflict Prevention Rules
1. **Double Room Allocation Index (`UQ_ACTIVE_ROOM_DATE_SLOT`):**  
   Oracle unique function-based index on:
   `(CASE WHEN status = 'ACTIVE' THEN room_id END, CASE WHEN status = 'ACTIVE' THEN occurrence_date END, CASE WHEN status = 'ACTIVE' THEN slot_id END)`
   Only active reservations occupy the index. Cancelling a lecture sets `status = 'CANCELLED'` and evaluates to `NULL`, immediately freeing the room and time slot for new bookings.
2. **Faculty Clash Prevention Trigger (`TRG_PREVENT_BOOKING_CONFLICTS`):**  
   Compound trigger on `BOOKING_OCCURRENCE` that checks if the assigned faculty is already lecturing in another classroom during the exact same date and time slot. Raises `RAISE_APPLICATION_ERROR(-20002, ...)`.
