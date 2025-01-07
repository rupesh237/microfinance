document.addEventListener('DOMContentLoaded', function () {
    const inputFields = document.querySelectorAll('thead input[type="text"]');
    const tableRows = document.querySelectorAll('tbody tr');

    inputFields.forEach((input) => {
        input.addEventListener('input', function () {
            const fieldId = this.id.replace('search', '').toLowerCase();
            const filterValue = this.value.toLowerCase();

            tableRows.forEach((row) => {
                const cell = row.querySelector(`td:nth-child(${Array.from(inputFields).indexOf(this) + 1})`);
                if (cell) {
                    const cellText = cell.textContent.toLowerCase();
                    row.style.display = cellText.includes(filterValue) ? '' : 'none';
                }
            });
        });
    });
});