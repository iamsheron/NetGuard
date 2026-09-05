from telegram_notifier import TelegramNotifier


telegram = TelegramNotifier()

result = telegram.send(
    "🛡 NETGUARD TEST\n\n"
    "Telegram security notifications are working!"
)

print("Result:", result)