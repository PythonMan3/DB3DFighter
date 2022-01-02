from ctypes import *
import glm
import pathlib
from bounding_box import BoundBox
import numpy as np

# Imported Data
class Model:
    def __init__(self):
        self.bound_box = BoundBox()
        self.model_file = ""
        self.materials = []
        self.nodes = []
        self.animations = []
        self.center_frame = None
        self.center_pos = glm.vec3()
        
    def import_file(self, file_name):
        import_file(file_name)
        self.model_file = file_name
        self.read_mesh()
        #self.update_bound_box()
        self.read_tree_node()
        self.read_bone()
        self.read_animation()
        self.convert_bone()
        release_import()
        
    def update_bound_box(self):
        self.bound_box.reset()
        num_mesh = get_num_meshes()
        for mesh_idx in range(num_mesh):
            num_vertex = get_num_vertices(mesh_idx)
            vertexs = get_positions(mesh_idx)
            for i in range(num_vertex):
                x = vertexs[i * 3]
                y = vertexs[i * 3 + 1]
                z = vertexs[i * 3 + 2]
                self.bound_box.add_point([x, y, z])
        
    def read_mesh(self):
        num_mesh = get_num_meshes()
        for mesh_idx in range(num_mesh):
            mat = Material()
            self.materials.append(mat)
            # position and face
            if get_has_positions(mesh_idx):
                mat.num_vertex = get_num_vertices(mesh_idx)
                mat.vertexs = get_positions(mesh_idx)
                mat.num_face = get_num_faces(mesh_idx)
                mat.faces = get_faces(mesh_idx)
                mat.has_position = True
            # normal
            if get_has_normals(mesh_idx):
                mat.normals = get_normals(mesh_idx)
                mat.has_normal = True
            # texture coords
            if get_has_textureCoords(mesh_idx):
                mat.uvs = get_textureCoords(mesh_idx)
                mat.has_uv = True
            # texture
            tex_file_name = get_texture_file_name(mesh_idx)
            if tex_file_name:
                folder_p = pathlib.Path(self.model_file).absolute().parent
                tex_p = pathlib.Path(tex_file_name)
                path = folder_p.joinpath(tex_p)
                if path.exists():
                    tex_file_name = str(path)
                    mat.texture_file = tex_file_name
            # diffuse color
            mat.diffuse_color = get_diffuse_color(mesh_idx)
        
    def read_tree_node(self):
        import_skeleton_node()
        root_name = get_skeleton_root_node_name()
        node = Node(root_name)
        node.transform_matrix = glm.mat4(*get_skeleton_transform_matrix(root_name))
        node.index = len(self.nodes)
        self.nodes.append(node)
        add_node(node, self.nodes)
        
    def read_bone(self):
        for mesh_idx, mat in enumerate(self.materials):
            num_vertex = get_num_vertices(mesh_idx)
            mat.vertex_bone_idxs = [[0] * 4 for v_i in range(num_vertex)]
            mat.vertex_weights = [[0.0] * 4 for v_i in range(num_vertex)]
            bones = []
            num_bones = get_num_bones(mesh_idx)
            for j in range(num_bones):
                bone_name = get_bone_name(mesh_idx, j)
                bone = Bone(bone_name)
                mat.bones.append(bone)
                num_weights = get_bone_num_weights(mesh_idx, j)
                for k in range(num_weights):
                    vertex_idx = get_bone_vertex_id(mesh_idx, j, k)
                    weight = get_bone_weight(mesh_idx, j, k)
                    aweight = Weight()
                    aweight.vertex_index = vertex_idx
                    aweight.weight = weight
                    bone.weights.append(aweight)
                bone.offset_matrix = glm.mat4(*get_bone_offset_matrix(mesh_idx, j))
                    
    def read_animation(self):
        num_anim = get_num_animations()
        for anim_i in range(num_anim):
            anim = Animation()
            self.animations.append(anim)
            anim.time = 0.0
            anim.weight = 1.0
            anim.name = get_anim_name(anim_i)
            anim.duration = get_anim_duration(anim_i)
            anim.ticks_per_second = get_anim_ticks_per_second(anim_i)
            num_chan = get_anim_num_channels(anim_i)
            for i in range(num_chan):
                anim_key = AnimationKey()
                anim.keys.append(anim_key)
                name = get_anim_channel_node_name(anim_i, i)
                anim_key.node_name = name
                node = self.find_node(name)
                num_pos_key = get_anim_num_position_keys(anim_i, i)
                for j in range(num_pos_key):
                    key = get_anim_position_keys(anim_i, i, j)
                    anim_key.positions.append(key[:3])
                    anim_key.position_times.append(key[3])
                num_rot_key = get_anim_num_rotation_keys(anim_i, i)
                for j in range(num_rot_key):
                    key = get_anim_rotation_keys(anim_i, i, j)
                    anim_key.rotations.append(key[:4])
                    anim_key.rotation_times.append(key[4])
                num_sca_key = get_anim_num_scaling_keys(anim_i, i)
                for j in range(num_sca_key):
                    key = get_anim_scaling_keys(anim_i, i, j)
                    anim_key.scales.append(key[:3])
                    anim_key.scale_times.append(key[3])
                    
    def convert_bone(self):
        # 頂点に対してボーンのインデックスと重みのデータを作成 (最大4つ)
        for mesh_idx, mat in enumerate(self.materials):
            mat.vertex_bone_idxs = [[0] * 4 for v_i in range(mat.num_vertex)]
            mat.vertex_weights = [[0.0] * 4 for v_i in range(mat.num_vertex)]
            joint_d = {}
            for bone in mat.bones:
                node = self.find_node(bone.name)
                joint_idx = -1
                if node.index not in joint_d:
                    joint_idx = len(mat.node_indexs)
                    joint_d[node.index] = joint_idx
                    mat.node_indexs.append(node.index)
                else:
                    joint_idx = joint_d[node.index]
                if node:
                    for aweight in bone.weights:
                        vertex_idx = aweight.vertex_index
                        # 4個のデータ内で重みが 0.0 の位置 (まだ書き込まれていない位置) にデータを保存
                        for j in range(4):
                            vertex_weight = mat.vertex_weights[vertex_idx][j]
                            if vertex_weight == 0.0:
                                mat.vertex_weights[vertex_idx][j] = aweight.weight
                                mat.vertex_bone_idxs[vertex_idx][j] = joint_idx
                                break
                    node.offset_matrix = bone.offset_matrix
        # from channel bone to node bone
        for anim in self.animations:
            for anim_key in anim.keys:
                node = self.find_node(anim_key.node_name)
                if node:
                    anim_key.node = node
        
    def find_node(self, name):
        for node in self.nodes:
             if node.name == name:
                 return node
        return None
      
    def get_animation(self, index):
        if index < len(self.animations):
            return self.animations[index]
        else:
            return None
        
    def add_animation(self, anim):
        self.animations.append(anim)
        
    def animate_node(self, world):
        # アニメーションキーが関係するフレームの変形行列を初期化
        for anim in self.animations:
            if anim.weight == 0.0: continue
            # 0で初期化
            for key in anim.keys:
                key.node.transform_matrix = glm.mat4(0.0)
        # アニメーションキーが関係するフレームの変形行列を計算
        for anim in self.animations:
            if anim.weight == 0.0: continue
            for key in anim.keys:
                node = key.node
                # キーフレームの補間
                time = anim.time
                trans, rot, scale = [glm.mat4(1.0)] * 3
                # Position
                if len(key.position_times) > 0:
                    if time < key.position_times[0]:
                        pos = key.positions[0]
                        trans = glm.translate(glm.mat4(1.0), glm.vec3(pos[0], pos[1], pos[2]))
                    elif time >= key.position_times[-1]:
                        pos = key.positions[-1]
                        trans = glm.translate(glm.mat4(1.0), glm.vec3(pos[0], pos[1], pos[2]))
                    else:
                        for k, _ in enumerate(key.position_times):
                            if time < key.position_times[k] and key.position_times[k - 1] != key.position_times[k]:
                                r = (key.position_times[k] - time) / (key.position_times[k] - key.position_times[k - 1])
                                pos1 = key.positions[k - 1]
                                pos2 = key.positions[k]
                                trans1 = glm.translate(glm.mat4(1.0), glm.vec3(pos1[0], pos1[1], pos1[2]))
                                trans2 = glm.translate(glm.mat4(1.0), glm.vec3(pos2[0], pos2[1], pos2[2]))
                                trans = (trans1 * r + trans2 * (1 - r))
                                break
                if node == self.center_frame:
                    self.center_pos = glm.vec3(trans[3][0], trans[3][1], trans[3][2])
                # Rotation
                if len(key.rotation_times) > 0:
                    if time < key.rotation_times[0]:
                        rot_ = key.rotations[0]
                        quat = glm.quat(rot_[0], rot_[1], rot_[2], rot_[3])
                        rot = glm.mat4_cast(quat)
                    elif time >= key.rotation_times[-1]:
                        rot_ = key.rotations[-1]
                        quat = glm.quat(rot_[0], rot_[1], rot_[2], rot_[3])
                        rot = glm.mat4_cast(quat)
                    else:
                        for k, _ in enumerate(key.rotation_times):
                            if time < key.rotation_times[k] and key.rotation_times[k - 1] != key.rotation_times[k]:
                                r = (key.rotation_times[k] - time) / (key.rotation_times[k] - key.rotation_times[k - 1])
                                rot_ = key.rotations[k - 1]
                                quat1 = glm.quat(rot_[0], rot_[1], rot_[2], rot_[3])
                                rot_ = key.rotations[k]
                                quat2 = glm.quat(rot_[0], rot_[1], rot_[2], rot_[3])
                                rot1 = glm.mat4_cast(quat1)
                                rot2 = glm.mat4_cast(quat2)
                                rot = (rot1 * r + rot2 * (1 - r))
                                break
                # Scale
                if len(key.scale_times) > 0:
                    if time < key.scale_times[0]:
                        sca = key.scales[0]
                        scale = glm.scale(glm.mat4(1.0), glm.vec3(sca[0], sca[1], sca[2]))
                    elif time >= key.scale_times[-1]:
                        sca = key.scales[-1]
                        scale = glm.scale(glm.mat4(1.0), glm.vec3(sca[0], sca[1], sca[2]))
                    else:
                        for k, _ in enumerate(key.scale_times):
                            if time < key.scale_times[k] and key.scale_times[k - 1] != key.scale_times[k]:
                                r = (key.scale_times[k] - time) / (key.scale_times[k] - key.scale_times[k - 1])
                                sca1 = key.scales[k - 1]
                                sca2 = key.scales[k]
                                scale1 = glm.scale(glm.mat4(1.0), glm.vec3(sca1[0], sca1[1], sca1[2]))
                                scale2 = glm.scale(glm.mat4(1.0), glm.vec3(sca2[0], sca2[1], sca2[2]))
                                scale = (scale1 * r + scale2 * (1 - r))
                                break
                matrix = trans * rot * scale
                node.transform_matrix += matrix * anim.weight
        # ボーンノードのスキニング行列を計算
        self.nodes[0].animate(world)
        
    def get_skinning_matrix(self, mat):
        num_bone = len(mat.node_indexs)
        skin_mat = np.zeros((num_bone, 4, 4), dtype=np.float32)
        for i, node_index in enumerate(mat.node_indexs):
            node = self.nodes[node_index]
            skin_mat[i] = np.array(node.skinning_matrix, dtype=np.float32)
        return skin_mat
        
    def reset_animation_weight(self):
        for anim in self.animations:
            anim.weight = 0.0

class Material:
    def __init__(self):
        self.has_position = False
        self.has_normal = False
        self.has_uv = False
        self.num_vertex = 0
        self.vertexs = []
        self.num_face = 0
        self.faces = []
        self.normals = []
        self.uvs = []
        self.texture_file = ""
        self.vao = None
        self.vbo_vertex = None
        self.vbo_normal = None
        self.vbo_tex_coord = None
        self.ibo_faces = None
        self.texture = None
        self.diffuse_color = [1.0] * 4
        # bone
        self.bones = []
        self.node_indexs = []
        self.vbo_bone_id = None
        self.vbo_bone_weight = None
        #  weight per vertex (Max 4 bones per vertex)
        self.vertex_bone_idxs = []
        self.vertex_weights = []

class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.index = -1
        self.transform_matrix = glm.mat4(0.0)
        self.offset_matrix = glm.mat4(0.0)
        self.combined_matrix = glm.mat4()
        self.skinning_matrix = glm.mat4()
        
    def animate(self, parent):
        self.combined_matrix = parent * self.transform_matrix
        for child in self.children:
            child.animate(self.combined_matrix)
        self.skinning_matrix = self.combined_matrix * self.offset_matrix

class Bone:
    def __init__(self, name):
        self.name = name
        self.weights = []
        self.offset_matrix = glm.mat4(0.0)

class Weight:
    def __init__(self):
        self.vertex_index = -1
        self.weight = 0.0

class Animation:
    def __init__(self):
        self.name = ""
        self.duration = 0.0
        self.ticks_per_second = 0.0
        self.keys = []
        self.time = 0.0
        self.weight = 0.0
    def get_max_time(self):
        if len(self.keys) > 0:
            return self.keys[0].position_times[-1]
        else:
            return 0.0
    def is_over(self):
        return self.time >= self.get_max_time()

class AnimationKey:
    def __init__(self):
        self.position_times = []
        self.positions = []
        self.rotation_times = []
        self.rotations = []
        self.scale_times = []
        self.scales = []
        self.node_name = ""
        self.node = None

def add_node(parentNode, nodes):
    num_child = get_skeleton_node_num_children(parentNode.name)
    for i in range(num_child):
        child_name = get_skeleton_child_node_name(parentNode.name, i)
        node = Node(child_name)
        parentNode.children.append(node)
        node.transform_matrix = glm.mat4(*get_skeleton_transform_matrix(child_name))
        node.index = len(nodes)
        nodes.append(node)
        add_node(node, nodes)

def interate_skeleton_node(node, indent_level=0):
    yield (node, indent_level)
    indent_level += 1
    for child_node in node.children:
        for child_node2, indent_level2 in interate_skeleton_node(child_node, indent_level):
            yield (child_node2, indent_level2)

def show_skeleton_tree(root_node):
    for node, indent_level in interate_skeleton_node(root_node):
        print("{}-{} ({})".format(" "*indent_level*2, node.name, node.index))

if __name__ == "__main__":
    model = Model()
    model.import_file("data/simple_anim.fbx")
    show_skeleton_tree(model.nodes[0])
    """
    print("num_material={}".format(len(model.materials)))
    for i, mat in enumerate(model.materials):
        print()
        print('mat_index=', i)
        print('num_vertex=', mat.num_vertex)
    """
