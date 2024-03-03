# aio-connect-example-bot

Пример использования библиотеки [aio-connect](https://github.com/LilKirill00/aio-connect)

Для использования замените данные которые берутся из `config_reader.py` или настройте файл `.env` похожим образом:
```dotenv
# connect
API_LOGIN=__login__
API_PASSSWORD=__password__

SERVER_API="https://__server URL__"

# host
BASE_WEBHOOK_URL="http://__ip address__:8888"
WEBHOOK_PATH="/event/bot/"

# listen
WEB_SERVER_HOST="__ip address__"
WEB_SERVER_PORT=8888

# line
LINE_ID="__UUID линии на которой работает бот__"

# other data
SERVICE_REQUEST_CHANNEL_ID="__UUID Канала поступления__"
SERVICE_KIND_ID="__UUID Вида услуги__"
SERVICE_REQUEST_TYPE_ID="__UUID Вида работы__"
EXECUTOR_ID="__UUID выбраного специалиста по дефолту__"
```