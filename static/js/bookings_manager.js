document.addEventListener("DOMContentLoaded", (event) => {
  document
    .getElementById("bookings_container")
    .addEventListener("click", function (e) {
      if (e.target && e.target.classList.contains("edit-btn")) {
        const bookingId = e.target.getAttribute("data-booking-id");
        if (isValidBookingId(bookingId)) {
          populateModal(bookingId);
        } else {
          console.error("Invalid booking ID");
        }
      }
      if (e.target && e.target.classList.contains("cancel-btn")) {
        const bookingId = e.target.getAttribute("data-booking-id");
        if (isValidBookingId(bookingId)) {
          const sanitizedBookingId = encodeURIComponent(bookingId);
          const url = `/booking/${sanitizedBookingId}`;
          document
            .getElementById("frm_cancel")
            .setAttribute("action", `${url}/cancel`);
        } else {
          console.error("Invalid booking ID");
        }
      }
    });

  function isValidBookingId(bookingId) {
    return /^[a-zA-Z0-9_-]+$/.test(bookingId);
  }
});

function populateModal(bookingId) {
  const url = "/booking/" + bookingId;
  fetch(url)
    .then(function (response) {
      return response.json();
    })
    .then(function (booking) {
      document.getElementById("frm_edit").setAttribute("action", `${url}/edit`);
      document.getElementById("title").value = booking["Title"];
      document.getElementById("date").value = booking["Date"];
      document.getElementById("location").value = booking["Location"];
      document.getElementById("deal").value = booking["Deal"];
    });
}
