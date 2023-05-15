$(document).ready(function () {
    console.log('modal.js loaded');

    // Create the modal HTML structure
    var modalHtml = `
        <div id="myModal" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="addJobModalLabel">Add/Edit Job</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addJobForm" method="POST" onsubmit="Add_or_change_job_info(event);">
                            <div class="mb-3">
                                <label for="smo" class="form-label">SMO</label>
                                <input type="text" class="form-control" id="job_number" name="job_number" required>
                            </div>
                            <div class="mb-3">
                                <label for="client" class="form-label">Client Name</label>
                                <input type="text" class="form-control" id="client" name="client">
                            </div>
                            <div class="mb-3">
                                <label for="er" class="form-label">ER number</label>
                                <input type="text" class="form-control" id="er" name="er">
                            </div>
                            <div class="mb-3">
                                <label for="standard" class="form-label">Standard</label>
                                <input type="text" class="form-control" id="standard" name="standard">
                            </div>

                            <div class="mb-3">
                                <label for="status" class="form-label">Status</label>
                                <select class="form-control" id="status" name="status">
                                    <option value="awaiting_samples">Awaiting Samples</option>
                                    <option value="onsite">Samples Onsite</option>
                                    <option value="on_test">On Test</option>
                                    <option value="report_stage">Report Stage</option>
                                    <option value="report_sent">Report Sent</option>
                                    <option value="disposal">Awaiting Disposal</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="test_data_file" class="form-label">Upload test_data.cvs</label>
                                <input type="file" class="form-control" id="test_data_file" accept=".cvs">
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="submit" class="btn btn-primary" form="addJobForm">Save changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>  
        </div>  
    `;

    // Append the modal HTML to the body of the document
    $('body').append(modalHtml);

    // Attach event handlers
    $('.open-modal-button').on('click', function () {
        console.log('Button clicked');

        if (smo !== "") {
            // Fetch data from the server
            fetch(`/${smo}/data`)
                .then(response => response.json())
                .then(data => {
                    // Update the modal with the received data
                    $('#job_number').val(data.job_number);
                    $('#client').val(data.client);
                    $('#status').val(data.status);
                    $('#er').val(data.er);
                    $('#standard').val(data.standard);
                    // Update other fields as needed
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });

            $('#job_number').prop('readonly', true);
        } else {
            $('#job_number').prop('readonly', false);
        }

        $('#myModal').modal('show');
    });

    // Close the modal when the user clicks outside of it
    $(window).on('click', function (event) {
        var modal = $('#myModal');
        if (event.target == modal[0]) {
            modal.modal('hide');
        }
    });

    // Close the modal when the user presses the Escape key
    $(document).on('keydown', function (event) {
        var modal = $('#myModal');
        if (event.key === 'Escape') {
            modal.modal('hide');
        }
    });
});

function Add_or_change_job_info(event) {
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

