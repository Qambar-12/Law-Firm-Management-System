from django.core.mail import send_mail
from django.conf import settings
import time
def welcome_firm_email(user_email):
    """Send welcome email to the firm after successful signup."""
    subject = 'Welcome to Firmly'
    message = 'Thank you for signing up!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)
def welcome_lawyer_email(user_email,lawfirm_name,lawyer_name):
    """Send welcome email to the lawyer after successful signup."""
    subject = f'Welcome {lawyer_name} '
    message = f'Thank you for signing up! You are now a part of the law firm {lawfirm_name}.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)    
def welcome_case_email(lawfirm_name,case_name,client_name,client_email,lawyer_emails):  
    subject_client = f'Hi {client_name}'  
    message_client = f'Your case {case_name} has been successfully created by {lawfirm_name}.'
    subject_lawyer = f'Case Assignment'
    message_lawyer = f'You are assigned to the case {case_name}.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list_client = [client_email]
    recipient_list_lawyer = lawyer_emails
    send_mail(subject_client, message_client, email_from, recipient_list_client)
    send_mail(subject_lawyer, message_lawyer, email_from, recipient_list_lawyer)
def send_verification_email(user_email, verification_code):
    """Send verification email to user with the verification code. Return the start time of the email sending process.
    The start time is used to calculate the time taken to verify the code. If the time taken is more than 60 seconds"""
    subject = 'Your Verification Code'
    message = f'Please enter the following for TOTP: {verification_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)
    return time.time()

