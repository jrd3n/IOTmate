function updateFormAction(event) {
    event.preventDefault();

    const form = document.getElementById('addJobForm');
    
    const formData = new FormData(form);

    console.log(Array.from(formData.entries()));

    const jobNumberInput = document.querySelector('[name="job_number"]');
    const smo = jobNumberInput.value;
    const url = "/" + smo + "/data";

    const requestData = Object.fromEntries(formData.entries());

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    })
    .then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error submitting the form');
        }
    })
    .then((jsonResponse) => {
        console.log(jsonResponse);

        if (jsonResponse.success) {
            window.location.reload();
        } else {
            alert('Error: Could not submit the form.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function showJobModal(smo, jobInfo, onSave) {
    // Create the modal HTML
    const modalHTML = `
    <div class="modal fade" id="editJobModal" tabindex="-1" aria-labelledby="editJobModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="editJobModalLabel">Edit Job</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="editJobForm">
                        <!-- Form fields go here -->
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="saveChangesBtn">Save changes</button>
                </div>
            </div>
        </div>
    </div>
    `;

    // Insert the modal HTML into the DOM
    const modalWrapper = document.createElement("div");
    modalWrapper.innerHTML = modalHTML;
    document.body.appendChild(modalWrapper);

    // Get references to the modal and form elements
    const editJobModal = document.getElementById("editJobModal");
    const editJobForm = document.getElementById("editJobForm");

    // Populate the form fields
    editJobForm.querySelector("#job_number").value = jobInfo.job_number;
    editJobForm.querySelector("#client").value = jobInfo.client;
    editJobForm.querySelector("#standard").value = jobInfo.standard;

    // Save button click handler
    document.getElementById("saveChangesBtn").addEventListener("click", () => {
        // Call the provided onSave function
        onSave();
        // Close the modal
        const modalInstance = bootstrap.Modal.getInstance(editJobModal);
        modalInstance.hide();
    });

    // Show the modal
    const modalInstance = new bootstrap.Modal(editJobModal);
    modalInstance.show();
}
