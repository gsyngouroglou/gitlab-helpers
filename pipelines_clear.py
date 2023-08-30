import sys
import requests

# Fill these two variables with your data
base_url = "https://git.internal.softaware.gr"
projects = {
    "name_of_your_repo": {"id": 0, "token": "XXXXXXX"},
}


def pipeline_delete(pipeline, projectId, token):
    # Call the delete API
    pipeline_id = pipeline.get("id")
    url = f"{base_url}/api/v4/projects/{projectId}/pipelines/{pipeline_id}"
    response = requests.delete(url, headers={"PRIVATE-TOKEN": token})

    if response.ok:
        # Successful deletion
        print(f"Pipeline {pipeline_id} successfully deleted")
    else:
        # Error on deletion
        print(f"Deleting pipeline {pipeline_id} on path failed: {response.url}: "
              f"({response.status_code}) {response.reason}")

        # Case when rate limits have been reached
        if response.status_code == 429:
            # Watch out for rate specific limits https://docs.gitlab.com/ee/user/gitlab_com/index.html#gitlabcom-specific-rate-limits
            print("Rate Limits have been reached, wait and try again later")
            exit(20)


def delete_all(project_name):
    # Get the project id and token
    project_id = projects[project_name]["id"]
    token = projects[project_name]["token"]
    pipelines_query_url = f"{base_url}/api/v4/projects/{project_id}/pipelines"

    # Delete all pipelines
    print("Deleting pipelines")
    while True:
        response = requests.get(pipelines_query_url, headers={"PRIVATE-TOKEN": token})
        if response.ok:
            pipelines = response.json()
            if len(pipelines) == 0:
                print("No more pipelines found, exiting")
                exit(0)
            else:
                for pipeline in pipelines:
                    pipeline_delete(pipeline, project_id, token)
        else:
            print(f"Querying for pipelines failed: {response.url}: ({response.status_code}) {response.reason}")
            if response.status_code == 429:
                # Watch out for rate specific limits https://docs.gitlab.com/ee/user/gitlab_com/index.html#gitlabcom-specific-rate-limits
                print("Rate Limits have been reached, wait and try again later")
            exit(10)

print(sys.argv)
if len(sys.argv) != 2:
    print(f"You should provide the project name you wish to clear the pipelines from.\nAvailable options: {', '.join(projects.keys())}")
else:
    project_name = sys.argv[1]
    if project_name not in projects:
        print(f"Project {project_name} not found.\nAvailable options: {', '.join(projects.keys())}")
        exit(1)
    delete_all(sys.argv[1])
