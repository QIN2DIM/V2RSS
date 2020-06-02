import paramiko
import os
import pyperclip
import sys
import easygui

title = '【goto】https://github.com/QIN2DIM/Alkaid'
VMess = ''
Ene_dir = 'C://V2RaySpider'
Ene_name =  'V2Ray云采姬'
outPATH = Ene_dir+'/V2Ray订阅链接.txt'

def qinse_cloud():
    global VMess
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            hostname='104.224.177.249',
            port=29710,
            username='root',
            password='DlREm0I3WiE3'

        )
        # ssh.exec_command('python')
        stdin, stdout, stderr = ssh.exec_command('python3 /qinse/first_proj/UFO_VMess云采集.py')
        VMess = stdout.read().decode()

def save_vmess():
    if not os.path.exists(Ene_dir):
        os.mkdir(Ene_dir)
    with open(outPATH,'w',) as f:
        f.write(VMess)

def GUI_PANEL():
    choice = easygui.enterbox('开启V2Ray云采集',Ene_name,default=title)
    print(choice)
    if choice:
        qinse_cloud()
        save_vmess()
        pyperclip.copy(VMess)
        easygui.enterbox('VMess订阅连接',title=Ene_name,default='{}'.format(VMess))
        os.startfile(outPATH)
    else:
        sys.exit(0)

if __name__ == '__main__':

    GUI_PANEL()
