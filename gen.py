#!/usr/bin/env python3
import random
import sys
import time
import argparse

def _error(parser):
    def wrapper(interceptor):
        parser.print_help()

        sys.exit(-1)

    return wrapper

def _args_get(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.error = _error(parser)

    parser.add_argument("elq", type=int, help=argparse.SUPPRESS)
    parser.add_argument("dx", type=int, help=argparse.SUPPRESS)
    parser.add_argument("dy", type=int, help=argparse.SUPPRESS)
    parser.add_argument("nx", type=int, help=argparse.SUPPRESS)
    parser.add_argument("ny", type=int, help=argparse.SUPPRESS)
    parser.add_argument("edq", type=int, help=argparse.SUPPRESS)
    parser.add_argument("edq_max", type=int, help=argparse.SUPPRESS)
    parser.add_argument("its", type=int, help=argparse.SUPPRESS)
    parser.add_argument("fname", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--with-swap", action="store_true",
        help="swap random elements positions")
    parser.add_argument("--with-sort", action="store_true",
        help="sort elements positions")
    parser.add_argument("--ll-show", action="store_true",
        help="show sum of links lengths, if changed")
    parser.add_argument("--mode", type=str,
        help="hard: randomize all elements positions, each iteration; " +
            "soft: randomize one random element's position")
    parser.add_argument("-c", "--comp-diagonal", action="store_true")

    parser.set_defaults(with_swap=False)
    parser.set_defaults(with_sort=False)
    parser.set_defaults(ll_show=False)
    parser.set_defaults(mode="hard")
    parser.set_defaults(comp_diagonal=False)

    args = parser.parse_args(args)

    return parser, args

def same(lst):
    for i in lst:
        if lst.count(i) > 1:
            print("same")

            return

def rand(left, right):
    v = int((right + 1 - left) * random.random() + left)

    return v

def swap(lst, e1, e2):
    lst[e1], lst[e2] = lst[e2], lst[e1]

    return lst

def list_print(lst, step=4, ss=1):
    print("[", end="")

    for i in range(len(lst)):
        if i != 0 and i % step == 0:
            print()

            for j in range(ss):
                print(" ", end="")

        print(str(lst[i]) + (", " if i < len(lst) - 1 else ""), end="")

    print("]")

def edgs_gen(elq, edq, edq_max):
    def edg_gen(elq, edq_max):
        edg = list([0, 0, 0])

        edg[0] = rand(1, elq)
        edg[1] = rand(1, elq)
        edg[2] = rand(1, edq_max)

        return edg

    edgs = list()

    [edgs.append(tuple(edg_gen(elq, edq_max))) for i in range(edq)]

    return edgs

def els_place(elq, dx, dy, lx, ly):
    els = list()

    [els.append((dx * (elq - i) - dx, ly - dy)) for i in range(elq)]

    return els

def elp_rand(elsp, bq):
    p = rand(1, bq)

    while elsp.count(p) > 0:
        p = rand(1, bq)

    return p

# scatter elements on field
def els_scat(elq, bq):
    elsp = list()

    [elsp.append(elp_rand(elsp, bq)) for i in range(elq)]

    return elsp

def crd_to_elp(crd, dx, dy, nx):
    elp = crd[0] / dx + crd[1] / dy * nx + 1

    return int(elp)

def crd_calc(n, dx, dy, nx):
    crd = tuple()
    y = (n - 1) // nx # clean element's pos by Y (dy = 1)
    x = n - y * nx - 1 # clean element's pos by X (dx = 1)

    x *= dx
    y *= dy

    crd = (x, y)

    return crd

def crds_calc(elsp, dx, dy, nx):
    crds = list()

    [crds.append(crd_calc(elsp[i], dx, dy, nx)) for i in range(len(elsp))]

    return crds

def edg_link_len(edg, crds):
    ll = 0.0
    n1 = edg[0] - 1
    n2 = edg[1] - 1
    w = edg[2]

    x1, y1 = crds[n1][0], crds[n1][1]
    x2, y2 = crds[n2][0], crds[n2][1]

    ll = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 * w

    return ll

def edgs_links_len(edgs, crds, conf=None):
    ll = 0.0

    for edg in edgs:
        if conf == None:
            ll += edg_link_len(edg, crds)
        else:
            if edg[0] - 1 == conf or edg[1] - 1 == conf:
                ll += edg_link_len(edg, crds)

    return ll

def mut_comp(edgs, elsp, dx, dy, nx, ny, comp_diagonal):
    crds = crds_calc(elsp, dx, dy, nx)
    left = 1
    right = nx * ny + 1

    for i in range(len(elsp)):
        ll = edgs_links_len(edgs, crds, i)
        deltas = dict()
        j = 0

        if comp_diagonal:
            left = elsp[i] + 1

        for j in range(left, right):
            if j not in elsp:
                delta = 0.0

                crds[i] = crd_calc(j, dx, dy, nx)
                delta = edgs_links_len(edgs, crds, i)

                if delta < ll:
                    deltas[j] = delta

        if deltas:
            j = min(deltas, key=deltas.get)

            elsp[i] = j
            crds[i] = crd_calc(j, dx, dy, nx)

    return elsp

def mut_swap(edgs, elsp, dx, dy, nx):
    crds = crds_calc(elsp, dx, dy, nx)
    ll = 0.0
    delta = 0.0
    p = list([0, 0])

    for i in range(2):
        p[i] = rand(0, len(elsp) - 1)

        while p.count(p[i]) > 1:
            p[i] = rand(0, len(elsp) - 1)

        ll += edgs_links_len(edgs, crds, p[i])

    crds = swap(crds, p[0], p[1])

    for i in range(2):
        delta += edgs_links_len(edgs, crds, p[i])

    if delta < ll:
        elsp = swap(elsp, p[0], p[1])

    return elsp

def mut_sort(edgs, elsp, dx, dy, nx):
    crds = crds_calc(elsp, dx, dy, nx)
    ll = edgs_links_len(edgs, crds)

    crds.sort()

    if edgs_links_len(edgs, crds) < ll:
        elsp.sort()

    return elsp

def file_form(fname, edgs, crds, els):
    f = open(fname, "w")

    f.write("Clear Points" + "\n")

    for i in range(len(edgs)):
        cmd = "Add Point Cartesian " + \
            str(els[i][0]) + ", " + \
            str(els[i][1]) + "\n"

        f.write(cmd)

    for i in range(len(edgs)):
        cmd = "Add Point Cartesian " + \
            str(crds[i][0]) + ", " + \
            str(crds[i][1]) + "\n"

        f.write(cmd)

    f.write("Z Axis Up" + "\n")

    for i in range(len(edgs)):
        f.write("Move To Point " + str(i + 1) + "\n")
        f.write("Z Axis Down" + "\n")
        f.write("Vacuum On" + "\n")
        f.write("Z Axis Up" + "\n")
        f.write("Move To Point " + str(i + 1 + len(edgs)) + "\n")
        f.write("Z Axis Down" + "\n")
        f.write("Vacuum Off" + "\n")
        f.write("Z Axis Up" + "\n")

def main():
    parser, args = _args_get()
    elq = args.elq
    dx = args.dx
    dy = args.dy
    nx = args.nx
    ny = args.ny
    edq = args.edq
    edq_max = args.edq_max
    its = args.its
    fname = args.fname
    with_swap = args.with_swap
    with_sort = args.with_sort
    ll_show = args.ll_show
    mode = args.mode
    comp_diagonal = args.comp_diagonal
    cc = 0
    ts = 0 # time start
    tf = 0
    lx = 0
    ly = 0
    bq = 0 # blocks quantity
    els = list()
    edgs = list()
    elsp = list() # elements positions
    ll_start = 0.0
    ll_min = float("inf")
    times_opt = 0.0
    delta = 0.0
    perc = 0.0

    if mode not in ["hard", "soft"]:
        parser.print_help()

        sys.exit(-1)

    cc = edq / (elq * (elq - 1) / 2) * 100
    lx = dx * nx # field's size by X
    ly = dy * ny # field's size by Y
    bq = nx * ny
    els = els_place(elq, dx, dy, lx, ly) # only for file forming
    edgs = edgs_gen(elq, edq, edq_max)
    elsp = els_scat(elq, bq)
    crds = crds_calc(elsp, dx, dy, nx)
    ll_start = edgs_links_len(edgs, crds)

    print("connectedness coefficient: " + str(round(cc, 3)) + "%" + "\n")

    print("edgs    : ", end="")
    list_print(edgs, ss=11)

    print("elsp    : ", end="")
    list_print(elsp, step=12, ss=11)

    print("ll      : " + str(round(ll_start, 3)))

    if ll_show:
        print()

    ts = time.time()

    for i in range(its):
        # mutate acc
        while True:
            ll = 0.0

            elsp = mut_comp(edgs, elsp, dx, dy, nx, ny,
                comp_diagonal)

            if with_swap:
                elsp = mut_swap(edgs, elsp, dx, dy, nx)

            if with_sort:
                elsp = mut_sort(edgs, elsp, dx, dy, nx)

            crds = crds_calc(elsp, dx, dy, nx)
            ll = edgs_links_len(edgs, crds)
            if ll < ll_min:
                if ll_min < float("inf"):
                    perc = round((ll_min - ll) / ll_min * 100, 2)
                else:
                    perc = round((ll_start - ll) / ll_start * 100, 2)

                ll_min = ll

                if ll_show:
                    print(i + 1, round(ll_min, 3), "(" + str(perc) + "%)")
            else:
                break

        if i == its - 1:
            break

        # generate another acc
        if mode == "hard":
            elsp = els_scat(elq, bq)
        elif mode == "soft":
            elsp[rand(0, elq - 1)] = elp_rand(elsp, bq)

    tf = time.time() - ts

    print()
    print("--- generation completed ---")
    print()

    print("elsp    : ", end="")
    list_print(elsp, step=12, ss=11)

    #print("els     : ", end="")
    #list_print(els, ss=11)

    #print("crds    : ", end="")
    #list_print(crds, ss=11)

    print("ll_min  : " + str(round(ll_min, 3)))

    times_opt = round(ll_start / ll_min, 3)
    delta = ll_start - ll_min
    perc = round(delta / ll_start * 100, 2)

    print()
    print(str(times_opt) + " (" + str(perc) + "%) times optimized")

    print()
    print("elapsed: " + str(round(tf, 6)) + "s")

    file_form(fname, elsp, crds, els)

if __name__ == "__main__":
    main()
