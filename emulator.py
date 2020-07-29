#!/usr/bin/env python3
import random
import sys
import argparse

from interceptor import error
from time import sleep
from tkinter import Tk
from tkinter import Canvas
from tkinter import Label

def _args_get(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.error = error(parser)

    parser.add_argument("elq", type=int, help="elements quantity")
    parser.add_argument("dx", type=int, help="element's size by X")
    parser.add_argument("dy", type=int, help="element's size by Y")
    parser.add_argument("fsx", type=int, help="field size by X")
    parser.add_argument("fsy", type=int, help="field size by Y")
    parser.add_argument("fname", type=str, help="file with TP-ELC commands")
    parser.add_argument("--log-show", action="store_true", help="show log")

    parser.set_defaults(log_show=False)

    args = parser.parse_args(args)

    return parser, args

def file_read(fname):
    cmds = list()

    with open(fname) as f:
        for line in f:
            cmds += [line.split('\n')]

    return cmds

# place schemes
def schemes_place(canvas, n, dx, dy, ly):
    els = list()
    lbls = list()

    for i in range(n):
        els += [0]
        lbls += [0]

        els[i] = canvas.create_rectangle(dx * (n - i) - dx, ly - dy,
            dx * (n - i + 1) - dx, ly, outline="#000", fill="#1c1", width=2)
        lbls[i] = canvas.create_text(dx * (n - i + 0.5) - dx, ly - dy / 2,
            font=("Terminus", 8), text=str(i + 1))

    return els, lbls

# manipulator init
def man_init(canvas, r, dx, dy):
    hand = canvas.create_line(0, 0, dx / 2, dy / 2, width=6, fill="black")
    p = canvas.create_oval([0, 0],[r * 1.5, r * 1.5], fill="yellow")
    v = canvas.create_oval([r / 2, r / 2], [r, r],
        fill="blue")

    return hand, p, v

def man_move(canvas, x, y, hand, p, v, vstate, els, eln, lbls):
    v_crds = canvas.coords(v)
    el_crds = canvas.coords(els[0])

    canvas.coords(hand, 0, 0, v_crds[0] + x, v_crds[1] + y) # move hand
    canvas.move(p, x, y) # move pin
    canvas.move(v, x, y) # move vacuum

    if abs(v_crds[0] - el_crds[0]) <= 1 \
            and abs(v_crds[1] - el_crds[1]) <= 1 \
            and vstate == 1:
        canvas.move(els[0], x, y)
        canvas.move(lbls[eln], x, y)

def grid_create(canvas, lx, ly, dx, dy, w):
    for i in range(0, lx, dx):
        canvas.create_line([(i, 0), (i, ly)], fill="black", width=w,
            tags="grid_line_w")

    for i in range(0, ly, dy):
        canvas.create_line([(0, i), (lx, i)], fill="black", width=w,
            tags="grid_line_h")

    canvas.grid(row=0, column=0)

def cmds_parse(canvas, cmds, num, p, v, vstate, els, eln, p_crds_arr, log):
    cmd = cmds[num][0]
    pflag = False
    p_crds = list([0, 0])

    if cmd == "Clear Points":
        p_crds_arr = list()

        if log:
            print(cmd)
    elif cmd[0:19] == "Add Point Cartesian":
        raw = cmd[19:len(cmd)]
        crds = raw.split(",")
        p_crds_arr += [(float(crds[0]), float(crds[1]))]

        if log:
            print(cmd[0:19], int(crds[0]), int(crds[1]))
    elif cmd == "Z Axis Up":
        canvas.itemconfig(p, fill="yellow")

        if log:
            print(cmd)
    elif cmd == "Z Axis Down":
        canvas.itemconfig(p, fill="red")
        canvas.update()

        if log:
            print(cmd)

        sleep(0.25)
    elif cmd == "Vacuum On":
        canvas.itemconfig(v, fill="black")
        vstate = 1
        els[0] = els[eln]

        if log:
            print(cmd)
    elif cmd == "Vacuum Off":
        canvas.itemconfig(v, fill="blue")
        vstate = 0
        eln += 1

        if log:
            print(cmd)
    elif cmd[0:13] == "Move To Point":
        pnum = int(cmd[14:len(cmd)]) - 1
        p_crds[0] = p_crds_arr[pnum][0]
        p_crds[1] = p_crds_arr[pnum][1]

        pflag = True

        if log:
            print(cmd[0:14], pnum + 1)

    return pflag, els, eln, p_crds, p_crds_arr, vstate

# move element
# NOTE: recursive
def el_move(w, canvas, hand, p, v, vstate, p_crds, p_crds_arr, els, eln,
        lbls):
    crds = canvas.coords(v)
    x = 1.0
    y = 1.0

    if crds[0] < p_crds[0] and crds[1] < p_crds[1]:
        man_move(canvas, x, y, hand, p, v, vstate, els, eln, lbls)
    elif crds[0] > p_crds[0] and crds[1] > p_crds[1]:
        man_move(canvas, -x, -y, hand, p, v, vstate, els, eln, lbls)
    elif crds[0] < p_crds[0]:
        man_move(canvas, x, 0.0, hand, p, v, vstate, els, eln, lbls)
    elif crds[0] > p_crds[0]:
        man_move(canvas, -x, 0.0, hand, p, v, vstate, els, eln, lbls)
    elif crds[1] < p_crds[1]:
        man_move(canvas, 0.0, y, hand, p, v, vstate, els, eln, lbls)
    elif crds[1] > p_crds[1]:
        man_move(canvas, 0.0, -y, hand, p, v, vstate, els, eln, lbls)
    else:
        canvas.itemconfig(v, fill="black")

        return

    sleep(0.001)

    canvas.update()

    w.after(2, el_move(w, canvas, hand, p, v, vstate, p_crds, p_crds_arr,
        els, eln, lbls))

def main():
    parser, args = _args_get()
    elq = args.elq
    dx = args.dx
    dy = args.dy
    fsx = args.fsx
    fsy = args.fsy + 1
    fname = args.fname
    log = args.log_show;
    lx = dx * fsx # field's size by X
    ly = dy * fsy # field's size by Y
    hand = None
    p = None
    pr = 10 # pin's radius
    v = None
    vstate = 0 # vacuum state
    eln = 0 # current element's number
    p_crds_arr = list()
    cmds = file_read(fname)
    cmdn = 0
    w = Tk()
    l = Label(text='0')
    canvas = Canvas(w, background="white", width=lx, height=ly)

    w.title("TP-ELC emulator")

    grid_create(canvas, lx, ly, dx, dy, 2) # create grid
    els, lbls = schemes_place(canvas, elq, dx, dy, ly) # place schemes
    hand, p, v = man_init(canvas, pr, dx, dy) # manipulator init
    canvas.pack()

    canvas.update()
    sleep(2)

    # commands parse
    for i in range(len(cmds)):
        pflag, els, eln, p_crds, p_crds_arr, vstate = cmds_parse(canvas,
            cmds, cmdn, p, v, vstate, els, eln, p_crds_arr, log)
        cmdn += 1

        if pflag == True:
            el_move(w, canvas, hand, p, v, vstate, p_crds, p_crds_arr, els,
                eln, lbls)
            pflag = False

    sleep(5)

    w.destroy()

if __name__ == "__main__":
    main()
