document.addEventListener("DOMContentLoaded", (event) => {
  document
    .getElementById("bookings_container")
    .addEventListener("click", function (e) {
      if (e.target && e.target.classList.contains("edit-btn")) {
        const bookingId = e.target.getAttribute("data-booking-id");
        populateModal(bookingId);
      }
      if (e.target && e.target.classList.contains("cancel-btn")) {
        const bookingId = e.target.getAttribute("data-booking-id");
        const url = "/booking/" + bookingId;
        document
          .getElementById("frm_cancel")
          .setAttribute("action", `${url}/cancel`);
      }
    });
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
