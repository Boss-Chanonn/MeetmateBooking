// MeetMate main JavaScript file - Beginner-Friendly Version

// Wait for the page to load completely
document.addEventListener('DOMContentLoaded', function() {
    
    // Flash message handling
    var flashMessages = document.getElementsByClassName('flash-message');
    
    for (var i = 0; i < flashMessages.length; i++) {
        var message = flashMessages[i];
        var closeBtn = message.querySelector('.close-btn');
        
        if (closeBtn) {
            // Add click event to close button
            closeBtn.onclick = function() {
                this.parentElement.style.display = 'none';
            };
            
            // Auto-hide success messages after 5 seconds
            if (message.className.indexOf('success') !== -1) {
                setTimeout(function() {
                    message.style.opacity = '0';
                    setTimeout(function() {
                        message.style.display = 'none';
                    }, 300);
                }, 5000);
            }
        }
    }
    
    // Validate booking form if it exists
    var bookingForm = document.querySelector('.booking-form');
    if (bookingForm) {
        var startTime = document.getElementById('time_start');
        var endTime = document.getElementById('time_end');
        
        bookingForm.onsubmit = function(event) {
            if (startTime && endTime) {
                var startTimeValue = startTime.value;
                var endTimeValue = endTime.value;
                
                if (startTimeValue >= endTimeValue) {
                    event.preventDefault();
                    alert('End time must be after start time.');
                    return false;
                }
            }
        };
    }
    
    // Add current date to booking form
    var dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        var today = new Date();
        var year = today.getFullYear();
        var month = today.getMonth() + 1;
        var day = today.getDate();
        
        // Add leading zeros if needed
        if (month < 10) {
            month = '0' + month;
        }
        if (day < 10) {
            day = '0' + day;
        }
        
        dateInput.value = year + '-' + month + '-' + day;
    }
});

// Modal functionality for admin page - Simple version
function setupModalFunctions() {
    // Get all modals
    var modals = document.getElementsByClassName('modal');
    
    // Get all modal open buttons
    var modalOpenBtns = document.querySelectorAll('[data-modal]');
    
    // Get all close buttons
    var closeButtons = document.querySelectorAll('.modal .close');
    
    // Add click event to all open buttons
    for (var i = 0; i < modalOpenBtns.length; i++) {
        var btn = modalOpenBtns[i];
        btn.onclick = function() {
            var modalId = this.getAttribute('data-modal');
            var modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'block';
            }
        };
    }
    
    // Add click event to all close buttons
    for (var i = 0; i < closeButtons.length; i++) {
        var btn = closeButtons[i];
        btn.onclick = function() {
            var modal = this.parentElement.parentElement;
            modal.style.display = 'none';
        };
    }
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        for (var i = 0; i < modals.length; i++) {
            var modal = modals[i];
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
    };
}

// Call modal setup if we're on the admin page
if (document.querySelector('.admin-dashboard')) {
    setupModalFunctions();
}

// Simple function to handle cancel booking
function cancelBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        // Create a form and submit it
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/cancel_booking';
        
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'booking_id';
        input.value = bookingId;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
}

// Simple function to show/hide elements
function toggleElement(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        if (element.style.display === 'none') {
            element.style.display = 'block';
        } else {
            element.style.display = 'none';
        }
    }
}
