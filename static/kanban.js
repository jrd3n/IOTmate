// JavaScript code to initialize dragula and handle dragging, dropping, and updating data.json

const columns = {
    "awaiting_samples": [],
    "onsite": [],
    "on_test": [],
    "report_stage": [],
    "report_sent": [],
    "disposal": [],
    "archive": []
}

function loadData() {
    console.log('Loading data...');
    fetch('/static/all_jobs.json')
        .then(response => response.json())
        .then(data => {
            console.log('Data received:', data);
            for (const key in data) {
                columns[key] = data[key];  // Merge the loaded data into the columns object
            }
            // console.log('Columns:', columns); // Log here, after the data has been assigned
            renderColumns(); // Call this here too
        })
        .catch(error => {
            console.error(`Error loading all_jobs.json: ${error}`);
        });
}

function renderColumns() {
    console.log('Rendering columns...');

    // console.log('Columns:', columns);
    for (const key in columns) {
        console.log(`Rendering column: ${key}`);
        const itemsEl = document.querySelector(`#${key}`);
        if (itemsEl) {
            itemsEl.innerHTML = '';

            columns[key].forEach(item => {
                console.log(`Rendering item: ${JSON.stringify(item)}`);
                const itemEl = document.createElement('div');
                itemEl.classList.add('kanban-item', 'job-tile');

                let progressBarHtml = '';
                let progressColorClass = 'bg-warning'; // Yellow color for less than 100% complete
                let progressValue = "";
                if (item["Percentage Complete"] !== undefined) {

                    if (item["Percentage Complete"] === 100) {
                        progressColorClass = 'bg-success'; // Green color for 100% complete
                    }

                    progressValue = item["Percentage Complete"].toFixed(2);
                }
                else {

                    progressValue = 0

                }

                progressBarHtml = `
                <div class="progress">
                    <div class="progress-bar ${progressColorClass}" role="progressbar" aria-valuenow="${progressValue}"
                        aria-valuemin="0" aria-valuemax="100" style="width: ${progressValue}%">
                        ${progressValue}%
                    </div>

                </div>`;

                itemEl.innerHTML = `
                    <a href="/${item.SMO}" style="text-decoration: none; color: inherit;">
                        <h5>SMO:${item.SMO}</h5>
                        <p>ER:${item.ER}</p>
                        <h5>${item["Client Name"]}</h5>
                        <div class="existing-info">
                            <!-- Existing information goes here -->
                        </div>
                        ${progressBarHtml}
                    </a>`;

                itemEl.dataset.job_number = item.SMO;

                itemsEl.appendChild(itemEl);
            });
        } else {
            console.error(`No element found for column: ${key}`);
        }
    }
}

function send_New_Status(SMO, new_Status) {

    const jobData = {
        Status: new_Status
    };

    // Send job data to the server
    fetch(`/${SMO}/data`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jobData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Job status updated successfully on the server');
            } else {
                console.error('Failed to update job status on the server');
            }
        })
        .catch(error => console.error('Error:', error));
}

const columnEls = document.querySelectorAll('#awaiting_samples, #onsite, #on_test, #report_stage, #report_sent, #disposal, #archive');

dragula(Array.from(columnEls))
    .on('drop', (el, target, source, sibling) => {

        console.log('Drop event triggered');

        const job_number = el.dataset.job_number;
        console.log(`Dragged job number: ${job_number}`);

        const oldStatus = source.id;
        const newStatus = target.id;
        console.log(`Old status: ${oldStatus}, New status: ${newStatus}`);

        send_New_Status(job_number, newStatus)

        // loadData()

    });

// dragula(Array.from(columnEls))
//     .on('drop', (el, target, source, sibling) => {

//         loadData();

//         console.log('Drop event triggered');

//         const job_number = el.dataset.job_number;



//         const oldStatus = source.id;
//         const newStatus = target.id;
//         console.log(`Old status: ${oldStatus}, New status: ${newStatus}`);

//         console.log('Old status:', oldStatus);
//         console.log('Columns at drop:', columns);

//         var onsiteItems = columns['onsite'].slice;
//         console.log(`onsite items`, onsiteItems)

//         const oldColumn = columns[oldStatus];
//         const newColumn = columns[newStatus];

//         console.log('Columns after:', columns);

//         console.log('Old column:', oldColumn);
//         console.log('New column:', newColumn);

//         const item = oldColumn.find(i => i.SMO === job_number);
//         console.log('Item found in old column:', item);

//         oldColumn.splice(oldColumn.indexOf(item), 1);

//         const newIndex = Array.from(target.children).indexOf(el);
//         console.log('New index:', newIndex);

//         if (sibling) {
//             const siblingJobNumber = sibling.dataset.job_number;
//             console.log(`Sibling job number: ${siblingJobNumber}`);

//             const siblingIndex = newColumn.findIndex(i => i.SMO === siblingJobNumber);
//             console.log('Sibling index:', siblingIndex);

//             newColumn.splice(siblingIndex, 0, item);
//         } else {
//             newColumn.push(item);
//         }

//         item.status = newStatus;
//         console.log('Updated item:', item);

//         // updateData();
//     });

document.addEventListener('DOMContentLoaded', () => {
    loadData();

});