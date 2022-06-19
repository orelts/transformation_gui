import numpy as np 
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

def to_hom(points):
    hom = points.copy()
    hom = np.vstack([hom, np.ones(points.shape[1])])
    return  hom

def to_het(points):
    het = points.copy()
    het = het[:-1,:]
    return het


def computeA(p1, p2):
    """
    Args:
        p1: 2 x N matrix of points
        p2: 2 X N matrix of points

    Returns:
        A matrix derived from point coordinates
    """

    # Work around for a confusion made with homography dest
    tmp = p2
    p2 = p1
    p1 = tmp

    p1 = to_hom(p1)
    p1 = p1.T
    p2 = p2.T

    col1 = np.insert(p1[:], list(range(1, p1.shape[0] + 1)), [0, 0, 0], axis=0)
    col2 = np.insert(p1[:], list(range(0, p1.shape[0])), [0, 0, 0], axis=0)
    col3 = np.multiply(col1 + col2, -np.array([p2.reshape(-1)]).T)

    A = np.concatenate((col1, col2, col3), axis=1)

    return A


def computeH(p1, p2):
    """

    Args:
        p1: 2xN matrix
        p2: 2xN matrix

    Returns:
        H: 3x3 Matrix mapping from p2 to p1
    """

    assert (p1.shape[1] == p2.shape[1])
    assert (p1.shape[0] == 2)

    # Create A
    A = computeA(p1=p1, p2=p2)

    # Solving homegenous linear equations using SVD
    u, s, vh = np.linalg.svd(A)

    h = vh.T[:, -1]

    # Finding H using SVD
    H2to1 = h.reshape(3, 3) / h[-1]

    return H2to1


def get_matches(polygonA, polygonB):

    assert(polygonA.shape == polygonB.shape)

    matchesA = polygonA.copy()
    matchesB = polygonB.copy()

    if polygonA.shape[1] < 4:
        for idx in range(polygonA.shape[1] - 1):
                
            new_pointA = (matchesA[:, idx] + matchesA[:, idx + 1]) / 2
            new_pointB = (matchesB[:, idx] + matchesB[:, idx + 1]) / 2
            new_pointA = np.array([new_pointA]).T
            new_pointB = np.array([new_pointB]).T
            
            matchesA = np.hstack([matchesA, new_pointA])
            matchesB = np.hstack([matchesB, new_pointB])

    return matchesA, matchesB

def compute_transformation(polygonA, polygonB):
    matchesA, matchesB = get_matches(polygonA, polygonB)

    trans = computeH(matchesA, matchesB)

    trans = np.round(trans, decimals=3)

    return trans

def bmatrix(a):
    """Returns a LaTeX bmatrix

    :a: numpy array
    :returns: LaTeX bmatrix as a string
    """
    if len(a.shape) > 2:
        raise ValueError('bmatrix can at most display two dimensions')
    lines = str(a).replace('[', '').replace(']', '').splitlines()
    rv = [r'\begin{bmatrix}']
    rv += ['  ' + ' & '.join(l.split()) + r'\\' for l in lines]
    rv +=  [r'\end{bmatrix}']
    return '\n'.join(rv)
    
    
def string_matrix_mul(transformations, result=None):
    if transformations is None:
        return ""
    transformation_list = transformations.copy()
    transformation_list.reverse()
    row0 = [matrix[0] for matrix in transformation_list]
    row1 = [matrix[1] for matrix in transformation_list]
    row2 = [matrix[2] for matrix in transformation_list]

    result0 = "" if result is None else f"      |{result[0]}|"
    result1 = "" if result is None else f"  =   |{result[1]}|"
    result2 = "" if result is None else f"      |{result[2]}|"

    row0_str = [str(row) for row in row0]
    row0_str = "|" +"|   |".join(row0_str) + "|" + f"{result0}"+  "\n"

    row1_str = [str(row) for row in row1]
    row1_str = "|" +"| x |".join(row1_str) + "|" + f"{result1}"+  "\n"
    
    row2_str = [str(row) for row in row2]
    row2_str = "|" +"|   |".join(row2_str) + "|" + f"{result2}"+  "\n"

    mul_str =  row0_str + row1_str + row2_str
    return mul_str

def get_points_single(N, size=(15, 15)):
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
    plt.title("Select Polygon Corners - Left Click   |   Undo selection - Right Click   |   Finish - Press wheel", fontsize=25)
    plt.xticks(np.arange(-axlim, axlim, 1))
    plt.yticks(np.arange(-axlim, axlim, 1))

    points = plt.ginput(n=N, timeout=0)
    plt.close()
    # to numpy array
    p = np.array(points).T

    return p


def apply_transformation(transformation_list, points):
    points = to_hom(points)
    for idx, trans in enumerate(transformation_list):
        if idx == 0:
            temp = points
        temp = trans @ temp
    points = to_het(temp)

    return points

def calc_trans(transformation_list):
    for idx, trans in enumerate(transformation_list):
        if idx == 0:
            temp = trans
            continue
        temp = trans @ temp
   
    return temp

def rad(deg):
    return (deg / 180) * np.pi