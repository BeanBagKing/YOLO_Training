from cvat_sdk import make_client
from collections import Counter
import getpass
import requests

# Replace with your CVAT host (since you're using CVAT AI hosted)
cvat_host = 'https://app.cvat.ai'

# CVAT credentials (replace with your username and password)
username = 'USERNAME'
password = getpass.getpass(prompt='Enter your CVAT password: ')
#password = r'PASSWORD'

# Project ID
project_id = 123456

# Function to fetch task metadata and filter by subset (e.g., 'train' or 'val')
def fetch_task_images_by_subset(tasks, subset):
    total_images = 0
    for task in tasks:
        if task.project_id == project_id and task.subset == subset:
            task_info = client.tasks.retrieve(task.id)
            total_images += task_info.size  # Assuming 'size' represents number of images
    return total_images

# Initialize CVAT client
with make_client(cvat_host) as client:
    client.login((username, password))

    # Fetch all tasks
    tasks = client.tasks.list()

    # Count images in each subset
    subsets = Counter()
    total_images = 0

    # Iterate over tasks and filter by project_id
    for task in tasks:
        if task.project_id == project_id:
            subset = task.subset
            task_info = client.tasks.retrieve(task.id)
            subsets[subset] += task_info.size
            total_images += task_info.size

    # Output the result
    for subset, count in subsets.items():
        print(f"{subset}: {count}")

    # Print the total count of images
    print(f"\nTotal Images: {total_images}")
