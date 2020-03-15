#!/usr/bin/env python3
import random
import sys
import time
import argparse

from math import sqrt

def _opts_get(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.add_argument("--elq", type=int, help="elements quantity")
    parser.add_argument("--dx", type=int, help="cell's size by X")
    parser.add_argument("--dy", type=int, help="cell's size by Y")
    parser.add_argument("--nx", type=int, help="cells quantity by X")
    parser.add_argument("--ny", type=int, help="cells quantity by Y")
    parser.add_argument("--edq", type=int, help="edges quantity")
    parser.add_argument("--edq-max", type=int,
        help="max edges between elements")
    parser.add_argument("--its", type=int, help="iterations quantity")
    parser.add_argument("-f", "--fname", type=str, help="output file")
    parser.add_argument("--with-sort", action="store_true",
        help="sort elements positions")
    parser.add_argument("--ll-show", action="store_true",
        help="show sum of links lengths, if changed")
    parser.add_argument("--with-swap", action="store_true",
        help="swap random elements positions")
    parser.add_argument("--mode", type=str,
        help="hard: randomize all elements positions; " +
            "soft: randomize one random element's position; " +
            "pedantic: soft with storing changed position")
    parser.add_argument("-c", "--comp-diagonal", action="store_true")

    parser.set_defaults(with_sort=False)
    parser.set_defaults(ll_show=False)
    parser.set_defaults(with_swap=False)
    parser.set_defaults(mode="hard")
    parser.set_defaults(comp_diagonal=False)

    opts, unknown = parser.parse_known_args(args)

    if unknown:
        parser.print_help()

        sys.exit(-1)

    return parser, opts

def same(lst):
    for i in lst:
        if lst.count(i) > 1:
            print("same")

def rand(left, right):
    v = int((right + 1 - left) * random.random() + left)

    return v

def swap(lst, p1, p2):
    lst[p1], lst[p2] = lst[p2], lst[p1]

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

def dict_print(dct, step=4, ss=1):
    print("{", end="")

    for i, k in enumerate(sorted(dct.keys())):
        if i != 0 and i % step == 0:
            print()

            for j in range(ss):
                print(" ", end="")

        print(str(k) + ": " + str(dct[k]),
            end=", " if i < len(dct) - 1 else "")

    print("}")

def edges_gen(nmax, edq, wmax):
    edgs = list()
    e = list([0, 0, 0])

    for i in range(edq):
        e[0] = rand(1, nmax)
        e[1] = rand(1, nmax)
        e[2] = rand(1, wmax)

        edgs += [tuple(e)]

    return edgs

def els_place(elq, lx, ly, dx, dy):
    els = list()

    for i in range(elq):
        els += [0]
        #els[i] = (lx - dx - (i + 1) * dx, ly - dy)
        els[i] = (dx * (elq - i) - dx, ly - dy)

    return els

def elp_rand(elsp, bq):
    p = rand(1, bq)

    while elsp.count(p) > 0:
        p = rand(1, bq)

    return p

# scatter elements on field
def els_scat(elq, bq):
    elsp = list()

    for p in range(elq):
        elsp += [elp_rand(elsp, bq)]

    return elsp

def crd_calc(n, dx, dy, nx):
    y = (n - 1) // nx # clean scheme's pos by Y (dy = 1)
    x = n - y * nx - 1 # clean scheme's pos by X (dx = 1)

    x *= dx
    y *= dy

    return (x, y)

def crds_calc(elsp, dx, dy, nx):
    crds = list()

    if isinstance(elsp, int):
        return crd_calc(elsp, dx, dy, nx)

    for i in range(len(elsp)):
        crds += [crd_calc(elsp[i], dx, dy, nx)]

    return crds

# NOTE: expensive
def links_count(edgs):
    links = dict()

    for i in range(len(edgs)):
        n2 = edgs[i][1]

        if n2 in links:
            links[n2] += 1
        else:
            links[n2] = 1

    return links

def link_len_sum(edgs, crds):
    ll = 0.0

    for i in range(len(edgs)):
        n1 = edgs[i][0] - 1
        n2 = edgs[i][1] - 1
        w = edgs[i][2]

        x1 = crds[n1][0]
        y1 = crds[n1][1]
        x2 = crds[n2][0]
        y2 = crds[n2][1]

        ll += sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * w

    return ll

def mut_comp(edgs, elsp, dx, dy, nx, ny, comp_diagonal):
    crds = crds_calc(elsp, dx, dy, nx)
    ll_min = link_len_sum(edgs, crds)
    left = 1
    right = nx * ny + 1

    for i in range(len(elsp)):
        if comp_diagonal:
            left = elsp[i] + 1

        for j in range(left, right):
            if j not in elsp:
                ll = 0.0

                crds[i] = crds_calc(j, dx, dy, nx)

                ll = link_len_sum(edgs, crds)
                if ll < ll_min:
                    elsp[i] = j
                    ll_min = ll
                else:
                    crds[i] = crds_calc(elsp[i], dx, dy, nx)

    return elsp, crds

def mut_swap(edgs, elsp, dx, dy, nx):
    crds = crds_calc(elsp, dx, dy, nx)
    ll = 0.0
    ll_min = link_len_sum(edgs, crds)
    p1 = rand(0, len(elsp) - 1)
    p2 = rand(0, len(elsp) - 1)

    while p2 == p1:
        p2 = rand(0, len(elsp) - 1)

    ll = link_len_sum(edgs, swap(crds, p1, p2))
    if ll < ll_min:
        elsp = swap(elsp, p1, p2)
        crds = swap(crds, p1, p2)

    return elsp, crds

def mut_sort(edgs, elsp, dx, dy, nx):
    elsp_min = elsp[:]
    crds = crds_calc(elsp, dx, dy, nx)
    crds_min = list()
    ll = 0.0
    ll_min = link_len_sum(edgs, crds)

    elsp_min.sort()

    crds_min = crds_calc(elsp_min, dx, dy, nx)

    ll = link_len_sum(edgs, crds_min);
    if ll < ll_min:
        elsp = elsp_min[:]
        crds = crds_min[:]

    return elsp, crds

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
    parser, opts = _opts_get()
    elq = opts.elq
    dx = opts.dx
    dy = opts.dy
    nx = opts.nx
    ny = opts.ny
    edq = opts.edq
    edq_max = opts.edq_max
    its = opts.its
    fname = opts.fname
    with_sort = opts.with_sort
    ll_show = opts.ll_show
    with_swap = opts.with_swap
    mode = opts.mode
    comp_diagonal = opts.comp_diagonal
    cc = 0
    ts = 0 # time start
    tf = 0
    lx = 0
    ly = 0
    bq = 0 # blocks quantity
    els = list()
    edgs = list()
    elsp = list() # elements positions
    elsp_min = list()
    crds_min = list()
    ll = 0.0
    ll_min = float("inf")
    elp_prev = 0 # only for pedantic mode

    if elq is None \
            or dx is None \
            or dy is None \
            or nx is None \
            or ny is None \
            or edq is None \
            or edq_max is None \
            or its is None \
            or fname is None \
            or mode not in ["hard", "soft", "pedantic"]:
        parser.print_help()

        sys.exit(-1)

    cc = edq / (elq * (elq - 1) / 2) * 100
    lx = dx * nx # field's size by X
    ly = dy * ny # field's size by Y
    bq = nx * ny

    els = els_place(elq, lx, ly, dx, dy) # only for file forming
    edgs = edges_gen(elq, edq, edq_max)
    #links = links_count(edgs)
    elsp = els_scat(elq, bq)
    crds = crds_calc(elsp, dx, dy, nx)
    ll = link_len_sum(edgs, crds)

    elp_prev = list([0, elsp[0]])

    print("connectedness coefficient: " + str(round(cc, 3)) + "%" + "\n")

    #print("edgs    : ", end="")
    #list_print(edgs, ss=11)

    #print("links   : ", end="")
    #dict_print(links, step=6, ss=11)

    print("elsp    : ", end="")
    list_print(elsp, step=12, ss=11)

    print("ll      : " + str(round(ll, 3)))

    if ll_show:
        print()

    ts = time.time()

    for i in range(its):
        ll_mut_min = 0.0

        # mutate acc
        while True:
            elsp_min, crds_min = mut_comp(edgs, elsp, dx, dy, nx, ny,
                comp_diagonal)

            if with_swap:
                elsp_min, crds_min = mut_swap(edgs, elsp, dx, dy, nx)

            if with_sort:
                elsp_min, crds_min = mut_sort(edgs, elsp, dx, dy, nx)

            ll_mut_min = link_len_sum(edgs, crds_min)
            if ll_mut_min < ll_min:
                ll_min = ll_mut_min

                if ll_show:
                    print(i + 1, round(ll_min, 3))
            else:
                break

        # generate another acc
        if mode == "hard":
            elsp = els_scat(elq, bq)
        elif mode == "soft":
            elsp[rand(0, elq - 1)] = elp_rand(elsp, bq)
        elif mode == "pedantic":
            p = rand(0, elq - 1)

            if ll_mut_min >= ll_min:
                elsp[elp_prev[0]] = elp_prev[1]

            elsp[p] = elp_rand(elsp, bq)
            elp_prev = [p, elsp[p]]

        crds = crds_calc(elsp, dx, dy, nx)

    tf = time.time() - ts

    print("\n" + "--- generation completed ---")

    print("\n" + "elsp_min: ", end="")
    list_print(elsp_min, step=12, ss=11)

    #print("crds_min: ", end="")
    #list_print(crds_min, ss=11)

    print("ll_min  : " + str(round(ll_min, 3)))

    #print("els     : ", end="")
    #list_print(els, ss=11)

    print("\n" + str(round(ll / ll_min, 3)) + " times optimized")

    print("\n" + "elapsed: " + str(round(tf, 6)) + "s")

    file_form(fname, elsp, crds_min, els)

if __name__ == "__main__":
    main()
