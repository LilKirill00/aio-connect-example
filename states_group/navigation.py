from aio_connect.fsm.state import StatesGroup, State


class Navigation(StatesGroup):
    # 0 - уровень меню
    on_main_menu = State()  # Меню
    # 1 - уровень меню
    on_had_a_problem = State()  # Меню - Возникла проблема
    on_faq = State()  # Меню - Часто задаваемые вопросы
    on_background_information = State()  # Меню - Справочная информация
    on_applications = State()  # Меню - Заявки
    # 2 - уровень меню
    on_documentation = State()  # Меню - Справочная информация - Документация
    # регистрация заявки в Другая проблема
    on_register_of_application = State()  # Меню - Возникла проблема - Другая проблема
    on_register_of_application_step1 = State()  # Получение описания
    on_register_of_application_finaly = State()  # Регистрация
    # Функии заявки
    on_get_application_info = State()  # Получение информации по номеру заявки
    on_edit_application = State()  # Редактировать заявку
    on_edit_application_step1 = State()  # Выбор вида редактирования
    on_edit_application_step2_summary = State()  # Изменить тему
    on_edit_application_step2_description = State()  # Изменить описание
    on_edit_application_step2_kind = State()  # Изменить вид услуги
    on_edit_application_step2_type_after_kind = State()  # Изменить вид работы если поменялся вид услуги
    on_edit_application_step2_type = State()  # Изменить вид работы
    on_edit_application_step2_cancel_status = State()  # Отменить заявку
    on_edit_application_step2_add_message = State()  # Написать сообщение
    on_edit_application_step3_add_message = State()  # Написать сообщение. Получение сообщения
    # Функии заявки - Создать заявку
    on_create_application_step1 = State()  # Тема
    on_create_application_step2 = State()  # Описание
    on_create_application_step3 = State()  # Услуга
    on_create_application_step4 = State()  # Вид работы
    on_create_application_step5 = State()  # Регистрация
