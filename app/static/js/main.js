/**
 * Classroom Booking and Timetable Management System
 * Vanilla JavaScript Frontend Enhancements
 */

document.addEventListener("DOMContentLoaded", function () {
    // 0. Dark Mode Switcher & Persistence
    const themeBtn = document.getElementById("theme-toggle-btn");
    const themeIcon = document.getElementById("theme-icon");
    const currentTheme = localStorage.getItem("classroom_theme") || "light";

    if (currentTheme === "dark") {
        document.documentElement.setAttribute("data-theme", "dark");
        if (themeIcon) {
            themeIcon.classList.remove("fa-moon");
            themeIcon.classList.add("fa-sun");
        }
    }

    if (themeBtn) {
        themeBtn.addEventListener("click", function () {
            const isDark = document.documentElement.getAttribute("data-theme") === "dark";
            if (isDark) {
                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem("classroom_theme", "light");
                if (themeIcon) {
                    themeIcon.classList.remove("fa-sun");
                    themeIcon.classList.add("fa-moon");
                }
            } else {
                document.documentElement.setAttribute("data-theme", "dark");
                localStorage.setItem("classroom_theme", "dark");
                if (themeIcon) {
                    themeIcon.classList.remove("fa-moon");
                    themeIcon.classList.add("fa-sun");
                }
            }
        });
    }

    // 1. Auto-dismiss alerts after 7 seconds (except danger/conflict alerts which stay visible)
    const alerts = document.querySelectorAll(".alert:not(.alert-danger)");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        }, 7000);
    });

    // 2. Booking Type Toggle Handler (New Booking Form)
    const periodicRadio = document.getElementById("type-periodic");
    const oneoffRadio = document.getElementById("type-oneoff");
    const periodicFields = document.getElementById("periodic-fields");
    const oneoffFields = document.getElementById("oneoff-fields");

    function updateBookingType() {
        if (!periodicRadio || !oneoffRadio) return;
        if (periodicRadio.checked) {
            periodicFields.style.display = "block";
            oneoffFields.style.display = "none";
            document.getElementById("day_of_week")?.setAttribute("required", "required");
            document.getElementById("semester_id")?.setAttribute("required", "required");
            document.getElementById("booking_date")?.removeAttribute("required");
        } else {
            periodicFields.style.display = "none";
            oneoffFields.style.display = "block";
            document.getElementById("day_of_week")?.removeAttribute("required");
            document.getElementById("semester_id")?.removeAttribute("required");
            document.getElementById("booking_date")?.setAttribute("required", "required");
        }
    }

    if (periodicRadio && oneoffRadio) {
        periodicRadio.addEventListener("change", updateBookingType);
        oneoffRadio.addEventListener("change", updateBookingType);
        updateBookingType();
    }

    // 3. Timetable Grid Filter Auto-submit
    const timetableTypeSelect = document.getElementById("timetable-type-select");
    const timetableEntitySelect = document.getElementById("timetable-entity-select");
    if (timetableTypeSelect) {
        timetableTypeSelect.addEventListener("change", function () {
            document.getElementById("timetable-filter-form").submit();
        });
    }
    if (timetableEntitySelect) {
        timetableEntitySelect.addEventListener("change", function () {
            document.getElementById("timetable-filter-form").submit();
        });
    }
});

// Utility Confirmation Dialog for Cancellations
function confirmCancel(message) {
    return confirm(message || "Are you sure you want to cancel this lecture? The slot will be freed immediately.");
}
