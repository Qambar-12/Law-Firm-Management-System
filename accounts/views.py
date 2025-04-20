from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages


def homepage(request):
    return render(request, 'homepage.html')

def firm_signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM firm WHERE email = %s", [email])
            if cursor.fetchone():
                messages.error(request, 'Email already registered.')
                return render(request, 'firm_signup.html')

            cursor.execute("""
                INSERT INTO firm (name, address, email, password, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, [name, address, email, password, phone])

        messages.success(request, 'Signup successful! Please login.')
        return redirect('firm_login')

    return render(request, 'firm_signup.html')


def firm_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        with connection.cursor() as cursor:
            cursor.execute("SELECT firm_id, name FROM firm WHERE email = %s AND password = %s", [email, password])
            firm = cursor.fetchone()

            if firm:
                request.session['firm_id'] = firm[0]
                request.session['firm_name'] = firm[1]
                messages.success(request, f'Welcome {firm[1]}!')
                return redirect('firm_dashboard')  #ye view comment out hai kiun k dashboard template nhi hai

            messages.error(request, 'Invalid credentials.')

    return render(request, 'firm_login.html')

def firm_dashboard(request):
    return render(request, 'firm_dashboard.html')