from cvat_sdk import make_client
from collections import Counter
import getpass
import requests

# Replace with your CVAT host (since you're using CVAT AI hosted)
cvat_host = 'https://app.cvat.ai'

# CVAT credentials (replace with your username and password)
username = 'USERNAME'
password = getpass.getpass(prompt='Enter your CVAT password: ')
#password = r'PASSWORD' # If you like to be lazy and live dangerously

# Project ID
project_id = 123456

# Function to fetch all labels, handling pagination
def fetch_all_labels(labels_url, auth):
    all_labels = []
    while labels_url:
        response = requests.get(labels_url, auth=auth)
        data = response.json()
        all_labels.extend(data['results'])  # Add the labels from the current page
        labels_url = data.get('next')  # Get the URL for the next page, if any
    return all_labels

# Initialize CVAT client
with make_client(cvat_host) as client:
    client.login((username, password))


    # Fetch all tasks
    tasks = client.tasks.list()

    label_counter = Counter()

    # Iterate over tasks and filter them by project_id
    for task in tasks:
        if task.project_id == project_id:
            # Retrieve task annotations
            annotations = client.tasks.retrieve(task.id).get_annotations()

            # Retrieve task metadata (including label info)
            task_info = client.tasks.retrieve(task.id)

            # Fetch all labels using pagination
            labels_url = task_info.labels['url']
            labels_data = fetch_all_labels(labels_url, auth=(username, password))

            # Create a label map from label id to label name using 'results' key
            label_map = {label['id']: label['name'] for label in labels_data}

            # Count the instances for each label using label_id
            for shape in annotations.shapes:
                label_name = label_map.get(shape.label_id, "Unknown Label")  # Handle unknown labels
                label_counter[label_name] += 1

    # Output the result
    total_count = 0
    for label, count in label_counter.items():
        print(f"{label}, {count}")
        total_count += count

    # Print the total count of all tags
    print(f"\nTotal labeled instances: {total_count}")
