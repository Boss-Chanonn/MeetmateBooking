// MeetMate main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Flash message handling
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        const closeBtn = message.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.display = 'none';
            });
            
            // Auto-hide success messages after 5 seconds
            if (message.classList.contains('success')) {
                setTimeout(() => {
                    message.style.opacity = '0';
                    setTimeout(() => {
                        message.style.display = 'none';
                    }, 300);
                }, 5000);
            }
        }
    });
      // Validate booking form if it exists
    const bookingForm = document.querySelector('.booking-form');
    if (bookingForm) {
        const startTime = document.getElementById('time_start');
        const endTime = document.getElementById('time_end');
        
        bookingForm.addEventListener('submit', function(event) {
            if (startTime && endTime) {
                const startTimeValue = startTime.value;
                const endTimeValue = endTime.value;
                  if (startTimeValue >= endTimeValue) {
                    event.preventDefault();
                    alert('End time must be after start time.');
                    return false;
                }
            }
        });
    }
    
    // Add current date to booking form
    const dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        dateInput.value = `${year}-${month}-${day}`;
    }
});

// Modal functionality for admin page
function setupModalFunctions() {
    // Get all modals
    const modals = document.querySelectorAll('.modal');
    
    // Get all modal open buttons
    const modalOpenBtns = document.querySelectorAll('[data-modal]');
    
    // Get all close buttons
    const closeButtons = document.querySelectorAll('.modal .close');
    
    // Add click event to all open buttons
    modalOpenBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.dataset.modal;
            document.getElementById(modalId).style.display = 'block';
        });
    });
    
    // Add click event to all close buttons
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            modal.style.display = 'none';
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// Call modal setup if we're on the admin page
if (document.querySelector('.admin-dashboard')) {
    setupModalFunctions();
}
