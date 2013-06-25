import wx
import Model
import Utils
import PhotoFinish
import VideoBuffer
import os
import re
import sys

def getRiderName( info ):
	lastName = info.get('LastName','')
	firstName = info.get('FirstName','')
	if lastName:
		if firstName:
			return '%s, %s' % (lastName, firstName)
		else:
			return lastName
	return firstName
	
def getTitle( num ):
	if not num:
		return ''
		
	try:
		externalInfo = Model.race.excelLink.read()
	except:
		return str(num)
		
	info = externalInfo.get(num, {})
	name = getRiderName( info )
	if info.get('Team', ''):
		name = '%d: %s  (%s)' % (num, name, info.get('Team', '').strip())
	return name

def RescaleImage( image, width, height ):
	bWidth, bHeight = image.GetWidth(), image.GetHeight()
	# Keep the same aspect ratio.
	ar = float(bHeight) / float(bWidth)
	if width * ar > height:
		width = height / ar
	image.Rescale( int(width), int(height), wx.IMAGE_QUALITY_HIGH )
	return image
	
def RescaleBitmap( dc, bitmap, width, height ):
	bWidth, bHeight = bitmap.GetWidth(), bitmap.GetHeight()
	# Keep the same aspect ratio.
	ar = float(bHeight) / float(bWidth)
	if width * ar > height:
		width = height / ar
	image = bitmap.ConvertToImage()
	image.Rescale( int(width), int(height), wx.IMAGE_QUALITY_HIGH )
	if dc.GetDepth() == 8:
		image = image.ConvertToGreyscale()
	return image.ConvertToBitmap( dc.GetDepth() )
	
class PhotoSyncViewerDialog( wx.Dialog ):
	def __init__(
			self, parent, ID, title='Photo Sync Previewer', size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER ):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)
		
		self.timeFrames = []

		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		self.title = wx.StaticText( self, wx.ID_ANY, '' )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		
		self.scrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY )
		self.numPhotos = 40
		self.photoWidth, self.photoHeight = int(2 * 320 / 2), int(2 * 240 / 2)
		self.hgap = 4
		gs = wx.FlexGridSizer( rows = 2, cols = self.numPhotos, hgap = self.hgap, vgap = 4 )
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CrossMgrSplash.png'), wx.BITMAP_TYPE_PNG )
		self.bitmap = RescaleBitmap( wx.WindowDC(self), bitmap, self.photoWidth, self.photoHeight )
		
		self.photoBitmaps = [wx.BitmapButton(
									self.scrolledWindow, wx.ID_ANY,
									bitmap=self.bitmap, size=(self.photoWidth+4,self.photoHeight+4),
									style=wx.BU_AUTODRAW)
								for i in xrange(self.numPhotos)]
		self.photoLabels = [wx.StaticText(self.scrolledWindow, wx.ID_ANY, style=wx.ALIGN_CENTRE) for i in xrange(self.numPhotos)]
		for i, p in enumerate(self.photoLabels):
			p.SetLabel( str(i) )
		for i, w in enumerate(self.photoBitmaps):
			w.Bind( wx.EVT_BUTTON, lambda event, i = i: self.OnBitmapButton(event, i) )
		gs.AddMany( (w,0,) for w in self.photoBitmaps )
		gs.AddMany( (w,1,wx.ALIGN_CENTER_HORIZONTAL) for w in self.photoLabels )
		
		self.scrolledWindow.SetSizer( gs )
		self.scrolledWindow.Fit()
		width, height = self.scrolledWindow.GetBestSize()
		self.scrolledWindow.SetVirtualSize( (width, height) )
		self.scrolledWindow.SetScrollRate( 20, 20 )
		self.scrolledWindow.SetScrollbars( 1, 1, width, height )
		
		wx.CallAfter( self.ScrollToPicture, len(self.photoBitmaps) - 1 )
		
		self.vbs.Add( self.title, 0 )
		self.vbs.Add( self.scrolledWindow, 1, wx.EXPAND )
		
		self.SetSizer( self.vbs )
		
		displayWidth, displayHeight = wx.GetDisplaySize()
		self.SetSize( (int(displayWidth * 0.75),height + 80) )
		self.vbs.Layout()
		
		self.clear()

	def OnBitmapButton( self, event, i ):
		milliseconds = self.photoLabels[i].GetLabel()
		if milliseconds and Model.race:
			Model.race.advancePhotoMilliseconds = int( milliseconds )
			Utils.MessageOK( self, 'Advance Photo Milliseconds Set to %s' % milliseconds, 'Advance Milliseconds Set' )
		
	def OnClose( self, event ):
		self.Show( False )
		
	def ScrollToPicture( self, iPicture ):
		pos = 0
		for i, b in enumerate(self.photoBitmaps):
			if i == iPicture:
				break
			pos += b.GetSize().GetWidth() + self.hgap
		self.scrolledWindow.Scroll( pos / self.scrolledWindow.GetScrollPixelsPerUnit()[0], -1 )
			
	def OnRefresh( self, event ):
		self.refresh( self.num )
		
	def clear( self ):
		for w in self.photoBitmaps:
			w.SetBitmapLabel( self.bitmap )
		for w in self.photoLabels:
			w.SetLabel( '' )
		self.timeFrames = []
		
	def refresh( self, videoBuffer, t, num = None ):
		if not videoBuffer:
			for i in xrange(len(self.photoLabels)):
				self.photoBitmaps[i].SetBitmapLabel( wx.NullBitmap )
				self.photoLabels[i].SetLabel( '' )
			return
	
		timeFrames = videoBuffer.findBeforeAfter( t, self.numPhotos - 10, 10 )
		deltaMS = [int((tFrame - t) * 1000.0) for tFrame, frame in timeFrames]
		
		if len(timeFrames) < self.numPhotos:
			d = self.numPhotos - len(timeFrames)
			timeFrames = ([(None, None)] * d) + timeFrames
			deltaMS = ([None] * d) + deltaMS
			
		deltaMin = sys.float_info.max
		iMin = 0
		dc = wx.WindowDC( self )
		for i, (tFrame, frame) in enumerate(timeFrames):
			if deltaMS[i] is not None and abs(deltaMS[i]) < deltaMin:
				deltaMin = abs(deltaMS[i])
				iMin = i
			if deltaMS[i] is None:
				self.photoLabels[i].SetLabel( '' )
				self.photoBitmaps[i].SetBitmapLabel( wx.NullBitmap )
			else:
				self.photoLabels[i].SetLabel( str(deltaMS[i]) )
				image = PhotoFinish.PilImageToWxImage( frame )
				image = RescaleImage( image, self.photoWidth, self.photoHeight )
				bitmap = image.ConvertToBitmap( dc.GetDepth() )
				self.photoBitmaps[i].SetBitmapLabel( bitmap )

		self.title.SetLabel( getTitle(num) )
		
		picturesShown = self.GetSize().GetWidth() / (self.photoWidth + self.hgap)
		self.ScrollToPicture( max(0, iMin - picturesShown // 2) )
		self.Refresh()
		
		self.timeFrames = timeFrames
				
photoSyncViewer = None
def PhotoSyncViewerShow():
	global photoSyncViewer
	if not photoSyncViewer:
		photoSyncViewer = PhotoSyncViewer( wx.GetTopLevelParent(), wx.ID_ANY, "Photo Sync Viewer" )
	photoSyncViewer.Show( True )
	
def PhotoSyncViewerHide():
	if not photoSyncViewer:
		return
	photoSyncViewer.Show( False )
	photoSyncViewer.clear()

if __name__ == '__main__':
	import time
	import datetime
	import shutil
	
	race = Model.newRace()
	race._populate()

	app = wx.PySimpleApp()
	
	dirName = 'VideoBufferTest_Photos'
	if os.path.isdir(dirName):
		shutil.rmtree( dirName, True )
	os.mkdir( dirName )
	
	tRef = datetime.datetime.now()
	camera = PhotoFinish.SetCameraState( True )
	vb = VideoBuffer.VideoBuffer( camera, tRef, dirName )
	vb.start()
	time.sleep( 1.0 )
	
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	mainWin.Show()
	photoSyncDialog = PhotoSyncViewerDialog( mainWin, wx.ID_ANY, "PhotoSyncViewer", size=(600,400) )
	def doRefresh():
		t = (datetime.datetime.now() - tRef).total_seconds()
		wx.CallLater( 300, photoSyncDialog.refresh, vb, t, 100 )
		
	photoSyncDialog.Show()
	for d in xrange(0, 1000*60, 1000):
		wx.CallLater( d, doRefresh )
	app.MainLoop()
