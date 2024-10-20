# Picante
World's Hottest Thermal Solver






Picante
A finite-volume solver for heat transfer in solids.















Joseph M. Basile
Pensive Lookout LLC

8/23/2023
Table of Contents
1 Introduction	3
2 Procedure	3
2.1 STL Import and Boundary Conditions	3
2.2 Mesh Generation	4
2.3 Case Setup	5
2.4 Run Case	6
2.5 Results	8
3. Limitations	9
3.1 Execution Speed	9
3.2 Slow Convergence	9
3.3 Model Complexity	9
3.4 Graphical Limitations	10
3.5 Single Volume Conditions	10
3.6 Save Case Files	10
4. Next Steps	10
4.1 Conversion of Algorithms to C	10
4.2 Improved Convergence	11
4.3 Improved Graphics Area	11
4.4 Save a Case	11
4.5 Multiple Volume Conditions	11
4.6 Radiation	11
4.7 Time-Accurate Solutions	11
5. Conclusion	11
6. References	12


Table of Figures

Figure 1: The Import STL tab showing boundary condition assignment.	4
Figure 2: A hexahedral mesh generated with the Hexer algorithm.	5
Figure 3: The Case Setup tab showing setup for a convection type boundary condition.	6
Figure 4: The Run Case tab showing solver setup.	8
Figure 5: A solution displayed with the temperature characteristics plotted to the console.	9

1	Introduction
Picante is a solver for simulating steady-state heat transfer in solids using the finite-volume method. It is in the early development phase. The software is written in Python and includes console output, a graphical user interface with a graphics area, and an STL file interpreter. 
2	Procedure
A typical analysis includes the following steps: import an STL file and assign boundary conditions, generate a mesh over the problem domain, set up the case, initialize and run the solution, and view the solution. 
2.1	STL Import and Boundary Conditions
Users can export an STL file from their CAD software and read it into the GUI on the Import STL tab. The file will be read in as a series of triangles and displayed in the graphics area. The user must then assign all triangles from the model to named boundary conditions. For instance, they can create a boundary condition called convection and then assign all of the triangle representing convecting surfaces to it. To help with workflow, the user has the option to select all unassigned triangles for assignment to the final boundary condition.

The program is designed to use SI units and the user should be careful to enter the model units before importing the STL file. Length units are converted to millimeters and all calculations are done in SI units. 



In this example case, the model is a 20 mm by 20 mm aluminum heat sink with 3 fins. Each fin is 4 mm wide and 12 mm tall. The base is 4 mm thick.

It is important to note that Figure 1 also shows the graphical limitations of the graphics area as described in Section 3.4.
2.2	Mesh Generation
Once all triangles have been assigned to boundary conditions, the user can proceed to the Generate Mesh Tab where they will have a choice of two algorithms. The first algorithm is called Tetra and generates a tetrahedral style mesh using a 3D Delaunay triangulation. The second algorithm is called Hexer and generates a hexehedral style mesh and is suitable only for simple geometries with regularly spaced features. 

Once the user has selected a meshing algorithm they should assign a maximum cell size appropriate to the problem at hand. It is recommended that the user enters a cell size of approximately half the length of the smallest edge in the model. This will ensure that a reasonably well resolved solution is found without causing unreasonably long solution times. 




Figure 2 shows a mesh that was generated using the hexer algorithm. Due to a limitation of the graphics area, (See section 3.4) quadrilateral cell faces must be decomposed into triangles for display, and a result show up as a series of triangular faces. This effect is graphical only and all cells generated with the Hexer algorithm are indeed hexahedral. 
2.3 	Case Setup
Once a mesh has been generated, the user can proceed to case setup. 

The first step in case setup is to assign a heat transfer coefficient for the material that the model is made of. The default value is 237 W/m-K which corresponds to aluminum.

All of the boundary conditions created as described in Section 2.1 will appear on the Case Setup tab. This menu allows the user to assign a boundary condition type to each boundary condition. 

The fixed temperature boundary condition type assigns a fixed temperature to the surface. 

The heat flux boundary condition type assigns a constant heat flux per area to the surface with a positive number representing heat flow into the domain. A heat flux of 0 watts/m2 can be assigned to represent an adiabatic condition. 

The convection boundary condition type assigns a bulk fluid temperature for the surrounding fluid and a convection coefficient representing the approximate amount of convection expected at the surface. A resource such as Reference [A] can be used to estimate convection coefficients for a wide range of physical phenomena.



In this example, the volume condition is configured for aluminum (237 W/m-K) while the bottom of the heat sink is assigned as a flux condition with 12,500 W/m2 of heating. Since the heat sink is 20 mm by 20 mm, the total heating is 5 Watts. The remaining surfaces, including all three fins, are assigned as convection with T∞ set to 300 K and the convection coefficient H set to 50 W/m2-K representing moderate forced convection in air. 
2.4 	Run Case
Once all boundary conditions have been assigned properties, the user can proceed with running their case from the Run Case tab. 

First the user must initialize the solution at a fixed temperature. The user can either initialize with the default setting of 300K or they can take some time to estimate an expected average temperature for their problem domain. Entering a reasonable predicted average temperature will speed convergence of the solution.

Once the solution has been initialized, the user should review and adjust the solver settings.

The relaxation factor is used to slow down the iteration scheme. The will help to stabilize convergence at the cost of requiring more iterations. 

It is recommended that the user starts off with a small number of iteration steps when they start a solution to ensure that all setup has been completed properly. Once the solver is shown to be converging, a larger number of iterations can be used. Iterations will always continue from the most recent solution unless the solution is reinitialized.

The residual is a measure of the average error across all the cells of the mesh. It is appropriate for the user to continue solving until the residual has reduced by at least several orders of magnitude. The default minimum residual of 1E-8 will ensure this condition is met in most cases. Users should note however that the solver will stop solving at the maximum iterations even if the minimum residual condition is not yet met. 

Finally, the user must select which solver to use when iterating. The Second Order solver approximates the temperature to flux relationship as a second order polynomial and performs best on problems involving fixed heat fluxes and convection. The First Order and First Order Dual solvers approximate the temperature to flux relationship as a first over polynomial (linear) and are most effective for problems involving fixed temperature surfaces. 

The solver will utilize up to N-1 processors when solving, greatly improving solution times when compared to serial processes. N represents the number of threads available on the system. The iteration numbers and corresponding residuals will print to the consol while the program is iterating.



In this example, the solution was initialized at 300 K. The relaxation factor was kept at the default of 0.7 and the minimum residual was kept at 1E-8. The Second Order solver was used. The solver was run for about 100,000 iterations across three sessions.
2.5	Results
Once a solution has been found, the user can review the temperatures on the surface of their model using the Results Tab. This will produce a colored plot with warmer temperatures showing up as warmer colors and cooler temperatures showing up as cooler colors. The high temperature, low temperature, and average temperature will plot to the console when the solution is displayed. 

In this example, the minimum temperature is 340.64 K while the maximum is 341.47 K. The average is 341.02 K. The heat flux residual was reduced to 8.0889E-7 after about 100,000 iterations.
3. 	Limitations
3.1	Execution Speed
The primary limitations of Picante are the meshing speed and the iteration speed, limiting the size and complexity of the problems that can be solved. This is believed to be due to the fundamental limitations of Python, which is a non-compiled scripting language that relies on an interpreter rather than direct hardware execution.
3.2	Slow Convergence
Despite using a Second-Order algorithm to iterate on the solution, the test case took over 100,000 iterations and the residual still did not meet the minimum residual setting of 1E-8.
3.3	Model Complexity
Both meshing algorithms have difficulties with large and complex geometry. This is partially due to limitation 3.1, as slow execution speeds limits the design cycle for the meshing algorithms and resulted in compromises being made in the interest of speed. Presently only small problems resulting is meshes of less than 1000 cells have been shown to run effectively on the software.
3.4	Graphical Limitations
The Picante GUI features a graphics area capable of displaying triangles with color-mapping. This makes it useful for displaying the STL model, the mesh, and the solution. However, it is based on the Python library matplotlib which is not hardware accelerated. As a result, it uses the Painter’s Algorithm to determine the “Z-sort” order of the triangles based on their centroids distance to the virtual camera. This algorithm is known to have severe limitations when rendering large number of triangles, resulting in graphical glitches as some triangles are erroneously determined to be behind others. This results in some triangles showing through the model when they should be obscured by closer triangles. 

Additionally, the lack of hardware acceleration significantly slows down rotation and panning when a large number of triangles are on the screen. To help mitigate this effect, only the outside surfaces of the mesh and solution models are displayed in the graphics area.
3.5	Single Volume Conditions
Presently, Picante can only compute a solution for a single volume condition. For instance, it can solve the temperature gradients through a heat sink but not the adjacent processor that is heating it up. This limits the classes of problems that can be solved and limits the practical use of the software for real-world applications.
3.6	Save Case Files
Presently Picante does not include the ability to save a case file. This limits the practical use of the software since shutting down the program erases the mesh and solution, forcing the user to start over after restarting.
4. 	Next Steps
Picante has been shown to converge on low-error solutions for small problems comprising less than 1000 cells. As shown in Figure 5, it is capable of computing temperature gradients across a 3D model of a heat sink, and therefore could become useful for heat sink design if the limitations discussed in Section 3 can be overcome. Practical steps toward that end include the following:
4.1	Conversion of Algorithms to C
Python is an effective language with processing large and complex data, but it does not perform well compared to compiled languages such as C and C++. Fortunately, Python includes a library called ctypes which allows for interaction with compiled libraries written in C. An effort is currently underway to convert the meshing and solver algorithms over to a compiled C library in order to speed up execution speed. This may greatly improve performance and reduce the need for imposing performance limitations as described in Section 3.3. As a result, it could open the software up to solving significantly more complex problems. 

4.2	Improved Convergence
It is possible that improvements could be made to the solver to reduce the number of iterations needed to achieve a converged solution. Further research on this topic is warranted.
4.3	Improved Graphics Area
The graphics area in Picante is practical but severely limited as described in Section 3.4. Converting the graphics area from matplotlib to a hardware accelerated option such as OpenGL could dramatically improve performance and reduce or eliminate graphical glitches associated with the painter’s algorithm. 
4.4	Save a Case
Before the software can be considered practical it must have a way to save case files so that users don’t need to start over after restarting the program. This is considered to be the least technically challenging improvement to make and it will be completed as the software reaches a point of practicality.
4.5	Multiple Volume Conditions
The ability to simultaneously solve multiple volume conditions would greatly improve the usefulness of the software. For instance, a heat sink could be simulated with an adjacent processor separated by a layer of thermal paste as would be encountered in real life applications. 
4.6	Radiation
Presently the convection boundary condition does not include the option to simulate radiative heat transfer with the surrounding environment. Adding this feature would improve the accuracy of models compared with a convection-only approach as fins on the outside of the heat sink could be assigned to radiate heat while fins on the inside could be assigned not to radiate heat since they would be radiating to each other and thus have a very small net radiation. 
4.7 Time-Accurate Solutions
Some problems in electronics design require a time-to-failure or other time-dependent solution to be implemented. For instance, in a failed-fan scenario, the heat transfer coefficient on the fins of the heat sink may be reduced to natural-convection levels. In this situation, a processor running at 100% of it’s design capacity (or greater) may fail due to thermal stresses. It may be advantageous to determine how long the processor could run in such a condition before exceeding its design temperature. 
It should be possible to implement a time-accurate solver using an explicit method such as a forward-Euler. 
5.	Conclusion
Picante is a work in progress that shows it is practical to solve simple 3D heat transfer problems using Python. Additional development work as described in Section 4 could turn the program into practical software for heat sink design and other real-world applications, eliminating the need for expensive CFD software such as Fluent or Star CCM+, for this class of problems. 

6. 	References

	A. Introduction to Heat Transfer, Fifth Edition. Incropera, DeWitt, Bergman, Lavine. John Wiley & Sons 2007. ISBN: 978-0-471-45727-5
