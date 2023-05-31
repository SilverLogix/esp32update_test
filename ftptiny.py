import socket
import os
import _thread
import gc
import network
DATA_PORT=13333
class FtpTiny:
 def __init__(self):
  self.dorun=True
  self.isrunning=False
  self.cwd=os.getcwd()
  self.ftpsocket=None
  self.datasocket=None
  self.dataclient=None
 def start_listen(self):
  self.ftpsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  self.datasocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  self.ftpsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  self.datasocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  self.ftpsocket.bind(socket.getaddrinfo("0.0.0.0",21)[0][4])
  self.datasocket.bind(socket.getaddrinfo("0.0.0.0",DATA_PORT)[0][4])
  self.ftpsocket.listen(1)
  self.datasocket.listen(1)
  self.datasocket.settimeout(10)
  self.lastpayload=''
 def send_list_data(self,client):
  for file in os.listdir(self.cwd):
   stat=os.stat(self.get_absolute_path(file))
   file_permissions="drwxr-xr-x" if(stat[0]&0o170000==0o040000)else "-rw-r--r--"
   file_size=stat[6]
   description="{}    1 owner group {:>13} Jan 1  1980 {}".format(file_permissions,file_size,file)
   self.sendcmdline(client,description)
 def send_file_data(self,path,client):
  with open(path)as file:
   chunk=file.read(256)
   while len(chunk)>0:
    client.sendall(chunk)
    if len(chunk)==256:
     chunk=file.read(256)
    else:
     chunk=[]
 def save_file_data(self,path,client):
  client.settimeout(.5)
  with open(path,"w")as file:
   try:
    chunk=client.recv(256)
    while chunk and len(chunk)>0:
     file.write(chunk)
     if len(chunk)==256:
      chunk=client.recv(256)
     else:
      chunk=None
   except Exception as ex:
    pass
 def get_absolute_path(self,payload):
  rslt=payload
  if not payload.startswith("/"):
   if len(self.cwd)>1:
    rslt=self.cwd+"/"+payload
   else:
    rslt=self.cwd+payload
  if len(rslt)>1:
   return rslt.rstrip("/")
  return rslt
 def stop(self):
  self.dorun=False
  self.thread=0
 def start(self):
  if not self.isrunning:
   self.dorun=True
   _thread.stack_size(2048)
   tid=_thread.start_new_thread(self.runserver,())
   print("FTP Stack:", _thread.stack_size())
   self.thread=tid
   print("FTP Server Listening\n")
  else:
   print("An instance is already running.")
 def sendcmdline(self,cl,txt):
  cl.sendall(txt)
  cl.sendall("\r\n")
 def closeclient(self):
  if self.dataclient:
   self.dataclient.close()
   self.dataclient=None
 def client(self,cl):
  return self.dataclient if self.dataclient else cl
 def _handle_command(self,cl,command,payload):
  if command=="USER":
   self.sendcmdline(cl,"230 Logged in.")
  elif command=="SYST":
   self.sendcmdline(cl,"215 ESP32 MicroPython")
  elif command=="SYST":
   self.sendcmdline(cl,"502")
  elif command=="PWD":
   self.sendcmdline(cl,'257 "{}"'.format(self.cwd))
  elif command=="CWD":
   path=self.get_absolute_path(payload)
   try:
    os.chdir(path)
    self.sendcmdline(cl,'250 Directory changed successfully')
   except:
    self.sendcmdline(cl,'550 Failed to change directory')
   finally:
    self.cwd=os.getcwd()
  elif command=="EPSV":
   self.sendcmdline(cl,'502')
  elif command=="TYPE":
   self.sendcmdline(cl,'200 Transfer mode set')
  elif command=="SIZE":
   path=self.get_absolute_path(payload)
   try:
    size=os.stat(path)[6]
    self.sendcmdline(cl,'213 {}'.format(size))
   except:
    self.sendcmdline(cl,'550 Could not get file size')
  elif command=="QUIT":
   self.sendcmdline(cl,'221 Bye.')
  elif command=="PASV":
   addr=network.WLAN().ifconfig()[0]
   self.sendcmdline(cl,'227 Entering Passive Mode ({},{},{}).'.format(addr.replace('.',','),DATA_PORT>>8,DATA_PORT%256))
   self.dataclient,data_addr=self.datasocket.accept()
   print("FTP Data connection from:",data_addr)
  elif command=="LIST":
   try:
    self.send_list_data(self.client(cl))
    self.closeclient()
    self.sendcmdline(cl,"150 Here comes the directory listing.")
    self.sendcmdline(cl,"226 Listed.")
   except:
    self.sendcmdline(cl,'550 Failed to list directory')
   finally:
    self.closeclient()
  elif command=="RETR":
   try:
    self.send_file_data(self.get_absolute_path(payload),self.client(cl))
    self.closeclient()
    self.sendcmdline(cl,"150 Opening data connection.")
    self.sendcmdline(cl,"226 Transfer complete.")
   except:
    self.sendcmdline(cl,'550 Failed to send file')
   self.closeclient()
  elif command=="STOR":
   try:
    self.sendcmdline(cl,"150 Ok to send data.")
    self.save_file_data(self.get_absolute_path(payload),self.client(cl))
    self.closeclient()
    print("Finished receiving file")
    self.sendcmdline(cl,"226 Transfer complete.")
   except Exception as ex:
    print("Failed to receive file: "+str(ex))
    self.sendcmdline(cl,'550 Failed to send file')
   finally:
    print("Finally closing dataclient")
    self.closeclient()
  elif command=="DELE":
   try:
    path=self.get_absolute_path(payload)
    os.remove(path)
    print("Deleted file: "+path)
    self.sendcmdline(cl,"250 File deleted ok.")
   except Exception as ex:
    print("Failed to delete file: "+str(ex))
    self.sendcmdline(cl,'550 Failed to delete file.')
   finally:
    self.closeclient()
  elif command=="MKD":
   try:
    path=self.get_absolute_path(payload)
    os.mkdir(path)
    print("Create folder: "+path)
    self.sendcmdline(cl,"257 Path created ok.")
   except Exception as ex:
    print("Failed to create folder: "+str(ex))
    self.sendcmdline(cl,'550 Failed to create folder.')
   finally:
    self.closeclient()
  elif command=="RMD":
   try:
    path=self.get_absolute_path(payload)
    os.rmdir(path)
    print("Deleted folder: "+path)
    self.sendcmdline(cl,"250 Folder deleted ok.")
   except Exception as ex:
    print("Failed to delete folder: "+str(ex))
    self.sendcmdline(cl,'550 Failed to delete file.')
   finally:
    self.closeclient()
  elif command=="CDUP":
   try:
    if self.cwd and len(self.cwd)>1:
     paths=self.cwd.split('/')
     xpat='/'+'/'.join(paths[:-1])
    else:
     xpat='/'
    os.chdir(xpat)
    self.cwd=xpat
    print("Go to parent: "+xpat)
    self.sendcmdline(cl,"250 Went to parent folder.")
   except Exception as ex:
    print("Failed to delete folder: "+str(ex))
    self.sendcmdline(cl,'550 Failed to go to parent.')
   finally:
    self.closeclient()
  elif command=="RNFR":
   self.lastpayload=payload
   self.sendcmdline(cl,"226 Starting rename.")
  elif command=="RNTO":
   if self.lastpayload:
    try:
     os.rename(self.lastpayload,payload)
     self.sendcmdline(cl,"250 Renamed file.")
    except Exception as ex:
     print("Failed to rename file: "+str(ex))
     self.sendcmdline(cl,'550 Failed to rename file.')
    finally:
     self.closeclient()
     self.lastpayload=None
  else:
   self.sendcmdline(cl,"502 Unsupported command.")
   print("Unsupported command {} with payload {}".format(command,payload))
 def runserver(self):
  self.isrunning=True
  try:
   self.start_listen()
   while self.dorun:
    cl,remote_addr=self.ftpsocket.accept()
    cl.settimeout(300)
    try:
     print("FTP connection from:",remote_addr)
     self.sendcmdline(cl,"220 Hello. Welcome to FtpTiny.")
     while self.dorun:
      data=cl.readline().decode("utf-8").replace("\r\n","")
      if len(data)<=0:
       print("Client is gone")
       break
      command,payload=(data.split(" ")+[""])[:2]
      command=command.upper()
      print("Command={}, Payload={}".format(command,payload))
      self._handle_command(cl,command,payload)
      gc.collect()
    except Exception as ex:
     print(str(ex))
    finally:
     print("Closing dataclient socket")
     cl.close()
  except Exception as ex:
   print("TinyFtp error: "+str(ex))
  finally:
   self.isrunning=False
   self.closeclient()
   self.datasocket.close()
   self.ftpsocket.close()
   gc.collect()
