import itchat
from utils import send_mail
import random
import time
import threading
from settings import JOBS_MAPPING
from utils import run_jenkins_job

def start_jobs(phrase, root_id):
    result = run_jenkins_job(phrase)
    itchat.send(result, root_id)


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def print_content(msg):
    # 随机时间以模拟通常的键盘输入,防止被封
    # time.sleep(random.randrange(5, 20))
    if msg['IsAt']:
        chatroom_id = msg['FromUserName']
        message = msg['Text'].split()
        if len(message) > 1:
            phrase = message[1]
            if phrase in JOBS_MAPPING:
                t = threading.Thread(target=start_jobs, args=(phrase, chatroom_id))
                t.start()
                time.sleep(random.randrange(2, 5))
                itchat.send("收到", chatroom_id)
                # t.join()

def qr_callback(uuid, status, qrcode):
    send_mail(qrcode)

itchat.auto_login(hotReload=True, qrCallback=qr_callback)
itchat.run()
