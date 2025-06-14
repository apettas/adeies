"""
Views για το frontend interface των χρηστών
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import timezone
from .models import CustomUser, Employee
from leave_app.models import LeaveRequest, LeaveStatus, LeaveType
from django.db.models import Q


def home(request):
    """Αρχική σελίδα - redirect ανάλογα με το αν είναι logged in"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'users/home.html')


@login_required
def dashboard(request):
    """Dashboard για τον χρήστη"""
    context = {
        'user': request.user,
    }
    
    # Αν ο χρήστης έχει Employee profile
    try:
        employee = request.user.employee
        context['employee'] = employee
        
        # Στατιστικά αδειών
        current_year = timezone.now().year
        context['leave_balance'] = employee.get_leave_balance(current_year)
        context['sick_leave_balance'] = employee.self_declaration_sick_days_remaining
        
        # Πρόσφατες αιτήσεις
        recent_requests = LeaveRequest.objects.filter(
            employee=employee
        ).order_by('-created_at')[:5]
        context['recent_requests'] = recent_requests
        
        # Εκκρεμείς αιτήσεις
        pending_requests = LeaveRequest.objects.filter(
            employee=employee,
            status__is_final_status=False
        )
        context['pending_requests'] = pending_requests
        
    except Employee.DoesNotExist:
        context['employee'] = None
        messages.warning(request, 'Δεν έχετε ολοκληρώσει το προφίλ υπαλλήλου σας. Επικοινωνήστε με τη διοίκηση.')
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """Προφίλ χρήστη"""
    context = {
        'user': request.user,
    }
    
    try:
        employee = request.user.employee
        context['employee'] = employee
    except Employee.DoesNotExist:
        context['employee'] = None
    
    return render(request, 'users/profile.html', context)


@login_required
def leave_list(request):
    """Λίστα αιτήσεων άδειας του χρήστη"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Δεν έχετε δικαιώματα πρόσβασης σε αιτήσεις αδειών.')
        return redirect('users:dashboard')
    
    # Φίλτρα
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', timezone.now().year)
    
    # Βασικό queryset
    leaves = LeaveRequest.objects.filter(employee=employee)
    
    # Εφαρμογή φίλτρων
    if status_filter:
        leaves = leaves.filter(status__name=status_filter)
    
    if year_filter:
        leaves = leaves.filter(created_at__year=year_filter)
    
    leaves = leaves.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(leaves, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Υπολογισμός statistics
    all_leaves = LeaveRequest.objects.filter(employee=employee)
    total_leaves = all_leaves.count()
    pending_count = all_leaves.filter(status__name='ΚΑΤΑΧΩΡΗΘΗΚΕ').count()
    approved_count = all_leaves.filter(status__name='ΕΓΚΡΙΘΗΚΕ').count()
    rejected_count = all_leaves.filter(status__name='ΑΠΟΡΡΙΦΘΗΚΕ').count()
    
    # Δεδομένα για φίλτρα
    statuses = LeaveStatus.objects.all()
    years = range(2020, timezone.now().year + 2)
    
    context = {
        'leaves': page_obj,  # Για να λειτουργεί το template
        'page_obj': page_obj,
        'statuses': statuses,
        'years': years,
        'current_status': status_filter,
        'current_year': int(year_filter) if year_filter else timezone.now().year,
        'employee': employee,
        'total_leaves': total_leaves,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'users/leave_list.html', context)


@login_required
def leave_create(request):
    """Δημιουργία νέας αίτησης άδειας"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Δεν έχετε δικαιώματα για δημιουργία αιτήσεων αδειών.')
        return redirect('users:dashboard')
    
    if not employee.can_request_leave:
        messages.error(request, 'Δεν έχετε δικαίωμα αίτησης άδειας.')
        return redirect('users:leave_list')
    
    if request.method == 'POST':
        # Επεξεργασία φόρμας με πολλαπλές περιόδους
        leave_type_id = request.POST.get('leave_type')
        start_dates = request.POST.getlist('start_dates[]')
        end_dates = request.POST.getlist('end_dates[]')
        reason = request.POST.get('reason', '')
        include_weekends = request.POST.get('include_weekends') == 'on'
        
        print(f"DEBUG: leave_type_id={leave_type_id}")
        print(f"DEBUG: start_dates={start_dates}")
        print(f"DEBUG: end_dates={end_dates}")
        print(f"DEBUG: reason={reason}")
        print(f"DEBUG: include_weekends={include_weekends}")
        print(f"DEBUG: FILES={list(request.FILES.keys())}")
        print(f"DEBUG: FILES details={[(k, v.name, v.size) for k, v in request.FILES.items()]}")
        
        if leave_type_id and start_dates and end_dates and len(start_dates) == len(end_dates):
            try:
                from datetime import datetime
                from leave_app.models import LeaveRequestPeriod
                
                # Helper function για parsing Greek dates
                def parse_greek_date(date_str):
                    """Parse dd/mm/yyyy format to date object"""
                    try:
                        return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
                    except ValueError:
                        raise ValueError(f"Μη έγκυρη ημερομηνία: {date_str}")
                
                # Validate και parse όλες τις ημερομηνίες
                parsed_periods = []
                total_days = 0
                
                for start_str, end_str in zip(start_dates, end_dates):
                    if not start_str.strip() or not end_str.strip():
                        continue
                        
                    start_date = parse_greek_date(start_str)
                    end_date = parse_greek_date(end_str)
                    
                    if start_date > end_date:
                        raise ValueError("Η ημερομηνία έναρξης δεν μπορεί να είναι μετά την ημερομηνία λήξης")
                    
                    # Υπολογισμός εργάσιμων ημερών
                    days_count = 0
                    current_date = start_date
                    while current_date <= end_date:
                        # Αν συμπεριλαμβάνονται σαββατοκύριακα ή δεν είναι σαββατοκύριακο
                        if include_weekends or current_date.weekday() < 5:  # 0-4 = Monday-Friday
                            days_count += 1
                        current_date += timezone.timedelta(days=1)
                    
                    parsed_periods.append({
                        'start': start_date,
                        'end': end_date,
                        'days': days_count
                    })
                    total_days += days_count
                
                if not parsed_periods:
                    raise ValueError("Δεν βρέθηκαν έγκυρες περίοδοι άδειας")
                
                leave_type = LeaveType.objects.get(pk=leave_type_id)
                
                # Δημιουργία αίτησης
                leave_request = LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    description=reason,
                    created_by=employee,
                    status=LeaveStatus.objects.get(name='ΚΑΤΑΧΩΡΗΘΗΚΕ'),
                    total_days=sum(period['days'] for period in parsed_periods),
                    working_days=sum(period['days'] for period in parsed_periods)
                )
                
                # Δημιουργία περιόδων
                for period in parsed_periods:
                    LeaveRequestPeriod.objects.create(
                        leave_request=leave_request,
                        start_date=period['start'],
                        end_date=period['end'],
                        working_days=period['days'],
                        total_days=period['days']  # Προσθήκη total_days στο period
                    )
                
                # Handle file attachments
                attachments = request.FILES.getlist('attachments')
                print(f"DEBUG: Αρχεία που στάλθηκαν: {len(attachments)} αρχεία")
                for i, att in enumerate(attachments):
                    print(f"DEBUG: Αρχείο {i+1}: {att.name} ({att.size} bytes)")
                
                if attachments:
                    import os
                    from django.conf import settings
                    
                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(leave_request.id))
                    print(f"DEBUG: Δημιουργία φακέλου: {upload_dir}")
                    os.makedirs(upload_dir, exist_ok=True)
                    print(f"DEBUG: Φάκελος δημιουργήθηκε: {os.path.exists(upload_dir)}")
                    
                    for attachment in attachments:
                        # Basic file validation
                        max_size = 10 * 1024 * 1024  # 10MB
                        if attachment.size > max_size:
                            messages.warning(request, f'Το αρχείο "{attachment.name}" είναι πολύ μεγάλο (>10MB) και δεν θα επισυναφθεί.')
                            continue
                            
                        # Save file to upload directory
                        file_path = os.path.join(upload_dir, attachment.name)
                        print(f"DEBUG: Αποθήκευση αρχείου: {file_path}")
                        try:
                            with open(file_path, 'wb+') as destination:
                                for chunk in attachment.chunks():
                                    destination.write(chunk)
                            print(f"DEBUG: Αρχείο αποθηκεύτηκε επιτυχώς: {os.path.exists(file_path)}")
                        except Exception as save_error:
                            print(f"DEBUG: Σφάλμα αποθήκευσης αρχείου: {save_error}")
                            messages.error(request, f'Σφάλμα αποθήκευσης αρχείου {attachment.name}: {save_error}')
                else:
                    print("DEBUG: Δεν στάλθηκαν αρχεία!")
                
                messages.success(request, f'Η αίτηση άδειας δημιουργήθηκε επιτυχώς! Συνολικές ημέρες: {total_days}')
                return redirect('users:leave_detail', pk=leave_request.pk)
                
            except Exception as e:
                print(f"DEBUG: Error = {str(e)}")
                messages.error(request, f'Σφάλμα κατά τη δημιουργία: {str(e)}')
        else:
            missing = []
            if not leave_type_id:
                missing.append("τύπος άδειας")
            if not start_dates:
                missing.append("ημερομηνίες έναρξης")
            if not end_dates:
                missing.append("ημερομηνίες λήξης")
            if start_dates and end_dates and len(start_dates) != len(end_dates):
                missing.append("ίσος αριθμός ημερομηνιών έναρξης και λήξης")
            
            messages.error(request, f'Παρακαλώ συμπληρώστε: {", ".join(missing)}')
    
    # GET request
    leave_types = LeaveType.objects.filter(is_active=True)
    
    context = {
        'employee': employee,
        'leave_types': leave_types,
        'leave_balance': employee.get_leave_balance(),
    }
    
    return render(request, 'users/leave_create.html', context)


@login_required
def leave_detail(request, pk):
    """Λεπτομέρειες αίτησης άδειας"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Δεν έχετε δικαιώματα πρόσβασης.')
        return redirect('users:dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
    
    # Get attachments if they exist
    import os
    from django.conf import settings
    
    attachments = []
    attachment_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(leave_request.id))
    if os.path.exists(attachment_dir):
        for filename in os.listdir(attachment_dir):
            file_path = os.path.join(attachment_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                attachments.append({
                    'name': filename,
                    'size': file_size,
                    'url': f'/media/leave_attachments/{leave_request.id}/{filename}'
                })
    
    context = {
        'leave_request': leave_request,
        'leave': leave_request,  # Για συμβατότητα με το template
        'employee': employee,
        'attachments': attachments,
    }
    
    return render(request, 'users/leave_detail.html', context)


@login_required
def approval_list(request):
    """Λίστα αιτήσεων προς έγκριση (για προϊσταμένους)"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Δεν έχετε δικαιώματα πρόσβασης.')
        return redirect('users:dashboard')
    
    # Έλεγχος αν είναι προϊστάμενος (απλοποιημένος)
    from .models import UserRole
    is_supervisor = UserRole.objects.filter(
        employee=employee,
        role__name__in=['Προϊστάμενος τμήματος', 'Περιφερειακός Διευθυντής'],
        is_active=True
    ).exists()
    
    if not is_supervisor:
        messages.error(request, 'Δεν έχετε δικαιώματα έγκρισης αιτήσεων.')
        return redirect('users:dashboard')
    
    # Εκκρεμείς αιτήσεις για έγκριση
    pending_requests = LeaveRequest.objects.filter(
        employee__current_service=employee.current_service,
        status__name='ΚΑΤΑΧΩΡΗΘΗΚΕ'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(pending_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'employee': employee,
    }
    
    return render(request, 'users/approval_list.html', context)


@login_required
def approve_leave(request, pk):
    """Έγκριση αίτησης άδειας"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Δεν έχετε δικαιώματα πρόσβασης.')
        return redirect('users:dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Έλεγχος δικαιωμάτων (απλοποιημένος)
    if leave_request.employee.current_service != employee.current_service:
        messages.error(request, 'Δεν έχετε δικαίωμα έγκρισης αυτής της αίτησης.')
        return redirect('users:approval_list')
    
    # Ενημέρωση κατάστασης
    try:
        approved_status = LeaveStatus.objects.get(name='ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ')
        leave_request.status = approved_status
        leave_request.manager_approved_by = employee
        leave_request.save()
        
        messages.success(request, f'Η αίτηση του/της {leave_request.employee} εγκρίθηκε επιτυχώς.')
    except LeaveStatus.DoesNotExist:
        messages.error(request, 'Σφάλμα στην ενημέρωση κατάστασης.')
    
    return redirect('users:approval_list')


@login_required
def reject_leave(request, pk):
    """Απόρριψη αίτησης άδειας"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Δεν έχετε δικαιώματα πρόσβασης.')
        return redirect('users:dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Έλεγχος δικαιωμάτων (απλοποιημένος)
    if leave_request.employee.current_service != employee.current_service:
        messages.error(request, 'Δεν έχετε δικαίωμα απόρριψης αυτής της αίτησης.')
        return redirect('users:approval_list')
    
    # Ενημέρωση κατάστασης
    try:
        rejected_status = LeaveStatus.objects.get(name='ΜΗ_ΕΓΚΡΙΣΗ_ΑΠΟ_ΠΡΟΪΣΤΑΜΕΝΟ')
        leave_request.status = rejected_status
        leave_request.save()
        
        messages.success(request, f'Η αίτηση του/της {leave_request.employee} απορρίφθηκε.')
    except LeaveStatus.DoesNotExist:
        messages.error(request, 'Σφάλμα στην ενημέρωση κατάστασης.')
    
    return redirect('users:approval_list')

@login_required
def leave_delete(request, pk):
    """Διαγραφή αίτησης άδειας (μόνο αν είναι σε κατάσταση ΚΑΤΑΧΩΡΗΘΗΚΕ)"""
    print(f"DEBUG: leave_delete called for pk={pk}, method={request.method}")
    
    try:
        employee = request.user.employee
        print(f"DEBUG: Employee found: {employee.user.email}")
    except Employee.DoesNotExist:
        print("DEBUG: Employee not found")
        messages.error(request, 'Δεν έχετε δικαιώματα για διαγραφή αιτήσεων αδειών.')
        return redirect('users:dashboard')
    
    # Εύρεση της αίτησης
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
    print(f"DEBUG: Leave request found: {leave_request.id}, status: {leave_request.status}")
    
    # Έλεγχος αν μπορεί να διαγραφεί (μόνο εκκρεμείς αιτήσεις)
    if leave_request.status.name != 'ΚΑΤΑΧΩΡΗΘΗΚΕ':
        print(f"DEBUG: Status check failed - current status: {leave_request.status.name}")
        messages.error(request, 'Μπορείτε να διαγράψετε μόνο εκκρεμείς αιτήσεις.')
        return redirect('users:leave_detail', pk=leave_request.pk)
    
    if request.method == 'POST':
        print("DEBUG: Processing POST request for deletion")
        
        # Διαγραφή συνημμένων αρχείων
        import os
        from django.conf import settings
        
        attachment_dir = os.path.join(settings.MEDIA_ROOT, 'leave_attachments', str(leave_request.id))
        if os.path.exists(attachment_dir):
            try:
                import shutil
                shutil.rmtree(attachment_dir)
                print(f"DEBUG: Διαγράφηκε φάκελος συνημμένων: {attachment_dir}")
            except Exception as e:
                print(f"DEBUG: Σφάλμα διαγραφής φακέλου: {e}")
        
        # Διαγραφή της αίτησης
        leave_type = leave_request.leave_type.eidos_adeias
        total_days = leave_request.total_days
        leave_id = leave_request.id
        leave_request.delete()
        
        print(f"DEBUG: Διαγράφηκε η αίτηση {leave_id}")
        messages.success(request, f'Η αίτηση άδειας "{leave_type}" ({total_days} ημέρες) διαγράφηκε επιτυχώς.')
        return redirect('users:leave_list')
    else:
        print("DEBUG: Non-POST request, redirecting to list")
        # GET request - επιβεβαίωση διαγραφής (δεν χρειάζεται template γιατί γίνεται μέσω modal)
        return redirect('users:leave_list')


@login_required
def test_simple_delete(request, pk):
    """Απλή test view για debugging"""
    print(f"TEST_SIMPLE_DELETE: Called with pk={pk}, method={request.method}")
    
    if request.method == 'POST':
        print("TEST_SIMPLE_DELETE: Processing POST")
        messages.success(request, 'Test deletion successful!')
        return redirect('users:leave_list')
    else:
        print("TEST_SIMPLE_DELETE: Processing GET")
        return redirect('users:leave_list')
