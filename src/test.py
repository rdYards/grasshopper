from playsound import playsound
from threading import Thread

Thread(target=playsound, args=("audio/kill_yourself.mp3")).start()
print("finished")