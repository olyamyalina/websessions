import datetime


accounts = []
messages = []
feedbacks = []


def get_next_uid(table: list) -> int:
    if len(table) == 0:
        return 0
    entity = max(table, key=lambda entity: entity[0])
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
    for i, account in enumerate(accounts):
        if account[0] == uid:
            index = i
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
            f"Нельзя создать Message: "
            f"Account с uid={account} не найден"
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
    for i, message in enumerate(messages):
        if message[0] == uid:
            index = i
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
            f"Нельзя создать Feedback: "
            f"Message с uid={message} не найден"
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


def edit_feedback(uid, result=None, status=None, failure=None, message=None):
    index = None
    for i, feedback in enumerate(feedbacks):
        if feedback[0] == uid:
            index = i
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
    time_limit = current_timestamp - 8 * 60

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


def handle_account_command(current_choice):
    match current_choice:
        case "create_account":
            ip = input("Введите IP-адрес: ")
            account = create_account(ip)
            print(f"Создан аккаунт: {account}")

        case "get_all_accounts":
            print(f"Все аккаунты: {get_all_accounts()}")

        case "get_account_by_uid":
            uid = int(input("Введите UID аккаунта: "))
            account = get_account_by_uid(uid)
            print(f"Аккаунт: {account}")

        case "edit_account":
            uid = int(input("Введите UID аккаунта: "))
            ip = input(
                "Введите новый IP-адрес "
                "(или оставьте пустым для сохранения текущего): "
            )
            ip = ip if ip else None
            account = edit_account(uid, ip=ip)
            print(f"Аккаунт обновлен: {account}")


def handle_message_command(current_choice):
    match current_choice:
        case "create_message":
            argument = input("Введите аргумент: ")
            account = int(input("Введите UID аккаунта: "))
            completed = int(input("Введите статус выполнения: "))
            message = create_message(argument, account, completed)
            print(f"Создано сообщение: {message}")

        case "get_all_messages":
            print(f"Все сообщения: {get_all_messages()}")
        case "get_message_by_uid":
            uid = int(input("Введите UID сообщения: "))
            message = get_message_by_uid(uid)
            print(f"Сообщение: {message}")

        case "edit_message":
            uid = int(input("Введите UID сообщения: "))
            argument = input(
                "Введите новый аргумент "
                "(или оставьте пустым для сохранения текущего): "
            )
            argument = argument if argument else None
            account = input(
                "Введите новый UID аккаунта "
                "(или оставьте пустым для сохранения текущего): "
            )
            account = int(account) if account else None
            completed = input(
                "Введите новый статус выполнения "
                "(или оставьте пустым для сохранения текущего): "
            )
            completed = int(completed) if completed else None
            message = edit_message(
                uid,
                argument=argument,
                account=account,
                completed=completed,
            )
            print(f"Сообщение обновлено: {message}")


def handle_edit_feedback():
    uid = int(input("Введите UID обратного сообщения: "))
    result = input(
        "Введите новый результат "
        "(или оставьте пустым для сохранения текущего): "
    )
    result = result if result else None
    status = input(
        "Введите новый статус "
        "(или оставьте пустым для сохранения текущего): "
    )
    status = status if status else None
    failure = input(
        "Введите новую причину ошибки "
        "(или оставьте пустым для сохранения текущего): "
    )
    failure = failure if failure else None
    message = input(
        "Введите новый UID сообщения "
        "(или оставьте пустым для сохранения текущего): "
    )
    message = int(message) if message else None
    feedback = edit_feedback(
        uid,
        result=result,
        status=status,
        failure=failure,
        message=message,
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
            feedback = get_feedback_by_uid(uid)
            print(f"Обратное сообщение: {feedback}")

        case "edit_feedback":
            handle_edit_feedback()


def repl():
    while True:
        try:
            current_choice = input("Введите команду: ").strip()

            match current_choice:
                case "get_data_sample":
                    print(f"Результат выборки: {get_data_sample()}")

                case "exit":
                    print("Выход из программы.")
                    break

                case command if command in ACCOUNT_COMMANDS:
                    handle_account_command(command)

                case command if command in MESSAGE_COMMANDS:
                    handle_message_command(command)

                case command if command in FEEDBACK_COMMANDS:
                    handle_feedback_command(command)

                case _:
                    print("Неизвестная команда.")

        except ValueError as error:
            print(f"Ошибка: {error}")

        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break


if __name__ == "__main__":
    repl()
