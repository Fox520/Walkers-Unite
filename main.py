from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.theming import ThemeManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
Window.softinput_mode = "below_target"  # resize to accomodate keyboard

from kivymd.list import OneLineListItem
from kivymd.list import TwoLineListItem
from kivymd.list import ThreeLineListItem

import socket
import json
import traceback
import threading
import urllib

host = "127.0.0.1"
port = 800
address = "http://tinkledebug.ddns.net/access/ip_address.txt"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
__NAME = None
welcome_txt = ""
CONNECTION_ESTABLISHED = False


def set_host():
    try:
        global host
        host = urllib.urlopen(address).read().strip()
    except:
        pass


def start_connections():
    global __NAME
    global welcome_txt
    global CONNECTION_ESTABLISHED
    try:
        set_host()
        s.connect((host, port))
        data = json.loads(s.recv(1024))

        __NAME = data["name"]
        welcome_txt = "Welcome "+__NAME + ". Walkers United!"
        CONNECTION_ESTABLISHED = True
    except:
        print(traceback.format_exc())


def getName():
    return __NAME


Builder.load_string('''
#:import Toolbar kivymd.toolbar.Toolbar
#:import ThemeManager kivymd.theming.ThemeManager
#:import MDTab kivymd.tabs.MDTab
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDLabel kivymd.label.MDLabel
#:import Toolbar kivymd.toolbar.Toolbar
#:import MDList kivymd.list.MDList
#:import MDTextField kivymd.textfields.MDTextField


#:include kv/initial_screen.kv
#:include kv/main_screen.kv

''')


class InitialScreen(Screen):
    def on_enter(self):
        threading.Thread(target=start_connections).start()
        # call my_callback every 0.5 seconds
        self.event = Clock.schedule_interval(self.my_callback, 0.5)

    def my_callback(self, dt):
        if CONNECTION_ESTABLISHED:
            Launcher().change_screen("walker_screen")

    def on_leave(self):
        Clock.unschedule(self.event)


class WalkerScreen(Screen):
    def __init__(self, **kwargs):
        super(WalkerScreen, self).__init__(**kwargs)
        self.walker_tab = self.ids["walker_tab"]
        self.ml = self.ids["ml"]
        self.online_num = self.ids["online_num"]

    def on_enter(self):
        self.add_one_line(welcome_txt)
        threading.Thread(target=self.incomingMessageHandler).start()

    def add_one_line(self, data):
        self.ml.add_widget(OneLineListItem(text=data))

    def add_two_line(self, name, data):
        self.ml.add_widget(TwoLineListItem(text=data, secondary_text=name))

    def add_three_line(self, name, data):
        self.ml.add_widget(ThreeLineListItem(text=data, secondary_text=name))

    def incomingMessageHandler(self):

        while True:
            try:
                message = json.loads(s.recv(1024))
                message_type = message["message_type"]

                if message_type == "short_text":
                    self.add_two_line(message["from"], message["text"])
                elif message_type == "long_text":
                    self.add_three_line(message["from"], message["text"])
                elif message_type == "online_number":
                    self.online_num.text = message["walkers_online"]
                else:
                    self.add_one_line(message["text"])
            except:
                print(traceback.format_exc())

    def send_message(self, data):
        try:
            # character limit
            if(len(data) > 150):
                pass
            else:
                template = {}
                template["message_type"] = "broadcast"
                template["from"] = getName()
                template["text"] = data
                s.send(json.dumps(template))
        except:
            print(traceback.format_exc())


class Launcher(App):
    global sm
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Blue'
    theme_cls.theme_style = "Dark"
    sm = ScreenManager()

    def change_screen(self, screen_name):
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            print("Screen [" + screen_name+"] does not exist.")

    def build(self):
        global sm
        sm.add_widget(InitialScreen(name="initial_screen"))
        sm.add_widget(WalkerScreen(name="walker_screen"))
        return sm

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    Launcher().run()
