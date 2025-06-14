import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adeies.settings')
django.setup()

from django.contrib.auth import get_user_model
from leave_app.models import LeaveRequest, LeaveType, LeaveStatus
from users.models import Employee
import shutil

print("=== ΆΜΕΣΗ ΔΟΚΙΜΗ FILE UPLOAD ===")

# Εύρεση χρήστη και δεδομένων
User = get_user_model()
user = User.objects.get(email='papanikolaou@sch.gr')
employee = user.employee
leave_type = LeaveType.objects.first()
status = LeaveStatus.objects.get(name='ΚΑΤΑΧΩΡΗΘΗΚΕ')

print(f"1. Χρήστης: {user.get_full_name()}")
print(f"2. Leave type: {leave_type.eidos_adeias}")

# Δημιουργία αίτησης απευθείας στη βάση
from datetime import date
leave_request = LeaveRequest.objects.create(
    employee=employee,
    leave_type=leave_type,
    description="Direct test για file upload",
    created_by=employee,
    status=status,
    total_days=2,
    working_days=2
)

print(f"3. Δημιουργήθηκε αίτηση ID: {leave_request.id}")

# Δημιουργία περιόδου
from leave_app.models import LeaveRequestPeriod
period = LeaveRequestPeriod.objects.create(
    leave_request=leave_request,
    start_date=date(2024, 6, 19),
    end_date=date(2024, 6, 20),
    working_days=2,
    total_days=2
)

print(f"4. Δημιουργήθηκε περίοδος από {period.start_date} έως {period.end_date}")

# Τώρα δοκιμάζω να δημιουργήσω φάκελο και αρχείο χειροκίνητα
attachment_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(leave_request.id))
print(f"5. Δημιουργία φακέλου: {attachment_dir}")

try:
    os.makedirs(attachment_dir, exist_ok=True)
    print(f"6. Φάκελος δημιουργήθηκε: {os.path.exists(attachment_dir)}")
    
    # Δημιουργία test αρχείου
    test_file_path = os.path.join(attachment_dir, 'direct_test.txt')
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write('Αυτό είναι ένα test αρχείο για το file upload debugging')
    
    print(f"7. Αρχείο δημιουργήθηκε: {os.path.exists(test_file_path)}")
    print(f"8. Μέγεθος αρχείου: {os.path.getsize(test_file_path)} bytes")
    
    # Έλεγχος αν εμφανίζεται στο leave_detail view
    from users.views import leave_detail
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get(f'/leaves/{leave_request.id}/')
    request.user = user
    
    # Προσομοίωση του view logic για attachments
    import os
    from django.conf import settings
    
    attachment_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(leave_request.id))
    attachments = []
    
    if os.path.exists(attachment_dir):
        for filename in os.listdir(attachment_dir):
            file_path = os.path.join(attachment_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_url = f"{settings.MEDIA_URL}leave_attachments/{leave_request.id}/{filename}"
                attachments.append({
                    'name': filename,
                    'size': file_size,
                    'url': file_url
                })
    
    print(f"9. Attachments βρέθηκαν: {len(attachments)}")
    for att in attachments:
        print(f"   - {att['name']}: {att['size']} bytes, URL: {att['url']}")
    
except Exception as e:
    print(f"ΣΦΑΛΜΑ: {e}")
    import traceback
    traceback.print_exc()

print("\n=== ΤΕΛΟΣ ΆΜΕΣΗΣ ΔΟΚΙΜΗΣ ===")