$(document).ready(function () {
    console.log('upload_to_dradis_modal.js loaded');

    // Function to retrieve console output from Flask server
    function getConsoleOutput() {
        $.ajax({
            url: '/get_console_output', // Flask route to fetch console output
            type: 'GET',
            success: function (response) {
                // Update the element with the received console output
                $('#console-output').text(response);
            },
            error: function (error) {
                console.error('Error fetching console output:', error);
            }
        });
    }

    // Function to stop retrieving console output
    function stopConsoleOutput() {
        clearInterval(consoleOutputInterval);
    }

    // Submit form handler
    $('#upload_to_dradis_form').on('submit', function (event) {
        event.preventDefault();

        // Make the AJAX request to save form data
        $.ajax({
            url: '/submit_form', // Flask route to handle form submission
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                // Start retrieving console output
                getConsoleOutput();

                // Stop retrieving console output after 10 seconds
                setTimeout(stopConsoleOutput, 10000);
            },
            error: function (error) {
                console.error('Error submitting the form:', error);
            }
        });
    });
    
        var consoleOutputInterval;

    // Create the modal HTML structure
    var modalHtml = `
        <div id="myDradisModal" class="modal fade" tabindex="-1" style="z-index: 3000;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="addJobModalLabel">Dradis Uploader</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="upload_to_dradis_form" method="POST" onsubmit="Upload_to_dradis(event);">
                            <div class="mb-3">
                                <label for="Project" class="form-label">Select Dradis Project</label>
                                <select class="form-control" id="Dradis_job_name" name="">
                                </select>
                            </div>
                            <div id="console-output" style="background-color: black; color: white; font-family: monospace; padding: 10px; overflow: auto; height: 200px; border: 1px solid #ccc; border-radius: 5px;"></div>

                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="submit" class="btn btn-primary" form="upload_to_dradis_form">Upload</button>
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
    $('.open-dradis-modal-button').on('click', function () {
        console.log('Button clicked');

        fetch(`/dradis/projects`)
            // console.log("Hello")
            .then(response => response.json())
            .then(data => {

                Dradis_Projects = data;
                console.log(Dradis_Projects);

                // Update the modal with the received data
                var selectElement = $('#Dradis_job_name');
                selectElement.empty(); // Clear existing options

                // Add options to the select element
                Dradis_Projects.forEach(project => {
                    selectElement.append($('<option>', {
                        value: project.name,
                        text: project.name
                    }));
                });
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });

        $('#myDradisModal').modal('show');
    });

    // Close the modal when the user clicks outside of it
    $(window).on('click', function (event) {
        var modal = $('#myDradisModal');
        if (event.target == modal[0]) {
            modal.modal('hide');
        }
    });

    // Close the modal when the user presses the Escape key
    $(document).on('keydown', function (event) {
        var modal = $('#myDradisModal');
        if (event.key === 'Escape') {
            modal.modal('hide');
        }
    });
});

function Upload_to_dradis(event) {
    event.preventDefault();

    const form = document.getElementById('upload_to_dradis_form');

    const formData = new FormData(form);

    console.log("HERE")

    console.log(Array.from(formData.entries()));

    const url = "/" + smo + "/data";

    // const requestData = Object.fromEntries(formData.entries());

    // fetch(url, {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(requestData),
    // })
    //     .then((response) => {
    //         if (response.ok) {
    //             return response.json();
    //         } else {
    //             throw new Error('Error submitting the form');
    //         }
    //     })
    //     .then((jsonResponse) => {
    //         console.log(jsonResponse);

    //         if (jsonResponse.success) {
    //             window.location.reload();
    //         } else {
    //             alert('Error: Could not submit the form.');
    //         }
    //     })
    //     .catch((error) => {
    //         console.error('Error:', error);
    //     });
}