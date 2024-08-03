document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");
  const myModal = new bootstrap.Modal(document.getElementById("form"), {});
  const close = document.querySelector(".btn-close");

  // Fetch bookings and store in localStorage
  fetch("/booking/calendar")
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
        title: `${event["Additional Info"]}\nby ${
          event["Vendor_Name"] || event["Vendor_ID"]
        }`,
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

        dateInput.value = event.Date;
        locationInput.value = event.Location;
        dealInput.value = event.Deal;
        additionalInfoInput.value = `${event["Additional Info"]} by ${
          event["Vendor_Name"] || event["Vendor_ID"]
        }`;

        myModal.show();
      },
    });

    calendar.render();
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
