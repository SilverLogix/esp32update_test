
_A=None
import gc,_thread,uos,usocket as socket,utime
DEFAULT_PAGE='index.html'
PAGE_404=b'HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nPage not found'
STOP_COMMAND='/stop'
THREAD_TIMEOUT=1
w_name='weufwefiui'
w_color='blue'
class WebServer:
 def __init__(self):self.server_socket=_A;self.active_thread=_A
 def handle_request(self,client_socket,server_socket):
  request=_A
  try:
   request=client_socket.makefile('rwb',0);request_lines=request.readline().decode().split('\r\n');command=_A
   for line in request_lines:
    if line.startswith('GET ')or line.startswith('POST '):command=line.split()[1];break
   if not command or command=='/':command=DEFAULT_PAGE
   if command==STOP_COMMAND:uos.dupterm(_A);client_socket.close();server_socket.close();_thread.exit();return
   response=self.get_page(command)
   if response is _A:response=PAGE_404
   client_socket.send(response)
  finally:request.close();client_socket.close();gc.collect()
 def get_page(self,page):
  try:
   with open(page,'r')as file:content=file.read();formatted_content=self.format_fstrings(content);return formatted_content.encode()
  except Exception as e:
   print('Error reading file:',e)
   return
 @staticmethod
 def format_fstrings(content):
  import re
  def eval_fstring(match):
   expr=match.group(1)
   try:allowed_globals={'name':w_name,'color':w_color};return str(eval(expr,allowed_globals))
   except Exception as e:print('Error evaluating f-string expression:',e);return match.group(0)
  pattern=re.compile('\\{([^{}]+)}');formatted_content=re.sub(pattern,eval_fstring,content);return formatted_content
 def handle_request_with_timeout(self,client_socket,server_socket):
  self.active_thread=_thread.start_new_thread(self.handle_request,(client_socket,server_socket));utime.sleep(THREAD_TIMEOUT)
  if self.active_thread is not _A:_thread.exit()
 def start(self):
  self.server_socket=socket.socket();self.server_socket.bind(('0.0.0.0',80));self.server_socket.listen(5);print('server started')
  while True:
   result=self.accept()
   if result is not _A:client_socket,addr=result;self.handle_request_with_timeout(client_socket,self.server_socket)
 def accept(self):return self.server_socket.accept()
 def stop(self):uos.dupterm(_A);self.server_socket.close();_thread.exit()
server=WebServer()
server.start()
