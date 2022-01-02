import glfw
import glm
import model
from model import ANIM_ID
from h5_reader import H5Reader
import gl_util

MIN_DIST = 1.0
INPUT_COUNT = 60
VIEW_FROM_Y = 1.5
VIEW_LOOKAT_Y = 1.0
VIEW_DIST = 4.3
VIEW_DIST_RATE = 0.3
WEIGHT_ATTENUATION = 0.2

# 入力
INPUT1 = 0x1
INPUT2 = 0x2
INPUT3 = 0x4
INPUT4 = 0x8
INPUT5 = 0x10
INPUT6 = 0x20
INPUT7 = 0x40
INPUT8 = 0x80
INPUT9 = 0x100
INPUT_G = 0x200
INPUT_P = 0x400
INPUT_K = 0x800

INPUT_NOT1 = 0x1000
INPUT_NOT2 = 0x2000
INPUT_NOT3 = 0x4000
INPUT_NOT4 = 0x8000
INPUT_NOT5 = 0x10000
INPUT_NOT6 = 0x20000
INPUT_NOT7 = 0x40000
INPUT_NOT8 = 0x80000
INPUT_NOT9 = 0x100000
INPUT_NOT_G = 0x200000
INPUT_NOT_P = 0x400000
INPUT_NOT_K = 0x800000

INPUT_NULL = 0x40000000
INPUT_END = 0x80000000

# コマンド
CMD26P = [INPUT2, INPUT6, INPUT_P, INPUT_END|20]
CMD5K = [INPUT_NOT_K, INPUT_K, INPUT_END|10]
CMD5P = [INPUT_NOT_P, INPUT_P, INPUT_END|10]
CMD4 = [INPUT4, INPUT_END|1]
CMD6 = [INPUT6, INPUT_END|1]
CMD5 = [INPUT_END|1]

class MOTION:
    def __init__(self, anim_index, command):
        self.anim_index = anim_index
        self.command = command
Motion = [
    MOTION(ANIM_ID.ANIM_KICK, CMD5K),
    MOTION(ANIM_ID.ANIM_PUNCH, CMD5P),
    MOTION(ANIM_ID.ANIM_SHORT_STEP_BACKWARD, CMD4),
    MOTION(ANIM_ID.ANIM_SHORT_STEP_FORWARD, CMD6),
    MOTION(ANIM_ID.ANIM_IDLE, CMD5),
]

class Key:
    def __init__(self, window):
        self.window = window
        self.reset_key()
        self.keys = [glfw.KEY_Z, glfw.KEY_X, glfw.KEY_C]  # ガード、パンチ、キックのキー
        
    def reset_key(self):
        self.down = False
        self.up = False
        self.left = False
        self.right = False
        self.button = [False] * 10
        
    def check_key(self):
        self.reset_key()
        # キーボード
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            self.down = True
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            self.up = True
        if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
            self.left = True
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.right = True
        for i in range(3):
            if glfw.get_key(self.window, self.keys[i]) == glfw.PRESS:
                self.button[i] = True
        # キーパッド
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_X]:  # ガード
                self.button[0] = True
            if state.buttons[glfw.GAMEPAD_BUTTON_A]:  # パンチ
                self.button[1] = True
            if state.buttons[glfw.GAMEPAD_BUTTON_B]:  # キック
                self.button[2] = True
            if state.buttons[glfw.GAMEPAD_BUTTON_LEFT_BUMPER]:
                self.button[5] = True
            if state.buttons[glfw.GAMEPAD_BUTTON_RIGHT_BUMPER]:
                self.button[6] = True
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_UP]:
                self.up = True
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_RIGHT]:
                self.right = True
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_DOWN]:
                self.down = True
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_LEFT]:
                self.left = True
            
    def __str__(self):
        return 'down={}, up={}, left={}, right={}, G={}, P={}, K={}'.format(
            self.down, self.up, self.left, self.right,
            self.button[0], self.button[1], self.button[2])

# キャラクタ
class CPlayer:
    def __init__(self, game, window, ID, model_file, model_name, scale):
        self.game = game
        self.window = window
        self.model = None
        self.anim_index = 0
        self.prev_anim_index = 0
        self.key = Key(window)
        self.reverse = False
        self.input = [0] * INPUT_COUNT
        self.ID = ID
        self.model_file = model_file
        self.model_name = model_name
        self.scale = scale
        self.enemy = None  # CPlayer
        self.pos = glm.vec3([-0.8, 0.8][self.ID], 0.0, 0.0)
        self.yaw = [0.5, 1.5][self.ID] * glm.pi()
        self.cpu = False
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
        
    # 入力の判定
    def check_input(self, command):
        i, j = 0, 0
        while not (command[i] & INPUT_END): i += 1
        time = command[i] & ~INPUT_END
        for i_ in range(i - 1, -1, -1):  # [i-1, i-2, ..., 1, 0]
            input_ = command[i_]
            while j < INPUT_COUNT and (self.input[j] & input_ != input_): j += 1
            if j >= time or j == INPUT_COUNT:
                return False
        return True
        
    def move(self):
        # 入力の更新
        if self.ID == 0:
            self.key.check_key()
        key = self.key
        input_ = 0
        if not self.cpu:
            input_ |= INPUT5 if not key.down and not key.up and not key.left and not key.right else INPUT_NOT5
            input_ |= INPUT2 if key.down else INPUT_NOT2
            input_ |= INPUT8 if key.up else INPUT_NOT8
            input_ |= INPUT_G if key.button[0] else INPUT_NOT_G
            input_ |= INPUT_P if key.button[1] else INPUT_NOT_P
            input_ |= INPUT_K if key.button[2] else INPUT_NOT_K
            if self.reverse:
                input_ |= INPUT6 if key.left else INPUT_NOT6
                input_ |= INPUT4 if key.right else INPUT_NOT4
                input_ |= INPUT3 if key.left and key.down else INPUT_NOT3
                input_ |= INPUT1 if key.right and key.down else INPUT_NOT1
                input_ |= INPUT9 if key.left and key.up else INPUT_NOT9
                input_ |= INPUT7 if key.right and key.up else INPUT_NOT7
            else:
                input_ |= INPUT4 if key.left else INPUT_NOT4
                input_ |= INPUT6 if key.right else INPUT_NOT6
                input_ |= INPUT1 if key.left and key.down else INPUT_NOT1
                input_ |= INPUT3 if key.right and key.down else INPUT_NOT3
                input_ |= INPUT7 if key.left and key.up else INPUT_NOT7
                input_ |= INPUT9 if key.right and key.up else INPUT_NOT9
        
        self.input[1:INPUT_COUNT] = self.input[0:INPUT_COUNT - 1]
        self.input[0] = input_
        
        # 動作の切り替え
        anim = self.get_animation()
        if self.anim_index == ANIM_ID.ANIM_IDLE or \
            self.anim_index == ANIM_ID.ANIM_SHORT_STEP_BACKWARD or \
            self.anim_index == ANIM_ID.ANIM_SHORT_STEP_FORWARD or \
            anim.is_over():
            for motion in Motion:
                if self.check_input(motion.command):
                    self.prev_anim_index = self.anim_index
                    self.anim_index = motion.anim_index
                    break
        
        # アニメーションの進行
        new_anim = self.get_animation()
        if anim != new_anim:
            # 補間
            self.model.save_smoother()
            self.model.smoother_weight = 1.0
            
            # 位置更新
            if self.prev_anim_index != ANIM_ID.ANIM_IDLE:
                self.pos = self.get_center_pos()
            # アニメーション切り替え
            self.model.reset_animation_weight()
            new_anim.weight = 1.0
            new_anim.time = 0.0
        elif anim.is_over():
            # 位置更新
            if self.prev_anim_index != ANIM_ID.ANIM_IDLE:
                self.pos = self.get_center_pos()
            anim.time = 0.0
        else:
            self.model.smoother_weight -= WEIGHT_ATTENUATION
            if self.model.smoother_weight < 0.0: self.model.smoother_weight = 0.0
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
        
