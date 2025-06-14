from leave_app.models import LeaveRequest, LeaveStatus

# Έλεγχος για την αίτηση 10
request_10 = LeaveRequest.objects.get(pk=10)
print(f'Αίτηση ID: {request_10.id}')
print(f'Status: "{request_10.status}"')
print(f'Status type: {type(request_10.status)}')
print(f'Status repr: {repr(request_10.status)}')
print(f'Σύγκριση με ΚΑΤΑΧΩΡΗΘΗΚΕ: {request_10.status == "ΚΑΤΑΧΩΡΗΘΗΚΕ"}')
print(f'Όλες οι διαθέσιμες τιμές:')

statuses = LeaveStatus.objects.all()
for status in statuses:
    print(f'  - "{status.name}" (id={status.id})')