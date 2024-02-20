
import warp as wp
from mpm_solver_warp import MPM_Simulator_WARP
from engine_utils import *
import torch
import time

t1 = time.time()

wp.init()
wp.config.verify_cuda = True


dvc = "cuda:0"

batch_size = 1
dx = 0.02

# first initialization
mpm_solver = MPM_Simulator_WARP(n_particles=10, batch_size=batch_size, dx=dx, device=dvc)

# grid_lim = [0.81, 0.87, 0.95]
grid_lim = [1.0, 1.0, 1.0]

# second initialization
# You can either load sampling data from an external h5 file, containing initial position (n,3) and particle_volume (n,)
mpm_solver.load_from_sampling("sim_data/sand_column.h5", batch_size=batch_size, dx=dx, device=dvc, fps=1000)
# mpm_solver.load_from_sampling("sim_data/rot_tree_sampling.h5", batch_size=batch_size, dx=dx, 
#                               grid_lim=[3.63005695, 2.52705687, 2.61115279], device=dvc, fps=10000)

# mpm_solver.load_from_sampling("sim_data/vsf_orange_tree_angle06_sampling.h5", batch_size=batch_size, 
#                               dx=dx, grid_lim=grid_lim, device=dvc, fps=-1)

# Or load from torch tensor (also position and volume)
# Here we borrow the data from h5, but you can use your own
volume_tensor = torch.ones((batch_size, mpm_solver.n_particles)) * 2.5e-8  # (bsz, n)
# volume_tensor = torch.ones((batch_size, mpm_solver.n_particles)) * 1e-5  # (bsz, n)
position_tensor = mpm_solver.export_particle_x_to_torch()  # (bsz, n, 3)

# third initialization
mpm_solver.load_initial_data_from_torch(position_tensor, volume_tensor, batch_size=batch_size, 
                                        dx=dx, grid_lim=grid_lim, device=dvc)

# Note: You must provide 'density=..' to set particle_mass = density * particle_volume

material_params = {
    'E': 2000,
    'nu': 0.2,
    "material": "sand",
    'friction_angle': 35,
    'g': [0.0, 0.0, -4.0],
    "density": 200.0
}
mpm_solver.set_parameters_dict(material_params)

mpm_solver.finalize_mu_lam() # set mu and lambda from the E and nu input

mpm_solver.add_surface_collider((0.0, 0.0, -0.22), (0.0,0.0,1.0), 'sticky', 0.0)
# mpm_solver.add_surface_collider((0.27673412, 2.44109263, 1.15073543), (0.0,-1.0,0.0), 'sticky', 0.0)

directory_to_save = './sim_results_warp'

save_data_at_frame(mpm_solver, directory_to_save, 0, save_to_ply=True, save_to_h5=False)

time1 = time.time()
for k in range(1, 500):
    mpm_solver.p2g2p(k, 0.002, device=dvc)
    save_data_at_frame(mpm_solver, directory_to_save, k, save_to_ply=True, save_to_h5=False)
time2 = time.time()
print("Time for 500 iterations: ", time2-time1)

t2 = time.time()
print("Total time: ", t2-t1)


# extract the position, make some changes, load it back
# e.g. we shift the x position
# position = mpm_solver.export_particle_x_to_torch()
# position[..., 0] = position[..., 0] + 0.1
# mpm_solver.import_particle_x_from_torch(position)

# keep running sim
# for k in range(50, 1000):
#  
#     mpm_solver.p2g2p(k, 0.002, device=dvc)
#     save_data_at_frame(mpm_solver, directory_to_save, k, save_to_ply=True, save_to_h5=False)
