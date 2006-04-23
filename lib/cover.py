# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image
from reportlab.lib import colors
import sys
import string
import os, gtk
import version
import gutils
import pango
	
exec_location = os.path.abspath(os.path.dirname(sys.argv[0]))

def cover_image(self,id):
	filename = gutils.file_chooser(_("Select image"), \
		action=gtk.FILE_CHOOSER_ACTION_OPEN, \
		buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
			gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	if filename[0]:
		cover_image_process(self, filename[0], id)
		
def cover_image_process(self, filename, id):
	size = self.cover_image_size.get_active()
	number = self.cover_image_number.get_active()
	
	if self.config.get('font', '')!='':
		fontName = "custom_font"
		pdfmetrics.registerFont(TTFont(fontName,self.config.get('font', '')))
	else:
		fontName = "Helvetica"

	if size == 0:
		#standard
		cover_x=774
		cover_y=518
	elif size == 1:
		#slim
		cover_x=757;
		cover_y=518
	else:
		#double slim
		cover_x=757
		cover_y=518
		
	# A4 landscape definition
	pageWidth = 842
	pageHeight = 595
		
	# hardcoded to A4
	pos_x=(pageWidth-cover_x)/2;
	pos_y=(pageHeight-cover_y)/2;
	
	# make a pdf
	# using a truetype font with unicode support
	c = canvas.Canvas(os.path.join(self.griffith_dir, "cover.pdf"), \
		(pageWidth, pageHeight))
	c.setFont(fontName, 8)
	# copyright line
	c.drawString(20, 20 ,_("Cover generated by Griffith v").encode('utf-8') + \
		version.pversion+" (C) 2004 Vasco Nunes - "+ \
		_("Released Under the GNU/GPL License").encode('utf-8'))
	
	# get movie information from db
	data = self.db.select_movie_by_num(id)

	for row in data:
		c.drawImage(filename, pos_x, pos_y, cover_x, cover_y)
		if number == True:
			c.setFillColor(colors.white)	
			c.rect((pageWidth/2)-13, 520, 26, 70, fill=1, stroke=0)
			c.setFillColor(colors.black)	
			c.setFont(fontName, 10)
			c.drawCentredString(pageWidth/2, 530, id)
	
	# draw cover area
	c.rect(pos_x, pos_y, cover_x, cover_y)
	
	c.showPage()
	c.save()
	self.w_print_cover_simple.hide()
	cover_file = os.path.join(self.griffith_dir, "cover.pdf")
	if self.windows:
		os.popen3("\"" + cover_file + "\"")
	else:
		os.popen3(self.pdf_reader + " " + cover_file)

def cover_simple(self, id):
	size = self.cover_simple_size.get_active()
	number = self.cover_simple_include_movie_number.get_active()
	poster = self.cover_simple_include_poster.get_active()
	
	if self.config.get('font', '')!='':
		fontName = "custom_font"
		pdfmetrics.registerFont(TTFont(fontName,self.config.get('font', '')))
	else:
		fontName = "Helvetica"
	
	if size == 0:
		#standard
		cover_x=774
		cover_y=518
	elif size == 1:
		#slim
		cover_x=757;
		cover_y=518
	else:
		#double slim
		cover_x=757
		cover_y=518
		
	# A4 landscape definition
	pageWidth = 842
	pageHeight = 595
		
	# hardcoded to A4
	pos_x=(pageWidth-cover_x)/2;
	pos_y=(pageHeight-cover_y)/2;
	# make a pdf
	c = canvas.Canvas(os.path.join(self.griffith_dir, "cover.pdf"), (pageWidth, pageHeight))
	c.setFont(fontName,8)
	
	# copyright line
	c.drawString(20,20,_("Cover generated by Griffith v").encode('utf-8') + \
		version.pversion+" (C) 2004 Vasco Nunes - "+ \
		_("Released Under the GNU/GPL License").encode('utf-8'))
	
	# draw cover area
	c.rect(pos_x, pos_y, cover_x, cover_y)
	
	# get movie information from db
	cursor = self.db.select_movie_by_num(id)
	while not cursor.EOF:
		row = cursor.GetRowAssoc(0)
		if number == True:
			c.setFont(fontName, 10)
			c.drawCentredString(pageWidth/2, 530, id)
			
		c.setFont(fontName, 16)
		c.rotate(90)
		c.drawString(60, (-pageWidth/2)-8, row['original_title'].encode('utf-8'))
		c.rotate(-90)
		if str(row['image']): 
			tmp_dest = os.path.join(self.griffith_dir, "posters")
			image = os.path.join(tmp_dest, str(row['image']+".jpg"))
			c.drawImage(image, x=(pageWidth-30)/2, y=470, width=30, height=50)
		# print movie info
		c.setFont(fontName, 8)
		textObject = c.beginText()
		textObject.setTextOrigin(pageWidth-cover_x, 300)
		textObject.setFont(fontName, 8)
		textObject.textLine(_("Original Title").encode('utf-8')+': '+str(row['original_title']).encode('utf-8'))
		textObject.textLine(_("Title").encode('utf-8')+': '+str(row['title']).encode('utf-8'))
		textObject.textLine("")
		textObject.textLine(_("Director").encode('utf-8')+': '+str(row['director']).encode('utf-8'))
		textObject.textLine("")
		textObject.textLine(_("Running Time").encode('utf-8')+': '+str(row['runtime']).encode('utf-8')+ _(" min").encode('utf-8'))
		textObject.textLine(_("Country").encode('utf-8')+': '+str(row['country']).encode('utf-8'))
		textObject.textLine(_("Genre").encode('utf-8')+': '+str(row['genre']).encode('utf-8'))
		textObject.textLine("")
		c.drawText(textObject)
		# draw bigger poster image
		if poster == True and str(row['image']):
			c.drawImage(image, x=(pageWidth-(pageWidth-cover_x)-235), y=(pageHeight/2)-125, width=180, height=250)
		cursor.MoveNext()
	c.showPage()
	c.save()
	self.w_print_cover_simple.hide()
	cover_file = os.path.join(self.griffith_dir, "cover.pdf")
	if self.windows:
		os.popen3("\"" + cover_file + "\"")
	else:
		os.popen3(self.pdf_reader + " " + cover_file)
