from calendar import c
from pickle import TRUE
from this import s
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
import tkinter.messagebox

import numpy as np
import matplotlib
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import transformation as tr
import enum

class AppMode(enum.Enum):
    PlayGround = 0
    FindTrans = 1


class SimpleTableInput(tk.Frame):
    def __init__(self, parent, rows, columns, ipadx=25, ipady=5):
        tk.Frame.__init__(self, parent)
        
        self._entry = {}
        self.rows = rows
        self.columns = columns

        # register a command to use for validation
        vcmd = (self.register(self._validate), "%P")

        # create the table of widgets
        for row in range(self.rows):
            for column in range(self.columns):
                index = (row, column)
                e = tk.Entry(self, validate="key", validatecommand=vcmd, font=(f'Georgia {ipadx}'))
                e.grid(row=row, column=column, stick="nsew", ipadx=ipadx, ipady=ipady)
                self._entry[index] = e
                if column == row:
                    
                    e.insert(tk.END, "1")
                else:
                    e.insert(tk.END, "0")
        # adjust column weights so they all expand equally
        for column in range(self.columns):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        self.grid_rowconfigure(rows, weight=1)

    def get(self):
        '''Return a list of lists, containing the data in the table'''
        result = []
        for row in range(self.rows):
            current_row = []
            for column in range(self.columns):
                index = (row, column)
                current_row.append(self._entry[index].get())
            result.append(current_row)
        return np.array(result).astype(np.float64)
    
    def _validate(self, P):
        '''Perform input validation. 

        Allow only an empty value, or a value that can be converted to a float
        '''
        if P.strip() == "-":
            return True

        if P.strip() == "":
            return True

        try:
            f = float(P)
        except ValueError:
            self.bell()
            return False
        return True

class PolygonCtx:
    def __init__(self, fig=None, canv=None):
        self.figure = fig
        self.canvas = canv

class Polygon:
    def __init__(self, points, trans=None, axlim=None):
        self.polyg_ctx = PolygonCtx()
        self.transformation = trans
        self.points = points
        self.axlim = None
    
    def add_figure(self, f):
        self.polyg_ctx.figure = f

    def add_canvas(self, canvas):
        self.polyg_ctx.canvas = canvas

    def plot_polyg(self, polygon_list, size, num, t=None, c=None):

        f = plt.figure(num, figsize=size)
        title = f"Transformation{num}" if t is None else t
        plt.title(f"{title}")
        plt.grid()
        plt.axhline(0, color='black')
        plt.axvline(0, color='black')

        polygon_list = np.array(polygon_list)
        xmin = min(min(polygon_list[:, 0]))
        xmax = max(max(polygon_list[:, 0]))
        ymin = min(min(polygon_list[:, 1]))
        ymax = max(max(polygon_list[:, 1]))

        xlim = round(max(abs(xmin), abs(xmax)))
        ylim = round(max(abs(ymin), abs(ymax)))
        
        if (self.axlim is not None) and (self.axlim[0] >= xlim) and (self.axlim[1] >= ylim):   
            xlim = self.axlim[0]
            ylim = self.axlim[1]
        else:
            self.axlim = (xlim, ylim)

        xlim = xlim + 2
        ylim = ylim + 2
        
        plt.xlim([-xlim, xlim + 1])
        plt.ylim([-ylim, ylim + 1])

        plt.xticks(np.arange(-xlim, xlim, 1))
        plt.yticks(np.arange(-ylim, ylim, 1))

        colors = ['red', 'blue', 'black', 'green', 'brown', 'yellow']
        for polygon, color in zip(polygon_list, colors):
            if c is None:
                clr = color
            else:
                clr = c

            t = plt.Polygon(polygon.T, color=c)
            plt.gca().add_patch(t)

        return f

class Polygons(tk.Frame):
    def __init__(self, parent, mode=AppMode.PlayGround, id=0, is_target=False, color=None):
        tk.Frame.__init__(self, parent)
        self.color = color
        self.is_target = is_target
        self.id = id
        self.mode=mode
        self.main_polygon: Polygon = None

        self.get_polygon()

        if mode == AppMode.PlayGround:
            # Transformed polygons
            self.polygonsFrame = tk.Frame(parent) # Right Side for Polygons (plots+scroll)
            self.TransformedPolygCanv = tk.Canvas(self.polygonsFrame, borderwidth=0, background="#ffffff")
            self.TransformedPolygFrame = tk.Frame(self.TransformedPolygCanv) 

            self.vsb = tk.Scrollbar(self.polygonsFrame, orient="vertical", command=self.TransformedPolygCanv.yview)
            self.TransformedPolygCanv.configure(yscrollcommand=self.vsb.set)

            self.polygonsFrame.pack(side=tk.RIGHT, fill="both", expand=True, anchor=tk.NE)
            self.vsb.pack(side="right", fill="y")
            self.TransformedPolygCanv.create_window((4, 4), window=self.TransformedPolygFrame, anchor="ne", tags="self.TransformedPolygFrame")
            self.TransformedPolygCanv.pack(side="left", fill="both", expand=True)

            self.TransformedPolygFrame.bind("<Configure>", self.onFrameConfigure)

        self.polygons = []
        
    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.TransformedPolygCanv.configure(scrollregion=self.TransformedPolygCanv.bbox("all"))

    def get_polygon(self, size=(4, 4)):
        points = []
        fignum = 1000 + self.id * 3 # just for unique figure ID 

        fig = plt.figure(num=fignum)
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, self)

        xlim = 6
        ylim = 6
        plt.title("Select Polygon Corners - Left Click   |   Undo selection - Right Click   |   Finish - Press wheel", fontsize=7)
        plt.xlim([-xlim, xlim + 1])
        plt.ylim([-ylim, ylim + 1])
        plt.grid()
        plt.axhline(0, color='black')
        plt.axvline(0, color='black')
        plt.xticks(np.arange(-xlim, xlim, 1))
        plt.yticks(np.arange(-ylim, ylim, 1))
  
        canvas.draw()
        def on_click(event):
            if event.button is MouseButton.LEFT:
                if event.inaxes is not None:
                    points.append(np.array([event.xdata, event.ydata]))
                else:
                    print('Clicked ouside axes bounds but inside plot window')
            if event.button is MouseButton.RIGHT:
                if points:
                    point = points.pop()
                    for line in ax.lines:
                        line.set_marker(None)
            if event.button is MouseButton.MIDDLE:
                polyg = Polygon(points = np.array(points).T)
                event.canvas.mpl_disconnect(cid)
                plt.close(fig)
                canvas.get_tk_widget().destroy()           
                self.draw(polyg=polyg, figid=fignum)
                self.main_polygon = polyg
            
            if points:
                np_points = np.array(points).T
                x = np_points[0].tolist()
                y = np_points[1].tolist()
                ax.plot(x, y, '.', markersize=12 )
        
            canvas.draw()

        cid = fig.canvas.callbacks.connect('button_press_event', on_click)
        canvas.get_tk_widget().grid(row=1, column=0)


    def draw(self, polyg: Polygon, size=(5, 5), figid=None):
        # Check if drawing the first polygon or the transformed
        if self.main_polygon is None:
            frame = self
            figure_id = 0
            title = "Original Polygon"
            if self.is_target:
                title = "Target Polygon"
        else:
            frame = self.TransformedPolygFrame
            figure_id = len(self.polygons) + 1
            title = None
        
        if figid is not None:
            figure_id = figid

        f = polyg.plot_polyg([polyg.points], size=size, num=figure_id, t=title, c=self.color)

        canvas = FigureCanvasTkAgg(f, frame)
        canvas.draw()

        row = int(len(self.polygons) / 2)
        col = len(self.polygons) % 2
        
        canvas.get_tk_widget().grid(row=row, column=col, columnspan=1) 
                                    
        polyg.add_figure(f)
        polyg.add_canvas(canvas)
        
            
    def transform(self, transformations):
        if self.polygons:
            polyg = self.polygons[-1]
        else:
            polyg = self.main_polygon
        temp = tr.apply_transformation(transformation_list=transformations, points=polyg.points)
        new_polyg = Polygon(points=temp, trans=transformations[0])
        self.draw(polyg=new_polyg, size=(4, 4))
        self.polygons.append(new_polyg)

    def calculate_transformation_accum(self):
        if not self.polygons:
            return None
        polygons_transformed = self.polygons
        transformations = [polygon.transformation for polygon in polygons_transformed]
        trans = tr.calc_trans(transformations)
        
        return trans
    
    def destroy_polyg(self, polyg):
        plt.close(polyg.polyg_ctx.figure)
        polyg.polyg_ctx.canvas.get_tk_widget().destroy()
    
    def destroy_all(self):
        for polyg in self.polygons:
            self.destroy_polyg(polyg)
        self.destroy_polyg(self.main_polygon)
        self.main_polygon = None
        self.polygons = []

    def destroy_last(self):
        if len(self.polygons) == 0:
            print("No Polygons nothing to undo")
        else:
            polyg = self.polygons[-1]
            self.destroy_polyg(polyg=polyg)
            self.polygons = self.polygons[:-1]
        


class FindTransformation(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.results = None
        self.controller = controller
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack()

        self.myFont = font.Font(size=10)

        self.ResultsFrame = tk.Frame(self)
        self.ResultsFrame.pack(side=tk.TOP, fill=tk.X, expand=True)

        ButtonsFrame = tk.Frame(self)
        ButtonsFrame.pack(side=tk.TOP)

        MainPlotFrame = tk.Frame(self)
        MainPlotFrame.pack(side = tk.TOP, expand=True, fill="both")

        self.submit = tk.Button(ButtonsFrame, text="Submit", command=self.on_submit, height=3, width=10)
        self.submit['font'] = self.myFont
        self.submit.pack(side=tk.LEFT, expand=True)

        self.restart = tk.Button(ButtonsFrame, text="Restart", command=self.on_restart, height=3, width=10)
        self.restart['font'] = self.myFont
        self.restart.pack(side=tk.LEFT, expand=True)

        self.polyg_main = Polygons(MainPlotFrame, mode=AppMode.FindTrans, id=1, color="green")
        self.polyg_main.pack(side=tk.LEFT)
        
        self.polyg_target = Polygons(MainPlotFrame, mode=AppMode.FindTrans, id=2, color='red', is_target=True)
        self.polyg_target.pack(side=tk.LEFT)

    def on_restart(self):
        self.polyg_main.destroy_all()
        self.polyg_target.destroy_all()

        self.polyg_main.get_polygon()
        self.polyg_target.get_polygon()
        self.transformation = None
        self.update_result()

    def on_submit(self):
        self.compute_transformation()
        self.update_result()

    def update_result(self):
        if self.results:
            self.results.pack_forget()

        if self.transformation is not None:
            self.results = tk.Text(self.ResultsFrame, undo = True, height = 7, width = 45)

            self.results.insert("1.0", "Transformation from Original to Target Polygon\n\n")
            self.results.insert("2.0", self.transformation)
            self.results.tag_add("start", "1.0", "2.0")
            self.results.tag_config("start", background="yellow", foreground="red")
     
            self.results.pack()

    def compute_transformation(self):
        while (self.polyg_main is None or self.polyg_target is None):
            continue
        target_points   = self.polyg_target.main_polygon.points
        original_points = self.polyg_main.main_polygon.points

        H = tr.compute_transformation(target_points, original_points)
        self.transformation = np.round(H, decimals=3)

class TransformationPlayGround(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack()

        self.myFont = font.Font(size=10)
        self.transformations_text = []
        # Main Window Frame
        # w = tk.Label(self, text ='Draw Polygon(Left) or insert Coordinates (Right)', font = "40",fg="Navyblue")
        # w.grid(row=0, column=1) 
        
        ButtonFrameInPlot = tk.Frame(self)
        ButtonFrameInPlot.pack(side=tk.TOP)

        self.ResultsFrame = tk.Frame(self)
        self.ResultsFrame.pack(side=tk.TOP, fill=tk.X, expand=True)

        # Main Plot Frame
        MainPlotFrame = tk.Frame(self)
        MainPlotFrame.pack(side = tk.TOP, expand=True, fill="both")

        self.polyg = Polygons(MainPlotFrame, mode=AppMode.PlayGround, id=0)
        self.polyg.pack(side = tk.LEFT)        

        self.table = SimpleTableInput(self, 3, 3, ipadx=10, ipady=3)
        self.table.pack(side=tk.TOP)

        self.submit = tk.Button(ButtonFrameInPlot, text="Submit", command=self.on_submit, height=4, width=5)
        self.submit['font'] = self.myFont
        self.submit.grid(row=0, column=1)
    
        self.undo = tk.Button(ButtonFrameInPlot, text="Undo", command=self.on_undo, height=4, width=5)
        self.undo['font'] = self.myFont
        self.undo.grid(row=0, column=2)

        self.restart = tk.Button(ButtonFrameInPlot, text="Restart", command=self.on_restart, height=4, width=10)
        self.restart['font'] = self.myFont
        self.restart.grid(row=0, column=3)

    def update_results(self):
        
        transformations = [polygon.transformation for polygon in self.polyg.polygons]
        full_trans = self.polyg.calculate_transformation_accum()

        for tt in self.transformations_text:
            tt.pack_forget()
        
        self.transformations_text = []
        for trans in transformations:
            transformation_text = tk.Text(self.ResultsFrame, undo = True, height = 5, width = 12)
            transformation_text.insert("1.0", trans)
            self.transformations_text.append(transformation_text)
        
        
        for tt in reversed(self.transformations_text):
            tt.pack(side=tk.LEFT)

        if full_trans is not None:
            transformation_text = tk.Text(self.ResultsFrame, undo = True, height = 6, width = 22)
            transformation_text.insert("1.0", "Overall Transformation\n\n")
            transformation_text.insert("2.0", f"{full_trans}")
            transformation_text.tag_add("start", "1.0", "2.0")
            transformation_text.tag_config("start", background="yellow", foreground="red")
            transformation_text.pack(side=tk.LEFT)
            self.transformations_text.append(transformation_text)
        
    def on_restart(self):
        self.polyg.destroy_all()
        self.polyg.get_polygon()
        self.update_results()

    def on_submit(self):
        trans = self.table.get()
        self.polyg.transform(transformations=[trans])
        self.update_results()

    def on_undo(self):
        self.polyg.destroy_last()
        self.update_results()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Start Page\n Choose Between the next apps", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Go to Transformation PlayGround app",  font = font.Font(size = 20),
                            command=lambda: controller.show_frame("TransformationPlayGround"))
        button2 = tk.Button(self, text="Go to Find Transformationo app",  font = font.Font(size = 20),
                            command=lambda: controller.show_frame("FindTransformation"))
        button1.pack(expand=True, fill="both")
        button2.pack(expand=True, fill="both")
        
class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Transformations GUI")
    
        width=1440
        height=800
        self.geometry(f"{width}x{height}")
        self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.maxsize(width, height)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, TransformationPlayGround, FindTransformation):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")


    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = MainApplication()

    def on_closing():
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            app.quit()
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
            

