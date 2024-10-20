import numpy as np
from stl import mesh

import pyvista as pv
from pyvista import CellType

import steputils as stp

from matplotlib import pyplot

from mpl_toolkits import mplot3d

from decimal import Decimal as dec

#Section 1 Initial Setup




#print(example_part.areas[0])
#print(example_part.vectors[0])
#print(example_part.vectors[1])

example_part = mesh.Mesh.from_file('PartDesignExample-Body.stl')

#Section 2 Functions

def find_model_extents(model):
    """Determines the overall extents and size of the polyhedron.
    
    The polyhedron should be formatted as a list of faces.

    The faces should be formatted as a list of planar points.

    The points should be formatted as a list of coordinates X, Y, Z.

    Returns a dictionary containing: x_min, x_max, x_size, y_min, y_max, y_size, z_min, z_max, z_size.
    
    """
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    min_z = 0
    max_z = 0    
    #print(example_part.vectors[0])
    for vectors in model:
        for vector in vectors:
            if vector[0] < min_x:
                min_x = vector[0]
            if vector[0] > max_x:
                max_x = vector[0]
            if vector[1] < min_y:
                min_y = vector[1]
            if vector[1] > max_y:
                max_y = vector[1]
            if vector[2] < min_z:
                min_z = vector[2]
            if vector[2] > max_z:
                max_z = vector[2]
    extents = {
        "x_min": min_x,
        "x_max": max_x,
        "x_size": max_x - min_x,
        "y_min": min_y,
        "y_max": max_y,
        "y_size": max_y - min_y,
        "z_min": min_z,
        "z_max": max_z,
        "z_size": max_z - min_z,
    }
    return extents

def find_triangle_centroid(triangle):
    """Finds the centroid of a triangular face. 
    Triangle should be formatted as a list of three points with X, Y, Z coordinates."""
    midpoint1 = find_midpoint([triangle[0],triangle[1]])
    line1 = [midpoint1,triangle[2]]

    midpoint2 = find_midpoint([triangle[0],triangle[2]])
    line2 = [midpoint2,triangle[1]]
    #print(line1,line2)
    centroid = find_lines_intersection(line1,line2)
    return centroid

def find_midpoint(line):
    """Finds the midpoint of a line segment.
    Line should be formatted as a list of two points with X, Y, Z coordinates."""
    midpoint = []
    for i in range(len(line[0])):
        mid = (line[0][i]+line[1][i])/2
        midpoint.append(mid)
    return midpoint

def subtract_point_from_point(point_1,point_2):
    """Subtracts one point from another point, forming a vector from point_1 to point_2

    The points should be formatted as a list of 3 coordinates X, Y, Z. The points must have the same dimension.

    Returns: The function returns a list of 3 magnitudes i, j, k. The magnitudes will be returned in as decimal data types.
    """

    if len(point_1) != len(point_2):
        return "Error, points must be of the same dimension."
    result_vector = []
    for i in range(len(point_1)):
        difference = point_1[i]-point_2[i]
        result_vector.append(difference)
    return result_vector

def find_volume_of_tetrahedron(tetrahedron):
    """Find the volume of a tetrahedron.
    
    Tetrahedron should be formatted as a list of four points.

    Points should be formatted as a list of three coordinates X, Y, Z.

    Returns volume as a numeric value.    
    """
    a = tetrahedron[0]
    b = tetrahedron[1]
    c = tetrahedron[2]
    d = tetrahedron[3]
    difference_ad = subtract_point_from_point(a,d)
    difference_bd = subtract_point_from_point(b,d)
    difference_cd = subtract_point_from_point(c,d)
    #print(tet_vol_matrix)
    volume = 1/6*dot_product_decimal(difference_ad,cross_product_decimal(difference_bd,difference_cd))    
    return np.abs(volume)

def check_if_lines_are_coplanar(line1,line2):
    """Checks if two lines are coplanar.
    
    Lines should be formatted as a list of two points.

    Points should be formatted as a lits of three coordinates X, Y, Z.    
    """
    tolerance = 1E-6
    a = line1[0]
    b = line1[1]
    c = line2[0]
    d = line2[1]
    difference_ad = subtract_point_from_point(a,d)
    difference_bd = subtract_point_from_point(b,d)
    difference_cd = subtract_point_from_point(c,d)
    #print(tet_vol_matrix)
    volume = (1/6)*dot_product_decimal(difference_ad,cross_product_decimal(difference_bd,difference_cd))
    #print(volume)
    
    if np.abs(volume) > tolerance:
        #print(f"Line1: {line1}; Line2: {line2}; Volume: {volume}")
        
        return False
    else:
        return True

def find_triangle_area(triangle):
    """Determines the area of a triangle.
    
    The triangle should be formatted as a list of three points.

    The points should be formatted as a list of coordinates X, Y, Z.  

    Returns the area as a number.  
    """
    tolerance = 1E-6
    line1 = [
        triangle[0],
        triangle[1],
        ]
    line2 = [
        triangle[0],
        triangle[2],
        ]
    line3 = [
        triangle[1],
        triangle[2],
        ]
    line1_length = find_line_length(line1)
    line2_length = find_line_length(line2)
    line3_length = find_line_length(line3)
    semi_perimeter = (line1_length+line2_length+line3_length)/2
    term = semi_perimeter*(semi_perimeter-line1_length)*(semi_perimeter-line2_length)*(semi_perimeter-line3_length)
    if term <0 and term >-tolerance:
        term = 0
    area = np.sqrt(term)
    return area
   
def get_vector_from_line_segment(line):
    """Returns a vector from a line segment with a magnitude equal to the length of the segment.
    
    The line segment should be defined as a list of two points.

    The points should be defined as a list of coordinates X, Y, Z.
    """
    vector = [
            line[1][0] - line[0][0],
            line[1][1] - line[0][1],
            line[1][2] - line[0][2],
        ]
    return vector

def get_magnitude_of_vector(vector):
    """Returns the magnitude of a vector.

    The vector should be defined as a list of three magnitudes i,j,k.
    """
    magnitude = np.sqrt(vector[0]**2 + vector[1]**2+vector[2]**2)
    return magnitude

def check_if_lines_are_colinear(line1, line2):
    """Checks if two line segments are colinear.
    
    Each line segment should be defined as a list of two points.

    Each point should be defined as a list of coordinates X, Y, Z.
    """
    for point in line1:
        three_points = [
            point,
            line2[0],
            line2[1],
        ]
        colinear = are_these_three_points_colinear(three_points)
        #print(f"Three_points: {three_points}, colinear: {colinear}")
        if colinear == False:
            return False
    return True

def vector_times_scalar(vector, scalar):
    """Determines the product of a vector and a scalar.
    
    The vector should be formatted as a list of magnitudes such as i, j, k.

    The scalar should be a number.

    Returns a vector with component magnitudes in the decimal data type.    
    """
    new_vector = []
    for component in vector:
        new_magnitude = scalar*component
        new_vector.append(new_magnitude)
    return new_vector

def add_two_vectors_decimal(vector1, vector2):
    """Adds two vectors together.

    Vectors should be defined as a list of three magnitudes i, j, k.

    Returns a vector sum of the two input vectors with magnitudes i, j, k.
    """
    if len(vector1) != len(vector2):
        return "Error: Vectors must be of the same dimension."
    
    vector_sum = []
    #print(f"Vector2: {vector2}")
    for i in range(len(vector1)):
        sum = vector1[i]+vector2[i]
        vector_sum.append(sum)
    #print(f'Vector Sum: {vector_sum}')
    return vector_sum

def find_lines_intersection(line1, line2):
    """Finds the intersection of two line segments. They must be coplanar. Skew line segments will return an error string.
    Each line input should be a list of two points. Each point should be a list of three coordinates X, Y, Z.
    The function will return False if the intersection is not within both input lines.
    Coordinates should be decimal datatype.
    """
    #Check if the two lines are coplanar but not colinear. 
    are_coplanar = check_if_lines_are_coplanar(line1,line2)
    are_colinear= check_if_lines_are_colinear(line1, line2)
    #print(f"Are coplanar: {are_coplanar}")
    if are_coplanar == False:
        #print(f"Line1 {line1}, Line2 {line2}")
        pass
    #print(f"Are colinear: {are_colinear}")
    if are_coplanar == True and are_colinear == False:
        x1 = line1[0]
        x2 = line1[1]
        x3 = line2[0]
        x4 = line2[1]
        a = subtract_point_from_point(x2,x1)
        b = subtract_point_from_point(x4,x3)
        c = subtract_point_from_point(x3,x1)
        axb = cross_product_decimal(a,b)
        magnitude_axb = np.sqrt(axb[0]**2+axb[1]**2+axb[2]**2)
        if magnitude_axb == 0:
            #print(f"magnitude of cross is zero")
            return False
        intersection = add_two_vectors_decimal(x1,vector_times_scalar(a,(dot_product_decimal(cross_product_decimal(c,b),cross_product_decimal(a,b))/magnitude_axb**2)))
        is_on_line1 = is_this_point_on_this_segment(line1, intersection)
        is_on_line2 = is_this_point_on_this_segment(line2, intersection)
        if is_on_line1 and is_on_line2:
            return intersection
        elif is_on_line1:
            #print(f"Intersection is only on line 1")
            return False
        elif is_on_line2:
            #print(f"Intersection is only on line 2")
            return False
        else:
            #Returns false if the line segments have an intersection point that does not lie on both segments.
            #print(f"Intersection is not on one of the segments.")
            return False
    else:
        if are_coplanar == False:
            return "Error: Lines are skew (not coplanar)."
        else:
            #print(f"Error: Lines are colinear (find_lines_instersection): {line1}, {line2}, {are_colinear}")
            return f"Error: Lines are colinear."

def are_these_three_points_colinear(points):
    """Determines whether 3 points lie along a single line.
    
    The input should be a list of 3 points.

    The points should be a list of 3 coordinates X, Y, Z.

    Will return False for the nodes of a triangle.
    """
    #Find the vectors
    unit_vector_1 = find_unit_vector([
        points[1][0]-points[0][0],
        points[1][1]-points[0][1],
        points[1][2]-points[0][2],
    ])
    unit_vector_2 = find_unit_vector([
        points[2][0]-points[0][0],
        points[2][1]-points[0][1],
        points[2][2]-points[0][2],
    ])    
    minus_unit_vector_2 = [
        -1*magnitude
        for magnitude in unit_vector_2
    ]
    tolerance = 1E-16
    magnitude_1 = get_magnitude_of_vector(unit_vector_1)
    magnitude_2 = get_magnitude_of_vector(unit_vector_2)
    if magnitude_1 == 0 or magnitude_2 == 0:
        return True
    if unit_vector_1[0] == unit_vector_2[0] and unit_vector_1[1] == unit_vector_2[1] and unit_vector_1[2] == unit_vector_2[2]: 
        return True
    if unit_vector_1[0] == minus_unit_vector_2[0] and unit_vector_1[1] == minus_unit_vector_2[1] and unit_vector_1[2] == minus_unit_vector_2[2]:
        return True
    a = unit_vector_1[0] - unit_vector_2[0]
    b = unit_vector_1[1] - unit_vector_2[1]
    c = unit_vector_1[2] - unit_vector_2[2]
    if (unit_vector_1[0] - unit_vector_2[0])**2 < tolerance and (unit_vector_1[1] - unit_vector_2[1])**2 < tolerance and (unit_vector_1[2] - unit_vector_2[2])**2 < tolerance:
        return True
    if (unit_vector_1[0] - minus_unit_vector_2[0])**2 < tolerance and (unit_vector_1[1] - minus_unit_vector_2[1])**2 < tolerance and (unit_vector_1[2] - minus_unit_vector_2[2])**2 < tolerance:
        return True
    return False

def is_this_point_on_this_segment(line_segment, point):
    """Determines if the supplied point is on a line segment. 

    The line segment should be defined as a list of two points with coordinates X, Y, Z.

    The points should be defined as a list of coordinates X, Y, Z.
       
    Will return False if the point is along the line of the segment but not within the segment itself."""

    tolerance = 1E-8

    #First, check if the point is one of the end points.
    if point[0] == line_segment[0][0] and point[1] == line_segment[0][1] and point[2] == line_segment[0][2]:
        return True
    if point[0] == line_segment[1][0] and point[1] == line_segment[1][1] and point[2] == line_segment[1][2]:
        return True
    if np.abs(point[0] - line_segment[0][0]) < tolerance and np.abs(point[1] - line_segment[0][1]) < tolerance and np.abs(point[2] - line_segment[0][2]) < tolerance:
        return True
    if np.abs(point[0] - line_segment[1][0]) < tolerance and np.abs(point[1] - line_segment[1][1]) < tolerance and np.abs(point[2] - line_segment[1][2]) < tolerance:
        return True



    points = [
        line_segment[0],
        line_segment[1],
        point,
    ]
    are_colinear = are_these_three_points_colinear(points)
    x_range = [line_segment[0][0], line_segment[1][0]]
    y_range = [line_segment[0][1], line_segment[1][1]]
    z_range = [line_segment[0][2], line_segment[1][2]]
    #print(f"y_range: {y_range}")
    x_range.sort()
    x_range[0] = x_range[0] - tolerance
    x_range[1] = x_range[1] + tolerance
    y_range.sort()
    y_range[0] = y_range[0] - tolerance
    y_range[1] = y_range[1] + tolerance
    z_range.sort()
    z_range[0] = z_range[0] - tolerance
    z_range[1] = z_range[1] + tolerance
    if are_colinear:
        if point[0]>=x_range[0] and point[0]<=x_range[1] and point[1]>=y_range[0] and point[1]<=y_range[1] and point[2]>=z_range[0] and point[2]<=z_range[1]:
            #print(f"X coord {point[0]} Inside x range: {x_range}")
            #print(f"y coord {point[1]} Inside y range: {y_range}")
            #print(f"z coord {point[2]} Inside z range: {z_range}")
            return True
        #else:
            #print(f"X coord {point[0]} x range: {x_range}")
            #print(f"y coord {point[1]} y range: {y_range}")
            #print(f"z coord {point[2]} z range: {z_range}")            
    return False

def convert_triangle_coords_to_float(triangle32):
    """Takes a traingle with single precision (32 bit) float coordinates and converts it to a triangle with double precision (64 bit) floats coordinates."""
    triangle = []
    for point in triangle32:
        new_point = [
            float(coord)
            for coord in point
        ]
        triangle.append(new_point)    
    return triangle

def remove_duplicate_points(planar_polygon):
    """Removes duplicate points from a planar polygon.
    
    Polygon should be formatted as a list of points.

    Points should be formatted as a list of coordinates X, Y, Z.

    Returns the polygon with duplicate points removed.    
    """
    tolerance = 1E-4
    new_polygon = []
    polygon_1 = [
        point
        for point in planar_polygon
    ]
    polygon_2 = [
        point
        for point in planar_polygon
    ]
    for i in range(len(polygon_1)):
        count = 0
        for j in range(len(polygon_2)):
            if polygon_2[j] != []:
                x_diff = np.abs(polygon_2[j][0]-polygon_1[i][0])
                y_diff = np.abs(polygon_2[j][1]-polygon_1[i][1])
                z_diff = np.abs(polygon_2[j][2]-polygon_1[i][2])
                if  x_diff < tolerance and y_diff < tolerance and z_diff < tolerance and count ==0:
                    new_polygon.append(polygon_2[j])
                    count = count + 1
                    polygon_2[j] = []
                elif x_diff < tolerance and y_diff < tolerance and z_diff < tolerance and count >=1:
                    count = count + 1
                    polygon_2[j] = []

    return new_polygon

def remove_duplcate_points_OLD(planar_polygon):
    """Removes duplicate points from a planar polygon.
    
    Polygon should be formatted as a list of points.

    Points should be formatted as a list of coordinates X, Y, Z.

    Returns the polygon with duplicate points removed.    
    """
    tolerance = 1E-8
    new_polygon = []
    for point in planar_polygon:
        count = 0
        for i in range(len(planar_polygon)):
            if len(planar_polygon[i])>0 and len(point)>0:
                #print(planar_polygon[i])
                #print(point)
                #print("---------")
                x_diff = np.abs(planar_polygon[i][0]-point[0])
                y_diff = np.abs(planar_polygon[i][1]-point[1])
                z_diff = np.abs(planar_polygon[i][2]-point[2])
                if  x_diff < tolerance and y_diff < tolerance and z_diff < tolerance and count ==0 and point!=[]:
                    new_polygon.append(point)
                    count = count + 1
                elif x_diff < tolerance and y_diff < tolerance and z_diff < tolerance and count >=1:
                    count = count + 1
                    planar_polygon[i] = []
                    
        
    return new_polygon

def find_line_length(line):
    """Finds the length of a line. The line should be a list of two points.
    Each point should be a list of three coordinates, X, Y, Z."""
    #print(f"Line length (404): {line}")
    dist_x = line[1][0]-line[0][0]
    dist_y = line[1][1]-line[0][1]
    dist_z = line[1][2]-line[0][2]
    length = np.sqrt(dist_x**2+dist_y**2+dist_z**2)
    #print(length)
    return length

def check_if_polyhedral_cell_is_manifold(cell):
    """Checks if a polyhedral cell is manifold and watertight by verifying that each line segment occurs exactly twice.
    
    Cell should be formatted as a dictionary with faces assembled into a list called 'faces'.

    Faces should be formatted as a dictionary with the points of the face contained in a list called 'face'.

    Points should be formatted as a list of three coordinates X, Y, Z.

    Returns False if any line segment occurs other than two times.

    Returns True if all line segments occure exactly twice.
    """
    tolerance = 1E-6
    for i in range(len(cell['faces'])):
        for j in range(len(cell['faces'][i]['face'])):
            line_1 = [
                cell['faces'][i]['face'][j-1],
                cell['faces'][i]['face'][j],
            ]
            occurences = 0
            for k in range(len(cell['faces'])):
                for l in range(len(cell['faces'][k]['face'])):
                    line_2 = [
                        cell['faces'][k]['face'][l-1],
                        cell['faces'][k]['face'][l],
                    ]
                    if np.abs(line_1[0][0]-line_2[0][0]) <= tolerance and np.abs(line_1[0][1]-line_2[0][1]) <= tolerance and np.abs(line_1[0][2]-line_2[0][2]) <= tolerance and np.abs(line_1[1][0]-line_2[1][0]) <= tolerance and np.abs(line_1[1][1]-line_2[1][1]) <= tolerance and np.abs(line_1[1][2]-line_2[1][2]) <= tolerance:
                        occurences = occurences +1
                    elif np.abs(line_1[1][0]-line_2[0][0]) <= tolerance and np.abs(line_1[1][1]-line_2[0][1]) <= tolerance and np.abs(line_1[1][2]-line_2[0][2]) <= tolerance and np.abs(line_1[0][0]-line_2[1][0]) <= tolerance and np.abs(line_1[0][1]-line_2[1][1]) <= tolerance and np.abs(line_1[0][2]-line_2[1][2]) <= tolerance:
                        occurences = occurences +1
            if occurences != 2:
                print(f"Non-Watertight cell detected: {line_1} occured {occurences} times in cell {cell}")
                return False
    return True                                

def check_if_manifold(faces):
    """Checks if a 3D shape made of triangles is manifold and watertight by verifying that each line shows up exactly twice."""
    #tolerance = 1E-8
    all_lines = []
    for triangle in faces:
        #Each face is a triangle. Extract the three lines of the triangle and append them to the list.
        line_1 = [
            (triangle[0]),
            (triangle[1]),
            ]
        line_2 = [
            (triangle[0]),
            (triangle[2]),
            ]
        line_3 = [
            (triangle[1]),
            (triangle[2]),
            ]
        all_lines.append(line_1)
        all_lines.append(line_2)
        all_lines.append(line_3)

    #Iterate through the lines and check if they each occur exactly twice. If they all pass the test return True.
    for line in all_lines:
        occurences = 0
        for i in range(len(all_lines)):
            if line[0][0] == all_lines[i][0][0] and line[0][1] == all_lines[i][0][1] and line[0][2] == all_lines[i][0][2] and line[1][0] == all_lines[i][1][0] and line[1][1] == all_lines[i][1][1] and line[1][2] == all_lines[i][1][2]:
                occurences = occurences + 1
            elif line[0][0] == all_lines[i][1][0] and line[0][1] == all_lines[i][1][1] and line[0][2] == all_lines[i][1][2] and line[1][0] == all_lines[i][0][0] and line[1][1] == all_lines[i][0][1] and line[1][2] == all_lines[i][0][2]:
                occurences = occurences + 1
        if occurences != 2:
            #print(occurences)
            #print(line)
            return False
    return True

def check_if_polygon_is_coplanar(polygon):
    """Checks if all points in a polygon are coplanar.
    
    Polygon should be formatted as a list of at least three points.

    Points should be formatted as a list of three coordinates X, Y, Z.    
    """
    if len(polygon)<=2:
        return "Error, polygon must contain at least 3 points."
    elif len(polygon)==3:
        #print(f"Coplanar check: This is a triangle {polygon}")
        return True
    for l in range(len(polygon)):
        for k in range(len(polygon)):
            line_1 = [
                polygon[l],
                polygon[k],
            ]
            for i in range(len(polygon)):
                line_2 = [
                    polygon[i-1],
                    polygon[i],
                ]
                is_coplanar = check_if_lines_are_coplanar(line_1, line_2)
                if is_coplanar == False:
                    #print(f"This is not coplanar: {polygon}")
                    return False
    #print(f"This is coplanar: {polygon}")
    return True

def cross_product_decimal(vector1,vector2):
    """Performs a cross product of two vectors. 
    
    Vectors should be formatted as a list of three magnitudes i, j, k.

    Vectors must be 3 dimensional.

    Returns the cross product as a list of three magnitudes i, j, k with each component being a decimal data type.
    """
    if len(vector1) != 3 or len(vector2) != 3:
        return "Error: Vectors must be 3 dimensional."
    a1 = vector1[0]
    a2 = vector1[1]
    a3 = vector1[2]
    b1 = vector2[0]
    b2 = vector2[1]
    b3 = vector2[2]
    A = (a2*b3)-(a3*b2)
    B = (a3*b1)-(a1*b3)
    C = (a1*b2)-(a2*b1)
    cross = [
        A,
        B,
        C,
    ]
    return cross

def dot_product_decimal(vector1, vector2):
    """Performs a dot product of two vectors. 

    Vectors should be formatted as a list of three magnitudes i, j, k.

    Vectors must have the same number of dimensions. They do not have to be 3D.
    
    Returns the value of the dot product as a Decimal data type.  
    """
    if len(vector1) != len(vector2):
        return "Error: vectors must be of the same dimension."
    dot = 0.00000
    for i in range(len(vector1)):
        dot = dot + vector1[i]*vector2[i]
    return dot

def unfold_polygon_points(planar_polygon):
    """Orders the points of a polygon so that an unfolded polygon is formed.
    
    The polygon should be formatted as a list of at least three points.

    The points should be formatted as a list of coordinates X, Y, Z.
    """
    tolerance = 1E-4
    #print(planar_polygon)
    if len(planar_polygon) <=2:
        return "Error: Polygon must contain at least 3 points."
    elif len(planar_polygon) == 3:
        is_colinear = are_these_three_points_colinear(planar_polygon)
        if is_colinear == False:
            return planar_polygon
        else:
            #print(f"Error (unfold_polygon_points): {planar_polygon}")
            return "Error: The three points of this shape are colinear and therefore not a polygon."
    #For 4 or more sided polygon, check if it is coplanar and return an error if not.
    is_coplanar = check_if_polygon_is_coplanar(planar_polygon)
    if is_coplanar == False:
        return "Error, polygon must be planar."
    
    centroid = find_approximate_centroid_of_polygon(planar_polygon)
    #print(centroid)
    line_1 = [
        centroid,
        planar_polygon[0],
    ]
    line_2 = [
        centroid,
        planar_polygon[1]
    ]
    vector_1 = get_vector_from_line_segment(line_1)
    vector_2 = get_vector_from_line_segment(line_2)
    dot_product = dot_product_decimal(vector_1, vector_2)
    length_line_1 = get_magnitude_of_vector(vector_1)
    length_line_2 = get_magnitude_of_vector(vector_2)
    this_cos = float(dot_product)/(float(length_line_1)*float(length_line_2))
    if this_cos > 1 and this_cos < 1+tolerance:
        this_cos = 1
    elif this_cos <-1 and this_cos > -1-tolerance:
        this_cos =-1
    theta_12 = np.arccos(this_cos)
    cross_product_12 = cross_product_decimal(vector_1,vector_2)
    #print(f"cross_product_12: {cross_product_12}")
    unit_normal_12 = find_unit_vector(cross_product_12)
    if unit_normal_12 == [0,0,0]:
        temp_point = planar_polygon[1]
        planar_polygon[1] = planar_polygon[2]
        planar_polygon[2] = temp_point
        line_2 = [
            centroid,
            planar_polygon[1]
        ]
        vector_2 = get_vector_from_line_segment(line_2)
        dot_product = dot_product_decimal(vector_1, vector_2)
        length_line_2 = get_magnitude_of_vector(vector_2)
        theta_12 = np.arccos(float(dot_product)/(float(length_line_1)*float(length_line_2)))
        cross_product_12 = cross_product_decimal(vector_1,vector_2)
        #print(f"cross_product_12: {cross_product_12}")
        unit_normal_12 = find_unit_vector(cross_product_12)
    thetas = [0,theta_12]

    
    temp_polygon = [[planar_polygon[0],0],[planar_polygon[1],theta_12]]
    for i in range(len(planar_polygon)):
        if i >= 2:
            line_3 = [
                centroid,
                planar_polygon[i],
            ]
            #print(f"line_3: {line_3}")
            vector_3 = get_vector_from_line_segment(line_3)
            dot_product = dot_product_decimal(vector_1, vector_3)
            length_line_3 = get_magnitude_of_vector(vector_3)
            if length_line_3 <1E-4 or length_line_1 <1E-4:
                print(f"line_3: {line_3}; face: {planar_polygon}")
            this_cos = float(dot_product)/(float(length_line_1)*float(length_line_3))
            if this_cos > 1 and this_cos < 1+tolerance:
                this_cos = 1
            elif this_cos <-1 and this_cos > -1-tolerance:
                this_cos = -1
            theta = np.arccos(this_cos)
            #print(f"Theta: {theta}")
            #print(f"Vector_1: {vector_1}")
            #print(f"Vector_3: {vector_3}")
            cross_product = cross_product_decimal(vector_1,vector_3)
            #print(f"Cross product: {cross_product}")
            unit_normal = find_unit_vector(cross_product)
            #print(f"unit_normal_12: {unit_normal_12}")
            #print(f"unit_normal: {unit_normal}")
            dot_product_check = ""
            if unit_normal == [0,0,0]:
                dot_product_check = 0
            else:
                dot_product_check = dot_product_decimal(unit_normal_12, unit_normal)
            #print(dot_product_check)
            if dot_product_check < 0:
                theta = 2*np.pi - theta
            thetas.append(theta)
            temp_polygon.append([planar_polygon[i],theta])
    thetas.sort()
    #print(thetas)
    #print(temp_polygon)
    final_polygon = []
    for j in range(len(thetas)):
        for k in range(len(temp_polygon)):
            if thetas[j] == temp_polygon[k][1]:
                temp_polygon[k][1] = ""
                final_polygon.append(temp_polygon[k][0])
    return final_polygon

def find_centroid_of_polygon_2(planar_polygon):
    """Determines the exact centroid of a polygon in 3d coordinates."""
    area_xy = 0
    for i in range(len(planar_polygon)-1):
        term = (1/2)*(planar_polygon[i][0]*planar_polygon[i+1][1]-planar_polygon[i+1][0]*planar_polygon[i][1])
        area_xy = area_xy + term
    c_x= 0
    for i in range(len(planar_polygon)-1):
        term = (1/(6*area_xy))*(planar_polygon[i][0]+planar_polygon[i+1][0])*(planar_polygon[i][0]*planar_polygon[i+1][1]-planar_polygon[i+1][0]*planar_polygon[i][1])
        c_x = c_x + term

    c_y= 0
    for i in range(len(planar_polygon)-1):
        term = (1/(6*area_xy))*(planar_polygon[i][1]+planar_polygon[i+1][1])*(planar_polygon[i][0]*planar_polygon[i+1][1]-planar_polygon[i+1][0]*planar_polygon[i][1])
        c_y = c_y + term

    area_xz = 0
    for i in range(len(planar_polygon)-1):
        term = (1/2)*(planar_polygon[i][0]*planar_polygon[i+1][2]-planar_polygon[i+1][0]*planar_polygon[i][2])    
        area_xz = area_xz + term
    
    c_z= 0
    for i in range(len(planar_polygon)-1):
        term = (1/(6*area_xz))*(planar_polygon[i][2]+planar_polygon[i+1][2])*(planar_polygon[i][0]*planar_polygon[i+1][2]-planar_polygon[i+1][0]*planar_polygon[i][2])
        c_z = c_z + term
    
    return [c_x,c_y,c_z]


def find_centroid_of_polygon(planar_polygon):
    """Finds an exact centroid for a planar polygon."""
    triangles = convert_polyhedron_to_approximate_triangular_polyhedron([planar_polygon])
    Cx = 0
    Cy = 0
    Cz = 0
    total_area = 0
    for triangle in triangles:
        centroid = find_triangle_centroid(triangle)
        area = find_triangle_area(triangle)
        #if len(centroid) >5:
        #if centroid == False or centroid == True:
            #print(f"centroid: {centroid}")
            #print(f"area: {area}; {type(area)}")
            #print(triangle)
            #print(planar_polygon)
        Cx = Cx + centroid[0]*area
        Cy = Cy + centroid[1]*area
        Cz = Cz + centroid[2]*area
        total_area = total_area + area
    Cx = Cx / total_area
    Cy = Cy / total_area
    Cz = Cz / total_area

    return [Cx,Cy,Cz]


def find_approximate_centroid_of_polygon(planar_polygon):
    """Determines an approximate center for a polygon which can be used for other checks.
    
    Polygon should be checked to be planar and contain at least three points prior to running this function. Checks are not done.

    Polygon should be formatted as a list of at least three points.

    Points should be formatted as a list of coordinates X, Y, Z.    

    Returns a list of coordinates X, Y, Z.
    """
    #Find the center of the polygon by averaging the points and projecting into the plane of the polygon.
    x_tot = 0
    y_tot = 0
    z_tot = 0
    #if planar_polygon[0] == "E":
    #    print(planar_polygon)
    tolerance = 1E-6
    for point in planar_polygon:
        
        x_tot = x_tot + point[0]
        y_tot = y_tot + point[1]
        z_tot = z_tot + point[2]
    average_point = [
        x_tot/len(planar_polygon),
        y_tot/len(planar_polygon),
        z_tot/len(planar_polygon),
    ]
    #print(average_point)
    #print(check_if_point_inside_polygon(planar_polygon,average_point))
    test_triangle = []
    for i in range(len(planar_polygon)):
        triangle = [planar_polygon[i-2],planar_polygon[i-1],planar_polygon[i]]
        is_colinear = are_these_three_points_colinear(triangle)
        if is_colinear == False:
            #print(is_colinear)
            test_triangle = [
                point
                for point in triangle
            ]
            #print(test_triangle)
    #print(f"test_triangle: {test_triangle}")
    plane_equation = find_equation_of_plane(test_triangle)
    #print(plane_equation)
    if np.abs(plane_equation[0][0]) >= tolerance:
        x_coord = (plane_equation[1] - plane_equation[0][1]*average_point[1] - plane_equation[0][2]*average_point[2])/plane_equation[0][0]
        average_point[0] = x_coord
    elif np.abs(plane_equation[0][1]) >= tolerance:
        y_coord = (plane_equation[1] - plane_equation[0][0]*average_point[0] - plane_equation[0][2]*average_point[2])/plane_equation[0][1]
        average_point[1] = y_coord
    elif np.abs(plane_equation[0][2]) >= tolerance:
        z_coord = (plane_equation[1] - plane_equation[0][0]*average_point[0] - plane_equation[0][1]*average_point[1])/plane_equation[0][2]
        average_point[2] = z_coord
    return average_point

def reverse_polygon_normal(planar_polygon):
    """Reverses the normal of a polygon by reversing the order of its nodes.
    
    Polygon should be formatted as a list of points.

    Points should be formatted as a list of coordinates X, Y, Z.
    
    Returns the same polygon with the order of the points reversed.
    """
    new_polygon = []
    for i in range(len(planar_polygon)):
        point = planar_polygon[len(planar_polygon)-1-i]
        new_polygon.append(point)
    return new_polygon

def check_if_point_inside_polygon(planar_polygon,point):
    """Checks if all points in the polygon are coplanar then if the point is coplanar with the polygon. If it is, runs the boundary crossing test to determine if the point is inside the polygon.
    
    The polygon should be formatted as a list of at least three points with X, Y, Z coordinates.
    """
    if len(planar_polygon) <=2:
        return "Error, polygon must contain at least 3 points."
    #Check if the point lies on one of the lines and return True if so.
    for j in range(len(planar_polygon)):
        line = [
            planar_polygon[j-1],
            planar_polygon[j],
        ]
        on_line = is_this_point_on_this_segment(line,point)
        if on_line:
            #print(f"Point is on segment.")
            return True
    line_1 = [
        planar_polygon[0],
        planar_polygon[1]
    ]
    for i in range(len(planar_polygon)):
        #Verify that the polygon is planar by checking all the points.
        if i >=2:
            line_2 = [
                planar_polygon[1],
                planar_polygon[i],
            ]
            is_coplanar = check_if_lines_are_coplanar(line_1,line_2)
            if is_coplanar == False:
                #print(f"Error: Polygon is not planar.")
                return False
    #Verify that the point is coplanar with the polygon.
    line_2 = [
        planar_polygon[1],
        point,
    ]
    is_coplanar = check_if_lines_are_coplanar(line_1,line_2)
    if is_coplanar == False:
        #print(f"Error: Point is not coplanar with polygon.")
        return False
    else: 
        #The point is verified to be coplanar with the planar polygon.
        #Derive the equation of the plane from the polygon.
        this_triangle = [
            planar_polygon[0],
            planar_polygon[1],
            planar_polygon[2],
        ]
        plane_equation = find_equation_of_plane(this_triangle)

        #The equation of the plane is u1*x+u2*y+u3*z = constant where u# is the component of the unit vector.
        #Apply the crossing test to determine if the point is inside the polygon.
        centroid = find_approximate_centroid_of_polygon(planar_polygon)
        distance_to_centroid = find_line_length([point,centroid])
        perimeter = 0
        for j in range(len(planar_polygon)):
            this_length = find_line_length([planar_polygon[j-1],planar_polygon[j]])
            perimeter = perimeter + this_length
        magnitude = distance_to_centroid + perimeter #This magnitude will be used to ensure the test line can cross the entire polygon.
        #print(plane_equation)
        random_vector = vector_times_scalar(generate_random_vector_in_plane(plane_equation),magnitude)
        #print(get_magnitude_of_vector(random_vector))
        #print(random_vector)
        far_point = add_two_vectors_decimal(point,random_vector)
        test_line = [
            point,
            far_point,
        ]
        #print(f"test_line: {test_line}")
        crossings = 0
        for l in range(len(planar_polygon)):
            line_5 = [
                planar_polygon[l-1],
                planar_polygon[l]
            ]
            #print(f"line_5: {line_5}")
            intersection = find_lines_intersection(line_5,test_line)
            #print(f"intersection: {intersection}")
            #if intersection != 'Error: Vectors must be of the same dimension.' and intersection != 'Error: Lines are skew (not coplanar).' and intersection != False and intersection != "Error: Lines are skew (not coplanar)." and intersection != "Error: Lines are colinear.":
            if type(intersection) == list:
                crossings = crossings +1
            else:
                pass
                #print(f"intersection: {intersection}")
        #print(f"Crossings: {crossings}")
        if crossings == 0 or crossings % 2 == 0:
            return False
        else:
            #print(f"crossings: {crossings}; test line: {test_line}")
            return True

def check_if_point_is_inside_polyhedron(polyhedron,point):
    """Checks if a point is contained inside a watertight polyhedron.
    
    Polyhedron should be formatted as a list of polygons.

    Polygons should be formatted as a list of points.

    Points should be formatted as a list of coordinates X, Y, Z.

    Returns True if the point is inside the polyhedron. Returns False if it is outside the polyhedron.
    """
    #Find the distance from the point to each point on the polygon and pick the largest distance
    length = 0
    for polygon in polyhedron:
        for polygon_point in polygon:
            magnitude = get_magnitude_of_vector(get_vector_from_line_segment([point,polygon_point]))
            if magnitude > length:
                length = magnitude
    length = length*4
    #print(f"length (739): {length}")
    
    #check if the point lies on any of the faces and return True if so.    
    for face in polyhedron:
        on_face = check_if_point_inside_polygon(face, point)
        if on_face:
            #print("Point lies on face")
            return True
    
    #Generate a random line segment long enough to pass through the polyhedron
    generate_vector = [np.random.random()-0.5, np.random.random()-0.5, np.random.random()-0.5]
    #print(f"generate vector: {generate_vector}")
    random_vector = scale_vector_to_magnitude(generate_vector,length)
    new_point = add_two_vectors_decimal(point,random_vector)
    line_segment = [
        point,
        new_point,
    ]
    #print(f"Length: {find_line_length(line_segment)}")
    
    #Check if the random vector directly intersects one of the lines of the polyhedron and start over if so.
    
    for j in range(len(polyhedron)):
        for k in range(len(polyhedron[j])):
            this_line = [
                polyhedron[j][k-1],
                polyhedron[j][k],
            ]
            intersects_edge = find_lines_intersection(line_segment, this_line)
            if type(intersects_edge) == list:
                point_on_edge = is_this_point_on_this_segment(this_line, point)
                if point_on_edge:
                    print(f'Point lies on edge.')
                    return True
                else:
                    return check_if_point_is_inside_polyhedron(polyhedron,point)
    
    
    
    #Check how many times the line segment crosses the faces. Odd number = inside. Even number = Outside
    crossings = 0
    #polygon_messages = []
    for i in range(len(polyhedron)):
        polygon2 = polyhedron[i]
        #print(f"Polygon[0:3]: {polygon[0:3]}")
        #print(f"line_segment: {line_segment}")
        intersection = find_intersection_of_plane_and_line_segment(polygon2[0:3],line_segment)
        if type(intersection) == type([]):
            in_polygon = check_if_point_inside_polygon(polygon2,intersection)
            if in_polygon == True:
                #polygon_messages.append(f"Polygon: {polygon2}; intersection: {intersection}")
                crossings = crossings +1
    #print(f"crossings: {crossings}")
    if crossings == 0 or crossings % 2 == 0:
        return False
    else:
        #print(polygon_messages)
        #print("--------------------")
        return True    

def scale_vector_to_magnitude(vector,magnitude):
    """Scales a vector so that it's magnitude is the value of the magnitude parameter.
    
    The vector should be formatted as a list of three magnitudes i, j, k.

    The magnitude should be formatted as a number.

    Returns a vector with a magntiude matching the input parameter as a list of three magnitudes i, j, k.    
    """
 
    original_magnitude = get_magnitude_of_vector(vector)
    if original_magnitude == 0:
        #print(f"Vector has zero magnitude: {vector}")
        return vector
    ratio = magnitude / original_magnitude
    new_vector = vector_times_scalar(vector,ratio)
    return new_vector

def generate_random_point_in_plane(plane_equation):
    """Generates a random point in a plane."""
    point_in_plane = []
    count = 0
    for i in range(len(plane_equation[0])):
        if plane_equation[0][i] ==0:
            random_coord = np.random.random()-0.5
            point_in_plane.append(random_coord)
        else:
            count = count + 1
            random_coord = 'TBD'
            point_in_plane.append(random_coord)   
    for j in range(len(plane_equation[0])):
        if point_in_plane[j] == 'TBD' and count > 1:
            random_coord = np.random.random()-0.5
            point_in_plane[j]=random_coord 
            count = count - 1
    last_coord = plane_equation[1]  
    for k in range(len(point_in_plane)):
        if point_in_plane[k] != 'TBD':
            last_coord = last_coord - point_in_plane[k]*plane_equation[0][k]
    for l in range(len(point_in_plane)):
        if point_in_plane[l] == 'TBD':
            last_coord = last_coord / plane_equation[0][l]
            point_in_plane[l] = last_coord
    #print(f"Point: {point_in_plane}")
    #print(f"Plane Equation: {plane_equation}")
    return point_in_plane
    
def generate_random_vector_in_plane(plane_equation):
    """Generates a random vector in a plane."""
    point_1 = generate_random_point_in_plane(plane_equation)
    point_2 = generate_random_point_in_plane(plane_equation)
    line = [
        point_1,
        point_2,
    ]
    #print(f"Line: {line}")
    vector = get_vector_from_line_segment(line)
    #print(f"Random Vector in Plane: {vector}")
    #print(f"Plane equation: {plane_equation}")
    magnitude = 1.000
    return scale_vector_to_magnitude(vector,magnitude)

def generate_random_vector_in_plane_2(plane_equation):
    """Generates a random vector in a plane."""
    #Generate a random unit vector in the plane.
    new_vector = []
    count = 0
    for component in plane_equation[0]:
        if component == 0:
            new_magnitude = np.random.random()-0.5
            new_vector.append(new_magnitude)
        else:
            count = count +1
            new_magnitude = "TBD"
            new_vector.append(new_magnitude)
    for i in range(count-1):
        new_magnitude = np.random.random()-0.5
        for j in range(len(new_vector)):
            if new_vector[j] == "TBD":
                new_vector[j] = new_magnitude
                break
    last_magnitude = 0
    solve_index = ""
    for k in range(len(new_vector)):
        if new_vector[k] != "TBD":
            last_magnitude = last_magnitude - new_vector[k]*plane_equation[0][k]
        else:
            solve_index = k
    last_magnitude = last_magnitude / plane_equation[0][solve_index]
    new_vector[solve_index] = last_magnitude
    new_vector = find_unit_vector(new_vector)
    return new_vector

def project_point_onto_plane(plane_equation,point):
    """Finds the closes point on a plane to the input point.
    
    The plane equation should be formatted as a list of a normal vector and a constant.

    The normal vector should be formatted as a list of three magnitudes i, j, k.

    The point should be formatted as a list of three coordinates X, Y, Z.    
    """
    constant_2 = plane_equation[0][0]*point[0]+plane_equation[0][1]*point[1]+plane_equation[0][2]*point[2]
    distance = np.abs(plane_equation[1]-constant_2)/np.sqrt(plane_equation[0][0]**2+plane_equation[0][1]**2+plane_equation[0][2]**2)
    vector = scale_vector_to_magnitude(plane_equation[0],distance)
    projected_point = add_two_vectors_decimal(vector,point)
    polygon = [
        generate_random_point_in_plane(plane_equation),
        generate_random_point_in_plane(plane_equation),
        generate_random_point_in_plane(plane_equation),
        projected_point,
    ]    
    #print(polygon)
    is_coplanar = check_if_polygon_is_coplanar(polygon)
    #print(is_coplanar)
    if is_coplanar == False:
        projected_point = add_two_vectors_decimal(point,vector_times_scalar(vector,-1))
    return projected_point


def check_if_polygon_is_colinear(polygon):
    """Checks if the points of a polygon are all colinear."""
    for i in range(len(polygon)):
        points = [
            polygon[i-2],
            polygon[i-1],
            polygon[i],
        ]
        is_colinear = are_these_three_points_colinear(points)
        if is_colinear == False:
            return False
    return True


def find_polygon_area(planar_polygon):
    """Calculates the area of a polygon from the coordinate points. The polygon must be planar.
    
    The polygon should be formatted as a list of at least three points.

    The points should be formatted as a list of three coordinates X, Y, Z.

    Returns a numeric area.
    """
    is_folded = check_if_polygon_is_folded(planar_polygon)
    if is_folded == True:
        return "Error: Polygon is folded. Use the unfolding algorythm to correct."
    


    line_1 = [
        planar_polygon[0],
        planar_polygon[1]
    ]
    is_coplanar = True
    for i in range(len(planar_polygon)):
        #Verify that the polygon is planar by checking all the points.
        if i >=2:
            line_2 = [
                planar_polygon[1],
                planar_polygon[i],
            ]
            this_point_is_coplanar = check_if_lines_are_coplanar(line_1,line_2)
            if this_point_is_coplanar == False:
                is_coplanar = False
    if is_coplanar == False:
        return "Error: Points are not coplanar."
    else:
        centroid = find_approximate_centroid_of_polygon(planar_polygon)
        area = 0
        for i in range(len(planar_polygon)-1):
            triangle = [
                centroid,
                planar_polygon[i],
                planar_polygon[i+1]
            ]
            this_area = find_triangle_area(triangle)
            area = area + this_area
        last_triangle = [
            centroid,
            planar_polygon[0],
            planar_polygon[-1]
        ]
        last_area = find_triangle_area(last_triangle)
        area = area + last_area
        return area
 
def find_equation_of_plane(triangle):
    """Determines the equation of a plane from a triangle.
    
    The triangle should be formatted as a list of three points.

    The points should be formatted as a list of three coordinates X, Y, Z.

    Returns a list containing the unit normal in index 0 and the constant in index 1.
    """
    tolerance = 1E-8
    vector1 = [
        triangle[1][0] - triangle[0][0],
        triangle[1][1] - triangle[0][1],
        triangle[1][2] - triangle[0][2],
    ]
    vector2 = [
        triangle[2][0] - triangle[0][0],
        triangle[2][1] - triangle[0][1],
        triangle[2][2] - triangle[0][2],
    ]
    normal_vector = np.cross(vector1,vector2)
    unit_vector = find_unit_vector(normal_vector)
    if np.abs(unit_vector[0]) < tolerance:
        unit_vector[0] = 0
    if np.abs(unit_vector[1]) < tolerance:
        unit_vector[1] = 0
    if np.abs(unit_vector[2]) < tolerance:
        unit_vector[2] = 0
    #print(f"Unit vector normal: {unit_vector}")
    constant = unit_vector[0]*triangle[0][0]+unit_vector[1]*triangle[0][1]+unit_vector[2]*triangle[0][2]
    #print(f"Constant: {constant}")
    #The equation of the plane is u1*x+u2*y+u3*z = constant where u# is the component of the unit vector.
    result = [
        unit_vector,
        constant,
    ]
    return result

def check_if_polygon_is_folded(planar_polygon):
    """Checks if the polygon is folded based on the order of the points. A folded polygon will return True. An unfolded polygon will return False.
    
    The polygon should be formatted as a list of points.

    The points should be formatted as a list of coordinates X, Y, Z.
    """
    #First check if the polygon folds back to an existing point and return True if it does.
    for point in planar_polygon:
        num_instances = 0
        for k in range(len(planar_polygon)):
            if point[0] == planar_polygon[k][0] and point[1] == planar_polygon[k][1] and point[2] == planar_polygon[k][2]:
                num_instances = num_instances + 1
        if num_instances > 2:
            #print(f"Too many instances of {point}")
            return True  
    #Check if the each line of the polygon intersects another line somewhere other than it's endpoints.  
    lines = []
    for i in range(len(planar_polygon)-1):
        line = [
            planar_polygon[i],
            planar_polygon[i+1],
        ]
        lines.append(line)
    last_line = [
        planar_polygon[len(planar_polygon)-1],
        planar_polygon[0]
    ]
    lines.append(last_line)
    for i in range(len(lines)):
        intersections = 0
        for j in range(len(lines)):
            if j != i:
                intersection = find_lines_intersection(lines[i],lines[j])
                if intersection != False and intersection != "Error: Lines are colinear." and intersection != "Error: Lines are skew (not coplanar).":
                    intersections = intersections + 1
                #What if the lines are colinear?
                #If either point on one line is contained in a colinear line and it is not the end point, that's a problem.
                    #print(f"Intersections: {intersections}")
                elif intersection == "Error: Lines are colinear.":
                    #print(f"Colinear lines: {lines[i]}, {lines[j]}")
                    for point_2 in lines[i]:
                        is_on_segment = is_this_point_on_this_segment(lines[j],point_2)
                        if is_on_segment:
                            #If the point is on the segment but it is not one of the end points, return true.
                            endpoint = False
                            for point_3 in lines[j]:
                                if point_2[0] == point_3[0] and point_2[1] == point_3[1] and point_2[2] == point_3[2]:
                                    endpoint = True
                            if endpoint == False:
                                return True

        if intersections > 2:
            #print(f"Too many intersections: {intersections}")
            return True
    return False

        #find_lines_intersection(lines[i],lines[i+1])

def convert_coords_to_decimal(list_of_coords):
    """Converts a set of float32 points to decimal points.

    Input should be formatted as a list of points.

    Points should be formatted as a list of coordinates X, Y, Z.    
    """
    new_list_float = []
    for point in list_of_coords:
        new_point = [
            f"{coord}"
            for coord in point
        ]
        new_list_float.append(new_point)  
    new_list_dec = []  
    for point in new_list_float:
        new_point = [
            coord
            for coord in point
        ]
        new_list_dec.append(new_point)  
    return new_list_dec                

def determine_extents_of_polygon(polygon):
        """Determines the extents of a 3D polygon and returns a dictionary with the values.

        Warning: Does not check if the points are coplanar.

        The polygon should be formatted as a list of points.

        The points should be formatted as a list of coordinates X, Y, Z.
        """
        x_min = polygon[0][0]
        x_max = polygon[0][0]
        y_min = polygon[0][1]
        y_max = polygon[0][1]
        z_min = polygon[0][2]
        z_max = polygon[0][3]    
        for point in polygon:
            if point[0] < x_min:
                x_min = point[0]
            if point[0] > x_max:
                x_max = point[0]
            if point[1] < y_min:
                y_min = point[1]
            if point[1] < y_max:
                y_max = point[1]
            if point[2] < z_min:
                z_min = point[2]
            if point[2] < z_min:
                z_max = point[2]     
        results = {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "z_min": z_min,
            "z_max": z_max,
        }     
        return results  

def find_unit_vector(vector):
    """Determines the unit vector in the same direction as the input vector. 
    
    The input vector should be a list of 3 magnitudes i, j, k.

    Returns a unit vector with magnitude 1 in the same direction as the input vector.
    """
    #print(f"SQ ROOT OF: {vector[0]}^2+{vector[1]}^2+{vector[2]}^2")
    magnitude = np.abs(np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2))
    if magnitude > 0.0:
        unit_vector = [
            vector[0]/magnitude,
            vector[1]/magnitude,
            vector[2]/magnitude,
        ]
        return unit_vector
    else: 
        return [0,0,0]

def find_intersection_of_plane_and_line_segment(triangle,line_segment):
    """Finds the intersection of a plane and a line segment.
    
    The plane should be formatted as a list containing three points on the plane.

    The line segment should be formatted as a list of two points.

    The points should be formatted as a list of three coordinates X, Y, Z.

    Returns the intersection point as a list of three coordinates X, Y, Z.  

    Will return False if the line segment does not intersect the plane.  
    """
    tolerance = 1E-10
    plane_equation = find_equation_of_plane(triangle)
    #print(plane_equation)
    line_unit_vector = find_unit_vector(get_vector_from_line_segment(line_segment))
    #print(line_unit_vector)

    if dot_product_decimal(line_unit_vector,plane_equation[0]) > tolerance:
        d = dot_product_decimal([triangle[0][0]-line_segment[0][0],triangle[0][1]-line_segment[0][1],triangle[0][2]-line_segment[0][2]],plane_equation[0])/dot_product_decimal(line_unit_vector,plane_equation[0])
        #print(d)
        intersection = add_two_vectors_decimal(line_segment[0],vector_times_scalar(line_unit_vector,d))
        intersection_on_line = is_this_point_on_this_segment(line_segment,intersection)
        if intersection_on_line:
            return intersection
        else:
            return False
    else:
        return False


def convert_polyhedron_to_approximate_triangular_polyhedron(polyhedron):
    """Converts all faces of a convex polyhedron into triangles.

    The polyhedron should be formatted as a list of polygons.

    The polygons should be formatted as a list of points.

    The points should be formatted as a list of coordinates X, Y, Z. 

    Returns a polyhedron as list of triangles.    
    """

    new_polyhedron = []
    for polygon in polyhedron:
        centroid = find_approximate_centroid_of_polygon(polygon)
        #print(f"centroid: {centroid}")
        if len(polygon) > 3:
            
            for i in range(len(polygon)):
                triangle = [
                    polygon[i-1],
                    polygon[i],
                    centroid,
                ]
                new_polyhedron.append(triangle)
        else:
            new_polyhedron.append(polygon)
    return new_polyhedron

def convert_polyhedron_to_triangular_polyhedron(polyhedron):
    """Converts all faces of a convex polyhedron into triangles.

    The polyhedron should be formatted as a list of polygons.

    The polygons should be formatted as a list of points.

    The points should be formatted as a list of coordinates X, Y, Z. 

    Returns a polyhedron as list of triangles.    
    """

    new_polyhedron = []
    for polygon in polyhedron:
        if len(polygon) > 3:
            centroid = find_centroid_of_polygon(polygon)
            for i in range(len(polygon)):
                triangle = [
                    polygon[i-1],
                    polygon[i],
                    centroid,
                ]
                new_polyhedron.append(triangle)
        else:
            new_polyhedron.append(polygon)
    return new_polyhedron

def find_centroid_of_polyhedron(polyhedron):
    """Finds the geometric centroid of a polyhedron.
    
    The polyhedron should be formatted as a list of polygons.

    The polygons should be formatted as a list of points.

    The points should be formatted as a list of coordinates X, Y, Z.    

    Returns the centroid as a list of coordinates X, Y, Z.
    """
    #print(polyhedron)
    triangularize = convert_polyhedron_to_triangular_polyhedron(polyhedron)
    triangular_polyhedron = make_faces_inward_facing(triangularize)
    volume = find_volume_of_polyhedron(triangular_polyhedron)
    #print(triangular_polyhedron)
    #triangular_polyhedron = triangular_polyhedron[0:1]
    x_bar = 0
    y_bar = 0
    z_bar = 0
    unit_vector_x = [1,0,0]
    unit_vector_y = [0,1,0]
    unit_vector_z = [0,0,1]
    for triangle in triangular_polyhedron: 
        a = triangle[0]
        b = triangle[1]
        c = triangle[2]
        minus_a = vector_times_scalar(a,-1)
        minus_b = vector_times_scalar(b,-1)
        minus_c = vector_times_scalar(c,-1)
        normal = cross_product_decimal(add_two_vectors_decimal(b,minus_a),add_two_vectors_decimal(c,minus_a))
        
        unit_normal = find_unit_vector(normal)
        supplemental_term_x = dot_product_decimal(add_two_vectors_decimal(a,b),unit_vector_x)**2+dot_product_decimal(add_two_vectors_decimal(b,c),unit_vector_x)**2+dot_product_decimal(add_two_vectors_decimal(c,a),unit_vector_x)**2
        supplemental_term_y = dot_product_decimal(add_two_vectors_decimal(a,b),unit_vector_y)**2+dot_product_decimal(add_two_vectors_decimal(b,c),unit_vector_y)**2+dot_product_decimal(add_two_vectors_decimal(c,a),unit_vector_y)**2
        supplemental_term_z = dot_product_decimal(add_two_vectors_decimal(a,b),unit_vector_z)**2+dot_product_decimal(add_two_vectors_decimal(b,c),unit_vector_z)**2+dot_product_decimal(add_two_vectors_decimal(c,a),unit_vector_z)**2

        x_term = (dot_product_decimal(normal,unit_vector_x)*supplemental_term_x)
        y_term = (dot_product_decimal(normal,unit_vector_y)*supplemental_term_y)
        z_term = (dot_product_decimal(normal,unit_vector_z)*supplemental_term_z)
        x_bar = x_bar + x_term/48
        y_bar = y_bar + y_term/48
        z_bar = z_bar + z_term/48
        #breakpoint()
    x_avg = x_bar / volume
    y_avg = y_bar / volume
    z_avg = z_bar / volume
    return [x_avg,y_avg,z_avg]

def find_volume_of_polyhedron(polyhedron):
    """Computes the volume of a polyhedron.
    
    The polyhedron should be formatted as a list of polygons.

    The polygons should be formatted as a list of points.

    The points should be formatted as a list of coordinates X, Y, Z.

    The normals of the polygons should be facing inward.

    Returns the volume as a number.
    """
    triangular_polyhedron = convert_polyhedron_to_triangular_polyhedron(polyhedron)

    #print(triangular_polyhedron)

    volume = 0
   
    for triangle in triangular_polyhedron: 
        a = triangle[0]
        b = triangle[1]
        c = triangle[2]
        minus_a = vector_times_scalar(a,-1)
        #print(triangle)
        #print(add_two_vectors_decimal(b,minus_a))
        normal = np.cross(add_two_vectors_decimal(b,minus_a),add_two_vectors_decimal(c,minus_a))
        unit_normal = find_unit_vector(normal)
        supplemental_term = dot_product_decimal(a,normal)/6
        #print(supplemental_term)
        volume = volume + supplemental_term
    return volume

def subtract_point_from_point(point1,point2):
    """Subtracts a point from another point, resulting in a new point.
    
    The points should be formatted as a list of three coordinates X, Y, Z.

    Returns the new point as a list of coordinates X, Y, Z.    
    """
    if len(point1) != len(point2):
        return "Error: Points must have the same dimension."
    else:
        new_point = []
        for i in range(len(point1)):
            new_coord = point1[i]-point2[i]
            new_point.append(new_coord)
        return new_point

def convert_polyhedron_to_arrays(polyhedron):
    """Converts the data in a polyhedron to array type data.
    
    The polyhedron should be formatted as a list of polygons.

    The polygons should be formatted as a list of points. 

    The points should be formatted as a list of coordinates X, Y, Z.

    Returns the same polyhedron with the lists formatted as arrays for plotting.

    Decimal numbers are converted to Floats for plotting. It is not reccomended to use this output for anything other than graphics display.
    """
    polyhedron_plot = []
    for polygon in polyhedron:
        fl_poly = []
        for point in polygon:
            fl_point = []
            for i in range(len(point)):
                fl_coord = float(point[i])
                fl_point.append(fl_coord)
            fl_point = np.array(fl_point)
            fl_poly.append(fl_point)
        polygon_array = np.array(fl_poly)
        polyhedron_plot.append(polygon_array)
    polyhedron_plot = np.array(polyhedron_plot)
    return polyhedron_plot


def make_cell_faces_inward_facing(cell):
    """Determines if the normal vector of the polyhedron is inward facing.
    
    The cell should be formatted as a dictionary with a list of faces called 'faces'.

    The faces should be formatted as a dictionary with a list of points called 'face'.

    The points should be formatted as a list of coordinates X, Y, Z.

    Returns True if the cross product of the vectors from the first three points faces into the polyhedron.
    """
    shortest_length = 0
    for i in range(len(cell['faces'])):
        for j in range(len(cell['faces'][i]['face'])):
            line_segment = [
                cell['faces'][i]['face'][j-1],
                cell['faces'][i]['face'][j],
            ]
            length = find_line_length(line_segment)
            if i == 0 and j == 0:
                shortest_length = length
            elif length < shortest_length:
                shortest_length = length
    magnitude = shortest_length / 100
    new_cell = {
        "faces": cell['faces'],
        "location": cell['location'],
        "centroid": cell['centroid'],
        "volume": cell['volume'],
    }
    for k in range(len(cell['faces'])):
        vector_1 = get_vector_from_line_segment([cell['faces'][k]['face'][-1],cell['faces'][k]['face'][0]])
        vector_2 = get_vector_from_line_segment([cell['faces'][k]['face'][0],cell['faces'][k]['face'][1]])
        normal_vector = cross_product_decimal(vector_1,vector_2)
        #print(get_magnitude_of_vector(normal_vector))
        small_normal = scale_vector_to_magnitude(normal_vector,magnitude)
        centroid = find_centroid_of_polygon(cell['faces'][k]['face'])
        #print(f'Polygon: {polyhedron[k]}')
        #print(f"Centroid: {centroid}")
        #print(f"Small normal: {small_normal}")
        test_point = add_two_vectors_decimal(centroid,small_normal)
        #print(f"Test point: {test_point}")
        polyhedron = []
        for b in range(len(cell['faces'])):
            polyhedron.append(cell['faces'][b]['face'])
        in_polyhedron = check_if_point_is_inside_polyhedron(polyhedron,test_point)
        #print(f"in_polyhedron: {in_polyhedron}")
        if in_polyhedron != True:
            new_polygon = reverse_polygon_normal(cell['faces'][k]['face'])
            new_cell['faces'][k]['face']=new_polygon
            #print(f"Polyk: {polyhedron[k]}")
            #print(f"new poly: {new_polygon}")
    return new_cell




def make_faces_inward_facing(polyhedron):
    """Determines if the normal vector of the polyhedron is inward facing.
    
    The polyhedron should be formatted as a list of polygons.

    The polygons should be formatted as a list of points.

    The points should be formatted as a list of coordinates X, Y, Z.

    Returns True if the cross product of the vectors from the first three points faces into the polyhedron.
    """
    shortest_length = 0
    for i in range(len(polyhedron)):
        for j in range(len(polyhedron[i])):
            line_segment = [
                polyhedron[i][j-1],
                polyhedron[i][j],
            ]
            length = find_line_length(line_segment)
            if i == 0 and j == 0:
                shortest_length = length
            elif length < shortest_length:
                shortest_length = length
    magnitude = shortest_length / 100
    new_polyhedron = []
    for k in range(len(polyhedron)):
        vector_1 = get_vector_from_line_segment([polyhedron[k][-1],polyhedron[k][0]])
        vector_2 = get_vector_from_line_segment([polyhedron[k][1],polyhedron[k][0]])
        normal_vector = cross_product_decimal(vector_1,vector_2)
        #print(get_magnitude_of_vector(normal_vector))
        small_normal = scale_vector_to_magnitude(normal_vector,magnitude)
        centroid = find_centroid_of_polygon(polyhedron[k])
        #print(f'Polygon: {polyhedron[k]}')
        #print(f"Centroid: {centroid}")
        #print(f"Small normal: {small_normal}")
        test_point = add_two_vectors_decimal(centroid,small_normal)
        #print(f"Test point: {test_point}")
        in_polyhedron = check_if_point_is_inside_polyhedron(polyhedron,test_point)
        #print(f"in_polyhedron: {in_polyhedron}")
        if in_polyhedron != True:
            new_polygon = reverse_polygon_normal(polyhedron[k])
            new_polyhedron.append(new_polygon)
            #print(f"Polyk: {polyhedron[k]}")
            #print(f"new poly: {new_polygon}")
        else:
            new_polyhedron.append(polyhedron[k])
    return new_polyhedron

#Section 3 Test Statements
line_1a = [
    example_part.vectors[10][0],
    example_part.vectors[10][1]
]
line_2a = [
    example_part.vectors[10][1],
    example_part.vectors[10][2]
]



line_1 = convert_coords_to_decimal(line_1a)
line_2 = convert_coords_to_decimal(line_2a)


#print(line1)
#print(line2)
#print(find_lines_intersection(line_1,line_2))



triangle = convert_coords_to_decimal(example_part.vectors[0])
equalateral_triangle = [[-10,0,0],[10,0,0],[0,17.3205080756888,0]]
extra_point = convert_coords_to_decimal(example_part.vectors[1])
#print(triangle)
polygon = [
    point
    for point in triangle
    ]
polygon.append(extra_point[2])

#polygon[1][0] = dec('20')
#polygon[2][0] = dec('20')

#print(polygon)



tet_vertex = [
    0,
    5.774,
    16.329,
]
triangle_2 = [
    equalateral_triangle[0],
    equalateral_triangle[1],
    tet_vertex,
]

triangle_3 = [
    equalateral_triangle[0],
    equalateral_triangle[2],
    tet_vertex,
    
]

triangle_4 = [
    equalateral_triangle[1],
    equalateral_triangle[2],
    tet_vertex,
]


simple_polyhedron = [
    equalateral_triangle,
    triangle_2,
    triangle_3,
    triangle_4,
]

#print(find_volume_of_polyhedron(simple_polyhedron))

#print(polygon)

polygon_2 = [
    [dec('-55'),dec('20'),dec('0')],
    [dec('-55'),dec('-20'),dec('0')],
    [dec('-55'),dec('-20'),dec('-100')],
    [dec('-55'),dec('20'),dec('-100')],
]

polygon_3 = [
    [dec('-55'),dec('-20'),dec('0')],
    [dec('-55'),dec('-20'),dec('-100')],
    [dec('20.358963012695312'),dec('-20'),dec('-100')],
    [dec('20.358963012695312'),dec('-20'),dec('0')],
]
#print(dec('20.358963012695312')**2)
#print(20.358963012695312**2)

polygon_4 = [
    [dec('20.358963012695312'),dec('20'),dec('0')],
    [dec('20.358963012695312'),dec('-20'),dec('0')],
    [dec('20.358963012695312'),dec('-20'),dec('-100')],
    [dec('20.358963012695312'),dec('20'),dec('-100')],
]

polygon_5 = [
    [dec('-55'),dec('20'),dec('0')],
    [dec('-55'),dec('-20'),dec('0')],
    [dec('20.358963012695312'),dec('-20'),dec('0')],
    [dec('20.358963012695312'),dec('20'),dec('0')],
]

polygon_6 = [
    [dec('-55'),dec('20'),dec('-100')],
    [dec('-55'),dec('-20'),dec('-100')],
    [dec('20.358963012695312'),dec('-20'),dec('-100')],
    [dec('20.358963012695312'),dec('20'),dec('-100')],
]

polyhedron = [
    polygon,
    polygon_2,
    polygon_3,
    polygon_4,
    polygon_5,
    polygon_6,
]

test_point = [dec('-17'),dec('40'),dec('-50')]

#inward_normals_polyhedron = make_faces_inward_facing(polyhedron)


#print(inward_normals_polyhedron)
#print("--------------")
#inward_again = make_faces_inward_facing(inward_normals_polyhedron)
#print(inward_again)

#print(check_if_point_is_inside_polyhedron(polyhedron,test_point))

#print(find_centroid_of_polygon(polygon_6))
#print(polyhedron)
#print(convert_polyhedron_to_triangular_polyhedron(polyhedron))

#triangular_polyhedron = convert_polyhedron_to_triangular_polyhedron(polyhedron)
#print(triangular_polyhedron)
#triangular_polyhedron = convert_polyhedron_to_triangular_polyhedron(triangular_polyhedron) #Returns the same triangular polyhedron since it was already triangular.
#print(triangular_polyhedron)
#print(find_centroid_of_polyhedron(polyhedron))
#simple_polyhedron_in = make_faces_inward_facing(simple_polyhedron)
#centroid_of_polyhedron = find_centroid_of_polyhedron(inward_normals_polyhedron)
#print(centroid_of_polyhedron)

#volume_of_polyhedron = find_volume_of_polyhedron(inward_normals_polyhedron)
#print(volume_of_polyhedron)


#print(check_if_point_is_inside_polyhedron(inward_normals_polyhedron,centroid_of_polyhedron))
#print((dec('55')+dec('20.358963012695312'))*dec('40')*dec('100'))
simple_polyhedron_vertices = [
    equalateral_triangle[0],
    equalateral_triangle[1],
    equalateral_triangle[2],
    tet_vertex,
]

#volume_of_tetrahedron = find_volume_of_tetrahedron(simple_polyhedron_vertices)
#print(volume_of_tetrahedron)
#simple_polyhedron_in2 = make_faces_inward_facing(simple_polyhedron_in)
#print(simple_polyhedron_in2)

inside_point = [dec('3.170042825957285174642110988'), dec('7.603893540173261504771490322'), dec('5.376335997404708405364924862')]


#Testing 

#print(f"{np.random.random()}") #works

#plane_equation = [[dec('0.8164953124122817965918330777'), dec('0.4714037884132977453930289103'), dec('0.3333374762584626605437553952')], dec('8.164953124122817965918330777')]

#random_point = generate_random_point_in_plane(plane_equation)

#print(f"Random point in plane: {random_point}")

#print(f"Inside polyhedron: {check_if_point_is_inside_polyhedron(simple_polyhedron,inside_point)}")





#simple_polyhedron_in2 = make_faces_inward_facing(simple_polyhedron_in)

#print(cross_product_decimal([70,0,0],[0,50,0]))

folded_polygon = [[dec('-55'), dec('20'), dec('0')], [dec('20.3589630126953125'), dec('20'), dec('-100')], [dec('20.3589630126953125'), dec('20'), dec('0')], [dec('-55'), dec('20'), dec('-100')]]
#print(folded_polygon)
#print(find_triangle_centroid(triangle))

#print(find_triangle_area(triangle))

#print(check_if_manifold(example_part.vectors))

#To be completed:
#print(check_if_point_inside_polygon(triangle,triangle[2]))

line_3 = [
    [0,0,0],
    [0,1,0],
]
line_4 = [
    [2,2,0],
    [3,2,0]
]

colinear = [
    [dec(0.0000),dec(0.0000),dec(0.0000)],
    [dec(1.0000),dec(1.0000),dec(1.0000)],
    [dec(-2.0000),dec(-2.0000),dec(-2.0000)],
]

#print(are_these_three_points_colinear(colinear))

#print(find_lines_intersection(line_1,line_2))

#print(check_if_polygon_is_folded(triangle))

#print(find_equation_of_plane(triangle))

#print(find_centroid_of_polygon(triangle))
#print(find_triangle_centroid(triangle))

#print(unfold_polygon_points(folded_polygon))
#
# 
# unfolded_polygon = unfold_polygon_points(folded_polygon)
#
# 
# print(find_polygon_area(unfolded_polygon))

point = [dec(-25), dec(20), dec(-50)]

line_6 = [[
    dec(-32),
    dec(0),
    dec(-50)
],[
    dec(-45),
    dec(40),
    dec(-60)
]]

#print(find_intersection_of_plane_and_line_segment(triangle,line_6))

#print(check_if_point_inside_polygon(unfolded_polygon,point))

#three_points = [
#    unfolded_polygon[1],
#    unfolded_polygon[2],
#    unfolded_polygon[3],
#]
#print(three_points)
#print(are_these_three_points_colinear(three_points))

#test_triangle = [[dec('-17.32051849365234375'), dec('20'), dec('-50')], [dec('-55'), dec('20'), dec('0')], [dec('20.3589630126953125'), dec('20'), dec('0')]]

#print(find_triangle_area(test_triangle))

#Testing projecting a point onto a plane

projector_point = [
    34,
    56,
    87,
]
#this_plane = find_equation_of_plane(triangle)
#projected_point = project_point_onto_plane(this_plane,projector_point)
#print(projected_point)


#Section 4 Plotting

figure = pyplot.figure()
axes = figure.add_subplot(projection='3d')


sample_array = np.array([[-55.0,20.0,0.0],[20.358963,20.0,0.0],[20.358963,20.0,-100.0]])
#print(sample_array)

polyhedron_plot = convert_polyhedron_to_arrays(example_part.vectors)

axes.add_collection3d(mplot3d.art3d.Poly3DCollection(polyhedron_plot, shade=True, facecolors='linen', edgecolors='lightslategray'))

scale = example_part.points[0:2].flatten()
axes.auto_scale_xyz(scale, scale, scale)
#axes.
#pyplot.show()