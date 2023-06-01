$(document).ready(function () {
    // Function to retrieve console output from Flask server
    function getConsoleOutput() {
        fetch('/get_console_output') // Flask route to fetch console output
            .then(response => response.text())
            .then(data => {
                // Update the element with the received console output
                $('#console-output').text(data);
            })
            .catch(error => {
                console.error('Error fetching console output:', error);
            });
    }
    // Function to start fetching console output
    function startFetchingConsoleOutput() {
        // Start fetching console output at an interval
        consoleOutputInterval = setInterval(getConsoleOutput, 1000);
    }

    // Function to stop fetching console output
    function stopFetchingConsoleOutput() {
        clearInterval(consoleOutputInterval);
    }

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
                                <select class="form-control" id="Dradis_job_name" name="Dradis_Name">
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
                // console.log(Dradis_Projects);

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

        startFetchingConsoleOutput();

        $('#myDradisModal').modal('show');
    });

    // Close the modal when the user clicks outside of it
    $(window).on('click', function (event) {
        var modal = $('#myDradisModal');
        if (event.target == modal[0]) {
            modal.modal('hide');
            stopFetchingConsoleOutput();
        }
    });

    // Close the modal when the user presses the Escape key
    $(document).on('keydown', function (event) {
        var modal = $('#myDradisModal');
        if (event.key === 'Escape') {
            modal.modal('hide');
            stopFetchingConsoleOutput();
        }
    });
});

function Upload_to_dradis(event) {
    event.preventDefault();

    const form = document.getElementById('upload_to_dradis_form');
    const formData = new FormData(form);
    const dradisName = formData.get('Dradis_Name');

    let jobId = null; // Define jobId with a default value

    const matchingProject = Dradis_Projects.find(project => project.name === dradisName);
    if (matchingProject) {
        jobId = matchingProject.id;
        console.log('Job ID:', jobId);

        // Continue with the code to submit the form to the server...
    } else {
        console.log('No matching project found for the provided name.');
    }

    const url = '/dradis/projects';
    const data = {
        dradisName: dradisName,
        jobId: jobId,
        smo: smo
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(responseData => {
            // Handle the response from the server as needed
            console.log('Response from server:', responseData);
        })
        .catch(error => {
            console.error('Error sending form data to server:', error);
        });
}
