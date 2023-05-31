# Kanban-webserver-with-PM

## install

```bash

    wget https://github.com/jrd3n/Kanban-webserver-with-PM/archive/refs/heads/master.zip
    unzip ./master.zip
    cd ./Kanban-webserver-with-PM-master/
    python3 -m venv ./venv
    mkdir ./data
    touch ./static/all_jobs.json
    source ./venv/bin/activate
    pip install -r ./requirements.txt
    python3 app.py

```
