"""
    Модуль приложения.
    Создает бота, обрабатывает команды пользователя.
"""
import telebot
from telebot import types
from typing import Optional
from Models import Invoice, Stack, User, Category, Currency, Report, Administrator
from NewExeptions import InvalidInvoice, EmptyName, EmptyCode, InvalidCurrencyCode, InvalidUserData
from Common import into_int
import BotCommands
import dotenv
import os

dotenv.load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))
stack = Stack()
new_users_await = {}


def cancel(message: types.Message):
    """Отменяет все вводы, отправляет стартовые команды."""
    user = stack.get_user_by_id(user_id=message.from_user.id)
    stack.clear_by_user(user=user)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    markup = BotCommands.StartKeyboard().keyboard
    bot_answer(
        chat_id=message.chat.id,
        answer_text='Доступные команды:',
        markup=markup
    )


def raise_commit(message: types.Message):
    """Спрашивает подтвеждение ввода. Вызвает след. клавиатуру."""
    user = stack.get_user_by_id(user_id=message.from_user.id)
    invoice = stack.get_invoice_by_user(user=user)
    text = f'Подтвердите ввод: \n' \
           f'{str(invoice)}'
    markup = BotCommands.CommitKeyboard().keyboard
    bot.reply_to(message, text=text, reply_markup=markup)


def raise_categories_kb(message: types.Message, income=False, expense=False, user_id: Optional[int] = None):
    """ Отправляет клавиатуру выбора категорий, создает новый инвойс."""
    if user_id is None:
        user_id = message.from_user.id
    user = stack.get_user_by_id(user_id=user_id)
    invoice = Invoice(income=income, expense=expense)
    stack.add_invoice(user=user, invoice=invoice)
    text = 'Выберите категорию или добавьте новую: '
    markup = BotCommands.CategoriesKeyboard().keyboard
    bot.reply_to(message, text=text, reply_markup=markup)


def raise_currencies_kb(message: types.Message, category: Optional[Category] = None, user_id: Optional[int] = None):
    """Отправляет клавиатуру выбора валюты, создает новый инвойс."""
    if user_id is None:
        user_id = message.from_user.id
    user = stack.get_user_by_id(user_id=user_id)
    invoice = stack.get_invoice_by_user(user=user)
    if invoice is None:
        invoice = Invoice(income=True)
    invoice.category = category
    stack.add_invoice(user=user, invoice=invoice)

    text = 'Выберите валюту: '
    markup = BotCommands.CurrenciesKeyboard().keyboard
    bot.reply_to(message, text=text, reply_markup=markup)


def raise_reports_kb(message: types.Message):
    """Отправляет клавиатуру выбора типа отчета."""
    text = 'Выберите тип отчета: '
    markup = BotCommands.ReportsKeyboard().keyboard
    bot.reply_to(message, text=text, reply_markup=markup)


def after_commit(message: types.Message, user_id: Optional[int] = None):
    """Сохраняет данные инвойса в БД."""
    if user_id is None:
        user_id = message.from_user.id
    user = stack.get_user_by_id(user_id=user_id)
    invoice = stack.get_invoice_by_user(user=user)
    invoice.user = user
    try:
        invoice.save()
        text = 'Учел!'
        stack.clear_by_user(user=user)
        markup = BotCommands.StartKeyboard().keyboard
        bot.reply_to(message, text=text, reply_markup=markup)
    except InvalidInvoice:
        text = f'Возникла ошибка при записи данных! Текст ошибки: \n' \
               f'{repr(InvalidInvoice().text)}'
        bot.reply_to(message, text=text)


def after_report_type_select(message: types.Message, report_type: str, user_id: Optional[int] = None):
    """Добавляет отчет в стак. Вызывает след. клавиатуру."""
    if user_id is None:
        user_id = message.from_user.id
    account_balance = False
    expenses = False
    income = False
    if report_type == 'account_balance':
        account_balance = True
    elif report_type == 'expenses':
        expenses = True
    elif report_type == 'income':
        income = True

    report = Report(account_balance=account_balance, expenses=expenses, income=income)
    user = stack.get_user_by_id(user_id=user_id)
    stack.add_report(user=user, report=report)
    if expenses:
        markup = BotCommands.YesNoKeyboard().keyboard
        text = 'В разрезе категорий затрат?'
        bot.reply_to(message, text=text, reply_markup=markup)
    else:
        markup = BotCommands.DateKeyboard().keyboard
        text = "Введите дату или выберите 'На сегодня'"
        msg = bot.reply_to(message, text=text, reply_markup=markup)
        bot.register_next_step_handler(msg, callback=after_date_input)


def after_group_select(message: types.Message, group_by_category: bool, user_id: Optional[int] = None):
    """Запоминает ответ на вопрос о группировке отчета по категориям. Вызывает след. клавиатуру."""
    if user_id is None:
        user_id = message.from_user.id
    user = stack.get_user_by_id(user_id=user_id)
    report = stack.get_report_by_user(user=user)
    report.group_by_category = group_by_category
    stack.add_report(user=user, report=report)
    markup = BotCommands.DateKeyboard().keyboard
    text = "Введите дату или выберите 'На сегодня'"
    msg = bot.reply_to(message, text=text, reply_markup=markup)
    bot.register_next_step_handler(msg, callback=after_date_input)


def after_currency_select(message: types.Message, currency: Currency, user_id: Optional[int] = None):
    """Отправляет сообщение, регистрирует след. обработчик."""
    if user_id is None:
        user_id = message.from_user.id
    user = stack.get_user_by_id(user_id=user_id)
    invoice = stack.get_invoice_by_user(user=user)
    if invoice is None:
        invoice = Invoice(income=True)
    invoice.currency = currency
    stack.add_invoice(user=user, invoice=invoice)
    markup = BotCommands.CancelKeyboard().keyboard
    text = 'Введите сумму: '
    msg = bot.reply_to(message, text=text, reply_markup=markup)
    bot.register_next_step_handler(msg, callback=after_amount_input)


def after_category_select(message: types.Message, category: Category, user_id: Optional[int] = None):
    """Вызывает след. клавиатуру."""
    raise_currencies_kb(message=message, category=category, user_id=user_id)


def after_amount_input(message: types.Message):
    """Добавляет сумму в инвойс, вызывает след. клавиатуру."""
    user = stack.get_user_by_id(user_id=message.from_user.id)
    invoice = stack.get_invoice_by_user(user=user)
    invoice.set_amount(amount=message.text)
    stack.add_invoice(user=user, invoice=invoice)
    raise_commit(message=message)


def after_date_input(message: types.Message, user_id: Optional[int] = None, for_today: Optional[bool] = False):
    """Сохраняет дату отчета, получает данные отчета из БД, отправляет отчет в чат."""
    if user_id is None:
        user_id = message.from_user.id
    user = stack.get_user_by_id(user_id=user_id)
    report = stack.get_report_by_user(user=user)
    if not for_today:
        report.start_date = message.text
        report.end_date = message.text
    report.fill_report_data_from_db()
    markup = BotCommands.StartKeyboard().keyboard
    bot.reply_to(message, text=str(report), reply_markup=markup)
    stack.clear_by_user(user=user)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)


def adding_new_category(message: types.Message):
    """Обрабатывает команду добавления новой категории."""
    text = 'Введите название новой категории: '
    markup = BotCommands.CancelKeyboard().keyboard
    msg = bot.reply_to(message, text=text,  reply_markup=markup)
    bot.register_next_step_handler(msg, callback=after_new_category_input)


def after_new_category_input(message: types.Message):
    """Добавляет новую категорию."""
    new_category = Category(category_name=message.text.strip())
    try:
        new_category.save()
        text = f'Категория {repr(new_category.get_name())} добавлена!\n' \
               f'Выберите категорию: '
    except EmptyName:
        text = 'Не удалось сохранить новую категорию! Текст ошибки: \n' \
               f'{repr(EmptyName().text)}'
    finally:
        markup = BotCommands.CategoriesKeyboard().keyboard

    bot.reply_to(message, text=text, reply_markup=markup)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)


def adding_new_currency(message: types.Message):
    """Обрабатывает команду добавления новой валюты."""
    text = "Введите код новой валюты из трех симоволов, например, 'EUR': "
    markup = BotCommands.CancelKeyboard().keyboard
    msg = bot.reply_to(message, text=text, reply_markup=markup)
    bot.register_next_step_handler(msg, callback=after_new_currency_input)


def after_new_currency_input(message: types.Message):
    """Добавляет новую валюту."""
    new_currency = Currency(currency_code=message.text)
    try:
        new_currency.save()
        text = f'Валюта {repr(new_currency.get_code())} добавлена!\n' \
               f'Выберите валюту: '
    except EmptyCode:
        text = 'Не удалось сохранить новую валюту! Текст ошибки: \n' \
               f'{repr(EmptyCode().text)}'
    except InvalidCurrencyCode:
        text = 'Не удалось сохранить новую валюту! Текст ошибки: \n' \
               f'{repr(InvalidCurrencyCode().text)}'
    finally:
        markup = BotCommands.CurrenciesKeyboard().keyboard

    bot.reply_to(message, text=text, reply_markup=markup)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)


def after_admin_confirm(message: types.Message, admin_confirmed: bool, admin_id: int):
    """Обрабатывает ответ администратора, если есть разрешение - сохраняет нового пользователя в БД."""

    pos1 = message.html_text.find('(')
    pos2 = message.html_text.find(')')
    new_user_id = into_int(message.html_text[pos1:pos2+1].replace('(id: ', '').replace(')', ''))
    if not admin_confirmed:
        bot_answer(answer_text='Вам отказано в регистрации.', chat_id=new_user_id)
        bot_answer(answer_text='Пользователю отказано в регистрации.', chat_id=admin_id)
        return

    new_user_name = new_users_await.get(new_user_id)
    new_user = User(user_id=new_user_id, user_name=new_user_name)
    try:
        new_user.save()
        text = 'Пользователь успешно добавлен! \n' \
               'Доступные команды: '
        bot_answer(answer_text='Пользователь успешно добавлен!', chat_id=admin_id)
        markup = BotCommands.StartKeyboard().keyboard
    except InvalidUserData:
        text = f'Ошибка при добавлении нового пользователя! Текст ошибки: \n' \
               f'{repr(InvalidUserData().text)}'
        markup = None

    bot_answer(answer_text=text, chat_id=new_user_id, markup=markup)
    new_users_await.clear()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    """Функция-диспетчер, определяет следующие вызовы."""
    user = stack.get_user_by_id(user_id=call.from_user.id)
    if user is None:
        user = User(user_id=call.from_user.id, user_name=call.from_user.full_name)
    if not user.is_registered():
        bot_answer(answer_text='У Вас нет доступа.', chat_id=call.message.chat.id)
        return
    stack.add_user(user=user)

    if call.data.find('new_user_confirm') > -1:
        admin_confirmed = call.data.split('_')[-1].lower() == 'yes'
        after_admin_confirm(message=call.message, admin_confirmed=admin_confirmed, admin_id = call.from_user.id)

    if call.data == 'cancel':
        cancel(call.message)

    if call.data == 'add_expenses':
        stack.clear_by_user(user=user)
        stack.add_user(user=user)
        raise_categories_kb(message=call.message, expense=True, user_id=call.from_user.id)

    if call.data == 'add_income':
        stack.clear_by_user(user=user)
        stack.add_user(user=user)
        raise_currencies_kb(message=call.message, user_id=call.from_user.id)

    if call.data.find('category_id_') > -1:
        category_id = call.data.split('_')[-1]
        category = Category()
        category.fill_from_db(category_id=category_id)
        after_category_select(message=call.message,
                              category=category,
                              user_id=call.from_user.id)

    if call.data.find('currency_id_') > -1:
        currency_code = call.data.split('_')[-1]
        currency = Currency()
        currency.fill_from_db(currency_code=currency_code)
        after_currency_select(message=call.message,
                              currency=currency,
                              user_id=call.from_user.id)

    if call.data == 'reports':
        raise_reports_kb(message=call.message)

    if call.data in ['account_balance', 'expenses', 'income']:
        after_report_type_select(message=call.message, report_type=call.data, user_id=call.from_user.id)

    if call.data.find('group_by_category') > -1:
        group_by_category = call.data.split('_')[-1].lower() == 'yes'
        after_group_select(message=call.message, user_id=call.from_user.id, group_by_category=group_by_category)

    if call.data == 'date_today':
        after_date_input(message=call.message, user_id=call.from_user.id, for_today=True)

    if call.data == 'new_category':
        adding_new_category(message=call.message)

    if call.data == 'new_currency':
        adding_new_currency(message=call.message)

    if call.data == 'commit':
        after_commit(message=call.message, user_id=call.from_user.id)


@bot.message_handler(commands=['Start', 'start'])
def start_command_answer(message: types.Message):
    """Отвечает на команду старт."""
    user = stack.get_user_by_id(user_id=message.from_user.id)
    if user is None:
        user = User(user_id=message.from_user.id, user_name=message.from_user.full_name)
    if not user.is_registered():
        bot_answer(answer_text='У Вас нет доступа.', chat_id=message.chat.id)
    else:
        stack.add_user(user=user)
        markup = BotCommands.StartKeyboard().keyboard
        bot_answer(
            chat_id=message.chat.id,
            answer_text='Готов к работе!\n'
                        'Доступные команды:',
            markup=markup)


@bot.message_handler(commands=['reg', 'Reg', 'REG'])
def reg_command_answer(message: types.Message):
    """Отвечает на команду регистрации нового пользователя."""
    user = stack.get_user_by_id(user_id=message.from_user.id)
    if user is None:
        user = User(user_id=message.from_user.id, user_name=message.from_user.username)
    awaiting_user = new_users_await.get(user.get_id())
    if awaiting_user is not None:
        bot_answer(chat_id=message.chat.id, answer_text='Пожалуйста, подождите...')
        return

    if not user.is_registered():
        admin = Administrator()
        admin.fill_from_db()
        if admin.is_valid():
            chat_id = admin.get_id()
            markup = BotCommands.AdminYesNoKeyboard().keyboard
            text = f'Новый пользователь @{message.from_user.username} (id: {user.get_id()}) запросил регистрацию.\n' \
                   f'Подтвердить регистрацию пользователя?'
            bot_answer(
                chat_id=chat_id,
                answer_text=text,
                markup=markup)
            new_users_await.update({user.get_id(): message.from_user.full_name})
            bot_answer(
                chat_id=message.chat.id,
                answer_text='Пожалуйста, подождите...')
        else:
            text = 'Не удалось зарегистрировать нового пользователя.'
            bot_answer(
                chat_id=message.chat.id,
                answer_text=text)
    else:
        stack.add_user(user=user)
        text = 'Вы уже есть в списке пользователей бота!\n' \
               'Доступные команды: '
        markup = BotCommands.StartKeyboard().keyboard
        bot_answer(
            chat_id=message.chat.id,
            answer_text=text,
            markup=markup)


def bot_answer(answer_text: str, chat_id: str or int, markup: Optional[types.InlineKeyboardMarkup] = None):
    """Отправляет сообщение в чат."""
    bot.send_message(chat_id, answer_text, reply_markup=markup)


if __name__ == '__main__':
    bot.infinity_polling()
