import PySimpleGUI as sg
import numpy as np
from stl import mesh
import db_calls as db
import datetime
from dateutil import parser
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib
import geo_functions as geo
from mpl_toolkits import mplot3d
from tkinter import Canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os.path
from decimal import Decimal as dec
import math
import sys
import resource
import multiprocessing as mp
import os


#Section 1 Date and Time Information
current_time = datetime.datetime.now()
sample_date = parser.parse('2023-04-02')

current_date = current_time.date()
week_past = current_date - datetime.timedelta(6)

#Section 2 Initial Data

program_title = "Pycante"

example_part = mesh.Mesh.from_file('PartDesignExample-Body.stl')

boundary_condition_types = ['Fixed Temperature', 'Heat Flux', 'Convection']
temperature_units = ["Kelvin", "Celsius", "Fahrenheit", "Rankine"]
thermal_conductivity_units = ["W/m-K", "BTU/hr-ft-°F"]
convective_coefficient_units = ["W/m2-K", "BTU/hr-ft2-°F"]
heat_flux_units = ["W/m2", "BTU/hr-ft2"]


#sys.setrecursionlimit(10**6)
#resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))

#Section 3 GUI Layout

sg.theme('DarkGrey4')

menu_def = [
    ['File',['New','Open','Save','Save As','Exit']],
    ['Help',['Documentation', 'About']]
]

import_stl_tab = [
    [sg.Text("STL File Definition")],
    [sg.Input(size=(40,1), key="-Import_Filename_Input-"), sg.FileBrowse(button_text="Select File", key="-Import_Filename_Button-", file_types=(('*.stl','*.stl'),))],
    [sg.Text("Model Units"),sg.Combo(['mm', 'cm', 'm', 'in', 'ft'], default_value="mm", key="-Model_Units-"), sg.Push(),sg.Button(button_text="Import", key="-Import_File_Button-")],
    [sg.Text("Boundary Conditions:")],
    [sg.Listbox(values=[], size=(52,5),key="-Boundary_Conditions-", enable_events=True, select_mode='single', tooltip="Select a boundary to display triangles.")],
    [sg.Input(size=(20,1), key="-Add_Boundary_Input-"), sg.Button("Add Boundary", key="-Add_Boundary_Button-", size=(10,0)), sg.Push(), sg.Button("Delete Boundary", key="-Delete_Boundary_Button-", auto_size_button=True)],
    [sg.Text("Triangles:", key="-Triangles_Title-")],
    [sg.Listbox(values=[], size=(52,10),key="-Selected_Triangles-", enable_events=True, select_mode='extended', tooltip="Select triangles then assign to a boundary with the dropdown.")],
    [sg.Button("Select All", key="-Select_All_Triangles_Button-"),sg.Push(), sg.Combo(['unassigned'], key="-Add_To_Boundary_Dropdown-", size=(15,1), tooltip="Select a boundary to move triangles.", readonly=True),sg.Button("Assign", key="-Assign_To_Boundary_Condition_Button-", tooltip="Select a boundary condition from the dropdown to move triangles.")],
]

generate_mesh_tab = [
    [sg.Text("Generate Mesh")],
    [sg.Text("Check Case: "), sg.Button("Check", key="-Check_Case_Button-")],
    [sg.Text("Model Extents: "), sg.Text("TBD", key="-Model_Extents_Display-")],
    [sg.Text("Max Cell Size: "), sg.Input(size=(10,1), key="-Max_Cell_Size_Input-"), sg.Text("Units")],
    [sg.Text("Algorythm: "), sg.Combo(["Hexer", "Tetra"], default_value="Tetra", key="-Mesh_Algorythm_Selector-")],
    [sg.Push(), sg.Button("Generate Mesh", key="-Generate_Mesh_Button-", disabled=True)],
    [sg.Input("all",size=(10,1), key = "-View_Specific_Cell-"),sg.Button("View Cell", key="-View_Cell_Button-")]
]

case_setup_tab = [
    [sg.Text("Setup Case")],
    [sg.Text("Volume Conditions:")],
    [sg.Text("k"),sg.Input("237", key="-Thermal_Conductivity_Input-", size=(6,1)),sg.Combo(thermal_conductivity_units, key="-Thermal_Conductivity_Units-", default_value="W/m-K"),sg.Button("Set Conductivity", key="-Thermal_Conduictivity_Button-")],
    [sg.Text("Boundary Conditions:")],
    [sg.Listbox(values=[], size=(52,5),key="-Boundary_Condition_Attributes-", enable_events=True, select_mode='single', tooltip="Select a boundary to set attributes.")],
    [sg.Text("Please select a boundary condition to set attributes.", key="-Boundary_Condition_Message-")],
    [sg.Text("Boundary Type:", key="-Boundary_Type_Label-",visible=False),sg.Combo(boundary_condition_types, enable_events=True, key="-Boundary_Condition_Type_Selector-", visible=False)],
    [sg.Text("T-surf", key="-T_Surface_Label-", visible=False),sg.Input("0", size=(6,1), key="-T_Surface_Input-", visible=False),sg.Combo(temperature_units, default_value="Kelvin", key="-T_Surf_Units-", visible=False)],
    [sg.Text("T-inf", key="-T_Infinity_Label-", visible=False),sg.Input("0", size=(6,1), key="-T_Infinity_Input-", visible=False),sg.Combo(temperature_units, default_value="Kelvin", key="-T_Infinity_Units-", visible=False)],
    [sg.Text("H-conv", key="-Convection_Coefficient_Label-", visible=False),sg.Input("0", size=(6,1),key="-Convection_Coefficient_Input-", visible=False),sg.Combo(convective_coefficient_units, default_value="W/m2-K", key="-H_Convection_Units-", visible=False)],
    [sg.Text("q/area", key="-Heat_Flux_Label-", visible=False),sg.Input("0", size=(6,1),key="-Heat_Flux_Input-", visible=False),sg.Combo(heat_flux_units, default_value="W/m2", key="-Heat_Flux_Units-", visible=False)],
    [sg.Push(),sg.Button("Set Attributes", key="-Set_Attributes_Button-", visible=False)],
]   

run_case_tab = [
    [sg.Text("Initialize Case:")],
    [sg.Text("Initial Temperature"), sg.Input("300", size=(5,1), key="-Initialize_Case_Input-"),sg.Combo(temperature_units, default_value="Kelvin", key="-Initial_T_Units-", visible=True), sg.Push(), sg.Button("Initialize", key="-Initialize_Case_Button-")],
    [sg.Text("Solver Parameters")],
    [sg.Text("Relaxation Factor:"), sg.Input("0.05", size=(5,1), key="-Relaxation_Factor_Input-"),sg.Push(), sg.Button("Set Relaxation Factor", key="-Set_Relaxation_Factor_Button-")],
    [sg.Text("Max Iterations:"), sg.Input("100", size=(8,1), key="-Max_Iterations_Input-"),sg.Push(), sg.Button("Set Max Iterations", key="-Set_Max_Iterations_Button-")],
    [sg.Text("Minimum Residual:"), sg.Input("1E-8", size=(8,1), key="-Min_Residual_Input-"),sg.Push(), sg.Button("Set Min Residual", key="-Set_Min_Residual_Button-")],
    [sg.Push(),sg.Button("Solve Case", key="-Solve_Case_Button-")],
]

results_tab = [
    [sg.Text("Results")],
    [sg.Text("Solution not found for this case.", key="-Solution_Message-")],
    [sg.Push(), sg.Button("View Solution", key="-View_Solution_Button-")],
]

graphics_layout = [
    [sg.Canvas(size=(800,600), key="-Graphics_Area-", pad=(10,10), expand_x=True, expand_y=True, background_color='lightgray')],
]
messages_layout = [
    [sg.Text(text="Import an STL file to get started.", size=(150,10), expand_x=True, expand_y=True, key="-System_Messages-")],
]
layout1 = [
    [sg.Menu(menu_def, )],
    [sg.Text(program_title, size=(80,1),justification="center",font=("",18))],
    [
        sg.TabGroup([
            [sg.Tab('Import STL', import_stl_tab)],
            [sg.Tab('Generate Mesh', generate_mesh_tab)],
            [sg.Tab('Case Setup', case_setup_tab)],
            [sg.Tab('Run Case', run_case_tab)],
            [sg.Tab('Results', results_tab)],
        ],size=(300,600), expand_y=True)
        , sg.Frame('Graphics Area', graphics_layout),
    ],
                    
    [sg.Frame('Messages',size=(1225,50),layout=messages_layout),],
]

#Section 4 Functions and Classes

def draw_figure(canvas, figure):
    print(figure)
    if not hasattr(draw_figure, 'canvas_packed'):
        draw_figure.canvas_packed = {}
    tkcanvas = FigureCanvasTkAgg(figure, canvas)
    tkcanvas.draw()
    tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    widget = tkcanvas.get_tk_widget()
    if widget not in draw_figure.canvas_packed:
        draw_figure.canvas_packed[widget] = figure
        widget.pack(side='top', fill='both', expand=1)
    return tkcanvas

def view_solution(face_mesh, cmapping, min_temp, max_temp, canvas, axes, figure):
    

    init_xmin = False
    init_xmax = False
    init_ymin = False
    init_ymax = False
    init_zmin = False
    init_zmax = False

    if(figure!=False):
        delete_figure(canvas)
        init_elev = axes.elev
        init_azim = axes.azim
        init_scale = axes.get_w_lims()
        init_xmin = init_scale[0]
        init_xmax = init_scale[1]
        init_ymin = init_scale[2]
        init_ymax = init_scale[3]
        init_zmin = init_scale[4]
        init_zmax = init_scale[5]
    else: 
        init_elev = 60
        init_azim = -45

    figure = plt.figure(facecolor='lightgray')
    axes = figure.add_subplot(1,1,1, frame_on=False, projection='3d', facecolor='lightgray')
    figure.set_figheight(6)
    figure.set_figwidth(8)
    figure.set_dpi(100)
    figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


    #Create the colormap. To be updated with selected_triangles, a list of indices.

    
    lighting = matplotlib.colors.LightSource(315, 45)
    colormap = matplotlib.colors.LinearSegmentedColormap.from_list(name="this_map",colors=['Blue','Green','Yellow','Orange','Red'],N=64)
    #print(cmapping)
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(face_mesh, color=colormap(cmapping), zsort="min"))
    
    if init_xmin==False:
        scale = this_analysis.stl_model.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
    else:
        axes.set_xlim(init_xmin,init_xmax)
        axes.set_ylim(init_ymin,init_ymax)
        axes.set_zlim(init_zmin,init_zmax)
    axes.set_xlabel('X')
    axes.set_ylabel('Y')
    axes.set_zlabel('Z')
    plt.gca().view_init(init_elev,init_azim)
    canvas = draw_figure(window["-Graphics_Area-"].TKCanvas, figure)



    return canvas, axes, figure

def view_scatter_plot(generated_mesh, canvas, axes, figure):
    init_xmin = False
    init_xmax = False
    init_ymin = False
    init_ymax = False
    init_zmin = False
    init_zmax = False

    if(figure!=False):
        delete_figure(canvas)
        init_elev = axes.elev
        init_azim = axes.azim
        init_scale = axes.get_w_lims()
        init_xmin = init_scale[0]
        init_xmax = init_scale[1]
        init_ymin = init_scale[2]
        init_ymax = init_scale[3]
        init_zmin = init_scale[4]
        init_zmax = init_scale[5]
    else: 
        init_elev = 60
        init_azim = -45

    figure = plt.figure(facecolor='lightgray')
    axes = figure.add_subplot(1,1,1, frame_on=False, projection='3d', facecolor='lightgray')
    figure.set_figheight(6)
    figure.set_figwidth(8)
    figure.set_dpi(100)
    figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)



    for point in generated_mesh:
        xs = point[0]
        ys = point[1]
        zs = point[2]
        axes.scatter(xs,ys,zs, marker='o')
    
    if init_xmin==False:
        scale = this_analysis.stl_model.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
    else:
        axes.set_xlim(init_xmin,init_xmax)
        axes.set_ylim(init_ymin,init_ymax)
        axes.set_zlim(init_zmin,init_zmax)
    axes.set_xlabel('X')
    axes.set_ylabel('Y')
    axes.set_zlabel('Z')
    plt.gca().view_init(init_elev,init_azim)
    canvas = draw_figure(window["-Graphics_Area-"].TKCanvas, figure)



    return canvas, axes, figure    


def view_stl_part(model, canvas, axes, figure, selected_triangles):

    

    init_xmin = False
    init_xmax = False
    init_ymin = False
    init_ymax = False
    init_zmin = False
    init_zmax = False

    if(figure!=False):
        delete_figure(canvas)
        init_elev = axes.elev
        init_azim = axes.azim
        init_scale = axes.get_w_lims()
        init_xmin = init_scale[0]
        init_xmax = init_scale[1]
        init_ymin = init_scale[2]
        init_ymax = init_scale[3]
        init_zmin = init_scale[4]
        init_zmax = init_scale[5]
    else: 
        init_elev = 60
        init_azim = -45

    figure = plt.figure(facecolor='lightgray')
    axes = figure.add_subplot(1,1,1, frame_on=False, projection='3d', facecolor='lightgray')
    figure.set_figheight(6)
    figure.set_figwidth(8)
    figure.set_dpi(100)
    figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


    #Create the colormap. To be updated with selected_triangles, a list of indices.
    cmapping = []
    for i in range(len(model)):
        index_selected = False
        for triangle_index in selected_triangles:
            if i == triangle_index:
                index_selected = True
                cmapping.append(1.0)
        if index_selected == False:
            cmapping.append(0.0)
    
    lighting = matplotlib.colors.LightSource(315, 45)
    cmapping = np.array(cmapping)
    colormap = matplotlib.colors.ListedColormap(colors=['lightsteelblue','indianred'],N=2)
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(model, color=colormap(cmapping), edgecolor='black', linewidth=0.3, zsort="min"))
    
    if init_xmin==False:
        scale = this_analysis.stl_model.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
    else:
        axes.set_xlim(init_xmin,init_xmax)
        axes.set_ylim(init_ymin,init_ymax)
        axes.set_zlim(init_zmin,init_zmax)
    axes.set_xlabel('X')
    axes.set_ylabel('Y')
    axes.set_zlabel('Z')
    plt.gca().view_init(init_elev,init_azim)
    canvas = draw_figure(window["-Graphics_Area-"].TKCanvas, figure)



    return canvas, axes, figure

def show_example_plot(example_part, canvas, axes, figure):

    init_xmin = False
    init_xmax = False
    init_ymin = False
    init_ymax = False
    init_zmin = False
    init_zmax = False

    if(figure!=False):
        delete_figure(canvas)
        init_elev = axes.elev
        init_azim = axes.azim
        init_scale = axes.get_w_lims()
        init_xmin = init_scale[0]
        init_xmax = init_scale[1]
        init_ymin = init_scale[2]
        init_ymax = init_scale[3]
        init_zmin = init_scale[4]
        init_zmax = init_scale[5]
    else: 
        init_elev = 60
        init_azim = -45

    figure = plt.figure(facecolor='lightgray')
    axes = figure.add_subplot(1,1,1, frame_on=False, projection='3d', facecolor='lightgray')
    figure.set_figheight(6)
    figure.set_figwidth(8)
    figure.set_dpi(100)
    figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    example_part_arrays = geo.convert_polyhedron_to_arrays(example_part.vectors)


    cmapping = []
    for i in range(len(example_part.vectors)):
        cmapping.append(0.0)
    cmapping[0] = 1.0
    cmapping[1] = 1.0
    cmapping = np.array(cmapping)
    colormap = matplotlib.colors.ListedColormap(colors=['lightsteelblue','indianred'],N=2)
    #colormap.__call__(cmapping)
    #print(colormap(cmapping))

    
    #axes.plot_surface(X=x, Y=y, Z=z)
    #axes.add_collection3d(mplot3d.art3d.Poly3DCollection(example_part_arrays[0:10], cmap= colormap, shade=True, facecolors='lightgray', edgecolors='gray'))

    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(example_part_arrays, color=colormap(cmapping), edgecolor='black', linewidth=0.3))
    
    if init_xmin==False:
        scale = example_part.points.flatten()
        #print(len(scale))
        axes.auto_scale_xyz(scale, scale, scale)
    else:
    #print(axes.get_scale_xyz)
        axes.set_xlim(init_xmin,init_xmax)
        axes.set_ylim(init_ymin,init_ymax)
        axes.set_zlim(init_zmin,init_zmax)
    #print(axes.get_w_lims())
    axes.set_xlabel('X')
    axes.set_ylabel('Y')
    axes.set_zlabel('Z')
    #print(axes.scale)
    #Canvas.create_window
    #Set initial view
    plt.gca().view_init(init_elev,init_azim)
    #axes._position = matplotlib.transforms.Bbox.from_bounds(0, 0, 1, 1)
    #print(axes.elev)
    #print(axes.azim)
    #print(axes.get_position())
    #figure.
    canvas = draw_figure(window["-Graphics_Area-"].TKCanvas, figure)
    return canvas, axes, figure

def delete_figure(canvas):
    canvas.get_tk_widget().forget()
    try:
        draw_figure.canvas_packed.pop(canvas.get_tk_widget())
    except Exception as e:
        print(f'Error removing {canvas} from list', e)
    plt.close()
    
def get_view_parameters(axes):
    print(axes.elev)
    print(axes.azim)
    print(axes.get_w_lims())

def view_boundary_condition(values):
    boundary_conditions = values['-Boundary_Conditions-']
    triangles = []
    if boundary_conditions[0] == 'all':
        triangles = [
            triangle[0]
            for triangle in this_analysis.triangles
        ]        
    else:
        triangles = [
            triangle[0]
            for triangle in this_analysis.triangles
            if triangle[1] == boundary_conditions[0]
        ]
    window['-Selected_Triangles-'].update(triangles)
    window['-Triangles_Title-'].update(f"""Viewing Triangles in {boundary_conditions[0]}""")

def select_all_triangles(values):
    all_triangles = window["-Selected_Triangles-"].Values
    #print(all_triangles)
    indices = []
    for i in range(len(all_triangles)):
        indices.append(i)
    window["-Selected_Triangles-"].update(set_to_index=indices)
    return all_triangles

def get_boundary_condition_options():
    new_boundary_conditions = []
    for condition in this_analysis.boundary_conditions:
        if condition != 'all':
            new_boundary_conditions.append(condition)
    return new_boundary_conditions

def prepare_mesh_for_display(generated_mesh, cell):
    """Creates a list of faces for display."""
    face_mesh = []
    if cell == 'all':
        for this_cell in range(len(generated_mesh)):
            for face in generated_mesh[this_cell]['faces']:
                this_face = []
                for point in face['face']:
                    this_face.append(point)
                face_mesh.append(this_face)
    else:
        print(generated_mesh[cell])
        for face in generated_mesh[cell]['faces']:
            this_face = []
            for point in face['face']:
                this_face.append(point)
            face_mesh.append(this_face)
    return face_mesh

def convert_temperature_to_kelvin(input, units):
    """Converts temperature from the input units to Kelvin."""
    if units == "Kelvin" or units == "kelvin":
        return input
    elif units == "Celsius" or units == "celsius":
        temperature = input + 273.15
        return temperature
    elif units == "Rankine" or units == "rankine":
        temperature = input * 5 / 9
        return temperature
    elif units == "Fahrenheit" or units == "fahrenheit":
        temperature = (input + 460.67) * 5 / 9
        return temperature
    else:
        return "Error: Please provide units as kelvin, celsius, rankine, or fahrenheit."
    
def convert_thermal_conductivity_to_si(input, units):
    """Converts thermal conductivity input to SI units (lenth units in mm)."""
    if units == "W/m-K":
        return input / 1000
    elif units == "BTU/hr-ft-°F":
        conductivitiy = input / (0.5779*1000) #From engineeringtoolbox.com
        return conductivitiy
    else:
        return "Error: Please provide units as W/m-K or BTU/hr-ft-°F"

def convert_convection_coefficient_to_si(input, units):
    """Converts convection coefficient to W/mm2-K"""
    if units == "W/m2-K":
        return input / (1E6)
    elif units == "BTU/hr-ft2-°F":
        coefficient = input * 5.678 / (1E6) #Introduction to Heat Transfer
        return coefficient
    else:
        return "Error: Please input in W/m2-K or BTU/hr-ft2-°F"

def convert_heat_flux_units_to_si(input, units):
    """Converts heat flux to SI units (area units in mm2)."""
    if units == "W/m2":
        return input / (1E6)
    elif units == "BTU/hr-ft2":
        heat_flux = input * 3.1525 / (1E6) #EngineeringToolbox.com
        return heat_flux
    else:
        return "Error: Please input heat flux in W/m2 or BTU/hr-ft2"

class analysis_case:
    def __init__(self, stl_file, scale):
        self.stl_file = stl_file
        self.boundary_conditions = ['all','unassigned']
        self.added_boundary_conditions = []
        self.boundary_condition_attributes = []
        self.thermal_conductivity = 237 / 1E3
        self.relaxation_factor = 0.5
        self.max_iterations = 100
        self.min_residual = 1E-8
        self.solution = []
        self.mesh = []
        self.stl_model = mesh.Mesh.from_file(stl_file)
        if scale != 1:
            self.scale_model(scale)
        self.triangles = [
            [index,'unassigned']
            for index in range(len(self.stl_model.vectors))
        ]
    
    def set_thermal_conductivity(self, conductivity):
        """Sets the thermal conductivity for the volume condition."""
        self.thermal_conductivity = conductivity #Always in W/m-K

    def set_relaxation_factor(self, relaxation_factor):
        """Sets the relaxation factor for the solver."""
        self.relaxation_factor = relaxation_factor

    def set_max_iterations(self, max_iterations):
        """Sets the maximum number of iterations in the solver."""
        self.max_iterations = max_iterations

    def set_min_residual(self, min_residual):
        """Sets the minimum allowable residual in the solver."""
        self.min_residual = min_residual

    def initialize_solution(self, initial_temperature):
        """Sets the initial temperature for cells and boundary faces."""
        self.solution = []
        for i in range(len(self.mesh)):
            initial_data = {
                "cell_index": i,
                "temperature": initial_temperature,
                "boundary_faces": [],
            }
            #['Fixed Temperature', 'Heat Flux', 'Convection']
            for k in range(len(self.mesh[i]['faces'])):
                for l in range(len(self.boundary_condition_attributes)):
                    if self.mesh[i]['faces'][k]['bc'] == self.boundary_condition_attributes[l][0]:
                        bc_type = self.boundary_condition_attributes[l][1]['type']
                        if bc_type == 'Fixed Temperature':
                            boundary_face = {
                                "location": (i,k), #Cell, Face
                                "temperature": self.boundary_condition_attributes[l][1]['T-surf'],
                            }
                            initial_data['boundary_faces'].append(boundary_face)
                        if bc_type == 'Heat Flux' or bc_type == 'Convection':
                            boundary_face = {
                                "location": (i,k), #Cell, Face
                                "temperature": initial_temperature,
                            }
                            initial_data['boundary_faces'].append(boundary_face)
            self.solution.append(initial_data)
        return "Solution Initialized"

    def solve_case(self):
        """Assigns cells to processors and calculates residuals."""
        num_cells = len(self.mesh)
        num_cores = os.cpu_count()-1
        max_cores = np.floor(len(self.mesh)/100)
        if max_cores < 1:
            max_cores = 1
        if max_cores < num_cores:
            num_cores = int(max_cores)
        input_values = []
        for i in range(num_cores):
            start_cell = int(i*np.floor(num_cells/num_cores))
            end_cell = int((i+1)*np.floor(num_cells/num_cores))
            if i == num_cores-1:
                end_cell = num_cells
            cell_range = (start_cell, end_cell)
            input_values.append(cell_range)
        with mp.Pool(processes=num_cores) as pool:
            result = pool.map(self.solve_iteration_multi,input_values)
            residuals = [
                index[0]
                for index in result
            ]
            solution = [
                index[1]
                for index in result
            ]
            total_solution = []
            for m in range(len(input_values)):
                this_start_cell = input_values[m][0]
                this_end_cell = input_values[m][1]
                for n in range(len(solution[m])):
                    if n >= this_start_cell and n < this_end_cell:
                        total_solution.append(solution[m][n])
            self.solution = total_solution
            this_residual= 0  
            for j in range(len(residuals)):
                this_residual = this_residual + residuals[j]
            return this_residual / len(self.mesh)      

    def solve_iteration_multi(self, cell_range):
        """Solves the cells in the input range."""
        start_cell = cell_range[0]
        end_cell = cell_range[1]
        temperature_delta = 0.00001
        residual = 0
        #Iterate through the cell in the range.
        this_solution = [
            cell
            for cell in self.solution
        ]
        for i in range(len(self.mesh)):
            if i >= start_cell and i < end_cell:
                heat_flux, this_solution = self.solve_cell_heat_flux_multi(i,this_solution)  
                residual = residual + np.abs(heat_flux)
                this_solution[i]["temperature"] = this_solution[i]["temperature"] - temperature_delta
                heat_flux_1, this_solution = self.solve_cell_heat_flux_multi(i,this_solution)  
                this_solution[i]["temperature"] = this_solution[i]["temperature"] + 2*temperature_delta
                heat_flux_2, this_solution = self.solve_cell_heat_flux_multi(i,this_solution)  
                flux_gradient = (heat_flux_2-heat_flux_1)/(2*temperature_delta)
                this_solution[i]["temperature"] = this_solution[i]["temperature"] - temperature_delta
                new_temp_delta = self.relaxation_factor*heat_flux/flux_gradient
                this_solution[i]["temperature"] = this_solution[i]["temperature"] - new_temp_delta
        return [residual, this_solution]

    def solve_cell_heat_flux_multi(self, i, this_solution):
        heat_flux = 0
        #Iterate through the faces of each cell.
        for j in range(len(self.mesh[i]['faces'])):
            #Iterate through the boundary condition attributes and compare to each face
            for k in range(len(self.boundary_condition_attributes)):
                if self.mesh[i]['faces'][j]['bc'] == self.boundary_condition_attributes[k][0]:
                    #If there's a match, solve the flux through the face based on the boundary condition.
                    #['Fixed Temperature', 'Heat Flux', 'Convection']
                    if self.boundary_condition_attributes[k][1]['type'] == "Fixed Temperature":
                        cell_temperature = this_solution[i]['temperature']
                        cell_centroid = self.mesh[i]['centroid']
                        face_temperature = 0
                        for m in range(len(this_solution[i]['boundary_faces'])):
                            if this_solution[i]['boundary_faces'][m]['location'][1] == j:
                                face_temperature = this_solution[i]['boundary_faces'][m]['temperature']
                        face_area = self.mesh[i]['faces'][j]['area']
                        face_centroid = self.mesh[i]['faces'][j]['centroid']
                        distance = np.abs(geo.find_line_length([cell_centroid,face_centroid]))
                        this_flux = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/distance
                        heat_flux = heat_flux + this_flux
                    if self.boundary_condition_attributes[k][1]['type'] == "Heat Flux":
                        face_area = self.mesh[i]['faces'][j]['area']
                        face_centroid = self.mesh[i]['faces'][j]['centroid']
                        this_flux = face_area*self.boundary_condition_attributes[k][1]['H-flux']
                        heat_flux = heat_flux + this_flux
                        cell_centroid = self.mesh[i]['centroid']
                        distance = geo.find_line_length([face_centroid, cell_centroid])
                        cell_temperature = this_solution[i]['temperature']
                        face_temperature = this_flux*distance/(self.thermal_conductivity*face_area)+cell_temperature
                        for m in range(len(this_solution[i]['boundary_faces'])):
                            if this_solution[i]['boundary_faces'][m]['location'][1] == j:
                                this_solution[i]['boundary_faces'][m]['temperature'] = face_temperature                       
                    if self.boundary_condition_attributes[k][1]['type'] == "Convection":
                        face_temperature = 0
                        for m in range(len(this_solution[i]['boundary_faces'])):
                            if this_solution[i]['boundary_faces'][m]['location'][1] == j:
                                face_temperature = this_solution[i]['boundary_faces'][m]['temperature']                                
                        face_area = self.mesh[i]['faces'][j]['area']
                        h_conv = self.boundary_condition_attributes[k][1]["H-conv"]
                        t_infinity = self.boundary_condition_attributes[k][1]["T-inf"]
                        
                        face_centroid = self.mesh[i]['faces'][j]['centroid']
                        cell_temperature = this_solution[i]['temperature']
                        cell_centroid = self.mesh[i]['centroid']
                        cell_distance = geo.find_line_length([cell_centroid,face_centroid])
                        error = 99999
                        face_delta = 0.00001
                        relaxation = 0.1
                        #while error > 1E-8:
                        #for p in range(10000):
                        boundary_flux = face_area*h_conv*(t_infinity - face_temperature)
                            #cell_flux = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/cell_distance
                            #error = np.abs(boundary_flux-cell_flux)
                            #if error < 1E-6:
                            #    break
                            #face_temperature = face_temperature - face_delta
                            #boundary_flux_1 = face_area*h_conv*(t_infinity - face_temperature)
                            #cell_flux_1 = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/cell_distance
                            #error_1 = np.abs(boundary_flux_1-cell_flux_1)  
                            #face_temperature = face_temperature + 2*face_delta         
                            #boundary_flux_2 = face_area*h_conv*(t_infinity - face_temperature)
                            #cell_flux_2 = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/cell_distance
                            #error_2 = np.abs(boundary_flux_2-cell_flux_2)      
                            #face_temperature = face_temperature - face_delta
                            #derror_dtemp = (error_2 - error_1)/(2*face_delta)
                            #new_temp_delta = relaxation*error / derror_dtemp
                            #face_temperature = face_temperature - new_temp_delta 
                        #boundary_flux = face_area*h_conv*(t_infinity - face_temperature)
                        face_temperature = boundary_flux*cell_distance/(self.thermal_conductivity*face_area)+cell_temperature
                        for m in range(len(this_solution[i]['boundary_faces'])):
                            if this_solution[i]['boundary_faces'][m]['location'][1] == j:
                                this_solution[i]['boundary_faces'][m]['temperature'] = face_temperature                           
                        heat_flux = heat_flux + boundary_flux
            #If the boundary condition of the face is a neighboring cell, solve the thermal conduction through the face.
            if type(self.mesh[i]['faces'][j]['bc']) == tuple:
                cell_temperature = this_solution[i]['temperature']
                cell_centroid = self.mesh[i]['centroid']
                adjacent_location = self.mesh[i]['faces'][j]['bc']
                adjacent_temperature = 0
                adjacent_centroid = 0
                for n in range(len(self.mesh)):
                    if self.mesh[n]['location'] == adjacent_location:
                        adjacent_temperature = this_solution[n]['temperature']
                        adjacent_centroid = self.mesh[n]['centroid']
                        break
                face_area = self.mesh[i]['faces'][j]['area']
                distance = np.abs(geo.find_line_length([cell_centroid,adjacent_centroid]))
                this_flux = face_area*self.thermal_conductivity*(adjacent_temperature - cell_temperature)/distance
                heat_flux = heat_flux + this_flux  
        #Return the net heat flux into the cell
        return heat_flux, this_solution

    def solve_iteration(self, cell_range):
        """Solves the cells in the input range."""
        start_cell = cell_range[0]
        end_cell = cell_range[1]
        temperature_delta = 0.00001
        residual = 0
        #Iterate through the cell in the range.
        for i in range(len(self.mesh)):
            if i >= start_cell and i < end_cell:
                heat_flux = self.solve_cell_heat_flux(i)  
                residual = residual + np.abs(heat_flux)
                self.solution[i]["temperature"] = self.solution[i]["temperature"] - temperature_delta
                heat_flux_1 = self.solve_cell_heat_flux(i)
                self.solution[i]["temperature"] = self.solution[i]["temperature"] + 2*temperature_delta
                heat_flux_2 = self.solve_cell_heat_flux(i)
                flux_gradient = (heat_flux_2-heat_flux_1)/(2*temperature_delta)
                self.solution[i]["temperature"] = self.solution[i]["temperature"] - temperature_delta
                new_temp_delta = self.relaxation_factor*heat_flux/flux_gradient
                self.solution[i]["temperature"] = self.solution[i]["temperature"] - new_temp_delta
        return residual

    def solve_cell_heat_flux(self, i):
        heat_flux = 0
        #Iterate through the faces of each cell.
        for j in range(len(self.mesh[i]['faces'])):
            #Iterate through the boundary condition attributes and compare to each face
            for k in range(len(self.boundary_condition_attributes)):
                if self.mesh[i]['faces'][j]['bc'] == self.boundary_condition_attributes[k][0]:
                    #If there's a match, solve the flux through the face based on the boundary condition.
                    #['Fixed Temperature', 'Heat Flux', 'Convection']
                    if self.boundary_condition_attributes[k][1]['type'] == "Fixed Temperature":
                        cell_temperature = self.solution[i]['temperature']
                        cell_centroid = self.mesh[i]['centroid']
                        face_temperature = 0
                        for m in range(len(self.solution[i]['boundary_faces'])):
                            if self.solution[i]['boundary_faces'][m]['location'][1] == j:
                                face_temperature = self.solution[i]['boundary_faces'][m]['temperature']
                        face_area = self.mesh[i]['faces'][j]['area']
                        face_centroid = self.mesh[i]['faces'][j]['centroid']
                        distance = np.abs(geo.find_line_length([cell_centroid,face_centroid]))
                        this_flux = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/distance
                        heat_flux = heat_flux + this_flux
                    if self.boundary_condition_attributes[k][1]['type'] == "Heat Flux":
                        face_area = self.mesh[i]['faces'][j]['area']
                        face_centroid = self.mesh[i]['faces'][j]['centroid']
                        this_flux = face_area*self.boundary_condition_attributes[k][1]['H-flux']
                        heat_flux = heat_flux + this_flux
                        cell_centroid = self.mesh[i]['centroid']
                        distance = geo.find_line_length([face_centroid, cell_centroid])
                        cell_temperature = self.solution[i]['temperature']
                        face_temperature = this_flux*distance/(self.thermal_conductivity*face_area)+cell_temperature
                        for m in range(len(self.solution[i]['boundary_faces'])):
                            if self.solution[i]['boundary_faces'][m]['location'][1] == j:
                                self.solution[i]['boundary_faces'][m]['temperature'] = face_temperature                       
                    if self.boundary_condition_attributes[k][1]['type'] == "Convection":
                        face_temperature = 0
                        for m in range(len(self.solution[i]['boundary_faces'])):
                            if self.solution[i]['boundary_faces'][m]['location'][1] == j:
                                face_temperature = self.solution[i]['boundary_faces'][m]['temperature']                                
                        face_area = self.mesh[i]['faces'][j]['area']
                        h_conv = self.boundary_condition_attributes[k][1]["H-conv"]
                        t_infinity = self.boundary_condition_attributes[k][1]["T-inf"]
                        
                        face_centroid = self.mesh[i]['faces'][j]['centroid']
                        cell_temperature = self.solution[i]['temperature']
                        cell_centroid = self.mesh[i]['centroid']
                        cell_distance = geo.find_line_length([cell_centroid,face_centroid])
                        error = 99999
                        face_delta = 0.00001
                        relaxation = 0.1
                        #while error > 1E-8:
                        #for p in range(10000):
                        boundary_flux = face_area*h_conv*(t_infinity - face_temperature)
                            #cell_flux = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/cell_distance
                            #error = np.abs(boundary_flux-cell_flux)
                            #if error < 1E-6:
                            #    break
                            #face_temperature = face_temperature - face_delta
                            #boundary_flux_1 = face_area*h_conv*(t_infinity - face_temperature)
                            #cell_flux_1 = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/cell_distance
                            #error_1 = np.abs(boundary_flux_1-cell_flux_1)  
                            #face_temperature = face_temperature + 2*face_delta         
                            #boundary_flux_2 = face_area*h_conv*(t_infinity - face_temperature)
                            #cell_flux_2 = face_area*self.thermal_conductivity*(face_temperature - cell_temperature)/cell_distance
                            #error_2 = np.abs(boundary_flux_2-cell_flux_2)      
                            #face_temperature = face_temperature - face_delta
                            #derror_dtemp = (error_2 - error_1)/(2*face_delta)
                            #new_temp_delta = relaxation*error / derror_dtemp
                            #face_temperature = face_temperature - new_temp_delta 
                        #boundary_flux = face_area*h_conv*(t_infinity - face_temperature)
                        face_temperature = boundary_flux*cell_distance/(self.thermal_conductivity*face_area)+cell_temperature
                        for m in range(len(self.solution[i]['boundary_faces'])):
                            if self.solution[i]['boundary_faces'][m]['location'][1] == j:
                                self.solution[i]['boundary_faces'][m]['temperature'] = face_temperature                           
                        heat_flux = heat_flux + boundary_flux
            #If the boundary condition of the face is a neighboring cell, solve the thermal conduction through the face.
            if type(self.mesh[i]['faces'][j]['bc']) == tuple:
                cell_temperature = self.solution[i]['temperature']
                cell_centroid = self.mesh[i]['centroid']
                adjacent_location = self.mesh[i]['faces'][j]['bc']
                adjacent_temperature = 0
                adjacent_centroid = 0
                for n in range(len(self.mesh)):
                    if self.mesh[n]['location'] == adjacent_location:
                        adjacent_temperature = self.solution[n]['temperature']
                        adjacent_centroid = self.mesh[n]['centroid']
                        break
                face_area = self.mesh[i]['faces'][j]['area']
                if type(cell_centroid) != list or type(adjacent_centroid) != list:
                    print(f"cell centroid: {cell_centroid}; adjacent_centroid: {adjacent_centroid}")
                distance = np.abs(geo.find_line_length([cell_centroid,adjacent_centroid]))
                this_flux = face_area*self.thermal_conductivity*(adjacent_temperature - cell_temperature)/distance
                heat_flux = heat_flux + this_flux  
        #Return the net heat flux into the cell
        return heat_flux

    def get_solution_for_display(self):
        """Generates a surface for display."""

        max_temp = self.solution[0]['temperature']
        min_temp = self.solution[0]['temperature']
        average_temp = 0
        for i in range(len(self.solution)):
            average_temp = average_temp + self.solution[i]['temperature']
            if self.solution[i]['temperature'] > max_temp:
                max_temp = self.solution[i]['temperature']
            if self.solution[i]['temperature'] < min_temp:
                min_temp = self.solution[i]['temperature']
            for j in range(len(self.solution[i]['boundary_faces'])):
                if self.solution[i]['boundary_faces'][j]['temperature'] > max_temp:
                    max_temp = self.solution[i]['boundary_faces'][j]['temperature']
                if self.solution[i]['boundary_faces'][j]['temperature']  < min_temp:
                    min_temp = self.solution[i]['boundary_faces'][j]['temperature']
        average_temp = average_temp/len(self.solution)
        temp_range = max_temp - min_temp
        print(f"max_temp: {max_temp}")
        print(f"min_temp: {min_temp}")
        print(f"average_temp: {average_temp}")
        color_map = []
        face_mesh = []
        for k in range(len(self.solution)):

            for l in range(len(self.solution[k]['boundary_faces'])):
                this_face = []
                this_face_temp = self.solution[k]['boundary_faces'][l]['temperature']
                #print(this_face_temp)
                this_face_index = self.solution[k]['boundary_faces'][l]['location'][1]
                for point in self.mesh[k]['faces'][this_face_index]['face']:
                    this_face.append(point)
                triangularized_face = geo.convert_polyhedron_to_triangular_polyhedron([this_face])
                for triangle in triangularized_face:
                    color = (this_face_temp - min_temp) / temp_range
                    color_map.append(color)
                    face_mesh.append(triangle)

        return face_mesh, color_map, min_temp, max_temp        

    def add_boundary_condition(self, boundary_condition):
        """Adds a new boundary condition to the list of boundary conditions. Does not assign triangles or properties to the new boundary condition."""
        self.boundary_conditions.append(boundary_condition)
        self.added_boundary_conditions.append(boundary_condition)
        self.add_boundary_condition_attributes(boundary_condition, {
            "type": None,
            "T-surf": None, #Always in Kelvin
            "T-inf": None,  #Always in Kelvin
            "H-conv": None, #Always in W/m2-K
            "H-flux": None, #Always in W/m2
        })
        
    def remove_boundary_condition(self, boundary_condition):
        """Removes a boundary condition. All triangles assigned to the removed boundary condition will be reassigned to the unassigned boundary condition."""
        new_boundary_conditions = []
        for condition in self.boundary_conditions:
            if condition != boundary_condition:
                new_boundary_conditions.append(condition)
        self.boundary_conditions = new_boundary_conditions
        #reassign triangles from the deleted boundary condition to unassigned.
        new_triangles = []
        for triangle in self.triangles:
            if triangle[1] == boundary_condition:
                new_triangles.append([triangle[0],"unassigned"])
            else:
                new_triangles.append(triangle)
        self.triangles = new_triangles

    def add_boundary_condition_attributes(self, boundary_condition, attributes):
        """Defines the attributes of a specific boundary condition."""
        self.boundary_condition_attributes.append([boundary_condition,attributes])

    def update_boundary_condition_attributes(self, boundary_condition, attributes):
        """Updates the attributes of a specific boundary condition."""
        for i in range(len(self.boundary_condition_attributes)):
            if self.boundary_condition_attributes[i][0] == boundary_condition:
                self.boundary_condition_attributes[i][1] = attributes

    def move_triangles_to_boundary_condition(self, triangles, boundary_condition):
        """Assigns triangles to the selected boundary condition."""
        for triangle in triangles:
            self.triangles[triangle][1] = boundary_condition

    def check_stl_model(self):
        """Performs a check on the stl model to ensure it is manifold (watertight), determine the extents, and ensure all triangles have been assigned to a boundary condition.

        Returns a dictionary containing "is_manifold" (bool), extents (dict), and unassigned (bool).  
        """
        #print(self.stl_model)
        model = self.stl_model.vectors
        is_manifold = geo.check_if_manifold(model)
        extents = geo.find_model_extents(model)
        triangles = self.triangles
        unassigned = False
        for triangle in triangles:
            if triangle[1] == "unassigned":
                unassigned = True
        results = {
            "is_manifold": is_manifold,
            "extents": extents,
            "unassigned": unassigned,
        }
        return results
    
    def scale_model(self, scale):
        """Scales the model to meters."""
        model = self.stl_model.vectors
        points =self.stl_model.points
        new_model = []
        for i in range(len(model)):
            new_triangle = []
            for j in range(len(model[i])):
                new_point = []
                for k in range(len(model[i][j])):
                    coord = scale*model[i][j][k]
                    new_point.append(coord)
                new_triangle.append(new_point)
            new_model.append(new_triangle)
        self.stl_model.vectors = new_model
        new_points = []
        for m in range(len(points)):
            new_point = []
            for n in range(len(points[m])):
                coord = scale*points[m][n]
                new_point.append(coord)
            new_points.append(new_point)
        #self.stl_model.points = new_points

    def generate_mesh_multi(self, max_cell_size):
        base_mesh = self.generate_base_mesh_4(max_cell_size)
        num_cells = len(base_mesh)
        input_values = []
        num_cores = mp.cpu_count() - 1
        print(f"detected {num_cores+1} cores, using {num_cores}")
        for i in range(num_cores):
            start_cell = int(i*np.floor(num_cells/num_cores))
            end_cell = int((i+1)*np.floor(num_cells/num_cores))
            if i == num_cores-1:
                end_cell = num_cells
            cell_range = (start_cell, end_cell)
            input_values.append(cell_range)
        print(input_values)
        with mp.Pool(processes=num_cores) as pool:
            final_cells = pool.map(self.generate_mesh_4,input_values)
            final_mesh = []
            for j in range(len(final_cells)):
                for k in range(len(final_cells[j])):
                    final_mesh.append(final_cells[j][k])
            self.mesh = final_mesh
            return final_mesh

    def generate_base_mesh_4(self, max_cell_size):
        """Generates a base mesh for use with the generate_mesh_4 function."""
        model = self.stl_model.vectors #Vectors is a list of triangles
        model = geo.make_faces_inward_facing(model)
        #model = []
        #for face in model_32:
        #    new_face = geo.convert_coords_to_decimal(face)
        #    model.append(new_face)
        #model = geo.convert_coords_to_decimal
        extents = geo.find_model_extents(model)
        #Determine the number of base cells in each direction.
        Nx = math.ceil(extents['x_size']/(max_cell_size))
        Ny = math.ceil(extents['y_size']/(max_cell_size))
        Nz = math.ceil(extents['z_size']/(max_cell_size))
        print('Generating base mesh.')
        print(f"Nx: {Nx}; Ny: {Ny}; Nz: {Nz}")
        #Define the size of the base cells:
        x_size = extents['x_size']/Nx
        y_size = extents['y_size']/Ny
        z_size = extents['z_size']/Nz
        final_mesh = []
        cell = 0
        for i in range(Nx):
            
            for j in range(Ny):
                for k in range(Nz):
                    cell = cell + 1
                    x_min = extents['x_min']+x_size*i
                    x_max = x_min+x_size
                    y_min = extents['y_min']+y_size*j
                    y_max = y_min+y_size
                    z_min = extents['z_min']+z_size*k
                    z_max = z_min+z_size
                    new_base_cell = {
                        "faces":
                        [
                            {#Face 1
                                'face':[
                                [x_min,y_min,z_min],
                                [x_min,y_max,z_min],
                                [x_max,y_max,z_min],
                                [x_max,y_min,z_min],
                                ],
                                'bc':(i,j,k-1),
                            },
                            {#Face 2
                                'face':[
                                [x_min,y_min,z_min],
                                [x_min,y_min,z_max],
                                [x_max,y_min,z_max],
                                [x_max,y_min,z_min],
                                ],
                                'bc':(i,j-1,k),
                            },
                            {#Face 3
                                'face':[
                                [x_max,y_min,z_min],
                                [x_max,y_min,z_max],
                                [x_max,y_max,z_max],
                                [x_max,y_max,z_min],
                                ],
                                'bc':(i+1,j,k),
                            },
                            {#Face 4
                                'face':[
                                [x_max,y_max,z_min],
                                [x_max,y_max,z_max],
                                [x_min,y_max,z_max],
                                [x_min,y_max,z_min],
                                ],
                                'bc':(i,j+1,k),
                            },
                            {#Face 5
                                'face':[
                                [x_min,y_max,z_min],
                                [x_min,y_max,z_max],
                                [x_min,y_min,z_max],
                                [x_min,y_min,z_min],
                                ],
                                'bc':(i-1,j,k),
                            },
                            {#Face 6
                                'face':[
                                [x_min,y_min,z_max],
                                [x_min,y_max,z_max],
                                [x_max,y_max,z_max],
                                [x_max,y_min,z_max],
                                ],
                                'bc':(i,j,k+1)
                            },
                        ],
                        "location": (i,j,k),
                        }
                    final_mesh.append(new_base_cell)
        self.base_mesh = final_mesh
        return final_mesh

    def generate_mesh_4(self, cell_range):
        """Generates a hexahedral dominant polyhedral mesh for finite volume calculations based on the stl file input and maximum allowable cell size."""
        model = self.stl_model.vectors #Vectors is a list of triangles
        #model = geo.make_faces_inward_facing(model)
        #cell_range is a tuple or list containing a range.
        base_mesh = self.base_mesh
        if base_mesh== None:
            print("Error: No base mesh found. Generate a base mesh.")
        else:
            final_mesh = []
            start_cell = cell_range[0] #Equal to 0 for the first process
            end_cell = cell_range[1] #Equal to the number of cells in the mesh for the last process
            for i in range(len(base_mesh)):
                if i >= start_cell and i< end_cell:
                    points_inside_model = 0
                    this_base_cell = base_mesh[i]
                    print(f"Cell {i+1} of {len(base_mesh)}")
                    #Generate a new cell by cycling through the base cell faces and intesecting them with the model.
                    this_cell = {
                        "faces":[],
                        "location": this_base_cell['location'],
                        "centroid": "",
                        "volume": "",
                    }
                    #Iterate through the base cell faces and intersect them with the model.
                    for l in range(len(this_base_cell['faces'])):
                        this_base_face = this_base_cell['faces'][l]['face']
                        this_face = {
                            "face": [],
                            "bc": (this_base_cell['faces'][l]['bc']),
                            "area": "",
                            "centroid": "",
                        }
                        #Iterate through the base cell points and check if they are inside the model.
                        for m in range(len(this_base_face)):
                            this_base_point = this_base_face[m]
                            is_inside_model = geo.check_if_point_is_inside_polyhedron(model,this_base_point)
                            #if this_base_point == [25.0, -25.0, 50.0]:
                                #print(f"Base point inside model: {is_inside_model}")
                            #If the base point is inside the model, append it to the new face. If not, find the intersection points with the model along the edges of the base cell.
                            if is_inside_model:
                                points_inside_model = points_inside_model +1
                                this_face["face"].append(this_base_point)
                            else:
                                #print(f"Point {this_base_point} is outside the model.")
                                base_edge_1 = [
                                    this_base_face[m-1],
                                    this_base_face[m],
                                ]
                                base_edge_2 = []
                                if m < len(this_base_face)-1:
                                    #print(f"m: {m}; len_this_base_face: {len(this_base_face)}")
                                    base_edge_2 = [
                                        this_base_face[m],
                                        this_base_face[m+1]
                                    ]
                                else:
                                    base_edge_2 = [
                                        this_base_face[m],
                                        this_base_face[0]
                                    ]
                                #Cycle through the model triangles and find if any of them intersect the base edges with the base point outside the model.
                                for n in range(len(model)):
                                    plane_point_1 = geo.find_intersection_of_plane_and_line_segment(model[n],base_edge_1)
                                    plane_point_2 = geo.find_intersection_of_plane_and_line_segment(model[n],base_edge_2)
                                    #if n==8 and l == 5 and m ==3:
                                        #print(f"model[n]: {model[n]}")
                                        #print(this_base_face)
                                        #print(f"base_edge_1: {base_edge_1}")
                                        #print(f"plane_point_1: {plane_point_1}")
                                        #print(f"base_edge_2: {base_edge_2}")
                                        #print(f"plane_point_1: {plane_point_2}")
                                    tolerance = 1E0
                                    if type(plane_point_1) == list:
                                        in_polygon = geo.check_if_point_inside_polygon(model[n],plane_point_1)
                                        #if abs(plane_point_1[0]-12.5) < tolerance and abs(plane_point_1[1]+25) < tolerance and abs(plane_point_1[2]-50) < tolerance and in_polygon==True:
                                            #print(f"plane_point_1 in polygon {model[n]}, {in_polygon}")
                                        if in_polygon == True:
                                            this_face['face'].append(plane_point_1)
                                        #else:
                                        #    print(f"plane_point_1: {plane_point_1}; in_polygon: {in_polygon}")
                                    if type(plane_point_2) == list:
                                        #print(f"plane_point_2: {plane_point_2}")
                                        in_polygon = geo.check_if_point_inside_polygon(model[n],plane_point_2)
                                        #if abs(plane_point_2[0]-12.5) < tolerance and abs(plane_point_2[1]+25) < tolerance and abs(plane_point_2[2]-50) < tolerance and in_polygon==True:
                                            #print(f"plane_point_2 in polygon {model[n]}, {in_polygon}")
                                        if in_polygon == True:
                                            this_face['face'].append(plane_point_2)
                                        #else:
                                        #    print(f"plane_point_2: {plane_point_2}; in_polygon: {in_polygon}")
                        #Iterate through the model and find any faces that are coplanar and coicident with the base face. Apply the boundary condition if a coplanar face is found.
                        for p in range(len(model)):
                            coplanar_check = [
                                point
                                for point in this_base_face
                            ]
                            for point in model[p]:
                                coplanar_check.append(point)
                            is_coplanar = geo.check_if_polygon_is_coplanar(coplanar_check)    
                            if is_coplanar == True:
                                #Iterate through the points to check if one of them is on the base face but not on one of the lines.
                                on_base_face = False
                                for q in range(len(model[p])):
                                    on_line = False
                                    for pc in range(len(this_base_face)):
                                        line = [
                                            this_base_face[pc-1],
                                            this_base_face[pc],
                                        ]
                                        on_this_line = geo.is_this_point_on_this_segment(line, model[p][q])
                                        if on_this_line == True:
                                            on_line = True
                                    if on_line == False:
                                        on_face = geo.check_if_point_inside_polygon(this_base_face,model[p][q])
                                        if on_face == True:
                                            on_base_face = True
                                #Iterate through the base face to check if any of the points are on a model triangle but not on one of the edges.
                                for pb in range(len(this_base_face)):
                                    on_line = False
                                    for pc in range(len(model[p])):
                                        line = [
                                            model[p][pc-1],
                                            model[p][pc],
                                        ]
                                        on_this_line = geo.is_this_point_on_this_segment(line,this_base_face[pb])
                                        if on_this_line == True:
                                            on_line = True
                                    if on_line == False:
                                        on_face = geo.check_if_point_inside_polygon(model[p],this_base_face[pb])
                                        if on_face == True:
                                            on_base_face = True
                                #Check the centroid of the base face to see if it is inside one of the model faces.
                                base_face_centroid = geo.find_centroid_of_polygon(this_base_face)

                                on_face = geo.check_if_point_inside_polygon(model[p],base_face_centroid)
                                if on_face == True:
                                    on_base_face = True                                

                                if on_base_face == True:
                                    
                                    this_face['bc'] = self.triangles[p][1]
                            #elif is_coplanar==False:
                            #Find the intersection of any triangle edges with the base face and append.
                            for pa in range(len(model[p])):
                                this_triangle_line = [
                                    model[p][pa-1],
                                    model[p][pa],
                                ]
                                
                                intersection = geo.find_intersection_of_plane_and_line_segment(this_base_face[0:3],this_triangle_line)
                                
                                if type(intersection) == type([]):
                                    is_on_line = geo.is_this_point_on_this_segment(this_triangle_line,intersection)
                                    if is_on_line == True:
                                        on_this_face = geo.check_if_point_inside_polygon(this_base_face,intersection)
                                        if on_this_face == True:
                                            #print(f"Appending point {intersection} to cell {i}, face: {l} from Triangle {p}")
                                            this_face['face'].append(intersection)
                                    
                                for pb in range(len(this_base_face)):
                                    this_base_line = [
                                        this_base_face[pb-1],
                                        this_base_face[pb],
                                    ]
                                    intersection_2 = geo.find_lines_intersection(this_triangle_line, this_base_line)
                                    if type(intersection_2) == type([]):
                                        this_face['face'].append(intersection_2)

                            
                    
                            
                        this_face['face'] = geo.remove_duplicate_points(this_face['face'])
                        if len(this_face['face']) >= 3:
                            is_colinear = geo.check_if_polygon_is_colinear(this_face['face'])
                            if is_colinear == False:
                                this_face['face'] = geo.unfold_polygon_points(this_face['face'])
                                #if type(this_face['face']) != type([]):
                                #    print(f"cell {i} face {l}: {this_face['face']}")
                                this_face['area'] = geo.find_polygon_area(this_face['face'])
                                this_face['centroid'] = geo.find_centroid_of_polygon(this_face['face'])
                                this_cell['faces'].append(this_face)
                    if points_inside_model <24 and points_inside_model !=0:
                        #Convert the base cell to a polyhedron so the points can be checked if inside.
                        base_polyhedron = []
                        for u in range(len(this_base_cell['faces'])):
                            base_polyhedron.append(this_base_cell['faces'][u]['face'])
                        #Iterate through the model again and find any model faces that lie inside the base cell and find the intersection.
                        for r in range(len(model)):
                            #First check if the model triangle is coplanar with any of the base faces and discard if so.
                            triangle_coplanar = False

                            for x in range(len(base_polyhedron)):
                                coplanar_check = [
                                    point
                                    for point in base_polyhedron[x]
                                ]
                        
                                for point in model[r]:
                                    coplanar_check.append(point)
                                is_coplanar = geo.check_if_polygon_is_coplanar(coplanar_check)  
                                if is_coplanar == True:
                                    #print(f'Triangle: {r} has a coplanar match and is being excluded.')
                                    triangle_coplanar = True

                            if triangle_coplanar != True:
                                #print(f"Triangle {r} has no coplanar match and is being checked for inclusion.")
                                #print(f"Base Polygon: {base_polyhedron[2]}")
                                model_face = {
                                    "face": [],
                                    "bc": self.triangles[r][1]
                                }
                                for s in range(len(model[r])):
                                    point_in_base_cell = geo.check_if_point_is_inside_polyhedron(base_polyhedron,model[r][s])
                                    if point_in_base_cell == True:
                                        #print(f'Appending point: {model[r][s]}')
                                        model_face['face'].append(model[r][s])
                                #Find points where the triangle face intersects the edges of the base cell and append them to the new face
                                for v in range(len(base_polyhedron)):
                                    for w in range(len(base_polyhedron[v])):
                                        check_line = [
                                            base_polyhedron[v][w-1],
                                            base_polyhedron[v][w],
                                        ]
                                        model_intersection = geo.find_intersection_of_plane_and_line_segment(model[r],check_line)
                                        if type(model_intersection) == list:
                                            in_triangle = geo.check_if_point_inside_polygon(model[r],model_intersection)
                                            if in_triangle == True:
                                                model_face['face'].append(model_intersection)
                                            else:
                                                if r == 7 and abs(model_intersection[0] - 15) <0.1 and abs(model_intersection[1] +5) <0.1 and abs(model_intersection[2]- 47.5)<0.1:
                                                    print(f"in_triangle: {in_triangle}; model_intersection: {model_intersection}; triangle: {r}")
                                #Find points where the triangle edges intersect the faces of the base cell and append them to the new face
                                for f in range(len(base_polyhedron)):
                                    for w in range(len(model[r])):
                                        check_line = [
                                            model[r][w-1],
                                            model[r][w],
                                        ]
                                        model_intersection = geo.find_intersection_of_plane_and_line_segment(base_polyhedron[f],check_line)
                                        if type(model_intersection) == list:
                                            in_triangle = geo.check_if_point_inside_polygon(base_polyhedron[f],model_intersection)
                                            if in_triangle == True:
                                                model_face['face'].append(model_intersection)
                                model_face['face'] = geo.remove_duplicate_points(model_face['face'])
                                if len(model_face['face'])>=3:
                                    model_face['face'] = geo.unfold_polygon_points(model_face['face'])
                                    model_face['area'] = geo.find_polygon_area(model_face['face'])
                                    model_face['centroid'] = geo.find_centroid_of_polygon(model_face['face'])
                                    this_cell['faces'].append(model_face)
                    #TO DO: Makes normals inward facing.
                    if len(this_cell['faces'])>=4:
                        this_polyhedron = []
                        for b in range(len(this_cell['faces'])):
                            this_polyhedron.append(this_cell['faces'][b]['face'])
                        watertight = geo.check_if_polyhedral_cell_is_manifold(this_cell)
                        if watertight == False:
                            print(f"Warning: Base Cell {i}: Non-watertight polyhedron detected and is being excluded.")
                            #print(this_cell)
                        else:
                        #Only if watertight:
                            this_cell = geo.make_cell_faces_inward_facing(this_cell)
                            this_cell['centroid'] = geo.find_centroid_of_polyhedron(this_polyhedron)
                            this_cell['volume'] = geo.find_volume_of_polyhedron(this_polyhedron)
                            final_mesh.append(this_cell)     
        #self.mesh = final_mesh 
        return final_mesh     

    def generate_mesh_3(self, max_cell_size):
        """DEPRECIATED. Works but doesn't include all necesarry info. Saving as backup.
        Generates a hexahedral dominant polyhedral mesh for finite volume calculations based on the stl file input and maximum allowable cell size."""
        model = self.stl_model.vectors #Vectors is a list of triangles
        model = geo.make_faces_inward_facing(model)
        #model = []
        #for face in model_32:
        #    new_face = geo.convert_coords_to_decimal(face)
        #    model.append(new_face)
        #model = geo.convert_coords_to_decimal
        extents = geo.find_model_extents(model)
        #Determine the number of base cells in each direction.
        Nx = math.ceil(extents['x_size']/(max_cell_size))
        Ny = math.ceil(extents['y_size']/(max_cell_size))
        Nz = math.ceil(extents['z_size']/(max_cell_size))
        print(f"Nx: {Nx}; Ny: {Ny}; Nz: {Nz}")
        #Define the size of the base cells:
        x_size = extents['x_size']/Nx
        y_size = extents['y_size']/Ny
        z_size = extents['z_size']/Nz
        final_mesh = []
        cell = 0
        for i in range(Nx):
            
            for j in range(Ny):
                for k in range(Nz):
                    cell = cell + 1
                    print(f"Cell {cell} of {Nx*Ny*Nz}")
                    x_min = extents['x_min']+x_size*i
                    x_max = x_min+x_size
                    y_min = extents['y_min']+y_size*j
                    y_max = y_min+y_size
                    z_min = extents['z_min']+z_size*k
                    z_max = z_min+z_size
                    new_base_cell = {
                        "faces":
                        [
                            {#Face 1
                                'face':[
                                [x_min,y_min,z_min],
                                [x_min,y_max,z_min],
                                [x_max,y_max,z_min],
                                [x_max,y_min,z_min],
                                ],
                                'bc':(i,j,k-1),
                            },
                            {#Face 2
                                'face':[
                                [x_min,y_min,z_min],
                                [x_min,y_min,z_max],
                                [x_max,y_min,z_max],
                                [x_max,y_min,z_min],
                                ],
                                'bc':(i,j-1,k),
                            },
                            {#Face 3
                                'face':[
                                [x_max,y_min,z_min],
                                [x_max,y_min,z_max],
                                [x_max,y_max,z_max],
                                [x_max,y_max,z_min],
                                ],
                                'bc':(i+1,j,k),
                            },
                            {#Face 4
                                'face':[
                                [x_max,y_max,z_min],
                                [x_max,y_max,z_max],
                                [x_min,y_max,z_max],
                                [x_min,y_max,z_min],
                                ],
                                'bc':(i,j+1,k),
                            },
                            {#Face 5
                                'face':[
                                [x_min,y_max,z_min],
                                [x_min,y_max,z_max],
                                [x_min,y_min,z_max],
                                [x_min,y_min,z_min],
                                ],
                                'bc':(i-1,j,k),
                            },
                            {#Face 6
                                'face':[
                                [x_min,y_min,z_max],
                                [x_min,y_max,z_max],
                                [x_max,y_max,z_max],
                                [x_max,y_min,z_max],
                                ],
                                'bc':(i,j,k+1)
                            },
                        ],
                        "location": (i,j,k),
                        }
                    #Generate a new cell by cycling through the base cell faces and intesecting them with the model.
                    this_cell = {
                        "faces":[],
                        "location": (i,j,k),
                    }
                    #Iterate through the base cell faces and intersect them with the model.
                    for l in range(len(new_base_cell['faces'])):
                        this_base_face = new_base_cell['faces'][l]['face']
                        this_face = {
                            "face": [],
                            "bc": (new_base_cell['faces'][l]['bc']),
                        }
                        #Iterate through the base cell points and check if they are inside the model.
                        for m in range(len(this_base_face)):
                            this_base_point = this_base_face[m]
                            is_inside_model = geo.check_if_point_is_inside_polyhedron(model,this_base_point)
                            #if this_base_point == [25.0, -25.0, 50.0]:
                                #print(f"Base point inside model: {is_inside_model}")
                            #If the base point is inside the model, append it to the new face. If not, find the intersection points with the model along the edges of the base cell.
                            if is_inside_model:
                                this_face["face"].append(this_base_point)
                            else:
                                #print(f"Point {this_base_point} is outside the model.")
                                base_edge_1 = [
                                    this_base_face[m-1],
                                    this_base_face[m],
                                ]
                                base_edge_2 = []
                                if m < len(this_base_face)-1:
                                    #print(f"m: {m}; len_this_base_face: {len(this_base_face)}")
                                    base_edge_2 = [
                                        this_base_face[m],
                                        this_base_face[m+1]
                                    ]
                                else:
                                    base_edge_2 = [
                                        this_base_face[m],
                                        this_base_face[0]
                                    ]
                                #Cycle through the model triangles and find if any of them intersect the base edges with the base point outside the model.
                                for n in range(len(model)):
                                    plane_point_1 = geo.find_intersection_of_plane_and_line_segment(model[n],base_edge_1)
                                    plane_point_2 = geo.find_intersection_of_plane_and_line_segment(model[n],base_edge_2)
                                    #if n==8 and l == 5 and m ==3:
                                        #print(f"model[n]: {model[n]}")
                                        #print(this_base_face)
                                        #print(f"base_edge_1: {base_edge_1}")
                                        #print(f"plane_point_1: {plane_point_1}")
                                        #print(f"base_edge_2: {base_edge_2}")
                                        #print(f"plane_point_1: {plane_point_2}")
                                    tolerance = 1E0
                                    if type(plane_point_1) == list:
                                        in_polygon = geo.check_if_point_inside_polygon(model[n],plane_point_1)
                                        #if abs(plane_point_1[0]-12.5) < tolerance and abs(plane_point_1[1]+25) < tolerance and abs(plane_point_1[2]-50) < tolerance and in_polygon==True:
                                            #print(f"plane_point_1 in polygon {model[n]}, {in_polygon}")
                                        if in_polygon == True:
                                            this_face['face'].append(plane_point_1)
                                        #else:
                                        #    print(f"plane_point_1: {plane_point_1}; in_polygon: {in_polygon}")
                                    if type(plane_point_2) == list:
                                        #print(f"plane_point_2: {plane_point_2}")
                                        in_polygon = geo.check_if_point_inside_polygon(model[n],plane_point_2)
                                        #if abs(plane_point_2[0]-12.5) < tolerance and abs(plane_point_2[1]+25) < tolerance and abs(plane_point_2[2]-50) < tolerance and in_polygon==True:
                                            #print(f"plane_point_2 in polygon {model[n]}, {in_polygon}")
                                        if in_polygon == True:
                                            this_face['face'].append(plane_point_2)
                                        #else:
                                        #    print(f"plane_point_2: {plane_point_2}; in_polygon: {in_polygon}")
                        #Iterate through the model and find any faces that are coplanar and coicident with the base face. Apply the boundary condition if a coplanar face is found.
                        for p in range(len(model)):
                            coplanar_check = [
                                point
                                for point in this_base_face
                            ]
                            for point in model[p]:
                                coplanar_check.append(point)
                            is_coplanar = geo.check_if_polygon_is_coplanar(coplanar_check)    
                            if is_coplanar == True:
                                #Iterate through the points to check if one of them is on the base face.
                                on_base_face = False
                                for q in range(len(model[p])):
                                    on_base_face = geo.check_if_point_inside_polygon(this_base_face,model[p][q])
                                if on_base_face == True:
                                    this_face['bc'] = self.triangles[p][1]
                            
                    
                            
                        this_face['face'] = geo.remove_duplicate_points(this_face['face'])
                        if len(this_face['face']) >= 3:
                            this_face['face'] = geo.unfold_polygon_points(this_face['face'])
                            this_cell['faces'].append(this_face)

                    #Convert the base cell to a polyhedron so the points can be checked if inside.
                    base_polyhedron = []
                    for u in range(len(new_base_cell['faces'])):
                        base_polyhedron.append(new_base_cell['faces'][u]['face'])
                    #Iterate through the model again and find any model faces that lie inside the base cell and find the intersection.
                    for r in range(len(model)):
                        #First check if the model triangle is coplanar with any of the base faces and discard if so.
                        triangle_coplanar = False

                        for x in range(len(base_polyhedron)):
                            coplanar_check = [
                                point
                                for point in base_polyhedron[x]
                            ]
                    
                            for point in model[r]:
                                coplanar_check.append(point)
                            is_coplanar = geo.check_if_polygon_is_coplanar(coplanar_check)  
                            if is_coplanar == True:
                                #print(f'Triangle: {r} has a coplanar match and is being excluded.')
                                triangle_coplanar = True

                        if triangle_coplanar != True:
                            #print(f"Triangle {r} has no coplanar match and is being checked for inclusion.")
                            #print(f"Base Polygon: {base_polyhedron[2]}")
                            model_face = {
                                "face": [],
                                "bc": self.triangles[r][1]
                            }
                            for s in range(len(model[r])):
                                point_in_base_cell = geo.check_if_point_is_inside_polyhedron(base_polyhedron,model[r][s])
                                if point_in_base_cell == True:
                                    #print(f'Appending point: {model[r][s]}')
                                    model_face['face'].append(model[r][s])
                            #Find points where the triangle face intersects the edges of the base cell and append them to the new face
                            for v in range(len(base_polyhedron)):
                                for w in range(len(base_polyhedron[v])):
                                    check_line = [
                                        base_polyhedron[v][w-1],
                                        base_polyhedron[v][w],
                                    ]
                                    model_intersection = geo.find_intersection_of_plane_and_line_segment(model[r],check_line)
                                    if type(model_intersection) == list:
                                        in_triangle = geo.check_if_point_inside_polygon(model[r],model_intersection)
                                        if in_triangle == True:
                                            model_face['face'].append(model_intersection)
                                        else:
                                            if r == 7 and abs(model_intersection[0] - 15) <0.1 and abs(model_intersection[1] +5) <0.1 and abs(model_intersection[2]- 47.5)<0.1:
                                                print(f"in_triangle: {in_triangle}; model_intersection: {model_intersection}; triangle: {r}")
                            #Find points where the triangle edges intersect the faces of the base cell and append them to the new face
                            for f in range(len(base_polyhedron)):
                                for w in range(len(model[r])):
                                    check_line = [
                                        model[r][w-1],
                                        model[r][w],
                                    ]
                                    model_intersection = geo.find_intersection_of_plane_and_line_segment(base_polyhedron[f],check_line)
                                    if type(model_intersection) == list:
                                        in_triangle = geo.check_if_point_inside_polygon(base_polyhedron[f],model_intersection)
                                        if in_triangle == True:
                                            model_face['face'].append(model_intersection)
                            model_face['face'] = geo.remove_duplicate_points(model_face['face'])
                            if len(model_face['face'])>=3:
                                model_face['face'] = geo.unfold_polygon_points(model_face['face'])
                                this_cell['faces'].append(model_face)
                    #TO DO: Makes normals inward facing.
                    if len(this_cell['faces'])>=4:
                        final_mesh.append(this_cell)     
        self.mesh = final_mesh 
        return final_mesh      

    def generate_mesh_2(self, max_cell_size):
        """DEPRECIATED. Doesn't work.
        Generates a hexahedral dominant polyhedral mesh for finite volume calculations based on the stl file input and maximum allowable cell size."""
        model = self.stl_model.vectors #Vectors is a list of triangles
        #model = []
        #for face in model_32:
        #    new_face = geo.convert_coords_to_decimal(face)
        #    model.append(new_face)
        #model = geo.convert_coords_to_decimal
        extents = geo.find_model_extents(model)
        #Determine the number of base cells in each direction.
        Nx = math.ceil(extents['x_size']/(max_cell_size))
        Ny = math.ceil(extents['y_size']/(max_cell_size))
        Nz = math.ceil(extents['z_size']/(max_cell_size))
        print(f"Nx: {Nx}; Ny: {Ny}; Nz: {Nz}")
        #Define the size of the base cells:
        x_size = extents['x_size']/Nx
        y_size = extents['y_size']/Ny
        z_size = extents['z_size']/Nz
        final_mesh = []
        for i in range(Nx):
            
            for j in range(Ny):
                for k in range(Nz):
                    print(f"k: {k}")
                    print(f"""Cell {(i+1)*(j+1)*(k+1)} of {Nx*Ny*Nz}.""")
                    x_min = extents['x_min']+x_size*i
                    x_max = x_min+x_size
                    y_min = extents['y_min']+y_size*j
                    y_max = y_min+y_size
                    z_min = extents['z_min']+z_size*k
                    z_max = z_min+z_size
                    new_base_cell = {
                        "faces":
                        [
                            {#Face 1
                                'face':[
                                [x_min,y_min,z_min],
                                [x_min,y_max,z_min],
                                [x_max,y_max,z_min],
                                [x_max,y_min,z_min],
                                ],
                                'bc':(i,j,k-1),
                            },
                            {#Face 2
                                'face':[
                                [x_min,y_min,z_min],
                                [x_min,y_min,z_max],
                                [x_max,y_min,z_max],
                                [x_max,y_min,z_min],
                                ],
                                'bc':(i,j-1,k),
                            },
                            {#Face 3
                                'face':[
                                [x_max,y_min,z_min],
                                [x_max,y_min,z_max],
                                [x_max,y_max,z_max],
                                [x_max,y_max,z_min],
                                ],
                                'bc':(i+1,j,k),
                            },
                            {#Face 4
                                'face':[
                                [x_max,y_max,z_min],
                                [x_max,y_max,z_max],
                                [x_min,y_max,z_max],
                                [x_min,y_max,z_min],
                                ],
                                'bc':(i,j+1,k),
                            },
                            {#Face 5
                                'face':[
                                [x_min,y_max,z_min],
                                [x_min,y_max,z_max],
                                [x_min,y_min,z_max],
                                [x_min,y_min,z_min],
                                ],
                                'bc':(i-1,j,k),
                            },
                            {#Face 6
                                'face':[
                                [x_min,y_min,z_max],
                                [x_min,y_max,z_max],
                                [x_max,y_max,z_max],
                                [x_max,y_min,z_max],
                                ],
                                'bc':(i,j,k+1)
                            },
                        ],
                        "location": (i,j,k),
                        }
                    this_cell = {
                        "faces":[],
                        "location": (i,j,k),
                    }
                    these_faces = []
                    for t in range(len(new_base_cell['faces'])):
                        these_faces.append(new_base_cell['faces'][t]['face'])
                    #for each face in the base cell, check for coplanar faces in the model and include them if they are contained within the base cell face.
                    for base_face in new_base_cell['faces']:

                        #base_face['face']
                        num_coplanar = 0
                        for triangle_index in range(len(model)):
                            coplanar_check = [
                                point
                                for point in base_face['face']
                            ]
                            for point in model[triangle_index]:
                                coplanar_check.append(point)
                                
                            is_coplanar = geo.check_if_polygon_is_coplanar(coplanar_check)
                            #print(f"is_coplanar: {is_coplanar}")
                            boundary_condition = self.triangles[triangle_index][1]
                            if is_coplanar:
                                num_coplanar = num_coplanar + 1
                                
                                new_face = {
                                    'face':[],
                                    'bc': boundary_condition,                                   
                                }
                                #for the coplanar triangle from the model, find the intersection with the base face.
                                for h in range(len(model[triangle_index])):
                                    triangle_point = model[triangle_index][h]
                                    on_base_polygon = geo.check_if_point_inside_polygon(base_face['face'],triangle_point)
                                    if on_base_polygon:
                                        #print(f"appending triangle point: {triangle_point}")
                                        new_face['face'].append(triangle_point)
                                    else:
                                        line = [
                                            model[triangle_index][h-1],
                                            model[triangle_index][h],
                                        ]
                                        for l in range(len(base_face['face'])):
                                            line_2 = [
                                                base_face['face'][l-1],
                                                base_face['face'][l],
                                            ]
                                            intersection = geo.find_lines_intersection(line,line_2)
                                            if type(intersection)==list:
                                                #print(f'Appending intersection {intersection}')
                                                new_face['face'].append(intersection)
                                #for the base face, find the intersection with the model triangle.
                                for p in range(len(base_face['face'])):
                                    on_triangle = geo.check_if_point_inside_polygon(model[triangle_index],base_face['face'][p])
                                    if on_triangle:
                                        #print(f"on_triangle: {on_triangle}; Triangle: {model[triangle_index]}; Point: {base_face['face'][p]}")
                                        new_face['face'].append(base_face['face'][p])
                                #Remove duplicate points from the face
                                #print(f"new face: {new_face['face']}")
                                refined_new_face = geo.remove_duplicate_points(new_face['face'])
                                if len(refined_new_face) >=3:
                                    refined_new_face = geo.unfold_polygon_points(refined_new_face)
                                    #print(f"refined face: {refined_new_face}")
                                    if type(refined_new_face) == list:
                                        new_face['face'] = refined_new_face
                                        this_cell['faces'].append(new_face)
                        
                            


                    #If the face is not coplanar with a base cell face but all three points of the triangle are inside the base cell it should be included in the new cell.
                    new_face = {
                        "face":[],
                        "bc": boundary_condition,
                    }
                    for triangle_index in range(len(model)):
                        coplanar_check = [
                            point
                            for point in base_face['face']
                        ]
                        for point in model[triangle_index]:
                            coplanar_check.append(point)
                            
                        is_coplanar = geo.check_if_polygon_is_coplanar(coplanar_check)
                        if is_coplanar == False:

                            for r in range(len(model[triangle_index])):
                                in_base_cell = geo.check_if_point_is_inside_polyhedron(these_faces,model[triangle_index][r])
                                if in_base_cell:
                                    new_face['face'].append(model[triangle_index][r])
                                else:
                                    line_3 = [
                                        model[triangle_index][r-1],
                                        model[triangle_index][r]
                                    ]
                                    line_4 = [
                                        model[triangle_index][r-2],
                                        model[triangle_index][r]                                            
                                    ]
                                    for base_face in new_base_cell['faces']:
                                        intersection_3 = geo.find_intersection_of_plane_and_line_segment(base_face['face'],line_3)
                                        if type(intersection_3) == list:
                                            in_polygon = geo.check_if_point_inside_polygon(base_face['face'],intersection_3)
                                            if in_polygon:
                                                if intersection_3 == []:
                                                    print(f"Intersection3: {intersection_3}")
                                                new_face['face'].append(intersection_3)
                                        intersection_4 = geo.find_intersection_of_plane_and_line_segment(base_face['face'],line_4)
                                        if type(intersection_4) == list:
                                            in_polygon = geo.check_if_point_inside_polygon(base_face['face'],intersection_4)
                                            if in_polygon:
                                                if intersection_4 == []:
                                                    print(f"Intersection4: {intersection_4}")
                                                new_face['face'].append(intersection_4) 
                        
                        #for base_face in new_base_cell['faces']:
                        #    for y in range(len(base_face['face'])):
                        #        base_line = [
                        #            base_face['face'][y-1],
                        #            base_face['face'][y],
                        #        ]
                        #        base_intersection = geo.find_intersection_of_plane_and_line_segment(model[triangle_index],base_line)
                        #        if type(base_intersection) == list:
                        #            in_triangle = geo.check_if_point_inside_polygon(model[triangle_index],base_intersection)
                        #            if in_triangle:
                        #                new_face['face'].append(base_intersection)
                        refined_new_face = geo.remove_duplicate_points(new_face['face'])   
                        if len(new_face['face']) >=3:
                            
                            refined_new_face = geo.unfold_polygon_points(refined_new_face)
                            if type(refined_new_face) == list:
                                new_face['face'] = refined_new_face
                                this_cell['faces'].append(new_face)  
                        for t in range(len(base_face['face'])):
                            line_5 = [
                                base_face['face'][t-1],
                                base_face['face'][t],
                            ]
                                      
                        #If the base cell face is not coplanar with any triangle from the model, it is part of the interior and should be included in the new cell.
                        if num_coplanar == 0:
                            
                            
                            #print('Appending base face')
                            this_cell['faces'].append(base_face)
                        #print(f"num coplanar: {num_coplanar}; face: {base_face}")
                    final_mesh.append(this_cell)
        return final_mesh
                                                                        
    def generate_mesh(self, max_cell_size):
        """DEPRECIATED. Doesn't Work.
        Generates a hexahedral dominant polyhedral mesh for finite volume calculations based on the stl file input and maximum allowable cell size."""
        model_32 = self.stl_model.vectors #Vectors is a list of triangles
        model = []
        for face in model_32:
            new_face = geo.convert_coords_to_decimal(face)
            model.append(new_face)
        #model = geo.convert_coords_to_decimal
        extents = geo.find_model_extents(model)
        #Determine the number of base cells in each direction.
        Nx = math.ceil(extents['x_size']/dec(max_cell_size))
        Ny = math.ceil(extents['y_size']/dec(max_cell_size))
        Nz = math.ceil(extents['z_size']/dec(max_cell_size))
        #Define the size of the base cells:
        x_size = extents['x_size']/Nx
        y_size = extents['y_size']/Ny
        z_size = extents['z_size']/Nz
        final_mesh = []
        for i in range(Nx):
            print(f"""Cell {i*Ny*Nz} of {Nx*Ny*Nz}.""")
            for j in range(Ny):
                for k in range(Nz):
                    x_min = extents['x_min']+x_size*i
                    x_max = x_min+x_size
                    y_min = extents['y_min']+y_size*j
                    y_max = y_min+y_size
                    z_min = extents['z_min']+z_size*k
                    z_max = z_min+z_size
                    new_base_cell = [
                        [#Face 1
                            [x_min,y_min,z_min],
                            [x_min,y_max,z_min],
                            [x_max,y_max,z_min],
                            [x_max,y_min,z_min],
                        ],
                        [#Face 2
                            [x_min,y_min,z_min],
                            [x_min,y_min,z_max],
                            [x_max,y_min,z_max],
                            [x_max,y_min,z_min],
                        ],
                        [#Face 3
                            [x_max,y_min,z_min],
                            [x_max,y_min,z_max],
                            [x_max,y_max,z_max],
                            [x_max,y_max,z_min],
                        ],
                        [#Face 4
                            [x_max,y_max,z_min],
                            [x_max,y_max,z_max],
                            [x_min,y_max,z_max],
                            [x_min,y_max,z_min],
                        ],
                        [#Face 5
                            [x_min,y_max,z_min],
                            [x_min,y_max,z_max],
                            [x_min,y_min,z_max],
                            [x_min,y_min,z_min],
                        ],
                        [#Face 6
                            [x_min,y_min,z_max],
                            [x_min,y_max,z_max],
                            [x_max,y_max,z_max],
                            [x_max,y_min,z_max],
                        ],
                    ]
                    this_cell = []
                    for face in new_base_cell:
                        this_face = []
                        for l in range(len(face)):
                            print(f"""i,j,k,l: {i}; {j}; {k}; {l}""")
                            inside_model = geo.check_if_point_is_inside_polyhedron(model, face[l])
                            if inside_model == False:
                                for model_face in model:
                                    intersection = geo.find_intersection_of_plane_and_line_segment(model_face, [face[l-1],face[l]])
                                    if intersection:
                                        in_face = geo.check_if_point_inside_polygon(model_face, intersection)
                                        if in_face:
                                            this_face.append(intersection)
                                    intersection_2 = geo.find_intersection_of_plane_and_line_segment(model_face, [face[l-2],face[l]])
                                    if intersection_2:
                                        in_face = geo.check_if_point_inside_polygon(model_face, intersection_2)
                                        if in_face:
                                            this_face.append(intersection_2)   
                            else:
                                this_face.append(face[l])
                        if len(this_face) >= 3:
                            ordered_face = geo.unfold_polygon_points(this_face)
                            this_cell.append(ordered_face)  
                    for model_face in model:
                        for face in new_base_cell:
                            this_polygon = [
                                this_point
                                for this_point in model_face
                            ]
                            for another_point in face:
                                this_polygon.append(another_point)
                            is_coplanar = geo.check_if_polygon_is_coplanar(this_polygon)
                            if is_coplanar != True:
                                new_face = []
                                for p in range(len(model_face)):
                                    in_base_cell = geo.check_if_point_is_inside_polyhedron(new_base_cell, model_face[p])
                                    if in_base_cell:
                                        new_face.append(model_face[p])
                                        for base_cell_face in new_base_cell:
                                            intersection = geo.find_intersection_of_plane_and_line_segment(base_cell_face[0:3],[model_face[p-1],model_face[p]])
                                            if intersection:
                                                for point in new_face:
                                                    if intersection[0] != point[0] or intersection[1] != point[1] or intersection[2] != point[2]:
                                                        new_face.append(intersection)
                                            intersection_2 = geo.find_intersection_of_plane_and_line_segment(base_cell_face[0:3],[model_face[p-2],model_face[p]])
                                            if intersection_2:
                                                for point in new_face:
                                                    if intersection_2[0] != point[0] or intersection_2[1] != point[1] or intersection_2[2] != point[2]:
                                                        new_face.append(intersection_2)
                                new_face = geo.remove_duplicate_points(new_face)
                                if len(new_face) >= 3:
                                    
                                    unfolded_face = geo.unfold_polygon_points(new_face)
                                    
                                    this_cell.append(unfolded_face)
                                else:
                                    pass
                                    #print(f"new_face (477): {new_face}")
                    if len(this_cell)>=4:
                        print(f"this_cell: {this_cell}")
                        final_cell = geo.make_faces_inward_facing(this_cell)
                        final_mesh.append(final_cell)
        return final_mesh

    def generate_mesh_tetra(self, max_cell_size):
        """Generates a tetrahedral mesh over the problem domain."""
        tolerance = 1E-8
        #Combine coplanar coincident triangles in the model.
        combined_model = []
        triangle_indices = []
        working_model = [
            triangle
            for triangle in self.stl_model.vectors
        ]
        
        combined_model = geo.combine_adjacent_coplanar_triangles(working_model)
        #combined_model = geo.remove_duplicate_points(combined_model)
        #combined_model = geo.make_faces_inward_facing(combined_model)
        all_points = []
        #Fill the lines with points.
        line_points = []
        for i in range(len(combined_model)):
            for j in range(len(combined_model[i])):
                points = geo.add_extra_points_to_segment([combined_model[i][j-1],combined_model[i][j]],max_cell_size)
                for point in points:
                    all_points.append(point)
                    line_points.append(point)
        #Fill the faces with points.
        face_points = []
        for i in range(len(combined_model)):
            plane_equation = []
            #Iterate through the points to find the equation of the plane that the face lies in.
            for j in range(len(combined_model[i])):
                triangle = [
                    combined_model[i][j-2],
                    combined_model[i][j-1],
                    combined_model[i][j],
                ]
                is_colinear = geo.are_these_three_points_colinear(triangle)
                if is_colinear == False:
                    plane_equation = geo.find_equation_of_plane(combined_model[i])
                    break
            #Append the points of the face to all points.
            for y in range(len(combined_model[i])):
                all_points.append(combined_model[i][y])
            face_extents = geo.find_model_extents([combined_model[i]])
            n_x = 2
            n_y = 2
            n_z = 2
            if face_extents['x_size'] > tolerance:
                n_x = int(np.ceil(face_extents['x_size']/max_cell_size)) 
            if face_extents['y_size'] > tolerance:
                n_y = int(np.ceil(face_extents['y_size']/max_cell_size)) 
            if face_extents['z_size'] > tolerance:
                n_z = int(np.ceil(face_extents['z_size']/max_cell_size)) 
            #Generate points across the current face. 
            for k in range(n_x):
                for l in range(n_y):
                    for m in range(n_z):
                        x_dist = face_extents['x_size']/((n_x))*(k)
                        point_x = face_extents['x_min']+ x_dist
                        y_dist = face_extents['y_size']/((n_y))*(l)
                        point_y = face_extents['y_min']+ y_dist
                        z_dist = face_extents['z_size']/((n_z))*(m)
                        point_z = face_extents['z_min']+ z_dist
                        this_point = geo.project_point_onto_plane(plane_equation,[point_x,point_y,point_z])
                        is_on_face = geo.check_if_point_inside_polygon(combined_model[i],this_point)
                        if is_on_face == True:
                            min_dist = 1E9
                            for n in range(len(all_points)):
                                this_dist = geo.find_line_length([all_points[n],this_point])
                                if this_dist < min_dist:
                                    min_dist = this_dist
                            min_allowable_dist = max_cell_size/10
                            if min_dist >= min_allowable_dist:
                                all_points.append(this_point)
                            #    face_points.append(this_point)
        #Fill the volume with points. 
        model_extents = geo.find_model_extents(combined_model)
        n_x = 2
        n_y = 2
        n_z = 2
        if model_extents['x_size'] > tolerance:
            n_x = int(np.floor(model_extents['x_size']/max_cell_size))+1
        if model_extents['y_size'] > tolerance:
            n_y = int(np.floor(model_extents['y_size']/max_cell_size))+1
        if model_extents['z_size'] > tolerance:
            n_z = int(np.floor(model_extents['z_size']/max_cell_size))+1
        for k in range(n_x):
            for l in range(n_y):
                for m in range(n_z):
                    x_dist = model_extents['x_size']/(n_x)*(k)
                    point_x = model_extents['x_min']+ x_dist
                    y_dist = model_extents['y_size']/(n_y)*(l)
                    point_y = model_extents['y_min']+ y_dist
                    z_dist = model_extents['z_size']/(n_z)*(m)
                    point_z = model_extents['z_min']+ z_dist
                    this_point = [point_x,point_y,point_z]
                    is_in_model = geo.check_if_point_is_inside_polyhedron(working_model,this_point)
                    if is_in_model == True:
                        min_dist = 1E9
                        for n in range(len(all_points)):
                            this_dist = geo.find_line_length([all_points[n],this_point])
                            if this_dist < min_dist:
                                min_dist = this_dist
                        min_allowable_dist = max_cell_size/10
                        if min_dist >= min_allowable_dist:
                            all_points.append(this_point)
                        #    face_points.append(this_point)  
                    #else: 
                    #    print(f"point {this_point} is outside the model")
        #Remove duplicate points.
        all_points = geo.remove_duplicate_points(all_points)
            #print(plane_equation)
            #print(face_extents)
        print(len(all_points))

        return all_points
        #To be continued


#Section 5 Window Generator and Process Loop

window = sg.Window(title=program_title, layout= layout1, margins=(25,25)).Finalize()
figure = False
canvas = False
axes = False
delete_boundary = False
min_extent = 0
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "-Import_File_Button-":
        file = values["-Import_Filename_Input-"]
        if file !="":
            #Scale to mm
            scale = 1
            units = values['-Model_Units-']
            if units == "mm":
                scale =1
            elif units== "cm":
                scale = 10
            elif units== "m":
                scale = 1000
            elif units== "in":
                scale = 25.4
            elif units== "ft":
                scale = 3048
            this_analysis = analysis_case(file, scale)
            #print(this_analysis.stl_model.vectors)
            canvas, axes, figure = view_stl_part(this_analysis.stl_model.vectors, canvas, axes, figure, [])
            window['-Boundary_Conditions-'].update(values=this_analysis.boundary_conditions)
    elif event == "-Boundary_Conditions-":
        view_boundary_condition(values)
    elif event == "-Selected_Triangles-":
        selected_triangles = values['-Selected_Triangles-']
        canvas, axes, figure = view_stl_part(this_analysis.stl_model.vectors, canvas, axes, figure, selected_triangles)
    elif event == "-Select_All_Triangles_Button-":
        selected_triangles = select_all_triangles(values)
        canvas, axes, figure = view_stl_part(this_analysis.stl_model.vectors, canvas, axes, figure, selected_triangles)
    elif event == "-Add_To_Boundary_Dropdown-":
        print(values["-Add_To_Boundary_Dropdown-"])
    elif event == "-Add_Boundary_Button-":
        matching_boundary = False
        for condition in this_analysis.boundary_conditions:
            if values['-Add_Boundary_Input-'] == condition:
                matching_boundary = True
        if values['-Add_Boundary_Input-'] == '':
            window['-System_Messages-'].update("Please enter a boundary name to add a boundary.")
        elif matching_boundary:
            window['-System_Messages-'].update("That boundary condition already exists. Please choose a unique name.")
        else:
            this_analysis.add_boundary_condition(values['-Add_Boundary_Input-'])
            window['-Boundary_Conditions-'].update(this_analysis.boundary_conditions, set_to_index=[0])
            window['-Boundary_Condition_Attributes-'].update(this_analysis.added_boundary_conditions)
            boundary_condition_options = get_boundary_condition_options()
            window['-Add_To_Boundary_Dropdown-'].update(values=boundary_condition_options)
    elif event == "-Delete_Boundary_Button-":
        if values["-Boundary_Conditions-"][0] == "unassigned" or values["-Boundary_Conditions-"][0] == "all":
            window['-System_Messages-'].update(f"""Cannot remove boundary condition {values["-Boundary_Conditions-"][0]}. Please choose another boundary condition to delete.""")
        elif delete_boundary:
            this_analysis.remove_boundary_condition(values["-Boundary_Conditions-"][0])
            window['-Boundary_Conditions-'].update(this_analysis.boundary_conditions, set_to_index=[0])
            boundary_condition_options = get_boundary_condition_options()
            window['-Add_To_Boundary_Dropdown-'].update(values=boundary_condition_options)
            delete_boundary = False
        else:
            window['-System_Messages-'].update(f"""Click again to delete {values["-Boundary_Conditions-"][0]}""")
            delete_boundary = True
    elif event == "-Assign_To_Boundary_Condition_Button-":
        boundary_condition = values['-Add_To_Boundary_Dropdown-']
        triangles = values['-Selected_Triangles-']
        this_analysis.move_triangles_to_boundary_condition(triangles, boundary_condition)
        view_boundary_condition(values)
    elif event == "-Check_Case_Button-":
        model_check = this_analysis.check_stl_model()
        extents = (
            model_check['extents']['x_size'],
            model_check['extents']['y_size'],
            model_check['extents']['z_size'],
            )
        min_extent = min(extents)
        window['-Model_Extents_Display-'].update(f"""{model_check['extents']['x_size']} by {model_check['extents']['y_size']} {model_check['extents']['z_size']} units.""")
        manifold_message = ""
        assigned_message = ""
        ready_message = ""
        if model_check['is_manifold']:
            manifold_message = "Model is watertight and manifold. "
        else:
            manifold_message = "Warning: Non-watertight or non-manifold model detected. Please revise. "
        if model_check['unassigned']:
            assigned_message = "Error: Triangles must be assigned to a boundary condition. Please revise. "
        else:
            assigned_message = "All triangles have been assigned to boundary conditions. "
        if model_check['is_manifold'] and model_check['unassigned'] == False:
            ready_message = "Check complete. You may proceed with meshing."
            window['-Generate_Mesh_Button-'].update(disabled=False)
        window['-System_Messages-'].update(f"""{manifold_message}{assigned_message}{ready_message}""")
    elif event == "-Generate_Mesh_Button-" and __name__== "__main__":
        if values['-Mesh_Algorythm_Selector-'] == "Hexer":
            if values['-Max_Cell_Size_Input-']:
                cell_size_ok = True
                for i in range(len(values['-Max_Cell_Size_Input-'])):
                    if values['-Max_Cell_Size_Input-'][i] not in '0123456789.':
                        window['-System_Messages-'].update("Please enter a positive number in the max cell size field.")
                        cell_size_ok = False
                        break
                if cell_size_ok:
                    if min_extent >= float(values['-Max_Cell_Size_Input-']):
                        max_cell_size = float(values['-Max_Cell_Size_Input-'])
                        #base_mesh = this_analysis.generate_base_mesh_4(max_cell_size)
                        #generated_mesh = this_analysis.generate_mesh_4([0,len(base_mesh)])
                        generated_mesh = this_analysis.generate_mesh_multi(max_cell_size)
                        #print(generated_mesh)
                        display_cell = values['-View_Specific_Cell-']
                        if display_cell != 'all':
                            display_cell = int(display_cell)
                        prepared_mesh = prepare_mesh_for_display(generated_mesh, display_cell)
                        #print(prepared_mesh)
                        display_mesh = geo.convert_polyhedron_to_triangular_polyhedron(prepared_mesh)
                        #print(generated_mesh[display_cell])
                        canvas, axes, figure = view_stl_part(display_mesh, canvas, axes, figure, selected_triangles=[])
                    else:
                        window['-System_Messages-'].update(f"Max cell size must be less than minimum extent ({min_extent} units).")
            else:
                window['-System_Messages-'].update("Please enter a positive number in the max cell size field.")
        elif values['-Mesh_Algorythm_Selector-'] == "Tetra":
            #Check max cell size
            max_cell_size = float(values['-Max_Cell_Size_Input-'])
            #Run tetra algorythm
            generated_mesh = this_analysis.generate_mesh_tetra(max_cell_size)
            #display_mesh = geo.convert_polyhedron_to_triangular_polyhedron(generated_mesh)
            #canvas, axes, figure = view_stl_part(display_mesh, canvas, axes, figure, selected_triangles=[])
            canvas, axes, figure = view_scatter_plot(generated_mesh, canvas, axes, figure)
    elif event == "-View_Cell_Button-":
        display_cell = values['-View_Specific_Cell-']
        if display_cell != 'all':
            display_cell = int(display_cell)
        prepared_mesh = prepare_mesh_for_display(this_analysis.mesh, display_cell)
        display_mesh = geo.convert_polyhedron_to_triangular_polyhedron(prepared_mesh)
        canvas, axes, figure = view_stl_part(display_mesh, canvas, axes, figure, selected_triangles=[])
    elif event == "-Boundary_Condition_Attributes-":
        this_boundary_condition = values['-Boundary_Condition_Attributes-'][0]
        for i in range(len(this_analysis.boundary_condition_attributes)):
            if this_analysis.boundary_condition_attributes[i][0]==this_boundary_condition:
                if this_analysis.boundary_condition_attributes[i][1]['type']== None:
                    window['-Boundary_Type_Label-'].update(visible=True)
                    window['-Boundary_Condition_Type_Selector-'].update("", visible=True)
                    window["-T_Surface_Label-"].update(visible=False)
                    window["-T_Surface_Input-"].update(visible=False)
                    window["-T_Surf_Units-"].update(visible=False, set_to_index=[0])
                    window["-T_Infinity_Label-"].update(visible=False)
                    window["-T_Infinity_Input-"].update(visible=False)
                    window["-T_Infinity_Units-"].update(visible=False, set_to_index=[0])
                    window["-Convection_Coefficient_Label-"].update(visible=False)
                    window["-Convection_Coefficient_Input-"].update(visible=False)
                    window["-H_Convection_Units-"].update(visible=False, set_to_index=[0])
                    window["-Heat_Flux_Label-"].update(visible=False)
                    window["-Heat_Flux_Input-"].update(visible=False)
                    window["-Heat_Flux_Units-"].update(visible=False, set_to_index=[0])
                    window["-Set_Attributes_Button-"].update(visible=True)
                    break
                if this_analysis.boundary_condition_attributes[i][1]['type']== 'Fixed Temperature':
                    window['-Boundary_Type_Label-'].update(visible=True)
                    window['-Boundary_Condition_Type_Selector-'].update(visible=True, set_to_index=[0])
                    window["-T_Surface_Label-"].update(visible=True)
                    window["-T_Surface_Input-"].update(str(this_analysis.boundary_condition_attributes[i][1]['T-surf']), visible=True)
                    window["-T_Surf_Units-"].update(visible=True, set_to_index=[0])
                    window["-T_Infinity_Label-"].update(visible=False)
                    window["-T_Infinity_Input-"].update(visible=False)
                    window["-T_Infinity_Units-"].update(visible=False, set_to_index=[0])
                    window["-Convection_Coefficient_Label-"].update(visible=False)
                    window["-Convection_Coefficient_Input-"].update(visible=False)
                    window["-H_Convection_Units-"].update(visible=False, set_to_index=[0])
                    window["-Heat_Flux_Label-"].update(visible=False)
                    window["-Heat_Flux_Input-"].update(visible=False)
                    window["-Heat_Flux_Units-"].update(visible=False, set_to_index=[0])
                    window["-Set_Attributes_Button-"].update(visible=True)
                    break
                if this_analysis.boundary_condition_attributes[i][1]['type']== 'Heat Flux':
                    window['-Boundary_Type_Label-'].update(visible=True)
                    window['-Boundary_Condition_Type_Selector-'].update(visible=True, set_to_index=[1])
                    window["-T_Surface_Label-"].update(visible=False)
                    window["-T_Surface_Input-"].update(visible=False)
                    window["-T_Surf_Units-"].update(visible=False, set_to_index=[0])
                    window["-T_Infinity_Label-"].update(visible=False)
                    window["-T_Infinity_Input-"].update(visible=False)
                    window["-T_Infinity_Units-"].update(visible=False, set_to_index=[0])
                    window["-Convection_Coefficient_Label-"].update(visible=False)
                    window["-Convection_Coefficient_Input-"].update(visible=False)
                    window["-H_Convection_Units-"].update(visible=False, set_to_index=[0])
                    window["-Heat_Flux_Label-"].update(visible=True)
                    window["-Heat_Flux_Input-"].update(str(this_analysis.boundary_condition_attributes[i][1]['H-flux']*(1E6)), visible=True)
                    window["-Heat_Flux_Units-"].update(visible=True, set_to_index=[0])
                    window["-Set_Attributes_Button-"].update(visible=True)
                    break
                if this_analysis.boundary_condition_attributes[i][1]['type']== 'Convection':
                    window['-Boundary_Type_Label-'].update(visible=True)
                    window['-Boundary_Condition_Type_Selector-'].update(visible=True, set_to_index=[2])
                    window["-T_Surface_Label-"].update(visible=False)
                    window["-T_Surface_Input-"].update(visible=False)
                    window["-T_Surf_Units-"].update(visible=False, set_to_index=[0])
                    window["-T_Infinity_Label-"].update(visible=True)
                    window["-T_Infinity_Input-"].update(str(this_analysis.boundary_condition_attributes[i][1]['T-inf']), visible=True)
                    window["-T_Infinity_Units-"].update(visible=True, set_to_index=[0])
                    window["-Convection_Coefficient_Label-"].update(visible=True)
                    window["-Convection_Coefficient_Input-"].update(str(this_analysis.boundary_condition_attributes[i][1]['H-conv']*(1E6)), visible=True)
                    window["-H_Convection_Units-"].update(visible=True, set_to_index=[0])
                    window["-Heat_Flux_Label-"].update(visible=False)
                    window["-Heat_Flux_Input-"].update(visible=False)
                    window["-Heat_Flux_Units-"].update(visible=False, set_to_index=[0])
                    window["-Set_Attributes_Button-"].update(visible=True)
                    break
    elif event == "-Boundary_Condition_Type_Selector-":
        #['Fixed Temperature', 'Heat Flux', 'Convection']
        boundary_condition_type = values['-Boundary_Condition_Type_Selector-']
        this_boundary_condition = values['-Boundary_Condition_Attributes-'][0]
        if boundary_condition_type == 'Fixed Temperature':
            window["-T_Surface_Label-"].update(visible=True)
            window["-T_Surface_Input-"].update(visible=True)
            window["-T_Surf_Units-"].update(visible=True)
            window["-T_Infinity_Label-"].update(visible=False)
            window["-T_Infinity_Input-"].update(visible=False)
            window["-T_Infinity_Units-"].update(visible=False)
            window["-Convection_Coefficient_Label-"].update(visible=False)
            window["-Convection_Coefficient_Input-"].update(visible=False)
            window["-H_Convection_Units-"].update(visible=False)
            window["-Heat_Flux_Label-"].update(visible=False)
            window["-Heat_Flux_Input-"].update(visible=False)
            window["-Heat_Flux_Units-"].update(visible=False)
            window["-Set_Attributes_Button-"].update(visible=True)
        elif boundary_condition_type == 'Heat Flux':
            window["-T_Surface_Label-"].update(visible=False)
            window["-T_Surface_Input-"].update(visible=False)
            window["-T_Surf_Units-"].update(visible=False)
            window["-T_Infinity_Label-"].update(visible=False)
            window["-T_Infinity_Input-"].update(visible=False)
            window["-T_Infinity_Units-"].update(visible=False)
            window["-Convection_Coefficient_Label-"].update(visible=False)
            window["-Convection_Coefficient_Input-"].update(visible=False)
            window["-H_Convection_Units-"].update(visible=False)
            window["-Heat_Flux_Label-"].update(visible=True)
            window["-Heat_Flux_Input-"].update(visible=True)
            window["-Heat_Flux_Units-"].update(visible=True)
            window["-Set_Attributes_Button-"].update(visible=True)
        elif boundary_condition_type == 'Convection':
            window["-T_Surface_Label-"].update(visible=False)
            window["-T_Surface_Input-"].update(visible=False)
            window["-T_Surf_Units-"].update(visible=False)
            window["-T_Infinity_Label-"].update(visible=True)
            window["-T_Infinity_Input-"].update(visible=True)
            window["-T_Infinity_Units-"].update(visible=True)
            window["-Convection_Coefficient_Label-"].update(visible=True)
            window["-Convection_Coefficient_Input-"].update(visible=True)
            window["-H_Convection_Units-"].update(visible=True)
            window["-Heat_Flux_Label-"].update(visible=False)
            window["-Heat_Flux_Input-"].update(visible=False)
            window["-Heat_Flux_Units-"].update(visible=False)
            window["-Set_Attributes_Button-"].update(visible=True)
    elif event == "-Set_Attributes_Button-":
        boundary_condition = values['-Boundary_Condition_Attributes-'][0]
        bc_type = values['-Boundary_Condition_Type_Selector-']
        bc_tsurf = float(values['-T_Surface_Input-'])
        bc_tsurf_units = values['-T_Surf_Units-']
        bc_tsurf = convert_temperature_to_kelvin(bc_tsurf,bc_tsurf_units)
        bc_tinf = float(values['-T_Infinity_Input-'])
        bc_tinf_units = values['-T_Infinity_Units-']
        bc_tinf = convert_temperature_to_kelvin(bc_tinf,bc_tinf_units)
        bc_hconv = float(values['-Convection_Coefficient_Input-'])
        bc_hconv_units = values['-H_Convection_Units-']
        bc_hconv = convert_convection_coefficient_to_si(bc_hconv,bc_hconv_units)
        bc_hflux = float(values['-Heat_Flux_Input-'])
        bc_hflux_units = values['-Heat_Flux_Units-']
        bc_hflux = convert_heat_flux_units_to_si(bc_hflux,bc_hflux_units)
        for i in range(len(this_analysis.boundary_condition_attributes)):
            if this_analysis.boundary_condition_attributes[i][0] == boundary_condition:
                attributes = {
                    "type": bc_type,
                    "T-surf": bc_tsurf, #Always in Kelvin
                    "T-inf": bc_tinf,  #Always in Kelvin
                    "H-conv": bc_hconv, #Always in W/mm2-K
                    "H-flux": bc_hflux, #Always in W/mm2
                }
                this_analysis.boundary_condition_attributes[i][1] = attributes
                window['-System_Messages-'].update(f"Boundary Condition {this_analysis.boundary_condition_attributes[i][0]} attributes updated.")
    elif event== "-Thermal_Conduictivity_Button-":
        conductivity = float(values['-Thermal_Conductivity_Input-'])
        conductivity_units = values['-Thermal_Conductivity_Units-']
        conductivity = convert_thermal_conductivity_to_si(conductivity, conductivity_units)
        this_analysis.set_thermal_conductivity(conductivity)
        window['-System_Messages-'].update(f"Volume Condition updated with thermal conductivity {conductivity} W/m-K.")
    elif event=="-Set_Relaxation_Factor_Button-":
        relaxation = float(values['-Relaxation_Factor_Input-'])
        this_analysis.set_relaxation_factor(relaxation)
        window['-System_Messages-'].update(f"Relaxation factor set to {relaxation}.")
    elif event=="-Set_Max_Iterations_Button-":
        max_iterations = int(values['-Max_Iterations_Input-'])
        this_analysis.set_max_iterations(max_iterations)
        window['-System_Messages-'].update(f"Maximum Iterations set to {max_iterations}.")
    elif event=="-Set_Min_Residual_Button-":
        min_residual = float(values['-Min_Residual_Input-'])
        this_analysis.set_min_residual(min_residual)
        window['-System_Messages-'].update(f"Minimum Residual set to {min_residual}.")
    elif event=="-Initialize_Case_Button-":
        initial_temperature = float(values['-Initialize_Case_Input-'])
        initial_units = values['-Initial_T_Units-']
        initial_temperature = convert_temperature_to_kelvin(initial_temperature,initial_units)
        this_analysis.initialize_solution(initial_temperature)
        window['-System_Messages-'].update(f"Volume Condition initialized at {initial_temperature} K")
        window['-Solution_Message-'].update("Solution Available. Click to view.")
    elif event=="-Solve_Case_Button-":
        
        for i in range(this_analysis.max_iterations):
            residual = this_analysis.solve_case()
            #residual = this_analysis.solve_iteration([0,len(this_analysis.mesh)])/len(this_analysis.mesh)
            print(f"iteration: {i}; residual: {residual}")
            if residual < this_analysis.min_residual:
                break
    elif event=="-View_Solution_Button-":
        face_mesh, color_map, min_temp, max_temp = this_analysis.get_solution_for_display()
        canvas, axes, figure = view_solution(face_mesh, color_map, min_temp, max_temp, canvas, axes, figure)
window.close()