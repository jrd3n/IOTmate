// JavaScript code to initialize dragula and handle dragging, dropping, and updating data.json

const columns = {
    "awaiting_samples": [],
    "onsite": [],
    "on_test": [],
    "report_stage": [],
    "report_sent": [],
    "disposal": []
}

function loadData() {
    console.log('Loading data...');
    fetch('/all_jobs')
        .then(response => response.json())
        .then(data => {
            console.log('Data received:', data);
            data.forEach(item => {
                console.log(`Processing item: ${JSON.stringify(item)}`);
                if (columns.hasOwnProperty(item.status)) {
                    columns[item.status].push(item);
                } else {
                    console.error(`Unknown status: ${item.status}`);
                }
            });
            renderColumns();
        });
}

function renderColumns() {
    console.log('Rendering columns...');
    for (const key in columns) {
        console.log(`Rendering column: ${key}`);
        const itemsEl = document.querySelector(`#${key}`);
        if (itemsEl) {
            itemsEl.innerHTML = '';

            columns[key].forEach(item => {
                console.log(`Rendering item: ${JSON.stringify(item)}`);
                const itemEl = document.createElement('div');
                itemEl.classList.add('kanban-item', 'job-tile');
                itemEl.innerHTML = `
                  <a href="/${item.job_number}" style="text-decoration: none; color: inherit;">
                    <h5>SMO:${item.job_number}</h5>
                    <p>ER:${item.er}</p>
                    <h5>${item.client}</h5>
                  </a>`;
                itemEl.dataset.job_number = item.job_number;

                itemsEl.appendChild(itemEl);
            });
        } else {
            console.error(`No element found for column: ${key}`);
        }
    }
}


function updateData() {
    const allData = [];
    for (const key in columns) {
        console.log(`Processing column: ${key}`); // Diagnostic
        columns[key].forEach(item => {
            item.status = key;
            const smo = item.job_number

            fetch(`/${smo}/data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(item)
            })
                .then(response => {
                    console.log(`Server response: ${JSON.stringify(response)}`); // Diagnostic
                    return response.json();
                })
                .then(result => {
                    if (result.success) {
                        console.log('Data updated successfully.');
                    } else {
                        console.error('Failed to update data.');
                    }
                })
                .catch(error => {
                    console.error(`Error during fetch: ${error}`); // Diagnostic
                });

        });
    }


}


const columnEls = document.querySelectorAll('#awaiting_samples, #onsite, #on_test, #report_stage, #report_sent, #disposal');

dragula(Array.from(columnEls))
    .on('drop', (el, target, source, sibling) => {
        console.log('Drop event triggered');

        const job_number = el.dataset.job_number;
        console.log(`Dragged job number: ${job_number}`);

        const oldStatus = source.id;
        const newStatus = target.id;
        console.log(`Old status: ${oldStatus}, New status: ${newStatus}`);

        const oldColumn = columns[oldStatus];
        const newColumn = columns[newStatus];

        const item = oldColumn.find(i => i.job_number === job_number);
        console.log(`Item found in old column: ${JSON.stringify(item)}`);

        oldColumn.splice(oldColumn.indexOf(item), 1);

        const newIndex = Array.from(target.children).indexOf(el);
        console.log(`New index: ${newIndex}`);

        if (sibling) {
            const siblingJobNumber = sibling.dataset.job_number;
            console.log(`Sibling job number: ${siblingJobNumber}`);

            const siblingIndex = newColumn.findIndex(i => i.job_number === siblingJobNumber);
            console.log(`Sibling index: ${siblingIndex}`);

            newColumn.splice(siblingIndex, 0, item);
        } else {
            newColumn.push(item);
        }

        item.status = newStatus;
        console.log(`Updated item: ${JSON.stringify(item)}`);

        updateData();
    });


document.addEventListener('DOMContentLoaded', () => {
    loadData();
});