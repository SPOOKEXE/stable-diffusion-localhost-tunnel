import base64
import os

from PIL import Image
from time import sleep
from typing import Callable
from pyngrok import ngrok
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

DISPLAY_DIRECTORY = "D:\\Adt\\StableDiffusionNSFW\\stable-diffusion-webui\\outputs\\out"
NGROK_CONNECTION = "https://3a653e8fe9ce.ngrok.app"

def string_to_bytes(string : str) -> bytes:
	return bytes(string, "utf-8")

def move_items_to( parent : str, to_this : str ) -> None:
	for filename in os.listdir(parent):
		try:
			print( os.path.join(parent, filename) )
			os.rename( os.path.join(parent, filename), os.path.join(to_this, filename) )
		except:
			pass

def update_folder_for_compresses( directory : str ) -> None:
	filenames = os.listdir(directory)
	filenames = filter( lambda x: x.endswith(".png") or x.endswith(".jpg") or x.endswith(".jpeg"), filenames )
	for folder_name in os.listdir(directory):
		dirpath = os.path.join(directory, folder_name)
		if os.path.isdir( dirpath ):
			move_items_to( dirpath, directory )
	for filename in filenames:
		filepath = os.path.join( directory, filename )
		compress_filepath = os.path.splitext(filepath)[0] + "_temp.webp"
		if not os.path.exists(compress_filepath):
			img = Image.open(filepath)
			img.thumbnail((128,128))
			img = img.convert('RGB')
			img.save( compress_filepath, optimize=True )

def get_html_page( directory=DISPLAY_DIRECTORY ) -> str:
	def get_creation_time( filename : str ) -> int:
		return os.path.getctime(os.path.join(directory, filename))

	update_folder_for_compresses( directory )

	img_tags = []
	filenames = os.listdir( directory )
	filenames = filter(lambda x: x.endswith(".webp"), filenames )
	filenames = sorted(filenames, key=get_creation_time)
	filenames.reverse()
	filenames = filenames[:50]
	for filename in filenames:
		filepath = os.path.join( directory, filename )
		base64_utf8_str = base64.b64encode( open(filepath, "rb").read() ).decode('utf-8')
		filename = filename.replace('_temp.webp', '.png')
		img_tags.append(f'<a href={NGROK_CONNECTION}/{filename}><img src="data:image/webp;base64,{base64_utf8_str}" style="width:128px;height:128px;"></b>')
	img_tags = "\n".join(img_tags)
	return f"""
<!DOCTYPE html>
<html>
<head> <title>Generated Images</title> </head>
{img_tags}
</html>
"""

class LocalHost:

	class ThreadedServerResponder(BaseHTTPRequestHandler):
		def _write_wfile(self, message : str) -> None:
			self.wfile.write( string_to_bytes(message) )

		def do_GET(self):
			print(self.path)
			ext = self.path.endswith(".png") and "png" or "jpg"
			isImagePath = self.path.endswith(".png") or self.path.endswith('jpg')

			# send response status code
			self.send_response(200)
			# send header information
			self.send_header("Content-Type", isImagePath and f"image/{ext}" or "text/html")
			# end headers and close response
			self.end_headers()

			if isImagePath:
				filepath = os.path.join(DISPLAY_DIRECTORY, self.path[1:])
				filepath = filepath.replace('webp', 'png')
				# base64_utf8_str = base64.b64encode( open(filepath, "rb").read() ).decode('utf-8')
				# self._write_wfile( f"data:image/webp;base64,{base64_utf8_str}" )
				self.wfile.write( open(filepath, "rb").read() )
			else:
				self._write_wfile( get_html_page( ) )

		# prevent console logs
		def log_message(self, format, *args):
			return

	class ServerThreadWrapper:
		webserver : HTTPServer = None

		server_thread : Thread = None
		shutdown_callback_thread : Thread = None

		def shutdown(self) -> None:
			self.webserver.shutdown()

		def join_thread_callback(self, thread : Thread, callback : Callable):
			thread.join()
			callback(self)

		def thread_ended_callback(self, main_thread : Thread, callback) -> Thread:
			callback_thread = Thread(target=self.join_thread_callback, args=(main_thread, callback))
			callback_thread.start()
			return callback_thread

		def start(self, webserver=None, server_closed_callback=None):
			self.webserver = webserver
			if webserver == None:
				return
			server_thread : Thread = Thread(target=webserver.serve_forever)
			self.server_thread = server_thread
			print(f"Server Starting @ {self.webserver.server_address}")
			server_thread.start()
			if server_closed_callback != None:
				self.shutdown_callback_thread = self.thread_ended_callback(server_thread, server_closed_callback)

		def __init__(self, webserver=None, server_closed_callback=None):
			self.start(webserver=webserver, server_closed_callback=server_closed_callback)

	def start_local_host(port=500) -> ServerThreadWrapper:
		customThreadedResponder = LocalHost.ThreadedServerResponder
		customThreadedResponder.webserver = None
		LocalHost.webServer = HTTPServer(('localhost', port), customThreadedResponder)
		def ThreadExitCallback(self):
			print("Server Closed")
			LocalHost.webServer.server_close()
		return LocalHost.ServerThreadWrapper(webserver=LocalHost.webServer, server_closed_callback=ThreadExitCallback)

webserver = LocalHost.start_local_host()
while True:
	try:
		sleep(0.1)
	except KeyboardInterrupt:
		break
webserver.shutdown()
