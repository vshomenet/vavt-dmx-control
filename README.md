Управление световыми приборами по протоколу DMX-512 при помощи веб-интерфейса.
===
### Описание
Проект в разработке

### Системные требования
* Операционная система Debian или Ubuntu
* nginx
* Python3
* pip3
* git

### Python модули
* Flask 2.1.2 или выше
* Flask-WTF 1.0.1 или выше
* WTForms 3.0.1 или выше
* Jinja2 3.1.2 или выше
* Pyserial 3.5 или выше
* Dmx485 1.2.1 или выше
* Aiogram 2.22.2 или выше

### Установка
1. `apt install git`
2. `git clone https://github.com/vshomenet/vavt-dmx-control.git`
3. `cd vavt-dmx-control` 
4. `./install.sh`

###  Настройка Telegram-бота
1. Зарегистрировать бота через @BotFather и получить токен.
2. В веб-интерфейсе зайти в раздел "Telegram" и сохранить полученный токен.
3. После добавления токена, через 5-10 секунд в разделе "Обслуживание", убедиться в отсутствии ошибки "Service dmx-telegram not installed or removed".
4. Отправить команду /id боту и узнать свой ID или через раздел "Помощь" в боте.
5. В веб-интерфейсе в разделе "Telegram" добавить свой ID в раздел "Пользователи telegram-бота". Только добавленные пользователи имеют возможность управлять пресетами.

### API - примеры
* Получение информации от сервера
1. `curl -i http://my_domain/api/v1/dmx/all` - получить полную информацию о сервере
2. `curl -i http://my_domain/api/v1/dmx/all_preset` - получить список доступных пресетов
3. `curl -i http://my_domain/api/v1/dmx/device` - получить список всех устройств
* Вызов пресетов
1. `curl -i -H "Content-Type: application/json" -X POST -d '{"preset":"default"}' http://my_domain/api/v1/dmx` - загрузить пресет "default"
2. `curl -i -H "Content-Type: application/json" -X POST -d '{"preset":"Red"}' http://my_domain/api/v1/dmx` - загрузить пресет "Red"
