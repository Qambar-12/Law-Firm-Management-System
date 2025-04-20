document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const showSignup = document.getElementById('showSignup');
    const signupModal = document.getElementById('signupModal');
    const closeBtn = document.querySelector('.close-btn');
    const signupForm = document.getElementById('signupForm');
  
    showSignup.addEventListener('click', (e) => {
        e.preventDefault();
        signupModal.style.display = 'flex';
    });
  
    closeBtn.addEventListener('click', () => {
        signupModal.style.display = 'none';
    });
  
    window.addEventListener('click', (e) => {
        if (e.target === signupModal) {
            signupModal.style.display = 'none';
        }
    });
  
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (email && password) {
            window.location.href = 'dashboard.html';
        } else {
            alert('Please enter both email and password');
        }
    });
  
    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        if (!email || !password || !confirmPassword) {
            alert('Please fill in all fields');
            return;
        }
        
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }
        
        alert('Account created successfully! You can now login.');
        signupModal.style.display = 'none';
        signupForm.reset();
    });
  });