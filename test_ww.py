import logging
import time

import requests
from scipy.io.wavfile import read

from libs.dsp import get_rms, add_gain
from libs.play import play_data
from libs.recorder import Recorder
from libs.testloop import lombard
from telebot.credentials import bot_token
from telebot.telegram_logbot import Telebot


class MyRec(Recorder):
    def __init__(self):
        super(MyRec, self).__init__()
        self.activated = False
        self.waiting_for_mic = False
        self.waiting_for_cancel = False
        self.waiting_for_music = False
        self.timeout = 1

    def calculate_tresholds(self):
        input("Turn off radio and press ENTER")
        self.record(5, channel=1, monitor=True)
        noise_off = get_rms(self.data)[1]
        print("RMS: %sdBSPL\n" % (noise_off + self.correction[0]))
        input("Turn on radio and press ENTER")
        self.record(5, channel=1, monitor=True)
        noise_on = get_rms(self.data)[1]
        print("RMS: %sdBSPL\n" % (noise_on + self.correction[0]))
        print("\nLombard effect: %0.2fdB" % (lombard(noise_on)))
        return noise_on, noise_off

    def on_timeout(self):
        print("TIMEOUT")
        if self.waiting_for_music:
            self.waiting_for_cancel = True
            print("TIMEOUT: trying again with cancel command")
            raise KeyboardInterrupt

    def on_negative_edge(self):
        print("Negative edge")
        if self.waiting_for_mic:
            print("MIC ACTIVATED")
            self.activated = True
            self.waiting_for_mic = False
            self.waiting_for_cancel = True
            raise KeyboardInterrupt
        else:
            pass

    def on_positive_edge(self):
        print("Positive edge")
        if self.waiting_for_cancel:
            print("COMMAND DETECTED")
            self.activated = False
            raise KeyboardInterrupt
        else:
            pass


def load_settings():
    """
    Load saved settings
    """
    try:
        with open("settings/settings.vcfg", "r", encoding="utf-16") as f:
            for line in f.readlines():
                if "MIC_DBFSTODBSPL" in line:
                    r.correction = eval(line.split("=")[-1])
    except FileNotFoundError:
        raise FileNotFoundError("Settings file not found!")
    return


def print_ww_report(filename):
    with open(filename, "w", encoding="utf-16") as f:
        f.write("Issued ww:\t %s\n" % issued_ww)
        f.write("Recognized ww:\t %s\n" % recognized_ww)
        f.write("Wakeup time\tRecognition time\n")
        for index in range(len(time_response)):
            f.write("%0.5f\t%0.5f\n" % (time_wakeup[index], time_response[index]))


def telegram_bot_sendtext(bot_message, chat_id):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode' \
                                                                                                 '=Markdown&text=' + \
                bot_message
    response = requests.get(send_text)
    return response.json()


if __name__ == "__main__":

    lang = "PLP"

    oscar = Telebot(bot_token)
    oscar.main()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    name = input("Insert the name for the WW test:\n-->")
    t_logging = (input("Activate telegram logging? (y/n)")).lower()
    if t_logging == "y":
        telegram_logging = True
        oscar.send_message("Test started!")
    else:
        telegram_logging = False

    ww = "phrases/harman/%s/%s_000.wav" % (lang, lang)
    cancel = "phrases/harman/%s/%s_999.wav" % (lang, lang)
    report_name = "ww_tests/" + name + ".csv"

    fs, ww_data = read(ww)
    _, cancel_data = read(cancel)

    r = MyRec()
    load_settings()
    if telegram_logging:
        oscar.send_message("Calculating treshold...")
    # calculate treshold based on the difference between radio on and radio off noise
    noise_radio_on, noise_radio_off = r.calculate_tresholds()

    ww_data = add_gain(ww_data, lombard(noise_radio_on + r.correction[0]))
    mean_noise = ((noise_radio_on + noise_radio_off) / 2)

    r.hightreshold = (noise_radio_on + mean_noise) / 2
    r.lowtreshold = (noise_radio_off + mean_noise) / 2

    txt = "High treshold = %sdB\nLow treshold = %sdB" % (r.hightreshold, r.lowtreshold)
    print(txt)
    if telegram_logging:
        oscar.send_message("Done! \n" + txt)

    n_tests = 200
    time_wakeup = []
    time_response = []
    issued_ww = 0
    recognized_ww = 0

    try:
        for i in range(n_tests):
            oscar.bot_text = "++ Test '%s' (%s of %s) ++\n" % (name.replace("_", " ").upper(), (i + 1), n_tests)
            start_time = time.time()
            print("Test number %s" % (i + 1))
            while True:
                play_data(ww_data, fs)
                issued_ww += 1
                r.waiting_for_mic = True
                r.record(10, channel=1, monitor=True)
                if r.activated:
                    r.waiting_for_mic = False
                    print("Time: %0.2fs" % (len(r.data) / r.fs))
                    recognized_ww += 1
                    wt = len(r.data) / r.fs
                    time_wakeup.append(wt)
                    print("Waiting for cancel")
                    while True:
                        r.waiting_for_cancel = True
                        play_data(cancel_data, fs)
                        r.record(20, channel=1, monitor=False)
                        rt = len(r.data) / r.fs
                        print("Time: %0.2fs" % rt)
                        # record. If timeout after response is bigger than 3 seconds, assumes the radio is not back
                        # to music
                        r.waiting_for_cancel = False
                        r.waiting_for_music = True
                        print(r.timeout)
                        print("Waiting for response from radio (threshold = %0.2fdB)" % r.lowtreshold)
                        r.record(10, channel=1, l_threshold=r.lowtreshold, monitor=True)
                        if not r.waiting_for_cancel:
                            print("No timeout: music resumed")
                            r.waiting_for_music = False
                            # cancel has been correctly understood
                            print(telegram_logging)
                            if telegram_logging:
                                try:
                                    deltat = time.time() - start_time
                                    ETA = deltat * (n_tests - (i + 1))
                                    print(ETA)
                                    ETA_hours = ETA / 3600
                                    ETA_minutes = (ETA % 3600) / 60
                                    ETA_seconds = ETA % 60
                                    oscar.bot_text += (
                                            "WW_accuracy: %s/%s\nWakeup time: %0.2fs\nRecognition time: %0.2fs\nETA: "
                                            "%02d:%02d:%02ds" % (
                                                recognized_ww, issued_ww, wt, rt, ETA_hours, ETA_minutes,
                                                ETA_seconds))
                                    oscar.send_message(oscar.bot_text)
                                except Exception as e:
                                    print("Error! (%s)" % e)
                            print_ww_report(report_name)
                            print("Cancel\nResult: %s/%s" % (recognized_ww, issued_ww))
                            print("Proceeding to next test")
                            time_response.append(rt)
                            r.activated = False
                            break
                    break
                else:
                    print("Trying again...")

    except KeyboardInterrupt:
        print("Test interrupted")

    print("Saving report...")
    print_ww_report(report_name)
