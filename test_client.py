import paramiko
import threading

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('localhost',port=9000, username='root', password='toor')
chan = client.get_transport().open_session()
chan.send('Hey i am connected :)')
print(chan.recv(1024))
client.close
