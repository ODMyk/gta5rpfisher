import json
import keyboard
from bot import *

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

with open(f"{path}\\defaults.json", 'r') as j:
	c = json.load(j)[0]

window = tk.Tk()

def button(text: str) -> tk.Button:
	return tk.Button(window, text=text, width=10, height=2)

def field() -> tk.Entry:
	return tk.Entry(window, width=10)

status_text = tk.Label(window, text="OFF", foreground="red", font="TimesNewRoman 18 bold")
button_cook = button("Cook")
bot = Fisher(status_text, button_cook)

window.title("Easy Fishing")
window.geometry("200x300+0+100")
window.resizable(0, 0)

button_start = button("Start")
button_stop = button("Stop")
button_reset = button("Fish reset")
button_baitset = button("Set bait")

fish_field = field()
cook_field = field()

button_start.grid(column=1, row=1)
button_stop.grid(column=1, row=2)
button_reset.grid(column=1, row=5)
button_cook.grid(column=1, row=4)
fish_field.grid(column=2, row=3)
cook_field.grid(column=2, row=4)
status_text.grid(column=2, row=1)
button_baitset.grid(column=1, row=3)

fish_field.insert(0, c)

def reset() -> None:
	logger.info("Reset function was called")
	bot.catched_fish = 0
	bot.bag_is_full = False

@logger.catch
def baitset() -> None:
	c = int(fish_field.get())
	logger.info(f"Bait count was setted to {c}")
	with open(f"{path}\\defaults.json", 'w') as j:
		json.dump([c], j)
	bot.fish_bait = c

@logger.catch
def cook() -> None:
	c = int(cook_field.get())
	bot.to_cook = c
	t2 = threading.Thread(target=bot.cook, daemon=True)
	t2.start()	

@logger.catch
def start() -> None:
	baitset()
	bot.start()

button_start.config(command=start)
button_stop.config(command=bot.stop)
button_reset.config(command=reset)
button_baitset.config(command=baitset)
button_cook.config(command=cook)

keyboard.add_hotkey("Ctrl+Num 1", start)
keyboard.add_hotkey("Ctrl+Num 2", bot.stop)
keyboard.add_hotkey("Ctrl+Num 3", reset)

bot.stop()
window.mainloop()
bot.active = False
logger.info("Exit application")
