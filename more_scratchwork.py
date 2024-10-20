import geo_functions as geo

from stl import mesh


planar_polygon = [
    [0,0,0],
    [1,1,1],
    [2,3,4],
    [4,5,6],
    [1,1,1],
]

non_planar_polygon = [
    [0,0,0],
    [0,0,1],
    [0,1,1],
    [1,1,1],
    [1,0,1],
    [1,1,0],
]

#print(geo.remove_duplcate_points(planar_polygon))

#print(geo.check_if_polygon_is_coplanar(non_planar_polygon))
Triangle = [[-25,  25,   0.],
 [-25, -25,  50.],
 [-25,  25,  50.],]
Point= [-25.0, -25.0, 0.0]


#for i in range(1000):
#    check_it = geo.check_if_point_inside_polygon(Triangle,Point)
#    if check_it == True:
#        print(check_it)

Test_Line = [[-25.0, -25.0, 0.0], 
             [-25.0, 108.54839831539317, 172.11606617580352]]

line1 = [
    Triangle[-1],
    Triangle[0],
]
line2 = [
    Triangle[0],
    Triangle[1],
]
line3 = [
    Triangle[1],
    Triangle[2],
]
intersection_1 = geo.find_lines_intersection(line1, Test_Line)
#print(intersection_1)

intersection_2 = geo.find_lines_intersection(line2, Test_Line)
#print(intersection_2)

intersection_3 = geo.find_lines_intersection(line3, Test_Line)
#print(intersection_3)



model = mesh.Mesh.from_file('single_cell_cutout.stl').vectors
model = geo.make_faces_inward_facing(model)

point = [25,25,50]
inside = 0
for i in range(1000):
    check_it = geo.check_if_point_is_inside_polyhedron(model,point)
    if check_it == True:
       inside = inside +1
       #print(check_it)
print(inside/1000)




face = [[5.0, 25.0, 20.0], [5.0, 25.0, 22.5], [5.0, 25.0, 30.0], [5.0, 15.0, 30.0], [5.0, 15.0, 20.0]]



[[15.0, -5.0, 47.5], [22.5, -5.0, 40.0]]

{'faces': [
    
    {'face': [[15.0, -5.0, 40.0], [15.0, 5.0, 40.0], [22.5, 5.0, 40.0], [22.5, -5.0, 40.0]], 'bc': (4, 2, 3), 'area': 75.0, 'centroid': [18.75, 0.0, 40.0]}, 
    {'face': [[15.0, -5.0, 40.0], [15.0, -5.0, 47.5], [22.5, -5.0, 40.0]], 'bc': (4, 1, 4), 'area': 28.124999999999986, 'centroid': [17.5, -5.0, 42.5]}, 
    {'face': [[22.5, 5.0, 40.0], [15.0, 5.0, 47.5], [15.0, 5.0, 40.0]], 'bc': (4, 3, 4), 'area': 28.124999999999986, 'centroid': [17.5, 5.0, 42.5]}, 
    {'face': [[15.0, 5.0, 40.0], [15.0, 5.0, 47.5], [15.0, -5.0, 47.5], [15.0, -5.0, 40.0]], 'bc': (3, 2, 4), 'area': 75.0, 'centroid': [15.0, 0.0, 43.75]}, 
    {'face': [[15.0, -5.0, 47.5], [15.0, 5.0, 47.5], [20.0, 5.0, 42.5], [17.5, -5.0, 45.0]], 'bc': 'asdfasd', 'area': 53.03300858899106, 'centroid': [16.874999999999996, 0.0, 45.625]}, 
    {'face': [[22.5, -5.0, 40.0], [22.5, 5.0, 40.0], [20.0, 5.0, 42.5], [17.5, -5.0, 45.0]], 'bc': 'asdfasd', 'area': 53.03300858899105, 'centroid': [20.624999999999996, 0.0, 41.875]}], 'location': (4, 2, 4), 'centroid': '', 'volume': ''}