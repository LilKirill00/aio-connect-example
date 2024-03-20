import asyncio
import datetime
import os

from aio_connect import Router, F
from aio_connect.fsm.context import FSMContext
from aio_connect.filters import Command
from aio_connect.types import TypeLine, Button, FSInputFile

from docxtpl import DocxTemplate

from handlers.navigation_menu import applications
from handlers.applications_function import dateformat
from main_bot_1C_Connect import bot
from states_group.navigation import Navigation

router = Router()


@router.line(Command("help_template", prefix="?"))  # ?help_template
async def help_template(line: TypeLine) -> None:
    if line.user_id == line.author_id:
        await bot.send_message_line(
            line_id=line.line_id, user_id=line.user_id,
            text=(
                "Инструкция:\n"
                "Для создания своего шаблона, который может обработать бот, необходимо выполнить следующие шаги:\n\n"
                "1. Создайте шаблон документа в формате `.docx`.\n"
                "2. Для вставки значений в шаблон используйте плейсхолдеры в формате `{{placeholder}}`, где вместо "
                "`placeholder` укажите соответствующую переменную.\n"
                "   Например, если вы хотите, чтобы бот вставил номер заявки, используйте плейсхолдер `{{number}}` в "
                "желаемом месте документа.\n"
                "3. После добавления всех необходимых плейсхолдеров, сохраните документ и выбрав в меню "
                "`Распечатать по своему шаблону` загрузите его в чат.\n\n"
                "Список доступных плейсхолдеров:\n"
                "{{number}} - номер заявки\n"
                "{{created_at}} - дата и время создания заявки\n"
                "{{updated_at}} - дата и время последнего изменения\n"
                "{{summary}} - тема заявки\n"
                "{{description}} - описание заявки\n"
                "{{status_name}} - статус заявки\n"
                "{{kind_name}} - вид предоставляемой услуги\n"
                "{{type_name}} - тип выполняемых работ\n"
                "{{initiator_surname}} {{initiator_name}} {{initiator_patronymic}} - ФИО заказчика\n"
                "{{executor_surname}} {{executor_name}} {{executor_patronymic}}- ФИО исполнителя\n"
                "{{result}} - результат обращения\n"
                "{{datetime_generate}} - дата и время генерации отчета\n"
            )
        )


@router.line(F.text == "Распечатать", Navigation.on_applications)
async def select_print_template(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await bot.send_message_line(
            line_id=line.line_id, user_id=line.user_id,
            text="Пожалуйста, выберите один из следующих вариантов:\n"
                 "`Распечатать по своему шаблону` – вы можете загрузить и использовать свой индивидуальный документ в "
                 "качестве шаблона для отчета. Подробные инструкции по подготовке вашего шаблона вы найдёте, введя "
                 "команду: ?help_template.\n"
                 "`Распечатать по шаблону компании` – мы автоматически сгенерируем отчет о заявке, используя "
                 "стандартный шаблон компании. \n"
                 "Если вы хотите отменить эту операцию или вернуться в главное меню, пожалуйста, нажмите `Отмена`.",
            keyboard=[
                [Button(text="Отмена")],
                [Button(text="Распечатать по своему шаблону")],
                [Button(text="Распечатать по шаблону компании")],
            ])
        await state.set_state(Navigation.on_select_print_template)


@router.line(F.text == "Отмена", Navigation.on_select_print_template)
@router.line(F.text == "Отмена", Navigation.on_select_file_template)
async def stop_in_application(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await state.update_data(ticket={}, print_template={})  # Очистить данные в ticket и print_template
        await applications(line, state)


@router.line(F.text == "Назад", Navigation.on_select_file_template)
async def back_select_print(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await select_print_template(line, state)


@router.line(F.text == "Распечатать по своему шаблону", Navigation.on_select_print_template)
async def select_print_by_file_template(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        await bot.send_message_line(
            line_id=line.line_id, user_id=line.user_id,
            text="Пожалуйста, прикрепите Word файл со своим шаблоном для отчета в ответ на это сообщение. "
                 "Файл должен быть в формате `.docx` (`.doc не работает`).\n"
                 "После загрузки файла я начну процесс заполнения вашего шаблона данными о заявке. Убедитесь, что ваш "
                 "шаблон содержит все необходимые плейсхолдеры.\n"
                 "Если вам нужна помощь по структуре шаблона или информация о том, какие плейсхолдеры вы можете "
                 "использовать, введите команду ?help_template.",
            keyboard=[
                [Button(text="Отмена")],
                [Button(text="Назад")],
            ]
        )
        await state.set_state(Navigation.on_select_file_template)


@router.line(F.file, Navigation.on_select_file_template)
async def select_file_template(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        file_name = line.file.file_id + line.file.file_name

        # если имя файла в формате .docx то скачиваем и используем его как шаблон
        if file_name.lower().endswith('.docx'):
            destination = f"./uploads/temp/{file_name}"
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                        text="Получен файл. Происходит процесс создания, подождите немного")
            download_success = await bot.download_file(file_path=line.file.file_path, destination=destination)

            if download_success:
                await paste_in_template_from_ticket(destination, destination, state)

                send_result = await bot.send_file_line(line_id=line.line_id, user_id=line.user_id,
                                                       file_name=line.file.file_name, file=FSInputFile(destination))
                if send_result:
                    os.remove(destination)
                await state.update_data(print_template={})  # Очистить данные в print_template
                await applications(line, state)
        else:
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                        text="Файл не соответствует формату `.docx`.\nПовторите попытку")


async def paste_in_template_from_ticket(template_path, save_path, state) -> None:
    """Заполнение шаблона однотипными данными

    :param template_path: Путь с шаблоном
    :param save_path: Путь для сохранения
    :param state: Состаяния в которых находятся даннные заявки
    :return: None
    """
    print_template = (await state.get_data())['print_template']
    ticket = print_template['ticket']
    doc = DocxTemplate(template_path)
    context = {
        'number': ticket['number'], 'created_at': dateformat(ticket['created_at']),
        'updated_at': dateformat(ticket['updated_at']), 'summary': ticket['summary'],
        'description': ticket['description'], 'status_name': ticket['status']['name'],
        'kind_name': ticket['kind']['name'], 'type_name': ticket['type']['name'],
        'initiator_surname': ticket['initiator']['surname'], 'initiator_name': ticket['initiator']['name'],
        'initiator_patronymic': ticket['initiator']['patronymic'],
        'executor_surname': ticket['executor']['surname'], 'executor_name': ticket['executor']['name'],
        'executor_patronymic': ticket['executor']['patronymic'],
        'result': ticket['result'] if 'result' in ticket else '',
        'datetime_generate': dateformat(str(datetime.datetime.now())),
        'updated_at_new': '{{updated_at_new}}', 'summary_new': '{{summary_new}}',
        'description_new': '{{description_new}}', 'status_name_new': '{{status_name_new}}',
        'kind_name_new': '{{kind_name_new}}', 'type_name_new': '{{type_name_new}}',
    }
    doc.render(context)
    doc.save(save_path)


@router.line(F.text == "Распечатать по шаблону компании", Navigation.on_select_print_template)
async def select_print_by_company_template(line: TypeLine, state: FSMContext) -> None:
    if line.user_id == line.author_id:
        print_template = (await state.get_data())['print_template']

        # Определяем какой шаблон надо использовать
        if print_template['where'] == 'get_info':
            file_name = 'Информация о заявке.docx'
        elif print_template['where'] == 'create_info':
            file_name = 'Отчет по созданию заявки.docx'
        elif print_template['where'] == 'edit_info':
            file_name = 'Отчет по изменению заявки.docx'
        else:
            await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                        text="Произошла ошибка создания отчета")
            return

        # Заполняем шаблон
        template = f'./uploads/permanent/templates/{file_name}'
        destination = f'./uploads/temp/{line.user_id}{file_name}'
        await paste_in_template_from_ticket(template, destination, state)

        # Если шаблон об изменение то добавить в него уникальные данные которые не могут быть учитаны на предыдущем шаге
        if print_template['where'] == 'edit_info':
            ticket = await bot.get_ticket_by_number(print_template['ticket']['number'])
            if ticket['updated_at'] == print_template['ticket']['updated_at']:
                await bot.send_message_line(line_id=line.line_id, user_id=line.user_id,
                                            text="Информация о заявке не успела прогрузиться подождите немного")
                while ticket['updated_at'] == print_template['ticket']['updated_at']:
                    await asyncio.sleep(1)
                    ticket = await bot.get_ticket_by_number(print_template['ticket']['number'])
            ticket_update = print_template['ticket_update']
            doc = DocxTemplate(destination)
            context = {
                'updated_at_new': dateformat(ticket['updated_at']),
                'summary_new': ticket_update['summary'] if ticket_update['summary'] else ticket['summary'],
                'description_new': ticket_update['description'] if ticket_update['description']
                else ticket['description'],
                'status_name_new': ticket_update['status']['name'] if ticket_update['status']['name']
                else ticket['status']['name'],
                'kind_name_new': ticket['kind']['name'], 'type_name_new': ticket['type']['name'],
            }
            doc.render(context)
            doc.save(destination)

        send_result = await bot.send_file_line(line_id=line.line_id, user_id=line.user_id,
                                               file_name=file_name, file=FSInputFile(destination))
        if send_result:
            os.remove(destination)
        await state.update_data(print_template={})  # Очистить данные в print_template
        await applications(line, state)
