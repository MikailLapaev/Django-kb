// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    
    // ===== USER DROPDOWN MENU =====
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');
    const userMenuTrigger = document.getElementById('userMenuTrigger');

    if (userMenu && userDropdown && userMenuTrigger) {
        userMenuTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });

        document.addEventListener('click', function(e) {
            if (!userMenu.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                userDropdown.classList.remove('show');
            }
        });
    }

    // ===== AUTO-DISMISS MESSAGES =====
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(msg) {
        const closeBtn = msg.querySelector('.message-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                msg.remove();
            });
        }
        
        setTimeout(function() {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.3s';
            setTimeout(function() {
                msg.remove();
            }, 300);
        }, 5000);
    });

    // ===== FORM VALIDATION =====
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        const inputs = form.querySelectorAll('.form-control');
        
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (this.value.trim() === '' && this.required) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.value.trim() !== '') {
                    this.classList.remove('is-invalid');
                }
            });
        });
    });
});

function confirmDelete(message) {
    return confirm(message || 'Вы уверены?');
}