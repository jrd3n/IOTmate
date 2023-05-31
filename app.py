from flask import Flask, render_template, request, jsonify, url_for,redirect, send_file
from werkzeug.utils import secure_filename
import openpyxl
import pandas as pd
import json
import os

app = Flask(__name__, static_url_path='/static')

import pandas as pd

def update_all_jobs_json():
    data_dir = 'data/'

    columns = {
        "awaiting_samples": [],
        "onsite": [],
        "on_test": [],
        "report_stage": [],
        "report_sent": [],
        "disposal": [],
        "archive": []
    }

    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)

        if os.path.isdir(folder_path):
            job_data = read_json_from_excel(folder_path, 'job_information.xlsx')  # Assuming you have a function to read job data from an Excel file
            status = job_data[0].get("Status", "")

            if status in columns:
                columns[status].append(job_data[0])
            else:
                columns["archive"].append(job_data[0])

    # Write columns to all_jobs.json
    with open('static/all_jobs.json', 'w') as json_file:
        json.dump(columns, json_file)

def write_json_to_excel(folder_path, file_name, new_data, index_value):
    full_file_path = os.path.join(folder_path, file_name)

    # Check if the directory exists, if not, create it
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Directory {folder_path} created ")
        except Exception as e:
            print("Error while creating directory: ", e)
           # return False

    # If the Excel file does not exist, create a new one with all data
    if not os.path.exists(full_file_path):
        print("HERE: {smo} new data {new_data}".format(smo=index_value,new_data=new_data))
        df = pd.DataFrame([new_data])
        ##df.set_index(index_value, inplace=True)
        print(df)
        df.to_excel(full_file_path, index=False)
        update_all_jobs_json()
        print(df.head())
        return True

    # Load the Excel file into a DataFrame, using the first column as the index and as a string type
    df = pd.read_excel(full_file_path, index_col=0, dtype={0: str})

    # Strip white spaces from index
    df.index = df.index.str.strip()

    # Replace all NaN values with an empty string
    df = df.fillna("")

    # Now you can locate the row to update using the DataFrame index
    row_to_update = df.index.astype(str) == str(index_value)

    # Assuming new_data is a dictionary like {"column1": value1, "column2": value2}
    for column, value in new_data.items():
        df.loc[row_to_update, column] = value

    # Write the DataFrame back to the Excel file, keeping the DataFrame index
    try:
        df.to_excel(full_file_path, index=True)
        update_all_jobs_json()
        return True
    except Exception as e:
        print("Error while writing to Excel: ", e)
        return False

def read_json_from_excel(folder_path,file_name):

    full_file_path = os.path.join(folder_path, file_name)
    if os.path.exists(full_file_path):

        # Load the Excel file
        df = pd.read_excel(full_file_path)

        # Replace all NaN values with an empty string
        df = df.fillna("")

        # Convert the DataFrame back to a dictionary
        data = df.to_dict(orient='records')

        #print(data)

        return data

    else:
        print("ERROR NO FILE NAMED {file_name} in folder {folder_path}".format(file_name=file_name,folder_path=folder_path))
        return []
        pass

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_upload():

    smo = request.form.get('smo')
    test = request.form.get('test')

    print('{smo} and test {test}'.format(smo=smo, test=test))

    if test != "":
        upload_folder = f'data/{smo}/{test}/'
    else:
        upload_folder = f'data/{smo}/'

    print(upload_folder)
   
    app.config['UPLOAD_FOLDER'] = upload_folder

    def save_file(file, upload_folder):
    # Save the uploaded file
        filename = secure_filename(file.filename)

        # Make sure the upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file.save(os.path.join(upload_folder, filename))

        return os.path.join(upload_folder, filename)

    if 'file' in request.files:
        print("OTHER FILE")
        other_file = request.files['file']
        if other_file:
            save_file(other_file, upload_folder)

    next_url = request.form.get('next') or url_for('default_route')
    return redirect(next_url)

@app.route('/<smo>/<test>', methods=['GET'])
def test_form(smo, test):
    test_number = test
    folder_path = f'data/{smo}/'

    all_test_data = read_json_from_excel(folder_path, file_name="test_data.xlsx")
    job_data = read_json_from_excel(folder_path, 'job_information.xlsx')

    filtered_test = [test for test in all_test_data if test["Number"].strip() == test_number]

    if filtered_test:  # check if the filtered_test list is not empty
        filtered_test = filtered_test[0]  # Get the first (and should be the only) item in the list
    else:
        print(f"No test with Number: {test_number} found.")

    app.config['UPLOAD_FOLDER'] = f'data/{smo}/{test_number}/'

    files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []

    return render_template('test_form.html', test_data=filtered_test, smo=smo, job_info=job_data, files=files)

@app.route('/<smo>/<test>', methods=['POST'])
def test_form_submission(smo, test):
    test_number = test
    folder_path = f'data/{smo}/'

    new_data = request.json

    print("SMO: {smo}, test :{test}, new data {new_data}".format(smo=smo,test=test,new_data=new_data))

    written_bool = write_json_to_excel(folder_path, 'test_data.xlsx', new_data, test)

    def calc_percent_complete(tests):
        total_jobs = len(tests)
        blank_conclusion_count = sum(1 for item in tests if item['Conclusion'] != '')

        percentage_complete = (blank_conclusion_count / total_jobs) * 100

        print(percentage_complete)

        return percentage_complete

    all_test_data = read_json_from_excel(folder_path, file_name="test_data.xlsx")
    percentage_complete = calc_percent_complete(all_test_data)

    new_data = {'Percentage Complete': percentage_complete}

    written_bool = write_json_to_excel(folder_path,'job_information.xlsx',new_data,smo)

    return redirect(url_for('test_form', smo=smo, test=test_number))

@app.route('/<smo>')
def test_toc(smo):
    folder_path = f'data/{smo}/'
    tests = read_json_from_excel(folder_path=folder_path,file_name="test_data.xlsx")

    # After line where app.config['UPLOAD_FOLDER'] is set
    app.config['UPLOAD_FOLDER'] = f'data/{smo}/'
    
    # List all files in upload directory
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    else:
        files = []

    job_info = read_json_from_excel(folder_path=folder_path,file_name="job_information.xlsx")

    return render_template('test_toc.html', tests=tests, smo=smo, job_info=job_info, files=files)

@app.route('/<smo>/<test>/download/<filename>')
def download_file_from_test(filename,smo,test):

    filepath = f'data/{smo}/{test}/{filename}'

    return send_file(filepath, as_attachment=True) 

@app.route('/<smo>/download/<filename>')
def download_file_from_job(filename,smo):

    filepath = f'data/{smo}/{filename}'

    return send_file(filepath, as_attachment=True)

@app.route('/<smo>/data', methods=['GET', 'POST'])
def data(smo):

    job_file_path = f'data/{smo}/'

    if request.method == 'GET':

        job_data = read_json_from_excel(job_file_path,'job_information.xlsx')

        return jsonify(job_data)
        
    elif request.method == 'POST':

        new_data = request.json

        print("SMO: {smo} new data {new_data}".format(smo=smo,new_data=new_data))

        written_bool = write_json_to_excel(job_file_path,'job_information.xlsx',new_data,smo)

        if written_bool == True:
            return jsonify({'success': True})       

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True , port=5000)