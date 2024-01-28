function getDate() {
    const date_start = document.getElementById('date_start').value;
    const date_end = document.getElementById('date_end').value;

    if (date_start === 'none' || !date_start) {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        document.getElementById('date_start').value = formattedDate;
    }

    if (date_end === 'none' || !date_end) {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        document.getElementById('date_end').value = formattedDate;
    }

}
function getDateAndSendPost() {
    getDate();

    const date_start = document.getElementById('date_start').value;
    const date_end = document.getElementById('date_end').value;

    const formData = new FormData();
    formData.append('date_start', date_start);
    formData.append('date_end', date_end);

    fetch('/admin/orders/1', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data); // Обработайте полученные данные
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
}