#!/usr/bin/python
## My first python code

##imports:

import numpy as np
import Util


## My functions:

def get_element_data():
  abundTc=[('AlI',1665.  ), ('CaI',1647.  ), ('CoI',1347.  ), ('CrI',1291.  ), 
           ('CrII',1291  ), ('MgI',1387.  ), ('MnI',1150.  ), ('NaI',953.   ),  
           ('NiI',1348.  ), ('ScI',1647.  ), ('ScII',1647. ), ('SiI',1519.  ), 
           ('TiI',1584.  ), ('TiII',1584. ), ('VI',1427.   ), ('[S/H]',693. ),
           ('[Ba/H]',906.), ('[C/H]',77   ), ('[Cu/H]',1033), ('[Eu/H]',1347), 
           ('[Nd/H]',1594), ('[O/H]',181. ), ('[Y/H]',1647) ,
           ('[Li/H]',1135), ('[Nd/H]',1594), ('[O/H]',181. ), ('[Y/H]',1647) ,
           ('[Zn/H]',723 ), ('[Zr/H]',1758)]
## Data from Lodders 2003
  element_dic = {'H' : ( 1,  181), 'He': ( 2,    3), 'Li': ( 3, 1135), 'Be': ( 4, 1445),
                 'B' : ( 5,  906), 'C' : ( 6,   77), 'N' : ( 7,  131), 'O' : ( 8,  181),
                 'F' : ( 9,  731), 'Ne': (10,  9.3), 'Na': (11,  953), 'Mg': (12, 1387),
                 'Al': (13, 1665), 'Si': (14, 1519), 'P' : (15, 1245), 'S' : (16,  693),
                 'Cl': (17,  948), 'Ar': (18,   48), 'K' : (19, 1001), 'Ca': (20, 1647),
                 'Sc': (21, 1647), 'Ti': (22, 1584), 'V' : (23, 1427), 'Cr': (24, 1291),
                 'Mn': (25, 1150), 'Fe': (26, 1351), 'Co': (27, 1347), 'Ni': (28, 1348),
                 'Cu': (29, 1033), 'Zn': (30,  723), 'Ga': (31,  971), 'Ge': (32,  885),
                 'As': (33, 1061), 'Se': (34,  688), 'Br': (35,  544), 'Kr': (36,   53), 
                 'Rb': (37,  798), 'Sr': (38, 1455), 'Y' : (39, 1647), 'Zr': (40, 1758), 
                 'Nb': (41, 1557), 'Mo': (42, 1587), 'Tc': (43,   -1), 'Ru': (44, 1546), 
                 'Rh': (45, 1387), 'Pd': (46, 1318), 'Ag': (47,  992), 'Cd': (48,  650), 
                 'In': (49,  535), 'Sn': (50,  703), 'Sb': (51,  976), 'Te': (52,  705), 
                 'I ': (53,  533), 'Xe': (54,   68), 'Cs': (55,  797), 'Ba': (40, 1447), 
                 'La': (57, 1570), 'Ce': (58, 1477), 'Pr': (59, 1574), 'Nd': (60, 1594), 
                 'Pm': (61,   -1), 'Sm': (62, 1580), 'Eu': (63, 1347), 'Gd': (64, 1647)
                }
     
      
            
  return element_dic
  


### Main program:
def main():
#  path = '/home/sousasag/Programas/SPECPAR/'
  path = './'
  print get_element_data()['Sb']
  
  
  


if __name__ == "__main__":
    main()
