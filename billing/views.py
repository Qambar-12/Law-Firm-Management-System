from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import TimeLog,Invoice
from cases.models import Case
from accounts.models import Lawyer
from django.contrib import messages
from decimal import Decimal
import io
from reportlab.pdfgen import canvas

def case_timelogs_view(request, case_id):
    lawyer_id = request.session.get('lawyer_id')
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id)
    case = get_object_or_404(Case, pk=case_id, lawyers=lawyer)

    # If lawyer_id is not in session, stop all their active timers
    if not lawyer_id:
        TimeLog.objects.filter(is_active=True, lawyer__pk=lawyer_id).update(end_time=timezone.now(), is_active=False)

    # Only get the active log for this case
    active_log = TimeLog.objects.filter(lawyer=lawyer, case=case, is_active=True).first()
    timelogs = TimeLog.objects.filter(case=case, lawyer=lawyer).order_by('-start_time')

    context = {
        'case': case,
        'timelogs': timelogs,
        'active_log': active_log,
    }
    return render(request, 'billing/case_timelogs.html', context)


def start_timer_view(request, case_id):
    lawyer_id = request.session.get('lawyer_id')
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id)
    case = get_object_or_404(Case, pk=case_id, lawyers=lawyer)

    # Stop existing active timer
    existing = TimeLog.objects.filter(lawyer=lawyer, is_active=True).first()
    if existing:
        messages.error(request, "You already have an active timer. Please stop it first.")
        return redirect('case_timelogs', case_id=case_id)

    TimeLog.objects.create(
        lawyer=lawyer,
        case=case,
        start_time=timezone.now(),
        is_active=True
    )
    return redirect('case_timelogs', case_id=case_id)


def stop_timer_view(request, case_id):
    lawyer_id = request.session.get('lawyer_id')
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id)

    active_log = TimeLog.objects.filter(lawyer=lawyer, case_id=case_id, is_active=True).first()
    if active_log:
        active_log.end_time = timezone.now()
        active_log.is_active = False
        active_log.save()
    else:
        messages.warning(request, "No active timer found.")

    return redirect('case_timelogs', case_id=case_id)



def case_logs_for_invoice(request, case_id):
    case = get_object_or_404(Case, pk=case_id)
    timelogs = TimeLog.objects.filter(case=case, end_time__isnull=False)
    invoices = case.invoices.all().order_by('-generated_at')
    return render(request, 'billing/case_logs_for_invoice.html', {'case': case, 'timelogs': timelogs, 'invoices': invoices})

def generate_invoice(request, case_id):
    case = get_object_or_404(Case, pk=case_id)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_logs')
        if not selected_ids:
            messages.error(request, "Please select at least one time log to generate an invoice.")
            return redirect('case_logs_for_invoice', case_id=case_id)
        logs = TimeLog.objects.filter(id__in=selected_ids, case=case)

        total_hours = sum(log.duration() for log in logs)
        total_amount = sum(Decimal(log.duration()) * log.lawyer.lawyer_hourly_rate for log in logs)

        invoice = Invoice.objects.create(
            case=case,
            total_hours=total_hours,
            total_amount=total_amount
        )

        # Create basic PDF for now
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"Invoice for Case: {case.case_title}")
        p.drawString(100, 780, f"Total Hours: {total_hours:.2f}")
        p.drawString(100, 760, f"Total Amount: ${total_amount:.2f}")
        p.showPage()
        p.save()

        buffer.seek(0)
        filename = f"invoice_case_{case_id}_{invoice.generated_at.date()}.pdf"
        invoice.invoice_pdf.save(filename, buffer, save=True)

        return redirect('case_logs_for_invoice', case_id=case_id)

    return redirect('case_logs_for_invoice', case_id=case_id)

def delete_invoice(request, invoice_id):
    lawfirm_id = request.session.get('lawfirm_id')
    if not lawfirm_id:
        messages.error(request, "You must be logged in as a Firm to delete invoices.")
        return redirect('firm_login')  # Adjust this to your actual login URL name

    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Ensure the invoice belongs to a case owned by this firm
    if invoice.case.lawfirm.lawfirm_id != lawfirm_id:
        messages.error(request, "You are not authorized to delete this invoice.")
        return redirect('case_logs_for_invoice', case_id=invoice.case.case_id)

    invoice.delete()
    messages.success(request, "Invoice deleted successfully.")
    return redirect('case_logs_for_invoice', case_id=invoice.case.case_id)