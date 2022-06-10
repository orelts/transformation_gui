import numpy as np 
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

def get_points_single(N, size=(5, 5)):
    """
    Args:
        im: 2D grayscale image
        N: number of corresponding points to extract

    Returns:
        p1: 2 x N matrix of points chosen from image
    """

    f = plt.figure(figsize=size)
    plt.grid()
    plt.axhline(0, color='black')
    plt.axvline(0, color='black')
    axlim = 10
    plt.xlim([-axlim, axlim])
    plt.ylim([-axlim, axlim])
    plt.xticks(np.arange(-axlim, axlim, 1))
    plt.yticks(np.arange(-axlim, axlim, 1))

    points = plt.ginput(n=N, timeout=0)
    plt.close()
    # to numpy array
    p = np.array(points).T

    return p

def to_hom(points):
    hom = points.copy()
    hom = np.vstack([hom, np.ones(points.shape[1])])
    return  hom

def to_het(points):
    het = points.copy()
    het = het[:-1,:]
    return het

def apply_transformation(transformation_list, points):
    for idx, trans in enumerate(transformation_list):
        if idx == 0:
            temp = points
        temp = trans @ temp

    return temp

def calc_trans(transformation_list):
    for idx, trans in enumerate(transformation_list):
        if idx == 0:
            temp = trans
            continue
        temp = trans @ temp
   
    return temp

def rad(deg):
    return (deg / 180) * np.pi