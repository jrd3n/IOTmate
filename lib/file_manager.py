import os
import json
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
