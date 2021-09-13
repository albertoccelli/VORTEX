# VoRTEx
A Python-based framework for the voice-recognition test automation.

## Introduction
**VoRTEx (Voice Recognition Test Execution)** was created with the aim of helping with the test of the voice recognition performances of the car infotainment systems.
The project is originally born around the database of vocal commands provided by Harman, so it's best suitable for tests on R1 radios. However, further improvements are being implemented in order for the tool to be as versatile as possible.

The test includes several voice commands recorded by native speakers, based on the Harman list. For other commands, a TTS system based on Google Translate engine will be included.
Currently on database:
1. Dutch
2. French (France) - female
3. German - female
4. Italian - male and female
5. Polish
6. Portuguese (Portugal)
7. Russian - female
8. Spanish (Spain) - female

To be added:
1. English (UK)
2. English (India)
3. English (Australia)
4. Portuguese (Brazil)
5. Arabic
6. Japanese
7. Korean
8. Chinese
9. French (Canada)
10. English (USA)
11. Spanish (Mexico)

### Coming soon features
New features are being implemented in the software as you read this. Among those, the most important are:
- **Recording and translation of the radio's answer**. This is pretty useful when dealing with languages such as russian, arabic, chinese, japanese,...

# Setup
## 1. Requirements
**Python 3.6 or higher** is needed to run the framework.
* Install [ffmpeg](https://ffmpeg.org/download.html#get-packages). 
* Install **PyAudio** by running `pip install utilities/PyAudio-0.2.11-cp39-cp39-win_amd64.whl`
* Install the remaining necessary packages by running `pip install -r requirements.txt`.

## 2. Hardware
### Sound card
The built-in pc audio card is suitable to pronounce the audio commands but not to record the response. For that an external **USB audio interface** is needed, with at least one input channel (ear/voice calibration) and one output channel (mouth/background noise). For the most complete test experience, a 2in/2out channels audio interface will be recommended (for example the Tascam UH7000).

<img src="https://tascam.com/images/products/main_en_uh-7000.jpg" width="350" >

### Speaker
#### Mouth
For high-quality tests, the usage of a **HATS** is highly recommended (i. e. the Bruel and Kjaer 4128-C). The mouth simulator will reproduce the voice commands. The level can be adjusted to reach the **nominal value of 94dBSPL** (for that, a sound calibrator will be necessary - i. e. Bruel and Kjaer 4231)

<p float="left">
  <img src="https://www.bksv.com/-/media/Images/Products/Transducers/Head-and-torso-simulators-and-ear-simulators/HATS/Type-4128C/HATS_Type4128-C_600x600.ashx?w=768&hash=7CDAB4D71A2C0F10EEB7AD2A190B42D4D34DB716" width="300">
  <img src="https://www.bksv.com/-/media/Images/Products/Transducers/Acoustic-Transducers/Acoustic-calibrators/TYPE-4231_1180x674.ashx?w=768&hash=3B3E732621D75408DDF115FB0821571C5EA6EBA5" width="400">
</p>

#### Background noise
In order to simulate the moving condition of the vehicle, a **loudspeaker** can be used (usually reproducing a filtered brown noise, from 20 to 200Hz; otherwise, a recording of the background noise can be done).

### Microphones
#### Ear
The ear microphone (the 4128-C HATS is provided with two type 3.3 ear simulators) has 2 main purposes:
* listen to the answer from the device to ensure the command has been understood (and possibly traduce/transliterate it)
* measure the environmental noise in order to apply the Lombard effect to the output file
* calibrate the loudspeaker level, if available

#### Measurement microphone
A **free-field microphone** (e.g. Bruel & Kjaer 4191/4939), placed at the MRP (mouth reference point), is used to calibrate the level of the voice.

<img src="https://www.bksv.com/-/media/New_Products/Transducers/Microphones/4191.ashx?w=768&hash=DBC3220A6663A77F6931862CA2D40543B70FFA9B" width="200" >

#### Preparing the test
The wiring should be organized as follows:
* The measurement free-field microphone should be connected to channel 1 (or L) of the sound card
* The artificial ear should be connected to channel 2 (or R) of the sound card. If available, the second ear can be connected to a third channel of the sound card for a stereo background noise recording.
* The output 1 (or L) of the sound card should be connected to the amplifier for the artificial mouth.

## 3. Test Execution



### New test
Double click on the main.py file or run `python main.py`. 
Since this is our first test, a dialog box will appear (as shown in figure).

![alt text](https://github.com/albertoccelli/VoRTEx/blob/main/docs/new_dialog.PNG?raw=true)

Choose a name for the test. Select the test file (.vrtl). Currently only the test for Harman radios (R1H, R1L, etc...) is available, so leave that. If both female and male voices are available, choose one, then select the desired microphone activation mode:
1. Manual: the microphone will be activated by pressing the PTT button on the steering wheel or on the radio touchscreen by the tester;
2. Wake-word: use the wakeword (i. e. "Hey Maserati", "Hey Uconnect",...) to activate the microphone. This is done automatically by the software (if the wakeword recorded file is available) in order to speed up the test execution.

Choose whether to apply or not the Lombard effect: if enabled, the software will measure the ambiance noise before the test execution. The noise is passed through a A-weighted filter and the gain value to apply to the voice is calculated based on the noise intensity. Check [here](https://en.wikipedia.org/wiki/Lombard_effect) for more information.

Press OK to create the new test.

![alt text](https://github.com/albertoccelli/VoRTEx/blob/main/docs/main_screenshot.PNG?raw=true)
