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
graph_x = [12.84, 13.80, 15.12, 16.77, 18.75, 21.01, 23.57, 26.42, 29.52, 32.75,
           36.16, 39.70, 43.45, 47.01, 50.91, 54.64, 58.39, 62.28, 66.34, 70.26,
           73.82, 77.94, 81.55, 85.62, 89.65, 93.94, 97.85, 101.37, 106.05,
           110.05, 113.95, 118.18, 122.26, 126.61, 131.32, 135.72, 139.71,
           145.15, 149.12, 154.08, 158.65, 163.57, 168.58, 172.46, 178.72,
           183.33, 186.73, 192.04, 198.36, 201.31, 206.18, 210.25, 215.56,
           219.23, 222.31, 228.64, 230.82, 235.77, 240.92]
graph_y = [1.24, 1.45, 1.58, 1.66, 2.09, 2.06, 2.07, 1.93, 1.87, 1.76, 1.70,
           1.63, 1.57, 1.54, 1.50, 1.46, 1.43, 1.41, 1.38, 1.35, 1.34, 1.32,
           1.31, 1.29, 1.27, 1.26, 1.25, 1.24, 1.23, 1.22, 1.22, 1.20, 1.20,
           1.19, 1.18, 1.17, 1.17, 1.16, 1.15, 1.15, 1.14, 1.14, 1.14, 1.14,
           1.13, 1.13, 1.12, 1.12, 1.12, 1.11, 1.11, 1.11, 1.10, 1.10, 1.10,
           1.08, 1.09, 1.08, 1.08]
graph_errx = [0.0126, 0.0125, 0.0130, 0.0144, 0.0164, 0.0193, 0.0234, 0.0284,
              0.0335, 0.0384, 0.0443, 0.0504, 0.0588, 0.0628, 0.0713, 0.0748,
              0.0796, 0.0867, 0.0930, 0.1023, 0.1062, 0.1143, 0.1185, 0.1251,
              0.1296, 0.1345, 0.1368, 0.1405, 0.1500, 0.1585, 0.1696, 0.1884,
              0.2009, 0.2163, 0.2404, 0.2599, 0.2890, 0.3181, 0.3374, 0.3851,
              0.4344, 0.4716, 0.5152, 0.5511, 0.5856, 0.6463, 0.6325, 0.6788,
              0.7586, 0.7251, 0.7403, 0.7848, 0.7571, 0.8102, 0.8083, 0.8217,
              0.8111, 0.8104, 0.8158]
graph_erry = [0.0006, 0.0005, 0.0004, 0.0004, 0.0015, 0.0015, 0.0026, 0.0019,
              0.0026, 0.0019, 0.0021, 0.0019, 0.0021, 0.0019, 0.0020, 0.0018,
              0.0020, 0.0019, 0.0022, 0.0019, 0.0019, 0.0016, 0.0020, 0.0017,
              0.0016, 0.0020, 0.0017, 0.0016, 0.0016, 0.0019, 0.0019, 0.0018,
              0.0018, 0.0016, 0.0017, 0.0021, 0.0021, 0.0021, 0.0021, 0.0023,
              0.0022, 0.0025, 0.0026, 0.0024, 0.0030, 0.0027, 0.0031, 0.0033,
              0.0038, 0.0032, 0.0031, 0.0031, 0.0037, 0.0039, 0.0035, 0.0030,
              0.0030, 0.0030, 0.0027]

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
    axes.errorbar(x, y, xerr=err_x, yerr=err_y, fmt='-', lw=2, color='black')


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

draw_reference_graph(axes, graph_x, graph_y, graph_errx, graph_erry)
plot_fit_func(axes, et, params)

#############
# Setup frames
#############
# frame for canvas
left_frame = Tk.Frame(root)
left_frame.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)

# frame for everything else on the right
right_frame = Tk.Frame(root)
right_frame.pack(side=Tk.RIGHT, expand=False, padx=4, pady=4)

# subframe for file/graph selector
selector_frame = Tk.LabelFrame(master=right_frame, text='Select file/graph', padx=4, pady=4)
selector_frame.pack(fill='both', expand='yes')

# subframe for buttons
button_frame = Tk.Frame(right_frame)
button_frame.pack(ipadx=4, ipady=4, padx=4, pady=4, expand=True, fill=Tk.X)

# A tk.DrawingArea for the main plot
canvas = FigureCanvasTkAgg(fig, master=left_frame)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# The matplotlib toolbar
toolbar = NavigationToolbar2TkAgg(canvas, left_frame)
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

#############
# Add sliders with multiplier entry boxes
##############
sliders = []
multiplier_boxes = []

def set_slider_box_values(slider, multiplier_box, value):
    """Set slider and multiplier box value, since slider only goes -1 to 1."""
    # break up the number such that x = y * 10^n
    # this way we can fit it on a scale of [-1, 1]
    n = ceil(log10(abs(value))) # power of 10
    y = value / pow(10, n)
    copysign(y,value) # mantissa
    slider.set(y)
    multiplier_box.delete(0, Tk.END)
    multiplier_box.insert(0, pow(10, n))


def update_plot(event):
    """Update the main plot whenever a slider or multiplier box is updated."""
    for i, (slider, box) in enumerate(zip(sliders, multiplier_boxes)):
        params[i] = slider.get() * float(box.get())
    # this retains whatever the current axes limits are,
    # incase the user zoomed/transposed
    global y_min, y_max, et_min, et_max
    # global y_max
    # global et_min
    # global et_max
    y_min, y_max = axes.get_ylim()
    et_min, et_max = axes.get_xlim()
    axes.clear()
    draw_reference_graph(axes, graph_x, graph_y, graph_errx, graph_erry)
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
    if i == 0:
        col = "blue"
    elif i in [1, 2]:
        col = "green"
    else:
        col = "orange"

    param_frame = Tk.LabelFrame(master=right_frame, text='p%d' % i, padx=2, fg=col)
    param_frame.pack(fill='both', expand='yes')

    slider = Tk.Scale(master=param_frame, orient=Tk.HORIZONTAL, from_=-1, to=1,
                      resolution=1E-8, length=450, tickinterval=1, command=update_plot) # label='p%d' %i,
    slider.grid(column=0, row=i+1)
    sliders.append(slider)

    label = Tk.Label(master=param_frame, text=" * ")
    label.grid(column=1, row=i+1)

    box = Tk.Entry(master=param_frame, width=9)#, validatecommand=validate_float, validate='key')
    box.register(validate_float)
    box.bind('<Key>', update_plot)
    box.grid(column=2, row=i+1)
    multiplier_boxes.append(box)
    set_slider_box_values(slider, box, p)


######################
# File/graph selector
######################

graph_label = Tk.Label(master=selector_frame, text="Graph:")

graph_entry = Tk.Entry(master=selector_frame, width=20)
graph_entry.insert(0, "l1corr_eta_0_0.348")

fn_label = Tk.Label(master=selector_frame, text="TF1:")
fn_entry = Tk.Entry(master=selector_frame, width=20)
fn_entry.insert(0, "fitfcneta_0_0.348")

root_file = None
def choose_file():
    """Get graph & fit fcn from ROOT file via tkFileDialog, plot them on the canvas"""
    ftypes = [('ROOT files', '*.root'), ('All files', '*')]
    dlg = tkFileDialog.Open(filetypes=ftypes)
    fl = dlg.show()
    if fl != '':
        root_file = ROOT.TFile(fl, "READ")
        gr = root_file.Get(graph_entry.get())
        fn = root_file.Get(fn_entry.get())
        if gr and fn:
            tkMessageBox.showinfo("Got graph & fit", "Got graph %s and function %s" % (graph_entry.get(), fn_entry.get()))
            # store xy points so properly drawn when canvas updated
            global graph_x, graph_errx, graph_y, graph_erry
            graph_x, graph_y = cu.get_xy(gr)
            graph_errx, graph_erry = cu.get_exey(gr)
            new_params = [fn.GetParameter(i) for i in xrange(fn.GetNumberFreeParameters())]
            for slider, box, param in zip(sliders, multiplier_boxes, new_params):
                set_slider_box_values(slider, box, param)
        else:
            if not gr:
                tkMessageBox.showwarning("No graph", "Graph with name %s does not exist" % graph_entry.get())
            if not fn:
                tkMessageBox.showwarning("No function", "Function with name %s does not exist" % graph_entry.get())

open_button = Tk.Button(master=selector_frame, text="Open file", command=choose_file)
graph_label.pack(side=Tk.LEFT, expand=True)
graph_entry.pack(side=Tk.LEFT, expand=True)
fn_label.pack(side=Tk.LEFT, expand=True)
fn_entry.pack(side=Tk.LEFT, expand=True)
open_button.pack(side=Tk.LEFT, expand=True)

##############
# Add buttons
##############

def print_params():
    for i,p in enumerate(params):
        print 'p{0} = {1}'.format(i, p)
    print et
    print pf_func(et, params)


print_button = Tk.Button(master=button_frame, text='Print params', command=print_params)
print_button.pack(side=Tk.LEFT, expand=True)


def reset_params():
    for slider, box, param in zip(sliders, multiplier_boxes, original_params):
        set_slider_box_values(slider, box, param)
    # update_plot(None)


reset_button = Tk.Button(master=button_frame, text='Reset params', command=reset_params)
reset_button.pack(side=Tk.LEFT, expand=True)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

quit_button = Tk.Button(master=button_frame, text='Quit', command=_quit)
quit_button.pack(side=Tk.LEFT, expand=True)

###########
# Fitting
###########
fit_frame = Tk.LabelFrame(right_frame, text='Fitting', padx=2)
fit_frame.pack()

# dummy button to make the Fit button show for some weird reason
button = Tk.Button(fit_frame, text='')
button.pack(side=Tk.RIGHT)

label_min = Tk.Label(fit_frame, text="ET min:")
label_max = Tk.Label(fit_frame, text="ET max:")
label_curr = Tk.Label(fit_frame, text="Current chi2: NA")
label_end = Tk.Label(fit_frame, text="End chi2:")
box_min = Tk.Entry(fit_frame, width=3)
box_min.insert(0, 20)
box_max = Tk.Entry(fit_frame, width=3)
box_max.insert(0, 200)
box_end = Tk.Entry(fit_frame, width=3)
box_end.insert(0, 1.5)
label_min.pack(side=Tk.LEFT)
box_min.pack(side=Tk.LEFT)
label_max.pack(side=Tk.LEFT)
box_max.pack(side=Tk.LEFT)
label_curr.pack(side=Tk.LEFT)
label_end.pack(side=Tk.LEFT)
box_end.pack(side=Tk.LEFT)


def calc_penalty(params, min_x, max_x):
    """Calculates a penalty that is proportional to the 'distance' between
    the graph and the function. Based on chi2, but with a sign to indicate
    on average whether the new function is above or below the graph. """
    pen = 0
    sign = 0
    counter = 0
    for i, (x_pt, y_pt, yerr) in enumerate(zip(graph_x, graph_y, graph_erry)):
        if min_x < x_pt < max_x:
            counter += 1
            y_new = pf_func(x_pt, params)
            pen += pow(y_new - y_pt, 2)/pow(yerr, 2)
            sign += (y_new - y_pt)/abs(y_new - y_pt)
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
            for slider, box, param in zip(sliders, multiplier_boxes, new_params):
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


