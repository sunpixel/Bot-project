document.getElementById('checkoutForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Clear previous error messages
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.textContent = '');

    // Get form values
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const address = document.getElementById('address').value.trim();
    const phone = document.getElementById('phone').value.trim();

    let isValid = true;

    // Validate First Name
    if (firstName === '') {
        document.getElementById('firstNameError').textContent = 'First name is required';
        isValid = false;
    } else if (!/^[a-zA-Z]+$/.test(firstName)) {
        document.getElementById('firstNameError').textContent = 'First name should contain only letters';
        isValid = false;
    }

    // Validate Last Name
    if (lastName === '') {
        document.getElementById('lastNameError').textContent = 'Last name is required';
        isValid = false;
    } else if (!/^[a-zA-Z]+$/.test(lastName)) {
        document.getElementById('lastNameError').textContent = 'Last name should contain only letters';
        isValid = false;
    }

    // Validate Address
    if (address === '') {
        document.getElementById('addressError').textContent = 'Address is required';
        isValid = false;
    } else if (address.length < 10) {
        document.getElementById('addressError').textContent = 'Address should be at least 10 characters long';
        isValid = false;
    }

    // Validate Phone Number
    if (phone === '') {
        document.getElementById('phoneError').textContent = 'Phone number is required';
        isValid = false;
    } else if (!/^[\d\s\-+]+$/.test(phone)) {
        document.getElementById('phoneError').textContent = 'Phone number should contain only digits, spaces, + or -';
        isValid = false;
    } else if (phone.replace(/[^\d]/g, '').length < 8) {
        document.getElementById('phoneError').textContent = 'Phone number should be at least 8 digits';
        isValid = false;
    }

    // If form is valid, proceed with submission
    if (isValid) {
        // In a real application, you would send the data to a server here
        alert('Order placed successfully!');
        this.reset();
    }
});

// Add real-time validation for better UX
document.querySelectorAll('#checkoutForm input, #checkoutForm textarea').forEach(input => {
    input.addEventListener('input', function() {
        const errorElement = document.getElementById(`${this.id}Error`);
        errorElement.textContent = '';
    });
});

document.addEventListener()