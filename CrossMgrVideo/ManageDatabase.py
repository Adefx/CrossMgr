import wx
import datetime

class ManageDatabase( wx.Dialog ):
	def __init__( self, parent, dbSize, dbName, id=wx.ID_ANY, title='', size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE ):
		super(ManageDatabase, self).__init__( parent, id, title=title, size=size, style=style )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label='Database File:'), flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( wx.TextCtrl(self, value=dbName, style=wx.TE_READONLY, size=(300,-1)), flag=wx.LEFT, border=4 )
		vs.Add( hs, flag=wx.ALL, border=4 )
			
		vs.Add( wx.StaticText(self, label='Database Size: {:.1f} meg'.format(dbSize/1048576.0)),
			flag=wx.ALL, border=4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label='Delete all data (inclusive) from'), flag=wx.ALIGN_CENTER_VERTICAL )
		tQuery = datetime.datetime.now() - datetime.timedelta(days=7)
		self.dateFrom = wx.DatePickerCtrl(
			self,
			dt=wx.DateTimeFromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE
		)
		hs.Add( self.dateFrom, flag=wx.LEFT, border=4 )
		
		hs.Add( wx.StaticText(self, label='to'), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4 )
		tQuery = datetime.datetime.now() - datetime.timedelta(days=1)
		self.dateTo = wx.DatePickerCtrl(
			self,
			dt=wx.DateTimeFromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE
		)
		hs.Add( self.dateTo, flag=wx.LEFT, border=4 )

		vs.Add( hs, flag=wx.ALL, border=4)
		
		vs.Add( wx.StaticText(self, label='Uncheck dates for min/max values.'), flag=wx.ALL, border=4 )
		vs.Add( wx.StaticText(self, label='Be Careful!  There is no undo.'), flag=wx.ALL, border=4 )
		
		btnsizer = wx.StdDialogButtonSizer()
        
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		vs.Add( btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)
		
	def GetDates( self ):
		v = self.dateFrom.GetValue()
		dateFrom = datetime.datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() ) if v else None
		v = self.dateTo.GetValue()
		dateTo = datetime.datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() ) if v else None
		return dateFrom, dateTo

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="ManageDatabase", size=(200,100))
	mainWin.Show()
	
	dlg = ManageDatabase( mainWin, 1000000, 'TestDatabase' )
	print dlg.ShowModal() == wx.ID_OK
	print dlg.GetDates()
	dlg.Destroy()
	
	app.MainLoop()
