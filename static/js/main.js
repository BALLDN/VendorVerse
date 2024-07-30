document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");
  const myModal = new bootstrap.Modal(document.getElementById("form"));
  const close = document.querySelector(".btn-close");

  // Fetch bookings and store in localStorage
  fetch("/get_bookings_for_calendar")
    .then((response) => response.json())
    .then((bookings) => {
      localStorage.setItem("events", JSON.stringify(bookings));
      initializeCalendar(bookings);
    })
    .catch((error) => console.error("Error fetching bookings:", error));

  function initializeCalendar(events) {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      height: "100%",
      headerToolbar: {
        center: "customButton",
        right: "today,prev,next",
      },
      plugins: ["dayGrid", "interaction"],
      events: events.map((event) => ({
        id: event.id,
        title: `${event["Vendor_Name"]}`,
        start: event.Date,
        backgroundColor: getRandomRGB(),
        allDay: true,
        editable: false,
      })),
      eventClick: function (info) {
        // Fetch the latest events data from localStorage
        const events = JSON.parse(localStorage.getItem("events")) || [];
        const event = events.find((e) => e.id === info.event.id);

        // Populate the modal fields with the latest event data
        const dateInput = document.getElementById("date");
        const locationInput = document.getElementById("location");
        const dealInput = document.getElementById("deal");
        const additionalInfoInput = document.getElementById("additional-info");
        const submitButton = document.getElementById("submit-button");
        const eventIdInput = document.getElementById("event-id");

        dateInput.value = event.Date;
        locationInput.value = event.Location;
        dealInput.value = event.Deal;
        additionalInfoInput.value = event["Additional Info"];
        eventIdInput.value = event.id;
        submitButton.innerHTML = "Save changes";

        myModal.show();
      },
    });

    calendar.render();

    // Form submission logic
    document
      .getElementById("booking-form")
      .addEventListener("submit", function (event) {
        event.preventDefault();

        const dateInput = document.getElementById("date").value;
        const locationInput = document.getElementById("location").value;
        const dealInput = document.getElementById("deal").value;
        const additionalInfoInput =
          document.getElementById("additional-info").value;
        const eventIdInput = document.getElementById("event-id").value;

        const updatedEvent = {
          id: eventIdInput,
          Date: dateInput,
          Location: locationInput,
          Deal: dealInput,
          "Additional Info": additionalInfoInput,
        };

        // Update local storage
        let events = JSON.parse(localStorage.getItem("events")) || [];
        const eventIndex = events.findIndex((e) => e.id === updatedEvent.id);
        if (eventIndex !== -1) {
          events.splice(eventIndex, 1, updatedEvent);
        } else {
          events.push(updatedEvent);
        }
        localStorage.setItem("events", JSON.stringify(events));

        // Update the calendar event
        let calendarEvent = calendar.getEventById(updatedEvent.id);
        if (calendarEvent) {
          calendarEvent.remove();
        }
        calendar.addEvent({
          id: updatedEvent.id,
          title: updatedEvent["Additional Info"],
          start: updatedEvent.Date,
          backgroundColor: "blue",
          allDay: true,
        });

        myModal.hide();
      });
  }

  function getRandomRGB() {
    // Generate random values for red, green, and blue (0-255)
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);

    // Return the RGB color string
    return `rgb(${r}, ${g}, ${b})`;
  }
});
