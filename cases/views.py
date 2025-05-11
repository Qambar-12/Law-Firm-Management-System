from django.shortcuts import render , redirect, get_object_or_404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from accounts.models import LawFirm,Lawyer, Client
from chat.models import ChatRoom
from .models import Case , Document
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from accounts.email import welcome_case_email
import os
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
        if Client.objects.filter(client_email=client_email, lawfirm=firm).exists() or Lawyer.objects.filter(lawyer_email=client_email, lawfirm=firm).exists():
            messages.error(request, "Email already exists.")
            return render(request, "cases/add_case.html", {'lawyers': lawyers_qs})
        if Client.objects.filter(client_contact=client_contact, lawfirm=firm).exists() or Lawyer.objects.filter(lawyer_contact=client_contact, lawfirm=firm).exists():
            messages.error(request, "Contact already exists.")
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

        # Create a chatroom for the case
        ChatRoom.objects.create(case=case)
        # --- Assign Lawyers (Many-to-Many) ---
        selected_lawyers = lawyers_qs.filter(pk__in=lawyer_ids)
        case.lawyers.set(selected_lawyers)
        welcome_case_email(firm.lawfirm_name,case.case_title,client.client_name,client.client_email,[lawyer.lawyer_email for lawyer in selected_lawyers])
        messages.success(request, "Case and Client added successfully, and lawyers assigned.")
        return redirect('firm_dashboard')

    # GET Request: Load form with lawyers dropdown
    return render(request, "cases/add_case.html", {'lawyers': lawyers_qs})


def firm_view_case(request):
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
    
    ChatRoom.objects.filter(case=case).delete()  # Delete associated chatroom
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
            if Client.objects.filter(client_email=client_email, lawfirm=lawfirm).exists() :
                messages.error(request, "Client with this email already exists.")
                return redirect('firm_view_case')
            client.client_email = client_email
            updated = True

        if client_contact and client_contact != client.client_contact:
            if Client.objects.filter(client_contact=client_contact, lawfirm=lawfirm).exists() or Lawyer.objects.filter(lawyer_contact=client_contact, lawfirm=lawfirm).exists():
                messages.error(request, "Client with this contact already exists.")
                return redirect('firm_view_case')
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
        if lawyer_ids:
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

    return render(request, "cases/firm_view_cases.html", {'case': case, 'client': client, 'lawyers': lawyers_qs})

def view_doc(request, case_id):
    """
    Generalized view for documents, works for lawfirm, lawyer, and client.
    Determines role based on available session keys.
    """
    # Identify role and user
    if 'lawfirm_id' in request.session:
        role = 'lawfirm'
        user_id = request.session['lawfirm_id']
        user = get_object_or_404(LawFirm, pk=user_id)
        case = get_object_or_404(Case, pk=case_id, lawfirm_id=user_id)
    elif 'lawyer_id' in request.session:
        role = 'lawyer'
        user_id = request.session['lawyer_id']
        user = get_object_or_404(Lawyer, pk=user_id)
        case = get_object_or_404(Case, pk=case_id, lawyers=user)
    elif 'client_id' in request.session:
        role = 'client'
        user_id = request.session['client_id']
        user = get_object_or_404(Client, pk=user_id)
        case = get_object_or_404(Case, pk=case_id, client=user)
    else:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('homepage')
        
    if role == 'lawfirm':
        lawfirm_name = user.lawfirm_name
        lawfirm_id = user.lawfirm_id
    else:
        lawfirm_name = user.lawfirm.lawfirm_name
        lawfirm_id = user.lawfirm.lawfirm_id
    documents = Document.objects.filter(case=case)

    # Filtering
    search_query = request.GET.get('search_doc', '')
    uploaded_by_filter = request.GET.get('uploaded_by', '')
    sort_by = request.GET.get('sort_by', '')

    if search_query:
        documents = documents.filter(doc_name__icontains=search_query)

    if uploaded_by_filter:
        content_type_map = {
            'lawfirm': LawFirm,
            'lawyer': Lawyer,
            'client': Client
        }
        model = content_type_map.get(uploaded_by_filter)
        if model:
            ct_id = ContentType.objects.get_for_model(model).id
            documents = documents.filter(uploaded_by_content_type_id=ct_id)

    if sort_by == "recent":
        documents = documents.order_by('-uploaded_at')
    elif sort_by == "oldest":
        documents = documents.order_by('uploaded_at')

    # Document Upload
    if request.method == "POST":
        if 'delete_doc_id' in request.POST:
            doc_id = request.POST.get('delete_doc_id')
            doc = get_object_or_404(Document, pk=doc_id, case=case)
            file_path = os.path.join(settings.MEDIA_ROOT, str(doc.doc_path))
            if os.path.exists(file_path):
                os.remove(file_path)
            doc.delete()
            messages.success(request, "Document deleted successfully.")
            return redirect('view_doc', case_id=case_id)
        else:
            doc_name = request.POST.get('doc_name', '').strip()
            doc_file = request.FILES.get('doc_file')
            doc_type = request.POST.get('doc_type', '').strip()

            if doc_file:
                folder_path = f"case_documents/{lawfirm_name}_{lawfirm_id}/{case.case_title}_{case.case_id}/{case.case_type}/{role}/{doc_type}/"
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_path))
                file_name = f"{doc_name}_{doc_file.name}"
                saved_file_path = fs.save(file_name, doc_file)

                Document.objects.create(
                    case=case,
                    doc_name=doc_name,
                    doc_path=os.path.join(folder_path, file_name),
                    doc_type=doc_type,
                    uploaded_by_content_type=ContentType.objects.get_for_model(type(user)),
                    uploaded_by_object_id=user_id,
                )
                messages.success(request, "Document uploaded successfully.")
            else:
                messages.error(request, "Please select a file to upload.")

    context = {
        'case': case,
        'documents': documents,
        'uploaded_by_filter': uploaded_by_filter,
        'user_role': role,
        'user_id': user_id,
    }
    return render(request, 'cases/view_documents.html', context)