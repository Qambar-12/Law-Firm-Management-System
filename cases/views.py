from django.shortcuts import render , redirect, get_object_or_404
from django.contrib import messages
from accounts.models import LawFirm, Lawyer, Client
from .models import Case
from django.db.models import Q
from accounts.email import welcome_case_email
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
            return render(request, "cases/add_case.html", {'lawyers': lawyers_qs})

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
    return render(request, "cases/add_case.html", {'lawyers': lawyers_qs})


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

    return render(request, 'cases/firm_view_cases.html', context)

def firm_delete_case(request, case_id):
    lawfirm_id = request.session.get('lawfirm_id')
    case = get_object_or_404(Case, pk=case_id, lawfirm_id=lawfirm_id)
    client = case.client

    client.delete()
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
        if lawyer_ids:  # Only update if form provides input
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

    return render(request, "cases/firm_view_case.html", {'case': case, 'client': client, 'lawyers': lawyers_qs})

