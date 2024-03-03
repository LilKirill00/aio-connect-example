from aio_connect import Router, types, F
from aio_connect.fsm.context import FSMContext

from main_bot_1C_Connect import bot
from handlers.navigation_menu import show_main_menu, had_a_problem
from states_group.navigation import Navigation

import zeep
from zeep.transports import AsyncTransport
import httpx

router = Router()


@router.line(F.text == "Понятно", Navigation.on_register_of_application_finaly)
async def register_of_application_step2(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        await state.set_state(Navigation.on_main_menu)
        await show_main_menu(line, state)


@router.line(F.text == "Отмена", Navigation.on_register_of_application_step1)
async def register_of_application_cancel(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id, text="Регистрация заявки была отменена")
        await state.set_state(Navigation.on_had_a_problem)
        await had_a_problem(line, state)


@router.line(F.file, Navigation.on_register_of_application_step1)
async def another_problem(line: types.TypeLine):
    if line.user_id == line.author_id:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Это не сообщение."
                                         "\nОпишите подробно что случилось (одним сообщением), по нему будет "
                                         "зарегистрирована заявка. Отправка сообщения = переход на сл. шаг.",
                                    keyboard=[
                                        [{"text": "Отмена"}],
                                    ])


@router.line(F.text, Navigation.on_register_of_application_step1)
async def register_of_application_finaly(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        transport = AsyncTransport(client=httpx.AsyncClient(auth=(bot.api_login, bot.api_password)),
                                   wsdl_client=httpx.Client(auth=(bot.api_login, bot.api_password)))

        client = zeep.AsyncClient("https://tusdevelop.1c-connect.com/tusdevelop/ws/PartnerWebAPI2?wsdl",
                                  transport=transport)

        structure = client.get_type('ns0:Structure')

        from handlers.applications_function import ServiceRequestStatusID
        from config_reader import config
        params = structure(Property=[
            {'Value': config.SERVICE_REQUEST_CHANNEL_ID, 'name': "ServiceRequestChannelID"},
            {'Value': line.line_id, 'name': "ServiceLineKindID"},
            {'Value': config.SERVICE_KIND_ID, 'name': "ServiceKindID"},
            {'Value': config.SERVICE_REQUEST_TYPE_ID, 'name': "ServiceRequestTypeID"},
            {'Value': config.EXECUTOR_ID, 'name': "ExecutorID"},
            {'Value': ServiceRequestStatusID['Новая']['ServiceRequestStatusID'], 'name': "ServiceRequestStatusID"},
            {'Value': line.user_id, 'name': "UserID"},
            {'Value': line.text, 'name': "Description"},
            {'Value': "Возникла проблема.", 'name': "Summary"},
        ])

        response = await client.service.ServiceRequestAdd(Params=[params])

        if response[0]['Value'] == "SUCCESS":
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                        text="По вашей проблеме зарегистрирована заявка, вы сможете видеть ход ее "
                                             "рассмотрения в приложении. Кнопка “Понятно” = возврат в общее меню.",
                                        keyboard=[
                                            [{"text": "Понятно"}]
                                        ])
            await state.set_state(Navigation.on_register_of_application_finaly)
