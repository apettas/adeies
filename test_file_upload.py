import os
import django
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adeies.settings')
django.setup()

from leave_app.models import LeaveType, LeaveRequest

# Δημιουργία test αρχείου
test_content = b'Test file content for debugging file upload'
test_file = SimpleUploadedFile('test_upload.txt', test_content, content_type='text/plain')

# Login με τον χρήστη papanikolaou
client = Client()
User = get_user_model()
user = User.objects.get(email='papanikolaou@sch.gr')
client.force_login(user)

# Εύρεση leave type
leave_type = LeaveType.objects.first()

# POST data για νέα αίτηση με αρχείο
data = {
    'leave_type': leave_type.id,
    'start_dates[]': ['15/06/2024'],
    'end_dates[]': ['16/06/2024'],
    'reason': 'Test αίτηση για debug file upload',
    'attachments': test_file
}

print('Στέλνω αίτηση με αρχείο...')
response = client.post('/leaves/create/', data, follow=True)

print(f'Response status: {response.status_code}')
print(f'Final URL: {response.wsgi_request.path if hasattr(response, "wsgi_request") else "N/A"}')

# Έλεγχος για νέα αίτηση
newest_request = LeaveRequest.objects.order_by('-id').first()
if newest_request:
    print(f'Τελευταία αίτηση ID: {newest_request.id}')
    
    # Έλεγχος φακέλου συνημμένων
    attachment_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(newest_request.id))
    print(f'Φάκελος συνημμένων: {attachment_dir}')
    print(f'Υπάρχει φάκελος: {os.path.exists(attachment_dir)}')
    
    if os.path.exists(attachment_dir):
        files = os.listdir(attachment_dir)
        print(f'Αρχεία στον φάκελο: {files}')
        print(f'Συνολικά αρχεία: {len(files)}')
        
        for filename in files:
            file_path = os.path.join(attachment_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                print(f'  - {filename}: {file_size} bytes')
    else:
        print('✗ Δεν υπάρχει φάκελος συνημμένων!')
else:
    print('Καμία αίτηση')

print('Test ολοκληρώθηκε!')