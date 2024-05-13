# aio-connect-example-bot

Пример использования пакета [aio-connect](https://github.com/LilKirill00/aio-connect)

## Использование
Для использования замените данные которые берутся из `config_reader.py` или настройте файл `.env` похожим образом:
```dotenv
# connect
API_LOGIN='your_login_here'  # Замените your_login_here на ваш логин API
API_PASSWORD='your_password_here'  # Замените your_password_here на ваш пароль API

SERVER_API='https://api_server_url_here'  # Замените api_server_url_here на URL сервера API

# host
BASE_WEBHOOK_URL='http://your_ip_address_here:8888'  # Замените your_ip_address_here на IP адрес host сервера
WEBHOOK_PATH='/event/bot/'  # Путь к webhook. Менять обычно не нужно.

# listen
WEB_SERVER_HOST='your_ip_address_here'  # Замените your_ip_address_here на IP адрес, по которому будет доступен веб-сервер
WEB_SERVER_PORT=8888  # Порт, который будет использоваться для веб-сервера. Менять обычно не нужно.

# line
LINE_ID='your_line_uuid_here'  # Замените your_line_uuid_here на UUID линии, на которой работает бот

# other data connect
# Замените следующие UUID заглушки на реальные значения с информацией о вашем сервисе.
SERVICE_REQUEST_CHANNEL_ID='uuid_of_service_request_channel'  # UUID канала поступления заявок по умолчанию.
SERVICE_KIND_ID='uuid_of_service_kind'  # UUID вида услуги по умолчанию.
SERVICE_REQUEST_TYPE_ID='uuid_of_service_request_type'  # UUID вида работы по умолчанию.
EXECUTOR_ID='uuid_of_default_executor'  # UUID исполнителя, назначаемого по умолчанию.
```