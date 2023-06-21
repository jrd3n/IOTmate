import json
import os
import requests
import urllib3
import warnings

# Filter out the InsecureRequestWarning
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

def Dradis_requirements(Requirement_title, Requirement_text = "-"):

    Working_String = "#[{Requirement_title}]#\n{Requirement_text}\n\n".format(Requirement_title=Requirement_title, Requirement_text=Requirement_text)

    return Working_String

def score_from_Rating(Rating):

    if Rating.lower() == "failed" or Rating.lower() == "fail" :
        return "7.0"
    elif Rating.lower() == "passed":
        return "0.0"
    elif Rating.lower() == "medium":
        return "3.0"
    else:
        return "kljfdklsajfkil"

def clauses_field(Test_number,References ):

    working_string = "* IoT Kitemark clause {Test_number}\n\t\nReferences\n\n* {References}\n".format(Test_number=Test_number, References=References)

    return working_string

def Area_field(Test_number):

    first_char = Test_number[0].upper()

    #         Case "A"
    #                 Area = "Foundation"
    #         Case "B"
    #                 Area = "Documentation&Policy"
    #         Case "C"
    #                 Area = "Hardware"
    #         Case "D"
    #                 Area = "UserInterface"
    #         Case "E"
    #                 Area = "WirelessCommunication"
    #         Case "F"
    #                 Area = "WiredCommunication"
    #         Case "G"
    #                 Area = "SupportingInfrastructure"
    #         Case "H"
    #                 Area = "Cryptography"

    if first_char == 'A':
         Area = "Foundation"
    elif first_char == 'B':
        Area = "Documentation&Policy"
    elif first_char == 'C':
        Area = "Hardware"
    elif first_char == 'D':
        Area = "UserInterface"
    elif first_char == 'E':
        Area = "WirelessCommunication"
    elif first_char == 'F':
        Area = "WiredCommunication"
    elif first_char == 'G':
        Area = "SupportingInfrastructure"
    elif first_char == 'H':
        Area = "Cryptography"
    else:
        Area=  "A,B,C,D,E,F,G,H, not found in string {Test_number}".format(Test_number)

    return Area

def issue_write(api_token, project_ID, test_row_json, Dradis_issue_ID):
    # Takes a test row from the test data spreadsheet and returns the

    text = Dradis_requirements("Title", test_row_json.get('Requirement'))
    text += Dradis_requirements("CVSSv3.BaseScore", score_from_Rating(test_row_json.get('Status')))
    text += Dradis_requirements("CVSSv3.Vector")
    text += Dradis_requirements("Rating", test_row_json.get('Status'))
    text += Dradis_requirements("Area", Area_field(test_row_json.get('Number')))
    text += Dradis_requirements("Clauses", clauses_field(test_row_json.get('Number'), test_row_json.get('References')))
    text += Dradis_requirements("Nonconformance", test_row_json.get('criteria-comment'))
    text += Dradis_requirements("ClauseRequirement", test_row_json.get('Requirement'))
    text += Dradis_requirements("Tools")
    text += Dradis_requirements("Cause")
    text += Dradis_requirements("CorrectionContainment")
    text += Dradis_requirements("CorrectiveAction")
    text += Dradis_requirements("Description")
    text += Dradis_requirements("Solution")
    text += Dradis_requirements("References")
    text += Dradis_requirements("AddonTags")
    text += Dradis_requirements("Tags", test_row_json.get('Status'))

    

    if Dradis_issue_ID and str(Dradis_issue_ID).strip() != "":
        print("\tissue_ID {}".format(Dradis_issue_ID), end="\t")
        try:
            Dradis_issue_ID = issue_update_existing(api_token, project_ID, Dradis_issue_ID, text)
        except Exception as e:
        # This block will be executed if any other exception occurs
            print("An error occurred:", str(e),end="\t")
            # print("ERROR{}ERROR".format(e))
            if str(e) == "ERROR: Project not found.":
                print("Adding issue regardless",end="\t")
                Dradis_issue_ID = issue_add_new(api_token, project_ID, text)
                print("issue_ID {}".format(Dradis_issue_ID), end="\t")
            else:
                raise
    else:
        print("\tNo Issue_ID", end="\t")
        Dradis_issue_ID = issue_add_new(api_token, project_ID, text)
        print("issue_ID {}".format(Dradis_issue_ID), end="\t")

    print("COMPLETE")
    return Dradis_issue_ID

def evidence_write(api_token, project_ID, test_row_json, node_ID, Dradis_evidence_ID, Dradis_issue_ID):
    # Takes a test row from the test data spreadsheet and returns the

    text = Dradis_requirements("Objective", test_row_json.get('method-comment'))
    text += Dradis_requirements("Screenshot")

    if Dradis_issue_ID and str(Dradis_issue_ID).strip() != "":
        # If we have a valid issue number

        print("\tevidence_ID {}".format(Dradis_evidence_ID), end="\t")

        if Dradis_evidence_ID and str(Dradis_evidence_ID).strip() != "":
            try:
                Dradis_evidence_ID = evidence_update_existing(api_token, project_ID, Dradis_issue_ID, node_ID, Dradis_evidence_ID, text)
            except Exception as e:
            # This block will be executed if any other exception occurs
                print("An error occurred:", str(e),end="\t")
                if str(e) == "ERROR: Project not found.":
                    print("Adding evidence regardless",end="\t")
                    Dradis_evidence_ID = evidence_add_new(api_token, project_ID, Dradis_issue_ID, node_ID, text)
                else:
                    raise
        else:
            print("No evidence_ID", end="\t")

            Dradis_evidence_ID = evidence_add_new(api_token, project_ID, Dradis_issue_ID, node_ID, text)
            
            print("evidence_ID {}".format(Dradis_evidence_ID), end="\t")
    else:
        return False

    print("COMPLETE")
    return Dradis_evidence_ID

def response_error_handling(response):
    if response.status_code == 201:
        return True
    elif response.status_code == 200:
        return True
    elif response.status_code == 402:
        raise Exception("ERROR: Please check API token.")
    elif response.status_code == 404:
        raise Exception("ERROR: Project not found.")
    elif response.status_code == 403:
        raise Exception("ERROR: 403 forbidden — You don't have permission to access this resource. Check your API Key.")
    elif response.status_code == 415:
        raise Exception("ERROR: A 'Content-Type' header set to 'application/json' must be sent for this request.")
    else:
        raise Exception("Unknown error occurred with status code {}: {}".format(response.status_code, response.json()))

def evidence_update_existing(api_token, project_ID, issue_ID, node_ID, evidence_ID, Text):

    server_url = "https://10.81.253.200/pro/api/nodes/{node_ID}/evidence/{evidence_ID}".format(node_ID=node_ID, evidence_ID=evidence_ID)
    
    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": "{}".format(project_ID),
               "Content-type": "application/json"}

    data = { "evidence": { "content": Text,
            "issue_id": "{issue_ID}".format(issue_ID=issue_ID)
            }
        }
    
    response = requests.put(
        server_url, headers=headers, verify=False, json=data)

    if response_error_handling(response):
        response_json = response.json()
        return response_json.get('id')
    
def nodes_get_all(api_token,project_ID):

    server_url = "http://10.81.253.200/pro/api/nodes"
    
    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": "{}".format(project_ID),
               }

    response = requests.post(
        server_url, headers=headers, verify=False)

    if response_error_handling(response):
        response_json = response.json()
        return response_json

def projects_get_all(api_token):
    server_url = 'https://10.81.253.200/pro/api/projects/'

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token)}

    response = requests.get(server_url, headers=headers, verify=False)

    if response_error_handling(response):
        response_json = response.json()
        return response_json

def evidence_add_new(api_token, project_ID, issue_ID, node_ID, Text):

    server_url = 'https://10.81.253.200/pro/api/nodes/{node_ID}/evidence'.format(node_ID=node_ID)

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": "{}".format(project_ID),
               "Content-type": "application/json"}

    data = { "evidence": { "content": Text,
            "issue_id": "{issue_ID}".format(issue_ID=issue_ID)
            }
        }

    response = requests.post(
        server_url, headers=headers, verify=False, json=data)

    if response_error_handling(response):
        response_json = response.json()
        return response_json.get('id')

def issue_add_new(api_token, project_ID, Text):

    server_url = 'https://10.81.253.200/pro/api/issues'

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": "{}".format(project_ID),
               "Content-type": "application/json"}

    data = {'issue': {'text':    Text } }

    response = requests.post(
        server_url, headers=headers, verify=False, json=data)

    if response_error_handling(response):
        response_json = response.json()
        return response_json.get('id')

def issue_update_existing(api_token, project_ID, issue_ID, Text):

    server_url = 'https://10.81.253.200/pro/api/issues/{issue_ID}'.format(issue_ID=issue_ID)

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": "{}".format(project_ID),
               "Content-type": "application/json"}

    data = {'issue': {'text': Text }}

    response = requests.put(
        server_url, headers=headers, verify=False, json=data)
    
    if response_error_handling(response):
        response_json = response.json()
        return response_json.get('id')
    else:
        print("Resetting issue_ID assosiated with this test.")
        return ""

if __name__ == "__main__":

    api_token = 'gszaZ8EiynJB6ipzPqzA'
    project_ID = '86'
    node_ID = '948'

    from file_manager import *
   
    folder_path = 'data/3625585/'
    file_name = 'test_data.xlsx'

    all_tests_json = read_json_from_excel(folder_path,file_name)

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