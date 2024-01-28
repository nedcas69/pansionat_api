var zxcasd2356 = role

    var guestTypeInput = document.getElementById('guest_type');
    var tabelGroup = document.getElementById('tabel-group');
    guestTypeInput.addEventListener('change', function(event) {

        if (this.value === "sebe") {

            tabelGroup.style.display = 'block';
        }else{
            tabelGroup.style.display = 'none';
            var tabel = document.getElementById('tabel');
            tabel.value =0;
        }
    });

    var headers = new Headers();
    headers.append('Content-Type', 'application/json');
    // headers.append('Authorization', 'Bearer');

    function submitForm() {

        // Получаем ссылку на форму
        var form = document.getElementById('new_order_form');

        // Получаем значения полей формы
        var dateStart = document.getElementById('date_starts').value;
        var dateEnd = document.getElementById('date_ends').value;
        var guestType = document.getElementById('guest_type').value;
        var tabel = document.getElementById('tabel').value;
        var fio = document.getElementById('fio').value;
        var roomNumber = document.getElementById('room_number').value;

        // Проверка значений полей перед отправкой
//        if (!dateStart || !dateEnd || !guestType || !fio || !roomNumber) {
//            alert('Пожалуйста, заполните все обязательные поля.');
//            return;
//        }


        // Создаем объект с данными для отправки
        var jsonData = {
            date_start: dateStart,
            date_end: dateEnd,
            guest_type: guestType,
            tabel: tabel,
            fio: fio,
            room_number: roomNumber,
            room_id: 0,
            zxcasd2356: 'admin',
            tel: '',
            user_id: 0,
            room_class: '',
            work: false,
            paytype: '',
            pay_status: false,
            sebe_35: 0,
            pension_30: 0,
            semye_70: 0,
            commerc_100: 0,
            summa: 0,
        };

        // URL, куда отправлять данные формы
        var url = '/orders/admin';  // Замените на реальный URL

        // Опции запроса
        var options = {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(jsonData)

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
                // Получаем ссылку на модальное окно
                if(data.message=='true'){
                   $('#new_order').modal('hide');
                }
            })
            .catch(error => {
                // Обработка ошибок
                console.error('Error:', error);

            });


    }


    const date_start = document.getElementById('date_start');
    const date_end = document.getElementById('date_end');

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
