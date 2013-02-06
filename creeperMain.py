#!/usr/bin/env python2
import pygtk
pygtk.require("2.0")
import gtk
import httplib

class creeper:
	def __init__(self):
		self.window = gtk.Window()
		self.window.set_title("Comic Creeper")
		self.window.set_size_request(600, 400)
		self.window.connect("delete_event", self.delete)
		
		# StatusBar
		self.StatusBar = gtk.Statusbar()
		self.StatusBar.push(0, "Ready")
		self.StatusBar.show()
		
		# Label
		self.label1 = gtk.Label("Comic ID")
		self.label1.set_justify(gtk.JUSTIFY_CENTER)
		self.label1.set_line_wrap(True)
		self.label1.show()

		# Frame
		self.frame1 = gtk.Frame("tset")
		self.frame1.show()

		# Text entry
		self.ComicID = gtk.Entry(5)
		self.ComicID.show()

		# Button for handling input ID
		self.SearchBtn = gtk.Button("Commit")
		self.SearchBtn.connect("clicked", self.Search, self.ComicID)
		self.SearchBtn.show()
		
		# Packing
		self.VBox1 = gtk.VBox(False, 0)
		self.HBox1 = gtk.HBox(True, 5)
		self.HBox1.pack_start(self.label1, False, True, 0)
		self.HBox1.pack_start(self.ComicID, True, True, 0)
		self.HBox1.pack_start(self.SearchBtn, False, True, 0)
		self.HBox1.show()
		self.VBox1.pack_start(self.HBox1, False, True, 0)
		self.VBox1.pack_start(self.frame1, True, True, 10)
		self.VBox1.pack_start(self.StatusBar, False, True, 0)
		self.VBox1.show()
		self.window.add(self.VBox1)
		self.window.show()
	
	def main(self):
		gtk.main()
	
	def delete(self, widget, event):
		gtk.main_quit()
		return False

	def Search(self, widget, cid): # cid for Comic ID
		url = 'www.8comic.com'
		
		# Checking input data if a number
		if cid.get_text().isdigit() == False :
			self.StatusBar.push(0, "Please input a Comic ID!")
			return
		
		# Get the index
		index = self.GetWebData(url, '/html/' + cid.get_text() + '.html')

	def GetWebData(self, host, path):
		get = httplib.HTTPConnection(host)
		
		get.request('GET', path, '', {'Referer': 'http://www.8comic.com/',
			'User-Agent': 'Mozilla/5.0  AppleWebKit/537.11 (KHTML, like Gecko)\
			Chromium/23.0.1271.97 Chrome/23.0.1271.97 Safari/537.11'})
		self.StatusBar.push(0, 'Loading')
		index = get.getresponse()
		self.StatusBar.push(0, str(index.status) + ' ' + index.reason)
		
		# Checking http status code
		if index.status != 200:
			get.close()
			return
		
		data = index.read().decode('big5')
		get.close()
		return data

if __name__ == '__main__':
	cc = creeper()
	cc.main()