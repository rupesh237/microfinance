document.getElementById('add-member-btn').addEventListener('click', function() {
    const formCount = document.querySelectorAll('tbody tr').length;
    fetch(/get_new_form/?count=$:{formCount}, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        const newFormRow = data.form_html;
        const tableBody = document.getElementById('form-table-body');
        tableBody.insertAdjacentHTML('beforeend', newFormRow);
    });
});