import geo_functions as geo
import numpy as np
from stl import mesh

polygon = [
  [ 12.5,  25.,   50. ],
  [ 12.5, -25.,   50. ],
  [ 25.,   25.,   37.5],
]

intersection = [29.229041195000516, 37.69638116056837, 33.27095880499948]

#inside = 0
#for i in range(1000):
#    check_it = geo.check_if_point_inside_polygon(polygon, intersection)
#    if check_it == True:
#       inside = inside +1
#       #print(check_it)
#print(inside/1000)


#test_line= [[29.229041195000516, 37.69638116056837, 33.27095880499948], [-60.02878571606698, -52.305719347917, 122.52878571606432]]
#crossings = 0
#for i in range(len(polygon)):
#    line = [
#        polygon[i-1],
#        polygon[i],
#    ]
#    is_coplanar = geo.check_if_lines_are_coplanar(test_line,line)
#    print(is_coplanar)
#    this_intersection = geo.find_lines_intersection(test_line,line)
#    if type(this_intersection) == list:
#        crossings = crossings +1
#print(crossings)

model = mesh.Mesh.from_file('small_heatsink_2.stl').vectors
#model = geo.make_faces_inward_facing(model)



nonarray = []

for triangle in model:
  this_triangle = []
  for point in triangle:
    this_point = []
    for coord in point:
        this_point.append(coord)
    this_triangle.append(this_point)
  nonarray.append(this_triangle)

base_edge_2 = [
    [25.0, -25.0, 50.0],
    [-25.0, -25.0, 50.0],
]

#plane_point_2 = geo.find_intersection_of_plane_and_line_segment(model[8],base_edge_2)

#print(plane_point_2)


coplanar_check = [[25.0, 25.0, 0.0], 
 [25.0, 25.0, 50.0], 
 [-25.0, 25.0, 50.0], 
 [-25.0, 25.0, 0.0], 
 [-25.,  25.,   0.], 
 [-25.,  25.,  50.], 
 [12.5, 25. , 50. ]]

#print(geo.check_if_polygon_is_coplanar(coplanar_check))

#print(geo.find_equation_of_plane(coplanar_check[0:3]))

#print(geo.find_equation_of_plane(coplanar_check[3:6]))

#print(geo.find_equation_of_plane(coplanar_check[4:7]))


test_point = [15.0, -5.0, 47.5]

triangle = model[7]

#print(geo.check_if_point_inside_polygon(triangle, test_point))

test_line = [[15.0,-5.0,40],
             [15.0,-5.0,50]]


test_polygon = [
    [0,0,0],
    [2,0,0],
    [4,0,0],
    [4,4,0],
    [0,4,0],

]

cell_171_face_5 = [[8.333333333333336, 8.333333333333336, 25.0], [8.333333333333336, 16.66666666666667, 25.0], [16.66666666666667, 16.66666666666667, 25.0], [16.66666666666667, 8.333333333333336, 25.0]]

#print(geo.find_intersection_of_plane_and_line_segment(model[7],test_line))

#print(geo.find_centroid_of_polygon(cell_171_face_5))

#print(geo.find_centroid_of_polygon_2(model[7]))
#print(geo.find_triangle_centroid(model[7]))



face = [[-16.666666666666664, 25.000000000000007, 0.0], 
 [-16.666666666666664, 25.0, 6.2500000000000036], 
 [-16.666666666666664, 25.000000000000007, 8.333333333333334], 
 [-18.749999999999993, 25.0, 8.333333333333343], 
 [-25.0, 25.000000000000007, 8.333333333333334], 
 [-25.0, 25.000000000000007, 0.0]]

#print(geo.find_approximate_centroid_of_polygon(face))

#print(geo.convert_polyhedron_to_approximate_triangular_polyhedron([face]))

triangle = [[-16.666666666666664, 25.000000000000007, 0.0],
  [-16.666666666666664, 25.0, 6.2500000000000036], 
  [-16.666666666666664, 25.000000000000004, 5.208333333333336]]

triangle_2 = [[-25.,   25.,    0. ],
 [-25.,   25.,   50. ],
 [ 12.5,  25.,   50. ]]

#print(geo.find_triangle_centroid(triangle))

line1 = [[-16.666666666666664, 25.000000000000004, 3.1250000000000018], 
 [-16.666666666666664, 25.000000000000004, 5.208333333333336]] 

line2 = [[-16.666666666666664, 25.000000000000007, 2.604166666666668], 
 [-16.666666666666664, 25.0, 6.2500000000000036]]

#print(geo.check_if_lines_are_colinear(line1, line2))


face_2 = [[-25.0, -25.0, 8.333333333333334], 
          [-25.0, -16.666666666666664, 8.333333333333334], 
          [-16.666666666666664, -16.666666666666664, 8.333333333333334], 
          [-16.666666666666664, -25.0, 8.333333333333334], 
          [-18.749999999999996, -25.0, 8.333333333333336]]

face_2_triangles = geo.convert_polyhedron_to_approximate_triangular_polyhedron([face_2])
#print(geo.find_approximate_centroid_of_polygon(face_2))





line_1 = [np.array([25., 25.,  0.]), np.array([-25.,  25.,  50.])] 

line_check= [np.array([-25.,  25.,  50.]), np.array([25., 25.,  0.])]

#print(geo.are_these_line_segments_the_same(line_1, line_check))

#corrected_model = geo.combine_adjacent_coplanar_triangles(model)
#corrected_model = geo.combine_adjacent_coplanar_triangles(nonarray)

#corrected_model = geo.remove_duplicate_points(corrected_model)
#corrected_model = geo.make_faces_inward_facing(corrected_model)
#corrected_model = geo.unfold_polyhedron(corrected_model)

#print(corrected_model)



#print(geo.are_these_points_the_same([  2., -10.,   4.],[  2., -10.,   4.]))



#TEST: Divide a line segment up into sub-segments.

#print(geo.find_line_length(line_1))
#divided_segment = geo.add_extra_points_to_segment(line_1,10.)

#print(divided_segment)

#total_length = 0
#for i in range(len(divided_segment)-1):
#  this_length = geo.find_line_length([divided_segment[i],divided_segment[i+1]])
#  total_length = total_length + this_length
#  if i==0:
#    print(this_length)

#print(total_length)

#END TEST


point_1 = [4,2,2]
point_2 = [2,4,2]
point_3 = [2,0,2]
point_4 = [2,2,4]


print(geo.find_center_and_radius_of_sphere(point_1,point_2,point_3,point_4))