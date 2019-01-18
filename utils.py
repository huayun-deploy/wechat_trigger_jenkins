import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.build import Build
from settings import (JOBS_MAPPING, JENKINS_URL, JENKINS_USER, JENKINS_PASS,
                      mail_host, mail_pass, mail_user, mailto_list)
from requests import HTTPError
import time


def run_jenkins_job(phrase):
    job_name = JOBS_MAPPING.get(phrase, None)
    if job_name is None:
        return "任务不存在"

    try:
        server = Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_PASS)
    except HTTPError as ex:
        return "jenkins连接出错: %s" % ex
    job = server[job_name]
    job_buildid = server.get_job(job_name).get_next_build_number()
    run_job = job.invoke()
    time.sleep(10)

    #  查看任务状态
    url = f'''{job.baseurl}/{job_buildid}/'''
    obj = Build(url, job_buildid, job)
    obj.block()
    # obj 只是获取当时的任务状态，所以需要等待任务执行完，再获取一次状态
    obj = Build(url, job_buildid, job)
    result = f'''{phrase}完成， 任务名称: {obj.name}, 执行结果:{obj.get_status()}, 耗时: {obj.get_duration().total_seconds()}秒'''
    return result





def send_mail(binary_img_data, title='微信登录', img_id='qrcode'):
    me = "华云部署团队" + "<" + mail_user + ">"
    me = "华云部署团队" + ""
    me = formataddr(("华云部署团队", mail_user))
    msg = MIMEMultipart()
    msg['Subject'] = title
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        # set data
        msg_text = MIMEText('<b>扫码登录.</b><br><img src="cid:%s"><br>' % img_id, 'html')
        msg.attach(msg_text)
        img_data = MIMEImage(binary_img_data)
        img_data.add_header('Content-ID', '<%s>' % img_id)
        msg.attach(img_data)
        # send mail
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, msg['To'], msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    # send_mail(binary_img_data=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\xc2\x00\x00\x01\xc2\x01\x00\x00\x00\x00Tc\xf4\xe8\x00\x00\x02\x8cIDATx\x9c\xed\xdaKn\x840\x10E\xd1\x92X@/\xc9[gI,\xa0\xa5JS_\x83I\x14e\x18]\x06\x88\x8f\x0f\xa3\'\xbb\\\xdd\xa2\x7f<vA"\x91H$\x12\x89\xfcGR\xe2\xd8>O^o\x91q|\xae\xf4\x90x[\xb7~\x0c$r\x95v\xa3\x87I\x8dS\x84,\x9f\xd9\xdb\x1e\x8cD\xde\xe4\x19\xad3d\x16\xaf\xcfc\xa9\x08\xce\x89\xb4\x80"\x91?\xcb\x91C}\xbc\xcfj"H\xe4oe\xcfV\x970F\x0e\x91\xc8\xef\xa5\xc6\xf8\xac\x9f,}\x1a9\xd4\x9a\xcbz0\x12\xf9M5\xde\xd3\xd8z\xcaQH\xe4*\xa7\xe3\xcc\xdc\xe7\xdd;\x07\x9c\xb7\xf2\xca\xdbi\x1c\x12y\x93VoG!\x1e\xab\xa0\xda\xe4%r\x19\xbf!\x91\xcf\xd2\x90\x95\xdf\xd9\x10\xb0+\x0f\x9e\x9f\xec\xb0E\x11\x89\\e\x15L1[\x1d\xb1(Z\xdcZ\xfa\'\x07\x12\xf9$#i\xd9\x10\xb0w"\xb1(\x1e\xb9\xad\xdb\xef;:$2\x03\xe5]\x81\xf3\xa4=G\xf5m\xad\x91US!\x91\xb7}Y?\xb6\xc9\xcb\x07d_;\x9e\xa9\xef\xed\xf2\xbbH\xe4Ej\xaes6ou\x17Izj\x93hV\xde\xbb\x02H\xa4Vq\xf4\xca\xa1s\xf06\xffn\xbc\x15\xb9V\xe3H\xe4\x9c\xbe\xb9\x06\xcf\x08\xdaU\x97S\xd1.@"\xef2&/\xaf\xc1\xb7\nY5\x04\xaaL\xd7\xa9\xceB"g9\x17L\xd9\x93\xdc\xed\x039\xa1\x05Z\xd2\x87DF\xfa*Z{\x16\xe2\xdam\x00\xebX\xeeuR$r\x91\x81j\x01\xb4\xe0\r\x1b\xf0\xca\x9aJ\xea\x1bH\xe4*}Ts/\xac|@\xef\xe3\xaaBG"\x1fd\xae\x82\xd9\xe1~O\x9f\x8cU0\x11\x12\xf9 \xa7\xaaI\xaaE\xe9\xa3n\xado\xdb\xd6!\x91\xab\xec\x0e\x80\xf6D5\xcdV\x97\xdfm\x07\x12\xb9H\xcb\xde|U?\x9aH6\x95.{;$r\x959o\xc5\xe3l\rX\x04#\x969\x8d\xdd\xd2\x87D\x9a\x8c"\xcaP\xd5J\xd5\xac\xec\xf4\x89\xdc~\xadE"Sf\x99\x94\xdd\xc9mN\xa4\xcfe\x12\x1c\x89|\x90}t\xe5\xedI\xbb&\xd20\x12\xf9 3[9[\xf5\x84\xa6Y:I\xb7(\x07\x12\xb9J\xbb\xf1m\x9d\xaf}\xe7Q\xc1\xab\xf1\xf9k\n\x12\xb9\xca\xac\xbc3Z!\xa3\xbd\xa4\xb9\n\xae;:$r\x91\xc7\xbc\xf6\xc5\xd1{\xbb\xb5\x06C"\xaf2\xa6\xac:\r\xed\xab\x8e \x12\xb9J\x0f\xd96\'\xcd7x\xd6\x068\xe2\x94\xb5:\x12\xb9\xc88,}Y~K\xfdad\xd8\xc7+\x9bH\xe4*\xffp \x91H$\x12\x89D\xfe\x13\xf9\x05\xe1\xdf?D\x8f\x85;M\x00\x00\x00\x00IEND\xaeB`\x82',
    #           )
    print(run_jenkins_job('更新前端'))
