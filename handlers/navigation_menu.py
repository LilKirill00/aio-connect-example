from aio_connect import Router, F
from aio_connect.filters import Command
from aio_connect.fsm.context import FSMContext
from aio_connect.types import TypeLine, Button

from main_bot_1C_Connect import bot
from states_group.navigation import Navigation


router = Router()


@router.line(Command("help", prefix="/"))  # /help
async def help_bot(line: TypeLine):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Здравствуйте!\nВас приветствует чат бот. Чтобы не возникали проблем рекомендую "
                                     "делать все по полученым инструкциям и вызывать только те команды которые "
                                     "доступны на клавиатуре :point_down:")


@router.line(F.text.lower() == "меню")
async def show_main_menu(line: TypeLine, state: FSMContext):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Здравствуйте!\n\nВыберите, что вас интересует :point_down:",
                                keyboard=[
                                    [Button(text="Возникла проблема")],
                                    [Button(text="Часто задаваемые вопросы")],
                                    [Button(text="Справочная информация")],
                                    [Button(text="Заявки")],
                                    [Button(text="Закрыть обращение")],
                                ])
    await state.set_state(Navigation.on_main_menu)


@router.line(F.text == "Возникла проблема", Navigation.on_main_menu)
async def had_a_problem(line: TypeLine, state: FSMContext):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Возможно ваша проблема нам уже известна, уточните что случилось:",
                                keyboard=[
                                    [{"text": "Не запускается 1С-Коннект"}],
                                    [{"text": "Не авторизуется. Статус “Не в сети”"}],
                                    [{"text": "Проблемы с удаленным доступом"}],
                                    [{"text": "Другая проблема"}],
                                    [{"text": "Перевести на специалиста"}],
                                    [{"text": "Назад"}],
                                ])
    await state.set_state(Navigation.on_had_a_problem)


@router.line(F.text == "Часто задаваемые вопросы", Navigation.on_main_menu)
async def faq(line: TypeLine, state: FSMContext):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Выберите, что вас интересует :point_down:",
                                keyboard=[
                                    [{"text": "Как скачать 1С-Коннект?"}],
                                    [{"text": "Как удалить историю переписки?"}],
                                    [{"text": "Как настроить SIP-клиент?"}],
                                    [{"text": "Удаленный доступ на Linux и macOS"}],
                                    [{"text": "Работа для 32-разрядных ОС"}],
                                    [{"text": "Интеграция с мессенджерами"}],
                                    [{"text": "Как удалить 1С-Коннект?"}],
                                    [{"text": "Назад"}],
                                ])
    await state.set_state(Navigation.on_faq)


@router.line(F.text == "Справочная информация", Navigation.on_main_menu)
async def background_information(line: TypeLine, state: FSMContext):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Выберите, что вас интересует :point_down:",
                                keyboard=[
                                    [{"text": "Технические требования"}],
                                    [{"text": "Используемые ресурсы в сети Интернет"}],
                                    [{"text": "Документация"}],
                                    [{"text": "Назад"}],
                                ])
    await state.set_state(Navigation.on_background_information)


@router.line(F.text == "Документация", Navigation.on_background_information)
async def documentation(line: TypeLine, state: FSMContext):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Полная документация о сервисе размещена здесь: "
                                     "https://1c-connect.atlassian.net/wiki/spaces/PUBLIC/pages/1373930296/1+-+.."
                                     "\nВы можете выбрать точнее по разделам.",
                                keyboard=[
                                    [{"text": "Руководство пользователя"}],
                                    [{"text": "Руководство администратора"}],
                                    [{"text": "API и интеграции"}],
                                    [{"text": "Управление базами знаний и чат бот"}],
                                    [{"text": "Назад"}],
                                ])
    await state.set_state(Navigation.on_documentation)


@router.line(F.text == "Заявки", Navigation.on_main_menu)
async def applications(line: TypeLine, state: FSMContext):
    await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                text="Выберите, что вас интересует :point_down:",
                                keyboard=[
                                    [Button(text="Создать заявку")],
                                    [Button(text="Получение информации о заявке")],
                                    [Button(text="Редактировать заявку")],
                                    [Button(text="Назад")],
                                ])
    await state.set_state(Navigation.on_applications)
