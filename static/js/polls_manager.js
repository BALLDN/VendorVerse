document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("addOptionBtn")
    .addEventListener("click", addOptionHandler);

  document
    .getElementById("options_container")
    .addEventListener("click", function (e) {
      e.preventDefault();
      if (e.target.classList.contains("remove-btn")) {
        const btnRemove = e.target;
        btnRemove.parentElement.remove();
      }
      if (e.target.classList.contains("bi")) {
        const btnRemove = e.target.parentElement;
        btnRemove.parentElement.remove();
      }
    });

  document
    .getElementById("vendor_checkbox")
    .addEventListener("click", function () {
      document.getElementById("vendor_name_section").toggleAttribute("hidden");
    });
});

let optionCount = 2; // Initialize with the count of existing options

function addOptionHandler() {
  optionCount++;
  const inputContainer = this.parentElement;

  const newInputGroup = document.createElement("div");
  newInputGroup.className = "input-group mb-3";

  // Create the input element
  const newInput = document.createElement("input");
  newInput.type = "text";
  newInput.id = `option_${optionCount}`;
  newInput.name = `option_${optionCount}`;
  newInput.className = "form-control form-control-md";
  newInput.placeholder = "option";
  newInput.required = true;

  // Create the button element
  const newButton = document.createElement("button");
  newButton.className = "btn btn-outline-secondary remove-btn";
  newButton.type = "button";
  newButton.innerHTML = '<i class="bi bi-x"></i>';

  // Append the input and button to the input group
  newInputGroup.appendChild(newInput);
  newInputGroup.appendChild(newButton);

  // Insert the new input group above the "Add Option" button
  inputContainer.insertBefore(newInputGroup, this);

  // Add event listener to the new remove button
  newButton.addEventListener("click", function () {
    inputContainer.removeChild(newInputGroup);
  });
}
