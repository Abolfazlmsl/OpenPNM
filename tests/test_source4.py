import OpenPNM
import scipy as sp
print('-----> Using OpenPNM version: '+OpenPNM.__version__)
pn = OpenPNM.Network.Cubic(shape=[10,10,40],spacing=0.0001)
pn.add_boundaries()

Ps = pn.pores('boundary',mode='not')
Ts = pn.find_neighbor_throats(pores=Ps,mode='intersection',flatten=True)
geom = OpenPNM.Geometry.Toray090(network=pn,pores=Ps,throats=Ts)

Ps = pn.pores('boundary')
Ts = pn.find_neighbor_throats(pores=Ps,mode='not_intersection')
boun = OpenPNM.Geometry.Boundary(network=pn,pores=Ps,throats=Ts)

air = OpenPNM.Phases.Air(network=pn)

#---------------------------------------------------------------------------------------------
phys_air = OpenPNM.Physics.Standard(network=pn,phase=air,pores=sp.r_[600:pn.Np],throats=pn.Ts)
#Add some source terms to phys_air1
phys_air.add_model(model=OpenPNM.Physics.models.generic_source_term.power_law,
                   propname='pore.blah1',
                   A1=0.5e-13,
                   A2=1.5,
                   A3=2.5e-14)
phys_air.add_model(model=OpenPNM.Physics.models.generic_source_term.power_law,
                   propname='pore.blah2',
                   A1=0.9e-13,
                   A2=1.9,
                   A3=4.15e-14)
phys_air.add_model(model=OpenPNM.Physics.models.generic_source_term.natural_exponential,
                   propname='pore.blah3',
                   A1=0.3e-11,
                   A2=0.5,
                   A3=2,
                   A4=-0.34,
                   A5=2e-14)
#-----------------------------------------------------------------------------------------------                   
phys_air2 = OpenPNM.Physics.Standard(network=pn,phase=air,pores=sp.r_[0:600])
#Add some source terms to phys_air2
phys_air2.add_model(model=OpenPNM.Physics.models.generic_source_term.power_law,
                   propname='pore.blah1',
                   A1=1.5e-13,
                   A2=1.7,
                   A3=1.5e-14)
#-----------------------------------------------------------------------------------------------                   
alg = OpenPNM.Algorithms.FickianDiffusion(network=pn,phase=air)
BC1_pores = pn.pores('right_boundary')
alg.set_boundary_conditions(bctype='Dirichlet', bcvalue=0.6, pores=BC1_pores)
BC2_pores = pn.pores('left_boundary')
alg.set_boundary_conditions(bctype='Neumann_group', bcvalue=0.2*1e-11, pores=BC2_pores)
#-----------------------------------------------------------------------------------------------                   
alg.set_source_term(source_name=['pore.blah1','pore.blah2'],pores=sp.r_[500:700],tol = 1e-10)
alg.set_source_term(source_name='pore.blah3',pores=sp.r_[800:900])
alg.setup()
alg.solve()
alg.return_results()
print('--------------------------------------------------------------')
print('steps: ',alg._steps)
print('tol_reached: ',alg._tol_reached)
print('--------------------------------------------------------------')
print('reaction from the physics for pores [500:700]:',\
                        sp.sum(1.5e-13*air['pore.mole_fraction'][sp.r_[500:600]]**1.7+1.5e-14)\
                        +sp.sum(0.5e-13*air['pore.mole_fraction'][sp.r_[600:700]]**1.5+2.5e-14)\
                        +sp.sum(0.9e-13*air['pore.mole_fraction'][sp.r_[600:700]]**1.9+4.15e-14))
print('rate from the algorithm for pores [500:700]:',alg.rate(sp.r_[500:700])[0])
print('--------------------------------------------------------------')
print('reaction from the physics for pores [800:900]:',sp.sum(0.3e-11*sp.exp(0.5*air['pore.mole_fraction'][sp.r_[800:900]]**2-0.34)+2e-14))
print('rate from the algorithm for pores [800:900]:',alg.rate(sp.r_[800:900])[0])
