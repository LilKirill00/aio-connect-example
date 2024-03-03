from aio_connect import Router, types, F
from aio_connect.fsm.context import FSMContext

from main_bot_1C_Connect import bot
from handlers.navigation_menu import show_main_menu, background_information
from states_group.navigation import Navigation


router = Router()


@router.line(F.text == "Другая проблема", Navigation.on_had_a_problem)
async def another_problem(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                    text="Опишите подробно что случилось (одним сообщением), по нему будет "
                                         "зарегистрирована заявка. Отправка сообщения = переход на сл. шаг.",
                                    keyboard=[
                                        [{"text": "Отмена"}],
                                    ])
        await state.set_state(Navigation.on_register_of_application_step1)


@router.line(F.text == "Перевести на специалиста", Navigation.on_had_a_problem)
async def transfer_to_specialist(line: types.TypeLine):
    if line.user_id == line.author_id:
        tariff = True
        if tariff:
            await bot.appoint_start(line_id=line.line_id, user_id=line.user_id)
        else:
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                        text="Ваш тариф не предполагает консультирование с помощью специалистов. "
                                             "Расширьте тариф для связи со специалистами техподдержки.")


@router.line(F.text == "Закрыть обращение", Navigation.on_main_menu)
@router.line(F.message_type.in_({82, 90, 91, 92, 93}))
async def close_treatment(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        if await bot.get_treatments(line_id=line.line_id, user_id=line.user_id):
            await bot.drop_treatment(line_id=line.line_id, user_id=line.user_id)
        await state.clear()


@router.line(F.text == "Назад", Navigation.on_had_a_problem)
@router.line(F.text == "Назад", Navigation.on_faq)
@router.line(F.text == "Назад", Navigation.on_background_information)
@router.line(F.text == "Назад", Navigation.on_applications)
@router.line(F.text == "Назад", Navigation.on_documentation)
async def go_back(line: types.TypeLine, state: FSMContext):
    if line.user_id == line.author_id:
        menu_state = await state.get_state()
        if menu_state in (Navigation.on_had_a_problem, Navigation.on_faq, Navigation.on_background_information,
                          Navigation.on_applications):
            await show_main_menu(line, state)
        if menu_state == Navigation.on_documentation:
            await background_information(line, state)
