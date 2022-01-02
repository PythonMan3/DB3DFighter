import glfw
import glm
import model
from model import ANIM_ID
from h5_reader import H5Reader
import gl_util

MIN_DIST = 1.0
VIEW_FROM_Y = 1.5
VIEW_LOOKAT_Y = 1.0
VIEW_DIST = 4.3
VIEW_DIST_RATE = 0.3

button_pressed = False
right_pressed = False
left_pressed = False

# キャラクタ
class CPlayer:
    def __init__(self, game, window, ID, model_file, model_name, scale):
        self.game = game
        self.window = window
        self.model = None
        self.anim_index = 0
        self.prev_anim_index = 0
        self.ID = ID
        self.model_file = model_file
        self.model_name = model_name
        self.scale = scale
        self.enemy = None  # CPlayer
        self.pos = glm.vec3([-0.8, 0.8][self.ID], 0.0, 0.0)
        self.yaw = [0.5, 1.5][self.ID] * glm.pi()
        self.import_model()
        self.center_frame = self.model.find_node("mixamorig:Hips")
        self.model.center_frame = self.center_frame
        
    def import_model(self):
        # メッシュとアニメーション読み込み
        reader = H5Reader(self.model_file)  # DB_ALL_assimp.h5
        reader.read_mesh(self.model_name)
        for anim in reader.model.animations:
            anim.weight = 0.0
        reader.model.animations[self.anim_index].weight = 1.0
        # モデルデータを保持
        self.model = reader.model
        
    # アニメーションの取得
    def get_animation(self):
        return self.model.get_animation(self.anim_index)
        
    def animate_node(self):
        rot = glm.rotate(glm.mat4(), self.yaw, glm.vec3(0.0, 1.0, 0.0))
        trans = glm.translate(glm.mat4(), glm.vec3(self.pos.x, self.pos.y, self.pos.z))
        scale = glm.scale(glm.mat4(1.0), glm.vec3(self.scale, self.scale, self.scale))
        world = trans * rot * scale
        self.model.animate_node(world)
        
    def get_fixed_center_pos(self):
        m = self.center_frame.combined_matrix
        pos = glm.vec3(m[3][0], m[3][1], m[3][2])
        curr_hip_pos = self.model.center_pos[2] * self.scale  # Z値にスケールをかける
        if self.ID == 0:
            adjust_pos = glm.vec3(pos[0] - curr_hip_pos, self.pos[1], self.pos[2])
        elif self.ID == 1:
            adjust_pos = glm.vec3(pos[0] + curr_hip_pos, self.pos[1], self.pos[2])
        return adjust_pos
        
    def get_center_pos(self):
        m = self.center_frame.combined_matrix
        pos = glm.vec3(m[3][0], m[3][1], m[3][2])
        center_key = self.model.animations[self.anim_index].keys[1]  # mixamorig:Hipsチャンネル
        start_hip_pos = center_key.positions[0][2] * self.scale  # Z値にスケールをかける
        adjust_pos = glm.vec3(pos[0] - start_hip_pos, self.pos[1], self.pos[2])
        return adjust_pos
        
    def move(self):
        global button_pressed, right_pressed, left_pressed
        # 入力の更新
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS and not button_pressed: # 右キーが押された場合
            right_pressed = True
            button_pressed = True
        elif glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS and not button_pressed: # 左キーが押された場合
            left_pressed = True
            button_pressed = True
        elif glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.RELEASE and button_pressed:
            right_pressed = False
            left_pressed = False
            button_pressed = False
        
        # 動作の切り替え
        anim = self.get_animation()
        #print(anim.is_over())##
        if not anim.is_over():
            if right_pressed:
                self.prev_anim_index = self.anim_index
                self.anim_index = ANIM_ID.ANIM_SHORT_STEP_FORWARD
            elif left_pressed:
                self.prev_anim_index = self.anim_index
                self.anim_index = ANIM_ID.ANIM_SHORT_STEP_BACKWARD
        else:
            self.prev_anim_index = self.anim_index
            self.anim_index = ANIM_ID.ANIM_IDLE
        
        # アニメーションの進行
        new_anim = self.get_animation()
        if anim != new_anim:
            # 位置更新
            if self.prev_anim_index != ANIM_ID.ANIM_IDLE:
                self.pos = self.get_center_pos()
            # アニメーション切り替え
            self.model.reset_animation_weight()
            new_anim.weight = 1.0
            new_anim.time = 0.0
        elif anim.is_over():
            anim.time = 0.0
        else:
            ticks_per_second = 1.0
            if anim.ticks_per_second != 0.0:
                ticks_per_second = anim.ticks_per_second
            anim.time += model.ANIM_TIME_STEP * ticks_per_second
            #if anim.time >= anim.duration:
            #    anim.time = anim.duration - anim.time
        self.animate_node()
        
    def draw(self, mdl_rot):
        model.draw(self, mdl_rot)

# ゲーム本体
class DB3DFighterVersus:
    def __init__(self, window, width, height, cpu):
        self.window = window
        self.width = width
        self.height = height
        self.player = [None] * 2
        self.view = glm.mat4()
        self.proj = glm.mat4()
        self.top_view = False
        
    def init(self):
        # プレイヤー初期化
        players = ["goku-ssj", "videl-3"]
        scales = [0.1, 10.0]
        for i in range(2):
            self.player[i] = CPlayer(self, self.window, i, model.MODEL_FILE_NAME, players[i], scales[i])
        for i in range(2):
            self.player[i].enemy = self.player[1 - i]
        # モデル初期化
        model.init(self.window, self.width, self.height, self.player[0].model)
        # ビュー行列
        self.view_from = glm.vec3(0, VIEW_FROM_Y, VIEW_DIST)  # reverse Z direction
        lookat = glm.vec3(0.0, VIEW_LOOKAT_Y, 0.0)
        up = glm.vec3(0.0, 1.0, 0.0)
        self.view = glm.lookAt(self.view_from, lookat, up)
        
    # 移動
    def move(self):
        # プレイヤーの移動
        for i in range(2):
            self.player[i].move()
        
        # 調整の準備
        if self.player[0].anim_index == ANIM_ID.ANIM_IDLE:
            p0 = self.player[0].get_fixed_center_pos()
        else:
            p0 = self.player[0].get_center_pos()
        if self.player[1].anim_index == ANIM_ID.ANIM_IDLE:
            p1 = self.player[1].get_fixed_center_pos()
        else:
            p1 = self.player[1].get_center_pos()
        center = (p0 + p1) * 0.5
        unit = p0 - p1
        dist= glm.length(unit)
        unit = glm.normalize(unit)
        
        # 間合いと角度の調整
        if dist < MIN_DIST:
            vpos = unit * (MIN_DIST - dist) * 0.5
            self.player[0].pos += vpos
            self.player[1].pos -= vpos
        
        # カメラ調整
        if dist >= MIN_DIST * 0.5:
            view_dist = dist * VIEW_DIST * VIEW_DIST_RATE
            if view_dist < VIEW_DIST: view_dist = VIEW_DIST
            view_from = [
                glm.vec3(center.x - unit.z * view_dist, VIEW_FROM_Y, center.z + unit.x * view_dist),
                glm.vec3(center.x + unit.z * view_dist, VIEW_FROM_Y, center.z - unit.x * view_dist)
            ]
            d = [0.0] * 2
            for i in range(2):
               v = self.view_from - view_from[i]
               d[i] = glm.length(v)
            self.view_from = view_from[0 if d[0] < d[1] else 1]
            lookat = glm.vec3(center.x, VIEW_LOOKAT_Y, center.z)
            up = glm.vec3(0, 1, 0)
            if self.top_view:
                self.view_from = glm.vec3(center.x, view_dist * 1.2, center.z)
                lookat = glm.vec3(center.x, 0, center.z)
                up = glm.vec3(unit.z, 0, -unit.x)
            self.view = glm.lookAt(self.view_from, lookat, up)
        
    def draw(self, mdl_rot):
        # 射影行列
        w, h = self.width, self.height
        self.proj = glm.perspective(glm.degrees(1.0), w/h, 1.0, 1000.0)
        
        # 行列の設定
        model.set_eye_pos(self.view_from)
        model.set_view_matrix(self.view)
        model.set_projection_matrix(self.proj)
        
        # キャラクタの描画
        for i in range(2):
            self.player[i].draw(mdl_rot)
        
