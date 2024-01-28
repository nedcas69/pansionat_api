let role = 'admin'
//<!--    let role = {{role}}-->
    var guestTypeInput = document.getElementById('guest_type');
    var tabelGroup = document.getElementById('tabel-group');
    guestTypeInput.addEventListener('change', function(event) {

<!--        if (this.value === "sebe") {-->

<!--            tabelGroup.style.display = 'block';-->
<!--        }else{-->
<!--            tabelGroup.style.display = 'none';-->
<!--            var tabel = document.getElementById('tabel');-->
<!--            tabel.value =0;-->
<!--        }-->
    });

    function submitForm() {
        // Получаем ссылку на форму
        var form = document.getElementById('new_order_form');

        // Получаем значения полей формы
        var dateStart = document.getElementById('date_starts').value;
        var dateEnd = document.getElementById('date_ends').value;
        var guestType = document.getElementById('guest_type').value;
        var tabel = document.getElementById('tabel').value;
        var fio = document.getElementById('fio').value;
        var tel = document.getElementById('tel').value;
        var roomNumber = document.getElementById('room_number').value;

        // Проверка значений полей перед отправкой
        if (!dateStart || !dateEnd || !guestType || !fio || !tel || !roomNumber) {
            alert('Пожалуйста, заполните все обязательные поля.');
            return;
        }


        // Создаем объект FormData для удобной отправки данных формы
        var formData = new FormData(form);
        formData.append('date_start', dateStart);
        formData.append('date_end', dateEnd);
        formData.append('guest_type', guestType);
        formData.append('tabel', tabel);
        formData.append('fio', fio);
        formData.append('tel', tel);
        formData.append('zxcasd2356', role);
        formData.append('room_number', roomNumber);

        // URL, куда отправлять данные формы
        var url = '/orders/admin';  // Замените на реальный URL

        // Опции запроса
        var options = {
            method: 'POST',
            body: formData,

        };

            // Отправка запроса с использованием fetch
            // ...

        // Отправка запроса с использованием fetch
        fetch(url, options)
            .then(response => {
                // Check if the response is successful (status code 2xx)
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                return response.json();
            })
            .then(data => {
            if (data.err != '0'){
                $('#new_order').modal('hide');
             }
             alert(data.message);
            })
            .catch(error => {
                // Обработка ошибок
                console.error('Error:', error);
                alert('Возникла ошибка!');
            });


    }



    const date_start = document.getElementById('date_starts');
    const date_end = document.getElementById('date_ends');

    const todaysDate = new Date();
    const year = todaysDate.getFullYear();
    const month = ("0" + (todaysDate.getMonth() + 1)).slice(-2);
    const day = ("0" + todaysDate.getDate()).slice(-2);
    const maxDate = (year +"-"+ month +"-"+ day);

    date_start.setAttribute('min', maxDate);
    date_end.setAttribute('min', maxDate);

    date_start.addEventListener('change', (e) => {
        date_end.setAttribute('min', e.currentTarget.value);
    })