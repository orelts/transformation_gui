import tkinter as tk
from tkinter import ttk
import tkinter.font as font
import tkinter.messagebox
import numpy as np

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import transformation as tr
from matplotlib.figure import Figure

class SimpleTableInput(tk.Frame):
    def __init__(self, parent, rows, columns):
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
                e = tk.Entry(self, validate="key", validatecommand=vcmd, font=('Georgia 30'))
                e.grid(row=row, column=column, stick="nsew", ipadx=50, ipady=10)
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
        if P.strip() == "":
            return True

        try:
            f = float(P)
        except ValueError:
            self.bell()
            return False
        return True


class Polygon:
    def __init__(self, points, trans=None):
        self.transformation_applied_before = trans
        self.points = points
        self.figure = None
        self.canvas = None
    
    def add_figure(self, f):
        self.figure = f

    def add_canvas(self, canvas):
        self.canvas = canvas

    def plot_polyg(self, polygon_list, size, num):
        colors = ['red', 'blue', 'black', 'green', 'brown', 'yellow']
        f = plt.figure(num, figsize=size)
        plt.grid()
        plt.axhline(0, color='black')
        plt.axvline(0, color='black')

        polygon_list = np.array(polygon_list)
        xmin = min(min(polygon_list[:, 0]))
        xmax = max(max(polygon_list[:, 0]))
        ymin = min(min(polygon_list[:, 1]))
        ymax = max(max(polygon_list[:, 1]))

        xlim = round(max(abs(xmin), abs(xmax)) * 2)
        ylim = round(max(abs(ymin), abs(ymax)) * 2)

        plt.xlim([-xlim, xlim + 1])
        plt.ylim([-ylim, ylim + 1])

        plt.xticks(np.arange(-xlim, xlim, 1))
        plt.yticks(np.arange(-ylim, ylim, 1))
        for polygon, color in zip(polygon_list, colors):
            t = plt.Polygon(polygon.T, color=color)
            plt.gca().add_patch(t)

        return f

class Polygons(tk.Frame):
    def __init__(self, parent, points):
        tk.Frame.__init__(self, parent)
        points = tr.get_points_single(-1)
        self.polygons = []
        self.draw(polyg=Polygon(points=points))
        
    def draw(self, polyg, size=(5, 5)):    
        f = polyg.plot_polyg([polyg.points], size=size, num=len(self.polygons))
        plt.text(0.5,0.5,f'{polyg.transformation_applied_before}',horizontalalignment='center',
        verticalalignment='center', fontsize=14, color='r')
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
     
        canvas._tkcanvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        polyg.add_figure(f)
        polyg.add_canvas(canvas)
        
        self.polygons.append(polyg)
        
    def transform(self, transformations):
        polyg = self.polygons[-1]

        temp = tr.to_hom(polyg.points)
        temp = tr.apply_transformation(transformation_list=transformations, points=temp)
        temp = tr.to_het(temp)

        new_polyg = Polygon(points=temp, trans=transformations[0])

        self.draw(polyg=new_polyg)

    def calculate_transformation_accum(self):
        polygons_transformed = self.polygons[1:]
        transformations = [polygon.transformation_applied_before for polygon in polygons_transformed]
        trans = tr.calc_trans(transformations)
        
        return trans
    
    def destroy_last(self):
        if len(self.polygons) <= 1:
            print("No Polygons nothing to undo")
        else:
            polyg = self.polygons[-1]
            polyg.canvas.get_tk_widget().destroy()
            
            self.polygons = self.polygons[:-1]
        
        
class MyNiceTransformations(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Transformations GUI")
        
        myFont = font.Font(size=30)
        self.polyg = Polygons(self, points=np.array([[1,1], [2,2], [0,1]]).T)
        self.polyg.grid(row=0, column=0)
        
        self.table = SimpleTableInput(self, 3, 3)
        self.table.grid(row=1, column=0)
        
        self.submit = tk.Button(self.polyg, text="Submit", command=self.on_submit, height=5, width=20)
        self.submit['font'] = myFont
        self.submit.pack(side=tk.RIGHT)
    
        self.undo = tk.Button(self.polyg, text="Undo", command=self.undo, height=5, width=20)
        self.undo['font'] = myFont
        self.undo.pack(side=tk.RIGHT)

        self.full_trans = tk.Button(self.polyg, text="Transformation", command=self.full_trans, height=5, width=20)
        self.full_trans['font'] = myFont
        self.full_trans.pack(side=tk.RIGHT)

        
    def on_submit(self):
        trans = self.table.get()
        self.polyg.transform(transformations=[trans])

    def undo(self):
        self.polyg.destroy_last()

    def full_trans(self):
        trans = self.polyg.calculate_transformation_accum()
        tkinter.messagebox.showinfo("Total Transformations",f"{trans}")


app = MyNiceTransformations()
app.mainloop()
        

