import logging
import time
from threading import Thread
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
        input("Turn on radio and press ENTER")
        self.record(5, channel=1, monitor=True)
        noise_on = get_rms(self.data)[1]
        print("RMS: %sdBSPL\n" % (noise_on + self.correction[0]))
        input("Turn off radio and press ENTER")
        self.record(5, channel=1, monitor=True)
        noise_off = get_rms(self.data)[1]
        print("RMS: %sdBSPL\n" % (noise_off + self.correction[0]))
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

    lang = "RUR"

    # create a thread to record all the process
    main_recorder = Recorder()
    t = Thread(target=main_recorder.record, args=(None, 0, None, None, False))
    t.start()
    time.sleep(2)

    name = input("Insert the name for the WW test:\n-->")
    t_logging = (input("Activate telegram logging? (y/n)")).lower()

    if t_logging == "y":
        telegram_logging = True
        oscar = Telebot(bot_token)
        oscar.main()
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

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

    # Automatically calculate treshold. Just turn on the radio
    input("Turn on radio and press ENTER")
    r.record(5, channel=1, monitor=True)  # record noise with radio on
    noise_on = get_rms(r.data)[1]  # measure noise
    print("RMS: %sdBSPL\n" % (noise_on + r.correction[0]))
    play_data(ww_data, fs)  # Wakeword to stop music
    r.lowtreshold = noise_on - 3  # set default treshold value
    r.waiting_for_mic = True  # recording will stop at negative edge (to detect when music stops)
    r.record(5, channel=1, monitor=True)  # detect when the music actually stops to measure noise without radio
    r.hightreshold = r.lowtreshold - 3  # set default treshold value
    r.waiting_for_cancel = True  # now recording will stop on positive edge
    r.record(5, channel=1, monitor=True)  # record silence until positive edge
    play_data(cancel_data, fs)  # Cancel command
    r.waiting_for_music = True  # now recording will stop if timeout (noise level under treshold) longer than 1 second
    r.record(5, channel=1, monitor=True)  # ensure that the "cancel" command has been understood (if music resumes)
    noise_off = get_rms(r.data)[1]  # value of noise without radio

    # Calculate treshold values (negative and positive)
    print("RMS: %sdBSPL\n" % (noise_off + r.correction[0]))
    print("\nLombard effect: %0.2fdB" % (lombard(noise_on + r.correction[0])))
    ww_data = add_gain(ww_data, lombard(noise_on + r.correction[0]))  # adjust gain based on Lombard effect
    mean_noise = ((noise_on + noise_off) / 2)

    r.hightreshold = (noise_on + mean_noise) / 2
    r.lowtreshold = (noise_off + mean_noise) / 2

    txt = "High treshold = %sdB\nLow treshold = %sdB" % (r.hightreshold, r.lowtreshold)
    print(txt)
    time.sleep(2)
    if telegram_logging:
        try:
            oscar.send_message("Done! \n" + txt)
        except Exception as e:
            print("Something went wrong... :(\n(%s)" % e)
    n_tests = 200
    time_wakeup = []  # array of wakeup times
    time_response = []  # array of response times
    issued_ww = 0  # number of issued wakewords
    recognized_ww = 0  # number of times the wakeword is recognized
    r.waiting_for_cancel = False
    r.waiting_for_mic = True
    try:
        for i in range(n_tests):
            if telegram_logging:
                oscar.bot_text = "Test '%s' (%s of %s)\n" % (name.replace("_", " ").upper(), (i + 1), n_tests)
                try:
                    oscar.send_message(oscar.bot_text + "...")
                except Exception as e:
                    print("Something went wrong... :(\n(%s)" % e)

            start_time = time.time()
            print("Test number %s" % (i + 1))
            cancel_repetitions = 0
            while True:
                play_data(ww_data, fs)
                t1 = time.time()
                issued_ww += 1
                r.waiting_for_mic = True
                r.record(10, channel=1, monitor=True)
                if r.activated:
                    r.waiting_for_mic = False
                    wt = time.time() - t1
                    print("Time: %0.2fs" % (wt))
                    recognized_ww += 1
                    time_wakeup.append(wt)
                    print("Waiting for cancel")
                    while True:
                        r.waiting_for_cancel = True
                        play_data(cancel_data, fs)
                        cancel_repetitions += 1
                        t2 = time.time()
                        r.record(20, channel=1, monitor=False)
                        rt = time.time() - t2
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
                            time_response.append(rt)
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
                                    txt = "WW_accuracy: %s of %s" % (recognized_ww, issued_ww)
                                    oscar.bot_text += txt
                                    mean_wt = sum(time_wakeup) / len(time_wakeup)
                                    mean_rt = sum(time_response) / len(time_response)
                                    print("Logging to telegram: %s" % oscar.bot_text)
                                    oscar.send_message("Done! \n"
                                                       "Rate: %s of %s\n"
                                                       "Wakeup time: %0.2fs (mean: %0.2fs)\n"
                                                       "Recognition time: %0.2fs (mean: %0.2fs)\n"
                                                       ""
                                                       % (recognized_ww, issued_ww, wt, mean_wt, rt, mean_rt))
                                    print("DONE")
                                except Exception as e:
                                    print("Error! (%s)" % e)
                            print_ww_report(report_name)
                            print("Cancel\nResult: %s/%s" % (recognized_ww, issued_ww))
                            print("Proceeding to next test")
                            r.activated = False
                            break
                    break
                else:
                    print("Trying again...")

    except KeyboardInterrupt:
        print("Test interrupted")

    if telegram_logging:
        oscar.bot_text = "Test completed!"
        oscar.send_message("Test completed!")

    print("Saving report...")
    print_ww_report(report_name)

    # stopping main recording
    main_recorder.terminate()
    print(main_recorder.data)
    main_recorder.save("ww_tests/%s_FULL_RECORDING.wav" % name)
