from django.shortcuts import render, redirect , get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import LawFirm, Lawyer, Client
from cases.models import Case
from .captcha import generate_captcha
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
import datetime,os
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
            messages.success(request,f"Welcome {lawfirm_name}" )
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

        messages.success(request, "Case and Client added successfully, and lawyers assigned.")
        return redirect('firm_dashboard')

    # GET Request: Load form with lawyers dropdown
    return render(request, "accounts/add_case.html", {'lawyers': lawyers_qs})

def firm_view_cases(request):
    lawfirm_id    = request.session.get('lawfirm_id')
    search_query  = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by       = request.GET.get('sort_by', '')

    cases = (Case.objects.filter(lawfirm_id=lawfirm_id).select_related('client').prefetch_related('lawyers'))

    if search_query:
        cases = cases.filter(
            Q(case_title__icontains=search_query) |
            Q(client__client_name__icontains=search_query) |
            Q(lawyers__lawyer_name__icontains=search_query)
        ).distinct()

    if status_filter:
        cases = cases.filter(case_status__iexact=status_filter)

    if sort_by == "created_asc":
        cases = cases.order_by('case_created_at')
    elif sort_by == "created_desc":
        cases = cases.order_by('-case_created_at')
    elif sort_by == "title_asc":
        cases = cases.order_by('case_title')
    elif sort_by == "title_desc":
        cases = cases.order_by('-case_title')

    return render(request, 'accounts/firm_view_case.html', {
        'cases': cases
    })

def lawyer_login(request):
    pass
def client_login(request):
    pass

