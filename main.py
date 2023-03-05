from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from moviepy.editor import *
import random
import string
import os


def gen_random_string():
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(10))


audio_files = []
images_files = []
_duration = 0
MAX_CHARS_PER_COMMENT = 300
MIN_CHARS_PER_COMMENT = 70
NB_OF_COMMENTS = 4
files = ["post"]
comments = ["comment_" + str(i) for i in range(1, NB_OF_COMMENTS + 1)]
files = files + comments
print (files)


def gen_audio_files():
	last_audio_at = 0
	for file in files:
		tmp_audio_file = "audios/" + gen_random_string() + ".aiff"
		os.system("say -r 160 -v Daniel -o " + tmp_audio_file + " -f" + "scraped_assets/" + file + ".txt")
		os.system("lame --silent " + tmp_audio_file + " " + tmp_audio_file.replace(".aiff", ".mp3"))
		audio = AudioFileClip(tmp_audio_file.replace(".aiff", ".mp3"))
		audio = audio.set_start(last_audio_at + 0.5)
		audio = audio.set_end(audio.duration + last_audio_at + 0.5)
		last_audio_at = audio.duration + last_audio_at + 0.5
		global _duration 
		_duration += audio.duration + 0.5
		print("Duration: " + str(_duration))
		audio_files.append(audio)

def gen_images(video_w, video_h):
	last_image_at = 0
	for audio,image in zip(audio_files, files):
		image = ImageClip("scraped_assets/" + image + ".png")
		image = image.resize((video_w - video_w / 6) / image.w)
		image = image.set_start(last_image_at + 0.5)
		image = image.set_end(audio.duration + last_image_at + 0.5)
		last_image_at = audio.duration + last_image_at + 0.5
		images_files.append(image)

def generate_video():
	filename = open("scraped_assets/post.txt", "r").read().replace("[[pbas 47]]","")[:99].replace("/", "-")
	video_name = "background_videos/" + os.listdir("background_videos")[random.randint(0, len(os.listdir("background_videos")) - 1)]
	print("picked video " + video_name)
	video = VideoFileClip(video_name)
	gen_audio_files()
	gen_images(video.w, video.h)
	images = []
	for image in images_files:
		image = image.set_position(("center", "center"))
		images.append(image)
	start_before = video.duration - _duration
	start = random.random() * start_before
	video = video.subclip(start, start + _duration)
	video = video.set_audio(None)
	video = CompositeVideoClip([video] + images)
	video = video.set_audio(CompositeAudioClip(audio_files))
	video.write_videofile("output_videos/" + filename + ".mp4")
	os.system("rm -rf audios/*.mp3 audios/*.aiff")
	os.system("rm -rf scraped_assets/*.png scraped_assets/*.txt")

def scrape(url):
	options = webdriver.ChromeOptions()
	options.add_argument("--headless")
	username = "_Ophen"
	decoded_password = ""
	chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	login_url = "https://www.reddit.com/login/"
	chrome.get(login_url)
	time.sleep(2)
	chrome.set_window_size(1000, 1000)
	username_field = chrome.find_element(By.ID, "loginUsername")
	username_field.send_keys(username)
	password_field = chrome.find_element(By.ID, "loginPassword")
	password_field.send_keys(decoded_password)
	login_button = chrome.find_element(By.XPATH, "//button[@type='submit']")
	login_button.click()
	time.sleep(2)
	chrome.get(url + "?sort=top")
	time.sleep(20)
	try:
		area_close = chrome.find_element(By.XPATH, "//button[@aria-label='Close']")
		if area_close:
			area_close.click()
	except:
		pass
	POST = chrome.find_element(By.CLASS_NAME, "Post")
	POST.screenshot("scraped_assets/post.png")
	text = POST.find_element(By.XPATH, "//div[@data-adclicklocation='title']").text
	with open("scraped_assets/post.txt", "w") as f:
		f.write("[[pbas 47]]" + text)
	for i in range(0, 10):
		chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(1)
	time.sleep(5)
	COMMENTS = chrome.find_elements(By.CLASS_NAME, "Comment")
	counter = 0
	for i, comment in enumerate(COMMENTS):
		if "level 1" in comment.text:
			text = ""
			try:
				text = comment.find_element(By.CLASS_NAME, "RichTextJSON-root").text
				if len(text) > MAX_CHARS_PER_COMMENT or len(text) < MIN_CHARS_PER_COMMENT:
					continue
			except:
				continue
			counter += 1
			parent = comment.find_element(By.XPATH, "../../..")
			chrome.execute_script("arguments[0].scrollIntoView(true);", parent)
			chrome.execute_script("window.scrollBy(0, -100);")
			parent.screenshot("scraped_assets/comment_" + str(counter) + ".png")
			with open("scraped_assets/comment_" + str(counter) + ".txt", "w") as f:
				f.write("[[pbas 47]]" + text)
		if counter == NB_OF_COMMENTS:
			break
	chrome.quit()

if __name__ == "__main__":
	url = __import__("sys").argv[1]
	scrape(url)
	generate_video()
	with open("past.log", 'a') as log:
		log.write(url + "\n")
