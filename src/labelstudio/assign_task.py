# from label_studio_sdk import LabelStudio
# client = LabelStudio(base_url="http://localhost:8080", api_key="yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA3MTUyNDg2MywiaWF0IjoxNzY0MzI0ODYzLCJqdGkiOiI4MTFhMDUwMTc1OTI0MWY0OGFmNDIzOTAzMDk4NmEzMCIsInVzZXJfaWQiOiIxIn0.1DvhFU98gkuZdQ-OJ-09AqBDCb4yarruBD9QvPlE-xQ")
# # Get user IDs
# users = client.users.list()
# for u in users:
# print(u.id, u.email or u.username)
# assign_tasks_to_annotators.py
# Run this anytime to split tasks between your 2 annotators
from label_studio_sdk import LabelStudio 
LS_URL = "http://localhost:8080" 
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA3MTkzOTkyNSwiaWF0IjoxNzY0NzM5OTI1LCJqdGkiOiJmZjljZTNmYzU0ODA0MzI5YTlkM2RiY2Q2YTMwOTcxZCIsInVzZXJfaWQiOiIyIn0.rLlywwxrA-2leLhEogT7vqwBUjoD9YzCJAYZ_B4DHeQ"
PROJECT_ID = 7
client = LabelStudio(base_url=LS_URL, api_key=API_KEY)
# Usernames OR numeric IDs accepted
ANNOTATORS = ["1", "2"] # must match LS usernames OR user IDs as string
# --------------------------------------------------
# FETCH TASKS
# --------------------------------------------------
tasks = list(client.tasks.list(project=PROJECT_ID)) 
print(f"Total tasks: {len(tasks)}\n") 
if not tasks: 
    print("No tasks found!") 
    exit()
# --------------------------------------------------
# ROUND-ROBIN ASSIGNMENT (meta + data)
# --------------------------------------------------
print("Assigning tasks...\n") 
for idx, task in enumerate(tasks):     
    assigned_user = ANNOTATORS[idx % len(ANNOTATORS)]
# --- Update META (for backend / logging) ---
    new_meta = task.meta or {}     
    new_meta["assigned_to"] = assigned_user
# --- Update DATA (for UI column under data.*) ---
    new_data = task.data or {}     
    new_data["assigned_to"] = assigned_user
# --- Update Task ---
    client.tasks.update( id=task.id, meta=new_meta, data=new_data) 
    print(f"Assigned Task {task.id:<5} → {assigned_user}") 
    print("\n✓ Finished assigning tasks\n")
# --------------------------------------------------
# VERIFY ASSIGNMENTS
# --------------------------------------------------
print("Verifying assignments...\n") 
tasks = list(client.tasks.list(project=PROJECT_ID)) 
for task in tasks:     
    meta_user = task.meta.get("assigned_to") if task.meta else None     
    data_user = task.data.get("assigned_to") if task.data else None 
    print(f"Task {task.id:<5} → meta: {meta_user}, data: {data_user}") 
    print("\n✓ Verification complete")


