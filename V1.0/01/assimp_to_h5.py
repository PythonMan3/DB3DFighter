import numpy as np
import h5py
from PIL import Image
import c_assimp
import sys
import os

def main(data_folder, model_file, h5_file, model_idx):
    with h5py.File(h5_file, mode='a') as fo:
        model = c_assimp.Model()
        file_path = data_folder + "/" + model_file
        model.import_file(file_path)
        read_model = False
        read_anim = True
        if model_idx == 0:
            read_model = True
        player_name = model_file[model_file.rfind('/') + 1:model_file.find('_')]
        # read mesh
        if read_model:
            print(player_name)####
            for mat_idx, mat in enumerate(model.materials):
                folder = '{}/meshes/{:02d}'.format(player_name, mat_idx)
                mesh_grp = fo.create_group(folder)
                # POSITION
                if mat.has_position:
                    name = 'POSITION'
                    dtype = np.float32
                    dataset = mesh_grp.create_dataset(name=name, shape=(len(mat.vertexs) // 3, 3), dtype=dtype, data=mat.vertexs)
                    min_pos = [sys.float_info.max, sys.float_info.max, sys.float_info.max]
                    max_pos = [-sys.float_info.max, -sys.float_info.max, -sys.float_info.max]
                    for pos_idx in range(len(mat.vertexs) // 3):
                        x, y, z = mat.vertexs[pos_idx*3:pos_idx*3+3]
                        min_pos[0] = min(min_pos[0], x)
                        min_pos[1] = min(min_pos[1], y)
                        min_pos[2] = min(min_pos[2], z)
                        max_pos[0] = max(max_pos[0], x)
                        max_pos[1] = max(max_pos[1], y)
                        max_pos[2] = max(max_pos[2], z)
                    name = 'max_pos'
                    max_pos = np.array(max_pos, dtype=np.float32)
                    dataset = mesh_grp.create_dataset(name=name, shape=3, dtype=np.float32, data=max_pos)
                    name = 'min_pos'
                    min_pos = np.array(min_pos, dtype=np.float32)
                    dataset = mesh_grp.create_dataset(name=name, shape=3, dtype=np.float32, data=min_pos)
                # indices
                name = 'indices'
                dtype = np.uint32
                dataset = mesh_grp.create_dataset(name=name, shape=(len(mat.faces) // 3, 3), dtype=dtype, data=mat.faces)
                # normal
                if mat.has_normal:
                    name = 'NORMAL'
                    dtype = np.float32
                    dataset = mesh_grp.create_dataset(name=name, shape=(len(mat.normals) // 3, 3), dtype=dtype, data=mat.normals)
                # texture coords
                if mat.has_uv:
                    name = 'TEXCOORD_0'
                    dtype = np.float32
                    dataset = mesh_grp.create_dataset(name=name, shape=(len(mat.uvs) // 2, 2), dtype=dtype, data=mat.uvs)
                # texture
                if mat.texture_file:
                    #img = Image.open(mat.texture_file)
                    #width, height = img.size
                    #texture_data = img.tobytes()
                    img_f = open(mat.texture_file, 'rb')
                    texture_data = img_f.read()
                    name = 'image'
                    dtype = np.uint8
                    byte_len = len(texture_data)
                    np_buf = np.frombuffer(texture_data, dtype=dtype, count=byte_len, offset=0)
                    dataset = mesh_grp.create_dataset(name=name, shape=byte_len, dtype=dtype, data=np_buf)
                # JOINTS_0
                name = 'JOINTS_0'
                dtype = np.uint32
                dataset = mesh_grp.create_dataset(name=name, shape=(len(mat.vertex_bone_idxs), 4), dtype=dtype, data=mat.vertex_bone_idxs)
                # WEIGHTS_0
                name = 'WEIGHTS_0'
                dtype = np.float32
                dataset = mesh_grp.create_dataset(name=name, shape=(len(mat.vertex_weights), 4), dtype=dtype, data=mat.vertex_weights)
                # node_indexs
                name = 'node_indexs'
                dtype = np.uint32
                dataset = mesh_grp.create_dataset(name=name, shape=len(mat.node_indexs), dtype=dtype, data=mat.node_indexs)
                # diffuse_color
                name = 'diffuse_color'
                diffuse_color = mat.diffuse_color
                diffuse_color = np.array(diffuse_color, dtype=np.float32)
                dataset = mesh_grp.create_dataset(name=name, shape=4, dtype=np.float32, data=diffuse_color)
        # read animations
        if read_anim:
            for anim_idx, anim in enumerate(model.animations):
                anim_idx0 = 0
                anim_root_grp = '{}/animations'.format(player_name)
                if anim_root_grp in fo:
                    anims = fo[anim_root_grp]
                    anim_idx0 = len(anims)
                #print(anim.name)
                folder = '{}/animations/{:03d}'.format(player_name, anim_idx0)
                anim_grp = fo.create_group(folder)
                # name
                anim_name = model_file[model_file.find('_') + 1:model_file.rfind('.')]
                print("{}: {}".format(anim_idx0, anim_name))####
                name = 'name'
                dtype = h5py.special_dtype(vlen=str)
                dataset = anim_grp.create_dataset(name=name, dtype=dtype, data=anim_name)
                # duration, ticks_per_second
                name = 'duration'
                dtype = np.float32
                dataset = anim_grp.create_dataset(name=name, shape=2, dtype=dtype, data=[anim.duration, anim.ticks_per_second])
                for key_idx, key in enumerate(anim.keys):
                    folder2 = folder + '/channels/{:03d}'.format(key_idx)
                    chan_grp = fo.create_group(folder2)
                    # node
                    name = 'node'
                    dtype = h5py.special_dtype(vlen=str)
                    dataset = chan_grp.create_dataset(name=name, dtype=dtype, data=key.node_name)
                    # position
                    name = 'position_times'
                    dtype = np.float32
                    dataset = chan_grp.create_dataset(name=name, shape=len(key.position_times), dtype=dtype, data=key.position_times)
                    name = 'positions'
                    dtype = np.float32
                    dataset = chan_grp.create_dataset(name=name, shape=(len(key.positions), 3), dtype=dtype, data=key.positions)
                    # rotation
                    name = 'rotation_times'
                    dtype = np.float32
                    dataset = chan_grp.create_dataset(name=name, shape=len(key.rotation_times), dtype=dtype, data=key.rotation_times)
                    name = 'rotations'
                    dtype = np.float32
                    dataset = chan_grp.create_dataset(name=name, shape=(len(key.rotations), 4), dtype=dtype, data=key.rotations)
                    # scale
                    name = 'scale_times'
                    dtype = np.float32
                    dataset = chan_grp.create_dataset(name=name, shape=len(key.position_times), dtype=dtype, data=key.scale_times)
                    name = 'scales'
                    dtype = np.float32
                    dataset = chan_grp.create_dataset(name=name, shape=(len(key.scales), 3), dtype=dtype, data=key.scales)
        # read nodes
        if read_model:
            for node_idx, node in enumerate(model.nodes):
                folder = '{}/nodes/{:03d}'.format(player_name, node_idx)
                node_grp = fo.create_group(folder)
                # name
                name = 'name'
                dtype = h5py.special_dtype(vlen=str)
                dataset = node_grp.create_dataset(name=name, dtype=dtype, data=node.name)
                # children
                if node.children:
                    name = 'children'
                    dtype = h5py.special_dtype(vlen=str)
                    child_nodes = [node.name for node in node.children]
                    dataset = node_grp.create_dataset(name=name, dtype=dtype, data=child_nodes)
                # transform_matrix
                name = 'transform_matrix'
                dtype = np.float32
                dataset = node_grp.create_dataset(name=name, shape=16, dtype=dtype, data=node.transform_matrix)
                # offset_matrix
                name = 'offset_matrix'
                dtype = np.float32
                dataset = node_grp.create_dataset(name=name, shape=16, dtype=dtype, data=node.offset_matrix)

if __name__ == '__main__':
    h5_file = 'DB_ALL_models.h5'
    if  os.path.exists(h5_file):
        os.remove(h5_file)
    data_folder = 'data/DB'
    model_files = [
        'goku-ssj/goku-ssj_BouncingFightIdle.fbx',
        ]
    for idx, model_file in enumerate(model_files):
        main(data_folder, model_file, h5_file, idx)
