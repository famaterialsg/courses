document.addEventListener('DOMContentLoaded', function () {
    // Lắng nghe sự kiện collapse trên các module
    document.querySelectorAll('.nav-link').forEach(function (element) {
        element.addEventListener('click', function () {
            const icon = this.querySelector('i');

            // Kiểm tra xem phần tử collapse có đang mở hay không
            if (this.classList.contains('collapsed')) {
                icon.classList.remove('fa-caret-down');
                icon.classList.add('fa-caret-up');
            } else {
                icon.classList.remove('fa-caret-up');
                icon.classList.add('fa-caret-down');
            }
        });
    });
});