#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#-------		Math Prelab experiment 			- Written by Liam Booth--------#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# REV 0.0 - Example menu navigation - 13/11/2019 19:29pm						#
# REV 0.1 - Plotter intergrated with slider functionality - 20/11/2019 10:43am	#
# REV 0.2 - Q calculator added - 01/12/2019 17:28pm								#
# REV 0.3 - axis swapper added to plotter - 20/12/2019 13:19pm					#
# REV 0.4 - xlsx exporter for excluded data points - 03/01/2020 23:51pm			#
#-------------------------------------------------------------------------------#
#++++++++++++++++++++++++++ Notes and comments! ++++++++++++++++++++++++++++++++#
# 
#-------------------------------------------------------------------------------#
# Send ONLY comments, love, and affection to liam.booth2014@hull.ac.uk			#
#-------------------------------------------------------------------------------#
import time
import kivy
import base64
import datetime
import random
import xlsxwriter
import io
from io import BytesIO # for putting image in to xlsx
from io import StringIO
import sqlite3

from scipy import stats
from scipy import optimize
from lmfit import Model

import numpy as np
from numpy import linalg, exp, pi, sqrt


# import matplotlib for making and customising plots, with kivy garden extention
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
import matplotlib.pyplot as plt

# import main libraries, import object types and layouts
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.properties import (StringProperty, ObjectProperty, 
OptionProperty, NumericProperty, ListProperty, BooleanProperty)
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior

# import screen features
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider

from rangeslider import RangeSlider

import q_calculator
from q_calculator import Q_addition, find_elements

# load in kv file, deals with cosmetics of each screen
kv = """
# load in main menu screen

# load in main menu screen
<MenuScreen>:
	canvas.before:
		Color:
			rgba: 0.3, 0.3, 0.3, 1
		Rectangle:
			size: self.size
		Color:
			rgba: 0.8, 0.8, 0.8, 1                
		Rectangle:
			size: 2000, 8
			pos: root.x, root.height*3/4-2
		Color:
			rgba: 0, 0, 0, 0.9                
		Rectangle:
			size: 2000, 6
			pos: root.x, root.height*3/4-6
    GridLayout:
		cols:1 
		rows:2
        orientation: 'vertical'
        padding: 0
        spacing: 1
        size_hint: 1, 1
        GridLayout:
			cols: 1
			rows: 1
			size_hint: 1, 0.35
			#color: 1.0,1.0,1.0,1.0
			Label:
				#size_hint: 1, 0.5
				text: '--Arithmetic Experiment--'
				color: root.textcolour
				font_size: 54
				size_hint: 1, 0.1
				#pos_hint_y: 0.1
        GridLayout
            cols:2
            GridLayout:
                cols: 1
                rows: 2
                orientation: 'vertical'
                padding: 0
                spacing: 1
                size_hint: 0.25, 1
                Button: # 
                    size_hint: 0.5, 0.25
                    text: 'Select Participants'
                    font_size: 30
                    on_press:
						root.manager.current = 'participant'
                        root.manager.transition.direction = 'left'
				Button: # 
                    size_hint: 0.5, 0.25
                    text: 'Q Calculator'
                    font_size: 30
                    on_press:
						root.manager.current = 'calculator'
                        root.manager.transition.direction = 'left'	
<SelectableLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if root.selected else (0, 0, 0, .1)
        Rectangle:
            pos: self.pos
            size: self.size
			
<SelectparticipantScreen>:
	BoxLayout:
        canvas:
            Color:
                rgba: 0.3, 0.3, 0.3, 1
            Rectangle:
                size: self.size
        orientation: 'vertical'
        GridLayout:
            cols: 2
            rows: 2
            size_hint_y: .25
            height: dp(54)
            padding: dp(8)
            spacing: dp(16)
			BoxLayout:
				Button: # Go to normal plot
					text: 'Plot selected'
					font_size: 22
					on_press:
						root.plot()
			BoxLayout:
				Button:
					text: 'Select all'
					font_size: 22
					on_release:
						root.select_all()
			BoxLayout:
				Button:
					text: 'Deselect all'
					font_size: 22
					on_release:
						root.clear_all()
						controller.clear_all()
			BoxLayout:
				Label:
					font_size: 22
					text: 'Combine data'	
				CheckBox:
					id: combinecheckbox
					#on_active: root.update_plots(spinner_x.text, spinner_y.text)
        RecycleView:
            id: rv
            scroll_type: ['bars', 'content']
            scroll_wheel_distance: dp(114)
            bar_width: dp(10)
            viewclass: 'SelectableLabel'
            SelectableRecycleBoxLayout:
				id: controller
				key_selection: 'selectable'
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                multiselect: True
                touch_multiselect: True
                spacing: dp(2)

<PlottingScreen>:
	plot : plot
    BoxLayout:
        canvas:
            Color:
                rgba: 0.3, 0.3, 0.3, 1
            Rectangle:
                size: self.size
        orientation: 'vertical'
		
        GridLayout:
            cols: 1
            rows: 5
            height: dp(54)
            padding: dp(8)
            spacing: dp(16)
			
			MyRangeSlider:
				id: sliderx2
				size_hint_y: 0.02
				orientation: 'horizontal'
				step: 1
				value1: 0
				value2: 7.0
				max: root.upperx
				min: root.lowerx
				step: (root.upperx-root.lowerx)/40
				on_value: root.update_plots(spinner_x.text, spinner_y.text)
			
			GridLayout:
				cols: 3
				rows: 1
				MyRangeSlider:
					id: slidery
					size_hint_x: 0.04
					orientation: 'vertical'
					step: 1
					value1: 0
					value2: 100
					max: root.uppery
					min: root.lowery
					step: (root.upperx-root.lowerx)/40
					on_value: root.limitdata()
					#on_value: root.update_plots(spinner_x.text, spinner_y.text)
				BoxLayout:
					id: plot
				MyRangeSlider:
					id: slidery2
					size_hint_x: 0.04
					orientation: 'vertical'
					step: 1
					value1: 0
					value2: 100
					max: root.uppery
					min: root.lowery
					step: (root.upperx-root.lowerx)/40
					#on_value: root.limitdata()
					on_value: root.update_plots(spinner_x.text, spinner_y.text)
				
			MyRangeSlider:
				id: sliderx
				size_hint_y: 0.02
				orientation: 'horizontal'
				step: 1
				value1: 0
				value2: 7.0
				max: root.upperx
				min: root.lowerx
				step: (root.upperx-root.lowerx)/40
				#on_value: root.update_plots(spinner_x.text, spinner_y.text)
				on_value: root.limitdata()
				
			GridLayout:
				cols: 6
				rows: 2
				size_hint_y: 0.1
				Button: # Go to normal plot
					text: 'Export All'
					font_size: 16
					on_press: root.xlsx_all()
				Label:
					color: 1,1,1,1
					text: 'X axis:' 
					font_size: 16
				Spinner:
					id: spinner_x
					text: "Q value"
					values: 
					on_text: root.changeaxisdata(spinner_x.text, spinner_y.text)
				Label:
					color: 1,1,1,1
					text: 'Y Axis:' 
					font_size: 16
				Spinner:
					id: spinner_y
					text: "Time"
					values: 
					on_text: root.changeaxisdata(spinner_x.text, spinner_y.text)
				Button: # Go to normal plot
					text: 'Menu'
					font_size: 16
					on_press:
						root.manager.current = 'menu'
						root.manager.transition.direction = 'left'	
				
				Button: # Go to normal plot
					text: 'Export Excluded'
					font_size: 16
					on_press: root.xlsx_outliers()
				BoxLayout:
					Label:
						font_size: 16
						text: 'Best Fit'	
					CheckBox:
						id: bestfitcheckbox
						on_active: root.update_plots(spinner_x.text, spinner_y.text)
				
				BoxLayout:
					Label:
						font_size: 16
						text: 'Curve Fit'	
					CheckBox:
						id: curvecheckbox
						on_active: root.update_plots(spinner_x.text, spinner_y.text)

				BoxLayout:
					Label:
						font_size: 16
						text: 'Colour Deviation'	
					CheckBox:
						id: colourcheckbox
						on_active: root.update_plots(spinner_x.text, spinner_y.text)
						
				BoxLayout:
					Label:
						font_size: 16
						text: 'Keep Limits'	
					CheckBox:
						id: limitscheckbox
						on_active: root.setlimitdata()
						
				

<MyRangeSlider@RangeSlider>:
    Label:
		text: str(round(root.value1,2))
		pos: (root.value1_pos[0] - sp(16), root.center_y - sp(16)) if root.orientation == 'horizontal' else (root.center_x - sp(16), root.value1_pos[1] - sp(16))
		size_hint: 0.5, None
		size: sp(32), sp(32)
	Label:
		text: str(round(root.value2,2))
		pos: (root.value2_pos[0] - sp(16), root.center_y - sp(16)) if root.orientation == 'horizontal' else (root.center_x - sp(16), root.value2_pos[1] - sp(16))
		size_hint: 0.5, None
		size: sp(32), sp(32)
						
# Draws screen for displaying current question to particpant						
<QcalculatorScreen>:
	canvas.before:
		Color:
			rgba: 0.3, 0.3, 0.3, 1
		Rectangle:
			size: self.size
	GridLayout:
		cols: 3
		rows: 3
        orientation: 'vertical'
        padding: 0
        spacing: 1
        size_hint: 1, 1
		Label:
			color: 1, 1, 1, 1
			text: 'Input first digit'
			font_size: 22
		Label:
			color: 1, 1, 1, 1
			text: 'Input second digit'
			font_size: 22
		Label:
			color: 1, 1, 1, 1
			text: 'Answer is'
			font_size: 22	
		TextInput:
			id: first
			text: 'Input first number'
			font_size: 22
			multiline: False
			on_touch_down: if self.collide_point(*args[1].pos): self.text = ""
			on_text_validate: 
				root.Calculate_Q(first.text, second.text)		
		TextInput:
			id: second
			text: 'Input second number'
			font_size: 22
			multiline: False
			on_touch_down: if self.collide_point(*args[1].pos): self.text = ""
			on_text_validate: 
				root.Calculate_Q(first.text, second.text)	
		Label:
			color: 1, 1, 1, 1
			text: root.display_answer
			font_size: 26
		
		Label:
			color: 1, 1, 1, 1
			text: 'Q value for input digits is : '
			font_size: 22
		
		Label:
			color: 1, 1, 1, 1
			text: root.display_q
			font_size: 30		
		Button: # Go to normal plot
			size_hint: 0.5, 0.25
			text: 'Menu'
			font_size: 26
			on_press:
				root.manager.current = 'menu'
				root.manager.transition.direction = 'left'	
"""
Builder.load_string(kv)
combineplots = [] # holder for combining plots recycleview 

conn = sqlite3.connect("participantmerged.db")
c = conn.cursor()
# Draw Menu screen
class MenuScreen(Screen):
	def __init__(self,**kwargs):
		self.textcolour = [1,1,1,1]
		self.backcolour = [0.3,0.3,0.3,1]
		self.buttoncolour = [0.3,0.3,0.3,1]
		super(MenuScreen, self).__init__(**kwargs)	# needed for real time redraws of the screen
	
	def reset_database(self):
		conn = sqlite3.connect("participantmerged.db")
		c = conn.cursor()
		c.execute("DROP TABLE IF EXISTS participants")
		c.execute("CREATE TABLE participants (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, num INTEGER);")

# Adds selectable labels to lists (recycleview)
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,RecycleBoxLayout):
	def clear_all(self):
		self.clear_selection()
			
# Create action on selectable list, for example apply selection remembers previous selection and saves to db
class SelectableLabel(RecycleDataViewBehavior, Label, LayoutSelectionBehavior):
	''' Add selection support to the Label '''
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)
	index = int
    
	def refresh_view_attrs(self, rv, index, data):
		''' Catch and handle the view changes '''
		self.index = index
		return super(SelectableLabel, self).refresh_view_attrs(
			rv, index, data)

	def on_touch_down(self, touch):
		''' Add selection on touch down '''
		if super(SelectableLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		''' Respond to the selection of items in the view. '''
		self.selected = is_selected
		if self.selected:
			print("selection changed to {0}".format(rv.data[index]))
			if rv.data[index] in combineplots:
				pass
			else:
				combineplots.append(rv.data[index])
			try:
				self.select_node(index)
			except:
				pass
		else:
			print("selection removed for {0}".format(rv.data[index]))
			if rv.data[index] in combineplots:
				combineplots.remove(rv.data[index])
			else:
				pass
		
# Screen for selecting user to plot      
class SelectparticipantScreen(Screen):
	def __init__(self, **kwargs):
		super(SelectparticipantScreen, self).__init__(**kwargs)
		c.execute("SELECT * FROM participants")
		rows = c.fetchall()
		self.ids.rv.data = [{'text':'participant'+str(row[0])}for row in rows]  
        
	def plot(self): # selects participants from list new value to database
		participants = []
		for participant in combineplots:
			participants.append(str(participant)[10:-2])
		if len(participants) > 0:	
			if self.ids.combinecheckbox.state is 'down':	
				sm.get_screen('plot').loaddata(participants, "True") # Will comebine all participant data.
				sm.current = ('plot')
			else:
				sm.get_screen('plot').loaddata(participants, "False") # Colour codes participant data points.
				sm.current = 'plot'
				
	def select_all(self):
		for num in range(len(self.ids.rv.data)):
			SelectableLabel.apply_selection(self.ids.controller, self.ids.rv, num, True)

			
	def clear_all(self):
		for num in range(len(self.ids.rv.data)):
			SelectableLabel.apply_selection(self.ids.controller, self.ids.rv, num, False)
		

# Q-value calculator screen
class QcalculatorScreen(Screen):	
	display_answer = StringProperty()
	display_q = StringProperty()
	
	def __init__(self,**kwargs): 					# initialise plot data from newtest-256.bdf
		super(QcalculatorScreen, self).__init__(**kwargs)	# needed for real time redraws of the screen
		
	def Calculate_Q(self, input1, input2):
		try:
			int(input1)
			int(input2)
			self.display_answer = str(int(input1)+int(input2))
			self.display_q = str(round(Q_addition(int(input1),int(input2)),9))	
		except:
			pass

# Data plotter screen
class PlottingScreen(Screen):
	axis_options = ["Order","digit1","digit2", "Answer","Actual answer", "Q value", "Time", "Personal rating", "Normalised rating", "Fixed Q", "Elements"]
	upperx = NumericProperty(7.0)
	lowerx = NumericProperty(0.0)
	uppery = NumericProperty(50.0)
	lowery = NumericProperty(0.0)
	classx = []
	classy = []
	people = []
	
	def __init__(self, **kwargs):
		super(PlottingScreen, self).__init__(**kwargs)
		self.ids.spinner_x.values = self.axis_options
		self.ids.spinner_y.values = self.axis_options
		self.fig, self.ax1 = plt.subplots()
		self.mpl_canvas = self.fig.canvas
		self.plot.add_widget(self.mpl_canvas)
		
	def loaddata(self, participants, combine): #loads all data in to one big data set
		self.idnum = [[]]
		self.digit1 = [[]]
		self.digit2 = [[]]
		self.answer = [[]]
		self.actualanswer = [[]]
		self.q = [[]]
		self.time = [[]]
		self.rating = [[]]
		self.normrating = [[]]
		self.fixedq = [[]]
		self.elements = [[]]
		self.people = participants
		num = 0
		tidnum, tdigit1, tdigit2, tanswer, tactualanswer, tanswer, tq, ttime, trating, tfixedq, telements = [], [], [], [], [], [], [], [], [], [], []
		for table in participants:
			c.execute("SELECT * FROM [%s];"% (table)) #SELECT max(id)
			rows = c.fetchall() # [id, x, y, answer, actualanswer, q, time, rating]
			if combine is "False":
				tidnum, tdigit1, tdigit2, tanswer, tactualanswer, tanswer, tq, ttime, trating, tfixedq, telements = [], [], [], [], [], [], [], [], [], [], []
				for row in rows:
					tidnum.append(row[0])
					tdigit1.append(row[1])
					tdigit2.append(row[2])
					tanswer.append(row[3])
					tactualanswer.append(row[4])
					tq.append(row[5])
					ttime.append(row[6])
					trating.append(row[7])
					tfixedq.append(Q_addition(row[1],row[2]))
					telements.append(find_elements(row[1],row[2]))
				self.idnum.insert(num, tidnum)
				self.digit1.insert(num, tdigit1)
				self.digit2.insert(num, tdigit2)
				self.answer.insert(num, tanswer)
				self.actualanswer.insert(num, tactualanswer)
				self.q.insert(num, tq)
				self.time.insert(num, ttime)
				self.rating.insert(num, trating)
				self.normrating.insert(num, [(float(i)/max(trating))*100 for i in trating])# normalise to make maximum 100 and shift all points accordingly
				self.fixedq.insert(num, tfixedq)
				self.elements.insert(num, telements)
			else:
				for row in rows: # it is appended to a temoporary list and added to the 2d array list to ensure calculations for best fit lines can execute in the same fashion
					tidnum.append(row[0])
					tdigit1.append(row[1])
					tdigit2.append(row[2])
					tanswer.append(row[3])
					tactualanswer.append(row[4])
					tq.append(row[5])
					ttime.append(row[6])
					trating.append(row[7])
					tfixedq.append(Q_addition(row[1],row[2]))
					telements.append(find_elements(row[1],row[2]))
		if combine is "True":			
			self.idnum.insert(num, tidnum)
			self.digit1.insert(num, tdigit1)
			self.digit2.insert(num, tdigit2)
			self.answer.insert(num, tanswer)
			self.actualanswer.insert(num, tactualanswer)
			self.q.insert(num, tq)
			self.time.insert(num, ttime)
			self.rating.insert(num, trating)
			self.normrating.insert(num, [(float(i)/max(trating))*100 for i in trating])# normalise to make maximum 100 and shift all points accordingly
			self.fixedq.insert(num, tfixedq)
			self.elements.insert(num, telements)				
			num = num + 1
		self.changeaxisdata("Q value",  "Time")
	
	def changeaxisdata(self, xaxis, yaxis):
		self.classx = self.pickaxis(self.axis_options.index(xaxis))
		self.classy = self.pickaxis(self.axis_options.index(yaxis))
		if len(self.idnum) > 1:
			factor = 1
		else:
			factor = 0	
		self.upperx, self.uppery = 1, 1
		self.lowerx, self.lowery = 0, 0
		for num in range(len(self.idnum)-factor):	
			# Set slider limits
			passivex = max(self.classx[num])*1.1
			passivey = max(self.classy[num])*1.1
			if self.upperx < passivex:
				self.upperx = passivex
			if self.uppery < passivey:
				self.uppery = passivey	
			passivex = min(self.classx[num])*0.9
			passivey = min(self.classy[num])*0.9
			if self.lowerx > passivex:
				self.lowerx = passivex
			if self.lowery > passivey:
				self.lowery = passivey	
		print("lowery is "+str(self.lowery))	
		print("uppery is "+str(self.uppery))	
		self.ids.sliderx.value1 = self.lowerx
		self.ids.sliderx.value2 = self.upperx
		self.ids.slidery.value1 = self.lowery
		self.ids.slidery.value2 = self.uppery
		self.ids.sliderx2.value1 = self.lowerx
		self.ids.sliderx2.value2 = self.upperx
		self.ids.slidery2.value1 = self.lowery
		self.ids.slidery2.value2 = self.uppery
		self.update_plots(xaxis, yaxis)
	
	def update_plots(self, xaxis, yaxis,  *args):
		if len(self.idnum[0]) > 0:
			self.ax1.clear()
			x = self.classx.copy()
			y = self.classy.copy()
			minx = self.ids.sliderx.value1
			maxx = self.ids.sliderx.value2
			miny = self.ids.slidery.value1
			maxy = self.ids.slidery.value2
			r2 = 0
			if len(self.idnum) > 1:
				factor = 1
			else:
				factor = 0
				
			minx2 = self.ids.sliderx2.value1
			maxx2 = self.ids.sliderx2.value2
			miny2 = self.ids.slidery2.value1
			maxy2 = self.ids.slidery2.value2
			for num in range(len(self.idnum)-factor):	
				minplaces = np.where((np.array(x[num]) < minx2) & (np.array(y[num]) > maxy2))[0] # check minimum x values
				if len(minplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), minplaces)
					y[num] = np.delete(np.array(y[num]), minplaces)
				minplaces = np.where((np.array(y[num]) < miny2) & (np.array(x[num]) > maxx2))[0] # check minimum y values
				if len(minplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), minplaces)
					y[num] = np.delete(np.array(y[num]), minplaces)	
				maxplaces = np.where((np.array(x[num]) > maxx2) & (np.array(y[num]) < miny2))[0] # check maximum x values
				if len(maxplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), maxplaces)
					y[num] = np.delete(np.array(y[num]), maxplaces)
				maxplaces = np.where((np.array(y[num]) > maxy2) & (np.array(x[num]) < minx2))[0] # check maximum y values
				if len(maxplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), maxplaces)
					y[num] = np.delete(np.array(y[num]), maxplaces)		
				
			self.colours = [[]]	# Because I'm British!
			for num in range(len(self.idnum)-factor):

				minplaces = np.where(np.array(x[num]) < minx)[0] # check minimum x values
				if len(minplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), minplaces)
					y[num] = np.delete(np.array(y[num]), minplaces)
				minplaces = np.where(np.array(y[num]) < miny)[0] # check minimum y values
				if len(minplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), minplaces)
					y[num] = np.delete(np.array(y[num]), minplaces)	
				maxplaces = np.where(np.array(x[num]) > maxx)[0] # check maximum x values
				if len(maxplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), maxplaces)
					y[num] = np.delete(np.array(y[num]), maxplaces)
				maxplaces = np.where(np.array(y[num]) > maxy)[0] # check maximum y values
				if len(maxplaces) > 0: 	
					x[num] = np.delete(np.array(x[num]), maxplaces)
					y[num] = np.delete(np.array(y[num]), maxplaces)	
				tcolours = []
				if len(x[num]) > 1:
					x1 = 0
					y1 = stats.linregress(x[num], y[num])[1]
					p1 = np.array([x1,y1])
					x2 = self.upperx
					y2 = (x2* stats.linregress(x[num], y[num])[0])+(stats.linregress(x[num], y[num])[1])
					p2 = np.array([x2,y2])
					if self.ids.colourcheckbox.active:
						for point in range(len(x[num])):
							p3 = np.array([x[num][point], y[num][point]])
							d = np.linalg.norm(np.cross(p2-p1, p1-p3))/np.linalg.norm(p2-p1)
							tcolours.append(d)
						self.colours.insert(num, tcolours)
					r2 = stats.linregress(x[num], y[num])[2] # get r**2 value of data
					if self.ids.colourcheckbox.active:
						self.ax1.scatter(x[num], y[num], marker=".", label= self.people[num] + " r^2 " + str(round(r2,3)), c=self.colours[num],cmap="plasma")
					else:
						self.ax1.scatter(x[num], y[num], marker=".", label= self.people[num] + " r^2 " + str(round(r2,3)))
			self.ax1.set_prop_cycle(None) # initialises colours to for resetting colours when doing curved line	
			if self.ids.bestfitcheckbox.active:	# Adds line of best fit (straight)
				for num in range(len(self.idnum)-1): # ensure added for each participant
					data = stats.linregress(x[num], y[num])
					equation = str(round(data[0],2)) + "x + " + str(round(data[1],2)) 
					self.ax1.plot(np.unique(x[num]), np.poly1d(np.polyfit(x[num], y[num], 1))(np.unique(x[num])), '--',label=equation)
		
			if self.ids.curvecheckbox.active:
				self.ax1.set_prop_cycle(None) # resets colours for matching 
				gmodel = Model(self.gaussian) # bring in gaussian model function
				x = np.asarray(x)
				y = np.asarray(y)
				for num in range(len(self.idnum)-1): # ensure added for each participant
					sort_array = np.argsort(x[num]) # sort arrays by x
					pos=0
					ynew = []
					xnew = []
					for order in sort_array:
						ynew.append(y[num][order])
						pos = pos + 1
					xnew = np.sort(x[num])	
					result = gmodel.fit(ynew, x=xnew, amp=10, cen=1, wid=1)
					self.ax1.plot(xnew, result.best_fit, '-', label='curve fit '+str(num))

			if self.ids.limitscheckbox.active:
				self.ax1.set_xlim([self.aminx,self.amaxx])
				self.ax1.set_ylim([self.aminy,self.amaxy])
			self.ax1.legend()
			self.ax1.grid(True)
			self.ax1.set_xlabel(xaxis)
			self.ax1.set_ylabel(yaxis)
			self.mpl_canvas.draw_idle()
	
	# different models
	def test(self, x, a, b): #  test model
		return a * np.sin(b * x)
		
	def gaussian(self, x, amp, cen, wid): # Guassian model
		return amp * exp(-(x-cen)**2 / wid)
	
	def pickaxis(self,i): # switch statement for finding places in arrays, used for axis
		switcher={
				0:self.idnum,
				1:self.digit1,
				2:self.digit2,
				3:self.answer,
				4:self.actualanswer,
				5:self.q,
				6:self.time,
				7:self.rating,
				8:self.normrating,
				9:self.fixedq,
				10:self.elements
			}
		return switcher.get(i,"Invalid entry")
		
	# outport all excluded data points to excel file
	def xlsx_outliers(self):
		x = self.classx.copy()
		y = self.classy.copy()
		if len(self.idnum) > 1:
			factor = 1
		else:
			factor = 0
		minx = self.ids.sliderx.value1
		maxx = self.ids.sliderx.value2
		miny = self.ids.slidery.value1
		maxy = self.ids.slidery.value2
		minx2 = self.ids.sliderx2.value1
		maxx2 = self.ids.sliderx2.value2
		miny2 = self.ids.slidery2.value1
		maxy2 = self.ids.slidery2.value2
		print("making xlsx")
		title = "Excluded " + str(self.ids.spinner_x.text) + " vs " + str(self.ids.spinner_y.text) + " between " + str(int(minx)) + "-" + str(int(maxx)) + " & " + str(int(miny)) +"-" + str(int(maxy)) + ".xlsx "
		workbook = xlsxwriter.Workbook(title)
		spamwriter = workbook.add_worksheet()
		col = 0
		row = 0
		spamwriter.write(row, col, self.ids.spinner_x.text)
		spamwriter.write(row, col+1, self.ids.spinner_y.text)
		self.fig.savefig("plot1.png", format='png')
		spamwriter.insert_image(row+1, 11, 'plot1.png')
		self.setlimitdata()
		self.ax1.clear()
		self.ax1.set_prop_cycle(None) # initialises colours to for resetting colours when doing curved line	
		for num in range(len(self.idnum)-1): # ensure added for each participant
			r2 = stats.linregress(x[num], y[num])[2] # get r**2 value of data
			self.ax1.scatter(x[num], y[num], marker=".", label= "r^2 " + str(round(r2,2)))
			data = stats.linregress(x[num], y[num])
			equation = str(round(data[0],2)) + "x + " + str(round(data[1],2)) 
			self.ax1.plot(np.unique(x[num]), np.poly1d(np.polyfit(x[num], y[num], 1))(np.unique(x[num])), '--',label=equation)
		self.ax1.set_prop_cycle(None) # resets colours for matching 
		gmodel = Model(self.gaussian) # bring in gaussian model function
		x = np.asarray(x)
		y = np.asarray(y)
		for num in range(len(self.idnum)-1): # ensure added for each participant
			sort_array = np.argsort(x[num]) # sort arrays by x
			pos=0
			ynew = []
			xnew = []
			for order in sort_array:
				ynew.append(y[num][order])
				pos = pos + 1
			xnew = np.sort(x[num])	
			result = gmodel.fit(ynew, x=xnew, amp=10, cen=1, wid=1)
			self.ax1.plot(xnew, result.best_fit, '-', label='curve fit '+str(num))

		self.ax1.set_xlim([self.aminx,self.amaxx])
		self.ax1.set_ylim([self.aminy,self.amaxy])
		self.ax1.legend()
		self.ax1.grid(True)
		self.ax1.set_xlabel(self.ids.spinner_x.text)
		self.ax1.set_ylabel(self.ids.spinner_y.text)
		self.fig.savefig("plot2.png", format='png')
		spamwriter.insert_image(row+44, 11, 'plot2.png')

		row = row + 2
		for participant in range(len(self.idnum)-factor):	
			row = row + 1
			spamwriter.write(row, col, self.people[participant])
			r2 = stats.linregress(x[participant], y[participant])[2] # get r**2 value of data
			spamwriter.write(row, col+2, "Original R^2 Value")
			spamwriter.write(row, col+3, r2)
			row = row + 1
			col_names = ["Order","digit1","digit2", "Answer","Actual answer", "Q value", "Time", "Personal rating", "Normalised rating", "Modified Q", "Elements"]
			for name in col_names:
				spamwriter.write( row, col, name)
				col = col + 1
			row = row + 1
			col = 0
			maxplacesy = np.where(np.array(y[participant]) > maxy)[0] # check maximum y values
			maxplacesx = np.where(np.array(x[participant]) > maxx)[0] # check maximum x values
			minplacesy = np.where(np.array(y[participant]) < miny)[0] # check maximum y values
			minplacesx = np.where(np.array(x[participant]) < minx)[0] # check maximum x values

			maxplacesy = np.concatenate([maxplacesy, np.where((np.array(x[participant]) < minx2) & (np.array(y[participant]) > maxy2))[0]]) # check minimum x values
			maxplacesx = np.concatenate([maxplacesx, np.where((np.array(y[participant]) < miny2) & (np.array(x[participant]) > maxx2))[0]]) # check minimum y values
			minplacesy = np.concatenate([minplacesy, np.where((np.array(x[participant]) > maxx2) & (np.array(y[participant]) < miny2))[0]]) # check maximum x values
			minplacesx = np.concatenate([minplacesx, np.where((np.array(y[participant]) > maxy2) & (np.array(x[participant]) < minx2))[0]]) # check maximum y values
			if (minplacesx is not None)or(minplacesy is not None)or(maxplacesx is not None)or(maxplacesy is not None): 
				excludeddata =np.concatenate([minplacesx,minplacesy,maxplacesx,maxplacesy])
				excludeddata = np.unique(excludeddata)
				for num in excludeddata:
					datapoint = [self.idnum[participant][num],self.digit1[participant][num],self.digit2[participant][num],self.answer[participant][num],self.actualanswer[participant][num],self.q[participant][num],self.time[participant][num],self.rating[participant][num],self.normrating[participant][num],self.fixedq[participant][num]]
					for info in datapoint:				
						spamwriter.write(row, col, info)
						col = col + 1
					row = row + 1	
					col = 0	
			else:
				print("not making xlsx")
			workbook.close()
	
	def xlsx_all(self):
		x = self.classx.copy()
		y = self.classy.copy()
		if len(self.idnum) > 1:
			factor = 1
		else:
			factor = 0
		minx = self.ids.sliderx.value1
		maxx = self.ids.sliderx.value2
		miny = self.ids.slidery.value1
		maxy = self.ids.slidery.value2
		minx2 = self.ids.sliderx2.value1
		maxx2 = self.ids.sliderx2.value2
		miny2 = self.ids.slidery2.value1
		maxy2 = self.ids.slidery2.value2
		print("making xlsx")
		title = "Included " + str(self.ids.spinner_x.text) + " vs " + str(self.ids.spinner_y.text) + " between " + str(int(minx)) + "-" + str(int(maxx)) + " & " + str(int(miny)) +"-" + str(int(maxy)) + ".xlsx "
		workbook = xlsxwriter.Workbook(title)
		spamwriter = workbook.add_worksheet()
		col = 0
		row = 0
		spamwriter.write(row, col, self.ids.spinner_x.text)
		spamwriter.write(row, col+1, self.ids.spinner_y.text)
		self.fig.savefig("plot1.png", format='png')
		spamwriter.insert_image(row+1, 11, 'plot1.png')
		self.setlimitdata()
		self.ax1.clear()
		self.ax1.set_prop_cycle(None) # initialises colours to for resetting colours when doing curved line	
		for num in range(len(self.idnum)-1): # ensure added for each participant
			r2 = stats.linregress(x[num], y[num])[2] # get r**2 value of data
			self.ax1.scatter(x[num], y[num], marker=".", label= "r^2 " + str(round(r2,2)))
			data = stats.linregress(x[num], y[num])
			equation = str(round(data[0],2)) + "x + " + str(round(data[1],2)) 
			self.ax1.plot(np.unique(x[num]), np.poly1d(np.polyfit(x[num], y[num], 1))(np.unique(x[num])), '--',label=equation)
		self.ax1.set_prop_cycle(None) # resets colours for matching 
		gmodel = Model(self.gaussian) # bring in gaussian model function
		x = np.asarray(x)
		y = np.asarray(y)
		for num in range(len(self.idnum)-1): # ensure added for each participant
			sort_array = np.argsort(x[num]) # sort arrays by x
			pos=0
			ynew = []
			xnew = []
			for order in sort_array:
				ynew.append(y[num][order])
				pos = pos + 1
			xnew = np.sort(x[num])	
			result = gmodel.fit(ynew, x=xnew, amp=10, cen=1, wid=1)
			self.ax1.plot(xnew, result.best_fit, '-', label='curve fit '+str(num))

		self.ax1.set_xlim([self.aminx,self.amaxx])
		self.ax1.set_ylim([self.aminy,self.amaxy])
		self.ax1.legend()
		self.ax1.grid(True)
		self.ax1.set_xlabel(self.ids.spinner_x.text)
		self.ax1.set_ylabel(self.ids.spinner_y.text)
		self.fig.savefig("plot2.png", format='png')
		spamwriter.insert_image(row+44, 11, 'plot2.png')

		row = row + 2
		for participant in range(len(self.idnum)-factor):	
			row = row + 1
			spamwriter.write(row, col, self.people[participant])
			r2 = stats.linregress(x[participant], y[participant])[2] # get r**2 value of data
			spamwriter.write(row, col+2, "Original R^2 Value")
			spamwriter.write(row, col+3, r2)
			row = row + 1
			col_names = ["Order","digit1","digit2", "Answer","Actual answer", "Q value", "Time", "Personal rating", "Normalised rating", "Modified Q", "Elements"]
			for name in col_names:
				spamwriter.write( row, col, name)
				col = col + 1
			row = row + 1
			col = 0
			for num in range(len(x[0])):
				datapoint = [self.idnum[participant][num],self.digit1[participant][num],self.digit2[participant][num],self.answer[participant][num],self.actualanswer[participant][num],self.q[participant][num],self.time[participant][num],self.rating[participant][num],self.normrating[participant][num],self.fixedq[participant][num]]
				for info in datapoint:				
					spamwriter.write(row, col, info)
					col = col + 1
				row = row + 1	
				col = 0	
		workbook.close()
		
	def limitdata(self):
		if self.ids.sliderx.value1 > self.ids.sliderx.value2*0.99:
			self.ids.sliderx.value1 = self.ids.sliderx.value2*0.99
		if self.ids.sliderx.value2 < self.ids.sliderx.value1*1.01:
			self.ids.sliderx.value2 = self.ids.sliderx.value1*1.01
		
		if self.ids.slidery.value1 > self.ids.slidery.value2*0.99:
			self.ids.slidery.value1 = self.ids.slidery.value2*0.99
		if self.ids.slidery.value2 < self.ids.slidery.value1*1.01:
			self.ids.slidery.value2 = self.ids.slidery.value1*1.01

		self.update_plots(self.ids.spinner_x.text, self.ids.spinner_y.text)	
			
	def setlimitdata(self):
		self.amaxx = 0.0
		self.aminx = 0.0
		self.amaxy = 0.0
		self.aminy = 0.0
		x = self.classx.copy()
		y = self.classy.copy()
		if len(self.idnum) > 1:
			factor = 1
		else:
			factor = 0
		for num in range(len(self.idnum)-factor):	
			if self.amaxx < max(x[num])*1.1:
				self.amaxx = max(x[num])*1.1
			if self.aminx > min(x[num])*0.9:
				self.aminx = min(x[num])*0.9
			if self.amaxy < max(y[num])*1.1:
				self.amaxy = max(y[num])*1.1
			if self.aminy > min(y[num])*0.9:
				self.aminy = min(y[num])*0.9
		self.update_plots(self.ids.spinner_x.text, self.ids.spinner_y.text)	
	
	
# Screen manager
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu')) # main starting menu
sm.add_widget(QcalculatorScreen(name='calculator')) # q calculator screen
sm.add_widget(SelectparticipantScreen(name='participant')) # main starting menu
sm.add_widget(PlottingScreen(name='plot')) # q calculator screen


# Build the app return screenmanager
class PlotViewerApp(App):
	#liveplot = Liveplot()
	def build(self):
		return sm

if __name__ == '__main__':
	PlotViewerApp().run()	