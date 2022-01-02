from OpenGL.GL import *
from OpenGL.GLU import *
import glm
import numpy as np
import h5py
import c_assimp
from bounding_box import BoundBox
import gl_util

class H5Reader:
    def __init__(self, model_file):
        self.model_file = model_file
        self.fo = h5py.File(model_file, mode='r')
        self.model = c_assimp.Model()
        self.player_name = ""
        
    def read_mesh(self, player_name):
        self.read_meshes(player_name)
        self.player_name = player_name
        self.create_vao()
        self.read_nodes(player_name)
        self.read_animations(player_name)
        
    def read_meshes(self, player_name):
        meshes = self.fo['{}/meshes'.format(player_name)]
        if not meshes: return
        for mesh_grp_key in meshes.keys():
            mat = c_assimp.Material()
            self.model.materials.append(mat)
            mesh_folder = '{}/meshes/{}'.format(player_name, mesh_grp_key)
            mesh_grp = self.fo[mesh_folder]
            pos_folder = mesh_folder + '/POSITION'
            #print(pos_folder)
            if pos_folder in self.fo:
                pos = self.fo[pos_folder][...]
                #print(pos)
                mat.has_position = True
                mat.pos_type = GL_FLOAT
                mat.pos_elem_count = 3
                mat.vbo_vertex = gl_util.create_vbo(pos)
            max_folder = mesh_folder + '/max_pos'
            if max_folder in self.fo:
                max_pos = self.fo[max_folder][...]
                #print(max_pos)
                #max_pos = [100., 200., 0.]  ###TODO!!!
                self.model.bound_box.add_point(max_pos)
            min_folder = mesh_folder + '/min_pos'
            if min_folder in self.fo:
                min_pos = self.fo[min_folder][...]
                #print(min_pos)
                self.model.bound_box.add_point(min_pos)
            ind_folder = mesh_folder + '/indices'
            #print(ind_folder)
            if ind_folder in self.fo:
                indices = self.fo[ind_folder][...]
                #print(indices)
                mat.num_face = len(indices)
                mat.idx_type = GL_UNSIGNED_INT
                mat.ibo_faces = gl_util.create_ibo(indices)
            norm_folder = mesh_folder + '/NORMAL'
            #print(norm_folder)
            if norm_folder in self.fo:
                norm = self.fo[norm_folder][...]
                #print(norm)
                mat.has_normal = True
                mat.norm_elem_count = 3
                mat.vbo_normal = gl_util.create_vbo(norm)
            tex_folder = mesh_folder + '/TEXCOORD_0'
            #print(tex_folder)
            if tex_folder in self.fo:
                tex_coords = self.fo[tex_folder][...]
                #print(tex_coords)
                mat.uv_elem_count = 2
                mat.has_uv = True
                mat.vbo_tex_coord = gl_util.create_vbo(tex_coords)
            joints_folder = mesh_folder + '/JOINTS_0'
            #print(joints_folder)
            if joints_folder in self.fo:
                joints = self.fo[joints_folder][...]
                mat.vbo_bone_id = gl_util.create_vbo(joints)
                mat.bone_id_type = GL_UNSIGNED_INT
                #print(joints)
            # node_indexs
            node_indexs_folder = mesh_folder + '/node_indexs'
            if node_indexs_folder in self.fo:
                mat.node_indexs = self.fo[node_indexs_folder][...]
                #print(mat.node_indexs)
            weights_folder = mesh_folder + '/WEIGHTS_0'
            #print(weights_folder)
            if weights_folder in self.fo:
                weights = self.fo[weights_folder][...]
                mat.vbo_bone_weight = gl_util.create_vbo(weights)
                mat.weight_type = GL_FLOAT
                #print(weights)
            image_folder = mesh_folder + '/image'
            if image_folder in self.fo:
                image = self.fo[image_folder][...]
                img_bytes = image.tobytes()
                #print(len(img_bytes))
                #print(image.shape, image.dtype)
                mat.has_texture = True
                mat.texture = gl_util.create_texture(img_bytes)
            # diffuse_color
            diffuse_folder = mesh_folder + '/diffuse_color'
            if diffuse_folder in self.fo:
                diffuse_color = self.fo[diffuse_folder][...]
                mat.diffuse_color = diffuse_color
        
    def read_animations(self, player_name):
        if '{}/animations'.format(player_name) not in self.fo: return
        anims = self.fo['{}/animations'.format(player_name)]
        if not anims: return
        node_d = {node.name: node for node in self.model.nodes}
        for anim_grp_key in anims.keys():
            anim_folder = '{}/animations/{}'.format(player_name, anim_grp_key)
            # animation
            anim = c_assimp.Animation()
            self.model.animations.append(anim)
            anim.time = 0.0
            anim.weight = 1.0
            # anim name
            anim_name = self.fo[anim_folder + '/name'][...]
            anim_name = str(anim_name)
            if "b'" in anim_name:
                anim_name = anim_name[2:-1]
            #print(anim_name)
            anim.name = anim_name
            # duration, ticks_per_second
            dur = self.fo[anim_folder + '/duration'][...]
            anim.duration = dur[0]
            anim.ticks_per_second = dur[1]
            chan_folder = anim_folder + '/channels'
            chans = self.fo[chan_folder]
            for chan in chans.keys():
                chan_item_folder = chan_folder + '/' + chan
                # anim key
                anim_key = c_assimp.AnimationKey()
                anim.keys.append(anim_key)
                # node name
                node_name = self.fo[chan_item_folder + '/node'][...]
                node_name = str(node_name)
                if "b'" in node_name:
                    node_name = node_name[2:-1]
                anim_key.node_name = node_name
                if node_name in node_d:
                    anim_key.node = node_d[node_name]
                # position
                anim_key.position_times = self.fo[chan_item_folder + '/position_times'][...]
                anim_key.positions = self.fo[chan_item_folder + '/positions'][...]
                # rotation
                anim_key.rotation_times = self.fo[chan_item_folder + '/rotation_times'][...]
                anim_key.rotations = self.fo[chan_item_folder + '/rotations'][...]
                # scale
                anim_key.scale_times = self.fo[chan_item_folder + '/scale_times'][...]
                anim_key.scales = self.fo[chan_item_folder + '/scales'][...]
        
    def read_nodes(self, player_name):
        if '{}/nodes'.format(player_name) not in self.fo: return
        nodes = self.fo['{}/nodes'.format(player_name)]
        if not nodes: return
        node_d = {}
        children_d = {}
        for node_grp_key in nodes.keys():
            node_folder = '{}/nodes/{}'.format(player_name, node_grp_key)
            # name
            name_folder = node_folder + '/name'
            #print(name_folder)
            if name_folder not in self.fo: continue
            name = self.fo[name_folder][...]
            name = str(name)
            if "b'" in name:
                name = name[2:-1]
            node = c_assimp.Node(name)
            # transform_matrix
            trans_mat_folder = node_folder + '/transform_matrix'
            trans_mat = self.fo[trans_mat_folder][...]
            node.transform_matrix = glm.mat4(*trans_mat)
            # offset_matrix
            offset_mat_folder = node_folder + '/offset_matrix'
            offset_mat = self.fo[offset_mat_folder][...]
            node.offset_matrix = glm.mat4(*offset_mat)
            # set node index
            node.index = len(self.model.nodes)
            self.model.nodes.append(node)
            node_d[name] = node
            # children
            children_folder = node_folder + '/children'
            if children_folder in self.fo:
                children = self.fo[children_folder][...]
                children = [str(child_name)[2:-1] for child_name in children]
                children_d[name] = children
        # set children
        for node in self.model.nodes:
            if node.name in children_d:
                for child_name in children_d[node.name]:
                    if child_name in node_d:
                        child_node = node_d[child_name]
                        node.children.append(child_node)
    
    def create_vao(self):
        for mat in self.model.materials:
            mat.vao = glGenVertexArrays(1)
            glBindVertexArray(mat.vao)
            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, mat.vbo_vertex)
            glVertexAttribPointer(0, mat.pos_elem_count, mat.pos_type, GL_FALSE, 0, None)
            if mat.has_normal:
                glEnableVertexAttribArray(1)
                glBindBuffer(GL_ARRAY_BUFFER, mat.vbo_normal)
                glVertexAttribPointer(1, mat.norm_elem_count, GL_FLOAT, GL_FALSE, 0, None)
            if mat.has_uv:
                glEnableVertexAttribArray(2)
                glBindBuffer(GL_ARRAY_BUFFER, mat.vbo_tex_coord)
                glVertexAttribPointer(2, mat.uv_elem_count, GL_FLOAT, GL_FALSE, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mat.ibo_faces)
            if mat.vbo_bone_id:
                glEnableVertexAttribArray(3)
                glBindBuffer(GL_ARRAY_BUFFER, mat.vbo_bone_id)
                glVertexAttribIPointer(3, 4, mat.bone_id_type, 0, None)
            if mat.vbo_bone_weight:
                glEnableVertexAttribArray(4)
                glBindBuffer(GL_ARRAY_BUFFER, mat.vbo_bone_weight)
                glVertexAttribPointer(4, 4, mat.weight_type, GL_FALSE, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)
    
if __name__ == "__main__":
    reader = H5Reader('zzz_DB_assimp.h5')
    reader.read_meshes("models/goku-ssj")
