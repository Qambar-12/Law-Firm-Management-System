from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import LawFirm
from .captcha import generate_captcha
def homepage(request):
    return render(request, 'accounts/homepage.html')
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

        # CAPTCHA check
        if not captcha_input:
            messages.error(request, 'Captcha is required.')
        elif captcha_input.upper() != captcha_session:
            messages.error(request, 'Incorrect CAPTCHA.')

        # Email and password validations
        elif not lawfirm_email or not password:
            messages.error(request, 'Both email and password are required.')
        else:
            try:
                law_firm = LawFirm.objects.get(lawfirm_email=lawfirm_email)
                if check_password(password, law_firm.password):
                    messages.success(request, f"Welcome, {law_firm.lawfirm_name}!")
                    return render(request,'accounts/firm_dashboard.html')
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

def lawyer_login(request):
    pass
def client_login(request):
    pass

