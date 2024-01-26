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
//async function fetchOrders() {
//        // Получение access_token из куки
//        const accessToken = getCookie('token');
//
//        if (!accessToken) {
//            // Если токен отсутствует, перенаправьте пользователя на страницу входа
//            window.location.href = '/login';
//            return;
//        }
//
//        const headers = new Headers({
//            'Authorization': `Bearer ${accessToken}`
//        });
//
//        try {
//            const response = await fetch('/admin/orders/1', { headers });
//
//            if (!response.ok) {
//                // Обработка ошибок, например, если токен истек или недействителен
//                console.error('Failed to fetch orders');
//                alert('Failed to fetch orders. Please log in again.');
//                // Перенаправьте пользователя на страницу входа
//                window.location.href = '/login';
//            }
//
//            // Обработка успешного ответа от сервера
//            const orders = await response.json();
//            console.log('Orders:', orders);
//
//        } catch (error) {
//            // Обработка других ошибок, например, сетевых проблем
//            console.error('Failed to fetch orders', error);
//            //alert('Failed to fetch orders. Please try again later.', error);
//        }
//    }
//
//    // Функция для извлечения значения из куки по имени
//    function getCookie(name) {
//        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
//        if (match) return match[2];
//    }
//
//    // Вызов функции для получения заказов
//    fetchOrders();