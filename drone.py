import winsound
import random
def beep():
	winsound.Beep(random.randint(250, 5000), random.randint(500, 5000))
beep()
