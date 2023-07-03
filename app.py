from flask import Flask, render_template, request, jsonify, url_for,redirect, send_file
from werkzeug.utils import secure_filename
from lib.file_manager import *
import zipfile

api_token = 'gszaZ8EiynJB6ipzPqzA'

app = Flask(__name__, static_url_path='/static')

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

    # print(upload_folder)

    app.config['UPLOAD_FOLDER'] = upload_folder

    def save_file(file, upload_folder):
        # Save the uploaded file
        filename = secure_filename(file.filename)

        # Make sure the upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file.save(os.path.join(upload_folder, filename))

        return os.path.join(upload_folder, filename)
    
    if 'file[]' in request.files:
        print("OTHER FILES")
        for file in request.files.getlist('file[]'):
            if file:
                save_file(file, upload_folder)

    next_url = request.form.get('next') or url_for('default_route')
    return redirect(next_url)

@app.route('/<smo>/create_report', methods=['POST'])
def create_report(smo):
   
    folder_path = 'data/{smo}/'.format(smo=smo)
    file_name = 'test_data.xlsx'

    all_tests_json = read_json_from_excel(folder_path,file_name)

    # print(all_tests_json)

    generate_report(test_json=all_tests_json,report_output_file_path="{folder_path}/testnotes_{smo}.docx".format(folder_path=folder_path,smo=smo))

    # Process the message and create the report
    # ...
    # Return a response indicating the success or any relevant information
    return jsonify({'success': True, 'message': 'Report created successfully.'})


@app.route('/<smo>/zip_pictures', methods=['POST'])
def zip_pictures(smo):
    main_folder = f'data/{smo}/'
    output_zip = f'data/{smo}/{smo}_pictures.zip'

    # Check if the main folder exists
    if not os.path.exists(main_folder):
        return "Main folder does not exist."

    # Create a new zip file
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        # Traverse through all subfolders and files
        for root, dirs, files in os.walk(main_folder):
            for file in files:
                # Check if the file is a picture (you can modify this condition to match your specific criteria)
                if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Get the full path of the file
                    file_path = os.path.join(root, file)
                    # Get the subfolder name
                    subfolder_name = os.path.basename(root)
                    # Generate the new filename with the prefix
                    # Get the original filename without the subdirectory prefix
                    _, original_filename = os.path.split(file_path)

                    new_filename = f"{subfolder_name}_{original_filename}"
                    # # Add the file to the zip with the new filename
                    # zipf.write(file_path, os.path.join(subfolder_name, new_filename))

                    # Add the file to the zip with the original filename
                    zipf.write(file_path, new_filename)

    # Send the zip file as a response for download
    return send_file(output_zip, as_attachment=True)

@app.route('/<smo>/<test>', methods=['GET'])
def test_form(smo, test):
    test_number = test
    folder_path = f'data/{smo}/'

    all_test_data = read_json_from_excel(folder_path, file_name="test_data.xlsx")

    job_info = read_json_from_excel(folder_path=folder_path,file_name="job_information.xlsx")

    filtered_test = [test for test in all_test_data if test["Number"].strip() == test_number]

    if filtered_test:  # check if the filtered_test list is not empty
        filtered_test = filtered_test[0]  # Get the first (and should be the only) item in the list
    else:
        print(f"No test with Number: {test_number} found.")

    app.config['UPLOAD_FOLDER'] = f'data/{smo}/{test_number}/'

    files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []

    return render_template('test_form.html', test_data=filtered_test, smo=smo, job_info=job_info, files=files)

    # Retrieve the message data from the request
from lib.word_report import generate_report

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

    print(files)

    job_info = read_json_from_excel(folder_path=folder_path,file_name="job_information.xlsx")

    print(job_info)

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

        print(job_data)

        return jsonify(job_data)
        
    elif request.method == 'POST':

        new_data = request.json

        print("SMO: {smo} new data {new_data}".format(smo=smo,new_data=new_data))

        written_bool = write_json_to_excel(job_file_path,'job_information.xlsx',new_data,smo)

        if written_bool == True:
            return jsonify({'success': True})       

@app.route('/dradis/projects', methods=['GET'])
def dradis_jobs():
    from lib.dradis_API_funcs import projects_get_all

    all_dradis_jobs = projects_get_all(api_token=api_token)

    return jsonify(all_dradis_jobs)

from lib.dradis_API_funcs import nodes_get_all

@app.route('/dradis/<project_ID>/nodes', methods=['GET'])
def dradis_nodes(project_ID):

    nodes = nodes_get_all(api_token=api_token, project_ID=project_ID)

    #print(nodes)

    return jsonify(nodes)

from lib.dradis_API_funcs import issue_write, evidence_write

console = ""

@app.route('/dradis/upload', methods=['POST'])
def dradis_upload():
    try:
        # Access the JSON data

        data = request.get_json()

        node_ID = data.get('node_ID')
        project_ID = data.get('project_ID')
        smo = data.get('smo')

        folder_path = 'data/{smo}/'.format(smo=smo)
        file_name = 'test_data.xlsx'

        all_tests_json = read_json_from_excel(folder_path, file_name)

        for test_row_json in all_tests_json:
            
            test_number = test_row_json.get('Number')

            print("Writing {}...".format(test_number))

            # Get issue ID and Evidence ID from sheet
            Dradis_issue_ID = test_row_json.get('Dradis_issue_ID')
            Dradis_evidence_ID = test_row_json.get('Dradis_evidence_ID')

            Dradis_issue_ID = issue_write(api_token,project_ID,test_row_json, Dradis_issue_ID)

            #Write new Dradis_issue_ID to excel
            new_data = {'Dradis_issue_ID': Dradis_issue_ID}
            write_json_to_excel(folder_path,file_name,new_data,test_number)

            # Write evidence
            Dradis_evidence_ID = evidence_write(api_token, project_ID, test_row_json, node_ID, Dradis_evidence_ID, Dradis_issue_ID)

            #Write new Dradis_evidence_ID to excel
            new_data = {'Dradis_evidence_ID': Dradis_evidence_ID}
            write_json_to_excel(folder_path,file_name,new_data,test_number)

        return jsonify({"message": "Data uploaded to Dradis Pro successfully."})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True , port=5000)