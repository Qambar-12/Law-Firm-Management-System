from django.shortcuts import render, redirect , get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import LawFirm, Lawyer, Client
from cases.models import Case
from .captcha import generate_captcha
from .email import send_verification_email,welcome_firm_email , welcome_lawyer_email , welcome_case_email
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
import datetime
from datetime import datetime, timedelta
import os,random
def homepage(request):
    return render(request, 'accounts/homepage.html')
def firm_dashboard(request):
    if request.session.get('lawfirm_logged_in'):
        return render(request, 'accounts/firm_dashboard.html')
def firm_signup(request):
    if request.method == 'POST':
        lawfirm_name = request.POST.get('lawfirm_name', '').strip()
        lawfirm_email = request.POST.get('lawfirm_email', '').strip()
        lawfirm_contact = request.POST.get('lawfirm_contact', '').strip()
        country = request.POST.get('country', '').strip()
        state = request.POST.get('state', '').strip()
        street_address = request.POST.get('street_address', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        captcha_input = request.POST.get('captcha', '').strip().upper()
        lawfirm_address = f"{street_address}, {state}, {country}"
        form_data = {
            'lawfirm_name': lawfirm_name,
            'lawfirm_email': lawfirm_email,
            'lawfirm_contact': lawfirm_contact,
            'street_address': street_address,
            'country': country,
            'state': state
        }

        session_captcha = request.session.get('captcha_code', '')

        # Validations
        if not all([lawfirm_name, lawfirm_email, lawfirm_contact,country,state, password, confirm_password, captcha_input]):
            messages.error(request, 'All fields are required.')
        elif LawFirm.objects.filter(lawfirm_name=lawfirm_name).exists():
            messages.error(request, 'Law firm name already taken.')
        elif len(password) < 7:
            messages.error(request, 'Password must be at least 7 characters long.')
        elif lawfirm_contact.isdigit() == False:
            messages.error(request, 'Contact number must be numeric.')    
        elif len(lawfirm_contact) < 11:
            messages.error(request, 'Contact number must be at least 11 digits long.')     
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif captcha_input != session_captcha:
            messages.error(request, 'Invalid captcha.')
        else:
            try:
                validate_email(lawfirm_email)
            except ValidationError:
                messages.error(request, 'Invalid email format.')
                return reload_form(request, form_data)

            if LawFirm.objects.filter(lawfirm_email=lawfirm_email).exists():
                messages.error(request, 'Email already registered.')
                return reload_form(request, form_data)

            # Save firm
            LawFirm.objects.create(
                lawfirm_name=lawfirm_name,
                lawfirm_email=lawfirm_email,
                lawfirm_contact=lawfirm_contact,
                lawfirm_address=lawfirm_address,
                password=make_password(password),
            )

            messages.success(request, 'Law firm registered successfully!')
            welcome_firm_email(lawfirm_email)
            messages.success(request,f"Welcome {lawfirm_name}" )
            request.session['lawfirm_logged_in'] = True
            return render(request,'accounts/firm_dashboard.html')
        return reload_form(request, form_data)
    else:
        return reload_form(request)


def reload_form(request, form_data=None):
    """Helper to regenerate captcha & reload form with preserved data"""
    captcha_code, captcha_image = generate_captcha()
    request.session['captcha_code'] = captcha_code
    context = form_data or {}
    context['captcha_image'] = captcha_image
    return render(request, 'accounts/firm_signup.html', context)


def firm_login(request):
    if request.method == 'POST':
        lawfirm_email = request.POST.get('lawfirm_email', '').strip()
        password = request.POST.get('password', '')
        captcha_input = request.POST.get('captcha', '').strip()
        captcha_session = request.session.get('captcha_code', '')

        context = {
            'lawfirm_email': lawfirm_email,
            'captcha_image': '',
        }
        if not all([lawfirm_email, password, captcha_input]):
            messages.error(request, 'All fields are required.')
        elif captcha_input.upper() != captcha_session:
            messages.error(request, 'Incorrect CAPTCHA.')
        else:
            try:
                law_firm = LawFirm.objects.get(lawfirm_email=lawfirm_email)
                if check_password(password, law_firm.password):
                    messages.success(request, f"Welcome, {law_firm.lawfirm_name}!")
                    request.session['lawfirm_logged_in'] = True
                    request.session['lawfirm_id'] = law_firm.lawfirm_id

                    return redirect('firm_dashboard')
                else:
                    messages.error(request, 'Incorrect password. Please try again.')
            except LawFirm.DoesNotExist:
                messages.error(request, 'No law firm registered with that email.')

        captcha_code, captcha_image = generate_captcha()
        request.session['captcha_code'] = captcha_code
        context['captcha_image'] = captcha_image

        return render(request, 'accounts/firm_login.html', context)

    else:
        captcha_code, captcha_image = generate_captcha()
        request.session['captcha_code'] = captcha_code
        return render(request, 'accounts/firm_login.html', {'captcha_image': captcha_image})

def firm_logout(request):
    if request.session.get('lawfirm_logged_in'):
        request.session['lawfirm_logged_in'] = False
        del request.session['lawfirm_id']
        messages.success(request, 'Logged out successfully.')
    return redirect('homepage')


def add_lawyer(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        hire_date = request.POST.get('hire_date')
        salary = request.POST.get('salary')
        specialization = request.POST.get('specialization')
        profile_picture = request.FILES.get('profile_picture')


        if email and (Lawyer.objects.filter(lawyer_email=email).exists() or LawFirm.objects.filter(lawfirm_email=email).exists()):
            messages.error(request, "Email already exists.")
            return render(request, "accounts/add_lawyer.html")
        if phone and Lawyer.objects.filter(lawyer_contact=phone).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, "accounts/add_lawyer.html")
        hire_date_obj = datetime.datetime.strptime(hire_date, "%Y-%m-%d").date()
        if hire_date_obj > datetime.date.today():
            messages.error("Invalid hire date.")
            return render(request, "accounts/add_lawyer.html")

        if profile_picture and not profile_picture.name.lower().endswith((".jpg", ".jpeg", ".png")):
            messages.error("Profile picture must be a .jpg, .jpeg, or .png file.")

            return render(request, "accounts/add_lawyer.html")
        lawfirm = LawFirm.objects.filter(lawfirm_id=request.session['lawfirm_id']).first()
        new_lawyer = Lawyer.objects.create(
            lawfirm=lawfirm,
            lawyer_name=full_name,
            lawyer_email=email,
            lawyer_contact=phone,
            lawyer_hire_date=hire_date_obj,
            lawyer_salary=salary,
            lawyer_specialization=specialization,
        )

        if profile_picture:
            ext = os.path.splitext(profile_picture.name)[1]
            filename = f"{full_name.replace(' ', '_')}_{new_lawyer.lawyer_id}{ext}"
            folder_path = f"lawyer_profiles/{lawfirm.lawfirm_name}_{lawfirm.lawfirm_id}/{specialization.replace(' ', '_')}/"
            fs = FileSystemStorage(location='media/' + folder_path)
            saved_path = fs.save(filename, profile_picture)

            new_lawyer.lawyer_profile_picture.name = folder_path + filename
            new_lawyer.save()

        messages.success(request, "Lawyer added successfully.")
        welcome_lawyer_email(email,lawfirm.lawfirm_name,full_name)
        return render(request, 'accounts/firm_dashboard.html')
    return render(request, "accounts/add_lawyer.html")

def firm_view_lawyers(request):
    lawfirm_id = request.session.get('lawfirm_id')
    search_query = request.GET.get('search', '')
    specialization_filter = request.GET.get('specialization', '')
    sort_by = request.GET.get('sort_by', '')

    lawyers = Lawyer.objects.filter(lawfirm_id=lawfirm_id)

    if search_query:
        lawyers = lawyers.filter(
            Q(lawyer_name__icontains=search_query) | 
            Q(lawyer_email__icontains=search_query)
        )

    if specialization_filter:
        lawyers = lawyers.filter(lawyer_specialization__iexact=specialization_filter)

    if sort_by == "hire_date_asc":
        lawyers = lawyers.order_by('lawyer_hire_date')
    elif sort_by == "hire_date_desc":
        lawyers = lawyers.order_by('-lawyer_hire_date')
    elif sort_by == "salary_asc":
        lawyers = lawyers.order_by('lawyer_salary')
    elif sort_by == "salary_desc":
        lawyers = lawyers.order_by('-lawyer_salary')


    context = {
        'lawyers': lawyers
    }

    return render(request, 'accounts/firm_view_lawyers.html', context)

def firm_delete_lawyer(request, lawyer_id):
    lawfirm_id = request.session.get('lawfirm_id')

    lawyer = get_object_or_404(Lawyer, pk=lawyer_id, lawfirm_id=lawfirm_id)

    # Delete profile picture file if it exists
    if lawyer.lawyer_profile_picture:
        picture_path = os.path.join(settings.MEDIA_ROOT, lawyer.lawyer_profile_picture.name)
        if os.path.isfile(picture_path):
            os.remove(picture_path)

    # Delete the lawyer record
    lawyer.delete()

    messages.success(request, "Lawyer deleted successfully.")
    return redirect('firm_view_lawyers')

def firm_update_lawyer(request, lawyer_id):
    lawfirm_id = request.session.get('lawfirm_id')
    lawfirm = get_object_or_404(LawFirm, pk=lawfirm_id)
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id, lawfirm_id=lawfirm_id)

    if request.method == "POST":
        updated = False 

        full_name = request.POST.get('lawyer_name', '').strip()
        email = request.POST.get('lawyer_email', '').strip()
        phone = request.POST.get('lawyer_contact', '').strip()
        hire_date = request.POST.get('lawyer_hire_date', '').strip()
        salary = request.POST.get('lawyer_salary', '').strip()
        specialization = request.POST.get('lawyer_specialization', '').strip()
        profile_picture = request.FILES.get('lawyer_profile_picture')

        # 1. Validate email
        if email and email != lawyer.lawyer_email:
            if Lawyer.objects.exclude(pk=lawyer_id).filter(lawyer_email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('firm_view_lawyers')
            lawyer.lawyer_email = email
            updated = True

        # 2. Validate phone
        if phone and phone != lawyer.lawyer_contact:
            if Lawyer.objects.exclude(pk=lawyer_id).filter(lawyer_contact=phone).exists():
                messages.error(request, "Phone number already exists.")
                return redirect('firm_view_lawyers')
            lawyer.lawyer_contact = phone
            updated = True

        # 3. Validate hire date
        if hire_date:
            try:
                hire_date_obj = datetime.datetime.strptime(hire_date, "%Y-%m-%d").date()
                if hire_date_obj > datetime.date.today():
                    messages.error(request, "Invalid hire date.")
                    return redirect('firm_view_lawyers')
                if hire_date_obj != lawyer.lawyer_hire_date:
                    lawyer.lawyer_hire_date = hire_date_obj
                    updated = True
            except ValueError:
                messages.error(request, "Invalid hire date format.")
                return redirect('firm_view_lawyers')

        # 4. Update simple fields if changed
        if full_name and full_name != lawyer.lawyer_name:
            lawyer.lawyer_name = full_name
            updated = True

        if salary and salary != str(lawyer.lawyer_salary):
            lawyer.lawyer_salary = salary
            updated = True

        if specialization and specialization != lawyer.lawyer_specialization:
            lawyer.lawyer_specialization = specialization
            updated = True

        # 5. Handle profile picture upload
        if profile_picture:
            if not profile_picture.name.lower().endswith((".jpg", ".jpeg", ".png")):
                messages.error(request, "Profile picture must be a .jpg, .jpeg, or .png file.")
                return redirect('firm_view_lawyers')

            # Delete old picture if exists
            if lawyer.lawyer_profile_picture and lawyer.lawyer_profile_picture.name:
                old_picture_path = os.path.join(settings.MEDIA_ROOT, lawyer.lawyer_profile_picture.name)
                if os.path.isfile(old_picture_path):
                    os.remove(old_picture_path)

            ext = os.path.splitext(profile_picture.name)[1]
            filename = f"{full_name.replace(' ', '_')}_{lawyer.lawyer_id}{ext}"
            folder_path = f"lawyer_profiles/{lawfirm.lawfirm_name}_{lawfirm_id}/{specialization.replace(' ', '_')}/"
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_path))
            saved_path = fs.save(filename, profile_picture)

            lawyer.lawyer_profile_picture.name = os.path.join(folder_path, filename)
            updated = True

        # 6. Save only if something changed
        if updated:
            lawyer.save()
            messages.success(request, "Lawyer updated successfully.")
        else:
            messages.info(request, "No changes detected.")

        return redirect('firm_view_lawyers')

    return render(request, "accounts/firm_view_lawyers.html", {'lawyer': lawyer})

def add_case(request):
    firm = LawFirm.objects.filter(lawfirm_id=request.session['lawfirm_id']).first()
    lawyers_qs = firm.lawyers.all()

    if request.method == "POST":
        case_title = request.POST.get('case_title')  
        case_description = request.POST.get('case_description')  
        case_type = request.POST.get('case_type') 
        case_status = request.POST.get('case_status') 
        
        client_name = request.POST.get('client_name') 
        client_email = request.POST.get('client_email')  
        client_contact = request.POST.get('client_contact')  
        client_address = request.POST.get('client_address')  

        lawyer_ids = request.POST.getlist('lawyer_ids') 

        # --- Validate duplicates ---
        if Client.objects.filter(client_email=client_email, lawfirm=firm).exists():
            messages.error(request, "Client with this email already exists.")
            return render(request, "accounts/add_case.html", {'lawyers': lawyers_qs})
        if Client.objects.filter(client_contact=client_contact, lawfirm=firm).exists():
            messages.error(request, "Client with this contact already exists.")
            return render(request, "accounts/add_case.html", {'lawyers': lawyers_qs})

        client = Client.objects.create(
            lawfirm=firm,
            client_name=client_name,
            client_email=client_email,
            client_contact=client_contact,
            client_address=client_address
        )

        case = Case.objects.create(
            lawfirm=firm,
            client=client,
            case_title=case_title,
            case_description=case_description,
            case_type=case_type,
            case_status=case_status
        )

        # --- Assign Lawyers (Many-to-Many) ---
        selected_lawyers = lawyers_qs.filter(pk__in=lawyer_ids)
        case.lawyers.set(selected_lawyers)
        welcome_case_email(firm.lawfirm_name,case.case_title,client.client_name,client.client_email,[lawyer.lawyer_email for lawyer in selected_lawyers])
        messages.success(request, "Case and Client added successfully, and lawyers assigned.")
        return redirect('firm_dashboard')

    # GET Request: Load form with lawyers dropdown
    return render(request, "accounts/add_case.html", {'lawyers': lawyers_qs})


def firm_view_cases(request):
    lawfirm_id = request.session.get('lawfirm_id')
    search_query = request.GET.get('search', '')
    case_type_filter = request.GET.get('case_type', '')
    case_status_filter = request.GET.get('case_status', '')
    sort_by = request.GET.get('sort_by', '')

    cases = Case.objects.filter(lawfirm_id=lawfirm_id)

    if search_query:
        cases = cases.filter(
            Q(case_title__icontains=search_query) |
            Q(client__client_name__icontains=search_query) |
            Q(client__client_email__icontains=search_query)
        )

    if case_type_filter:
        cases = cases.filter(case_type__iexact=case_type_filter)

    if case_status_filter:
        cases = cases.filter(case_status__iexact=case_status_filter)

    if sort_by == "created_asc":
        cases = cases.order_by('created_at')
    elif sort_by == "created_desc":
        cases = cases.order_by('-created_at')

    context = {
        'cases': cases
    }

    return render(request, 'accounts/firm_view_cases.html', context)

def firm_delete_case(request, case_id):
    lawfirm_id = request.session.get('lawfirm_id')
    case = get_object_or_404(Case, pk=case_id, lawfirm_id=lawfirm_id)

    case.delete()
    messages.success(request, "Case deleted successfully.")
    return redirect('firm_view_case')

def firm_update_case(request, case_id):
    lawfirm_id = request.session.get('lawfirm_id')
    lawfirm = get_object_or_404(LawFirm, pk=lawfirm_id)
    case = get_object_or_404(Case, pk=case_id, lawfirm_id=lawfirm_id)

    # Retrieve existing client and lawyers for the case
    client = case.client
    lawyers_qs = lawfirm.lawyers.all()

    if request.method == "POST":
        updated = False

        # Case fields
        case_title = request.POST.get('case_title', '').strip()
        case_description = request.POST.get('case_description', '').strip()
        case_type = request.POST.get('case_type', '').strip()
        case_status = request.POST.get('case_status', '').strip()

        # Client fields
        client_name = request.POST.get('client_name', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        client_contact = request.POST.get('client_contact', '').strip()
        client_address = request.POST.get('client_address', '').strip()

        # --- Validate client info ---
        if client_email and client_email != client.client_email:
            if Client.objects.filter(client_email=client_email, lawfirm=lawfirm).exists():
                messages.error(request, "Client with this email already exists.")
                return redirect('firm_view_case', case_id=case.id)
            client.client_email = client_email
            updated = True

        if client_contact and client_contact != client.client_contact:
            if Client.objects.filter(client_contact=client_contact, lawfirm=lawfirm).exists():
                messages.error(request, "Client with this contact already exists.")
                return redirect('firm_view_case', case_id=case.id)
            client.client_contact = client_contact
            updated = True

        # --- Update case fields ---
        if case_title and case_title != case.case_title:
            case.case_title = case_title
            updated = True

        if case_description and case_description != case.case_description:
            case.case_description = case_description
            updated = True

        if case_type and case_type != case.case_type:
            case.case_type = case_type
            updated = True

        if case_status and case_status != case.case_status:
            case.case_status = case_status
            updated = True

        # --- Update client info ---
        if client_name and client_name != client.client_name:
            client.client_name = client_name
            updated = True

        if client_address and client_address != client.client_address:
            client.client_address = client_address
            updated = True

        # --- Assign Lawyers (Many-to-Many) ---
        lawyer_ids = request.POST.getlist('lawyer_ids')
        lawyer_ids = [id for id in lawyer_ids if id.strip() != '']
        print("POST lawyer_ids:", request.POST.getlist('lawyer_ids'))
        selected_lawyers = lawyers_qs.filter(pk__in=lawyer_ids)
        case.lawyers.set(selected_lawyers)
        updated = True

        # Save client and case updates
        if updated:
            client.save()
            case.save()
            messages.success(request, "Case and Client updated successfully.")
        else:
            messages.info(request, "No changes detected.")

        return redirect('firm_view_case')

    return render(request, "accounts/firm_view_case.html", {'case': case, 'client': client, 'lawyers': lawyers_qs})

def firm_lawyer_cases(request, lawyer_id):
    lawfirm_id = request.session.get('lawfirm_id')
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id, lawfirm_id=lawfirm_id)

    # Filter cases where this lawyer is assigned
    cases = Case.objects.filter(lawyers=lawyer, lawfirm_id=lawfirm_id).distinct()

    return render(request, 'accounts/firm_lawyer_cases.html', {
        'lawyer': lawyer,
        'cases': cases
    })



def user_login(request, role):
    # role will be either "lawyer" or "client"
    if request.method == "POST":
        totp = request.POST.get('totp')

        if not totp:
            # Email + CAPTCHA step
            user_email = request.POST.get('user_email', '').strip()
            captcha_input = request.POST.get('captcha', '').strip()
            captcha_session = request.session.get('captcha', '')

            context = {
                'user_email': user_email,
                'captcha_image': '',
                'role': role,
            }


            print("User email:", user_email)
            if captcha_input.upper() != captcha_session:
                messages.error(request, 'Incorrect CAPTCHA.')
                captcha_code, captcha_image = generate_captcha()
                request.session['captcha'] = captcha_code
                context['captcha_image'] = captcha_image
                return render(request, 'accounts/user_login.html', context)

            try:
                if role == 'lawyer':
                    user = Lawyer.objects.get(lawyer_email=user_email)
                    print("Lawyer found:", user.lawyer_name)
                elif role == 'client':
                    user = Client.objects.get(client_email=user_email)
                else:
                    raise ValueError("Invalid role")
            except (Lawyer.DoesNotExist,Client.DoesNotExist):
                messages.error(request, f"No {role} registered with that email.")
                captcha_code, captcha_image = generate_captcha()
                request.session['captcha'] = captcha_code
                context['captcha_image'] = captcha_image
                return render(request, 'accounts/user_login.html', context)

            # If everything OK, generate TOTP and email it
            totp_code = str(random.randint(100000, 999999))
            request.session['totp'] = totp_code
            request.session['totp_generated_at'] = datetime.now().isoformat()
            request.session['user_email'] = user_email
            request.session['role'] = role

            send_verification_email(user_email, totp_code)

            messages.success(request, "A verification code has been sent to your email.")
            return render(request, 'accounts/user_login.html', {'show_totp': True, 'user_email': user_email, 'role': role})

        else:
            # TOTP step
            session_totp = request.session.get('totp')
            totp_generated_at = request.session.get('totp_generated_at')
            role = request.session.get('role')

            if not totp_generated_at:
                messages.error(request, "TOTP has expired. Please try again.")
                return redirect('user_login', role=role)

            totp_generated_at = datetime.fromisoformat(totp_generated_at)
            if datetime.now() > totp_generated_at + timedelta(seconds=60):
                messages.error(request, "TOTP has expired. Please try again.")
                del request.session['totp']
                del request.session['totp_generated_at']
                return redirect('user_login', role=role)

            if totp == session_totp:
                user_email = request.session.get('user_email')

                try:
                    if role == 'lawyer':
                        user = Lawyer.objects.get(lawyer_email=user_email)
                    elif role == 'client':
                        user = Client.objects.get(client_email=user_email)
                    else:
                        raise ValueError("Invalid role")
                except Exception:
                    messages.error(request, "Something went wrong. Please try again.")
                    return redirect('user_login', role=role)

                request.session[f'{role}_logged_in'] = True
                request.session[f'{role}_id'] = getattr(user, f'{role}_id')

                # Clean session
                for key in ['totp', 'totp_generated_at', 'user_email', 'role']:
                    request.session.pop(key, None)

                messages.success(request, f"Welcome {getattr(user, f'{role}_name')}!")
                return redirect('lawyer_dashboard') if role == 'lawyer' else redirect('client_dashboard')
            else:
                messages.error(request, "Invalid TOTP.")
                return render(request, 'accounts/user_login.html', {'show_totp': True, 'user_email': request.session.get('user_email'), 'role': role})

    else:
        # Initial GET
        captcha_code, captcha_image = generate_captcha()
        request.session['captcha'] = captcha_code
        return render(request, 'accounts/user_login.html', {'captcha_image': captcha_image, 'role': role})

def lawyer_dashboard(request):
    """
    View for Lawyer Dashboard.
    Displays cases assigned to the logged-in lawyer with search, filter, and sort options.
    """
    if not request.session.get('lawyer_logged_in'):
        messages.error(request, "You need to log in first.")
        return redirect('user_login', role='lawyer')

    lawyer_id = request.session.get('lawyer_id')
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id)

    # Search, filter, and sort options
    search_query = request.GET.get('search', '')
    case_type_filter = request.GET.get('case_type', '')
    case_status_filter = request.GET.get('case_status', '')
    sort_by = request.GET.get('sort_by', '')

    # Filter cases assigned to the logged-in lawyer
    cases = Case.objects.filter(lawyers=lawyer)

    if search_query:
        cases = cases.filter(
            Q(case_title__icontains=search_query) |
            Q(client__client_name__icontains=search_query) |
            Q(client__client_email__icontains=search_query)
        )

    if case_type_filter:
        cases = cases.filter(case_type__iexact=case_type_filter)

    if case_status_filter:
        cases = cases.filter(case_status__iexact=case_status_filter)

    if sort_by == "created_asc":
        cases = cases.order_by('case_created_at')
    elif sort_by == "created_desc":
        cases = cases.order_by('-case_created_at')

    context = {
        'cases': cases,
        'lawyer': lawyer,
    }

    return render(request, 'accounts/lawyer_dashboard.html', context)

def lawyer_logout(request):
    if request.session.get('lawyer_logged_in'):
        request.session['lawyer_logged_in'] = False
        del request.session['lawyer_id']
        messages.success(request, 'Logged out successfully.')
    return redirect('homepage')


def client_dashboard(request):
    """
    View for Client Dashboard.
    Displays all cases associated with the logged-in client.
    """
    if not request.session.get('client_logged_in'):
        messages.error(request, "You need to log in first.")
        return redirect('user_login', role='client')

    client_id = request.session.get('client_id')
    client = get_object_or_404(Client, pk=client_id)

    # Search, filter, and sort options
    search_query = request.GET.get('search', '')
    case_status_filter = request.GET.get('case_status', '')
    sort_by = request.GET.get('sort_by', '')

    # Filter cases associated with the client
    cases = Case.objects.filter(client=client).prefetch_related('lawyers')

    if search_query:
        cases = cases.filter(
            Q(case_title__icontains=search_query) |
            Q(lawfirm__lawfirm_name__icontains=search_query) |
            Q(lawyers__lawyer_name__icontains=search_query)
        ).distinct()

    if case_status_filter:
        cases = cases.filter(case_status__iexact=case_status_filter)

    if sort_by == "created_asc":
        cases = cases.order_by('case_created_at')
    elif sort_by == "created_desc":
        cases = cases.order_by('-case_created_at')

    context = {
        'cases': cases,
        'client': client,
    }

    return render(request, 'accounts/client_dashboard.html', context)
def client_logout(request):
    if request.session.get('client_logged_in'):
        request.session['client_logged_in'] = False
        del request.session['client_id']
        messages.success(request, 'Logged out successfully.')
    return redirect('homepage')