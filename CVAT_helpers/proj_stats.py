from cvat_sdk import Client
from prettytable import PrettyTable
from collections import defaultdict
import requests
import logging

project_id = 123456   # Update with your project ID

# Set up logging to a file
#logging.basicConfig(filename='cvat_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

# CVAT SDK connection (update these variables accordingly)
cvat_host = 'https://app.cvat.ai'
# CVAT credentials (replace with your username and password)
username = 'USERNAME'
password = getpass.getpass(prompt='Enter your CVAT password: ')
#password = r'PASSWORD'

# Manually login using requests to get the token
session = requests.Session()
login_url = f'{cvat_host}/api/auth/login'
login_data = {'username': username, 'password': password}
login_response = session.post(login_url, json=login_data)

if login_response.status_code == 200:
    token = login_response.json().get('key')
    logging.debug(f"Successfully logged in, received token: {token}")
else:
    logging.error(f"Failed to log in. Status code: {login_response.status_code}")
    raise Exception("Login failed. Please check your credentials.")

# Function to fetch project-level labels with pagination
def fetch_project_labels(project_id):
    client = Client(cvat_host)
    client.login((username, password))
    
    # Fetch all pages of project labels
    project_labels = {}
    page = 1

    while True:
        # Make request to labels API for each page
        label_url = f"https://app.cvat.ai/api/labels?project_id={project_id}&page={page}"
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(label_url, headers=headers)

        if response.status_code == 200:
            label_data = response.json()
            if 'results' in label_data:
                # Add labels from this page to project_labels
                for label in label_data['results']:
                    project_labels[label['id']] = label['name']

                # If there is a next page, continue; otherwise, break
                if label_data.get('next'):
                    page += 1
                else:
                    break
            else:
                logging.error(f"No labels found in the response from {label_url}")
                break
        else:
            logging.error(f"Failed to fetch labels from {label_url}, Status Code: {response.status_code}")
            break
    
    logging.debug(f"Fetched project-level labels: {project_labels}")
    return project_labels

# Fetching labels by subset for a project
def fetch_labels_by_subset(project_id):
    subset_labels = defaultdict(lambda: defaultdict(int))  # {subset: {label: count}}
    total_labels = defaultdict(int)  # {label: total_count}

    # Fetch project-level labels once
    label_map = fetch_project_labels(project_id)

    # Initialize CVAT client for other operations
    client = Client(cvat_host)
    client.login((username, password))

    # Fetch and filter tasks by project_id
    logging.debug(f"Fetching tasks for project {project_id}...")
    tasks = client.tasks.list()
    filtered_tasks = [task for task in tasks if task.project_id == project_id]
    logging.debug(f"Found {len(filtered_tasks)} tasks for project {project_id}.")

    for task in filtered_tasks:
        logging.debug(f"Processing task {task.id}...")

        # Access task's subset and jobs
        subset = task.subset or 'undefined'
        logging.debug(f"Task {task.id} is in subset: {subset}")

        # Fetch jobs and filter by task ID
        task_jobs = client.jobs.list()
        task_jobs_filtered = [job for job in task_jobs if job.task_id == task.id]
        logging.debug(f"Found {len(task_jobs_filtered)} jobs in task {task.id}.")

        # Process jobs and their annotations
        for job in task_jobs_filtered:
            logging.debug(f"Processing job {job.id}...")

            # Retrieve job annotations
            job_data = client.jobs.retrieve(job.id)
            annotations = job_data.get_annotations()

            for shape in annotations['shapes']:
                label_id = shape['label_id']
                label_name = label_map.get(label_id, 'Unknown')
                if label_name == 'Unknown':
                    logging.error(f"Unknown label ID {label_id} found in task {task.id}, job {job.id}. Full shape data: {shape}")
                logging.debug(f"Label name for ID {label_id}: {label_name}")
                subset_labels[subset][label_name] += 1
                total_labels[label_name] += 1

    return subset_labels, total_labels, label_map

# Generate PrettyTable output
def generate_label_table(subset_labels, total_labels, label_map):
    subsets = sorted(list(subset_labels.keys()))  # Get subsets dynamically
    columns = ['Label'] + subsets + ['Total', 'val%']
    table = PrettyTable(columns)

    total_per_subset = defaultdict(int)

    # Ensure all labels (including those with 0 counts) are displayed
    for label_id, label_name in label_map.items():
        row = [label_name]
        label_total = 0
        val_count = subset_labels.get('val', {}).get(label_name, 0)

        for subset in subsets:
            count = subset_labels[subset].get(label_name, 0)
            row.append(count)
            total_per_subset[subset] += count
            label_total += count

        row.append(label_total)
        val_percent = (val_count / label_total * 100) if label_total > 0 else 0
        row.append(f"{val_percent:.1f}%")
        table.add_row(row)

    # Add total row
    total_row = ['Total']
    overall_total = 0
    for subset in subsets:
        subset_total = total_per_subset[subset]
        total_row.append(subset_total)
        overall_total += subset_total

    val_total = total_per_subset.get('val', 0)
    val_percent_total = (val_total / overall_total * 100) if overall_total > 0 else 0
    total_row.append(overall_total)
    total_row.append(f"{val_percent_total:.1f}%")

    table.add_row(total_row)
    return table

# Main function to fetch and generate the table
def main(project_id):
    subset_labels, total_labels, label_map = fetch_labels_by_subset(project_id)
    table = generate_label_table(subset_labels, total_labels, label_map)
    print(table)

main(project_id)
