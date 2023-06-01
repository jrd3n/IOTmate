import json
import os
import requests

def Dradis_requirements(Requirement_title, Requirement_text = "-"):

    Working_String = "#[{Requirement_title}]#\n{Requirement_text}\n\n".format(Requirement_title=Requirement_title, Requirement_text=Requirement_text)

    return Working_String

def issue_write(api_token, project_ID, test_row_json):
    # Takes a test row from the test data spread sheet and returns the

    text = Dradis_requirements("Title", test_row_json['Requirement'])
    text += Dradis_requirements("CVSSv3.BaseScore")  #Changed from Capital to the Dradis defined vble (Iker)
    text += Dradis_requirements("CVSSv3.Vector")        #Changed from Capital to the Dradis defined vble (Iker)
    text += Dradis_requirements("Rating", test_row_json['Status'])
    text += Dradis_requirements("Area")
    text += Dradis_requirements("Clauses", test_row_json['References'])
    text += Dradis_requirements("Nonconformance")
    text += Dradis_requirements("ClauseRequirement")
    text += Dradis_requirements("TOOLS")
    text += Dradis_requirements("Cause")
    text += Dradis_requirements("CorrectionContainment") # For some reason this one is not written in the issue
    text += Dradis_requirements("CorrectiveAction")           # For some reason this one is not written in the issue
    text += Dradis_requirements("Description")
    text += Dradis_requirements("Solution")
    text += Dradis_requirements("References")
    text += Dradis_requirements("ADDONTAGS")

    if test_row_json.get('Dradis_issue_ID') is not None and test_row_json.get('Dradis_issue_ID') != "":
        # if we have a issue number
        issue_ID = test_row_json['Dradis_issue_ID']
        issue_ID = issue_update_existing(api_token, project_ID, issue_ID,text)
        return issue_ID
    else:
        issue_ID = issue_add_new(api_token, project_ID, text)
        return issue_ID

def evidence_write(api_token, project_ID, test_row_json, node_ID):
    # Takes a test row from the test data spread sheet and returns the

    text = Dradis_requirements("Objective", test_row_json['Requirement'])
    text += Dradis_requirements("Screenshot")

    if test_row_json.get('Dradis_issue_ID') is not None and test_row_json.get('Dradis_issue_ID') != "":

        issue_ID = test_row_json['Dradis_issue_ID']

        # if we have a issue number
        if test_row_json.get('Dradis_evidence_ID') is not None and test_row_json.get('Dradis_evidence_ID') != "":
            evidence_ID = test_row_json['Dradis_evidence_ID']
            evidence_ID = evidence_update_existing(api_token, project_ID, issue_ID, node_ID, evidence_ID, text)
            return evidence_ID
        else:
            evidence_ID = evidence_add_new(api_token, project_ID, issue_ID, node_ID, text)
            return evidence_ID
    else:
        return False

def response_error_handling(response):

    if response.status_code == 201:
        return True
    if response.status_code == 200:
        return True
    elif response.status_code == 402:
        print("ERROR please check api token")
        return False
    elif response.status_code == 404:
        print("ERROR Project not found")
        return False
    elif response.status_code == 403:
        print("403 forbidden — you don't have permission to access this resource, Check your API Key")
        return False
    elif response.status_code == 415:
        print("A Content-Type header set to 'application/json' must be sent for this request")
        return False
    else:
        print(response.status_code)
        print(response.json())
        return False

def evidence_update_existing(api_token, project_ID, issue_ID, node_ID, evidence_ID, Text):

    server_url = "https://10.81.253.200/pro/api/nodes/{node_ID}/evidence/{evidence_ID}".format(node_ID=node_ID, evidence_ID=evidence_ID)

    print("HERE {}".format(server_url))
    
    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": project_ID,
               "Content-type": "application/json"}

    data = { "evidence": { "content": Text,
            "issue_id": "{issue_ID}".format(issue_ID=issue_ID)
            }
        }
    
    response = requests.put(
        server_url, headers=headers, verify=False, json=data)

    if response_error_handling(response):
        response_json = response.json()
        return response_json['id']
    
def nodes_get_all(api_token,project_ID):

    server_url = "http://dradis-pro.dev/pro/api/nodes"
    
    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": project_ID
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
               "Dradis-Project-Id": project_ID,
               "Content-type": "application/json"}

    data = { "evidence": { "content": Text,
            "issue_id": "{issue_ID}".format(issue_ID=issue_ID)
            }
        }

    response = requests.post(
        server_url, headers=headers, verify=False, json=data)

    if response_error_handling(response):
        response_json = response.json()
        return response_json['id']

def issue_add_new(api_token, project_ID, Text):

    server_url = 'https://10.81.253.200/pro/api/issues'

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": project_ID,
               "Content-type": "application/json"}

    data = {'issue': {'text':    Text } }

    response = requests.post(
        server_url, headers=headers, verify=False, json=data)

    if response_error_handling(response):
        response_json = response.json()
        return response_json['id']

def issue_update_existing(api_token, project_ID, issue_ID, Text):

    server_url = 'https://10.81.253.200/pro/api/issues/{issue_ID}'.format(issue_ID=issue_ID)

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token),
               "Dradis-Project-Id": project_ID,
               "Content-type": "application/json"}

    data = {'issue': {'text': Text }}

    response = requests.put(
        server_url, headers=headers, verify=False, json=data)
    
    if response_error_handling(response):
        response_json = response.json()
        return response_json['id']
    else:
        print("Resetting issue_ID assosiated with this test.")
        return ""

if __name__ == "__main__":

    api_token = 'gszaZ8EiynJB6ipzPqzA'
    project_ID = '87'
    node_ID = '968'

    from file_manager import *
   
    folder_path = 'data/456/'
    file_name = 'test_data.xlsx'

    all_tests_json = read_json_from_excel(folder_path,file_name)

    Console = ""

    for test_row_json in all_tests_json:
        print("Writing {}...".format(test_row_json['Number']))
        Dradis_issue_ID = issue_write(api_token,project_ID,test_row_json)
        if Dradis_issue_ID != "" or Dradis_issue_ID != None:
            print("issue ID {}".format(Dradis_issue_ID))
            test_number = test_row_json['Number']
            new_data = {'Dradis_issue_ID': Dradis_issue_ID}
            write_json_to_excel(folder_path,file_name,new_data,test_number)
            Dradis_evidence_ID = evidence_write(api_token, project_ID, test_row_json, node_ID)
            if Dradis_evidence_ID != "" or Dradis_evidence_ID != None:
                print("evidence ID {}".format(Dradis_evidence_ID))
                new_data = {'Dradis_evidence_ID': Dradis_evidence_ID}
                write_json_to_excel(folder_path,file_name,new_data,test_number)