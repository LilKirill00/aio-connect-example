import random

from aio_connect import Router, types, F
from aio_connect.fsm.context import FSMContext
from aio_connect.fsm.state import default_state
from aio_connect.exceptions import UnprocessalbleEntity
from aio_connect.types import FSInputFile

from main_bot_1C_Connect import bot
from handlers.navigation_menu import show_main_menu
from states_group.navigation import Navigation

router = Router()


@router.line(F.text, Navigation.on_main_menu)
async def response_to_main_menu(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text, Navigation.on_had_a_problem)
async def response_to_had_a_problem(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        send_file = False
        if line.text == "Не запускается 1С-Коннект":
            send_text = "Возможно в процессах появилось несколько процессов 1с-connect.exe. Попробуйте завершить их " \
                        "через диспетчер задач и запустите приложение заново. Так же программа должна быть добавлена " \
                        "в исключения средств активной безопасности (брандмауэр, файервол, антивирус) - это один из " \
                        "пунктов наших тех. требований " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1410761448/1.3.."
        if line.text == "Не авторизуется. Статус “Не в сети”":
            send_text = "Убедитесь, что приложение добавлено в исключения средств активной безопасности (брандмауэр, " \
                        "файервол, антивирус), согласно тех. требованиям и в на компьютере доступны хосты из списка: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1317568520/1.3.1.."
        if line.text == "Проблемы с удаленным доступом":
            send_text = "1. Проверьте добавлены ли в исключения средств активной безопасности (брандмауэр, " \
                        "файервол, антивирус) файлы rutview.exe, rutserv.exe, rfusclient.exe, " \
                        "по пути %USERPROFILE%\\AppData\\Local\\Programs\\1C-Connect Desktop\\app\\bin\\rda и " \
                        "компоненты службы удаленного доступа C:\\Program Files\\1C-Connect\\Services\\Remote." \
                        "\n2. Если в настройках приложения (в разделе “Удаленный доступ”) написано “Отсутствуют " \
                        "компоненты удаленного доступа” - распакуйте файлы из этого архива и перенесите их в каталог " \
                        "rda по адресу: “%USERPROFILE%\\AppData\\Local\\Programs\\Connect Desktop\\app\\bin”. "
            send_file = True

        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)
        if send_file:
            await bot.send_file_line(line_id=line.line_id, user_id=line.user_id,
                                     file_name="Файл архив с компонентами УД.zip",
                                     file=FSInputFile("./uploads/Файл архив с компонентами УД.zip"))


@router.line(F.text, Navigation.on_faq)
async def response_to_faq(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        if line.text == "Как скачать 1С-Коннект?":
            send_text = "Скачать 1С-Коннект можно здесь: https://1c-connect.com/ru/download/.."
        if line.text == "Как удалить историю переписки?":
            send_text = "В чате редактирование отправленных сообщений доступно в течение 10 минут после отправки. " \
                        "Кликните правой кнопкой мыши по сообщению, выберите пункт меню ”Изменить”. Отредактируйте " \
                        "или удалите сообщение. После редактирования в чате появится информация, что сообщение " \
                        "изменено. Полностью очистить переписку в чате нельзя."
        if line.text == "Как настроить SIP-клиент?":
            send_text = "*“*На текущий момент интеграция с внешними АТС (SIP-клиент) отложена в связи с другими " \
                        "приоритетами. Сроки рассмотрения пока не определены.”"
        if line.text == "Удаленный доступ на Linux и macOS":
            send_text = "“Удаленные подключения на операционных системах, отличных от Windows сейчас в разработке. " \
                        "Ожидайте.”"
        if line.text == "Работа для 32-разрядных ОС":
            send_text = "“В настоящее время не гарантируем работу на 32-х разрядных операционных системах. Так как " \
                        "аудитория таких пользователей менее 1%, поддержка не планируется из-за ее " \
                        "нецелесообразности. Рекомендуем организовать работу по переводу пользователей на более " \
                        "современные операционные системы.”"
        if line.text == "Интеграция с мессенджерами":
            send_text = "“Интеграция с Telegram в разработке, ожидайте. С остальными мессенджерами и соцсетями " \
                        "прорабатывается. Сроки пока не определены.”"
        if line.text == "Как удалить 1С-Коннект?":
            send_text = "Приложение 1С-Коннект удаляется стандартно через “Установку и удаление программ“."

        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text, Navigation.on_background_information)
async def response_to_background_information(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        if line.text == "Технические требования":
            send_text = "Технические требования размещены здесь: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1410761448/1.3.."
        if line.text == "Используемые ресурсы в сети Интернет":
            send_text = "Список ресурсов, которые сервис использует в сети Интернет, размещен здесь: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1317568520/1.3.1.."

        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text, Navigation.on_documentation)
async def response_to_documentation(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        if line.text == "Руководство пользователя":
            send_text = "Установка и запуск приложения 1С-Коннект: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383841315/3.1.+1+-.." \
                        "\nНастройка профиля пользователя: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383841474/3.2.." \
                        "\nРаздел “Линии“: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383841523/3.3.." \
                        "\nРаздел “Клиенты“: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383841670/3.4.." \
                        "\nРаздел “Заявки“: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383841962/3.5.." \
                        "\nРаздел “Коллеги“: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383842138/3.6.." \
                        "\nРаздел “Главная“: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383842325/3.7.." \
                        "\nНастройки приложения: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383842352/3.8.." \
                        "\nУдаленный доступ: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1420037711/3.9.."

        if line.text == "Руководство администратора":
            send_text = "Доступ в кабинет администратора: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383839512/2.1.." \
                        "\nУправление сотрудниками: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383839784/2.2.." \
                        "\nУправление линиями: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383839923/2.3.." \
                        "\nУправление клиентами: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383840518/2.4.." \
                        "\nЗаявки на обслуживание (тикеты): " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383840747/2.5.." \
                        "\nОнлайн-монитор: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383840921/2.6.+-.." \
                        "\nРассылки: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383840985/2.7.." \
                        "\nОтчеты: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/2383841250/2.9.."

        if line.text == "API и интеграции":
            send_text = "API серверов: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/975241472/4.1.+API+1+-." \
                        "\nТрансляция событий: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1349877768/4.2.." \
                        "\nЦифровое меню: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1355939922/4.3.."

        if line.text == "Управление базами знаний и чат бот":
            send_text = "Описание механизма работы с базами знаний размещено здесь: " \
                        "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/975536205/2.8.+-.."

        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text, Navigation.on_applications)
async def response_to_applications(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"

        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text, default_state)
@router.line(F.file, default_state)
async def response_to_question(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        try:
            answer = await bot.question_and_answering(line_id=line.line_id, user_id=line.user_id, skip_goodbyes=False,
                                                      skip_greetings=False)
            if "answers" in answer and answer["answers"]:
                await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                            text=random.choice(answer["answers"])["text"],
                                            keyboard=[[{'text': "Меню"}]])
            else:
                await show_main_menu(line, state)
        except UnprocessalbleEntity:
            await show_main_menu(line, state)


@router.line(F.text)
@router.line(F.file)
async def response_to_not_find(line: types.TypeLine):
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)
