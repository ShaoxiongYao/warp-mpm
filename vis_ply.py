import open3d as o3d
from time import sleep
import numpy as np

def set_view_params(o3d_vis, view_params={}):
    ctr = o3d_vis.get_view_control()
    if "zoom" in view_params.keys():
        ctr.set_zoom(view_params["zoom"])
    if "front" in view_params.keys():
        ctr.set_front(view_params["front"])
    if "lookat" in view_params.keys():
        ctr.set_lookat(view_params["lookat"])
    if "up" in view_params.keys():
        ctr.set_up(view_params["up"])

view_params = {
    "front" : [ 0.041602455176179332, 0.95464467308242218, 0.29482670143436696 ],
    "lookat" : [ 0.49333910768085065, 0.64480309531102475, 0.24721088918390274 ],
    "up" : [ 0.00040843342113954656, -0.29509839549305839, 0.95546678129569895 ],
    "zoom" : 0.059999999999999609
}

frames = 500

vis = o3d.visualization.Visualizer()
vis.create_window()

bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=(0.0, 0.0, 0.0), max_bound=(1.0, 1.0, 1.0))
bbox.color = (0.0, 0.0, 0.0)
vis.add_geometry(bbox)

vis_dir = 'sim_results_warp'

pcd = o3d.io.read_point_cloud(f'{vis_dir}/sim_0000000000.ply')
coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
vis.add_geometry(coord_frame)

print('points min:', np.min(np.array(pcd.points), axis=0))
print('points max:', np.max(np.array(pcd.points), axis=0))

vis.add_geometry(pcd)
vis.poll_events()
vis.update_renderer()

set_view_params(vis, view_params)
for i in range(1, frames):
    pcd.points = o3d.io.read_point_cloud(f'{vis_dir}/sim_{i:010d}.ply').points
    # o3d.visualization.draw_geometries([pcd, coord_frame], **view_params)
    vis.update_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()

    vis.capture_screen_image(f'{vis_dir}/sim_{i:010d}.png')
    sleep(0.02)
