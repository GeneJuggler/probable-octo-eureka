
# Module: Abe, A bioassay data analysis package written in Python
# Copyright (c) Gordon Webster, EMD Lexigen Research Center 2002, 2003
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""
Module: Abe, A bioassay data analysis package written in Python
Copyright 2002, 2003 Gordon Webster, EMD Lexigen research Center

ABE provides an interactive graphical user interface for the modeling and
visualization of experimental bioassay data. The sigmoidal curve from a
bioassay experiment can be modeled using either a four-parameter
dose-response model or a traditional polynomial of arbitrary degree.
A full log of all the data modeling and analysis can be saved along with
graphical images of the graphs of observed and modeled data. The fitted
parameters from the data modeling can also be saved as a table suitable
for importing into spreadsheet applications like Microsft Excel(TM).
"""

import os
import math
import Matfunc
import tkFileDialog
import string
from Tkinter import *
import xml.parsers.expat
import scipy.optimize.minpack
import Numeric
import webbrowser

global AbeVersion, AbeTitle
AbeVersion = '1.0'
AbeTitle = 'ABE ' + AbeVersion + ' - By Gordon Webster, EMD Lexigen Research Center'

global default_precision
default_precision = 1.0e-6

global default_graph_border, default_border_offset
default_graph_border = 20
default_border_offset = 5

global default_xoff, default_yoff
default_xoff = 3
default_yoff = 3

global abe_help_text, GPL_text

class Console:

    """The ABE console containing the menus and graphical display"""
    
    def __init__(self,graphpixels):
        self.gsize = graphpixels
        self.root = Tk()
        self.current = StringVar()
        self.root.resizable(width=0,height=0)
        self.root.geometry('+%d+%d' % (default_xoff,default_yoff))
        self.root.title(AbeTitle)
        self.root.protocol("WM_DELETE_WINDOW", self.adios)
        self.menuframe = Frame(self.root)
        self.menuframe.pack(fill=X)
        self.topmenu = {}
        self.topmenu['File'] = Menubutton(self.menuframe,text='File', underline=0)
        self.topmenu['File'].pack(side=LEFT,padx=5)
        self.topmenu['File'].menu=Menu(self.topmenu['File'])
        self.topmenu['File'].menu.add_command(label='Load Bioassay Data', underline=0,command = self.check_load_data)
        self.topmenu['File']['menu'] = self.topmenu['File'].menu
        self.topmenu['File'].menu.add_command(label='Save Activity Log', underline=0,command = self.save_log)
        self.topmenu['File']['menu'] = self.topmenu['File'].menu
        self.topmenu['File'].menu.add_command(label='Save Graph Image', underline=0,command = self.save_graph)
        self.topmenu['File']['menu'] = self.topmenu['File'].menu
        self.topmenu['File'].menu.add_command(label='Export Results Table', underline=0,command = self.export_results)
        self.topmenu['File']['menu'] = self.topmenu['File'].menu
        self.topmenu['File'].menu.add_command(label='Set Working Directory', underline=0,command = self.set_directory)
        self.topmenu['File']['menu'] = self.topmenu['File'].menu
        self.topmenu['File'].menu.add_command(label='Quit', underline=0,command = self.adios)
        self.topmenu['File']['menu'] = self.topmenu['File'].menu
        self.topmenu['Data'] = Menubutton(self.menuframe,text='Data', underline=0)
        self.topmenu['Data'].pack(side=LEFT,padx=5)
        self.topmenu['Data'].menu=Menu(self.topmenu['Data'])
        self.topmenu['Data'].menu.add_command(label='Process Data', underline=0,command = self.work_data)
        self.topmenu['Data']['menu'] = self.topmenu['Data'].menu
        self.topmenu['Graph'] = Menubutton(self.menuframe,text='Graph', underline=0)
        self.topmenu['Graph'].pack(side=LEFT,padx=5)
        self.topmenu['Graph'].menu=Menu(self.topmenu['Graph'])
        self.topmenu['Graph'].menu.add_command(label='Redraw Graph', underline=0,command = self.draw_graph)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.topmenu['Graph'].menu.add_separator()
        self.topmenu['Graph'].menu.add_command(label='Border Width', underline=0,command = self.set_graph_border)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.graph_key_on = IntVar()
        self.graph_key_on.set(1)
        self.topmenu['Graph'].menu.add_checkbutton(label=' Show Key',variable=self.graph_key_on)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.graph_leg_on = IntVar()
        self.graph_leg_on.set(1)
        self.topmenu['Graph'].menu.add_checkbutton(label=' Show Legend',variable=self.graph_leg_on)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.graph_fourp_on = IntVar()
        self.graph_fourp_on.set(1)
        self.topmenu['Graph'].menu.add_checkbutton(label=' Show 4-Parameter Model',variable=self.graph_fourp_on)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.graph_poly_on = IntVar()
        self.graph_poly_on.set(1)
        self.topmenu['Graph'].menu.add_checkbutton(label=' Show Polynomial Model',variable=self.graph_poly_on)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.graph_border_on = IntVar()
        self.graph_border_on.set(1)
        self.topmenu['Graph'].menu.add_checkbutton(label=' Draw Border',variable=self.graph_border_on)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.graph_ebar_on = IntVar()
        self.graph_ebar_on.set(0)
        self.topmenu['Graph'].menu.add_checkbutton(label=' Show Error Bars',variable=self.graph_ebar_on)
        self.topmenu['Graph']['menu'] = self.topmenu['Graph'].menu
        self.topmenu['Data Model'] = Menubutton(self.menuframe,text='Data Model', underline=0)
        self.topmenu['Data Model'].pack(side=LEFT,padx=5)
        self.topmenu['Data Model'].menu=Menu(self.topmenu['Data Model'])
        self.topmenu['Data Model'].menu.add_command(label='Estimate ED50', underline=0,command = self.pick_root)
        self.topmenu['Data Model']['menu'] = self.topmenu['Data Model'].menu
        self.topmenu['Data Model'].menu.add_command(label='Fit 4-Parameter Model', underline=0,command = self.fit_fourp)
        self.topmenu['Data Model']['menu'] = self.topmenu['Data Model'].menu
        self.topmenu['Data Model'].menu.add_command(label='Choose Polynomial', underline=0,command = self.choose_polynomial)
        self.topmenu['Data Model']['menu'] = self.topmenu['Data Model'].menu
        self.topmenu['Data Model'].menu.add_command(label='Fit Polynomial', underline=0,command = self.fit_polynomial)
        self.topmenu['Data Model']['menu'] = self.topmenu['Data Model'].menu
        self.topmenu['Data Model'].menu.add_command(label='Show Fitted Data', underline=0,command = self.show_fit)
        self.topmenu['Data Model']['menu'] = self.topmenu['Data Model'].menu
        self.topmenu['Options'] = Menubutton(self.menuframe,text='Options', underline=0)
        self.topmenu['Options'].pack(side=LEFT,padx=5)
        self.topmenu['Options'].menu=Menu(self.topmenu['Options'])
        self.topmenu['Options'].menu.add_command(label='4-Parameter Search', underline=0,command = self.set_fourp_opts)
        self.topmenu['Options']['menu'] = self.topmenu['Options'].menu
        self.fourp_defaults = {'ysrch':0.1, 'xsrch':0.1, 'yiter':10, 'eiter':10, 'siter':10, \
                              'slopemax':10.0, 'isiter':1000}
        self.fourp_options = {'ysrch':0.1, 'xsrch':0.1, 'yiter':10, 'eiter':10, 'siter':10, \
                              'slopemax':10.0, 'isiter':1000}
        self.topmenu['Options'].menu.add_command(label='Estimate Curve Max/Min', underline=0,command = self.pick_ymaxmin)
        self.topmenu['Options']['menu'] = self.topmenu['Options'].menu
        self.topmenu['Window'] = Menubutton(self.menuframe,text='Window', underline=0)
        self.topmenu['Window'].pack(side=LEFT,padx=5)
        self.topmenu['Window'].menu=Menu(self.topmenu['Window'])
        self.topmenu['Window'].menu.add_command(label='Activity Log', underline=0,command = self.toggle_al)
        self.topmenu['Window']['menu'] = self.topmenu['Window'].menu
        self.topmenu['Help'] = Menubutton(self.menuframe,text='Help', underline=0)
        self.topmenu['Help'].pack(side=RIGHT,padx=5)
        self.topmenu['Help'].menu=Menu(self.topmenu['Help'])
        self.topmenu['Help'].menu.add_command(label='About', underline=0,command = self.help_about)
        self.topmenu['Help']['menu'] = self.topmenu['Help'].menu
        self.topmenu['Help'].menu.add_command(label='Help', underline=0,command = self.help_help)
        self.topmenu['Help']['menu'] = self.topmenu['Help'].menu
        self.graph = Canvas(self.root,width=self.gsize,height=self.gsize,bg='white')
        self.graph.pack()
        self.base = Frame(self.root)
        self.base.pack(fill=X)
        self.status = Label(self.base,width=40,text=AbeTitle,font=('Arial',8),fg='blue',anchor=W)
        self.status.pack(fill=X)
        self.dwin = Toplevel(self.root)
        self.dwin.title("ABE "+ AbeVersion + ": Activity log")
        self.display = Text(self.dwin,width=120,height=10,font=('Arial',10),borderwidth=0)
        self.display.pack(side=LEFT,fill=BOTH,expand=YES)
        self.scroll = Scrollbar(self.dwin,orient=VERTICAL,command=self.display.yview)
        self.scroll.pack(fill=Y,expand=YES)
        self.display.configure(yscrollcommand=self.scroll.set)
        self.dwin.protocol("WM_DELETE_WINDOW", self.keep_display)
        self.root.update()
        dx = default_xoff
        dy = self.root.winfo_screenheight()- self.dwin.winfo_height() - default_yoff - 55
        self.dwin.geometry('+%d+%d' % (dx,dy))
        self.dwin.withdraw()
        self.display.tag_config('data', font=('Courier',10))
        self.update_display(AbeTitle,fmt='\n%s\n\n')
        if os.environ.has_key('ABE_PATH'):
            self.workdir = os.environ['ABE_PATH']
        else:
            self.workdir = os.getcwd()
        if os.environ.has_key('ABE_HELP'):
            self.helpfile = os.environ['ABE_HELP']
        else:
            self.helpfile = None
        self.initialize_data()
        self.root.withdraw()
        self.help_about()
        

    def initialize_data(self):

        """Initialize the bioassay data store, the Data-> menu and the graphical display"""
        
        self.data = {}
        self.bioassay = ''
        self.molecule = ''
        self.molecule_list = []
        self.in_data = 0
        self.graph_border = default_graph_border
        self.x = None
        self.y = None
        self.stderr = None
        try:
            self.topmenu['Data'].menu.delete(2,END)
            self.topmenu['Data'].menu=Menu(self.topmenu['Data'])
            self.topmenu['Data'].menu.add_command(label='Process Data', underline=0,command = self.work_data)
            self.topmenu['Data'].menu.add_separator()
        except:
            pass
        self.graph.delete(ALL)
        self.current.set('')

        
    def set_directory(self):

        """Set the current working directory"""

        wdir = tkFileDialog.askdirectory(initialdir=self.workdir)
        if wdir != '' and wdir != None:
            self.workdir = wdir

    
    def update_display(self,iolist,fmt='%s\n',tag='output'):

        """Update the text output window of the Abe Console"""

        self.display.insert(END,fmt % iolist,tag)
        self.display.see(END)


    def keep_display(self):

        """Don't let the user destroy the acitivity log window manually"""
        
        self.display.bell()
        self.whoops("Use the console 'Window' menu to Show/Hide the activity log window")
        return


    def check_load_data(self):

        """If bioassay data is already loaded, check that reloading new data is OK"""

        if self.bioassay != '':
            self.zdialog = Toplevel(self.root)
            self.zdialog.resizable(width=0,height=0)
            self.zdialog.title("Load New Data?")
            mtext = "Loading new data will erase all your current data and data models?"
            self.askq = Label(self.zdialog,text=mtext,font=('Arial',10),padx=5)
            self.askq.grid(row=0,column=0,columnspan=2,pady=5)
            self.yesq = Button(self.zdialog,text="That's OK, load new data",command=self.do_reload)
            self.yesq.grid(row=1,column=0,padx=5,pady=5,sticky=EW)
            self.noq = Button(self.zdialog,text="Whoops! Abort loading data",command=self.cancel_reload)
            self.noq.grid(row=1,column=1,padx=5,pady=5,sticky=EW)
        else:
            self.load_data()


    def do_reload(self):

        "Go ahead and load new bioassay data"""

        self.zdialog.destroy()
        self.load_data()


    def cancel_reload(self):

        "Abort loading new bioassay data"""

        self.zdialog.destroy()


    def load_data(self):

        """Reads the bioassy data from an XML file"""

        self.initialize_data()
        xmlfile = tkFileDialog.askopenfilename(title="ABE: Load Bioassay Data",initialdir=self.workdir, \
                    filetypes=[('XML Files', '*.xml'),('All Files','*.*')], defaultextension='.xml')
        if xmlfile == "": return
        if os.path.isfile(xmlfile):
            try:
                self.xmlstream = open(xmlfile, 'r')
            except:
                self.whoops("Unable to open data file:\n" + xmlfile)
                return
        self.xmlfile = xmlfile
        self.data = {}
        self.p = xml.parsers.expat.ParserCreate()
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
        pdata = 'Start'
        try:
            while pdata != '':
                pdata = self.xmlstream.readline()
                self.p.Parse(pdata)
            self.p.Parse(pdata,1)
        except:
            self.whoops("XML syntax errors in file:\n" + xmlfile)
            self.load_data_cleanup()
            return
        self.update_status(xmlfile)
        self.update_display("Bioassay data in XML format read from file:")
        self.update_display(xmlfile)
        self.xmlstream.close()
        xlabel = self.columns[self.x]
        ylabel = self.columns[self.y]
        elabel = self.columns[self.stderr]
        self.update_display("\nData columns selected:")
        self.update_display(xlabel,fmt="x    = %s\n")
        self.update_display(ylabel,fmt="y    = %s\n")
        if self.stderr != None:
            self.update_display(elabel,fmt="err  = %s\n")
        for mol in self.data[self.bioassay]:
            xdata = self.data[self.bioassay][mol]['xdata']
            ydata = self.data[self.bioassay][mol]['ydata']
            stderr = self.data[self.bioassay][mol]['stderr']
            self.update_display(mol,fmt="\n\nMolecule: %s\n")
            self.update_display(len(xdata),fmt="Number of data records read from bioassay data file = %i \n\n")
            n = 0
            while n < len(xdata):
                if len(stderr) > 0:
                    self.update_display((n+1,xlabel,xdata[n],ylabel,ydata[n],elabel,stderr[n]), \
                    fmt="%3i:   %s=%12.3f   %s=%12.3f   %s=%12.3f\n",tag='data')
                else:
                    self.update_display((n+1,xlabel,xdata[n],ylabel,ydata[n]), \
                    fmt="%3i:   %s=%12.3f   %s=%12.3f\n",tag='data')
                n = n + 1


    def load_data_cleanup(self):

        """Abandon data input, clean up data input errors and re-initialize data"""
        
        try:
            self.edialog.update()
        except:
            pass
        self.xmlstream.close()
        self.initialize_data()
        return

        
    def whoops(self,errtext):

        """The error dialog for the Abe Console"""

        self.edialog = Toplevel(self.root)
        self.edialog.resizable(width=0,height=0)
        self.edialog.title("ABE Error")
        self.edialog.bell()
        self.errhead = Label(self.edialog,text="ABE Error!",font=('Arial',10,'bold'),padx=5,fg='red')
        self.errhead.pack(pady=5)
        self.err = Label(self.edialog,text=errtext,font=('Arial',10),padx=20,anchor=W)
        self.err.pack(pady=5)
        self.okb = Button(self.edialog,text="Whoops!",command=self.scratch_error)
        self.okb.pack(pady=5)


    def scratch_error(self):

        """Kill the error dialog window"""
        
        self.edialog.destroy()


    def adios(self):

        """The exit dialog for the Abe Console"""

        self.qdialog = Toplevel(self.root)
        self.qdialog.resizable(width=0,height=0)
        self.qdialog.title("Quit ABE?")
        mtext = "Do you really (really) want to quit ABE?"
        self.askq = Label(self.qdialog,text=mtext,font=('Arial',10),padx=5)
        self.askq.grid(row=0,column=0,columnspan=2,pady=5)
        self.yesq = Button(self.qdialog,text="Yes, I really (really) do",command=self.do_quit)
        self.yesq.grid(row=1,column=0,padx=5,pady=5,sticky=EW)
        self.noq = Button(self.qdialog,text="Whoops! No not really!",command=self.cancel_quit)
        self.noq.grid(row=1,column=1,padx=5,pady=5,sticky=EW)


    def do_quit(self):

        "Kill the Abe console window and its dependents"""

        self.qdialog.destroy()
        self.root.destroy()


    def cancel_quit(self):

        "Abort killing the Abe Console window and its dependents"""

        self.qdialog.destroy()


      
    def start_element(self,name,attrs):

        """The XML parser data handler for starting a new XML element"""
        
        if name == "bioassay":
            if not attrs.has_key('id'):
                self.whoops("Bioassay data block with no ID (<bioassay id= ...>)")
                self.load_data_cleanup()
                return
            else:
                self.bioassay = attrs['id']
                self.data[self.bioassay] = {}
            if not attrs.has_key('columns'):
                self.whoops("Bioassay data block with no column description (<bioassay columns= ...>)")
                self.load_data_cleanup()
                return
            else:
                self.columns = string.split(attrs['columns'])
            if not attrs.has_key('x'):
                self.whoops("Bioassay data block with no x designation (<bioassay x= ...>)")
                self.load_data_cleanup()
                return
            else:
                if not attrs['x'] in self.columns: 
                    self.whoops("Designated x column '" + attrs['x'] + "' not found")
                    self.load_data_cleanup()
                    return
                else:
                    self.x = self.columns.index(attrs['x'])
            if not attrs.has_key('y'):
                self.whoops("Bioassay data block with no y designation (<bioassay y= ...>)")
                self.load_data_cleanup()
                return
            else:
                if not attrs['y'] in self.columns: 
                    self.whoops("Designated y column '" + attrs['y'] + "' not found")
                    self.load_data_cleanup()
                    return
                else:
                    self.y = self.columns.index(attrs['y'])
            if attrs.has_key('err'):
                if not attrs['err'] in self.columns: 
                    self.whoops("Designated error column '" + attrs['err'] + "' not found")
                    self.load_data_cleanup()
                    return
                else:
                    self.stderr = self.columns.index(attrs['err'])
        elif name == "molecule":
            if not attrs.has_key('id'):
                self.whoops("Molecule data block with no ID (<molecule id= ...>)")
                self.load_data_cleanup()
                return
            else:
                self.molecule = attrs['id']
                self.data[self.molecule] = {}
                self.molecule_list.append(self.molecule)
                self.data[self.bioassay][self.molecule] = {'xdata':[],'ydata':[], \
                'logx':[],'yfit':[],'polydeg':0, 'poly':[], 'poly1':[], 'poly2':[], \
                'poly3':[], 'edguess':0.0, 'edfit':0.0, 'stderr':[], 'residual':0.0, \
                'four_param':{'fit':0,'a':None,'b':None,'c':None,'d':None,'yfit':[]}  }
                self.topmenu['Data'].menu.add_radiobutton(label=attrs['id'],variable=self.current)
                self.topmenu['Data']['menu'] = self.topmenu['Data'].menu
        elif name == "data":
            self.in_data = 1
                
                

    def end_element(self,name):

        """The XML parser data handler for terminating an XML element"""

        if name == "bioassay":
            pass
        elif name == "molecule":
            if len(self.data[self.bioassay][self.molecule]['xdata']) == 0:
                self.whoops("Molecule: "+self.molecule+" contains no valid data points")
                self.load_data_cleanup()
                return
            if self.data[self.bioassay][self.molecule]['xdata'][0] > \
               self.data[self.bioassay][self.molecule]['xdata'][-1]:
                self.data[self.bioassay][self.molecule]['xdata'].reverse()
                self.data[self.bioassay][self.molecule]['ydata'].reverse()
                self.data[self.bioassay][self.molecule]['stderr'].reverse()
            for x in self.data[self.bioassay][self.molecule]['xdata']:
                self.data[self.bioassay][self.molecule]['logx'].append(math.log10(x))
            self.molecule = ''
        elif name == "data":
            self.in_data = 0

    def char_data(self,cdata):

        """The XML parser data handler for character data"""

        if self.bioassay != None and self.molecule != None and self.in_data:
            c = string.split(cdata)
            try:
                self.data[self.bioassay][self.molecule]['xdata'].append(string.atof(c[self.x]))
                self.data[self.bioassay][self.molecule]['ydata'].append(string.atof(c[self.y]))
                if self.stderr != None:
                    self.data[self.bioassay][self.molecule]['stderr'].append(string.atof(c[self.stderr]))
                return
            except:
                etext = "Molecule: "+self.molecule + " - Non numerical data encountered in data columns\n" + string.join(c)
                self.whoops(etext)
                self.load_data_cleanup()
                return


    def work_data(self):

        """Set the current molecule to the molecule dataset selected in the Data-> menu"""
        
        self.molecule = self.current.get()
        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        self.update_status("Bioassay=" + self.bioassay + ", Molecule=" + self.molecule)
        self.update_display((self.bioassay,self.molecule), \
                fmt="\n\nProcessing Data: Bioassay = %s, Molecule = %s\n")
        self.draw_graph()

    
    def get_current(self,field):

        """Return the data for the specified field, from the current molecule"""
        
        return self.data[self.bioassay][self.molecule][field]


    def put_current(self,field,value):

        """Set the data for the specified field, in the current molecule"""
        
        self.data[self.bioassay][self.molecule][field] = value

    
    def update_status(self,stext):

        """Update the status bar at the bottom of the ABE console"""
        
        self.status.configure(text=stext)


    def draw_graph(self):

        """Redraw the graph window on the Bioassy Console"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected")
            return
        self.graph.delete(ALL)
        xdata = self.get_current('xdata')
        ydata = self.get_current('ydata')
        if min(ydata) < 0.0:
            ny = 0
            while ny < len(ydata):
                if ydata[ny] < 0.0:
                    ydata[ny] = 0.0
                ny = ny + 1
            self.put_current('ydata',ydata)
            self.whoops("Negative Y-values in this data have been reset to zero")
        yfit = self.get_current('yfit')
        logx = self.get_current('logx')
        stderr = self.get_current('stderr')
        edguess = self.get_current('edguess')
        edfit = self.get_current('edfit')
        four_param = self.get_current('four_param')
        yfourp = four_param['yfit']
        ygmin = 0.0
        ygmax = max(ydata)
        dymin = min(ydata)
        self.update_status("["+self.bioassay+"]   ["+self.molecule+ \
                           "]   Ymin=%.1f, Ymax=%.1f" % (dymin,ygmax))
        if len(yfit) > 0:
            if max(yfit) > ygmax:
                ygmax = max(yfit)
        if len(yfourp) > 0:
            if max(yfourp) > ygmax:
                ygmax = max(yfourp)
        yscale = (self.gsize-self.graph_border*2)/ygmax
        xgmin = min(logx)
        xgmax = max(logx)
        if (xgmax-xgmin) <= 0.0:
            self.whoops("Invalid X-range for molecule: "+self.molecule)
            return
        xscale = abs((self.gsize-self.graph_border*2)/(xgmax-xgmin))
        datpoints = []
        fitpoints = []
        fppoints = []
        errpoints = []
        n = 0
        while n < len(logx):
            xd = self.graph_border + int((logx[n]-xgmin)*xscale)
            yd = int(self.gsize - (ydata[n]-ygmin)*yscale) - self.graph_border
            datpoints.append((xd,yd))
            if len(yfit) > 0:
                yf = int(self.gsize - (yfit[n]-ygmin)*yscale) - self.graph_border
                fitpoints.append((xd,yf))
            if len(yfourp) > 0:
                yf = int(self.gsize - (yfourp[n]-ygmin)*yscale) - self.graph_border
                fppoints.append((xd,yf))
            if len(stderr) > 0:
                yhi = int(self.gsize - (ydata[n]-ygmin-(stderr[n]/2.0))*yscale) - self.graph_border
                ylo = int(self.gsize - (ydata[n]-ygmin+(stderr[n]/2.0))*yscale) - self.graph_border
                errpoints.append((yhi,ylo))
            n = n + 1
        nerr = 0
        for x,y in datpoints:
            self.graph.create_oval(x-3,y-3,x+3,y+3,width=1,outline='blue')
            self.graph.create_line(datpoints,fill='blue',smooth=1)
            if len(stderr) > 0 and self.graph_ebar_on.get():
                self.graph.create_line(x,errpoints[nerr][0],x,errpoints[nerr][1],fill='blue')
                self.graph.create_line(x-3,errpoints[nerr][0],x+3,errpoints[nerr][0],fill='blue')
                self.graph.create_line(x-3,errpoints[nerr][1],x+3,errpoints[nerr][1],fill='blue')
                nerr = nerr + 1
        if edguess != 0.0:
            n = default_border_offset
            xd = self.graph_border + int((edguess-xgmin)*xscale)
            self.graph.create_line(xd,n,xd,self.gsize-n,fill='blue')
        if len(yfit) > 0 and self.graph_poly_on.get():
            for x,y in fitpoints:
                self.graph.create_oval(x-3,y-3,x+3,y+3,width=1,outline='red')
                self.graph.create_line(fitpoints,fill='red',smooth=1)
            if edfit != 0.0:
                n = default_border_offset
                xd = self.graph_border + int((edfit-xgmin)*xscale)
                self.graph.create_line(xd,n,xd,self.gsize-n,fill='red')
        if len(yfourp) > 0 and self.graph_fourp_on.get():
            for x,y in fppoints:
                self.graph.create_oval(x-3,y-3,x+3,y+3,width=1,outline='dark green')
                self.graph.create_line(fppoints,fill='dark green',smooth=1)
            n = default_border_offset
            edfourp = math.log10(four_param['c'])
            xd = self.graph_border + int((edfourp-xgmin)*xscale)
            self.graph.create_line(xd,n,xd,self.gsize-n,fill='dark green')
        if self.graph_key_on.get():
            self.update_graph_key()
        if self.graph_leg_on.get():
            self.update_graph_legend()
        if self.graph_border_on.get():
            n = default_border_offset
            self.graph.create_line(n,n,n,self.gsize-n,fill='black')
            self.graph.create_line(n,self.gsize-n,self.gsize-n,self.gsize-n,fill='black')
            self.graph.create_line(self.gsize-n,self.gsize-n,self.gsize-n,n,fill='black')
            self.graph.create_line(self.gsize-n,n,n,n,fill='black')


    def update_graph_key(self):

        """Redraw the graph key on the Bioassy Console"""

        xdata = self.get_current('xdata')
        poly = self.get_current('poly')
        polydeg = self.get_current('polydeg')
        edguess = self.get_current('edguess')
        edfit = self.get_current('edfit')
        residual = self.get_current('residual')
        four_param = self.get_current('four_param')
        n = default_border_offset
        yinc = 14
        ny = n+yinc
        self.graph.create_text(n+5,ny,text='A B E   1 . 0',font=('Arial',10,'bold'), \
                               fill='black',anchor=W)
        ny = ny + yinc + 5
        self.graph.create_text(n+5,ny,text=self.bioassay,font=('Courier',10,'bold'), \
                               fill='blue',anchor=W)
        ny = ny + yinc
        self.graph.create_text(n+5,ny,text=self.molecule,font=('Courier',10,'bold'), \
                               fill='blue',anchor=W)
        ny = ny + yinc
        self.graph.create_text(n+5,ny,text="Data records = "+str(len(xdata)), \
                               font=('Courier',10,'bold'),fill='blue',anchor=W)
        if edguess != 0.0:
            edg = 10.0**edguess
            ny = ny + yinc
            self.graph.create_text(n+5,ny,text="ED50(Estd) = %.3f" % edg, \
                                   font=('Courier',10,'bold'),fill='blue',anchor=W)
        if four_param['fit'] and self.graph_fourp_on.get():
            ny = ny + yinc
            self.graph.create_text(n+5,ny,text="ED50(4Par) = %.3f" % four_param['c'], \
                                   font=('Courier',10,'bold'),fill='dark green',anchor=W)
        if edfit != 0.0 and self.graph_poly_on.get():
            edf = 10.0**edfit
            ny = ny + yinc
            self.graph.create_text(n+5,ny,text="ED50(Poly) = %.3f" % edf, \
                                   font=('Courier',10,'bold'),fill='red',anchor=W)


    def update_graph_legend(self):

        """Redraw the graph legend on the Bioassy Console"""

        xdata = self.get_current('xdata')
        poly = self.get_current('poly')
        polydeg = self.get_current('polydeg')
        edguess = self.get_current('edguess')
        edfit = self.get_current('edfit')
        residual = self.get_current('residual')
        four_param = self.get_current('four_param')
        n = default_border_offset
        yinc = 14
        nx = self.gsize - n - 190
        dopoly = 0
        do4p = 0
        if edfit != 0.0 and self.graph_poly_on.get():
            dopoly = 1
        if four_param['fit'] and self.graph_fourp_on.get():
            do4p = 1
        if dopoly and do4p:
            ny1 = self.gsize - n - (polydeg+8)*yinc
        elif do4p:
            ny1 = self.gsize - n - 6*yinc
        elif dopoly:
            ny1 = self.gsize - n - (polydeg+3)*yinc
        else:
            return
        if do4p:
            ny1 = ny1 + yinc
            self.graph.create_text(nx,ny1,text="4-Parameter Fit:", \
                                   font=('Courier',10,'bold'),fill='dark green',anchor=W)
            ny1 = ny1 + yinc
            self.graph.create_text(nx,ny1,text="a (ymin)  =%12.3f" % four_param['a'], \
                                   font=('Courier',10,'bold'),fill='dark green',anchor=W)
            ny1 = ny1 + yinc
            self.graph.create_text(nx,ny1,text="b (slope) =%12.3f" % four_param['b'], \
                                   font=('Courier',10,'bold'),fill='dark green',anchor=W)
            ny1 = ny1 + yinc
            self.graph.create_text(nx,ny1,text="c (ED50)  =%12.3f" % four_param['c'], \
                                   font=('Courier',10,'bold'),fill='dark green',anchor=W)
            ny1 = ny1 + yinc
            self.graph.create_text(nx,ny1,text="d (ymax)  =%12.3f" % four_param['d'], \
                                   font=('Courier',10,'bold'),fill='dark green',anchor=W)
        if dopoly:
            ny1 = ny1 + yinc
            self.graph.create_text(nx,ny1,text="Polynomial (n=%d):" % polydeg, \
                                   font=('Courier',10,'bold'),fill='red',anchor=W)
            nc = 0
            ny1 = ny1 + yinc
            for coef in poly:
                self.graph.create_text(nx,ny1,text="a(%2i) = %15.3f" % (nc,coef), \
                                   font=('Courier',10,'bold'),fill='red',anchor=W)
                ny1 = ny1 + yinc
                nc = nc + 1


    def choose_polynomial(self):

        """Dialog to select the degree of the polynomial to use for data modeling"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        xdata = self.get_current('xdata')
        self.pdeg = StringVar()
        self.polyfit = Toplevel(self.root)
        self.polyfit.resizable(width=0,height=0)
        self.polyfit.title("ABE: Fit Polynomial")
        mtext = "Enter degree of polynomial to be fitted (3 - " + str(len(xdata)-1) + ")"
        self.cdeg = Label(self.polyfit,text=mtext,font=('Arial',10),padx=5)
        self.cdeg.grid(row=0,column=0,columnspan=2,pady=5)
        self.getd = Entry(self.polyfit,textvariable=self.pdeg,width=20)
        self.getd.grid(row=1,column=0,columnspan=2)
        self.setd = Button(self.polyfit,text="Accept",command=self.gotpolydeg)
        self.setd.grid(row=2,column=0,padx=5,pady=5,sticky=EW)
        self.fpfun = Button(self.polyfit,text="Cancel",command=self.cancel_degree)
        self.fpfun.grid(row=2,column=1,padx=5,pady=5,sticky=EW)


    def gotpolydeg(self):

        """Only allow sensible choices of polynomial that accord with the data"""

        xdata = self.get_current('xdata')
        nstr = self.pdeg.get()
        if len(nstr) == 0: return
        try:
            ndeg = string.atoi(nstr)
            if ndeg >= 3 and ndeg < len(xdata):
                self.put_current('polydeg',ndeg)
                self.polyfit.destroy()
                self.update_display(ndeg,fmt="\nPolynomial of degree = %i selected\n")
            else:
                self.getd.delete(0,"end")
                self.polyfit.bell()
                self.whoops("Your data do not support fitting a polynomial of degree=" + str(ndeg))
            return
        except:
            self.getd.delete(0,"end")
            self.polyfit.bell()
            self.whoops("Invalid specification of degree of polynomial")
            return


    def cancel_degree(self):

        """Cancel choice of degree of fitted polynomial"""

        self.polyfit.destroy()


    def pick_root(self):

        """Switch on feature to allow estimation of ED50 from data graph"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        self.put_current('edguess',0.0)
        self.draw_graph()
        self.status.configure(font=('Arial',8,'bold'),fg='red')
        self.update_status("Click on the graph to estimate the ED50 value .....")
        self.graph.bind('<Button-1>',self.get_pick)


    def get_pick(self,event):

        """Catch and process the mouse click on the data graph used to estimate ED50"""

        self.status.configure(font=('Arial',8),fg='blue')
        ydata = self.get_current('ydata')
        logx = self.get_current('logx')
        four_param = self.get_current('four_param')
        xs = self.graph.canvasx(event.x)
        xgmin = min(logx)
        xgmax = max(logx)
        xscale = abs((self.gsize-20.0)/(xgmax-xgmin))
        edguess = xgmin + ((xs-10)/xscale)
        self.put_current('edguess',edguess)
        edg = 10**edguess
        if four_param['c'] == None:
            four_param['c'] = edg
        self.put_current('four_param',four_param)
        self.graph.unbind('<Button-1>')
        self.draw_graph()
        self.update_display(edg,fmt="\nInitial estimate for ED50 = %12.3f\n")
        dymax = max(ydata)
        dymin = min(ydata)
        self.update_status("["+self.bioassay+"]   ["+self.molecule+ \
                           "]   Ymin=%.1f, Ymax=%.1f" % (dymin,dymax))



    def fit_polynomial(self):

        """ Fit the chosen polynomial to the data, compute polynomial derivatives and use
            them in Newton-Raphson iterations from the initial ED50 estimate, to solve
            the polynomial for the ED50 value at the local point of inflexion (d2y/dx2=0)"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        xdata = self.get_current('xdata')
        ydata = self.get_current('ydata')
        logx = self.get_current('logx')
        polydeg = self.get_current('polydeg')
        edguess = self.get_current('edguess')
        if polydeg == 0:
            self.whoops("No polynomial chosen for fitting")
            return
        if edguess == 0.0:
            self.whoops("No initial estimate for ED50 supplied")
            return
        x = Matfunc.Vec(logx)
        y = Matfunc.Vec(ydata)
        xy = Matfunc.Table([x, y])
        poly = Matfunc.polyfit(xy,degree=polydeg)
        poly.reverse()
        self.put_current('poly',poly)
        self.update_display("\nFitted polynomial coefficients:")
        n = 0
        while n <= polydeg:
            self.update_display((n,poly[n]),fmt="a(%2i) = %18.6f\n",tag='data')
            n = n + 1
        self.get_derivatives()
        self.find_root(default_precision)
        yfit = []
        n = 0
        while n < len(logx):
                yfit.append(self.eval_polynomial(poly,logx[n]))
                n = n + 1
        self.put_current('yfit',yfit)
        self.draw_graph()


    def eval_polynomial(self,coefs,x):

        """Evaluate y for the given polynomial at x"""

        n = 0
        y = 0.0
        while n < len(coefs):
            y = y + coefs[n]*x**n
            n = n + 1
        return y


    def get_derivatives(self):

        """Compute 1st, 2nd and 3rd derivatives of the fitted polynomial"""

        poly = self.get_current('poly')
        poly1 = []
        poly2 = []
        poly3 = []
        n = 1
        while n < len(poly):
            poly1.append(n*poly[n])
            n = n + 1
        n = 1
        while n < len(poly1):
            poly2.append(n*poly1[n])
            n = n + 1
        n = 1
        while n < len(poly2):
            poly3.append(n*poly2[n])
            n = n + 1
        self.put_current('poly1',poly1)
        self.put_current('poly2',poly2)
        self.put_current('poly3',poly3)


    def find_root(self,precision):

        """Solve local 2nd derivative root using Newton-Raphson method"""

        xdata = self.get_current('xdata')
        poly = self.get_current('poly')
        poly1 = self.get_current('poly1')
        poly2 = self.get_current('poly2')
        poly3 = self.get_current('poly3')
        edguess = self.get_current('edguess')
        self.update_display("\nNewton-Raphson iterations to solve local root of polynomial:")
        edfit = 0.0
        xmax = max(xdata)
        xmin = min(xdata)
        x = edguess
        f = self.eval_polynomial(poly2,x)
        fd = self.eval_polynomial(poly3,x)
        n = 0
        while 1:
            dx = f / fd
            if abs(dx) < precision * (1 + abs(x)):
                edfit = x - dx
                self.put_current('edfit',edfit)
                edf = 10**edfit
                self.update_display(edf,fmt="\nNewton-Raphson solution for fitted ED50 = %12.3f\n")
                return
            x = x - dx
            f = self.eval_polynomial(poly2,x)
            fd = self.eval_polynomial(poly3,x)
            n = n + 1
            lx = 10.0**x
            self.update_display((n, f, lx),fmt="Newton-Raphson iteration(%3i):   f(x)=%15.6f,   x=%15.6f\n", \
                                tag='data')


    def set_graph_border(self):

        """Dialog to select the size (in pixels) of the graph border"""

        self.pdeg = StringVar()
        self.gborder = Toplevel(self.root)
        self.gborder.resizable(width=0,height=0)
        self.gborder.title("ABE: Set Graph Border")
        mtext = "Enter size (in pixels) of graph border [default=" + str(default_graph_border) + "]"
        self.cdeg = Label(self.gborder,text=mtext,font=('Arial',10),padx=5)
        self.cdeg.grid(row=0,column=0,columnspan=2,pady=5)
        self.getd = Entry(self.gborder,textvariable=self.pdeg,width=20)
        self.getd.grid(row=1,column=0,columnspan=2)
        self.setd = Button(self.gborder,text="Accept",command=self.got_border)
        self.setd.grid(row=2,column=0,padx=5,pady=5,sticky=EW)
        self.fpfun = Button(self.gborder,text="Cancel",command=self.cancel_border)
        self.fpfun.grid(row=2,column=1,padx=5,pady=5,sticky=EW)



    def got_border(self):

        """Only allow sensible choices of the graph border"""

        nstr = self.pdeg.get()
        if len(nstr) == 0: return
        try:
            ndeg = string.atoi(nstr)
            if ndeg >= 0 and ndeg < int(self.gsize/2.5):
                self.graph_border = ndeg
                self.gborder.destroy()
            else:
                self.getd.delete(0,"end")
                self.gborder.bell()
                self.whoops("Sensible values for the graph border: 0 =< x =< " + str(int(self.gsize/3.0)))
            return
        except:
            self.getd.delete(0,"end")
            self.gborder.bell()
            self.whoops("Invalid specification of graph border")
            return


    def cancel_border(self):

        """Cancel choice of graph border width"""

        self.gborder.destroy()


    def toggle_al(self):

        """Toggle the visibility status of the activity log window"""

        a = self.dwin.state()
        if a == 'withdrawn' or a == 'iconic':
            self.dwin.deiconify()
        else:
            self.dwin.withdraw()


    def save_log(self):

        """Save the contents of the activity log window to file"""

        logfile = tkFileDialog.asksaveasfile(title="ABE: Save Activity Log",initialdir=self.workdir, \
                    filetypes=[('Text Files', '*.txt'),('All Files','*.*')], defaultextension='.txt')
        if logfile != None and logfile != '':
            logfile.write(self.display.get(1.0,END))
            logfile.close()


    def save_graph(self):

        """Save the currently displayed graph to file in PostScript format"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        grafile = tkFileDialog.asksaveasfilename(title="ABE: Save Graph Image",initialdir=self.workdir, \
                    filetypes=[('PostScript Files', '*.ps'),('All Files','*.*')],defaultextension='.ps')
        if grafile != None and grafile != '':
            self.graph.postscript(file=grafile,colormode='color')


    def export_results(self):

        """Export data models as a tab-delimited table for input to Excel"""
        
        exfile = tkFileDialog.asksaveasfile(title="ABE: Export Results Table",initialdir=self.workdir, \
                    filetypes=[('Text Files', '*.txt'),('All Files','*.*')],defaultextension='.txt')
        if exfile != None and exfile != '':
            exfile.write("ABE: Data modeling results\n")
            for mol in self.molecule_list:
                edfit = self.data[self.bioassay][mol]['edfit']
                edf = 10.0**edfit
                poly = self.data[self.bioassay][mol]['poly']
                four_param = self.data[self.bioassay][mol]['four_param']
                ffourp = four_param['fit']
                afourp = four_param['a']
                bfourp = four_param['b']
                cfourp = four_param['c']
                dfourp = four_param['d']
                if ffourp == 2:
                    exfile.write("%s \t %s \t'Four parameter fitted ED50'\t %.6f" % (self.bioassay,mol,cfourp))
                    exfile.write("\t'a(ymin)'\t%.6f\t'b(slope)'\t%.6f\t'c(ED50)'\t%.6f\t'd(ymax)'\t%.6f\n" \
                                  % (afourp,bfourp,cfourp,dfourp))
                elif ffourp == 1:
                    exfile.write("%s \t %s \t'Four parameter search ED50'\t %.6f" % (self.bioassay,mol,cfourp))
                    exfile.write("\t'a(ymin)'\t%.6f\t'b(slope)'\t%.6f\t'c(ED50)'\t%.6f\t'd(ymax)'\t%.6f\n" \
                                  % (afourp,bfourp,cfourp,dfourp))
                if edfit != 0.0:
                    exfile.write("%s \t %s \t'Polynomial fitted ED50'\t %.6f" % (self.bioassay,mol,edf))
                    n = 0
                    while n < len(poly):
                        exfile.write("\t a[%i] \t %.6f" % (n,poly[n]))
                        n = n + 1
                    exfile.write("\n")
            exfile.close()


    
    def show_fit(self):

        """Display a table of observed and fitted data in the activity log window"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        yfit = self.get_current('yfit')
        four_param=self.get_current('four_param')
        yfp = four_param['yfit']
        if len(yfit) == 0 and len(yfp) == 0:
            self.whoops("No fitting has yet been applied to this data")
            return
        xdata = self.get_current('xdata')
        ydata = self.get_current('ydata')
        logx = self.get_current('logx')
        self.update_display("\nShow Fitted Data:")       
        xlabel = self.columns[self.x]
        ylabel = self.columns[self.y]
        plabel = 'Poly'
        flabel = '4Par'
        n = 0
        for x in xdata:
            if len(yfp) > 0 and len(yfit) > 0:
                self.update_display((n+1,xlabel,xdata[n],ylabel,ydata[n],plabel,yfit[n],flabel,yfp[n]), \
                fmt="%3i:   %s=%12.3f   %s=%12.3f   %s=%12.3f  %s=%12.3f\n",tag='data')
            elif len(yfp) == 0 and len(yfit) > 0:
                self.update_display((n+1,xlabel,xdata[n],ylabel,ydata[n],plabel,yfit[n]), \
                fmt="%3i:   %s=%12.3f   %s=%12.3f   %s=%12.3f\n",tag='data')
            elif len(yfp) > 0 and len(yfit) == 0:
                self.update_display((n+1,xlabel,xdata[n],ylabel,ydata[n],flabel,yfp[n]), \
                fmt="%3i:   %s=%12.3f   %s=%12.3f   %s=%12.3f\n",tag='data')
            n = n + 1


    def pick_ymaxmin(self):

        """Dialog to select the ymax and ymin to use for 4-parameter fit"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected for processing")
            return
        four_param = self.get_current('four_param')
        edguess = self.get_current('edguess')
        a = four_param['a']
        b = four_param['b']
        c = four_param['c']
        d = four_param['d']
        self.fourpa = StringVar()
        self.fourpb = StringVar()
        self.fourpc = StringVar()
        self.fourpd = StringVar()
        self.fourpa.set(str(a))
        self.fourpb.set(str(b))
        self.fourpc.set(str(c))
        self.fourpd.set(str(d))
        self.fourfit = Toplevel(self.root)
        self.fourfit.resizable(width=0,height=0)
        self.fourfit.title("ABE: Estimate Curve Max/Min")
        mtext = "This is really NOT recommended as it allows you to 'fudge'\nthe four-parameter fit, but if you really feel you must, please\nenter estimates for the limits of y as x -> 0 and x -> infinity"
        self.fpt = Label(self.fourfit,text=mtext,font=('Arial',10),padx=5,anchor=W)
        self.fpt.grid(row=0,column=0,columnspan=2,pady=5)
        self.fpda = Label(self.fourfit,text='a (ymin)',font=('Arial',10),padx=5,anchor=E)
        self.fpda.grid(row=1,column=0,padx=10,pady=5)
        self.fpdb = Label(self.fourfit,text='b (slope)',font=('Arial',10),padx=5,anchor=E)
        self.fpdb.grid(row=2,column=0,padx=10,pady=5)
        self.fpdc = Label(self.fourfit,text='c (ED50)',font=('Arial',10),padx=5,anchor=E)
        self.fpdc.grid(row=3,column=0,padx=10,pady=5)
        self.fpdd = Label(self.fourfit,text='d (ymax)',font=('Arial',10),padx=5,anchor=E)
        self.fpdd.grid(row=4,column=0,padx=10,pady=5)
        self.esta = Entry(self.fourfit,textvariable=self.fourpa,width=15)
        self.esta.grid(row=1,column=1)
        self.estb = Entry(self.fourfit,textvariable=self.fourpb,width=15,state='disabled',fg='gray')
        self.estb.grid(row=2,column=1)
        self.estc = Entry(self.fourfit,textvariable=self.fourpc,width=15,state='disabled',fg='gray')
        self.estc.grid(row=3,column=1)
        self.estd = Entry(self.fourfit,textvariable=self.fourpd,width=15)
        self.estd.grid(row=4,column=1)
        self.setfp = Button(self.fourfit,text="Accept",command=self.gotfourp)
        self.setfp.grid(row=5,column=0,padx=5,pady=5,sticky=EW)
        self.canfp = Button(self.fourfit,text="Cancel",command=self.cancel_fourp)
        self.canfp.grid(row=5,column=1,padx=5,pady=5,sticky=EW)


    def gotfourp(self):

        """Set the 4-parameter model y asymptotes to the input values"""

        four_param = self.get_current('four_param')
        astr = self.fourpa.get()
        dstr = self.fourpd.get()
        try:
            a = string.atof(astr)
            four_param['a'] = a
            d = string.atof(dstr)
            four_param['d'] = d
            self.put_current('four_param',four_param)
            self.update_display("\nSetting initial y-limit estimates manually:")
            self.update_display(a,fmt="a (ymin)  = %18.3f\n",tag='data')
            self.update_display(d,fmt="d (slope) = %18.3f\n",tag='data')
            self.fourfit.destroy()
        except:
            self.esta.delete(0,"end")
            self.estb.delete(0,"end")
            self.fourfit.bell()
            self.whoops("Invalid specification of a and b parameters")
            return


    def cancel_fourp(self):

        """Cancel dialog to select the ymax and ymin to use for 4-parameter fit"""

        self.fourfit.destroy()


    def set_fourp_kill(self):

        """Set the kill flag for the 4-parameter fitting algorithm"""

        if self.fourp_kill == 1:
            self.fpdialog.destroy()
            return
        else:
            self.fourp_kill = 1
            self.fphead.configure(text="Cancelling 4 parameter fit\nplease wait ...",fg='red')
            self.fpdialog.update()
        

    def fit_fourp(self):

        """Launch the 4-parameter fitting algorithm"""

        if self.molecule == '':
            self.whoops("No molecule data currently selected")
            return
        self.fourp_kill = 0
        four_param = self.get_current('four_param')
        xdata = self.get_current('xdata')
        ydata = self.get_current('ydata')
        logx = self.get_current('logx')
        if four_param['c'] == None:
            self.whoops("No initial estimate for ED50 supplied")
            return
        ysrchfrac = self.fourp_options['ysrch']
        xsrchfrac = self.fourp_options['xsrch']
        ysi = self.fourp_options['yiter']
        esi = self.fourp_options['eiter']
        ssi = self.fourp_options['siter']
        isi = self.fourp_options['isiter']
        slpmax = self.fourp_options['slopemax']
        self.pccomplete = 0
        self.fpdialog = Toplevel(self.root)
        self.fpdialog.resizable(width=0,height=0)
        self.fpdialog.title("ABE: 4-Parameter fitting ...")
        self.fphead = Label(self.fpdialog, \
                text="Fitting four-parameter model, please wait ...\nFitting %d percent complete" % self.pccomplete,\
                font=('Arial',10,'bold'),padx=5,fg='dark green')
        self.fphead.pack(pady=5)
        self.fpkill = Button(self.fpdialog,text="Cancel 4-parameter fitting",command=self.set_fourp_kill)
        self.fpkill.pack(pady=5)
        self.fpdialog.update()
        xmax = max(xdata)
        xmin = min(xdata)
        xr = xmax - xmin
        if four_param['a'] == None:
            ymin = min(ydata)
        else:
            ymin = four_param['a']
        if four_param['d'] == None:
            ymax = max(ydata)
        else:
            ymax = four_param['d']
        yr = ymax - ymin
        yscale = xmax/ymax
        ysr = (ysrchfrac/2.0)*yr
        xsr = (xsrchfrac/2.0)*xr
        ymin1 = ymin - ysr
        ymin2 = ymin + ysr
        ymax1 = ymax - ysr
        ymax2 = ymax + ysr
        edg = four_param['c']
        emin1 = edg - xsr
        emin2 = edg + xsr
        incymin = (ymin2-ymin1)/ysi
        incymax = (ymax2-ymax1)/ysi
        ince = (emin2-emin1)/esi
        if emin1 < 0.0:
            emin1 = 0.001
        yminsp = []
        ymaxsp = []
        esp = []
        ssp = []
        for n in range(0,ysi):
            yminsp.append(ymin1 + n*incymin)
            ymaxsp.append(ymax1 + n*incymax)
        for n in range(0,esi):
            esp.append(emin1 + n*ince)
        nsmin = 0
        isinc = 1.0/isi
        for ns in range(0,isi):
            yd = 0.0
            n = 0
            while n < len(xdata):
                slope = ns * isinc * slpmax
                yc = self.eval_four_param_model(xdata[n],ymin,ymax,slope,edg)
                yd = yd + (ydata[n]-yc)*(ydata[n]-yc)
                n = n + 1
            if ns == 0:
                ydmin = yd
            else:
                if yd < ydmin:
                    ydmin = yd
                    nsmin = ns
        if self.fourp_kill:
            self.fpdialog.destroy()
            return
        sguess = nsmin * isinc * slpmax
        smin = sguess - (ysrchfrac/2.0)*sguess
        smax = sguess + (ysrchfrac/2.0)*sguess
        incs = (smax-smin)/ssi
        ssp = []
        for n in range(0,ssi):
            ssp.append(smin + n*incs)
        ydmin = 9.9E+20
        pcinc = int(100.0/ysi)
        for cymax in ymaxsp:
            self.pccomplete = self.pccomplete + pcinc
            self.fphead.configure(text="Fitting four-parameter model, please wait ...\nFitting %d percent complete" \
                                    % self.pccomplete)
            self.fpdialog.update()
            if self.fourp_kill:
                self.fpdialog.destroy()
                return
            for cymin in yminsp:
                for cedg in esp:
                    for cslp in ssp:
                        yd = 0.0
                        n = 0
                        while n < len(xdata):
                            yc = self.eval_four_param_model(xdata[n],cymin,cymax,cslp,cedg)
                            yd = yd + (ydata[n]-yc)*(ydata[n]-yc)
                            n = n + 1
                        if yd < ydmin:
                            ydmin = yd
                            optymax = cymax
                            optymin = cymin
                            opted50 = cedg
                            optslope = cslp
        fa = (xdata,ydata)
        x0 = [0, 0, 0, 0]
        x0[0] = optymin
        x0[1] = optslope
        x0[2] = opted50
        x0[3] = optymax
        fcn = four_param_model1
        try:
            fp = scipy.optimize.minpack.leastsq(fcn,x0,args=fa)
            four_param['a'] = fp[0][0]
            four_param['b'] = fp[0][1]
            four_param['c'] = fp[0][2]
            four_param['d'] = fp[0][3]
            four_param['fit'] = 2
        except:
            four_param['a'] = optymin
            four_param['b'] = optslope
            four_param['c'] = opted50
            four_param['d'] = optymax
            four_param['fit'] = 1
        n = 0
        a = four_param['a']
        b = four_param['b']
        c = four_param['c']
        d = four_param['d']
        four_param['yfit'] = []
        while n < len(xdata):
            yf = self.eval_four_param_model(xdata[n],a,d,b,c)
            four_param['yfit'].append(yf)
            n = n + 1
        self.put_current('four_param',four_param)
        self.update_display("\nFitted four-parameter model:")
        if four_param['fit'] == 1:
            self.update_display("Nonlinear least-squares regression was unstable")
            self.update_display("Using parameters derived from 4-D initialization search")
        else:
            self.update_display("Nonlinear least-squares regression was stable")
            self.update_display("Using parameters derived from nonlinear least-squares regression")
        self.update_display(a,fmt="a (ymin)  = %18.3f\n",tag='data')
        self.update_display(b,fmt="b (slope) = %18.3f\n",tag='data')
        self.update_display(c,fmt="c (ED50)  = %18.3f\n",tag='data')
        self.update_display(d,fmt="d (ymax)  = %18.3f\n",tag='data')
        self.update_display(c,fmt="\nFour-parameter data model solution for fitted ED50 = %12.3f\n")
        dtext = "Four-parameter data fitting completed\n\na = %15.3f\nb = %15.3f\nc = %15.3f\nd = %15.3f" % (a,b,c,d)
        self.fphead.configure(text=dtext,font=('Courier',10,'bold'))
        self.fpkill.configure(text="OK")
        self.fourp_kill = 1
        self.fpdialog.update()
        self.draw_graph()


    def eval_four_param_model(self,x,ymin,ymax,slope,ed50):

        """Return 4-parameter fitted y for supplied x"""
        
        return ymax + ( (ymin-ymax)/(1 + (x/ed50)**slope) )


    def set_fourp_opts(self):

        """Dialog to set 4-parameter initial search settings"""
        
        self.cur_ysrch = StringVar()
        self.cur_xsrch = StringVar()
        self.cur_yiter = StringVar()
        self.cur_eiter = StringVar()
        self.cur_siter = StringVar()
        self.cur_slopemax = StringVar()
        self.cur_isiter = StringVar()
        self.cur_ysrch.set(str(self.fourp_options['ysrch']))
        self.cur_xsrch.set(str(self.fourp_options['xsrch']))
        self.cur_yiter.set(str(self.fourp_options['yiter']))
        self.cur_eiter.set(str(self.fourp_options['eiter']))
        self.cur_siter.set(str(self.fourp_options['siter']))
        self.cur_slopemax.set(str(self.fourp_options['slopemax']))
        self.cur_isiter.set(str(self.fourp_options['isiter']))
        self.fouro = Toplevel(self.root)
        self.fouro.resizable(width=0,height=0)
        self.fouro.title("ABE: 4-Parameter Fit Options")
        mtext = "Change with extreme caution!\nThe defaults should normally work fine"
        self.fpto = Label(self.fouro,text=mtext,font=('Arial',10),padx=5,anchor=W)
        self.fpto.grid(row=0,column=0,columnspan=3,pady=5)
        self.fpdo1 = Label(self.fouro,text='Fractional Y-search',font=('Arial',10),padx=5,anchor=E)
        self.fpdo1.grid(row=1,column=0,columnspan=2,padx=10,pady=5)
        self.fpdo2 = Label(self.fouro,text='Fractional X-search',font=('Arial',10),padx=5,anchor=E)
        self.fpdo2.grid(row=2,column=0,columnspan=2,padx=10,pady=5)
        self.fpdo3 = Label(self.fouro,text='Y-search iterations',font=('Arial',10),padx=5,anchor=E)
        self.fpdo3.grid(row=3,column=0,columnspan=2,padx=10,pady=5)
        self.fpdo4 = Label(self.fouro,text='ED50 search iterations',font=('Arial',10),padx=5,anchor=E)
        self.fpdo4.grid(row=4,column=0,columnspan=2,padx=10,pady=5)
        self.fpdo5 = Label(self.fouro,text='Slope search iterations',font=('Arial',10),padx=5,anchor=E)
        self.fpdo5.grid(row=5,column=0,columnspan=2,padx=10,pady=5)
        self.fpdo6 = Label(self.fouro,text='Maximum slope',font=('Arial',10),padx=5,anchor=E)
        self.fpdo6.grid(row=6,column=0,columnspan=2,padx=10,pady=5)
        self.fpdo7 = Label(self.fouro,text='Initial slope search iterations',font=('Arial',10),padx=5,anchor=E)
        self.fpdo7.grid(row=7,column=0,columnspan=2,padx=10,pady=5)
        self.esto1 = Entry(self.fouro,textvariable=self.cur_ysrch,width=15)
        self.esto1.grid(row=1,column=2)
        self.esto2 = Entry(self.fouro,textvariable=self.cur_xsrch,width=15)
        self.esto2.grid(row=2,column=2)
        self.esto3 = Entry(self.fouro,textvariable=self.cur_yiter,width=15)
        self.esto3.grid(row=3,column=2)
        self.esto4 = Entry(self.fouro,textvariable=self.cur_eiter,width=15)
        self.esto4.grid(row=4,column=2)
        self.esto5 = Entry(self.fouro,textvariable=self.cur_siter,width=15)
        self.esto5.grid(row=5,column=2)
        self.esto6 = Entry(self.fouro,textvariable=self.cur_slopemax,width=15)
        self.esto6.grid(row=6,column=2)
        self.esto7 = Entry(self.fouro,textvariable=self.cur_isiter,width=15)
        self.esto7.grid(row=7,column=2)
        self.setfpo = Button(self.fouro,text="Accept",command=self.gotfouro)
        self.setfpo.grid(row=8,column=0,padx=5,pady=5,sticky=EW)
        self.defpo = Button(self.fouro,text="Restore Defaults",command=self.setfpdefs)
        self.defpo.grid(row=8,column=1,padx=5,pady=5,sticky=EW)
        self.canfpo = Button(self.fouro,text="Cancel",command=self.cancel_fouro)
        self.canfpo.grid(row=8,column=2,padx=5,pady=5,sticky=EW)


    def gotfouro(self):

        """Set 4-parameter initial search settings that were input"""
        
        try:
            ysrch = string.atof(self.cur_ysrch.get())
            xsrch = string.atof(self.cur_xsrch.get())
            yiter = string.atoi(self.cur_yiter.get())
            eiter = string.atoi(self.cur_eiter.get())
            siter = string.atoi(self.cur_siter.get())
            slopemax = string.atof(self.cur_slopemax.get())
            isiter = string.atoi(self.cur_isiter.get())
            self.fourp_options['ysrch'] = ysrch
            self.fourp_options['xsrch'] = xsrch
            self.fourp_options['yiter'] = yiter
            self.fourp_options['eiter'] = eiter
            self.fourp_options['siter'] = siter
            self.fourp_options['slopemax'] = slopemax
            self.fourp_options['isiter'] = isiter
            self.update_display("\nSetting 4-parameter search options manually:")
            self.update_display(ysrch,fmt="Fractional Y-search  = %.3f\n",tag='data')
            self.update_display(xsrch,fmt="Fractional X-search  = %.3f\n",tag='data')
            self.update_display(yiter,fmt="Y-search iterations  = %d\n",tag='data')
            self.update_display(eiter,fmt="ED50 search iterations  = %d\n",tag='data')
            self.update_display(siter,fmt="Slope search iterations  = %d\n",tag='data')
            self.update_display(slopemax,fmt="Maximum slope  = %.3f\n",tag='data')
            self.update_display(isiter,fmt="Initial slope search iterations  = %d\n",tag='data')
            self.fouro.destroy()
        except:
            self.cur_ysrch.set(str(self.fourp_options['ysrch']))
            self.cur_xsrch.set(str(self.fourp_options['xsrch']))
            self.cur_yiter.set(str(self.fourp_options['yiter']))
            self.cur_eiter.set(str(self.fourp_options['eiter']))
            self.cur_siter.set(str(self.fourp_options['siter']))
            self.cur_slopemax.set(str(self.fourp_options['slopemax']))
            self.cur_isiter.set(str(self.fourp_options['isiter']))
            self.fouro.bell()
            self.whoops("Invalid specification of parameters")
            return


    def cancel_fouro(self):

        """Cancel dialog to set 4-parameter initial search settings"""
        
        self.fouro.destroy()


    def setfpdefs(self):

        """Store 4-parameter initial search settings"""
        
        self.cur_ysrch.set(str(self.fourp_defaults['ysrch']))
        self.cur_xsrch.set(str(self.fourp_defaults['xsrch']))
        self.cur_yiter.set(str(self.fourp_defaults['yiter']))
        self.cur_eiter.set(str(self.fourp_defaults['eiter']))
        self.cur_siter.set(str(self.fourp_defaults['siter']))
        self.cur_slopemax.set(str(self.fourp_defaults['slopemax']))
        self.cur_isiter.set(str(self.fourp_defaults['isiter']))
        self.fouro.update()
        

    def dummy(self):

        """A blank (dummy) method for harmless redirects"""

        pass

    
    def help_about(self):

        """Display Help->About-> splash screen"""
        
        self.helpa = Toplevel(self.root)
        self.helpa.resizable(width=0,height=0)
        self.helpa.protocol("WM_DELETE_WINDOW", self.dummy)
        if self.root.state() == 'withdrawn':
            self.helpa.title('ABE: Startup')
        else:
            self.helpa.title('ABE: Help About')
        self.splash = Canvas(self.helpa,width=320,height=320,bg='white')
        self.splash.pack()
        self.splash.create_line(160,20,160,300,fill='light blue',width=3)
        self.splash.create_line(20,140,300,140,fill='light blue',width=3)
        d = [(50,250),(90,240),(140,200),(165,150),(180,100),(230,60),(280,50)]
        self.splash.create_line(d,fill='light green',width=5,smooth=1)
        if self.root.state() == 'withdrawn':
            self.gplbutton = Button(self.helpa,text="Terms and conditions for the use of ABE 1.0", \
                              fg='dark green',command=self.showgpl)
            self.gplbutton.pack(pady=5)
            self.bailha = Button(self.helpa,text="I do NOT accept the terms and conditions ... Quit", \
                          fg='red',command=self.adios)
            self.bailha.pack(pady=5)
            self.doneha = Button(self.helpa,text="I DO accept the terms and conditions ... Continue", \
                             fg='blue',command=self.done_help_about)
            self.doneha.pack(pady=5)
        else:
            self.gplbutton = Button(self.helpa,text="Terms and conditions for the use of ABE 1.0", \
                              fg='dark green',command=self.showgpl)
            self.gplbutton.pack(pady=5)
            self.doneha = Button(self.helpa,text="Close this window", \
                             fg='blue',command=self.helpa.destroy)
            self.doneha.pack(pady=5)
        nx = 50
        ny = 45
        self.splash.create_text(nx,ny,text='A B E',font=('Courier',56,'bold'),anchor=W)
        self.splash.create_text(nx+220,ny-18,text='1.0',font=('Courier',10,'bold'),anchor=W)
        ny = ny + 55
        self.splash.create_text(nx,ny,text='A',font=('Courier',24,'bold'),anchor=W)
        self.splash.create_text(nx+22,ny-2,text='nalysis of',font=('Times',24,'italic'),anchor=W)
        ny = ny + 28
        self.splash.create_text(nx,ny,text='B',font=('Courier',24,'bold'),anchor=W)
        self.splash.create_text(nx+22,ny-2,text='ioassay',font=('Times',24,'italic'),anchor=W)
        ny = ny + 28
        self.splash.create_text(nx,ny,text='E',font=('Courier',24,'bold'),anchor=W)
        self.splash.create_text(nx+22,ny-2,text='xperiments',font=('Times',24,'italic'),anchor=W)
        ny = ny + 40
        self.splash.create_text(nx,ny,text='(c) 2002, 2003 Gordon Webster',font=('Courier',10),anchor=W)
        ny = ny + 20
        self.splash.create_text(nx,ny,text='EMD Lexigen Research Center',font=('Courier',10),anchor=W)
        ny = ny + 18
        self.splash.create_text(nx,ny,text='Bedford Campus,',font=('Courier',10),anchor=W)
        ny = ny + 18
        self.splash.create_text(nx,ny,text='45A Middlesex Turnpike',font=('Courier',10),anchor=W)
        ny = ny + 18
        self.splash.create_text(nx,ny,text='Massachusetts 01821, USA',font=('Courier',10),anchor=W)
        ny = ny + 20
        self.splash.create_text(nx,ny,text='gwebster@users.sourceforge.net',font=('Arial',10,'italic'),anchor=W)

        
    def done_help_about(self):

        """Clear 'Help->About->' dialog and restore console if starting up"""

        self.helpa.destroy()
        if self.root.state() == 'withdrawn':
            self.root.deiconify()

            
    def showgpl(self):

        """The GPL terms and conditions display"""

        self.gpldialog = Toplevel(self.root)
        self.gpldialog.resizable(width=0,height=0)
        self.gpldialog.title("ABE Terms and conditions for use")
        self.gplhead = Label(self.gpldialog,text=GPL_text,font=('Arial',10,'bold'),padx=5,fg='blue')
        self.gplhead.pack(pady=5)
        self.yesgpl = Button(self.gpldialog,text="Close",font=('Arial',10,'bold'), \
                          fg='dark green',command=self.gpldialog.destroy)
        self.yesgpl.pack(pady=5)


    def help_help(self):

        """Display the help manual in a browser window or failing that, show a help summary window"""

        if self.helpfile != None:
            try:
                webbrowser.open(self.helpfile)
                return
            except:
                pass
        self.helph = Toplevel(self.root)
        self.helph.resizable(width=0,height=0)
        self.helph.title("ABE: Help")
        self.htext = Text(self.helph,width=60,height=20,font=('Courier',12))
        self.htext.grid(row=0,column=0,sticky=W+NSEW)
        self.scroll = Scrollbar(self.helph,orient=VERTICAL,command=self.htext.yview)
        self.scroll.grid(row=0, column=1, sticky=E+NS)
        self.htext.configure(yscrollcommand=self.scroll.set)
        self.hclose = Button(self.helph,text="Close",font=('Arial',12),command=self.helph.destroy)
        self.hclose.grid(row=1,column=0,columnspan=2,padx=5,pady=5)
        self.htext.insert(END, abe_help_text)



# This is the help summary text that is displayed in the help summary window

abe_help_text = """

ABE 1.0, A bioassay data analysis package written in Python
Copyright (C) 2002, 2003 Gordon Webster
EMD Lexigen Research Center
email: gwebster@emdlexigen.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

This help text is merely a quick reference guide
to ABE. Please see the accompanying manual for a
complete description of the program.




Introduction:

ABE is a fast and convenient Python program that allows
the user to mathematically model the dose-response data
from a standard bioassay experiment and compute best-
fit ED50 values using either a four-parameter equation
or a polynomial of arbitrary degree.

The data are loaded from a data file in XML format that
contains the results for a single bioassay experiment
with data records for an arbitrary number of molecules.
The XML fields in the data file must describe the format
of the data records and the appropriate data columns to
use for the numerical anlysis (see manual for details).

Once the data are loaded, the datasets for the individual
molecules can be selected and processed. The data are
displayed visually, allowing the user to provide an
initial estimate of the ED50 value that can be used as
a basis for generating either a four-parameter and/or a
polynomial model of the the data.

The fitted data can be subsequently displayed on the
same axes for comparison with the experimental data
and to ensure that the data modeling produced sensible
solutions. All activity and the results of the data
modeling are logged and the user can save the activity
log and any generated graphs as disk files, to provide
a complete record of the data analysis. The data models
can also be saved as tables suitable for importing
into spreadsheet applications like Microsft Excel(TM).



ABE Environment Variables

For ease of use, a number of environment variables (if
currently set) allow the user to define the default
working directory for ABE, as well as the file paths
to an HTML browser application and an HTML version of
the ABE manual. If these last two environment variables
are set, ABE will launch a separate browser window and
display the manual when the Help->Help-> menu function
is selected.

The three environment variables recognised by ABE are:

ABE_PATH
The default working directory for ABE to open/save files

ABE_BROWSER
The path to an HTML browser application for displaying
an online version of the ABE manual.

ABE_HELP
The path to the ABE manual, either locally or on the web.



ABE's Menu Functions:

File->

File-> Load Bioassay Data->
Loads the selected bioassay data file for processing

File-> Save Activity Log->
Saves the log of activity and results as a text file

File-> Save Graph Image->
Saves the CURRENTLY DISPLAYED graph as a postscript file

File-> Export Results Table->
Saves any current data models in tabular format for
input into MS Excel

File-> Set Working Directory
Set the default current working directory (which
defaults to the value of the environment variable
'ABE_PATH' or the current directory)

File-> Quit->
Exits the ABE program and ends the data analysis


Data->
Once the bioassay data are loaded, this menu contains
an entry for each molecule found in the data file

Data-> Process Data->
Load and process the currently selected molecule

Data-> [molecule-name]->
Selects the molecule [molecule-name] for processing


Graph->

Graph-> Redraw Graph->
Redraws the graph window using the current options

Graph-> Border Width->
Setting a higher border width produces a smaller
graph. (This is useful for formatting the graph
for printing or if some of the fitted data points
fall outside the graph area). [Default=20 pixels]

Graph-> Show Key->
Toggles the option to display the graph data key

Graph-> Show 4-parameter Model->
Toggles the option to display the fitted 4-parameter
model on the graph [Default=on]

Graph-> Show polynomial Model->
Toggles the option to display the fitted polynomial
model on the graph [Default=on]

Graph-> Draw Border->
Toggles the option to draw a rectangular graph
border (useful for printing) [Default=on]

Graph-> Show Error bars->
Toggles the option to plot error bars for the
experimental data, provided that a column of error
data was defined in the XML records in the data
file (see manual for details)


Data Model->

Data Model-> Estimate ED50->
Allows the user to select an initial value (of x)
for the ED50 by clicking on the graph

Data Model-> Fit 4-Parameter Model->
Fits a 4-parameter model to the current data

Data Model-> Choose Polynoimial->
Choose degree of polynomial to be fitted to
the current data

Data Model-> Fit Polynomial Model->
Fits a polynomial model of the chosen degree, to
the current data

Data Model-> Show Fitted Data->
Displays a table of the model(s) for the current
data set in the activity log


Options->
Use of the features in this menu is NOT normally
necessary and should be avoided unless real
problems are encountered during the data modeling

Options-> 4-Parameter Search->
Sets some of the search options for establishing
the initial parameter estimates for the nonlinear
regression (see manual for details)

Options-> Estimate Curve Max/Min->
Sets the initial estimates of the curve y-limits
(y as x -> 0 and x -> infinity) for the nonlinear
regression (see manual for details)


Window->

Window-> Activity Log->
Displays/hides the activity log window


Help->

Help-> About->
Shows the splash window for the current version of Abe

Help-> Help->
Displays this help window

"""


GPL_text = """
ABE 1.0, A bioassay data analysis package written in Python
Copyright (C) 2002, 2003 Gordon Webster
EMD Lexigen Research Center

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the
GNU General Public License
along with this program;
if not, write to:

The Free Software Foundation, Inc.,
59 Temple Place - Suite 330,
Boston, MA  02111-1307, USA.

(A full description of this license is given in Appendix A of the
HTML version of the ABE manual, included with this software)
"""

def four_param_model1(p,*args):

    """Four parameter evaluation function supplied to the nonlinear regression function"""
    
    a = p[0]
    b = p[1]
    c = p[2]
    d = p[3]
    x = args[0]
    y = args[1]
    ydiff = []
    ydtot = 0.0
    n = 0
    for xi in x:
        yi = d + ( (a-d)/(1 + (xi/c)**b) )
        ydiff.append(yi - y[n])
        ydtot = ydtot + ydiff[n]
        n = n + 1
    yda = Numeric.array(ydiff)
    return yda


