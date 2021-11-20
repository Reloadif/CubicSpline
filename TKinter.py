from tkinter import *
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np


# Структура, описывающая сплайн на каждом сегменте сетки
class SplineTuple:
    def __init__(self, a, b, c, d, x):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.x = x
 
# Построение сплайна
# x - узлы сетки, должны быть упорядочены по возрастанию, кратные узлы запрещены
# y - значения функции в узлах сетки
# n - количество узлов сетки
def BuildSpline(x, y, n):
    # Инициализация массива сплайнов
    splines = [SplineTuple(0, 0, 0, 0, 0) for _ in range(0, n)]
    for i in range(0, n):
        splines[i].x = x[i]
        splines[i].a = y[i]
    
    splines[0].c = splines[n - 1].c = 0.0
    
    # Решение СЛАУ относительно коэффициентов сплайнов c[i] методом прогонки для трехдиагональных матриц
    # Вычисление прогоночных коэффициентов - прямой ход метода прогонки
    alpha = [0.0 for _ in range(0, n - 1)]
    beta  = [0.0 for _ in range(0, n - 1)]
 
    for i in range(1, n - 1):
        hi  = x[i] - x[i - 1]
        hi1 = x[i + 1] - x[i]
        A = hi
        C = 2.0 * (hi + hi1)
        B = hi1
        F = 6.0 * ((y[i + 1] - y[i]) / hi1 - (y[i] - y[i - 1]) / hi)
        z = (A * alpha[i - 1] + C)
        alpha[i] = -B / z
        beta[i] = (F - A * beta[i - 1]) / z
  
 
    # Нахождение решения - обратный ход метода прогонки
    for i in range(n - 2, 0, -1):
        splines[i].c = alpha[i] * splines[i + 1].c + beta[i]
    
    # По известным коэффициентам c[i] находим значения b[i] и d[i]
    for i in range(n - 1, 0, -1):
        hi = x[i] - x[i - 1]
        splines[i].d = (splines[i].c - splines[i - 1].c) / hi
        splines[i].b = hi * (2.0 * splines[i].c + splines[i - 1].c) / 6.0 + (y[i] - y[i - 1]) / hi
    return splines
 
# Вычисление значения интерполированной функции в произвольной точке
def Interpolate(splines, x):
    if not splines:
        return None # Если сплайны ещё не построены - возвращаем NaN
    
    n = len(splines)
    s = SplineTuple(0, 0, 0, 0, 0)
    
    if x <= splines[0].x: # Если x меньше точки сетки x[0] - пользуемся первым эл-тов массива
        s = splines[0]
    elif x >= splines[n - 1].x: # Если x больше точки сетки x[n - 1] - пользуемся последним эл-том массива
        s = splines[n - 1]
    else: # Иначе x лежит между граничными точками сетки - производим бинарный поиск нужного эл-та массива
        i = 0
        j = n - 1
        while i + 1 < j:
            k = i + (j - i) // 2
            if x <= splines[k].x:
                j = k
            else:
                i = k
        s = splines[j]
    
    dx = x - s.x
    # Вычисляем значение сплайна в заданной точке по схеме Горнера 
    return s.a + (s.b + (s.c / 2.0 + s.d * dx / 6.0) * dx) * dx;

def calculateNexPoint(arrayX, spline):
    arr = []
    for x in arrayX:
        arr.append(Interpolate(spline, x))
    return arr


def calculateSpline():
    arrayX = []
    arrayY = []

    for widget in outputMainFrame.winfo_children():
        widget.destroy()

    for widget in plotFrame.winfo_children():
        widget.destroy()
  
    for x in arrayOfInputX:
        if(x.get() == ""):
            break
        else: 
            arrayX.append( float( x.get() ) )

    for y in arrayOfInputY:
        if(y.get() == ""):
            break
        else: 
            arrayY.append( float( y.get() ) )

    if(len(arrayX) == 0 or len(arrayY) == 0):
        if(len(arrayX) == 0 and len(arrayY) == 0):
            messagebox.showerror("Ошибка", "Пустые поля X и Y!")
            return
        elif(len(arrayY) == 0):
            messagebox.showerror("Ошибка", "Пустые поля Y!")
            return
        else:
            messagebox.showerror("Ошибка", "Пустые поля X!")
            return
    elif(len(arrayX) != len(arrayY)):
        messagebox.showerror("Ошибка", "Количество введеных точек X не соответсвует количеству значений Y!")
        return
    elif(len(arrayX) == 1):
        messagebox.showerror("Ошибка", "Сплайн не стоится по одной точке!")
        return

    sortedArrayX = list(arrayX)
    sortedArrayX.sort()
    sortedArrayY = []

    for i in range(len(sortedArrayX)):
        sortedArrayY.append(arrayY[arrayX.index(sortedArrayX[i])])

    spline = BuildSpline(sortedArrayX, sortedArrayY, len(sortedArrayX))
    arrayNewX = np.arange(sortedArrayX[0], sortedArrayX[-1], 0.01)

    placeCoefficient(spline, sortedArrayX)

    # the figure that will contain the plot
    fig = Figure(figsize = (4, 4), dpi = 100)
  
    # adding the subplot
    plot1 = fig.add_subplot(111)
    plot1.grid(True)

    # plotting the graph
    plot1.plot(sortedArrayX, sortedArrayY, 'o', arrayNewX, calculateNexPoint(arrayNewX,spline), '-')
  
    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=plotFrame)  
    canvas.draw()
  
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(relx=0.0)
    
def placeCoefficient(spline, arrayX):
    outputGapsFrame = Frame(outputMainFrame)
    outputGapsFrame.place(relx=0.0, rely=0.05, relwidth=1, relheight=0.15)

    title = Label(outputGapsFrame, text="G", font=40)
    title.place(relx=0.0)

    validRange = len(arrayX)-1

    for i in range(validRange):
        gaps = str(arrayX[i]) + ".." + str(arrayX[i+1])
        title = Label(outputGapsFrame, width=6, text=gaps)
        title.place(relx=0.08*(i+1), rely=0.1)

    outputAFrame = Frame(outputMainFrame)
    outputAFrame.place(relx=0.0, rely=0.25, relwidth=1, relheight=0.15)

    title = Label(outputAFrame, text="A", font=40)
    title.place(relx=0.0)

    for i in range(validRange):
        title = Label(outputAFrame, width=6, text=str('{:.5f}'.format(spline[i+1].a)))
        title.place(relx=0.08*(i+1), rely=0.1)

    outputBFrame = Frame(outputMainFrame)
    outputBFrame.place(relx=0.0, rely=0.45, relwidth=1, relheight=0.15)

    title = Label(outputBFrame, text="B", font=40)
    title.place(relx=0.0)

    for i in range(validRange):
        title = Label(outputBFrame, width=6, text=str('{:.5f}'.format(spline[i+1].b)))
        title.place(relx=0.08*(i+1), rely=0.1)

    outputCFrame = Frame(outputMainFrame)
    outputCFrame.place(relx=0.0, rely=0.65, relwidth=1, relheight=0.15)

    title = Label(outputCFrame, text="C", font=40)
    title.place(relx=0.0)

    for i in range(validRange):
        title = Label(outputCFrame, width=6, text=str('{:.5f}'.format(spline[i+1].c)))
        title.place(relx=0.08*(i+1), rely=0.1)

    outputDFrame = Frame(outputMainFrame)
    outputDFrame.place(relx=0.0, rely=0.85, relwidth=1, relheight=0.15)

    title = Label(outputDFrame, text="D", font=40)
    title.place(relx=0.0)

    for i in range(validRange):
        title = Label(outputDFrame, width=6, text=str('{:.5f}'.format(spline[i+1].d)))
        title.place(relx=0.08*(i+1), rely=0.1)




# the main Tkinter window
window = Tk()
  
# setting the title 
window.title('Кубическая сплайн-интерполяция')
window.geometry("800x600")
window.resizable(width=False, height=False)

plotFrame = Frame(window)
plotFrame.place(relx=0.0, rely=0.0, relwidth=0.65, relheight=0.65)

inputMainFrame = Frame(window)
inputMainFrame.place(relx=0.68, rely=0.0, relwidth=0.32, relheight=0.5)

inputXFrame = Frame(inputMainFrame)
inputXFrame.place(relx=0.0, rely=0.0, relwidth=0.5)

title = Label(inputXFrame, text="X", font=40)
title.pack()

arrayOfInputX = []

for i in range(12):
    title = Label(inputXFrame, text=str(i+1))
    title.place(relx=0.0, rely=0.1+0.075*i)
    input = Entry(inputXFrame, bg="white", width=15)
    arrayOfInputX.append(input)
    input.pack()

inputYFrame = Frame(inputMainFrame)
inputYFrame.place(relx=0.5, rely=0.0, relwidth=0.5)

title = Label(inputYFrame, text="Y", font=40)
title.pack()

arrayOfInputY = []

for i in range(12):
    title = Label(inputYFrame, text=str(i+1))
    title.place(relx=0.0, rely=0.1+0.075*i)
    input = Entry(inputYFrame, bg="white", width=15)
    arrayOfInputY.append(input)
    input.pack()

button = Button(inputMainFrame, text="Построить", command=calculateSpline)
button.pack(side=BOTTOM)

outputMainFrame = Frame(window)
outputMainFrame.place(relx=0.0, rely=0.7, relwidth=1, relheight=0.3)

placeCoefficient(0, [])

window.mainloop()