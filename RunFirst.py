import os, sys

dir_root = sys.argv[0]
if not os.path.isdir(dir_root):
    dir_root = "\\".join((dir_root, ".."))

token = input("Telegram-bot token: ")
uid = input("Telegram user id: ")

with open(f"{dir_root}\\config.py", 'a', encoding='utf-8') as file:
    file.write(f"\nTOKEN = '{token}'\nUSER_ID = {int(uid)}")

print("Sucess")
