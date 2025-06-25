
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
            }        };
    }
});

// Note: Modal functionality, cancelBooking, and toggleElement functions removed as they are not used in templates
