import datetime

SAMPLE_WINDOW_SECONDS = 8 * 60

accounts = []
messages = []
feedbacks = []


def get_next_uid(table: list) -> int:
    if len(table) == 0:
        return 0
    entity = max(table, key=lambda current_entity: current_entity[0])
    return entity[0] + 1


def create_account(ip):
    uid = get_next_uid(accounts)
    timestamp = int(datetime.datetime.now().timestamp())
    account = (uid, timestamp, ip)
    accounts.append(account)
    return account


def get_all_accounts():
    return accounts


def get_account_by_uid(uid):
    for account in accounts:
        if account[0] == uid:
            return account
    return None


def edit_account(uid, ip=None):
    index = None
    for current_index, account in enumerate(accounts):
        if account[0] == uid:
            index = current_index
            break

    if index is None:
        raise ValueError(f"Account с uid={uid} не найден")

    new_timestamp = int(datetime.datetime.now().timestamp())
    new_ip = ip if ip is not None else accounts[index][2]
    updated_account = (uid, new_timestamp, new_ip)
    accounts[index] = updated_account
    return updated_account


def create_message(argument, account, completed):
    if get_account_by_uid(account) is None:
        raise ValueError(
            f"Нельзя создать Message: Account с uid={account} не найден"
        )

    uid = get_next_uid(messages)
    timestamp = int(datetime.datetime.now().timestamp())
    message = (uid, timestamp, argument, account, completed)
    messages.append(message)
    return message


def get_all_messages():
    return messages


def get_message_by_uid(uid):
    for message in messages:
        if message[0] == uid:
            return message
    return None


def edit_message(uid, argument=None, account=None, completed=None):
    index = None
    for current_index, message in enumerate(messages):
        if message[0] == uid:
            index = current_index
            break

    if index is None:
        raise ValueError(f"Message с uid={uid} не найден")

    if account is not None and get_account_by_uid(account) is None:
        raise ValueError(f"Account с uid={account} не найден")

    new_timestamp = int(datetime.datetime.now().timestamp())
    new_argument = argument if argument is not None else messages[index][2]
    new_account = account if account is not None else messages[index][3]
    new_completed = completed if completed is not None else messages[index][4]
    updated_message = (
        uid,
        new_timestamp,
        new_argument,
        new_account,
        new_completed,
    )
    messages[index] = updated_message
    return updated_message


def create_feedback(result, status, failure, message):
    if get_message_by_uid(message) is None:
        raise ValueError(
            f"Нельзя создать Feedback: Message с uid={message} не найден"
        )

    uid = get_next_uid(feedbacks)
    timestamp = int(datetime.datetime.now().timestamp())
    feedback = (uid, timestamp, result, status, failure, message)
    feedbacks.append(feedback)
    return feedback


def get_all_feedbacks():
    return feedbacks


def get_feedback_by_uid(uid):
    for feedback in feedbacks:
        if feedback[0] == uid:
            return feedback
    return None


def edit_feedback(
    uid,
    result=None,
    status=None,
    failure=None,
    message=None,
):
    index = None
    for current_index, feedback in enumerate(feedbacks):
        if feedback[0] == uid:
            index = current_index
            break

    if index is None:
        raise ValueError(f"Feedback с uid={uid} не найден")

    if message is not None and get_message_by_uid(message) is None:
        raise ValueError(f"Message с uid={message} не найден")

    new_timestamp = int(datetime.datetime.now().timestamp())
    new_result = result if result is not None else feedbacks[index][2]
    new_status = status if status is not None else feedbacks[index][3]
    new_failure = failure if failure is not None else feedbacks[index][4]
    new_message = message if message is not None else feedbacks[index][5]
    updated_feedback = (
        uid,
        new_timestamp,
        new_result,
        new_status,
        new_failure,
        new_message,
    )
    feedbacks[index] = updated_feedback
    return updated_feedback


def get_data_sample():
    result = []
    current_timestamp = int(datetime.datetime.now().timestamp())
    time_limit = current_timestamp - SAMPLE_WINDOW_SECONDS

    for account in accounts:
        if account[1] >= time_limit:
            account_messages = [
                message
                for message in messages
                if message[3] == account[0]
            ]

            for message in account_messages:
                result.append((account[2], message[2]))

            if not account_messages:
                result.append((account[2], None))

    return result


def show_expected_error(function, *args):
    try:
        function(*args)
    except ValueError as error:
        print(f"Ожидаемая ошибка: {error}")
    else:
        raise AssertionError("Ожидаемая ошибка не возникла")


def test_accounts():
    print("\nAccount")
    first_account = create_account("127.0.0.1")
    second_account = create_account("192.168.0.1")
    print(f"create_account: {first_account}")
    print(f"create_account: {second_account}")
    print(f"get_all_accounts: {get_all_accounts()}")
    found_account = get_account_by_uid(first_account[0])
    print(f"get_account_by_uid: {found_account}")
    updated_account = edit_account(first_account[0], "10.0.0.1")
    print(f"edit_account: {updated_account}")
    return updated_account


def test_messages(account_uid):
    print("\nMessage")
    message = create_message("ping", account_uid, 0)
    print(f"create_message: {message}")
    print(f"get_all_messages: {get_all_messages()}")
    found_message = get_message_by_uid(message[0])
    print(f"get_message_by_uid: {found_message}")
    updated_message = edit_message(
        message[0],
        argument="ping-updated",
        completed=1,
    )
    print(f"edit_message: {updated_message}")
    return updated_message


def test_feedbacks(message_uid):
    print("\nFeedback")
    feedback = create_feedback("ok", "success", "", message_uid)
    print(f"create_feedback: {feedback}")
    print(f"get_all_feedbacks: {get_all_feedbacks()}")
    found_feedback = get_feedback_by_uid(feedback[0])
    print(f"get_feedback_by_uid: {found_feedback}")
    updated_feedback = edit_feedback(feedback[0], status="checked")
    print(f"edit_feedback: {updated_feedback}")


def test_errors():
    print("\nОбработка ошибок")
    show_expected_error(edit_account, 999)
    show_expected_error(create_message, "test", 999, 0)
    show_expected_error(
        create_feedback,
        "error",
        "failed",
        "failure",
        999,
    )


def test_model():
    saved_accounts = accounts.copy()
    saved_messages = messages.copy()
    saved_feedbacks = feedbacks.copy()
    accounts.clear()
    messages.clear()
    feedbacks.clear()

    try:
        account = test_accounts()
        message = test_messages(account[0])
        test_feedbacks(message[0])
        print(f"\nget_data_sample: {get_data_sample()}")
        test_errors()
        print("\nПроверка завершена успешно.")
    finally:
        accounts[:] = saved_accounts
        messages[:] = saved_messages
        feedbacks[:] = saved_feedbacks


ACCOUNT_COMMANDS = (
    "create_account",
    "get_all_accounts",
    "get_account_by_uid",
    "edit_account",
)

MESSAGE_COMMANDS = (
    "create_message",
    "get_all_messages",
    "get_message_by_uid",
    "edit_message",
)

FEEDBACK_COMMANDS = (
    "create_feedback",
    "get_all_feedbacks",
    "get_feedback_by_uid",
    "edit_feedback",
)


def show_commands():
    """Показать команды, доступные в интерактивном режиме."""
    groups = (
        ("Account", ACCOUNT_COMMANDS),
        ("Message", MESSAGE_COMMANDS),
        ("Feedback", FEEDBACK_COMMANDS),
        ("Дополнительно", ("get_data_sample", "test_model", "help", "exit")),
    )
    print("\nДоступные команды:")
    for title, commands in groups:
        print(f"  {title}:")
        for command in commands:
            print(f"    {command}")
    print("Введите название команды и следуйте подсказкам.\n")


def handle_account_command(current_choice):
    match current_choice:
        case "create_account":
            ip = input("Введите IP-адрес: ")
            print(f"Создан аккаунт: {create_account(ip)}")
        case "get_all_accounts":
            print(f"Все аккаунты: {get_all_accounts()}")
        case "get_account_by_uid":
            uid = int(input("Введите UID аккаунта: "))
            print(f"Аккаунт: {get_account_by_uid(uid)}")
        case "edit_account":
            uid = int(input("Введите UID аккаунта: "))
            ip = input("Введите новый IP или оставьте пустым: ")
            print(f"Аккаунт обновлен: {edit_account(uid, ip or None)}")


def handle_message_command(current_choice):
    match current_choice:
        case "create_message":
            argument = input("Введите аргумент: ")
            account = int(input("Введите UID аккаунта: "))
            completed = int(input("Введите статус выполнения: "))
            print(
                "Создано сообщение:",
                create_message(argument, account, completed),
            )
        case "get_all_messages":
            print(f"Все сообщения: {get_all_messages()}")
        case "get_message_by_uid":
            uid = int(input("Введите UID сообщения: "))
            print(f"Сообщение: {get_message_by_uid(uid)}")
        case "edit_message":
            handle_edit_message()


def handle_edit_message():
    uid = int(input("Введите UID сообщения: "))
    argument = input("Введите новый аргумент или оставьте пустым: ")
    account = input("Введите новый UID аккаунта или оставьте пустым: ")
    completed = input("Введите новый статус или оставьте пустым: ")
    message = edit_message(
        uid,
        argument=argument or None,
        account=int(account) if account else None,
        completed=int(completed) if completed else None,
    )
    print(f"Сообщение обновлено: {message}")


def handle_edit_feedback():
    uid = int(input("Введите UID обратного сообщения: "))
    result = input("Введите новый результат или оставьте пустым: ")
    status = input("Введите новый статус или оставьте пустым: ")
    failure = input("Введите причину ошибки или оставьте пустым: ")
    message = input("Введите новый UID сообщения или оставьте пустым: ")
    feedback = edit_feedback(
        uid,
        result=result or None,
        status=status or None,
        failure=failure or None,
        message=int(message) if message else None,
    )
    print(f"Обратное сообщение обновлено: {feedback}")


def handle_feedback_command(current_choice):
    match current_choice:
        case "create_feedback":
            result = input("Введите результат: ")
            status = input("Введите статус: ")
            failure = input("Введите причину ошибки: ")
            message = int(input("Введите UID сообщения: "))
            feedback = create_feedback(result, status, failure, message)
            print(f"Создано обратное сообщение: {feedback}")
        case "get_all_feedbacks":
            print(f"Все обратные сообщения: {get_all_feedbacks()}")
        case "get_feedback_by_uid":
            uid = int(input("Введите UID обратного сообщения: "))
            print(f"Обратное сообщение: {get_feedback_by_uid(uid)}")
        case "edit_feedback":
            handle_edit_feedback()


def process_command(current_choice):
    match current_choice:
        case "help":
            show_commands()
        case "test_model":
            test_model()
        case "get_data_sample":
            print(f"Результат выборки: {get_data_sample()}")
        case "exit":
            print("Выход из программы.")
            return False
        case command if command in ACCOUNT_COMMANDS:
            handle_account_command(command)
        case command if command in MESSAGE_COMMANDS:
            handle_message_command(command)
        case command if command in FEEDBACK_COMMANDS:
            handle_feedback_command(command)
        case _:
            print("Неизвестная команда.")
    return True


def repl():
    show_commands()
    while True:
        try:
            current_choice = input("Введите команду: ").strip()
            if not process_command(current_choice):
                break
        except ValueError as error:
            print(f"Ошибка: {error}")
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break


if __name__ == "__main__":
    repl()
