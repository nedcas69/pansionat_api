async function login() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const data = {
            username: username,
            password: password,
            grant_type: 'password',
            scope: 'offline_access'
        };

        try {
            const response = await fetch('/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const responseData = await response.json();
            const accessToken = responseData.access_token;

            // Сохранение токена в куки
            const expirationInSeconds = responseData.expires_in || 3600; // Или укажите свой срок действия
            const expirationTime = new Date(Date.now() + expirationInSeconds * 1000);
            document.cookie = `token=${accessToken}; expires=${expirationTime.toUTCString()}; path=/`;

            // Перенаправление на защищенную страницу
            window.location.href = '/admin/orders/';
        } catch (error) {
            console.error('Login failed', error);
            alert('Login failed. Check your credentials.');
        }
    }