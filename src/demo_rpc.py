from src.client import RPCClient, RPCError


def main() -> None:
    client = RPCClient()
    account = client.create_account("127.0.0.1")
    print("create_account:", account)
    print("get_all_accounts:", client.get_all_accounts())
    print("get_account_by_uid:", client.get_account_by_uid(account[0]))
    account = client.edit_account(account[0], "10.0.0.1")
    print("edit_account:", account)

    message = client.create_message("ping", account[0], 0)
    print("create_message:", message)
    print("get_all_messages:", client.get_all_messages())
    print("get_message_by_uid:", client.get_message_by_uid(message[0]))
    message = client.edit_message(message[0], completed=1)
    print("edit_message:", message)

    feedback = client.create_feedback("ok", "success", "", message[0])
    print("create_feedback:", feedback)
    print("get_all_feedbacks:", client.get_all_feedbacks())
    print("get_feedback_by_uid:", client.get_feedback_by_uid(feedback[0]))
    feedback = client.edit_feedback(feedback[0], status="checked")
    print("edit_feedback:", feedback)
    print("get_data_sample:", client.get_data_sample())

    try:
        client.create_message("invalid", 999_999, 0)
    except RPCError as error:
        print("Ожидаемая ошибка:", error)


if __name__ == "__main__":
    main()
