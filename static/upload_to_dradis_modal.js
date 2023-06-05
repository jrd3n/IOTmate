var Dradis_Projects = [];
var Dradis_Project_Node = [];

$(document).ready(function () {

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
                                <select class="form-control" id="Dradis_job_name" name="Dradis_Name" required>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="node" class="form-label">Select Dradis Project Node</label>
                                <select class="form-control" id="Dradis_node_name" name="Dradis_Node" required>
                                </select>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="submit" class="btn btn-primary" id="upload_button" form="upload_to_dradis_form">Upload</button>
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

                // Add blank option at the top
                selectElement.append($('<option>', {
                    value: '',
                    text: ''
                }));

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

        // startFetchingConsoleOutput();

        $('#myDradisModal').modal('show');
    });

    $(document).ready(function() {
        $('#Dradis_job_name').on('change', function() {
            var selectedProject = return_project_ID();
            console.log('User selected: ', selectedProject);
    
            // Make the HTTP GET request to the '/dradis/project_ID/nodes' endpoint
            fetch(`/dradis/${selectedProject}/nodes`)
                .then(response => response.json())
                .then(data => {

                    Dradis_Project_Node = data;

                    var selectElement = $('#Dradis_node_name');
                    selectElement.empty();  // Clear existing options
    
                    // Add options to the select element
                    Dradis_Project_Node.forEach(node => {
                        selectElement.append($('<option>', {
                            // value: node.id,  // Replace 'id' with the actual property name
                            text: node.label  // Replace 'name' with the actual property name
                        }));
                    });
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        });
    });
    

    $('#myDradisModal').on('hidden.bs.modal', function () {
        stopFetchingConsoleOutput();
    });    

    // Close the modal when the user clicks outside of it
    $(window).on('click', function (event) {
        var modal = $('#myDradisModal');
        if (event.target == modal[0]) {
            modal.modal('hide');
            // stopFetchingConsoleOutput();
        }
    });

    // Close the modal when the user presses the Escape key
    $(document).on('keydown', function (event) {
        var modal = $('#myDradisModal');
        if (event.key === 'Escape') {
            modal.modal('hide');
            // stopFetchingConsoleOutput();
        }
    });
});

function return_project_ID(){

    const form = document.getElementById('upload_to_dradis_form');
    const formData = new FormData(form);
    const dradisName = formData.get('Dradis_Name');

    let jobId = null; // Define jobId with a default value

    const matchingProject = Dradis_Projects.find(project => project.name === dradisName);
    if (matchingProject) {
        project_ID = matchingProject.id;
        console.log('Job ID:', project_ID);

        // Continue with the code to submit the form to the server...
    } else {
        console.log('No matching project found for the provided name.');
    }

    return project_ID
}

function return_node_ID() {

    const form = document.getElementById('upload_to_dradis_form');
    const formData = new FormData(form);
    const Node_Name = formData.get('Dradis_Node');

    console.log(Node_Name);

    let node_ID = null; // Define jobId with a default value

    const matchingNode = Dradis_Project_Node.find(node => node.label === Node_Name);
    if (matchingNode) {
        node_ID = matchingNode.id;
        console.log('Node ID:', node_ID);

        // Continue with the code to submit the form to the server...
    } else {
        console.log('No matching node found for the provided name.');
    }

    return node_ID;
}


function Upload_to_dradis(event) {
    var uploadButton = document.getElementById('upload_button');
    uploadButton.disabled = true;
    uploadButton.classList.add('disabled');

    event.preventDefault();

    const form = document.getElementById('upload_to_dradis_form');
    const formData = new FormData(form);
    const dradisName = formData.get('Dradis_Name');

    const node_ID = return_node_ID();

    const url = '/dradis/upload';
    const data = {
        dradisName: dradisName,
        project_ID: return_project_ID(),
        node_ID: node_ID,
        smo: smo
    };

    console.log(data);

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error sending form data to server');
            }
            return response.json();
        })
        .then(responseData => {
            if (responseData.error) {
                throw new Error(responseData.error);
            }
            // Handle the response from the server as needed
            console.log('Response from server:', responseData);
            alert("Upload successful!");
        })
        .catch(error => {
            console.error('Error sending form data to server:', error);
            alert("Error sending form data to server: " + error.message);
        })
        .finally(() => {
            uploadButton.disabled = false;
            uploadButton.classList.remove('disabled');
        });
}
