import sys
import utils.communication as comm
import pyaudio
import math
import numpy as np
import librosa
import time
from neopixel import *

# Setup
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0 / 33014.2)
CHANNELS = 1
RATE = 44100
INPUT_BLOCK_TIME = 0.05
CHUNK = 4096  # number of data points to read at a time
INPUT_FRAMES_PER_BLOCK = int(RATE * INPUT_BLOCK_TIME)

#print("hello")

beats_per_minute = 0
time_to_next_beat = 0
original_time_to_next_beat = 0
analyzing = True

LED_COUNT = 30
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 50
LED_INVERT = False
LED_CHANNEL = 0


# Update leds on the Raspberry Pi (G/R/B)
def update_led(strip, avglow, avgmid, avghigh):
    for i in range(strip.numPixels()):

        # Low
        if i < 10:
            if i < (avglow - 40) / 2:
                if i < 6:
                    strip.setPixelColor(i, Color(255, 0, 0))
                elif 9 > i > 5:
                    strip.setPixelColor(i, Color(255, 255, 0))
                elif i is 9:
                    strip.setPixelColor(i, Color(0, 255, 0))

            else:
                strip.setPixelColor(i, Color(0, 0, 0))

        # Mid
        if 20 > i > 10:

            # 21 < 30
            if i < (avgmid - 35) * 2:
                if i < 16:
                    strip.setPixelColor(i, Color(255, 0, 0))
                elif 19 > i > 15:
                    strip.setPixelColor(i, Color(255, 255, 0))
                elif i is 19:
                    strip.setPixelColor(i, Color(0, 255, 0))

            else:
                strip.setPixelColor(i, Color(0, 0, 0))

        # High
        if 30 > i > 20:
            if i < (avghigh - 20) * 2:
                if i < 26:
                    strip.setPixelColor(i, Color(255, 0, 0))
                elif 29 > i > 25:
                    strip.setPixelColor(i, Color(255, 255, 0))
                elif i is 29:
                    strip.setPixelColor(i, Color(0, 255, 0))

            else:
                strip.setPixelColor(i, Color(0, 0, 0))


        strip.show()
        # time.sleep(50/1000)


def update_servos():
    #TODO servo code
    {}


# Return array with decibel values
def return_db(fft):
    db_per_freq = []

    for j in range(len(fft)):
        db_per_freq.append(10. * np.log10(fft[j]))

    return db_per_freq


def callback(in_data, frame_count, time_info, status):
    global beats_per_minute
    global time_to_next_beat
    global original_time_to_next_beat
    global analyzing

    # convert data to array
    data = np.fromstring(in_data, dtype=np.float32)

    tempo, beats = librosa.beat.beat_track(y=data, sr=22050, hop_length=512)

    # Normalize ranges if they go out of bound
    if tempo >= 180:
        tempo /= 2

    if tempo < 70:
        tempo *= 2

    # print("registered tempo: ")
    # print(tempo)
    # print("registered beats: ")
    # print(beats)

    # Calculate difference of calculated tempo with global beats per minute
    difference = abs(beats_per_minute - tempo)

    # Only change bpm if there's a significant change
    if difference > 1:
        beats_per_minute = tempo
        time_to_next_beat = 60 / tempo
        original_time_to_next_beat = time_to_next_beat * 2

    # Toggle analyzing after first iteration
    analyzing = False

    # print('Estimated tempo: {:0.2f} beats per minute'.format(tempo))

    return None, pyaudio.paContinue


def parse_audio(audio_input_data, strip):
    # Decibel arrays for each frequency range
    low_freq = []
    mid_freq = []
    high_freq = []

    # Frequencies
    lower_bound = 50
    low_freq_cutoff = 200
    mid_freq_cutoff = 1000
    high_freq_cutoff = 10000

    # Fast Fourier Transform
    fft = abs(np.fft.rfft(audio_input_data).real)

    # Loop through audio data to fill frequency band arrays
    for j in range(fft.size):

        # Filter zero
        if j == 0:
            continue

        # Calculate current iteration frequency
        freq = j * (RATE / CHUNK)

        # We have no need for frequencies above this variable
        if freq > high_freq_cutoff:
            break

        # Fill frequency bands
        if lower_bound < freq < low_freq_cutoff:
            low_freq.append(fft[j])

        if low_freq_cutoff < freq < mid_freq_cutoff:
            mid_freq.append(fft[j])

        if mid_freq_cutoff < freq < high_freq_cutoff:
            high_freq.append(fft[j])

    # Calculate average decibel value for each frequency band
    low_avg = np.mean(return_db(low_freq))
    mid_avg = np.mean(return_db(mid_freq))
    high_avg = np.mean(return_db(high_freq))

    # Update leds
    update_led(strip, low_avg, mid_avg, high_avg)

    # print("Low Average db: ")
    # print(low_avg)
    #
    # print("Mid Average db: ")
    # print(mid_avg)
    #
    # print("High Average db: ")
    # print(high_avg)


class Linedance:
    def __init__(self):
        self.name = "linedance"
        self.conn = None
        self.is_stopped = False
        self.moving = False
        self.beats_per_minute = 0
        self.time_to_next_beat = 0
        self.original_time_to_next_beat = 0
        self.analyzing = True
        self.stream = None
        self.stream2 = None
        self.pa = None
        self.lib = None
        self.strip = None

    def run(self, conn):
        global time_to_next_beat
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

        # Initiate neopixel led strip
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

        # Initiate pyaudio and set settings
        self.pa = pyaudio.PyAudio()
        self.lib = pyaudio.PyAudio()

        self.stream = self.pa.open(format=FORMAT,
                         channels=CHANNELS,
                         # input_device_index=0,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK
                         )

        self.stream2 = self.lib.open(format=pyaudio.paFloat32,
                           channels=1,
                           rate=44100,
                           # input_device_index=0,
                           input=True,
                           output=False,
                           frames_per_buffer=int(44100 * 10),
                           stream_callback=callback)

        # start the stream (4)
        self.stream.start_stream()
        self.stream2.start_stream()

        while True:
            self.handleMessages()
            try:
                capture_time = time.time()                    # print("analyzing beat")

                audio_data = np.fromstring(self.stream.read(CHUNK), dtype=np.int16)
                parse_audio(audio_data, self.strip)

                capture_time_2 = time.time()
                time_to_next_beat -= capture_time_2 - capture_time

                # print("time to next beat: ")
                # print(time_to_next_beat)

                if time_to_next_beat < 0.05 and analyzing != True:
                    # print("beat!")
                    time_to_next_beat = original_time_to_next_beat
                elif analyzing:
                    {}
                    # print("analyzing beat")

            except KeyboardInterrupt:
                Looper = False
            except IOError as e:
                print("(%d) Error recording: %s" % e)

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)

            if received == "Stop":
                self.is_stopped = True
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Stopped")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()

        while self.is_stopped:
            received = comm.recv_msg(self.conn)
            if received == "Start":
                self.is_stopped = False
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()

    def unload(self):
        # stop stream (6)
        self.stream.stop_stream()
        self.stream2.stop_stream()
        self.stream.close()
        self.stream2.close()

        # close PyAudio (7)
        self.pa.terminate()
        self.lib.terminate()

linedance = None

def name():
    return linedance.name


def load():
    global linedance
    linedance = Linedance()


def unload():
    {}


def start(conn):
    try:
        linedance.run(conn)
    except KeyboardInterrupt:
        linedance.unload()
        sys.exit(1)

