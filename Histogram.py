import wx
import random
import bisect
import sys
import math

def ShimazakiMethod( data, minN = 2, maxN = None ):
	# From shimazaki@brain.riken.jp
	dataMin = float(min(data))
	T = float(max(data)) - dataMin
	dataCount = float(len(data))
	
	# Default return: all data points in one bin.
	best = ([len(data)], sys.float_info.max, 1, T)

	for N in xrange(minN, min(len(data), maxN or len(data))):
		width = T / N
		bins = [0] * N
		for x in data:
			try:
				bins[int((x-dataMin) / width)] += 1
			except IndexError:
				bins[-1] += 1
		
		kBar = dataCount / N
		v = math.fsum((k - kBar)**2 for k in bins) / N
		cost = (2.0 * kBar - v) / (width ** 2)
		if cost < best[1]:
			best = (bins, cost, N, width)

	return best
			
class Histogram(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="LineGraph"):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: StatusBar identifier. A value of -1 indicates a default value.
		@param pos: StatusBar position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param size: StatusBar size. If the default size (-1, -1) is specified
					then a default size is chosen.
		@param style: not used
		@param validator: Window validator.
		@param name: Window name.
		"""

		# Ok, let's see why we have used wx.PyControl instead of wx.Control.
		# Basically, wx.PyControl is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For StatusBar, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')

		self.data = None
		self.bins = None
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
	def DoGetBestSize(self):
		return wx.Size(100, 50)

	def SetForegroundColour(self, colour):
		wx.PyControl.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.PyControl.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		"""
		Overridden base class virtual.  By default we should use
		the same font/colour attributes as the native wx.StaticText.
		"""
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		"""
		Overridden base class virtual.  If the parent has non-default
		colours then we want this control to inherit them.
		"""
		return True

	def SetData( self, data ):
		self.bins = None
		self.data = None
		if data:
			self.data = [float(x) for x in data]
			self.dataMax = max(self.data)
			self.dataMin = min(self.data)
			self.bins = ShimazakiMethod( self.data )[0]
			self.barMax = max(self.bins)
		self.Refresh()
		
	def OnPaint(self, event):
		#dc = wx.BufferedPaintDC(self)
		dc = wx.PaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw(self, dc):		
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if not self.bins or width < 50 or height < 50:
			return

		textWidth, textHeight = dc.GetTextExtent( u'00:00' if self.dataMax < 60*60 else u'00:00:00' )
			
		xLeft = dc.GetTextExtent( unicode(self.barMax) )[0] + 4
		xRight = width - 8
		yBottom = height - textHeight - 8
		yTop = textHeight + 8

		# Draw the horizontal labels.
		# Find some reasonable tickmarks for the x axis.
		numLabels = (xRight - xLeft) / (textWidth * 1.5)
		d = (self.dataMax - self.dataMin) / float(numLabels)
		intervals = [1, 2, 5, 10, 15, 20, 30, 1*60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 1*60*60, 2*60*60, 4*60*60, 8*60*60, 12*60*60, 24*60*60]
		d = intervals[bisect.bisect_left(intervals, d, 0, len(intervals)-1)]
		dFactor = (xRight - xLeft) / (self.dataMax - self.dataMin)
		tStart = int(self.dataMin)
		tStart -= tStart % d
		if tStart < int(self.dataMin):
			tStart += d
		dc.SetPen(wx.Pen('light gray', 1))
		for t in xrange(tStart, int(self.dataMax), d):
			x = xLeft + (t - self.dataMin) * dFactor
			if x < xLeft:
				continue
			if t < 60*60:
				s = '%d:%02d' % ((t / 60), t%60)
			else:
				s = '%d:%02d:%02d' % (t/(60*60), (t / 60)%60, t%60)
			w, h = dc.GetTextExtent(s)
			dc.DrawText( s, x - w/2, yBottom + 4)
			dc.DrawText( s, x - w/2, 0 + 4 )
			dc.DrawLine( x, yBottom+2, x, yTop )
		
		# Find some reasonable tickmarks for the y axis.
		numLabels = float(yBottom - yTop) / (textHeight * 3)
		d = self.barMax / numLabels
		intervals = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500]
		d = intervals[bisect.bisect_left(intervals, d, 0, len(intervals)-1)]
		dFactor = (yBottom - yTop) / float(self.barMax)
		dc.SetPen(wx.Pen('light gray', 1))
		for i in xrange(0, self.barMax+1, d):
			s = '{}'.format(i)
			y = yBottom - int(i * dFactor)
			w, h = dc.GetTextExtent(s)
			dc.DrawText( s, xLeft - w - 2, y-textHeight/2 - 1)
			dc.DrawLine( xLeft, y, xRight, y )
		
		# set up the bars
		# thick lines with flat ends
		thick = int((xRight - xLeft) / len(self.bins))
		if thick == 0:
			return
		pen = wx.Pen('blue', thick)
		#pen = wx.Pen('black', thick)
		pen.SetCap(wx.CAP_BUTT)
		dc.SetPen(pen)
		
		x = xLeft + thick/2
		bFactor = float(yBottom - yTop) / float(self.barMax)
		for b in self.bins:
			y2 = yBottom - b * bFactor
			dc.DrawLine(x, yBottom, x, y2)
			x += thick

		# draw the baseline
		dc.SetPen(wx.Pen('black', 2))
		dc.DrawLine(xLeft, yBottom, xRight, yBottom)
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	# Data from Old Faithful
	data = [float(x) for x in 
'''4.37 3.87 4.00 4.03 3.50 4.08 2.25 4.70 1.73 4.93 1.73 4.62
3.43 4.25 1.68 3.92 3.68 3.10 4.03 1.77 4.08 1.75 3.20 1.85
4.62 1.97 4.50 3.92 4.35 2.33 3.83 1.88 4.60 1.80 4.73 1.77
4.57 1.85 3.52 4.00 3.70 3.72 4.25 3.58 3.80 3.77 3.75 2.50
4.50 4.10 3.70 3.80 3.43 4.00 2.27 4.40 4.05 4.25 3.33 2.00
4.33 2.93 4.58 1.90 3.58 3.73 3.73 1.82 4.63 3.50 4.00 3.67
1.67 4.60 1.67 4.00 1.80 4.42 1.90 4.63 2.93 3.50 1.97 4.28
1.83 4.13 1.83 4.65 4.20 3.93 4.33 1.83 4.53 2.03 4.18 4.43
4.07 4.13 3.95 4.10 2.72 4.58 1.90 4.50 1.95 4.83 4.12'''.split()]

	optimal = ShimazakiMethod( data )
	sys.stdout.write( '{}\n'.format(optimal) )
	
	bins, cost, N, width = optimal
	
	xMin = min(data)
	hMax = max(bins)
	hFactor = 1 if hMax < 40 else 40.0 / hMax
	for i, h in enumerate(bins):
		sys.stdout.write( '{:9.3f} {:9.3f}: {:6d}: {}\n'.format(xMin + i * width, xMin + (i+1) * width, h, '*' * int(h * hFactor)) )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="Histogram", size=(600,400))
	histogram = Histogram(mainWin)

	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	#histogram.SetData( [random.normalvariate(t, tVar) for x in xrange(90)] )
	histogram.SetData( data )

	mainWin.Show()
	app.MainLoop()
