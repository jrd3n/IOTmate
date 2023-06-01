from flask import Flask, render_template, request, jsonify, url_for,redirect, send_file
from werkzeug.utils import secure_filename
from lib.file_manager import *

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

    print(files)

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

@app.route('/dradis/projects', methods=['GET', 'POST'])
def dradis_jobs():
    from lib.dradis_project_data import get_all_project_data

    api_token = 'gszaZ8EiynJB6ipzPqzA'

    if request.method == 'GET':
        all_dradis_jobs = get_all_project_data(api_token=api_token)
        return jsonify(all_dradis_jobs)
    
    elif request.method == 'POST':

        from lib.dradis_API_funcs import add_issue

        dradis_name = request.json.get('dradisName')  # Access the form data
        smo = request.json.get('smo')  # Access the form data
        jobId = request.json.get('jobId')  # Access the form data

        TITLE = 'Network accessible components shall not expose any unnecessary services'
        BASESCORE = "N/A"
        VECTOR = "N/A"
        RATING = "Pass"
        AREA = "Foundation"
        CLAUSES = "IoT Kitemark Clause A1.2\nReference:\n\tBSI"
        NONCONFORMANCE = "(Network accessible components exposes unnecessary services/ports.)"
        CLAUSEREQUIREMENT = "Network accessible components shall not expose any unnecessary services/ports."
        TOOLS = "None"
        CAUSE = "-"
        CORRECTIONCONTAINMENT = "-"
        CORRECTIVEACTION = "-"
        DESCRIPTION = "-"
        SOLUTION = "-"
        REFERENCES = "-"
        ADDONTAGS = "-"

        issue_ID = add_issue(

            api_token=api_token,
            project_number=jobId,

            TITLE=TITLE,
            BASESCORE=BASESCORE,
            VECTOR=VECTOR,
            RATING=RATING,
            AREA=AREA,
            CLAUSES=CLAUSES,
            NONCONFORMANCE=NONCONFORMANCE,
            CLAUSEREQUIREMENT=CLAUSEREQUIREMENT,
            TOOLS=TOOLS,
            CAUSE=CAUSE,
            CORRECTIONCONTAINMENT=CORRECTIONCONTAINMENT,
            CORRECTIVEACTION=CORRECTIVEACTION,
            DESCRIPTION=DESCRIPTION,
            SOLUTION=SOLUTION,
            REFERENCES=REFERENCES,
            ADDONTAGS=ADDONTAGS
        )
        # Perform operations with the form data
        # Example: Save the data to the database or process it in some way
        
        # Return a response to the client
        response = {'success': True, 'message': 'Form data received successfully'}
        return jsonify(response)

# Store the console output in a global variable or a file
console_output = []

@app.route('/get_console_output', methods=['GET'])
def get_console_output():
    # Retrieve the console output
    output = '\n'.join(console_output)
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True , port=5000)