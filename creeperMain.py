#!/usr/bin/env python2
import pygtk
pygtk.require("2.0")
import gtk
import httplib
from bs4 import BeautifulSoup

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

		# Frame for showing comic index
		self.frame1 = gtk.Frame("Index")
		self.frame1.show()

		# Frame for showing comic info
		self.frame2 = gtk.Frame('Info')
		self.frame2.show()

		# Text entry
		self.ComicID = gtk.Entry(5)
		self.ComicID.show()

		# Button for handling input ID
		self.SearchBtn = gtk.Button("Commit")
		self.SearchBtn.connect("clicked", self.Search, self.ComicID)
		self.SearchBtn.show()

		# Button for cleaning frame
		self.CleanBtn = gtk.Button("Clean")
		self.CleanBtn.connect('clicked', self.CleanFrame)
		self.CleanBtn.show()

		# Foot Separator
		self.FSpeparator = gtk.HSeparator()
		self.FSpeparator.show()
		
		# Packing
		self.VBox1 = gtk.VBox(False, 0)
		self.HBox1 = gtk.HBox(True, 5)
		self.HBox1.pack_start(self.label1, False, True, 0)
		self.HBox1.pack_start(self.ComicID, True, True, 0)
		self.HBox1.pack_start(self.SearchBtn, False, True, 0)
		self.HBox1.pack_start(self.CleanBtn, False, True, 0)
		self.HBox1.show()
		self.VBox1.pack_start(self.HBox1, False, True, 0)
		self.VBox1.pack_start(self.frame2, True, True, 0)
		self.VBox1.pack_start(self.frame1, True, True, 0)
		self.VBox1.pack_start(self.FSpeparator, False, True, 0)
		self.VBox1.pack_start(self.StatusBar, False, True, 0)
		self.VBox1.show()
		self.window.add(self.VBox1)
		self.window.show()
	
	def main(self):
		gtk.main()
	
	def delete(self, widget, event):
		gtk.main_quit()
		return False

	def Search(self, widget, cid):
		"""cid for Comic ID."""
		url = 'www.8comic.com'
		
		# Checking input data if a number
		if cid.get_text().isdigit() == False :
			self.StatusBar.push(0, "Please input a Comic ID!")
			return
		
		src = self.GetWebData(url, '/html/' + cid.get_text() + '.html')
		if src == None :
			return
		# Get the index
		index = self.GetComicIndex(src)
		# Get the images code
		imgcode = self.GetImgCode(cid)
		## Packing index buttons with table
		row = len(index) // 5
		row += 1 if ((len(index) % 5) != 0) else 0
		self.table1 = gtk.Table(1, 1, True)
		num = len(index)
		k = 0
		for i in range(0, row):
			for j in range(0, 5 if num > 5 else num):
				btn = gtk.Button(index[k])
				k += 1
				self.table1.attach(btn, j, j+1, i, i+1)
				btn.show()
			num -= 5
		self.table1.show()
		self.frame1.add(self.table1)
		
		# Get Comic Info
		info = self.GetComicInfo(src)
		tmps = ''
		tmps = '%s\n%s:\t%s' % (tmps, 'Name', info['Name'])
		tmps = '%s\n%s:\t%s' % (tmps, 'Intro', info['Intro'])
		self.label2 = gtk.Label(tmps)
		self.label2.show()
		self.frame2.add(self.label2)
		del tmps

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

	def GetComicIndex(self, src):
		index = BeautifulSoup(src)
		ls = []

		# Remove needless string
		for i in index.find(id='rp_ctl00_tb_comic').find_all('script'):
			i.decompose()
		
		# Generate the index
		for i in index.find(id='rp_ctl00_tb_comic').table.find_all('table'):
			if i == index.find(id='rp_ctl00_tb_comic').table.table:
				continue	# Ignore the first table
			for j in i.stripped_strings:
				ls.append(j)
			
		return ls

	def GetComicInfo(self, src):
		src = BeautifulSoup(src)
		dic = {}
		
		# Get the comic name
		dic.update({'Name': 
			src.table.find_next_sibling('table').table.table.table.get_text('', True)})

		# Get the comic introduction
		dic.update({'Intro':
			src.table.find_next_sibling('table').table.find_all('td')[-1].get_text('', True)})
		
		return dic

	def CleanFrame(self, widget):
		self.frame1.remove(self.table1)
		self.frame2.remove(self.label2)
		self.ComicID.set_text('')
		self.StatusBar.push(0, 'Ready')

	def GetImgCode(self, cid):
		"""This function will generate a tow dimension list."""
		src = self.GetWebData('www.8comic.com', '/view/' + cid.get_text() + '.html')
		codes= BeautifulSoup(src)
		codes = str(codes.find_all('script', src='')[-1])
		start = codes.find('var codes=')
		end = codes.find('.split(\'|\')')
		codes = codes[start+11:end-1].split('|')
		
		# Simulating the decoding
		itemid = cid.get_text()
		ls = []
		for i in codes:
			num = i.split(' ')[0]
			sid = i.split(' ')[1]
			did = i.split(' ')[2]
			page = i.split(' ')[3]
			code = i.split(' ')[4]
			ch = int(num) # ch for Chapter
			j = []
			for p in range(1, int(page)+1):
				m = (((p - 1) // 10) % 10) + (((p - 1) % 10) * 3)
				if p < 10:
					img = "00" + str(p)
				elif p < 100:
					img = "0" + str(p)
				else:
					img = str(p)
				img += '_' + code[m:m+3]
				url = 'img' + sid + ".8comic.com"
				path = "/" + did + "/" + itemid + "/" + num + "/" + img + ".jpg"
				j.append((url, path))
			ls.append(j)
		
		return ls

if __name__ == '__main__':
	cc = creeper()
	cc.main()
