#!/usr/bin/env python

"""
Create a GUI to play around with the parameters of a fitting function.

Requires:
- Tkinter (which should come bundled in python)
- numpy
- matplotlib

Robin Aggleton July 2015
"""

import matplotlib
matplotlib.use('TkAgg')
# implement the default mpl key bindings
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import os
from math import *
import numpy as np
import random
import ROOT
import common_utils as cu
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
import tkMessageBox
import tkFileDialog

root = Tk.Tk()
root.wm_title("Play with fitting function by Robin Aggleton")

# Put the points for the graph here x, y, x errorbars, y errorbars:
xpt = [16.3945, 16.0968, 17.2177, 18.9381, 20.9077, 23.269, 25.7539, 28.328, 31.072, 37.2628, 52.434, 68.4167, 84.925]
ypt = [0.992469, 1.48571, 1.60127, 1.60084, 1.62146, 1.60733, 1.60065, 1.58229, 1.55749, 1.51606, 1.43605, 1.39438, 1.41854]
errx = [0.084203, 0.0421546, 0.0315441, 0.027393, 0.0278687, 0.0326988, 0.0392042, 0.0454415, 0.0494926, 0.0433829, 0.165039, 0.679132, 2.62304]
erry = [0.00537132, 0.00663933, 0.00473137, 0.00212173, 0.0019282, 0.00178581, 0.00191178, 0.00184522, 0.00267766, 0.001325, 0.0036714, 0.0110765, 0.0881421]

# fitting function and starting parameters
def pf_func(et, params):
    return params[0] + (params[1]/(np.power(np.log10(et), 2)+params[2])) + params[3] * np.exp(-1.*params[4]*np.power(np.log10(et)-params[5], 2))

# individual components of the fitting function so we can see how to modify each part
def pf_1(et, params):
    return params[0] * np.ones_like(et)


def pf_2(et, params):
    return params[1]/(np.power(np.log10(et), 2)+params[2])


def pf_3(et, params):
    return params[3] * np.exp(-1.*params[4]*np.power(np.log10(et)-params[5], 2))


p0 = 0.37419355
p1 = -0.55483871
p2 = -6.1612903
p3 = 6129032.0
p4 = 0.075557264
p5 = -13.548387

p0=   1.64971e-01
p1=   5.28710e+00
p2=   5.57367e+00
p3=   1.10390e+04
p4=   3.95751e-03
p5=  -4.78727e+01
params = [p0, p1, p2, p3, p4, p5]
original_params = params[:]

# ET arrays, pre and post calibration
# do at 0.5 GeV intervals since our pre-calibrated jets have 0.5 GeV granularity.
et_min = 0.5
et_max = 250
et_interval = 0.5
et = np.arange(et_min, et_max + et_interval, et_interval)

##############
# Main plotting area
##############
def draw_reference_graph(axes, x, y, err_x, err_y):
    """Draw the reference graph"""
    axes.errorbar(xpt, ypt, xerr=errx, yerr=erry, fmt='-', lw=2, color='black')


def plot_fit_func(axes, et, params):
    """Plot the fit function on an Axes object"""
    axes.plot(et, pf_func(et, params), lw=2, color='red', label='PF function')
    axes.plot(et, pf_1(et, params), lw=1, color='blue', label='p0')
    axes.plot(et, pf_2(et, params), lw=1, color='green', label='p1/((log(et))^2 + p2)')
    axes.plot(et, pf_3(et, params), lw=1, color='orange', label='p3 * exp[-p4 * (log(et)-p5)^2]')
    axes.axis([et_min, et_max, y_min, y_max])
    axes.set_xlabel("ET")
    axes.set_ylabel("Correction Factor")
    axes.minorticks_on()
    axes.grid(b=True, which='both')
    axes.legend(fontsize=10, loc=0)
    axes.set_title("p0 + (p1 / ((log10(et))^2 + p2)) + p3 * exp(-p4 * (np.log10(et) - p5)^2)", fontsize=12, y=1.04)


fig = Figure(figsize=(7, 7))
axes = fig.add_subplot(111)

y_min, y_max = 0, 2.5

draw_reference_graph(axes, xpt, ypt, errx, erry)
plot_fit_func(axes, et, params)

# Setup 3 pane window
# plot_pane = Tk.PanedWindow()
# plot_pane.pack(expand=1)

# mod_pane = Tk.PanedWindow(orient=Tk.HORIZONTAL)
# mod_pane.pack(expand=1)

button_pane = Tk.PanedWindow(orient=Tk.HORIZONTAL)
button_pane.pack(expand=1)

fitting_pane = Tk.PanedWindow(orient=Tk.HORIZONTAL)
fitting_pane.pack(expand=1)

# A tk.DrawingArea for the main plot
canvas = FigureCanvasTkAgg(fig, master=root)
# canvas = FigureCanvasTkAgg(fig, master=plot_pane)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
# plot_pane.add(canvas.get_tk_widget())

#############
# The matplotlib toolbar
#############
# toolbar = NavigationToolbar2TkAgg( canvas, root )
# toolbar.update()
# canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
# plot_pane.add(canvas._tkcanvas)

#############
# Add sliders with multiplier entry boxes
##############
sliders = []
boxes = []

def set_slider_box_values(slider, multiplier_box, value):
    """Set slider and multiplier box value, since slider only goes -1 to 1."""
    # break up the number such that x = y * 10^n
    # this way we can fit it on a scale of [-1, 1]
    n = ceil(log10(abs(value))) # power of 10
    y = value / pow(10, n)
    copysign(y,value) # mantissa
    slider.set(y)
    multiplier_box.delete(0, Tk.END)
    multiplier_box.insert(5, pow(10, n))


def update_plot(event):
    """Update the main plot whenever a slider or multiplier box is updated."""
    for i, (slider, box) in enumerate(zip(sliders, boxes)):
        params[i] = slider.get() * float(box.get())
    axes.clear()
    draw_reference_graph(axes, xpt, ypt, errx, erry)
    plot_fit_func(axes, et, params)
    canvas.draw()


def validate_float(contents):
    """Validate that contents is floating-point number"""
    try:
        val = float(contents)
    except ValueError:
        return False
    return True


for i, p in enumerate(params):
    slider = Tk.Scale(master=root, label='p%d' %i, orient=Tk.HORIZONTAL, from_=-1, to=1,
                      resolution=1E-8, length=500, tickinterval=1, command=update_plot)
    slider.pack(fill=Tk.X)
    sliders.append(slider)
    box = Tk.Entry(master=root)#, validatecommand=validate_float, validate='key')
    box.register(validate_float)
    box.bind('<Key>', update_plot)
    box.pack()
    boxes.append(box)
    set_slider_box_values(slider, box, p)

##############
# Add buttons
##############

def print_params():
    for i,p in enumerate(params):
        print 'p{0} = {1}'.format(i, p)
    print et
    print pf_func(et, params)


print_button = Tk.Button(master=root, text='Print params', command=print_params)
# print_button.pack(side=Tk.LEFT, expand=True)
button_pane.add(print_button)


def reset_params():
    for slider, box, param in zip(sliders, boxes, original_params):
        set_slider_box_values(slider, box, param)
    # update_plot(None)


reset_button = Tk.Button(master=root, text='Reset params', command=reset_params)
# reset_button.pack(side=Tk.LEFT, expand=True)
button_pane.add(reset_button)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

quit_button = Tk.Button(master=root, text='Quit', command=_quit)
# quit_button.pack(side=Tk.LEFT, expand=True)
button_pane.add(quit_button)

###########
# Fitting
###########

label_min = Tk.Label(root, text="ET min:")
label_max = Tk.Label(root, text="ET max:")
label_end = Tk.Label(root, text="Fit end condition:")
box_min = Tk.Entry(root, width=3)
box_min.insert(3, 20)
box_max = Tk.Entry(root, width=3)
box_max.insert(3, 200)
box_end = Tk.Entry(root, width=3)
box_end.insert(3, 1.5)
fitting_pane.add(label_min)
fitting_pane.add(box_min)
fitting_pane.add(label_max)
fitting_pane.add(box_max)
fitting_pane.add(label_end)
fitting_pane.add(box_end)


def calc_penalty(params, min_x, max_x):
    """Calculates a penalty that is proportional to the 'distance' between
    the graph and the function. Based on chi2, but with a sign to indicate
    on average whether the new function is above or below the graph. """
    pen = 0
    sign = 0
    counter = 0
    for i, (x, y_graph, yerr) in enumerate(zip(xpt, ypt, erry)):
        if min_x < x < max_x:
            counter += 1
            y_new = pf_func(x, params)
            pen += pow(y_new - y_graph, 2)/pow(yerr, 2)
            sign += (y_new - y_graph)/abs(y_new - y_graph)
    sign = sign/abs(sign)
    return sign * np.sqrt(pen) / counter


def generate_new_params(prev_params):
    new_params = prev_params[:]
    for i, p in enumerate(new_params):
        if random.random() > 0.5:
            new_params[i] += (random.random()/1. * p)
        else:
            new_params[i] -= (random.random()/1. * p)
    return new_params


def sensibility_check(params):
    """Check no poles nor goes negative"""
    y = pf_func(et, params)
    pair_diff = np.array([abs(y-x) for x,y in zip(y[:-1], y[1:])])
    return np.min(y) > 0 and np.max(y) < 5# and np.max(pair_diff) < 2


def approx_fit():
    """Do some Markov Chain type fitting to get a very rough approximation"""

    old_params = params[:]
    min_x = float(box_min.get())
    max_x = float(box_max.get())
    finish_condition = abs(float(box_end.get()))
    old_penalty = calc_penalty(old_params, min_x, max_x)
    found_fit = abs(old_penalty) < finish_condition
    stuck_counter = 0

    while not found_fit:
        if stuck_counter % 10000 == 0 and stuck_counter > 0:
            print "May be getting stuck...", stuck_counter

        new_params = generate_new_params(old_params)
        new_penalty = calc_penalty(new_params, min_x, max_x)
        if abs(new_penalty) < abs(old_penalty) and sensibility_check(new_params):
            print "Move"
            print 'old params:', old_params
            print 'new params:', new_params
            print 'old penalty:', old_penalty
            print 'new penalty:', new_penalty
            old_params, old_penalty = new_params[:], new_penalty
            for slider, box, param in zip(sliders, boxes, new_params):
                set_slider_box_values(slider, box, param)
            stuck_counter = 0
            update_plot(None)
        else:
            stuck_counter += 1

        # finishing condition
        if abs(new_penalty) < finish_condition:
            print "Finished fitting"
            tkMessageBox.showinfo("Done", "Finished fitting\nFinal penalty: %f" % abs(new_penalty))
            found_fit = True

        if stuck_counter == 100000:
            print "Got stuck, please try again"
            tkMessageBox.showwarning("Fit stalled", "Fitter got stuck, please try again")
            stuck_counter = 0
            break


fit_button = Tk.Button(fit_frame, text='Fit', command=approx_fit)
fit_button.pack(side=Tk.RIGHT)


##############
# Draw!
##############
# hack to bring the window to the front
os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
Tk.mainloop()
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.


