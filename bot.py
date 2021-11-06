import sys
import mss
import time
import mouse
import random
import config
import telebot
import threading
import pyautogui
import pytesseract
import numpy as np
import tkinter as tk

from PIL import Image
from os import path as p
from loguru import logger # Ёлочка импортов :)

path = sys.argv[0]
if not p.isdir(path):
        path = f"{path}\\.."
	

logger.add(f"{path}\\LOGS.log", format="[{level}] | {time} | {message}", level="DEBUG", rotation="5 MB", compression="zip")

class Notificator():

	def __init__(self):
		
		self.bot = telebot.TeleBot(config.TOKEN, False)

	def notify(self, message: str) -> None:
		
		self.bot.send_message(config.USER_ID, message)

class Fisher():

	def __init__(self,  status_text: tk.Label=None, cook_button: tk.Button=None) -> None:

		self.status_text = status_text
		self.cook_button = cook_button
		self.sct = mss.mss()
		self.notificator = Notificator()
		self.last_click = time.time()
		self.last_rod_dropped = time.time()
		self.active = False
		self.catched_fish = 0
		self.captcha = False
		self.bag_is_full = False
		self.to_cook = 0

	@logger.catch
	def drop_rod(self, seconds_to_prepare: float) -> None:
		time.sleep(self.delay() + seconds_to_prepare)
		pyautogui.press("num5")
		logger.info("New rod dropped")
		self.last_rod_dropped = time.time()
	
	@staticmethod
	def delay() -> float:

		return random.randint(1000, 2000)/250000

	@logger.catch
	def click(self, button: str="left") -> None:

		mouse.press(button)
		time.sleep(self.delay())
		mouse.release(button)
		time.sleep(self.delay())

	@logger.catch
	def cook(self) -> None:
		
		logger.info(f"Cooking a few fishes ({self.to_cook})")
		time.sleep(2)
		while self.to_cook > 0:
			if self.cook_button:
				self.cook_button.config(text=f"Cook - {self.to_cook}")
			mouse.move(*config.cooking[1])
			self.click("right")
			mouse.move(*config.cooking[2])
			self.click("right")
			mouse.move(*config.cooking[3])
			self.click()
			self.to_cook -= 1
			time.sleep(5.5)
		if self.cook_button:
			self.cook_button.config(text="Cook")

	@logger.catch
	def fish_2_bag(self) -> None:

		logger.info("Fish was replaced to bag")
		pyautogui.press("i")
		time.sleep(1)

		for slot in config.fish_slots:
			x, y = slot[1]
			x0, y0 = slot[0]
			mouse.drag(start_x=x0, start_y=y0, end_x=x, end_y=y)
			time.sleep(0.5)

		self.catched_fish = 0
		self.bag_is_full = True
		pyautogui.press("i")
		time.sleep(1)

	def start(self) -> None:

		if not self.active:
			
			logger.info("Start function was called")
			if self.status_text:
				self.status_text.config(text="PROCESS", font="TimesNewRoman 14 bold", foreground="yellow")
				time.sleep(2)
				self.status_text.config(text="ON", font="TimesNewRoman 14 bold", foreground="green")
			self.active = True
			self.last_click = time.time()
			self.drop_rod(0.0)

			t1 = threading.Thread(target=self.fishing_cycle, daemon=True)
			t1.start()	

	def stop(self) -> None:

		if self.active:

			logger.info("Stop function was called")
			self.active = False
			if self.status_text:
				self.status_text.config(text="OFF", font="TimesNewRoman 14 bold", foreground="red")

	@logger.catch
	def get_pcm6(self, monitor: dict) -> str:

		img = np.asarray(self.sct.grab(monitor))
		pcm6 = pytesseract.image_to_string(img, lang='rus', config='--psm 6').lower()
		return pcm6
	
	@logger.catch
	def fishing_cycle(self) -> None:

		while self.active:

			img2 = np.asarray(self.sct.grab(config.mon2))
			cond = True
			for something in img2:
				if not cond:
					break
				for pixel in something:
					if pixel[0] < 10 and\
					pixel[1] < 10 and\
					200 < pixel[2]:
						continue
					else:
						cond = False
						break

			if cond:
				if self.captcha:
					self.captcha = False
				self.click()
				self.last_click = time.time()
			else:
				
				seconds_after_catch = time.time() - self.last_click
				if 4 < seconds_after_catch < 6:
					
					pcm6_1 = self.get_pcm6(config.mon1)
					if ('у вас нет' in pcm6_1):
						logger.info("No more fish bait")
						self.notificator.notify("Закончилась приманка.")
						self.stop()
						break
					elif ('нельзя рыбачить' in pcm6_1):
						logger.info("Out of zone")
						self.notificator.notify("Слетела зона рыбалки.")
						self.stop()
						break
					elif ('нельзя делать' in pcm6_1):
						logger.info("Fall in sea")
						self.notificator.notify("Упал в воду.")
						self.stop()
						break
					elif ('не получилось' in pcm6_1):
						logger.info("One fish was lost")
						self.drop_rod(6 - seconds_after_catch)
					elif ("вы поймали" in pcm6_1):
						self.catched_fish += 1
						logger.info(f"Fish catched ({self.catched_fish})")
						if self.fish_bait > 0:
							if self.catched_fish == self.fish_bait and not self.bag_is_full:
								self.fish_2_bag()
						self.drop_rod(6 - seconds_after_catch)
					elif ("действие заблокировано" in pcm6_1):
						self.stop()
						break

				if 0 < time.time() - self.last_rod_dropped < 3 and not self.captcha:
					
					pcm6_3 = self.get_pcm6(config.mon3)
					if ('я робот' in pcm6_3):
						logger.info("Captcha was detected")
						self.notificator.notify("Капча.")
						self.captcha = True

	@staticmethod
	def save_image(title: str, img) -> None:
		
		im = Image.fromarray(img)
		im.save(f"{path}\\{title}.png")
