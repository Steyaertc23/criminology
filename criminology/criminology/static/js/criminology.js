// ───────────── Search Redirect ─────────────
function redirectToSearch(form) {
  const input = document.getElementById("searchCriminalName");
  const criminalName = input.value.trim();
  if (!criminalName) return false;
  const encodedCriminalName = encodeURIComponent(criminalName);
  window.location.href = `/search/${encodedCriminalName}/`;
  return false; // prevent default form submission
}

// ───────────── CSV File Validation ─────────────
document.addEventListener("DOMContentLoaded", function () {
  const csvInput = document.getElementById("csvFileInput");
  if (csvInput) {
    csvInput.addEventListener("change", function () {
      const file = this.files[0];
      if (!file) return;

      const MAX_SIZE = 2 * 1024 * 1024; // 2MB
      if (file.size > MAX_SIZE) {
        alert("File is too large. Please upload a file smaller than 2MB.");
        csvInput.value = "";
        return;
      }

      const reader = new FileReader();
      reader.onload = function (e) {
        const firstLine = e.target.result.split(/\r?\n/)[0].trim();
        const expected = "first_name,last_name,offense_type,offense_class,description,offense_source";
        if (firstLine.toLowerCase() !== expected.toLowerCase()) {
          alert("CSV header is invalid. Expected:\n" + expected);
          csvInput.value = "";
        }
      };
      reader.readAsText(file);
    });
  }
});

// ───────────── Load More Criminals ─────────────
async function loadMoreCriminals(button) {
  const groupId = button.dataset.group;
  const offset = parseInt(button.dataset.offset);
  const label = button.dataset.label;
  const list = document.getElementById(`list-${groupId}`);

  try {
    const response = await fetch(
      `/load_more_criminals/?label=${encodeURIComponent(label)}&offset=${offset}`
    );
    const data = await response.json();

    data.criminals.forEach((criminal, index) => {
      const li = document.createElement("li");
      const globalIndex = offset + index;
      li.className = `list-group-item ${globalIndex % 2 === 0 ? "list-group-item-light" : ""}`;
      li.textContent = `${criminal.first_name} ${criminal.last_name} - ${criminal.offense_type} ${criminal.offense_class}`;
      list.appendChild(li);
    });

    if (data.has_more) {
      button.dataset.offset = offset + data.criminals.length;
    } else {
      button.remove();
    }
  } catch (err) {
    console.error("Failed to load more criminals:", err);
  }
}

// ───────────── Dynamic Offense Class Update ─────────────
const CLASS_OPTIONS = {
  federal: {
    Felony: [
      { value: "A", label: "Class A" },
      { value: "B", label: "Class B" },
      { value: "C", label: "Class C" },
      { value: "D", label: "Class D" },
      { value: "E", label: "Class E" }
    ],
    Misdemeanor: [
      { value: "A", label: "Class A" },
      { value: "B", label: "Class B" },
      { value: "C", label: "Class C" }
    ],
    Infraction: [
      { value: "NA", label: "Infraction" }
    ]
  },
  virginia: {
    Felony: [
      { value: "1", label: "Class 1" },
      { value: "2", label: "Class 2" },
      { value: "3", label: "Class 3" },
      { value: "4", label: "Class 4" },
      { value: "5", label: "Class 5" },
      { value: "6", label: "Class 6" }
    ],
    Misdemeanor: [
      { value: "1", label: "Class 1" },
      { value: "2", label: "Class 2" },
      { value: "3", label: "Class 3" },
      { value: "4", label: "Class 4" }
    ],
    Infraction: [
      { value: "NA", label: "Infraction" }
    ]
  }
};

function updateOffenseClassOptions(selectedValue = null) {
  const sourceField = document.getElementById("id_offense_source");
  const typeField = document.getElementById("id_offense_type");
  const classSelect = document.getElementById("id_offense_class");

  if (!sourceField || !typeField || !classSelect) return;

  const source = sourceField.value;
  const type = typeField.value;

  const options = CLASS_OPTIONS[source]?.[type] || [];

  // Clear old options
  classSelect.innerHTML = "";

  options.forEach(opt => {
    const optionEl = document.createElement("option");
    optionEl.value = opt.value;
    optionEl.textContent = opt.label;
    classSelect.appendChild(optionEl);
  });

  // Restore previous selection if available
  if (selectedValue) {
    classSelect.value = selectedValue;
    if (classSelect.value !== selectedValue) {
      classSelect.selectedIndex = 0;
    }
  }

  // Disable for Infraction
  if (type === "Infraction") {
    classSelect.disabled = true;
  } else {
    classSelect.disabled = false;
  }
}

// ───────────── Initialize on DOM Load ─────────────
document.addEventListener("DOMContentLoaded", () => {
  const sourceSelect = document.getElementById("id_offense_source");
  const typeSelect = document.getElementById("id_offense_type");
  const classSelect = document.getElementById("id_offense_class");

  if (!sourceSelect || !typeSelect || !classSelect) return;

  const selectedClass = classSelect.getAttribute("data-selected");

  sourceSelect.addEventListener("change", () => updateOffenseClassOptions());
  typeSelect.addEventListener("change", () => updateOffenseClassOptions());

  updateOffenseClassOptions(selectedClass);
});
