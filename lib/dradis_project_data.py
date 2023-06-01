import requests
import json

def get_all_project_data(api_token):

    server_url = 'https://10.81.253.200/pro/api/projects/'

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token)}

    response = requests.get(server_url, headers=headers, verify=False)

    if response.status_code == 200:
        # Good reponse
        response_json = response.json()
        return response_json
    elif response.status_code == 402:
        print("ERROR please check api token")
        input("")
        exit()
    elif response.status_code == 403:
        print("403 forbidden — you don't have permission to access this resource, Check your API Key")
        return False
    else:
        # print(response.status_code)
        # print(response.json)
        return False
    
def upload_issue(api_token, issue, project_id):

    server_url = 'https://10.81.253.200/pro/api/projects/'

    headers = {"Authorization": 'Token token="{token}"'.format(token=api_token)}

    response = requests.get(server_url, headers=headers, verify=False)

    if response.status_code == 200:
        # Good reponse
        response_json = response.json()
        return response_json
    elif response.status_code == 402:
        print("ERROR please check api token")
        input("")
        exit()
    elif response.status_code == 403:
        print("403 forbidden — you don't have permission to access this resource, Check your API Key")
        return False
    else:
        # print(response.status_code)
        # print(response.json)
        return False

if __name__ == "__main__":

    api_token = 'gszaZ8EiynJB6ipzPqzA'

    print(get_all_project_data(api_token=api_token))

    input("")