import keyboard
import asyncio
import os


from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from functools import partial

import ctypes
import win32gui
import win32process
import threading


from config import Config , environ
from scripts import ENUMS

con = Config()

class FastMurer():
    def __init__(self) -> None:
        super(FastMurer,self).__init__()

        self.microphone_muted = False
        self.speakers_muted = False
        self.hide = False

        self.button_pressed = False

        asyncio.run(self.main())


    async def appBinds(self):
        combinations={
           "mute_microphone":[environ["CONFIG"]["binds"]["mute_microphone"],self.mute , [ENUMS.MUTE_MICRO]],
           "mute_speakers":[environ["CONFIG"]["binds"]["mute_speakers"],self.mute , [ENUMS.MUTE_SPEAKERS]],
           "exit_app":[environ["CONFIG"]["binds"]["exit_app"], self.exitApp, [0]]}

        keyboard.add_hotkey(combinations["mute_microphone"][0], lambda: asyncio.run_coroutine_threadsafe(self.mute(*combinations["mute_microphone"][2]), self.loop))
        keyboard.add_hotkey(combinations["mute_speakers"][0], lambda: asyncio.run_coroutine_threadsafe(self.mute(*combinations["mute_speakers"][2]),self.loop))
        keyboard.add_hotkey(combinations["exit_app"][0], lambda: asyncio.run_coroutine_threadsafe(self.exitApp(),self.loop))

    async def getDevices(self):
        while True:
            self.microphones = AudioUtilities.GetMicrophone()
            self.speakers = AudioUtilities.GetSpeakers()

            environ["microphone"] = self.microphones
            environ["speakers"] = self.speakers

            await asyncio.sleep(0.01)


    async def exitApp(self,*args):
        exit(1)

    async def mute(self, _type):
        if _type == ENUMS.MUTE_MICRO:
            interface = self.microphones.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL , None)
            self.microphone_volume = cast(interface, POINTER(IAudioEndpointVolume))

            muted = self.microphone_volume.GetMute()

            self.microphone_volume.SetMute(not muted , None)
            environ["LOGGER"].info(f"Micrphone is disabled" if not muted  else f"Micrphone is enabled")

            if environ["CONFIG"]["app"]["show_text"]:
                print(f"Micrphone is disabled" if not muted  else f"Micrphone is enabled")
        
        elif _type == ENUMS.MUTE_SPEAKERS:
            interface = self.speakers.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
            self.speakers_volume = cast(interface , POINTER(IAudioEndpointVolume))

            muted = self.speakers_volume.GetMute()

            self.speakers_volume.SetMute(not muted , None)
            environ["LOGGER"].info(f"Speakers is disabled" if not muted  else f"Speakers is enabled")

            if environ["CONFIG"]["app"]["show_text"]:
                print(f"Speakers is disabled" if not muted  else f"Speakers is enabled")



    def create_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()     

    async def main(self):
        environ["LOGGER"].info("Application was successfully initialized")


        # find and load devices
        self.microphones = AudioUtilities.GetMicrophone()
        if self.microphones != None:
            environ["LOGGER"].info("Microphone is detected")
        
        else:
            environ["LOGGER"].warning("Micrphone is not detected")

        self.speakers = AudioUtilities.GetSpeakers()
        if self.microphones != None:
            environ["LOGGER"].info("Speakers is detected")
        
        else:
            environ["LOGGER"].warning("Speakers is not detected")


        environ["microphone"] = self.microphones
        environ["speakers"] = self.speakers


        
        # call event to get devices
        run_loop = threading.Thread(target= self.create_event_loop, daemon= True)
        run_loop.start()

        # loop for bind in app
        await asyncio.gather(
            self.appBinds(),
            self.getDevices(),
            con.updateConfigFile(),)
        

    def getEnviron(self):
        print(environ)


if __name__ == "__main__":
    FastMurer()