import datetime
import locale

from aio_connect import Router, F
from aio_connect.fsm.context import FSMContext
from aio_connect.types import TypeLine, Button
from aio_connect.exceptions import ConnectBadRequest, ConnectNotFound

from main_bot_1C_Connect import bot
from handlers.navigation_menu import applications
from states_group.navigation import Navigation

import zeep
from zeep.transports import AsyncTransport
import httpx

service_request_status_list = []  # Список статусов
service_kind_list = []  # Список услуг
service_request_type_list = []  # Список видов работ

ServiceRequestStatusID = {}


async def set_application_info_lists() -> None:
    transport = AsyncTransport(client=httpx.AsyncClient(auth=(bot.api_login, bot.api_password)),
                               wsdl_client=httpx.Client(auth=(bot.api_login, bot.api_password)))

    client = zeep.AsyncClient("https://tusdevelop.1c-connect.com/tusdevelop/ws/PartnerWebAPI2?wsdl",
                              transport=transport)
    # Получаем и переоформляем список услуг
    service_kind = await client.service.ServiceKindRead(Params=[])
    service_kind = service_kind[1]['Value']
    column_name = [value['Name'] for value in service_kind['column']]
    for value in service_kind['row']:
        row = {}
        for _id in range(0, len(column_name)):
            row.update({column_name[_id]: value['Value'][_id]})
        service_kind_list.append(row)
    # Получаем и переоформляем список видов работ
    service_request_type = await client.service.ServiceRequestTypeRead(Params=[])
    service_request_type = service_request_type[1]['Value']
    column_name = [value['Name'] for value in service_request_type['column']]
    for value in service_request_type['row']:
        row = {}
        for _id in range(0, len(column_name)):
            row.update({column_name[_id]: value['Value'][_id]})
        service_request_type_list.append(row)
    # Получаем и переоформляем список статусов
    service_request_status = await client.service.ServiceRequestStatusRead(Params=[])
    service_request_status = service_request_status[1]['Value']
    column_name = [value['Name'] for value in service_request_status['column']]
    for value in service_request_status['row']:
        row = {}
        for _id in range(0, len(column_name)):
            row.update({column_name[_id]: value['Value'][_id]})
        service_request_status_list.append(row)
    # Переоформляем список статусов для удобного взаимодействия
    for value in service_request_status_list:
        if not value['Deleted']:
            ServiceRequestStatusID.update({value['Name']: value})

    # print(service_kind_list)
    # print(service_request_type_list)
    # print(service_request_status_list)
    # print(ServiceRequestStatusID)


router = Router()


async def do_create_application(line: TypeLine, state: FSMContext) -> None:
    ticket = (await state.get_data())['ticket']
    transport = AsyncTransport(client=httpx.AsyncClient(auth=(bot.api_login, bot.api_password)),
                               wsdl_client=httpx.Client(auth=(bot.api_login, bot.api_password)))

    client = zeep.AsyncClient("https://tusdevelop.1c-connect.com/tusdevelop/ws/PartnerWebAPI2?wsdl",
                              transport=transport)

    structure = client.get_type('ns0:Structure')
    from config_reader import config
    params = structure(Property=[
        {'Value': config.SERVICE_REQUEST_CHANNEL_ID, 'name': "ServiceRequestChannelID"},
        {'Value': line.line_id, 'name': "ServiceLineKindID"},
        {'Value': line.user_id, 'name': "UserID"},
        {'Value': config.EXECUTOR_ID, 'name': "ExecutorID"},
        {'Value': ticket['summary'], 'name': "Summary"},
        {'Value': ticket['description'], 'name': "Description"},
        {'Value': ServiceRequestStatusID['Новая']['ServiceRequestStatusID'], 'name': "ServiceRequestStatusID"},
        {'Value': ticket['kind']['id'], 'name': "ServiceKindID"},
        {'Value': ticket['type']['id'], 'name': "ServiceRequestTypeID"},
    ])
    response = await client.service.ServiceRequestAdd(Params=[params])
    if response[0]['Value'] == "SUCCESS":
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="По вашим данным зарегистрирована заявка, вы сможете видеть ход ее "
                                         "рассмотрения в приложении. Кнопка “Понятно” = возврат в меню.",
                                    keyboard=[
                                        [{"text": "Понятно"}]
                                    ])
        await state.set_state(Navigation.on_applications)
    else:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text="Ошибка сохранения изменений")
    await state.update_data(ticket={})


@router.line(F.text == "Создать заявку", Navigation.on_applications)
async def create_application(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Шаг 1/5\nВведите название темы заявки. ",
                                    keyboard=[[Button(text="Отмена")]]
                                    )
        await state.set_state(Navigation.on_create_application_step1)
        await state.update_data(ticket={})


@router.line(F.text == "Отмена", Navigation.on_create_application_step1)
@router.line(F.text == "Отмена", Navigation.on_create_application_step2)
@router.line(F.text == "Отмена", Navigation.on_create_application_step3)
@router.line(F.text == "Отмена", Navigation.on_create_application_step4)
@router.line(F.text == "Отмена", Navigation.on_create_application_step5)
async def stop_create_application(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await state.update_data(ticket={})
        await applications(line, state)


@router.line(F.text, Navigation.on_create_application_step1)
async def create_application_step1(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        data = await state.get_data()
        data['ticket']['summary'] = line.text
        await state.set_data(data)
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Шаг 2/5\nВведите описание заявки. ",
                                    keyboard=[[Button(text="Отмена")]]
                                    )
        await state.set_state(Navigation.on_create_application_step2)


@router.line(F.text, Navigation.on_create_application_step2)
async def create_application_step2(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        data = await state.get_data()
        data['ticket']['description'] = line.text
        await state.set_data(data)
        send_text = "Шаг 3/5\nВыберите услугу из списка"
        keyboard = [[Button(text="Отмена")]]
        for service_kind in service_kind_list:
            if not service_kind['Deleted']:
                for value in range(0, len(service_kind['ServiceLineKinds']['row'])):
                    if service_kind['ServiceLineKinds']['row'][value]['Value'][0] == line.line_id:
                        keyboard.append([Button(text=service_kind['Name'])])
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text, keyboard=keyboard)
        await state.set_state(Navigation.on_create_application_step3)


@router.line(F.text, Navigation.on_create_application_step3)
async def create_application_step3(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        for service_kind in service_kind_list:
            if not service_kind['Deleted']:
                if service_kind['Name'] == line.text:
                    data = await state.get_data()
                    data['ticket']['kind'] = {'id': service_kind['ServiceKindID'],
                                              'name': service_kind['Name']}
                    await state.set_data(data)
                    ticket = (await state.get_data())['ticket']
                    send_text = "Шаг 4/5\nВыберите вид работы из списка"
                    keyboard = [[Button(text="Отмена")]]
                    for service_request_type in service_request_type_list:
                        if not service_request_type['Deleted']:
                            for value in range(0, len(service_request_type['ServiceKinds']['row'])):
                                if service_request_type['ServiceKinds']['row'][value]['Value'][0] ==\
                                        ticket['kind']['id']:
                                    keyboard.append([Button(text=service_request_type['Name'])])
                    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text,
                                                keyboard=keyboard)
                    await state.set_state(Navigation.on_create_application_step4)
                    return
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text='Нет такой услуги. Выберите доступные варианты')


@router.line(F.text, Navigation.on_create_application_step4)
async def create_application_step4(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        for service_request_type in service_request_type_list:
            if not service_request_type['Deleted']:
                if service_request_type['Name'] == line.text:
                    data = await state.get_data()
                    data['ticket']['type'] = {'id': service_request_type['ServiceRequestTypeID'],
                                              'name': service_request_type['Name']}
                    await state.set_data(data)
                    ticket = (await state.get_data())['ticket']
                    await bot.send_message_line(
                        line_id=line.line_id, user_id=line.user_id,
                        text=("Шаг 5/5\nПредпросмотр заявки:\n"
                              f"Тема: {ticket['summary']}\n"
                              f"Описание: {ticket['description']}\n"
                              f"Услуга: {ticket['kind']['name']}\n"
                              f"Вид работ: {ticket['type']['name']}\n"),
                        keyboard=[[Button(text="Отмена"), Button(text="Зарегистрировать")]])
                    await state.set_state(Navigation.on_create_application_step5)
                    return
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text='Нет такого вида работ. Выберите доступные варианты')


@router.line(F.text, Navigation.on_create_application_step5)
async def create_application_step5(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        send_text = "Не понимаю, выберите доступные варианты"
        if line.text == "Зарегистрировать":
            await do_create_application(line, state)
            return
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text.in_(["Получение информации о заявке", "Повторить"]), Navigation.on_applications)
async def get_application_info_start(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Введите номер заявки по которой хотите получить информацию",
                                    keyboard=[[Button(text="Отмена")]])
        await state.set_state(Navigation.on_get_application_info)


@router.line(F.text == "Понятно", Navigation.on_applications)
@router.line(F.text == "Отменить редактирование", Navigation.on_edit_application_step1)
async def get_application_info_go_back(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await applications(line, state)


def dateformat(date: str) -> datetime:
    # Преобразует дату из формата 2024-02-21T14:54:28Z в формат 21 февраля 2024 14:54:28
    locale.setlocale(locale.LC_TIME, 'ru_RU')
    return datetime.datetime.fromisoformat(date.replace('Z', '+00:00')).strftime('%d %B %Y %H:%M:%S')


async def get_ticket(line: TypeLine, state: FSMContext) -> bool:
    # Функция ищет заявку по номеру. Если все нормально сохранит в state тикет,
    # иначе будет выводить различные ошибки пользователю
    try:
        if line.text.isdigit():
            ticket = await bot.get_ticket_by_number(int(line.text))
            if ticket['initiator']['user_id'] == line.user_id:
                await state.update_data(ticket=ticket)
                return True
            else:
                await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                            text="Ошибка: Заявка принадлежит другому пользователю."
                                                 "\nПовторите попытку",
                                            keyboard=[[Button(text="Отмена")]])
        else:
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                        text="Ошибка: Номер заявки не число.\nПовторите попытку",
                                        keyboard=[[Button(text="Отмена")]])
    except ConnectBadRequest:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Ошибка: Номер заявки превышает лимит символов.\nПовторите попытку",
                                    keyboard=[[Button(text="Отмена")]])
    except ConnectNotFound:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Ошибка: Заявка по данному номеру не найдена.\nПовторите попытку",
                                    keyboard=[[Button(text="Отмена")]])


@router.line(F.text, Navigation.on_get_application_info)
async def get_application_info(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        if line.text == "Отмена":
            await state.set_state(Navigation.on_applications)
            await applications(line, state)
            return
        if await get_ticket(line, state):
            ticket = (await state.get_data())['ticket']
            await bot.send_message_line(
                line_id=line.line_id, user_id=line.user_id,
                text=(f"Заявка № {ticket['number']} от {dateformat(ticket['created_at'])}\n"
                      f"Дата последнего изменения: {dateformat(ticket['updated_at'])}\n"
                      f"Тема: {ticket['summary']}\n"
                      f"Описание: {ticket['description']}\n"
                      f"Статус: {ticket['status']['name']}\n"
                      f"Услуга: {ticket['kind']['name']}\n"
                      f"Вид работ: {ticket['type']['name']}\n"
                      f"Результат: {ticket['result'] if 'result' in ticket else ''}\n"),
                keyboard=[[Button(text="Повторить"), Button(text="Понятно")]])
            await state.set_state(Navigation.on_applications)


@router.line(F.text == "Редактировать заявку", Navigation.on_applications)
async def edit_application_start(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Введите номер заявки информацию о которой хотите отредактировать",
                                    keyboard=[[Button(text="Отмена")]])
        await state.set_state(Navigation.on_edit_application)


@router.line(F.text, Navigation.on_edit_application)
async def edit_application(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        if line.text == "Отмена":
            await state.set_state(Navigation.on_applications)
            await applications(line, state)
            return
        if await get_ticket(line, state):
            ticket = (await state.get_data())['ticket']
            text = (f"Заявка № {ticket['number']} от {dateformat(ticket['created_at'])}\n"
                    f"Дата последнего изменения: {dateformat(ticket['updated_at'])}\n"
                    f"Тема: {ticket['summary']}\n"
                    f"Описание: {ticket['description']}\n"
                    f"Статус: {ticket['status']['name']}\n"
                    f"Услуга: {ticket['kind']['name']}\n"
                    f"Вид работ: {ticket['type']['name']}\n"
                    f"Результат: {ticket['result'] if 'result' in ticket else ''}\n")
            if ticket['status']['type'] not in ('FINISHED', 'CANCELLED'):
                await bot.send_message_line(
                    line_id=line.line_id, user_id=line.user_id,
                    text=text + "\nВыберите что хотите отредактировать :point_down:\n",
                    keyboard=[
                        [Button(text="Отменить редактирование")],
                        [Button(text="Изменить тему")],
                        [Button(text="Изменить описание")],
                        [Button(text="Изменить вид услуги")],
                        [Button(text="Изменить вид работы")],
                        [Button(text="Отменить заявку")],
                    ])
                await state.update_data(ticket_update={})
                await state.set_state(Navigation.on_edit_application_step1)
            else:
                await bot.send_message_line(
                    line_id=line.line_id, user_id=line.user_id,
                    text=text + "\nДля данного статуса недоступно редактирование\n",
                    keyboard=[[Button(text="Понятно")]])
                await state.set_state(Navigation.on_applications)


async def save_edit_application(line: TypeLine, state: FSMContext) -> None:
    ticket = (await state.get_data())['ticket']
    ticket_update = (await state.get_data())['ticket_update']
    transport = AsyncTransport(client=httpx.AsyncClient(auth=(bot.api_login, bot.api_password)),
                               wsdl_client=httpx.Client(auth=(bot.api_login, bot.api_password)))

    client = zeep.AsyncClient("https://tusdevelop.1c-connect.com/tusdevelop/ws/PartnerWebAPI2?wsdl",
                              transport=transport)

    structure = client.get_type('ns0:Structure')
    params = [{'Value': ticket['id'], 'name': "ServiceRequestID"}]
    if 'summary' in ticket_update:
        params.append({'Value': ticket_update['summary'], 'name': "Summary"})
    if 'description' in ticket_update:
        params.append({'Value': ticket_update['description'], 'name': "Description"})
    if 'status' in ticket_update:
        params.append({'Value': ticket_update['status']['id'], 'name': "ServiceRequestStatusID"})
    params = structure(Property=params)
    response = await client.service.ServiceRequestEdit(Params=[params])
    send_message = ""
    if 'kind' in ticket_update:
        send_message += f"Запрос изменения услуги на: {ticket_update['kind']['name']}\n"
    if 'type' in ticket_update:
        send_message += f"Запрос изменения вида работы на: {ticket_update['type']['name']}\n"
    if 'add_message_status' in ticket_update:
        send_message += f"Сообщение по поводу отмены заявки: {ticket_update['add_message_status']}\n"
    if send_message != "":
        response_message = await client.service.ServiceRequestSendTextMessage(
            ServiceRequestID=ticket['id'],
            AuthorID=line.user_id,
            Message=send_message,
        )
        if response_message[0]['Value'] == "SUCCESS":
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text="Сообщение отправлено\n")
        else:
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text="Ошибка отправки сообщения\n")
    if response[0]['Value'] == "SUCCESS":
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text="Изменения в заявке сохранены\n",
                                    keyboard=[[Button(text="Понятно")]])
        await state.set_state(Navigation.on_applications)
    else:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text="Ошибка сохранения изменений\n")


@router.line(F.text, Navigation.on_edit_application_step1)
async def edit_application_step1(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        ticket = (await state.get_data())['ticket']
        send_text = "Не понимаю, выберите доступные варианты"
        keyboard = []

        if line.text == 'Сохранить':
            await save_edit_application(line, state)
            return

        if line.text == "Изменить тему":
            send_text = f"Текущая тема: {ticket['summary']}\nВведите новое название темы"
            keyboard = [[Button(text="Назад")]]
            await state.set_state(Navigation.on_edit_application_step2_summary)

        if line.text == "Изменить описание":
            send_text = f"Текущее описание: {ticket['description']}\nВведите новое описание"
            keyboard = [[Button(text="Назад")]]
            await state.set_state(Navigation.on_edit_application_step2_description)

        if line.text == "Изменить вид услуги":
            send_text = f"Текущий вид услуги: {ticket['kind']['name']}\nВы не можете изменить услугу самостоятельно, " \
                        f"но можете отправить сообщение выбрав услугу из списка"
            keyboard = [[Button(text="Назад")]]
            for service_kind in service_kind_list:
                if not service_kind['Deleted']:
                    for value in range(0, len(service_kind['ServiceLineKinds']['row'])):
                        if service_kind['ServiceLineKinds']['row'][value]['Value'][0] == line.line_id:
                            # print(service_kind['ServiceKindID'], service_kind['Name'])
                            # print(service_kind['ServiceLineKinds']['row'][value]['Value'][0])
                            keyboard.append([Button(text=service_kind['Name'])])
            await state.set_state(Navigation.on_edit_application_step2_kind)

        if line.text == "Изменить вид работы":
            send_text = f"Текущий вид работы: {ticket['type']['name']}\nВы не можете изменить вид работы " \
                        f"самостоятельно, но можете отправить сообщение выбрав вид работы из списка"
            keyboard = [[Button(text="Назад")]]
            for service_request_type in service_request_type_list:
                if not service_request_type['Deleted']:
                    for value in range(0, len(service_request_type['ServiceKinds']['row'])):
                        if service_request_type['ServiceKinds']['row'][value]['Value'][0] == ticket['kind']['id']:
                            # print(service_request_type['ServiceRequestTypeID'], service_request_type['Name'])
                            # print(service_request_type['ServiceKinds']['row'][value]['Value'][0])
                            keyboard.append([Button(text=service_request_type['Name'])])
            await state.set_state(Navigation.on_edit_application_step2_type)

        if line.text == "Отменить заявку":
            keyboard = [[Button(text="Назад")]]
            if ticket['status']['type'] == 'NEW' and ticket['status']['name'] == "Новая":
                send_text = f"Текущий статус: {ticket['status']['name']}\nПодтвердите отмену заявки"
                keyboard.append([Button(text="Подтвердить")])
                await state.set_state(Navigation.on_edit_application_step2_cancel_status)
            else:
                send_text = f"Текущий статус: {ticket['status']['name']}\nДля данного статуса нельзя отменить заявку " \
                            f"самостоятельно, обратитесь к специалисту через заявку"
                keyboard.append([Button(text="Написать сообщение в заявке")])
                await state.set_state(Navigation.on_edit_application_step2_add_message)

        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text, keyboard=keyboard)


@router.line(F.text == "Назад", Navigation.on_edit_application_step2_summary)
@router.line(F.text == "Назад", Navigation.on_edit_application_step2_description)
@router.line(F.text == "Назад", Navigation.on_edit_application_step2_kind)
@router.line(F.text == "Назад", Navigation.on_edit_application_step2_type)
@router.line(F.text == "Назад", Navigation.on_edit_application_step2_cancel_status)
@router.line(F.text == "Назад", Navigation.on_edit_application_step2_add_message)
@router.line(F.text == "Назад", Navigation.on_edit_application_step3_add_message)
async def edit_application_go_back(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        ticket = (await state.get_data())['ticket']
        text = (f"Заявка № {ticket['number']} от {dateformat(ticket['created_at'])}\n"
                f"Дата последнего изменения: {dateformat(ticket['updated_at'])}\n"
                f"Тема: {ticket['summary']}\n"
                f"Описание: {ticket['description']}\n"
                f"Статус: {ticket['status']['name']}\n"
                f"Услуга: {ticket['kind']['name']}\n"
                f"Вид работ: {ticket['type']['name']}\n"
                f"Результат: {ticket['result'] if 'result' in ticket else ''}\n")
        keyboard = [[Button(text="Отменить редактирование")]]
        if 'ticket_update' in await state.get_data():
            ticket_update = (await state.get_data())['ticket_update']
            if ticket_update:
                text += "\nОбновляемые данные:\n"
                keyboard.append([Button(text="Сохранить")])
            if 'summary' in ticket_update:
                text += f"Тема: {ticket_update['summary']}\n"
            if 'description' in ticket_update:
                text += f"Описание: {ticket_update['description']}\n"
            if 'status' in ticket_update:
                text += f"Статус: {ticket_update['status']['name']}\n"
            if 'kind' in ticket_update:
                text += f"Услуга: {ticket_update['kind']['name']}\n"
            if 'type' in ticket_update:
                text += f"Вид работ: {ticket_update['type']['name']}\n"
            if 'add_message_status' in ticket_update:
                text += f"Отправляемое сообщение: {ticket_update['add_message_status']}\n"

        text += "\nВыберите что хотите отредактировать :point_down:\n"
        keyboard.extend((
            [Button(text="Изменить тему")],
            [Button(text="Изменить описание")],
            [Button(text="Изменить вид услуги")],
            [Button(text="Изменить вид работы")],
            [Button(text="Отменить заявку")],
        ))
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=text, keyboard=keyboard)
        await state.set_state(Navigation.on_edit_application_step1)


@router.line(F.text, Navigation.on_edit_application_step2_summary)
async def on_edit_application_step2_summary(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        data = await state.get_data()
        data['ticket_update']['summary'] = line.text
        await state.set_data(data)
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Готово')
        await edit_application_go_back(line, state)


@router.line(F.text, Navigation.on_edit_application_step2_description)
async def on_edit_application_step2_description(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        data = await state.get_data()
        data['ticket_update']['description'] = line.text
        await state.set_data(data)
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Готово')
        await edit_application_go_back(line, state)


@router.line(F.text, Navigation.on_edit_application_step2_kind)
async def on_edit_application_step2_kind(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        for service_kind in service_kind_list:
            if not service_kind['Deleted']:
                if service_kind['Name'] == line.text:
                    data = await state.get_data()
                    ticket = data['ticket']
                    data['ticket_update']['kind'] = {'id': service_kind['ServiceKindID'],
                                                     'name': service_kind['Name']}
                    await state.set_data(data)
                    if ticket['kind']['id'] == data['ticket_update']['kind']['id']:
                        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Готово')
                        await edit_application_go_back(line, state)
                    else:
                        send_text = f"У выбранного вида услуги отличаются доступные виды работ.\n" \
                                    f"Текущий вид работы: {ticket['type']['name']}\nВыберите вид работы из списка"
                        keyboard = [[Button(text="Назад")]]
                        for service_request_type in service_request_type_list:
                            if not service_request_type['Deleted']:
                                for value in range(0, len(service_request_type['ServiceKinds']['row'])):
                                    if service_request_type['ServiceKinds']['row'][value]['Value'][0] ==\
                                            ticket['kind']['id']:
                                        keyboard.append([Button(text=service_request_type['Name'])])
                        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text,
                                                    keyboard=keyboard)
                        await state.set_state(Navigation.on_edit_application_step2_type_after_kind)
                    return
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Нет такой услуги. '
                                                                                     'Выберите доступные варианты')


@router.line(F.text == "Назад", Navigation.on_edit_application_step2_type_after_kind)
async def on_edit_application_step2_type_after_kind(line: TypeLine, state: FSMContext) -> None:
    data = await state.get_data()
    data['ticket_update'].pop('kind')
    await state.set_data(data)
    await edit_application_go_back(line, state)


@router.line(F.text, Navigation.on_edit_application_step2_type)
@router.line(F.text, Navigation.on_edit_application_step2_type_after_kind)
async def on_edit_application_step2_type(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        for service_request_type in service_request_type_list:
            if not service_request_type['Deleted']:
                if service_request_type['Name'] == line.text:
                    data = await state.get_data()
                    data['ticket_update']['type'] = {'id': service_request_type['ServiceRequestTypeID'],
                                                     'name': service_request_type['Name']}
                    await state.set_data(data)
                    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Готово')
                    await edit_application_go_back(line, state)
                    return
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Нет такого вида работ. '
                                                                                     'Выберите доступные варианты')


@router.line(F.text == 'Подтвердить', Navigation.on_edit_application_step2_cancel_status)
async def on_edit_application_step2_cancel_status(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        data = await state.get_data()
        if data['ticket']['status']['type'] == 'NEW':
            data['ticket_update']['status'] = {'id': ServiceRequestStatusID['Отменена']['ServiceRequestStatusID'],
                                               'name': ServiceRequestStatusID['Отменена']['Name'],
                                               'type': ServiceRequestStatusID['Отменена']['ServiceRequestStatusIType']}
            await state.set_data(data)
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Готово')
            await edit_application_go_back(line, state)
        else:
            send_text = "Не понимаю, выберите доступные варианты"
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text)


@router.line(F.text == "Написать сообщение в заявке", Navigation.on_edit_application_step2_add_message)
async def on_edit_application_step2_add_message(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        send_text = "Введите сообщение которое хотите отправить в заявку"
        keyboard = [[Button(text="Назад")]]
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text=send_text, keyboard=keyboard)
        await state.set_state(Navigation.on_edit_application_step3_add_message)


@router.line(F.text, Navigation.on_edit_application_step3_add_message)
async def on_edit_application_step3_add_message(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        data = await state.get_data()
        data['ticket_update']['add_message_status'] = line.text
        await state.set_data(data)
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text='Готово')
        await edit_application_go_back(line, state)
