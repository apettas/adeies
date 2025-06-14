import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adeies.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from leave_app.models import LeaveType

print("=== ΔΟΚΙΜΗ FILE UPLOAD ===")

# Δημιουργία test αρχείου
test_content = b'Test file content for debugging'
test_file = SimpleUploadedFile('simple_test.txt', test_content, content_type='text/plain')
print(f"1. Δημιουργήθηκε test file: {test_file.name} ({test_file.size} bytes)")

# Login
client = Client()
User = get_user_model()
user = User.objects.get(email='papanikolaou@sch.gr')
client.force_login(user)
print(f"2. Logged in as: {user.get_full_name()}")

# Εύρεση leave type
leave_type = LeaveType.objects.first()
print(f"3. Leave type: {leave_type.eidos_adeias} (ID: {leave_type.id})")

# Δημιουργία data με σωστή μορφή για multipart/form-data
data = {
    'leave_type': str(leave_type.id),
    'start_dates[]': ['17/06/2024'],
    'end_dates[]': ['18/06/2024'],
    'reason': 'Simple debug test',
}

files = {
    'attachments': test_file
}

print(f"4. POST data: {data}")
print(f"5. FILES data: {list(files.keys())}")

print("\n6. Αποστολή αίτησης...")
response = client.post('/leaves/create/', data=data, files=files, follow=True)

print(f"7. Response status: {response.status_code}")
print(f"8. Final URL: {response.wsgi_request.path if hasattr(response, 'wsgi_request') else 'N/A'}")

# Έλεγχος αποτελέσματος
from leave_app.models import LeaveRequest
latest_request = LeaveRequest.objects.order_by('-id').first()
print(f"9. Τελευταία αίτηση ID: {latest_request.id if latest_request else 'Καμία'}")

if latest_request:
    attachment_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(latest_request.id))
    print(f"10. Φάκελος αναμένεται: {attachment_dir}")
    print(f"11. Φάκελος υπάρχει: {os.path.exists(attachment_dir)}")
    
    if os.path.exists(attachment_dir):
        files_found = os.listdir(attachment_dir)
        print(f"12. Αρχεία βρέθηκαν: {files_found}")
    else:
        print("12. ✗ Κανένα αρχείο δεν βρέθηκε")

print("\n=== ΤΕΛΟΣ ΔΟΚΙΜΗΣ ===")