#!/usr/local/bin/python3.11
# -*- coding: utf-8 -*-
# -*- encoding:UTF-8 -*-
# coding=utf-8
# coding:utf-8


from PyQt6.QtWidgets import (QWidget, QPushButton, QApplication,
							 QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,
							 QSystemTrayIcon, QMenu, QDialog, QMenuBar, QCheckBox,
							 QTextEdit, QComboBox, QListWidget, QFileDialog, QGraphicsOpacityEffect,
							 QStackedWidget, QScrollArea, QGraphicsDropShadowEffect, QMainWindow, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QUrl, QPropertyAnimation, QEasingCurve, QRectF, QPoint, QRect
from PyQt6.QtGui import QAction, QIcon, QColor, QMovie, QDesktopServices, QPixmap, QPainter, QPainterPath, QPainter, QPen, QBrush, QLinearGradient, QMouseEvent, QImage, QSurfaceFormat, QPalette, QCursor
import PyQt6.QtGui
import PyQt6.sip
import webbrowser
import sys
import subprocess
from bs4 import BeautifulSoup
import html2text
import urllib3
import logging
import requests
import re
import os
from pathlib import Path
from pynput import mouse
import urllib.parse
from PIL import Image, ImageFilter
import xattr
import plistlib
import datetime
import codecs
import time
import math
import shutil
import platform
import objc
try:
	from AppKit import NSWorkspace, NSScreen
	from Foundation import NSObject, NSNotificationCenter, NSSelectorFromString, NSDistributedNotificationCenter, NSUserDefaults
except ImportError:
	print("can't import AppKit -- maybe you're running python from homebrew?")
	print("try running with /usr/bin/python instead")
	exit(1)


os.environ["QT_QUICK_BACKEND"] = "metal"

fmt = QSurfaceFormat()
fmt.setSamples(8)  # 打开 MSAA 多重采样抗锯齿
QSurfaceFormat.setDefaultFormat(fmt)

def is_dark_theme(app):
	defaults = NSUserDefaults.standardUserDefaults()
	style = defaults.stringForKey_("AppleInterfaceStyle")
	return style == "Dark"

def set_light_palette(app):
	palette = QPalette()
	palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
	palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
	palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
	palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
	palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
	palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
	app.setPalette(palette)
	light_sheet = '''
	QTextEdit{
		border: 1px grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #F3F2EE;
		color: #000000;
		font: 14pt;
	}
	QListWidget{
		border: 1px grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #F3F2EE;
		color: #000000;
		font: 14pt;
	}
	QLabel{
		color: #000000;
	}
	'''
	app.setStyleSheet(light_sheet)

def set_dark_palette(app):
	palette = QPalette()
	palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
	palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
	palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
	palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
	palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
	palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
	app.setPalette(palette)
	dark_sheet = '''
	QTextEdit{
		border: 1px grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #2D2D2D;
		color: #FFFFFF;
		font: 14pt;
	}
	QListWidget{
		border: 1px grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #2D2D2D;
		color: #FFFFFF;
		font: 14pt;
	}
	QLabel{
		color: #FFFFFF;
	}
		'''
	app.setStyleSheet(dark_sheet)


class ThemeObserver(NSObject):
	def initWithApp_(self, app):
		self = objc.super(ThemeObserver, self).init()
		self.app = app
		return self

	def themeChanged_(self, notification):
		# 主题变更时自动切换 palette
		if is_dark_theme(self.app):
			set_dark_palette(self.app)
			#print("Dark theme changed")
		else:
			set_light_palette(self.app)
			#print("Light theme changed")


def install_theme_observer(app):
	observer = ThemeObserver.alloc().initWithApp_(app)
	center = NSDistributedNotificationCenter.defaultCenter()
	center.addObserver_selector_name_object_(
		observer,
		NSSelectorFromString("themeChanged:"),
		"AppleInterfaceThemeChangedNotification",
		None
	)
	return observer

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

if is_dark_theme(app):
	set_dark_palette(app)
else:
	set_light_palette(app)

theme_observer = install_theme_observer(app)


def is_macos_16_or_higher():
	version_str = platform.mac_ver()[0]  # 例如 "14.5.0" (macOS 14)
	if version_str:
		major = int(version_str.split('.')[0])
		return major >= 16
	return False

# 获取沙盒 Application Support 路径
base_dir = Path.home() / "Library/Application Support" / 'com.ryanthehito.hazelnut'
base_dir.mkdir(parents=True, exist_ok=True)
resource_tarname = "Resources/"
#resource_tarname = '/Applications/Hazelnut.app/Contents/Resources/'  # test
BasePath = str(os.path.join(base_dir, resource_tarname))
#BasePath = ''  # test
# base_dir = ''  # test

# copy items from app to basepath
old_base_path = Path('/Applications/Hazelnut Tags.app/Contents/Resources/')
if getattr(sys, 'frozen', False):  # 判断是否是打包后的应用
	old_base_path = Path(sys.executable).parent.parent / "Resources"
else:
	# 开发环境路径（可以自定义）
	old_base_path = Path(__file__).parent / "Resources"
	#old_base_path = Path('/Applications/Hazelnut Tags.app/Contents/Resources')  # test
source_dir = old_base_path
target_dir = os.path.join(base_dir, resource_tarname)
# 只在目标目录不存在文件时才复制
for item in source_dir.iterdir():
	target_item = os.path.join(target_dir, item.name)
	if os.path.exists(target_item):
		continue  # 已存在就跳过
	if item.is_dir():
		shutil.copytree(item, target_item)
	else:
		os.makedirs(os.path.dirname(target_item), exist_ok=True)  # 确保父目录存在
		shutil.copy2(item, target_item)

# Create the icon
icon = QIcon(BasePath + "Hazelnut-menu.icns")

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()

# action3 = QAction("🥜 Switch on Hazelnut!")
# action3.setCheckable(True)
# menu.addAction(action3)
#
# menu.addSeparator()

action7 = QAction("⚙️ Settings")
menu.addAction(action7)

action10 = QAction("🛠️ Start on login")
action10.setCheckable(True)
menu.addAction(action10)
plist_filename = 'com.ryanthehito.hazelnut.plist'
launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
launch_agents_dir.mkdir(parents=True, exist_ok=True)
destination = launch_agents_dir / plist_filename
if os.path.exists(destination):
	action10.setChecked(True)
else:
	action10.setChecked(False)

menu.addSeparator()

action2 = QAction("🆕 Check for Updates")
menu.addAction(action2)

action1 = QAction("ℹ️ About")
menu.addAction(action1)

action9 = QAction("🔤 Guide and Support")
menu.addAction(action9)

menu.addSeparator()

action8 = QAction("🔁 Restart")
menu.addAction(action8)

# Add a Quit option to the menu.
quit = QAction("Quit")
menu.addAction(quit)

# Add the menu to the tray
tray.setContextMenu(menu)

# create a system menu
btna4 = QAction("&Switch on Hazelnut Tags!")
btna5 = QAction("&Set!")
btna6 = QAction("&Quit!")
sysmenu = QMenuBar()
file_menu = sysmenu.addMenu("&Actions")
file_menu.addAction(btna4)
file_menu.addAction(btna5)
file_menu.addAction(btna6)


class WhiteButton(QPushButton):
	def __init__(self, text):
		super().__init__(text)
		self.setFixedHeight(30)
		self.setStyleSheet("""
		QPushButton {
			background-color: white;
			color: #444;
			border: none;
			border-radius: 15px;
			font-size: 13px;
			padding: 5px 20px;
		}
		QPushButton:hover {
			background-color: #f5f5f5;
		}
		""")

		shadow = QGraphicsDropShadowEffect(self)
		shadow.setBlurRadius(40)
		shadow.setXOffset(0)
		shadow.setYOffset(0)
		shadow.setColor(QColor(0, 0, 0, 40))  # 半透明黑色阴影
		self.setGraphicsEffect(shadow)


class MacWindowButton(QPushButton):
	def __init__(self, color, symbol, parent=None):
		super().__init__(parent)
		self.setFixedSize(12, 12)
		self.base_color = QColor(color)
		self.symbol = symbol  # "x", "-", "+"
		self.hovered = False
		self.setStyleSheet("border: none; background: transparent;")

	def enterEvent(self, event):
		self.hovered = True
		self.update()
		super().enterEvent(event)

	def leaveEvent(self, event):
		self.hovered = False
		self.update()
		super().leaveEvent(event)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
		# # 1. 选择底色
		# if self.hovered:
		# 	# hover 时用更深的颜色
		# 	if self.symbol == "x":
		# 		color = QColor("#BF4943")
		# 	elif self.symbol == "-":
		# 		color = QColor("#B29B32")
		# 	elif self.symbol == "+":
		# 		color = QColor("#24912D")
		# 	else:
		# 		color = self.base_color
		# else:
		# 	color = self.base_color
		# Draw circle
		painter.setBrush(self.base_color)
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawEllipse(0, 0, self.width(), self.height())
		# Draw symbol if hovered
		if self.hovered:
			pen = QPen(QColor("black"))
			pen.setWidth(1)
			painter.setPen(pen)
			margin = 4  # 增大 margin，叉号更小
			if self.symbol == "x":
				painter.drawLine(margin, margin, self.width()-margin, self.height()-margin)
				painter.drawLine(self.width()-margin, margin, margin, self.height()-margin)
			elif self.symbol == "-":
				painter.drawLine(margin, self.height()//2, self.width()-margin, self.height()//2)
			elif self.symbol == "+":
				painter.drawLine(self.width()//2, margin, self.width()//2, self.height()-margin)
				painter.drawLine(margin, self.height()//2, self.width()-margin, self.height()//2)


class window_about(QWidget):  # 增加说明页面(About)
	def __init__(self):
		super().__init__()
		self.radius = 16  # 圆角半径，可按 macOS 15 或 26 设置为 16~26

		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.Window
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

		self.init_ui()

	def init_ui(self):
		self.setUpMainWindow()
		self.setFixedSize(400, 600)
		self.center()
		self.setFocus()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

		rect = QRectF(self.rect())
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)

		painter.setClipPath(path)
		bg_color = self.palette().color(QPalette.ColorRole.Window)
		painter.fillPath(path, bg_color)

	# 让无边框窗口可拖动
	def mousePressEvent(self, event):
		if event.button() == Qt.MouseButton.LeftButton:
			self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
			event.accept()

	def mouseMoveEvent(self, event):
		if event.buttons() == Qt.MouseButton.LeftButton:
			self.move(event.globalPosition().toPoint() - self.drag_pos)
			event.accept()

	def setUpMainWindow(self):
		# 添加关闭按钮（仿 macOS 左上角红色圆点）
		# self.close_button = QPushButton(self)
		# self.close_button.setFixedSize(12, 12)
		# self.close_button.move(10, 10)
		# self.close_button.setStyleSheet("""
		# 	QPushButton {
		# 		background-color: #FF5F57;
		# 		border-radius: 6px;
		# 		border: none;
		# 	}
		# 	QPushButton:hover {
		# 		background-color: #BF4943;
		# 	}
		# """)
		# self.close_button.clicked.connect(self.close)
		# 三个按钮
		##FF5F57
		self.close_button = MacWindowButton("#FF605C", "x", self)
		self.close_button.move(10, 10)
		self.close_button.clicked.connect(self.close)
		##FFBD2E
		# self.min_button = MacWindowButton("#FFBD44", "-", self)
		# self.min_button.move(30, 10)
		# self.min_button.clicked.connect(self.showMinimized)
		##28C940
		# self.max_button = MacWindowButton("#00CA4E", "+", self)
		# self.max_button.move(50, 10)
		# self.max_button.clicked.connect(self.showMaximized)

		widg1 = QWidget()
		l1 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'Hazelnut-menu.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l1.setPixmap(png)  # 在l1里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l1.setMaximumWidth(100)
		l1.setMaximumHeight(100)
		l1.setScaledContents(True)
		blay1 = QHBoxLayout()
		blay1.setContentsMargins(0, 0, 0, 0)
		blay1.addStretch()
		blay1.addWidget(l1)
		blay1.addStretch()
		widg1.setLayout(blay1)

		widg2 = QWidget()
		lbl0 = QLabel('Hazelnut Tags', self)
		font = PyQt6.QtGui.QFont()
		font.setFamily("Arial")
		font.setBold(True)
		font.setPointSize(20)
		lbl0.setFont(font)
		blay2 = QHBoxLayout()
		blay2.setContentsMargins(0, 0, 0, 0)
		blay2.addStretch()
		blay2.addWidget(lbl0)
		blay2.addStretch()
		widg2.setLayout(blay2)

		widg3 = QWidget()
		lbl1 = QLabel('Version 0.0.8', self)
		blay3 = QHBoxLayout()
		blay3.setContentsMargins(0, 0, 0, 0)
		blay3.addStretch()
		blay3.addWidget(lbl1)
		blay3.addStretch()
		widg3.setLayout(blay3)

		widg4 = QWidget()
		lbl2 = QLabel('Thanks for your love🤟.', self)
		blay4 = QHBoxLayout()
		blay4.setContentsMargins(0, 0, 0, 0)
		blay4.addStretch()
		blay4.addWidget(lbl2)
		blay4.addStretch()
		widg4.setLayout(blay4)

		widg5 = QWidget()
		lbl3 = QLabel('感谢您的喜爱！', self)
		blay5 = QHBoxLayout()
		blay5.setContentsMargins(0, 0, 0, 0)
		blay5.addStretch()
		blay5.addWidget(lbl3)
		blay5.addStretch()
		widg5.setLayout(blay5)

		widg6 = QWidget()
		lbl4 = QLabel('Special thanks to ut.code(); of the University of Tokyo❤️', self)
		blay6 = QHBoxLayout()
		blay6.setContentsMargins(0, 0, 0, 0)
		blay6.addStretch()
		blay6.addWidget(lbl4)
		blay6.addStretch()
		widg6.setLayout(blay6)

		widg7 = QWidget()
		lbl5 = QLabel('This app is under the protection of  GPL-3.0 license', self)
		blay7 = QHBoxLayout()
		blay7.setContentsMargins(0, 0, 0, 0)
		blay7.addStretch()
		blay7.addWidget(lbl5)
		blay7.addStretch()
		widg7.setLayout(blay7)

		widg8 = QWidget()
		widg8.setFixedHeight(50)
		bt1 = WhiteButton('The Author')
		bt1.setMinimumWidth(100)
		bt1.clicked.connect(self.intro)
		bt2 = WhiteButton('Github Page')
		bt2.setMinimumWidth(100)
		bt2.clicked.connect(self.homepage)
		blay8 = QHBoxLayout()
		blay8.setContentsMargins(0, 0, 0, 0)
		blay8.addStretch()
		blay8.addWidget(bt1)
		blay8.addWidget(bt2)
		blay8.addStretch()
		widg8.setLayout(blay8)

		bt7 = WhiteButton('Buy me a cup of coffee☕')
		bt7.setMinimumWidth(215)
		bt7.clicked.connect(self.coffee)
		widg8_5 = QWidget()
		widg8_5.setFixedHeight(50)
		blay8_5 = QHBoxLayout()
		blay8_5.setContentsMargins(0, 0, 0, 0)
		blay8_5.addStretch()
		blay8_5.addWidget(bt7)
		blay8_5.addStretch()
		widg8_5.setLayout(blay8_5)

		widg9 = QWidget()
		widg9.setFixedHeight(70)
		bt3 = WhiteButton('🍪\n¥5')
		bt3.setMaximumHeight(50)
		bt3.setMinimumHeight(50)
		bt3.setMinimumWidth(50)
		bt3.clicked.connect(self.donate)
		bt4 = WhiteButton('🥪\n¥10')
		bt4.setMaximumHeight(50)
		bt4.setMinimumHeight(50)
		bt4.setMinimumWidth(50)
		bt4.clicked.connect(self.donate2)
		bt5 = WhiteButton('🍜\n¥20')
		bt5.setMaximumHeight(50)
		bt5.setMinimumHeight(50)
		bt5.setMinimumWidth(50)
		bt5.clicked.connect(self.donate3)
		bt6 = WhiteButton('🍕\n¥50')
		bt6.setMaximumHeight(50)
		bt6.setMinimumHeight(50)
		bt6.setMinimumWidth(50)
		bt6.clicked.connect(self.donate4)
		blay9 = QHBoxLayout()
		blay9.setContentsMargins(0, 0, 0, 0)
		blay9.addStretch()
		blay9.addWidget(bt3)
		blay9.addWidget(bt4)
		blay9.addWidget(bt5)
		blay9.addWidget(bt6)
		blay9.addStretch()
		widg9.setLayout(blay9)

		widg10 = QWidget()
		lbl6 = QLabel('© 2025 Yixiang SHEN. All rights reserved.', self)
		blay10 = QHBoxLayout()
		blay10.setContentsMargins(0, 0, 0, 0)
		blay10.addStretch()
		blay10.addWidget(lbl6)
		blay10.addStretch()
		widg10.setLayout(blay10)

		main_h_box = QVBoxLayout()
		main_h_box.setContentsMargins(20, 40, 20, 20)  # 重要，用来保证关闭按钮的位置。
		main_h_box.addSpacing(10)
		main_h_box.addWidget(widg1)
		main_h_box.addWidget(widg2)
		main_h_box.addSpacing(5)
		main_h_box.addWidget(widg3)
		main_h_box.addSpacing(5)
		main_h_box.addWidget(widg4)
		main_h_box.addSpacing(5)
		main_h_box.addWidget(widg5)
		main_h_box.addSpacing(5)
		main_h_box.addWidget(widg6)
		main_h_box.addSpacing(5)
		main_h_box.addWidget(widg7)
		main_h_box.addStretch()
		main_h_box.addWidget(widg8)
		main_h_box.addWidget(widg8_5)
		main_h_box.addWidget(widg9)
		main_h_box.addWidget(widg10)
		main_h_box.addStretch()
		main_h_box.addSpacing(10)
		self.setLayout(main_h_box)

	def intro(self):
		webbrowser.open('https://github.com/Ryan-the-hito/Ryan-the-hito')

	def homepage(self):
		webbrowser.open('https://github.com/Ryan-the-hito/Hazelnut')

	def coffee(self):
		webbrowser.open('https://www.buymeacoffee.com/ryanthehito')

	def donate(self):
		dlg = CustomDialog()
		dlg.exec()

	def donate2(self):
		dlg = CustomDialog2()
		dlg.exec()

	def donate3(self):
		dlg = CustomDialog3()
		dlg.exec()

	def donate4(self):
		dlg = CustomDialog4()
		dlg.exec()

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def activate(self):  # 设置窗口显示
		self.show()


class CustomDialog(QDialog):  # (About1)
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setUpMainWindow()
		self.setWindowTitle("Thank you for your support!")
		self.center()
		self.resize(440, 390)
		self.setFocus()
		self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

	def setUpMainWindow(self):
		widge_all = QWidget()
		l1 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'wechat5.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l1.setPixmap(png)  # 在l1里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l1.setMaximumSize(160, 240)
		l1.setScaledContents(True)
		l2 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'alipay5.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l2.setPixmap(png)  # 在l2里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l2.setMaximumSize(160, 240)
		l2.setScaledContents(True)
		bk = QHBoxLayout()
		bk.setContentsMargins(0, 0, 0, 0)
		bk.addWidget(l1)
		bk.addWidget(l2)
		widge_all.setLayout(bk)

		m1 = QLabel('Thank you for your kind support! 😊', self)
		m2 = QLabel('I will write more interesting apps! 🥳', self)

		widg_c = QWidget()
		widg_c.setFixedHeight(50)
		bt1 = WhiteButton('Thank you!')
		#bt1.setMaximumHeight(20)
		bt1.setMinimumWidth(100)
		bt1.clicked.connect(self.cancel)
		bt2 = WhiteButton('Neither one above? Buy me a coffee~')
		#bt2.setMaximumHeight(20)
		bt2.setMinimumWidth(260)
		bt2.clicked.connect(self.coffee)
		blay8 = QHBoxLayout()
		blay8.setContentsMargins(0, 0, 0, 0)
		blay8.addStretch()
		blay8.addWidget(bt1)
		blay8.addWidget(bt2)
		blay8.addStretch()
		widg_c.setLayout(blay8)

		self.layout = QVBoxLayout()
		self.layout.addWidget(widge_all)
		self.layout.addWidget(m1)
		self.layout.addWidget(m2)
		self.layout.addStretch()
		self.layout.addWidget(widg_c)
		self.layout.addStretch()
		self.setLayout(self.layout)

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def coffee(self):
		webbrowser.open('https://www.buymeacoffee.com/ryanthehito')

	def cancel(self):  # 设置取消键的功能
		self.close()


class CustomDialog2(QDialog):  # (About2)
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setUpMainWindow()
		self.setWindowTitle("Thank you for your support!")
		self.center()
		self.resize(440, 390)
		self.setFocus()
		self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

	def setUpMainWindow(self):
		widge_all = QWidget()
		l1 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'wechat10.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l1.setPixmap(png)  # 在l1里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l1.setMaximumSize(160, 240)
		l1.setScaledContents(True)
		l2 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'alipay10.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l2.setPixmap(png)  # 在l2里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l2.setMaximumSize(160, 240)
		l2.setScaledContents(True)
		bk = QHBoxLayout()
		bk.setContentsMargins(0, 0, 0, 0)
		bk.addWidget(l1)
		bk.addWidget(l2)
		widge_all.setLayout(bk)

		m1 = QLabel('Thank you for your kind support! 😊', self)
		m2 = QLabel('I will write more interesting apps! 🥳', self)

		widg_c = QWidget()
		widg_c.setFixedHeight(50)
		bt1 = WhiteButton('Thank you!')
		#bt1.setMaximumHeight(20)
		bt1.setMinimumWidth(100)
		bt1.clicked.connect(self.cancel)
		bt2 = WhiteButton('Neither one above? Buy me a coffee~')
		#bt2.setMaximumHeight(20)
		bt2.setMinimumWidth(260)
		bt2.clicked.connect(self.coffee)
		blay8 = QHBoxLayout()
		blay8.setContentsMargins(0, 0, 0, 0)
		blay8.addStretch()
		blay8.addWidget(bt1)
		blay8.addWidget(bt2)
		blay8.addStretch()
		widg_c.setLayout(blay8)

		self.layout = QVBoxLayout()
		self.layout.addWidget(widge_all)
		self.layout.addWidget(m1)
		self.layout.addWidget(m2)
		self.layout.addStretch()
		self.layout.addWidget(widg_c)
		self.layout.addStretch()
		self.setLayout(self.layout)

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def coffee(self):
		webbrowser.open('https://www.buymeacoffee.com/ryanthehito')

	def cancel(self):  # 设置取消键的功能
		self.close()


class CustomDialog3(QDialog):  # (About3)
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setUpMainWindow()
		self.setWindowTitle("Thank you for your support!")
		self.center()
		self.resize(440, 390)
		self.setFocus()
		self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

	def setUpMainWindow(self):
		widge_all = QWidget()
		l1 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'wechat20.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l1.setPixmap(png)  # 在l1里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l1.setMaximumSize(160, 240)
		l1.setScaledContents(True)
		l2 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'alipay20.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l2.setPixmap(png)  # 在l2里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l2.setMaximumSize(160, 240)
		l2.setScaledContents(True)
		bk = QHBoxLayout()
		bk.setContentsMargins(0, 0, 0, 0)
		bk.addWidget(l1)
		bk.addWidget(l2)
		widge_all.setLayout(bk)

		m1 = QLabel('Thank you for your kind support! 😊', self)
		m2 = QLabel('I will write more interesting apps! 🥳', self)

		widg_c = QWidget()
		widg_c.setFixedHeight(50)
		bt1 = WhiteButton('Thank you!')
		#bt1.setMaximumHeight(20)
		bt1.setMinimumWidth(100)
		bt1.clicked.connect(self.cancel)
		bt2 = WhiteButton('Neither one above? Buy me a coffee~')
		#bt2.setMaximumHeight(20)
		bt2.setMinimumWidth(260)
		bt2.clicked.connect(self.coffee)
		blay8 = QHBoxLayout()
		blay8.setContentsMargins(0, 0, 0, 0)
		blay8.addStretch()
		blay8.addWidget(bt1)
		blay8.addWidget(bt2)
		blay8.addStretch()
		widg_c.setLayout(blay8)

		self.layout = QVBoxLayout()
		self.layout.addWidget(widge_all)
		self.layout.addWidget(m1)
		self.layout.addWidget(m2)
		self.layout.addStretch()
		self.layout.addWidget(widg_c)
		self.layout.addStretch()
		self.setLayout(self.layout)

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def coffee(self):
		webbrowser.open('https://www.buymeacoffee.com/ryanthehito')

	def cancel(self):  # 设置取消键的功能
		self.close()


class CustomDialog4(QDialog):  # (About4)
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setUpMainWindow()
		self.setWindowTitle("Thank you for your support!")
		self.center()
		self.resize(440, 390)
		self.setFocus()
		self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

	def setUpMainWindow(self):
		widge_all = QWidget()
		l1 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'wechat50.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l1.setPixmap(png)  # 在l1里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l1.setMaximumSize(160, 240)
		l1.setScaledContents(True)
		l2 = QLabel(self)
		png = PyQt6.QtGui.QPixmap(BasePath + 'alipay50.png')  # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
		l2.setPixmap(png)  # 在l2里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
		l2.setMaximumSize(160, 240)
		l2.setScaledContents(True)
		bk = QHBoxLayout()
		bk.setContentsMargins(0, 0, 0, 0)
		bk.addWidget(l1)
		bk.addWidget(l2)
		widge_all.setLayout(bk)

		m1 = QLabel('Thank you for your kind support! 😊', self)
		m2 = QLabel('I will write more interesting apps! 🥳', self)

		widg_c = QWidget()
		widg_c.setFixedHeight(50)
		bt1 = WhiteButton('Thank you!')
		#bt1.setMaximumHeight(20)
		bt1.setMinimumWidth(100)
		bt1.clicked.connect(self.cancel)
		bt2 = WhiteButton('Neither one above? Buy me a coffee~')
		#bt2.setMaximumHeight(20)
		bt2.setMinimumWidth(260)
		bt2.clicked.connect(self.coffee)
		blay8 = QHBoxLayout()
		blay8.setContentsMargins(0, 0, 0, 0)
		blay8.addStretch()
		blay8.addWidget(bt1)
		blay8.addWidget(bt2)
		blay8.addStretch()
		widg_c.setLayout(blay8)

		self.layout = QVBoxLayout()
		self.layout.addWidget(widge_all)
		self.layout.addWidget(m1)
		self.layout.addWidget(m2)
		self.layout.addStretch()
		self.layout.addWidget(widg_c)
		self.layout.addStretch()
		self.setLayout(self.layout)

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def coffee(self):
		webbrowser.open('https://www.buymeacoffee.com/ryanthehito')

	def cancel(self):  # 设置取消键的功能
		self.close()


class window_update(QWidget):  # 增加更新页面（Check for Updates）
	def __init__(self):
		super().__init__()
		self.radius = 16  # 圆角半径，可按 macOS 15 或 26 设置为 16~26

		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.Window
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

		self.init_ui()

	def init_ui(self):
		self.setUpMainWindow()
		self.setFixedSize(280, 170)
		self.center()
		self.setFocus()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

		rect = QRectF(self.rect())
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)

		painter.setClipPath(path)
		bg_color = self.palette().color(QPalette.ColorRole.Window)
		painter.fillPath(path, bg_color)

	# 让无边框窗口可拖动
	def mousePressEvent(self, event):
		if event.button() == Qt.MouseButton.LeftButton:
			self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
			event.accept()

	def mouseMoveEvent(self, event):
		if event.buttons() == Qt.MouseButton.LeftButton:
			self.move(event.globalPosition().toPoint() - self.drag_pos)
			event.accept()

	def setUpMainWindow(self):
		# 添加关闭按钮（仿 macOS 左上角红色圆点）
		# self.close_button = QPushButton(self)
		# self.close_button.setFixedSize(12, 12)
		# self.close_button.move(10, 10)
		# self.close_button.setStyleSheet("""
		# 	QPushButton {
		# 		background-color: #FF5F57;
		# 		border-radius: 6px;
		# 		border: none;
		# 	}
		# 	QPushButton:hover {
		# 		background-color: #BF4943;
		# 	}
		# """)
		# self.close_button.clicked.connect(self.close)
		self.close_button = MacWindowButton("#FF605C", "x", self)
		self.close_button.move(10, 10)
		self.close_button.clicked.connect(self.close)

		widg5 = QWidget()
		lbl1 = QLabel('Latest version:', self)
		self.lbl2 = QLabel('', self)
		blay5 = QHBoxLayout()
		blay5.setContentsMargins(0, 0, 0, 0)
		# blay5.addStretch()
		blay5.addWidget(lbl1)
		blay5.addWidget(self.lbl2)
		blay5.addStretch()
		widg5.setLayout(blay5)

		widg3 = QWidget()
		self.lbl = QLabel('Current version: v0.0.8', self)
		blay3 = QHBoxLayout()
		blay3.setContentsMargins(0, 0, 0, 0)
		# blay3.addStretch()
		blay3.addWidget(self.lbl)
		blay3.addStretch()
		widg3.setLayout(blay3)

		widg4 = QWidget()
		widg4.setFixedHeight(50)
		lbl0 = QLabel('Check release:', self)
		bt1 = WhiteButton('Github')
		bt1.clicked.connect(self.upd)
		blay4 = QHBoxLayout()
		blay4.setContentsMargins(0, 0, 0, 0)
		# blay4.addStretch()
		blay4.addWidget(lbl0)
		blay4.addWidget(bt1)
		blay4.addStretch()
		widg4.setLayout(blay4)

		main_h_box = QVBoxLayout()
		main_h_box.setContentsMargins(20, 40, 20, 20)  # 重要，用来保证关闭按钮的位置。
		main_h_box.addWidget(widg5)
		main_h_box.addSpacing(10)
		main_h_box.addWidget(widg3)
		main_h_box.addWidget(widg4)
		self.setLayout(main_h_box)

	def upd(self):
		webbrowser.open('https://github.com/Ryan-the-hito/Hazelnut/releases')

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def activate(self):  # 设置窗口显示
		self.show()
		self.checkupdate()

	def checkupdate(self):
		targetURL = 'https://github.com/Ryan-the-hito/Hazelnut/releases'
		try:
			# Fetch the HTML content from the URL
			urllib3.disable_warnings()
			logging.captureWarnings(True)
			s = requests.session()
			s.keep_alive = False  # 关闭多余连接
			response = s.get(targetURL, verify=False)
			response.encoding = 'utf-8'
			html_content = response.text
			# Parse the HTML using BeautifulSoup
			soup = BeautifulSoup(html_content, "html.parser")
			# Remove all images from the parsed HTML
			for img in soup.find_all("img"):
				img.decompose()
			# Convert the parsed HTML to plain text using html2text
			text_maker = html2text.HTML2Text()
			text_maker.ignore_links = True
			text_maker.ignore_images = True
			plain_text = text_maker.handle(str(soup))
			# Convert the plain text to UTF-8
			plain_text_utf8 = plain_text.encode(response.encoding).decode("utf-8")

			for i in range(10):
				plain_text_utf8 = plain_text_utf8.replace('\n\n\n\n', '\n\n')
				plain_text_utf8 = plain_text_utf8.replace('\n\n\n', '\n\n')
				plain_text_utf8 = plain_text_utf8.replace('   ', ' ')
				plain_text_utf8 = plain_text_utf8.replace('  ', ' ')

			pattern2 = re.compile(r'(v\d+\.\d+\.\d+)\sLatest')
			result = pattern2.findall(plain_text_utf8)
			result = ''.join(result)
			nowversion = self.lbl.text().replace('Current Version: ', '')
			if result == nowversion:
				alertupdate = result + '. You are up to date!'
				self.lbl2.setText(alertupdate)
				self.lbl2.adjustSize()
			else:
				alertupdate = result + ' is ready!'
				self.lbl2.setText(alertupdate)
				self.lbl2.adjustSize()
		except:
			alertupdate = 'No Intrenet'
			self.lbl2.setText(alertupdate)
			self.lbl2.adjustSize()


class Slide(QWidget): # guide page
	def __init__(self, text, color, image_path=None, gif_path=None, acc_button=False, font=24, show_button=False, acc_button2=False):
		super().__init__()
		self.setStyleSheet(f"background-color: {color};border-radius:4px;")
		w3 = QWidget()
		layout = QVBoxLayout()
		layout.setSpacing(20)  # 设置控件间距为 0
		layout.setContentsMargins(0, 0, 0, 0)  # 设置边距为 0

		# 图片部分
		if image_path:
			self.image_label = QLabel()
			pixmap = QPixmap(image_path).scaledToHeight(300)
			self.image_label.setPixmap(pixmap)
			self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
			layout.addWidget(self.image_label)

		# Gif part
		if gif_path:
			self.gif_label = QLabel()
			#self.gif_label.setFixedWidth(250)
			movie = QMovie(gif_path)
			movie.setScaledSize(QSize(922, 264))
			self.gif_label.setMovie(movie)
			#movie.setSpeed(50)
			movie.start()  # 一定要启动！
			self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
			layout.addWidget(self.gif_label)
			# 设置定时器：3 秒后隐藏图片
			QTimer.singleShot(5200, self.hide_image)

		# 按钮（仅当 show_button=True 时）
		if show_button:
			button_layout = QHBoxLayout()

			button_layout.addStretch()

			btn1 = QPushButton("Documentation📑")
			btn1.setFixedWidth(200)
			btn1.clicked.connect(self.handle_feature_a)
			button_layout.addWidget(btn1)
			btn1.setStyleSheet('''
				QPushButton{
				border: 1px outset grey;
				background-color: #FFFFFF;
				border-radius: 4px;
				padding: 1px;
				color: #000000
			}
				QPushButton:pressed{
					border: 1px outset grey;
					background-color: #0085FF;
					border-radius: 4px;
					padding: 1px;
					color: #FFFFFF
			}''')

			button_layout.addStretch()

			btn2 = QPushButton("Tip me!❤️")
			btn2.setFixedWidth(200)
			btn2.clicked.connect(self.handle_feature_b)
			button_layout.addWidget(btn2)
			btn2.setStyleSheet('''
				QPushButton{
				border: 1px outset grey;
				background-color: #FFFFFF;
				border-radius: 4px;
				padding: 1px;
				color: #000000
			}
				QPushButton:pressed{
					border: 1px outset grey;
					background-color: #0085FF;
					border-radius: 4px;
					padding: 1px;
					color: #FFFFFF
			}''')

			button_layout.addStretch()

			btn3 = QPushButton("Bugs? Email me💌")
			btn3.setFixedWidth(200)
			btn3.clicked.connect(self.handle_feature_c)
			button_layout.addWidget(btn3)
			btn3.setStyleSheet('''
				QPushButton{
				border: 1px outset grey;
				background-color: #FFFFFF;
				border-radius: 4px;
				padding: 1px;
				color: #000000
			}
				QPushButton:pressed{
					border: 1px outset grey;
					background-color: #0085FF;
					border-radius: 4px;
					padding: 1px;
					color: #FFFFFF
			}''')

			button_layout.addStretch()

			layout.addLayout(button_layout)

		# 按钮（仅当 acc_button=True 时）
		if acc_button:
			btn4 = QPushButton("Open Accessibility")
			btn4.setFixedWidth(200)
			btn4.clicked.connect(self.handle_feature_d)
			btn4.setStyleSheet('''
				QPushButton{
				border: 1px outset grey;
				background-color: #FFFFFF;
				border-radius: 4px;
				padding: 1px;
				color: #000000
			}
				QPushButton:pressed{
					border: 1px outset grey;
					background-color: #0085FF;
					border-radius: 4px;
					padding: 1px;
					color: #FFFFFF
			}''')
			acc_layout = QHBoxLayout()
			acc_layout.setContentsMargins(0, 0, 0, 0)
			acc_layout.addStretch()
			acc_layout.addWidget(btn4)
			acc_layout.addStretch()
			layout.addLayout(acc_layout)

		# acc2
		if acc_button2:
			btn5 = QPushButton("Open Input Monitoring")
			btn5.setFixedWidth(200)
			btn5.clicked.connect(self.handle_feature_e)
			btn5.setStyleSheet('''
				QPushButton{
				border: 1px outset grey;
				background-color: #FFFFFF;
				border-radius: 4px;
				padding: 1px;
				color: #000000
			}
				QPushButton:pressed{
					border: 1px outset grey;
					background-color: #0085FF;
					border-radius: 4px;
					padding: 1px;
					color: #FFFFFF
			}''')
			acc_layout2 = QHBoxLayout()
			acc_layout2.setContentsMargins(0, 0, 0, 0)
			acc_layout2.addStretch()
			acc_layout2.addWidget(btn5)
			acc_layout2.addStretch()
			layout.addLayout(acc_layout2)

		# 文字部分
		self.label = QLabel(text)
		self.label.setStyleSheet(f"font-size: {font}px; color: black; font: bold Helvetica;")
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		if gif_path:
			self.label.setVisible(False)

			# 添加不透明度效果
			self.opacity_effect = QGraphicsOpacityEffect()
			self.label.setGraphicsEffect(self.opacity_effect)
			self.opacity_effect.setOpacity(0)  # 初始为完全透明

			# 创建动画
			self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
			self.animation.setDuration(2000)  # 动画时长：2000 毫秒
			self.animation.setStartValue(0)
			self.animation.setEndValue(1)
			self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

		#layout.addStretch()
		layout.addWidget(self.label)

		w3.setLayout(layout)
		w3.setStyleSheet('''
			border: 1px solid white;
			background: white;
			border-radius: 9px;
		''')

		blayend = QHBoxLayout()
		blayend.setContentsMargins(0, 0, 0, 0)
		blayend.addWidget(w3)
		self.setLayout(blayend)

	def hide_image(self):
		if self.gif_label:
			self.gif_label.hide()
			self.label.setVisible(True)# 或者 self.image_label.deleteLater() 完全移除
			self.animation.start()

	def handle_feature_a(self):
		webbrowser.open('https://github.com/Ryan-the-hito/Shameplant')

	def handle_feature_b(self):
		w1.show()


	def handle_feature_c(self):
		to = "sweeter.02.implant@icloud.com"
		subject = "[Feedback-Shameplant]"
		body = "\n\n---\nShameplant v1.0.6"
		# 对 subject 和 body 进行 URL 编码
		subject_encoded = urllib.parse.quote(subject)
		body_encoded = urllib.parse.quote(body)

		# 构造 mailto 链接
		mailto_link = f"mailto:{to}?subject={subject_encoded}&body={body_encoded}"

		# 打开默认邮件客户端
		QDesktopServices.openUrl(QUrl(mailto_link))

	def handle_feature_d(self):
		QDesktopServices.openUrl(QUrl("x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"))

	def handle_feature_e(self):
		toggle_dock_script = '''
			tell application "System Settings"
				quit
			end tell
			delay 1
			tell application "System Settings"
				activate
			end tell
			delay 1
			tell application "System Events"
				tell process "System Settings"
					click menu item "Privacy & Security" of menu "View" of menu bar 1
					delay 1
					click button 8 of group 4 of scroll area 1 of group 1 of group 2 of splitter group 1 of group 1 of window "Privacy & Security" of application process "System Settings" of application "System Events"
				end tell
			end tell
		'''
		# 运行AppleScript
		subprocess.run(["osascript", "-e", toggle_dock_script])


class SliderWindow(QWidget): # inside pages of guidance
	def __init__(self):
		super().__init__()
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
		self.resize(960, 550)

		self.stack = QStackedWidget()
		gifpath = BasePath + 'dock9.gif'
		imagepath1 = BasePath + 'access1.png'
		imagepath2 = BasePath + 'access2.png'
		imagepath3 = BasePath + 'access3.png'
		imagepath4 = BasePath + 'promote.png'
		self.slides = [
			Slide("Welcome to Shameplant!", "white", None, f'{gifpath}', False, 50),
			Slide("Allow automation", "white", f'{imagepath1}', None, False),
			Slide("Set up Accessibility", "white", f'{imagepath2}', None, True),
			Slide("Set up Input Monitoring", "white", f'{imagepath3}', None, False, 24, False, True),
			Slide("For more apps and info...", "white", f'{imagepath4}', None, False, 24, True),
			Slide("Thank you for using Shameplant! \n Let's get started!", "white", None, None, False, 45),
		]

		for slide in self.slides:
			self.stack.addWidget(slide)

		# 页码圆点
		self.dots = [QLabel("●") for _ in self.slides]
		for dot in self.dots:
			dot.setStyleSheet("font-size: 16px; color: lightgray;")
		self.update_dots(0)

		dots_layout = QHBoxLayout()
		dots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
		for dot in self.dots:
			dots_layout.addWidget(dot)

		# 翻页按钮
		self.prev_btn = QPushButton("←")
		self.prev_btn.setFixedWidth(100)
		self.next_btn = QPushButton("→")
		self.next_btn.setFixedWidth(100)
		self.prev_btn.clicked.connect(self.go_prev)
		self.next_btn.clicked.connect(self.go_next)
		self.prev_btn.setStyleSheet('''
			QPushButton{
			border: 1px outset grey;
			background-color: #FFFFFF;
			border-radius: 4px;
			padding: 1px;
			color: #000000
		}
			QPushButton:pressed{
				border: 1px outset grey;
				background-color: #0085FF;
				border-radius: 4px;
				padding: 1px;
				color: #FFFFFF
		}''')
		self.next_btn.setStyleSheet('''
			QPushButton{
			border: 1px outset grey;
			background-color: #FFFFFF;
			border-radius: 4px;
			padding: 1px;
			color: #000000
		}
			QPushButton:pressed{
				border: 1px outset grey;
				background-color: #0085FF;
				border-radius: 4px;
				padding: 1px;
				color: #FFFFFF
		}''')

		btn_layout = QHBoxLayout()
		btn_layout.addStretch()
		btn_layout.addWidget(self.prev_btn)
		btn_layout.addStretch()
		btn_layout.addWidget(self.next_btn)
		btn_layout.addStretch()

		w3 = QWidget()
		blay3 = QVBoxLayout()
		blay3.setContentsMargins(0, 0, 0, 0)
		blay3.addStretch()
		blay3.addWidget(self.stack)
		blay3.addLayout(dots_layout)
		blay3.addLayout(btn_layout)
		blay3.addStretch()
		w3.setLayout(blay3)
		w3.setStyleSheet('''
			border: 1px solid white;
			background: white;
			border-radius: 9px;
		''')

		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(w3)
		self.setLayout(layout)

		self.current_index = 0

	def update_dots(self, index):
		for i, dot in enumerate(self.dots):
			color = "black" if i == index else "lightgray"
			dot.setStyleSheet(f"font-size: 16px; color: {color};")

	def slide_to(self, new_index):
		if new_index < 0 or new_index >= self.stack.count():
			home_dir = base_dir
			tarname1 = "ShameplantAppPath"
			fulldir1 = os.path.join(home_dir, tarname1)
			if not os.path.exists(fulldir1):
				os.mkdir(fulldir1)
			tarname8 = "New.txt"
			self.fulldir8 = os.path.join(fulldir1, tarname8)
			if not os.path.exists(self.fulldir8):
				with open(self.fulldir8, 'a', encoding='utf-8') as f0:
					f0.write('0')
			with open(self.fulldir8, 'w', encoding='utf-8') as f0:
				f0.write('1')
			self.close()
		else:
			current_widget = self.stack.currentWidget()
			next_widget = self.stack.widget(new_index)

			direction = -1 if new_index > self.current_index else 1
			offset = self.stack.width() * direction

			next_widget.setGeometry(self.stack.geometry().translated(offset, 0))
			next_widget.show()

			anim_current = QPropertyAnimation(current_widget, b"geometry")
			anim_next = QPropertyAnimation(next_widget, b"geometry")

			rect = self.stack.geometry()

			anim_current.setDuration(300)
			anim_current.setStartValue(rect)
			anim_current.setEndValue(rect.translated(-offset, 0))

			anim_next.setDuration(300)
			anim_next.setStartValue(rect.translated(offset, 0))
			anim_next.setEndValue(rect)

			anim_current.setEasingCurve(QEasingCurve.Type.OutCubic)
			anim_next.setEasingCurve(QEasingCurve.Type.OutCubic)

			anim_current.start()
			anim_next.start()

			self.stack.setCurrentIndex(new_index)
			self.current_index = new_index
			self.update_dots(new_index)

	def go_next(self):
		self.slide_to(self.current_index + 1)

	def go_prev(self):
		self.slide_to(self.current_index - 1)


class GlassButton(QPushButton):
	singleClicked = pyqtSignal(str)
	rightClicked = pyqtSignal(str)

	def __init__(self, text="Glass Button", radius=30, bg_color=(255, 255, 255, 20), shadow_color=(0, 0, 0, 80), highlight_color=(255, 255, 255, 80), parent=None):
		super().__init__(text, parent)
		self.radius = radius
		self.bg_color = QColor(*bg_color)
		self.default_bg_color = QColor(*bg_color)
		self.deep_bg_color = QColor(
			max(0, self.bg_color.red() - 40),
			max(0, self.bg_color.green() - 40),
			max(0, self.bg_color.blue() - 40),
			min(255, self.bg_color.alpha() + 60)
		)
		self.shadow_color = QColor(*shadow_color)
		self.highlight_color = QColor(*highlight_color)
		self.setStyleSheet("""
			background-color: transparent;
			border: none;
			color: white;
			font-size: 16px;
			padding: 8px 24px;
		""")
		if not is_macos_16_or_higher():
			self.outer_shadow = QGraphicsDropShadowEffect(self)
			self.outer_shadow.setBlurRadius(12)
			self.outer_shadow.setColor(self.shadow_color)
			self.outer_shadow.setOffset(0, 6)
			self.setGraphicsEffect(self.outer_shadow)
		self.pressed_state = False
		self.blur_bg = None
		self.is_selected = False

	def setRadius(self, radius):
		self.radius = radius
		self.update()

	def enterEvent(self, event):
		self.animateScale(1.15)
		super().enterEvent(event)

	def leaveEvent(self, event):
		self.animateScale(1.0)
		super().leaveEvent(event)

	def animateScale(self, scale_factor):
		if not hasattr(self, "_original_geometry"):
			self._original_geometry = self.geometry()
		orig = self._original_geometry
		w, h = orig.width(), orig.height()
		cx, cy = orig.center().x(), orig.center().y()
		new_w, new_h = int(w * scale_factor), int(h * scale_factor)
		new_x = cx - new_w // 2
		new_y = cy - new_h // 2

		if hasattr(self, 'anim') and self.anim is not None:
			self.anim.stop()
			self.anim.deleteLater()
		self.anim = QPropertyAnimation(self, b"geometry")
		self.anim.setDuration(150)
		self.anim.setStartValue(self.geometry())
		self.anim.setEndValue(QRect(new_x, new_y, new_w, new_h))
		self.anim.finished.connect(self.cleanup_anim)
		self.anim.start()

	def cleanup_anim(self):
		if hasattr(self, 'anim') and self.anim is not None:
			self.anim.deleteLater()
			self.anim = None

	def isInRoundRect(self, pos):
		rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)
		return path.contains(pos)

	def mousePressEvent(self, event: QMouseEvent):
		if self.isInRoundRect(event.position()):
			if event.button() == Qt.MouseButton.LeftButton:
				# 对于"Clear Selection"按钮，始终发射信号
				if self.text() == "Clear" or self.text() == "Tag!" or self.text() == "Close":
					self.singleClicked.emit(self.text())
				elif not self.is_selected:
					self.setSelected(True)
					self.singleClicked.emit(self.text())
			elif event.button() == Qt.MouseButton.RightButton:
				if self.is_selected:
					self.setSelected(False)
					self.rightClicked.emit(self.text())
		super().mousePressEvent(event)

	def mouseReleaseEvent(self, event: QMouseEvent):
		if self.isInRoundRect(event.position()):
			self.pressed_state = False
			# 只在左键释放时处理
			if event.button() == Qt.MouseButton.LeftButton:
				if self.text() in ("Clear", "Tag!", "Close"):
					self.setSelected(False)
			self.update()
		super().mouseReleaseEvent(event)

	def setSelected(self, selected: bool):
		self.is_selected = selected
		self.bg_color = self.deep_bg_color if selected else self.default_bg_color
		self.update()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
		rect = QRectF(0, 0, self.width(), self.height()).adjusted(2, 2, -2, -2)
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)
		center_y = rect.center().y()

		painter.setBrush(QBrush(self.bg_color))
		painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
		painter.drawPath(path)
		if not is_macos_16_or_higher():
			if self.blur_bg is None or self.blur_bg.size() != self.size():
				tmp_img = QImage(self.size(), QImage.Format.Format_ARGB32)
				tmp_img.fill(Qt.GlobalColor.transparent)
				tmp_painter = QPainter(tmp_img)
				tmp_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
				tmp_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
				tmp_painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
				tmp_painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
				tmp_painter.drawPath(path)
				tmp_painter.end()
				pil_img = Image.fromqimage(tmp_img)
				pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=2))
				self.blur_bg = QImage(
					pil_img.tobytes("raw", "RGBA"),
					pil_img.width,
					pil_img.height,
					QImage.Format.Format_ARGB32
				)
			painter.drawImage(0, 0, self.blur_bg)

		if not self.pressed_state:
			path = QPainterPath()
			path.moveTo(rect.left()+self.radius, rect.bottom())
			path.lineTo(rect.right()-self.radius, rect.bottom())
			path.arcTo(rect.right() - 2 * self.radius, rect.bottom() - 2 * self.radius,
					   2 * self.radius, 2 * self.radius, 270, 90)
			path.lineTo(rect.right(), center_y)
			path.lineTo(rect.left(), center_y)
			path.arcTo(rect.left(), rect.bottom() - 2 * self.radius,
					   2 * self.radius, 2 * self.radius, 180, 90)
			path.closeSubpath()
			gradient = QLinearGradient(rect.left(), rect.bottom(),
									   rect.left(), center_y)
			gradient.setColorAt(0, self.highlight_color)
			gradient.setColorAt(1, QColor(255, 255, 255, 0))
			painter.setPen(QPen(QBrush(gradient), 2))
			painter.setBrush(Qt.BrushStyle.NoBrush)
			painter.drawPath(path)

		painter.setPen(QPen(QColor(255, 255, 255, 255)))
		painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class DropGlassButton(QPushButton):
	singleClicked = pyqtSignal(str)
	rightClicked = pyqtSignal(str)
	pathChanged = pyqtSignal(list)

	def __init__(self, text="Glass Button", radius=50, bg_color=(255, 255, 255, 20), shadow_color=(0, 0, 0, 80), highlight_color=(255, 255, 255, 80), parent=None):
		super().__init__(text, parent)
		self.setAcceptDrops(True)
		self.file_dropped_callback = None
		self.path = None

		self.radius = radius
		self.bg_color = QColor(*bg_color)
		self.default_bg_color = QColor(*bg_color)
		self.deep_bg_color = QColor(
			max(0, self.bg_color.red() - 40),
			max(0, self.bg_color.green() - 40),
			max(0, self.bg_color.blue() - 40),
			min(255, self.bg_color.alpha() + 60)
		)
		self.shadow_color = QColor(*shadow_color)
		self.highlight_color = QColor(*highlight_color)
		self.setStyleSheet("""
			background-color: transparent;
			border: none;
			color: white;
			font-size: 16px;
			padding: 8px 24px;
		""")
		if not is_macos_16_or_higher():
			self.outer_shadow = QGraphicsDropShadowEffect(self)
			self.outer_shadow.setBlurRadius(12)
			self.outer_shadow.setColor(self.shadow_color)
			self.outer_shadow.setOffset(0, 6)
			self.setGraphicsEffect(self.outer_shadow)
		self.pressed_state = False
		self.blur_bg = None
		self.is_selected = False

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
		else:
			event.ignore()

	def dropEvent(self, event):
		urls = event.mimeData().urls()
		if urls:
			self.path = [url.toLocalFile() for url in urls]
			#print("拖拽路径:", self.path)
			#self.path = urls[0].toLocalFile()
			self.pathChanged.emit(self.path)  # 发射信号
			main_window = self.window()  # 获取顶层窗口
			if hasattr(main_window, "circle_widget"):
				main_window.circle_widget.start_show_buttons()
			if hasattr(main_window, "hori_btn_window"):
				main_window.hori_btn_window.setVisible(True)
				main_window.hori_btn_window.show()
			if hasattr(main_window, "close_button"):
				main_window.close_button.setVisible(True)
			if hasattr(main_window, "check_button"):
				main_window.check_button.setVisible(True)
			if self.file_dropped_callback:
				self.file_dropped_callback()

	def setRadius(self, radius):
		self.radius = radius
		self.update()

	def enterEvent(self, event):
		self.animateScale(1.15)
		super().enterEvent(event)

	def leaveEvent(self, event):
		self.animateScale(1.0)
		super().leaveEvent(event)

	def animateScale(self, scale_factor):
		if not hasattr(self, "_original_geometry"):
			self._original_geometry = self.geometry()
		orig = self._original_geometry
		w, h = orig.width(), orig.height()
		cx, cy = orig.center().x(), orig.center().y()
		new_w, new_h = int(w * scale_factor), int(h * scale_factor)
		new_x = cx - new_w // 2
		new_y = cy - new_h // 2

		if hasattr(self, 'anim') and self.anim is not None:
			self.anim.stop()
			self.anim.deleteLater()
		self.anim = QPropertyAnimation(self, b"geometry")
		self.anim.setDuration(150)
		self.anim.setStartValue(self.geometry())
		self.anim.setEndValue(QRect(new_x, new_y, new_w, new_h))
		self.anim.finished.connect(self.cleanup_anim)
		self.anim.start()

	def cleanup_anim(self):
		if hasattr(self, 'anim') and self.anim is not None:
			self.anim.deleteLater()
			self.anim = None

	def isInRoundRect(self, pos):
		rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)
		return path.contains(pos)

	def mousePressEvent(self, event: QMouseEvent):
		if self.isInRoundRect(event.position()):
			if event.button() == Qt.MouseButton.LeftButton:
				# 对于"Clear Selection"按钮，始终发射信号
				if self.text() == "Clear":
					self.singleClicked.emit(self.text())
				elif not self.is_selected and self.text() != '+':
					self.setSelected(True)
					self.singleClicked.emit(self.text())
			elif event.button() == Qt.MouseButton.RightButton:
				if self.is_selected:
					self.setSelected(False)
					self.rightClicked.emit(self.text())
		super().mousePressEvent(event)

	def setSelected(self, selected: bool):
		self.is_selected = selected
		self.bg_color = self.deep_bg_color if selected else self.default_bg_color
		self.update()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
		rect = QRectF(0, 0, self.width(), self.height()).adjusted(2, 2, -2, -2)
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)
		center_y = rect.center().y()

		painter.setBrush(QBrush(self.bg_color))
		painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
		painter.drawPath(path)
		if not is_macos_16_or_higher():
			if self.blur_bg is None or self.blur_bg.size() != self.size():
				tmp_img = QImage(self.size(), QImage.Format.Format_ARGB32)
				tmp_img.fill(Qt.GlobalColor.transparent)
				tmp_painter = QPainter(tmp_img)
				tmp_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
				tmp_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
				tmp_painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
				tmp_painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
				tmp_painter.drawPath(path)
				tmp_painter.end()
				pil_img = Image.fromqimage(tmp_img)
				pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=2))
				self.blur_bg = QImage(
					pil_img.tobytes("raw", "RGBA"),
					pil_img.width,
					pil_img.height,
					QImage.Format.Format_ARGB32
				)
			painter.drawImage(0, 0, self.blur_bg)

		if not self.pressed_state:
			path = QPainterPath()
			path.moveTo(rect.left()+self.radius, rect.bottom())
			path.lineTo(rect.right()-self.radius, rect.bottom())
			path.arcTo(rect.right() - 2 * self.radius, rect.bottom() - 2 * self.radius,
					   2 * self.radius, 2 * self.radius, 270, 90)
			path.lineTo(rect.right(), center_y)
			path.lineTo(rect.left(), center_y)
			path.arcTo(rect.left(), rect.bottom() - 2 * self.radius,
					   2 * self.radius, 2 * self.radius, 180, 90)
			path.closeSubpath()
			gradient = QLinearGradient(rect.left(), rect.bottom(),
									   rect.left(), center_y)
			gradient.setColorAt(0, self.highlight_color)
			gradient.setColorAt(1, QColor(255, 255, 255, 0))
			painter.setPen(QPen(QBrush(gradient), 2))
			painter.setBrush(Qt.BrushStyle.NoBrush)
			painter.drawPath(path)

		painter.setPen(QPen(QColor(255, 255, 255, 255)))
		painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class CircleButtonWidget(QWidget):
	buttonSelected = pyqtSignal(str)
	buttonDeselected = pyqtSignal(str)
	clearAll = pyqtSignal()
	def __init__(self, button_names, bg_colors=None, shadow_colors=None, highlight_colors=None, parent=None):
		super().__init__(parent)
		self.button_names = button_names
		self.buttons = []
		#self.selected_captions = []
		# 创建所有按钮，并设置为圆形
		for i, name in enumerate(button_names):
			bg = bg_colors[i] if bg_colors else (255, 255, 255, 20)
			shadow = shadow_colors[i] if shadow_colors else (0, 0, 0, 80)
			highlight = highlight_colors[i] if highlight_colors else (255, 255, 255, 80)
			btn = GlassButton(name, bg_color=bg, shadow_color=shadow, highlight_color=highlight)
			btn.setFixedSize(60, 60)
			#btn.clicked.connect(lambda checked, n=name: self.on_button_clicked(n))
			if name == "Clear":
				btn.singleClicked.connect(self.clear_selection)
			else:
				btn.singleClicked.connect(lambda caption, n=name: self.buttonSelected.emit(n))
				btn.rightClicked.connect(lambda caption, n=name: self.buttonDeselected.emit(n))
			self.buttons.append(btn)
			btn.setParent(self)
			btn.setVisible(False)  # 初始隐藏
		# 初始布局
		self.updatePositions()
		#self.show_buttons_sequentially()  # 渐次显示

	def show_buttons_sequentially(self, idx=0):
		if idx < len(self.buttons):
			self.buttons[idx].setVisible(True)
			QTimer.singleShot(25, lambda: self.show_buttons_sequentially(idx + 1))  # 200ms 间隔

	def start_show_buttons(self):
		self.show_buttons_sequentially()

	# def on_button_single_clicked(self, caption):
	#	 if caption not in self.selected_captions:
	#		 self.selected_captions.append(caption)
	#	 print("Selected:", self.selected_captions)
	#
	# def on_button_right_clicked(self, caption):
	#	 if caption in self.selected_captions:
	#		 self.selected_captions.remove(caption)
	#	 print("Selected:", self.selected_captions)

	def clear_selection(self, _=None):
		for btn in self.buttons:
			btn.setSelected(False)
		self.clearAll.emit()
		#print("Selected:", self.selected_captions)

	def hide_all_buttons(self):
		for btn in self.buttons:
			btn.setVisible(False)

	def updatePositions(self):
		center = QPoint(self.width() // 2, self.height() // 2)
		radius = min(self.width(), self.height()) // 3
		angle_step = 2 * math.pi / len(self.buttons)
		for i, btn in enumerate(self.buttons):
			angle = angle_step * i
			x = center.x() + radius * math.cos(angle) - btn.width() // 2
			y = center.y() + radius * math.sin(angle) - btn.height() // 2
			btn.move(int(x), int(y))

	def resizeEvent(self, event):
		self.updatePositions()
		super().resizeEvent(event)


class DragMonitor(QThread):
	trigger_signal = pyqtSignal()  # 新增信号
	def __init__(self, on_trigger=None):
		super().__init__()
		home_dir = base_dir
		tarname1 = "HazelnutAppPath"
		fulldir1 = os.path.join(home_dir, tarname1)
		if not os.path.exists(fulldir1):
			os.mkdir(fulldir1)
		tarname2 = "Allow.txt"
		self.fulldir3 = os.path.join(fulldir1, tarname2)
		if not os.path.exists(self.fulldir3):
			with open(self.fulldir3, 'a', encoding='utf-8') as f0:
				f0.write('Finder\n')

		self.on_trigger = on_trigger
		self.dragging = False
		self.last_pos = None
		self.last_direction = None
		self.direction_changes = 0
		self.listener = None
		self._running = False

		# 只读取一次允许应用列表
		with codecs.open(self.fulldir3, 'r', encoding='utf-8') as f:
			self.allowed_apps = [line.strip() for line in f if line.strip()]

		self.trigger_signal.connect(self.handle_trigger)

	def handle_trigger(self):
		if self.on_trigger:
			self.on_trigger()

	def run(self):
		self._running = True
		with mouse.Listener(
				on_move=self.on_move,
				on_click=self.on_click
		) as self.listener:
			self.listener.join()

	# def startIt(self):
	# 	if self._running:
	# 		return
	# 	self.listener = mouse.Listener(
	# 		on_move=self.on_move,
	# 		on_click=self.on_click
	# 	)
	# 	self.listener.start()
	# 	self._running = True

	def stop(self):
		self._running = False
		if self.listener is not None:
			self.listener.stop()
			self.listener = None

	# def stop(self):
	# 	if self.listener is not None:
	# 		self.listener.stop()
	# 		self.listener.join()  # 等待线程完全退出
	# 		self.listener = None
	# 	self._running = False

	# def reset_state(self):
	# 	self.dragging = False
	# 	self.last_pos = None
	# 	self.last_direction = None
	# 	self.direction_changes = 0

	def on_click(self, x, y, button, pressed):
		if button.name == "left":
			self.dragging = pressed
			if not pressed:
				self.last_pos = None
				self.last_direction = None
				self.direction_changes = 0

	def on_move(self, x, y):
		if not self.dragging:
			return

		active_app = NSWorkspace.sharedWorkspace().activeApplication()
		app_name = active_app['NSApplicationName']

		if app_name == "loginwindow":
			return

		# ALLOWED_APPS = codecs.open(self.fulldir3, 'r', encoding='utf-8').read()
		# ALLOWED_APPS_LIST = ALLOWED_APPS.split('\n')
		# while '' in ALLOWED_APPS_LIST:
		# 	ALLOWED_APPS_LIST.remove('')

		# if app_name not in ALLOWED_APPS_LIST:
		# 	return

		if app_name not in self.allowed_apps:
			return

		if self.last_pos is None:
			self.last_pos = (x, y)
			return

		dx = x - self.last_pos[0]
		dy = y - self.last_pos[1]

		if abs(dx) > abs(dy):
			direction = 'right' if dx > 0 else 'left'
		elif abs(dy) > 2:
			direction = 'down' if dy > 0 else 'up'
		else:
			return

		if self.last_direction and direction != self.last_direction:
			self.direction_changes += 1
			#print(f"方向改变为: {direction}, 累积: {self.direction_changes}")
			if self.direction_changes >= 3:
				self.trigger_signal.emit()  # 用信号通知主线程
				self.direction_changes = 0

		self.last_direction = direction
		self.last_pos = (x, y)


class OuterWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.WindowStaysOnTopHint
		)
		self.setFixedSize(400, 80)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
		rect = QRectF(0, 0, self.width(), self.height())
		path = QPainterPath()
		path.addRoundedRect(rect, 16, 16)
		bg_color = self.palette().color(QPalette.ColorRole.Window)
		if is_macos_16_or_higher():
			bg_color.setAlpha(25)
			painter.setBrush(bg_color)  # 透明（macOS 16）
		else:
			bg_color.setAlpha(200)
			painter.setBrush(bg_color)  # 半透明白（旧系统）
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawPath(path)


class InnerWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
		rect = QRectF(0, 0, self.width(), self.height())
		path = QPainterPath()
		path.addRect(rect)  # 没有圆角
		bg_color = self.palette().color(QPalette.ColorRole.Window)
		if is_macos_16_or_higher():
			bg_color.setAlpha(25)
			painter.setBrush(bg_color)  # 透明（macOS 16）
		else:
			bg_color.setAlpha(200)
			painter.setBrush(bg_color)  # 半透明白（旧系统）
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawPath(path)


class HorizontalButtonWindow(OuterWidget):
	buttonSelected = pyqtSignal(str)
	buttonDeselected = pyqtSignal(str)
	customTagAdded = pyqtSignal(str)  # 新增信号
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("横向按钮")
		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.WindowStaysOnTopHint
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
		self.setFixedSize(400, 80)

		scroll = QScrollArea()
		scroll.setFixedWidth(380)
		scroll.setFixedHeight(60)
		scroll.setWidgetResizable(True)
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		scroll.setFrameShape(QScrollArea.Shape.NoFrame)

		home_dir = base_dir
		tarname1 = "HazelnutAppPath"
		fulldir1 = os.path.join(home_dir, tarname1)
		if not os.path.exists(fulldir1):
			os.mkdir(fulldir1)
		tarname2 = "Custom.txt"
		self.fulldir2 = os.path.join(fulldir1, tarname2)
		if not os.path.exists(self.fulldir2):
			with open(self.fulldir2, 'a', encoding='utf-8') as f0:
				f0.write('Home\nImportant\nWork\n')
		custom_tag = codecs.open(self.fulldir2, 'r', encoding='utf-8').read()
		self.custom_tag_list = custom_tag.split('\n')
		while '' in self.custom_tag_list:
			self.custom_tag_list.remove('')

		widget = InnerWidget()
		#widget.setStyleSheet("""background-color: white;opacity:0.5;""")
		hbox = QHBoxLayout(widget)
		hbox.setSpacing(20)
		hbox.setContentsMargins(10, 10, 10, 10)
		self.btn_refs = []
		for name in self.custom_tag_list:
			#btn = ScrollButton(name)
			btn = GlassButton(
				name,
				radius=15,
				bg_color=(174, 129, 94, 80),  # 背景：浅棕色（加透明）
				shadow_color=(80, 50, 30, 50),  # 阴影：深棕带灰
				highlight_color=(255, 235, 200, 60)  # 高亮：米白偏橙 + 半透明
			)
			#btn.setFixedHeight(60)
			btn.singleClicked.connect(lambda caption, n=name: self.buttonSelected.emit(n))
			btn.rightClicked.connect(lambda caption, n=name: self.buttonDeselected.emit(n))
			hbox.addWidget(btn)
			self.btn_refs.append(btn)
		# 新增：自定义 tag 输入框
		self.input_box = GlassLineEdit()
		self.input_box.returnPressed.connect(self.add_custom_tag)
		hbox.addWidget(self.input_box)
		hbox.addStretch(1)
		scroll.setWidget(widget)

		layout = QHBoxLayout(self)
		layout.setContentsMargins(10, 10, 10, 10)
		layout.addWidget(scroll)

	def add_custom_tag(self):
		text = self.input_box.text().strip()
		if text and text not in [btn.text() for btn in self.btn_refs]:
			with open(self.fulldir2, 'a', encoding='utf-8') as f0:
				f0.write(text+'\n')
			btn = GlassButton(
				text,
				radius=15,
				bg_color=(174, 129, 94, 80),
				shadow_color=(80, 50, 30, 50),
				highlight_color=(255, 235, 200, 60)
			)
			btn.singleClicked.connect(lambda caption, n=text: self.buttonSelected.emit(n))
			btn.rightClicked.connect(lambda caption, n=text: self.buttonDeselected.emit(n))
			self.btn_refs.append(btn)
			# 插入到输入框前
			hbox = self.input_box.parentWidget().layout()
			hbox.insertWidget(hbox.indexOf(self.input_box), btn)
			self.input_box.clear()
			self.customTagAdded.emit(text)

	def mousePressEvent(self, event):
		event.ignore()  # 忽略鼠标按下事件

	def mouseMoveEvent(self, event):
		event.ignore()  # 忽略鼠标移动事件


class PermissionInfoWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.radius = 16  # 圆角半径，可按 macOS 15 或 26 设置为 16~26

		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.Window |
			Qt.WindowType.WindowStaysOnTopHint
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

		self.init_ui()

	def init_ui(self):
		self.setUpMainWindow()
		self.setFixedSize(400, 600)
		self.center()
		self.setFocus()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

		rect = QRectF(self.rect())
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)

		painter.setClipPath(path)
		bg_color = self.palette().color(QPalette.ColorRole.Window)
		painter.fillPath(path, bg_color)

	# 让无边框窗口可拖动
	def mousePressEvent(self, event):
		if event.button() == Qt.MouseButton.LeftButton:
			self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
			event.accept()

	def mouseMoveEvent(self, event):
		if event.buttons() == Qt.MouseButton.LeftButton:
			self.move(event.globalPosition().toPoint() - self.drag_pos)
			event.accept()

	def setUpMainWindow(self):
		# 添加关闭按钮（仿 macOS 左上角红色圆点）
		# self.close_button = QPushButton(self)
		# self.close_button.setFixedSize(12, 12)
		# self.close_button.move(10, 10)
		# self.close_button.setStyleSheet("""
		# 			QPushButton {
		# 				background-color: #FF5F57;
		# 				border-radius: 6px;
		# 				border: none;
		# 			}
		# 			QPushButton:hover {
		# 				background-color: #BF4943;
		# 			}
		# 		""")
		# self.close_button.clicked.connect(self.close)
		self.close_button = MacWindowButton("#FF605C", "x", self)
		self.close_button.move(10, 10)
		self.close_button.clicked.connect(self.close)

		layout = QVBoxLayout()

		title = QLabel("<h2>Permissions Required</h2>")
		title.setAlignment(Qt.AlignmentFlag.AlignCenter)
		layout.addWidget(title)

		info_text = (
			"<b>This application requires the following macOS permissions:</b><br><br>"
			"<b>1. Accessibility</b> and <b>Input Monitoring</b>:<br>"
			"These permissions are required to detect mouse drag actions, "
			"which are used to trigger the main interface. "
			"The app does <b>not</b> monitor your input for any other purpose.<br><br>"
			"<b>2. AppleEvents:</b><br>"
			"AppleEvents are used to enable the tag functionality within the app. "
			"This is necessary for the app to work as intended.<br><br>"
			"<b>File Access:</b><br>"
			"All file access is performed <b>only</b> as a result of your explicit actions. "
			"The app will <b>never</b> access any files automatically or without your direct request.<br><br>"
			"<hr>"
			"<b>How to grant Accessibility and Input Monitoring permissions:</b><br>"
			"1. Open <b>System Settings</b> (or <b>System Preferences</b> on older macOS).<br>"
			"2. Go to <b>Privacy & Security</b>.<br>"
			"3. Select <b>Accessibility</b> from the sidebar.<br>"
			"4. Click the <b>+</b> button and add this application.<br>"
			"5. Repeat for <b>Input Monitoring</b>.<br>"
			"6. Restart the app if necessary.<br><br>"
			"For AppleEvents, macOS will prompt you automatically when needed.<br><br>"
			"<hr>"
			"<b>How to use this application:</b><br>"
			"1. In <b>Finder</b>, select a file or folder.<br>"
			"2. Drag it back and forth a few times.<br>"
			"3. A circular button will appear on the screen.<br>"
			"4. Drop the file or folder onto this circular button.<br>"
			"5. A set of color tags will be displayed for you to choose from.<br>"
			"6. You can also manually enter a custom text tag below.<br><br>"
			"To avoid unnecessary interruptions, you can configure in the settings which applications the drag gesture will respond to. "
			"By default, the app only responds to actions in Finder, but you can customize it to work with other applications as well.<br><br>"
			"<b>Enjoy using this app! 😊🎉</b>"
		)

		info_label = QTextEdit()
		info_label.setReadOnly(True)
		info_label.setHtml(info_text)
		info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		layout.addWidget(info_label)

		self.setLayout(layout)

	def first_show_window(self):
		home_dir = base_dir
		tarname1 = "HazelnutAppPath"
		fulldir1 = os.path.join(home_dir, tarname1)
		if not os.path.exists(fulldir1):
			os.mkdir(fulldir1)
		tarname2 = "Permission.txt"
		self.fulldir4 = os.path.join(fulldir1, tarname2)
		if not os.path.exists(self.fulldir4):
			self.show()
			self.raise_()
			with open(self.fulldir4, 'a', encoding='utf-8') as f0:
				f0.write('shown')

	def show_window(self):
		self.show()
		self.raise_()

	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


class GlassLineEdit(QLineEdit):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setPlaceholderText("Add tag...")
		self.setStyleSheet("""
			background: transparent;
			border: none;
			color: white;
			font-size: 16px;
			padding: 8px 24px;
		""")
		self.radius = 15
		self.bg_color = QColor(174, 129, 94, 80)
		self.setFixedHeight(40)
		self.setFixedWidth(120)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
		rect = QRectF(0, 0, self.width(), self.height()).adjusted(2, 2, -2, -2)
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)
		painter.setBrush(QBrush(self.bg_color))
		painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
		painter.drawPath(path)
		super().paintEvent(event)


class MainWindow(QMainWindow):
	show_window_signal = pyqtSignal()
	def __init__(self, monitor):
		super().__init__()
		home_dir = base_dir
		tarname1 = "HazelnutAppPath"
		fulldir1 = os.path.join(home_dir, tarname1)
		if not os.path.exists(fulldir1):
			os.mkdir(fulldir1)
		tarname2 = "Allow.txt"
		self.fulldir3 = os.path.join(fulldir1, tarname2)
		if not os.path.exists(self.fulldir3):
			with open(self.fulldir3, 'a', encoding='utf-8') as f0:
				f0.write('Finder\n')

		self.file_path = []
		self.monitor = monitor
		self.show_window_signal.connect(self.show_window_and_button)
		self.setWindowTitle("圆形排列按钮")
		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.Window |
			Qt.WindowType.WindowStaysOnTopHint
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

		self.hori_btn_window = HorizontalButtonWindow()
		self.hori_btn_window.setVisible(False)
		self.hori_btn_window.setFixedHeight(80)
		self.hori_btn_window.setParent(self)
		self.hori_btn_window.move(0, 380)
		#self.hori_btn_offset = (-5, 450)  # 横向按钮窗口相对主窗口的偏移（右侧10px）

		self.selected_captions = []

		# 按钮名称列表
		button_names = ["Red", "Yellow", "Orange", "Green", "Blue", "Purple", "Gray", "Clear"]
		color_defs = [
			(220, 38, 38, 30),  # Red
			(252, 211, 77, 30),  # Yellow
			(251, 146, 60, 30),  # Orange
			(34, 197, 94, 30),  # Green
			(59, 130, 246, 30),  # Blue
			(139, 92, 246, 30),  # Purple
			(156, 163, 175, 30),  # Gray
			(156, 163, 175, 15),  # Clear
		]
		shadow_defs = [
			(100, 0, 0, 80),
			(120, 100, 0, 80),
			(120, 60, 0, 80),
			(0, 100, 0, 80),
			(0, 0, 100, 80),
			(60, 0, 100, 80),
			(60, 60, 60, 80),
			(60, 60, 60, 40),
		]
		highlight_defs = [
			(255, 180, 180, 100),
			(255, 245, 180, 100),
			(255, 210, 180, 100),
			(180, 255, 200, 100),
			(180, 220, 255, 100),
			(220, 180, 255, 100),
			(220, 220, 220, 100),
			(220, 220, 220, 50),
		]
		# 创建圆形按钮控件，传递颜色参数列表
		self.circle_widget = CircleButtonWidget(
			button_names,
			bg_colors=color_defs,
			shadow_colors=shadow_defs,
			highlight_colors=highlight_defs
		)
		self.circle_widget.setFixedSize(400, 400)
		self.circle_widget.setParent(self)
		self.circle_widget.move(0, 0)
		# 新增一个手动触发的按钮
		#self.trigger_btn = QPushButton("显示圆形按钮")
		#self.trigger_btn.clicked.connect(self.circle_widget.start_show_buttons)
		self.main_button = DropGlassButton("+", bg_color=(156, 163, 175, 15), shadow_color=(60, 60, 60, 40), highlight_color=(220, 220, 220, 50))
		self.main_button.setFixedSize(100, 100)
		self.main_button.file_dropped_callback = self.on_file_dropped
		self.main_button.move(150, 150)
		self.main_button.setParent(self)
		self.main_button.show()
		self.main_button.setStyleSheet("""
			font-size: 40px;
		""")
		self.main_button.pathChanged.connect(self.on_path_changed)
		self.hide_timer = QTimer(self)
		self.hide_timer.setSingleShot(True)
		self.hide_timer.timeout.connect(self.hide_button)
		self.show_window_signal.connect(self.show_window_and_button)

		# 用垂直布局
		# layout = QVBoxLayout()
		# layout.setContentsMargins(0, 0, 0, 0)
		# layout.setSpacing(-400)
		# layout.addWidget(self.circle_widget)
		# layout.addWidget(self.hori_btn_window)
		# container = QWidget()
		# container.setLayout(layout)
		# self.setCentralWidget(container)
		self.setFixedSize(440, 620)

		# two buttons
		self.close_button = GlassButton('Close', radius=15, bg_color=(156, 163, 175, 15), shadow_color=(60, 60, 60, 40), highlight_color=(220, 220, 220, 50))
		self.close_button.setParent(self)
		self.close_button.clicked.connect(self.close_window)
		self.close_button.setFixedHeight(30)
		self.close_button.setFixedWidth(100)
		self.close_button.move(80, 490)

		self.check_button = GlassButton('Tag!', radius=15, bg_color=(156, 163, 175, 15), shadow_color=(60, 60, 60, 40),
										highlight_color=(220, 220, 220, 50))
		self.check_button.setParent(self)
		self.check_button.clicked.connect(self.tag_file)
		self.check_button.setFixedHeight(30)
		self.check_button.setFixedWidth(100)
		self.check_button.move(220, 490)

		# 连接信号
		self.circle_widget.buttonSelected.connect(self.on_button_selected)
		self.circle_widget.buttonDeselected.connect(self.on_button_deselected)
		self.circle_widget.clearAll.connect(self.clear_selection)
		self.hori_btn_window.buttonSelected.connect(self.on_button_selected)
		self.hori_btn_window.buttonDeselected.connect(self.on_button_deselected)

		self.main_button.raise_()
		self.close_button.raise_()
		self.check_button.raise_()
		self.close_button.setVisible(False)
		self.check_button.setVisible(False)

	def show_button_with_timeout(self):
		self.hide_timer.start(2000)  # 2秒

	def hide_button(self):
		self.close()

	def on_file_dropped(self):
		self.hide_timer.stop()

	def show_window_and_button(self):
		try:
			active_app = NSWorkspace.sharedWorkspace().activeApplication()
			app_name = active_app['NSApplicationName']

			if app_name == "loginwindow":
				return

			ALLOWED_APPS = codecs.open(self.fulldir3, 'r', encoding='utf-8').read()
			ALLOWED_APPS_LIST = ALLOWED_APPS.split('\n')
			while '' in ALLOWED_APPS_LIST:
				ALLOWED_APPS_LIST.remove('')

			if app_name not in ALLOWED_APPS_LIST:
				return

			self.WEIGHT = int(self.screen().availableGeometry().width())
			self.HEIGHT = int(self.screen().availableGeometry().height())
			# pos = QCursor.pos()
			# x, y = pos.x(), pos.y()
			# if x + 440 > self.WEIGHT:
			# 	x = self.WEIGHT - 440
			# if y + 620 > self.HEIGHT:
			# 	y = self.HEIGHT - 620
			win_w, win_h = self.width(), self.height()
			pos = QCursor.pos()
			x, y = pos.x(), pos.y()

			# 让窗口居中于鼠标
			x = x - win_w // 2
			y = y - win_h // 2

			# 保证窗口不会超出屏幕
			if x < 0:
				x = 0
			if y < 0:
				y = 0
			if x + win_w > self.WEIGHT:
				x = self.WEIGHT - win_w
			if y + win_h > self.HEIGHT:
				y = self.HEIGHT - win_h
			self.move(x, y)
			# 横向按钮窗口跟随主窗口
			# self.hori_btn_window.move(x + self.hori_btn_offset[0], y + self.hori_btn_offset[1])

			self.show()
			self.show_button_with_timeout()
			# self.monitor.reset_state()  # 新增：显示窗口时重置 DragMonitor 状态
			self.stop_monitor()  # 新增：窗口显示后停止监听
		except Exception as e:
			# 发生异常时打印错误信息
			p = "程序发生异常-显示时:" + str(e)
			with open(BasePath + "Error.txt", 'a', encoding='utf-8') as f0:
				f0.write(p)

	def close_window(self):
		self.circle_widget.hide_all_buttons()
		self.hori_btn_window.setVisible(False)
		self.close_button.setVisible(False)
		self.check_button.setVisible(False)
		self.close()

	def closeEvent(self, event):
		self.hori_btn_window.close()
		# self.monitor.reset_state()  # 新增：显示窗口时重置 DragMonitor 状态
		self.start_monitor()  # 新增：窗口关闭后重新监听
		super().closeEvent(event)

	def stop_monitor(self):
		if self.monitor is not None:
			self.monitor.stop()
			self.monitor = None

	def start_monitor(self):
		if self.monitor is None:
			self.monitor = DragMonitor(on_trigger=self.show_window_and_button)
			self.monitor.start()

	def on_path_changed(self, path):
		#print("MainWindow got path:", path)
		self.file_path = path

	def tag_file(self):
		def clean_finder_color_label(path, index=0):
			"""
			用 AppleScript 设置 Finder 标签颜色
			index: 0-7（0 表示移除标签）
			"""
			script = f'''
			tell application "Finder"
				set myFile to POSIX file "{path}" as alias
				set label index of myFile to {index}
			end tell
			'''
			subprocess.run(["osascript", "-e", script])
		def set_finder_tag(path, tags):
			"""
			设置 Finder 标签
			tags: 例如 ["Red", "Blue", "ProjectX"]，支持文字+颜色
			"""
			# 添加 timestamp metadata
			now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000")
			encoded_tags = [f"{tag}\n{now}" for tag in tags]

			plist_data = plistlib.dumps(encoded_tags)
			xattr.setxattr(path, 'com.apple.metadata:_kMDItemUserTags', plist_data)
		if self.file_path != []:
			captions = self.selected_captions
			if captions != []:
				for i in range(len(self.file_path)):
					clean_finder_color_label(self.file_path[i])
					set_finder_tag(self.file_path[i], captions)
			else:
				# remove all the tags
				try:
					for i in range(len(self.file_path)):
						clean_finder_color_label(self.file_path[i])
						xattr.removexattr(self.file_path[i], 'com.apple.metadata:_kMDItemUserTags')
				except Exception as e:
					pass
		self.close_window()

	def on_button_selected(self, caption):
		if caption not in self.selected_captions:
			self.selected_captions.append(caption)
		#print("Selected:", self.selected_captions)

	def on_button_deselected(self, caption):
		if caption in self.selected_captions:
			self.selected_captions.remove(caption)
		#print("Selected:", self.selected_captions)

	def clear_selection(self):
		self.selected_captions.clear()
		#print("Selected:", self.selected_captions)
		# 让所有按钮都取消选中
		for btn in self.circle_widget.buttons:
			btn.setSelected(False)
		for btn in self.hori_btn_window.btn_refs:
			btn.setSelected(False)


class window4(QWidget):  # Customization settings
	def __init__(self):
		super().__init__()
		self.radius = 16  # 圆角半径，可按 macOS 15 或 26 设置为 16~26

		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint |
			Qt.WindowType.Window
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

		self.initUI()

	def initUI(self):  # 设置窗口内布局
		self.setUpMainWindow()
		self.setFixedSize(500, 360)
		self.center()
		self.setWindowTitle('Customization settings')
		self.setFocus()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

		rect = QRectF(self.rect())
		path = QPainterPath()
		path.addRoundedRect(rect, self.radius, self.radius)

		painter.setClipPath(path)
		bg_color = self.palette().color(QPalette.ColorRole.Window)
		painter.fillPath(path, bg_color)

	# 让无边框窗口可拖动
	def mousePressEvent(self, event):
		if event.button() == Qt.MouseButton.LeftButton:
			self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
			event.accept()

	def mouseMoveEvent(self, event):
		if event.buttons() == Qt.MouseButton.LeftButton:
			self.move(event.globalPosition().toPoint() - self.drag_pos)
			event.accept()

	def setUpMainWindow(self):
		# 添加关闭按钮（仿 macOS 左上角红色圆点）
		# self.close_button = QPushButton(self)
		# self.close_button.setFixedSize(12, 12)
		# self.close_button.move(10, 10)
		# self.close_button.setStyleSheet("""
		# 	QPushButton {
		# 		background-color: #FF5F57;
		# 		border-radius: 6px;
		# 		border: none;
		# 	}
		# 	QPushButton:hover {
		# 		background-color: #BF4943;
		# 	}
		# """)
		# self.close_button.clicked.connect(self.cancel)
		self.close_button = MacWindowButton("#FF605C", "x", self)
		self.close_button.move(10, 10)
		self.close_button.clicked.connect(self.close)

		home_dir = base_dir
		tarname1 = "HazelnutAppPath"
		fulldir1 = os.path.join(home_dir, tarname1)
		if not os.path.exists(fulldir1):
			os.mkdir(fulldir1)
		tarname2 = "Allow.txt"
		self.fulldir3 = os.path.join(fulldir1, tarname2)
		if not os.path.exists(self.fulldir3):
			with open(self.fulldir3, 'a', encoding='utf-8') as f0:
				f0.write('Finder\n')

		lbl0 = QLabel("Only react to:", self)

		self.text_feed = QListWidget(self)
		self.text_feed.setFixedHeight(200)
		self.text_feed.itemSelectionChanged.connect(self.item_click_0)

		self.btn0_1 = QPushButton('', self)
		self.btn0_1.setParent(self)
		self.btn0_1.setFixedSize(15, 15)
		btn0_1_path = BasePath + 'plus.png'
		self.btn0_1.setStyleSheet('''
			QPushButton{
			border: transparent;
			background-color: transparent;
			border-image: url(%s);
			}
			QPushButton:pressed{
			border: 1px outset grey;
			background-color: #0085FF;
			border-radius: 4px;
			padding: 1px;
			color: #FFFFFF
			}
			''' % btn0_1_path)
		self.btn0_1.move(30, 240)

		self.btn0_2 = QPushButton('', self)
		self.btn0_2.setParent(self)
		self.btn0_2.setFixedSize(15, 15)
		btn0_2_path = BasePath + 'minus.png'
		self.btn0_2.setStyleSheet('''
			QPushButton{
			border: transparent;
			background-color: transparent;
			border-image: url(%s);
			}
			QPushButton:pressed{
			border: 1px outset grey;
			background-color: #0085FF;
			border-radius: 4px;
			padding: 1px;
			color: #FFFFFF
			}
			''' % btn0_2_path)
		self.btn0_2.move(55, 240)
		self.btn0_2.setVisible(False)

		self.btn_1 = WhiteButton('Save')
		self.btn_1.setParent(self)
		self.btn_1.clicked.connect(self.save_state)

		qw4 = QWidget()
		vbox4 = QVBoxLayout()
		vbox4.setContentsMargins(0, 0, 0, 0)
		vbox4.addWidget(lbl0)
		vbox4.addWidget(self.text_feed)
		vbox4.addStretch()
		qw4.setLayout(vbox4)

		qw3 = QWidget()
		qw3.setFixedHeight(50)
		vbox3 = QHBoxLayout()
		vbox3.setContentsMargins(0, 0, 0, 0)
		vbox3.addStretch()
		vbox3.addWidget(self.btn_1)
		vbox3.addStretch()
		qw3.setLayout(vbox3)

		vboxx = QVBoxLayout()
		vboxx.setContentsMargins(20, 20, 20, 20)
		vboxx.addSpacing(20)
		vboxx.addWidget(qw4)
		vboxx.addWidget(qw3)
		self.setLayout(vboxx)

		self.btn0_1.raise_()
		self.btn0_2.raise_()

		only_react = codecs.open(self.fulldir3, 'r', encoding='utf-8').read()
		only_react_list = only_react.split('\n')
		while '' in only_react_list:
			only_react_list.remove('')
		self.text_feed.clear()
		self.text_feed.addItems(only_react_list)

	def item_click_0(self):
		selected_items = self.text_feed.selectedItems()  # 获取已选择的项
		if len(selected_items) > 0:
			pass
			self.btn0_2.setVisible(True)
		else:
			pass
			self.btn0_2.setVisible(False)

	def add_item_0(self):
		fj = QFileDialog.getOpenFileName(self, "Open File", str(Path("/Applications")), "Application (*.app)")
		if fj[0] != '':
			pattern2 = re.compile(r'([^/]+)\.app$')
			result = ''.join(pattern2.findall(fj[0])) + '\n'
			never_react = codecs.open(self.fulldir3, 'r', encoding='utf-8').read()
			never_react_list = never_react.split('\n')
			while '' in never_react_list:
				never_react_list.remove('')
			if result.rstrip('\n') not in never_react_list:
				with open(self.fulldir3, 'a', encoding='utf-8') as f0:
					f0.write(result)
				never_react = codecs.open(self.fulldir3, 'r', encoding='utf-8').read().lstrip('\n')
				with open(self.fulldir3, 'w', encoding='utf-8') as f0:
					f0.write(never_react)
			never_react = codecs.open(self.fulldir3, 'r', encoding='utf-8').read()
			never_react_list = never_react.split('\n')
			while '' in never_react_list:
				never_react_list.remove('')
			self.text_feed.clear()
			self.text_feed.addItems(never_react_list)

	def delete_item_0(self):
		selected_items = self.text_feed.selectedItems()
		if len(selected_items) > 0:
			index = 0
			text = ''
			for item in selected_items:
				index = self.text_feed.row(item)  # 获取选中项的索引
				text = item.text()
			output_list = []
			for i in range(self.text_feed.count()):
				output_list.append(self.text_feed.item(i).text())
			while '' in output_list:
				output_list.remove('')
			if text != '':
				deletelist = []
				deletelist.append(output_list[index])
				output_list.remove(deletelist[0])
				#set show
				self.text_feed.clear()
				self.text_feed.addItems(output_list)
				# write to local
				output = '\n'.join(output_list) + '\n'
				with open(self.fulldir3, 'w', encoding='utf-8') as f0:
					f0.write('')
				with open(self.fulldir3, 'w', encoding='utf-8') as f0:
					f0.write(output)

	def save_state(self):
		self.close()

	def totalquit(self):
		sys.exit(0)

	def restart(self):
		time.sleep(3)
		self.restart_app()
		#os.execv(sys.executable, [sys.executable, __file__])

	def restart_app(self):
		applescript = '''
		if application "Hazelnut Tags" is running then
			try
				tell application "Hazelnut Tags"
					quit
					delay 1
					activate
				end tell
			on error number -128
				quit application "Hazelnut Tags"
				delay 1
				activate application "Hazelnut Tags"
			end try
		end if
		'''
		subprocess.Popen(['osascript', '-e', applescript])

	def login_start(self):
		plist_filename = 'com.ryanthehito.hazelnut.plist'
		if action10.isChecked():
			try:
				launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
				launch_agents_dir.mkdir(parents=True, exist_ok=True)
				plist_source_path = BasePath + plist_filename
				destination = launch_agents_dir / plist_filename
				shutil.copy2(plist_source_path, destination)
				# 设置权限确保 macOS 能读
				os.chmod(destination, 0o644)
			except Exception as e:
				# 发生异常时打印错误信息
				p = "程序发生异常: Autostart failed: " + str(e)
				with open(BasePath + "Error.txt", 'a', encoding='utf-8') as f0:
					f0.write(p)
		if not action10.isChecked():
			try:
				plist_path = Path.home() / "Library" / "LaunchAgents" / plist_filename
				if plist_path.exists():
					# 删除文件
					os.remove(plist_path)
			except Exception as e:
				# 发生异常时打印错误信息
				p = "程序发生异常: Removing autostart failed: " + str(e)
				with open(BasePath + "Error.txt", 'a', encoding='utf-8') as f0:
					f0.write(p)
	
	def center(self):  # 设置窗口居中
		qr = self.frameGeometry()
		cp = self.screen().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
	
	def keyPressEvent(self, e):  # 当页面显示的时候，按下esc键可关闭窗口
		if e.key() == Qt.Key.Key_Escape.value:
			self.close()
	
	def activate(self):  # 设置窗口显示
		w2.checkupdate()
		if w2.lbl2.text() != 'No Intrenet' and 'ready' in w2.lbl2.text():
			w2.show()

		never_react = codecs.open(self.fulldir3, 'r', encoding='utf-8').read()
		never_react_list = never_react.split('\n')
		while '' in never_react_list:
			never_react_list.remove('')
		self.text_feed.clear()
		self.text_feed.addItems(never_react_list)

		self.show()
		self.setFocus()
		self.raise_()
		self.activateWindow()
	
	def cancel(self):  # 设置取消键的功能
		self.close()

style_sheet_ori = '''
	QTabWidget::pane {
		border: 1px solid #ECECEC;
		background: #ECECEC;
		border-radius: 9px;
}
	QTableWidget{
		border: 1px solid grey;  
		border-radius:4px;
		background-clip: border;
		background-color: #FFFFFF;
		color: #000000;
		font: 14pt Helvetica;
}
	QWidget#Main {
		border: 1px solid #ECECEC;
		background: #ECECEC;
		border-radius: 9px;
}
	QPushButton{
		border: 1px outset grey;
		background-color: #FFFFFF;
		border-radius: 4px;
		padding: 1px;
		color: #000000
}
	QPushButton:pressed{
		border: 1px outset grey;
		background-color: #0085FF;
		border-radius: 4px;
		padding: 1px;
		color: #FFFFFF
}
	QPlainTextEdit{
		border: 1px solid grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #F3F2EE;
		color: #000000;
		font: 14pt Times New Roman;
}
	QPlainTextEdit#edit{
		border: 1px solid grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #FFFFFF;
		color: rgb(113, 113, 113);
		font: 14pt Helvetica;
}
	QTableWidget#small{
		border: 1px solid grey;  
		border-radius:4px;
		background-clip: border;
		background-color: #F3F2EE;
		color: #000000;
		font: 14pt Times New Roman;
}
	QLineEdit{
		border-radius:4px;
		border: 1px solid gray;
		background-color: #FFFFFF;
}
	QTextEdit{
		border: 1px grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #F3F2EE;
		color: #000000;
		font: 14pt;
}
	QListWidget{
		border: 1px grey;  
		border-radius:4px;
		padding: 1px 5px 1px 3px; 
		background-clip: border;
		background-color: #F3F2EE;
		color: #000000;
		font: 14pt;
}
'''

if __name__ == '__main__':
	while True:
		try:
			def show_window():
				window.show_window_signal.emit()

			monitor = DragMonitor(on_trigger=show_window)
			window = MainWindow(monitor)
			window.show()
			window.raise_()
			window.activateWindow()
			window.setVisible(False)
			monitor.start()  # 启动监听

			w1 = window_about()  # about
			w2 = window_update()  # update
			w4 = window4()  # CUSTOMIZING
			# w5 = SliderWindow() # guide
			# w5.setAutoFillBackground(True)
			# p = w5.palette()
			# p.setColor(w5.backgroundRole(), QColor('#ECECEC'))
			# w5.setPalette(p)
			# w3 = window3()  # main1
			# w3.setAutoFillBackground(True)
			# p = w3.palette()
			# p.setColor(w3.backgroundRole(), QColor('#ECECEC'))
			# w3.setPalette(p)
			permission = PermissionInfoWidget()
			permission.first_show_window()
			action1.triggered.connect(w1.activate)
			action2.triggered.connect(w2.activate)
			# action3.triggered.connect(w3.activate)
			action7.triggered.connect(w4.activate)
			action8.triggered.connect(w4.restart)
			action9.triggered.connect(permission.show_window)
			action10.triggered.connect(w4.login_start)
			# btna4.triggered.connect(w3.activate)
			# btna5.triggered.connect(w4.activate)
			# btna6.triggered.connect(w4.totalquit)
			w4.btn0_1.clicked.connect(w4.add_item_0)
			w4.btn0_2.clicked.connect(w4.delete_item_0)
			# w4.btn1_1.clicked.connect(w4.add_item_1)
			# w4.btn1_2.clicked.connect(w4.delete_item_1)
			# w4.btn2_1.clicked.connect(w4.add_item_2)
			# w4.btn2_2.clicked.connect(w4.delete_item_2)
			quit.triggered.connect(w4.totalquit)
			app.setStyleSheet(style_sheet_ori)
			sys.exit(app.exec())
		except Exception as e:
			# 发生异常时打印错误信息
			p = "程序发生异常:" + str(e)
			with open(BasePath + "Error.txt", 'w', encoding='utf-8') as f0:
				f0.write(p)
			w4 = window4()
			w4.restart_app()
			sys.exit(0)
			# # 延时一段时间后重新启动程序（例如延时 5 秒）
			# time.sleep(5)
			# # 使用 os.execv() 在当前进程中启动自身，实现自动重启
			# os.execv(sys.executable, [sys.executable, __file__])
