from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import glm
from enum import IntEnum, auto
import random
import model
from model import ANIM_ID
from h5_reader import H5Reader
import gl_util
import ball
import stage
import gauge
import text_renderer
import image_renderer
import title
import select_character
from PIL import ImageFont
import music

MIN_DIST = 1.0
INPUT_COUNT = 60
VIEW_FROM_Y = 1.5
VIEW_LOOKAT_Y = 1.0
VIEW_DIST = 4.3
VIEW_DIST_RATE = 0.3
WEIGHT_ATTENUATION = 0.2
STAGE_SIZE = 9.5

# ゲーム状態
class GAME_STATE(IntEnum):
    STATE_TITLE = 0
    STATE_SELECT_CHARA = auto()
    STATE_LOADING = auto()
    STATE_START_FIGHT = auto()
    STAGE_FIGHTING = auto()
    STATE_FINISH_FIGHT = auto()
    STATE_WINNER = auto()
    STATE_GAME_OVER = auto()
    STATE_QUIT = auto()

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
CMD5K = [INPUT_NOT_K, INPUT_K, INPUT_END|10]
CMD26K = [INPUT2, INPUT3, INPUT6, INPUT_K, INPUT_END|20]
CMD2K = [INPUT_NOT_K, INPUT2|INPUT_K, INPUT_END|10]
CMD6P = [INPUT6, INPUT_NOT6, INPUT6, INPUT_P, INPUT_END|15]
CMD5P = [INPUT_NOT_P, INPUT_P, INPUT_END|10]
CMD5G = [INPUT_NOT_G, INPUT_G, INPUT_END|10]
CMD4 = [INPUT4, INPUT_END|1]
CMD6 = [INPUT6, INPUT_END|1]
CMD5 = [INPUT_END|1]

class MOTION:
    def __init__(self, anim_index, command):
        self.anim_index = anim_index
        self.command = command
Motion = [
    MOTION(ANIM_ID.ANIM_LEG_SWEEP, CMD26K),
    MOTION(ANIM_ID.ANIM_LOW_KICK, CMD2K),
    MOTION(ANIM_ID.ANIM_KICK, CMD5K),
    MOTION(ANIM_ID.ANIM_HOOK, CMD6P),
    MOTION(ANIM_ID.ANIM_PUNCH, CMD5P),
    MOTION(ANIM_ID.ANIM_BLOCK, CMD5G),
    MOTION(ANIM_ID.ANIM_SHORT_STEP_BACKWARD, CMD4),
    MOTION(ANIM_ID.ANIM_SHORT_STEP_FORWARD, CMD6),
    MOTION(ANIM_ID.ANIM_IDLE, CMD5),
]

# 当たり判定
class HIT:
    def __init__(self, node_name, radius):
        self.node_name = node_name
        self.radius = radius
        self.node_index = -1
HitDefense = [
    HIT("mixamorig:Hips", 0.25),
    HIT("mixamorig:Spine2", 0.2),
    HIT("mixamorig:Head", 0.2),
    HIT("mixamorig:HeadTop_End", 0.15),
    HIT("mixamorig:LeftArm", 0.1),
    HIT("mixamorig:LeftForeArm", 0.1),
    HIT("mixamorig:LeftHand", 0.15),
    HIT("mixamorig:RightArm", 0.1),
    HIT("mixamorig:RightForeArm", 0.1),
    HIT("mixamorig:RightHand", 0.15),
    HIT("mixamorig:LeftUpLeg", 0.2),
    HIT("mixamorig:LeftLeg", 0.2),
    HIT("mixamorig:LeftFoot", 0.15),
    HIT("mixamorig:LeftToeBase", 0.1),
    HIT("mixamorig:RightUpLeg", 0.2),
    HIT("mixamorig:RightLeg", 0.2),
    HIT("mixamorig:RightFoot", 0.15),
    HIT("mixamorig:RightToeBase", 0.1),
]
HitAttack = [
    HIT("mixamorig:LeftHandThumb1", 0.1),
    HIT("mixamorig:RightHandThumb1", 0.1),
    HIT("mixamorig:LeftToeBase", 0.1),
    HIT("mixamorig:RightToeBase", 0.1),
]
HitAttackR = [
    HIT("mixamorig:RightHandThumb1", 0.1),
    HIT("mixamorig:LeftHandThumb1", 0.1),
    HIT("mixamorig:RightToeBase", 0.1),
    HIT("mixamorig:LeftToeBase", 0.1),

]
class HIT_ID(IntEnum):
    HIT_P_L = 0
    HIT_P_R = auto()
    HIT_K_L = auto()
    HIT_K_R = auto()

# 攻撃と防御
class ATTACK_POSITION(IntEnum):
    AP_HIGH = 0
    AP_MIDDLE = auto()
    AP_LOW = auto()
    AP_DOWN = auto()
    AP_BLOW = auto()
    AP_COUNT = auto()
class ATTACK:
    def __init__(self, anim_index, position, hit_index, from_time, to_time, wait_time, damage):
        self.anim_index = anim_index
        self.position = position
        self.hit_index = hit_index
        self.from_time = from_time
        self.to_time = to_time
        self.wait_time = wait_time
        self.damage = damage
Attack = [
    ATTACK(ANIM_ID.ANIM_PUNCH, ATTACK_POSITION.AP_MIDDLE, HIT_ID.HIT_P_R, 18, 43, 10, 0.1),
    ATTACK(ANIM_ID.ANIM_HOOK, ATTACK_POSITION.AP_MIDDLE, HIT_ID.HIT_P_L, 25, 42, 10, 0.1),
    ATTACK(ANIM_ID.ANIM_KICK, ATTACK_POSITION.AP_HIGH, HIT_ID.HIT_K_R, 34, 51, 20, 0.1),
    ATTACK(ANIM_ID.ANIM_LOW_KICK, ATTACK_POSITION.AP_LOW, HIT_ID.HIT_K_R, 30, 44, 20, 0.1),
    ATTACK(ANIM_ID.ANIM_LEG_SWEEP, ATTACK_POSITION.AP_LOW, HIT_ID.HIT_K_R, 76, 93, 30, 0.2),
]

# 防御の結果
class DEFENSE_ATTRIBUTE(IntEnum):
    DA_THROWABLE = 1
    DA_COUNTER = 2
    DA_DAMAGE = 4
    DA_GUARD = 8
class DEFENSE:
    def __init__(self, next_anim_index, attribute):
        self.next_anim_index = next_anim_index
        self.attribute = attribute
        self.counter_anim_index = -1
Defense = [
    # 移動
    # ANIM_IDLE
    # ANIM_SHORT_STEP_FORWARD
    # ANIM_SHORT_STEP_BACKWARD
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, -1], DEFENSE_ATTRIBUTE.DA_THROWABLE),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, -1], DEFENSE_ATTRIBUTE.DA_THROWABLE),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, -1], DEFENSE_ATTRIBUTE.DA_THROWABLE),

    # 攻撃
    # ANIM_PUNCH
    # ANIM_HOOK
    # ANIM_KICK
    # ANIM_LOW_KICK
    # ANIM_LEG_SWEEP
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, ANIM_ID.ANIM_STOMACH_HIT], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_COUNTER),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, ANIM_ID.ANIM_STOMACH_HIT], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_COUNTER),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, ANIM_ID.ANIM_STOMACH_HIT], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_COUNTER),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, ANIM_ID.ANIM_STOMACH_HIT], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_COUNTER),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, ANIM_ID.ANIM_STOMACH_HIT], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_COUNTER),
    
    # ガード
    # ANIM_BLOCK
    DEFENSE([-1, -1, -1, -1, -1], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_GUARD),
    
    # ダメージ
    # ANIM_LIGHT_HIT_TO_HEAD
    # ANIM_STOMACH_HIT
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, -1], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_DAMAGE),
    DEFENSE([ANIM_ID.ANIM_LIGHT_HIT_TO_HEAD, ANIM_ID.ANIM_STOMACH_HIT, ANIM_ID.ANIM_STOMACH_HIT, -1, -1], DEFENSE_ATTRIBUTE.DA_THROWABLE|DEFENSE_ATTRIBUTE.DA_DAMAGE),

    # 吹き飛び、ダウン
    # ANIM_FALLING_BACK_DEATH
    DEFENSE([-1, -1, -1, -1, -1], 0),
]

# CPU
class CPU_ACTION:
    def __init__(self, rate, command, repeat):
        self.rate = rate
        self.command = command
        self.repeat = repeat
CPUActionNear = [
    CPU_ACTION(1, CMD26K, 0),
    CPU_ACTION(1, CMD6P, 0),
    CPU_ACTION(1, CMD5P, 0),
    CPU_ACTION(1, CMD5K, 0),
    CPU_ACTION(1, CMD2K, 0),
    CPU_ACTION(1, CMD5G, 0),
    CPU_ACTION(1, CMD5, 20),
    CPU_ACTION(1, CMD4, 20),
    CPU_ACTION(3, CMD6, 50),
]
CPUActionFar = [
    CPU_ACTION(1, CMD6P, 0),
    CPU_ACTION(1, CMD5P, 0),
    CPU_ACTION(1, CMD5G, 0),
    CPU_ACTION(1, CMD5, 20),
    CPU_ACTION(4, CMD6, 50),
    CPU_ACTION(2, CMD4, 30),
    CPU_ACTION(2, CMD2K, 0),
    CPU_ACTION(2, CMD26K, 0),
    CPU_ACTION(2, CMD5K, 0),
]

# Sound
anim_sound_map = {
    ANIM_ID.ANIM_PUNCH: music.SMALL_PUNCH,
    ANIM_ID.ANIM_HOOK: music.SMALL_PUNCH,
    ANIM_ID.ANIM_KICK: music.SMALL_KICK,
    ANIM_ID.ANIM_LOW_KICK: music.SMALL_KICK,
    ANIM_ID.ANIM_LEG_SWEEP: music.MIDDLE_KICK,
    ANIM_ID.ANIM_FALLING_BACK_DEATH: music.FALLING_DOWN
}

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
        self.space = False
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
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.space = True
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
        return 'down={}, up={}, left={}, right={}, space={}, G={}, P={}, K={}'.format(
            self.down, self.up, self.left, self.right, self.space,
            self.button[0], self.button[1], self.button[2])

# キャラクタ
class CPlayer:
    def __init__(self, game, window, ID, model_file, model_name, scale, music):
        self.game = game
        self.window = window
        self.model = None
        self.anim_index = 0
        self.prev_anim_index = 0
        self.key = Key(window)
        self.half_body = False
        self.reverse = False
        self.next_anim_index = -1
        self.input = [0] * INPUT_COUNT
        self.ID = ID
        self.model_file = model_file
        self.model_name = model_name
        self.scale = scale
        self.enemy = None  # CPlayer
        self.wait_time = 0.0
        self.attack_valid = [True] * len(Attack)
        self.pos = glm.vec3([-0.8, 0.8][self.ID], 0.0, 0.0)
        self.yaw = [0.5, 1.5][self.ID] * glm.pi()
        self.cpu = False
        self.cpu_command = None
        self.cpu_command_time = 0
        self.cpu_repeat = 0
        self.hitDefence_nodeIndex = {}
        self.hitAttack_nodeIndex = {}
        self.import_model()
        self.center_frame = self.model.find_node("mixamorig:Hips")
        self.model.center_frame = self.center_frame
        self.music = music
        self.falling_down_se = False
        
    def delete_objects(self):
        for mat in self.model.materials:
            for vbo in [mat.vbo_vertex, mat.vbo_normal, mat.vbo_tex_coord,
                mat.vbo_bone_id, mat.vbo_bone_weight]:
                if vbo:
                    glDeleteBuffers(1, [vbo])
            if mat.vao:
                glDeleteVertexArrays(1, [mat.vao])
            if mat.texture:
                glDeleteTextures(1, [mat.texture])
        
    def reset(self):
        self.input = [0] * INPUT_COUNT
        self.wait_time = 0.0
        self.pos = glm.vec3([-0.8, 0.8][self.ID], 0.0, 0.0)
        self.yaw = [0.5, 1.5][self.ID] * glm.pi()
        
    def import_model(self):
        # メッシュとアニメーション読み込み
        reader = H5Reader(self.model_file)  # DB_ALL_assimp.h5
        reader.read_mesh(self.model_name)
        for anim in reader.model.animations:
            anim.weight = 0.0
        reader.model.animations[self.anim_index].weight = 1.0
        # モデルデータを保持
        self.model = reader.model
        # nodeのインデックスを初期化
        for i in range(len(HitDefense)):
            #HitDefense[i].node_index = self.model.find_node(HitDefense[i].node_name).index
            self.hitDefence_nodeIndex[i] = self.model.find_node(HitDefense[i].node_name).index
        for i in range(len(HitAttack)):
            #HitAttack[i].node_index = self.model.find_node(HitAttack[i].node_name).index
            self.hitAttack_nodeIndex[i] = self.model.find_node(HitAttack[i].node_name).index
        
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
        
    def update_key(self):
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
        else:
            if self.cpu_command is None:
                v = self.enemy.pos - self.pos
                dist = glm.length(v)
                if dist <= MIN_DIST * 1.5:
                    action = CPUActionNear
                    n = len(CPUActionNear)
                else:
                    action = CPUActionFar
                    n = len(CPUActionFar)
                sum = 0
                for i in range(n): sum += action[i].rate
                rate = int(random.random() * sum)
                sum = 0
                for i in range(n-1):
                    sum += action[i].rate;
                    if rate <= sum: break
                self.cpu_command = action[i].command;
                self.cpu_repeat=(int)(random.random() * action[i].repeat)
                self.cpu_command_time=0
            else:
                if self.cpu_command[self.cpu_command_time] & INPUT_END:
                    self.cpu_command_time = 0
                    if self.cpu_repeat > 0:
                        self.cpu_repeat -= 1
                    else:
                        self.cpu_command = None
                if self.cpu_command and not (self.cpu_command[self.cpu_command_time] & INPUT_END):
                    input_ |= self.cpu_command[self.cpu_command_time]
                    self.cpu_command_time += 1
        
        self.input[1:INPUT_COUNT] = self.input[0:INPUT_COUNT - 1]
        self.input[0] = input_
        
    def move(self, state):
        # 入力の更新
        if state == GAME_STATE.STAGE_FIGHTING:
            self.update_key()
        else:
            self.input = [0] * INPUT_COUNT
        
        # 動作の切り替え
        anim = self.get_animation()
        
        # ダメージとガード
        if state == GAME_STATE.STAGE_FIGHTING:
            if self.next_anim_index != -1:
                anim.time = 0.0
                self.anim_index = self.next_anim_index
                self.next_anim_index = -1
            else:
                if self.anim_index == ANIM_ID.ANIM_IDLE or \
                    self.anim_index == ANIM_ID.ANIM_SHORT_STEP_BACKWARD or \
                    self.anim_index == ANIM_ID.ANIM_SHORT_STEP_FORWARD or \
                    (anim.time >= self.wait_time and (Defense[self.anim_index].attribute & (DEFENSE_ATTRIBUTE.DA_DAMAGE))) or \
                    anim.is_over():
                    for motion in Motion:
                        if self.check_input(motion.command):
                            self.prev_anim_index = self.anim_index
                            self.anim_index = motion.anim_index
                            for j in range(len(Attack)): self.attack_valid[j] = True
                            break
        
        if self.anim_index == ANIM_ID.ANIM_FALLING_BACK_DEATH and not self.falling_down_se:
            anim_max_time = anim.get_max_time()
            if (anim_max_time <= 66.5 and anim.time >= 22) or (anim_max_time >= 130.5 and anim.time >= 40):
                self.falling_down_se = True
                self.music.play_sound(anim_sound_map[ANIM_ID.ANIM_FALLING_BACK_DEATH])
        
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
            if state == GAME_STATE.STATE_FINISH_FIGHT or state == GAME_STATE.STATE_WINNER:
                if self.anim_index == ANIM_ID.ANIM_FALLING_BACK_DEATH:
                    anim.time = anim.get_max_time()
                elif self.anim_index != ANIM_ID.ANIM_IDLE:
                    self.prev_anim_index = self.anim_index
                    self.anim_index = ANIM_ID.ANIM_IDLE
                    self.model.save_smoother()
                    self.model.smoother_weight = 1.0
                    self.pos = self.get_center_pos()
                    self.model.reset_animation_weight()
                    new_anim = self.get_animation()
                    new_anim.weight = 1.0
                    new_anim.time = 0.0
                else:
                    #if self.prev_anim_index != ANIM_ID.ANIM_IDLE:
                    #    self.pos = self.get_center_pos()
                    anim.time = 0.0
            else:
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
        self.animate_node()
        
        # ステージ端
        pos = self.get_center_pos()
        if pos.x < -STAGE_SIZE: self.pos.x += -STAGE_SIZE - pos.x
        if pos.x > STAGE_SIZE: self.pos.x += STAGE_SIZE - pos.x
        if pos.z < -STAGE_SIZE: self.pos.z+= -STAGE_SIZE - pos.z
        if pos.z > STAGE_SIZE: self.pos.z += STAGE_SIZE - pos.z
        
    def draw(self):
        model.draw(self)

# ゲーム本体
class DB3DFighterVersus:
    def __init__(self, window, width, height, cpu):
        self.window = window
        self.width = width
        self.height = height
        self.title = None
        self.select_character = None
        self.ball = None
        self.stage = None
        self.hit_mode = 0  # 0: デバッグ非表示、1: 1P攻撃表示, 2P防御表示、2: 1P防御表示, 2P攻撃表示
        self.cpu_mode = 1 if cpu else 0  # cpu_mode; 0: 人間vs人間, 1: 人間vsCPU, 2: CPUvs人間, 3: CPUvsCPU
        self.gauge = [None] * 2
        self.player = [None] * 2
        self.view = glm.mat4()
        self.proj = glm.mat4()
        self.top_view = False
        self.state = GAME_STATE.STATE_TITLE
        self.system_time = 0
        self.system_counter = 0
        self.round_count = 1
        text = "Round 1"
        self.MAX_WIN_COUNT = 3
        font_size = 48
        text_color = (255, 255, 255, 255)
        bk_color = (0, 0, 0, 0)
        font = ImageFont.truetype("msgothic.ttc", font_size, encoding="utf-8")
        self.renderer = text_renderer.text_renderer(text, font_size, text_color, bk_color, width, height)
        self.winner_renderer = None
        self.music = None
        self.title_count = 0
        
    def init_players(self, player_indexs):
        # プレイヤー破棄
        for i in range(2):
            if self.player[i]:
                self.player[i].delete_objects()
        self.player = [None] * 2
        # プレイヤー初期化
        players = ["goku-ssj", "gohan", "dabra", "kidbuu", "android-18", "videl-3"]
        scales = [0.1, 0.1, 10.0, 10.0, 0.1, 10.0]
        for i in range(2):
            self.player[i] = CPlayer(self, self.window, i, model.MODEL_FILE_NAME, players[player_indexs[i]], scales[player_indexs[i]], self.music)
        for i in range(2):
            self.player[i].enemy = self.player[1 - i]
        # モデル初期化
        model.init(self.window, self.width, self.height, self.player[0].model)
        
    def init(self):
        # ボール初期化
        self.ball = ball.CBall(model.MODEL_FILE_NAME, "Ball")
        ball.init()
        # ステージ初期化
        self.stage = stage.CStage()
        stage.init()
        # ビュー行列
        self.view_from = glm.vec3(0, VIEW_FROM_Y, VIEW_DIST)  # reverse Z direction
        lookat = glm.vec3(0.0, VIEW_LOOKAT_Y, 0.0)
        up = glm.vec3(0.0, 1.0, 0.0)
        self.view = glm.lookAt(self.view_from, lookat, up)
        # ゲージ初期化
        for i in range(2):
            self.gauge[i] = gauge.CGauge(i, self.width, self.height)
        gauge.init(self.width, self.height)
        # 音楽初期化
        self.music = music.Music()
        self.music.play_music(music.MUSIC_TITLE)
        # タイトル初期化
        self.title = title.GameTitle(self.window, self.width, self.height, self.music, Key(self.window))
        # キャラ選択初期化
        self.select_character = select_character.SelectChara(self.window, self.width, self.height, self.music, Key(self.window))
        
    # 当たり判定
    def check_hit(self, attack_player_id, attack_hit_id):
        hit_attack = (HitAttackR if self.player[attack_player_id].half_body else HitAttack)[attack_hit_id]
        player = self.player[attack_player_id]
        am = player.model.nodes[player.hitAttack_nodeIndex[attack_hit_id]].combined_matrix
        apos = glm.vec3(am[3][0], am[3][1], am[3][2])
        n = len(HitDefense)
        for i in range(n):
            player = self.player[1-attack_player_id]
            dm = player.model.nodes[player.hitDefence_nodeIndex[i]].combined_matrix
            dpos = glm.vec3(dm[3][0], dm[3][1], dm[3][2])
            dist = apos - dpos
            if glm.length(dist) <= hit_attack.radius + HitDefense[i].radius: return True
        return False
        
    # 移動
    def move(self):
        if self.state == GAME_STATE.STATE_TITLE:
            self.move_title()
        elif self.state == GAME_STATE.STATE_SELECT_CHARA:
            self.move_select_chara()
        elif self.state == GAME_STATE.STATE_LOADING:
            self.move_loading()
        elif self.state == GAME_STATE.STATE_START_FIGHT:
            self.move_start_fight()
        elif self.state == GAME_STATE.STAGE_FIGHTING:
            self.move_fighting()
        elif self.state == GAME_STATE.STATE_FINISH_FIGHT:
            self.move_finish_fight()
        elif self.state == GAME_STATE.STATE_WINNER:
            self.move_winner()
        self.system_time += model.ANIM_TIME_STEP
        
    def move_winner(self):
        self.move_fighting()
        if self.system_time >= 6.0:
            self.state = GAME_STATE.STATE_TITLE
            self.system_time = 0
            self.system_counter = 0
            self.title_count += 1
            self.music.stop_music()
            self.music.play_music(music.MUSIC_TITLE)
            # 位置のリセット
            for i in range(2):
                self.player[i].reset()
            # アニメーションのリセット
            self.player[0].prev_anim_index = -1
            self.player[0].next_anim_index = -1
            self.player[0].anim_index = ANIM_ID.ANIM_IDLE
            self.player[1].prev_anim_index = -1
            self.player[1].next_anim_index = -1
            self.player[1].anim_index = ANIM_ID.ANIM_IDLE
            self.player[0].model.reset_animation_weight()
            new_anim = self.player[0].get_animation()
            new_anim.weight = 1.0
            new_anim.time = 0.0
            self.player[1].model.reset_animation_weight()
            new_anim = self.player[1].get_animation()
            new_anim.weight = 1.0
            new_anim.time = 0.0
            # ゲージのリセット
            for i in range(2):
                self.gauge[i].reset()
                self.gauge[i].win_count = 0
            # ラウンドのリセット
            self.round_count = 1
        
    def is_quit(self):
        return self.state == GAME_STATE.STATE_QUIT
        
    def move_title(self):
        self.title.move()
        if self.title.is_finish():
            if self.title.is_quit():
                self.state = GAME_STATE.STATE_QUIT
                self.music.stop_music()
            else:
                self.cpu_mode = self.title.get_cpu_mode()
                self.title.reset()
                self.state = GAME_STATE.STATE_SELECT_CHARA
                self.system_time = 0
                self.system_counter = 0
                self.music.stop_music()
                self.music.play_music(music.MUSIC_SELECT_CHARA)
        
    def move_loading(self):
        player_indexs = self.select_character.get_player_indexs()
        self.init_players(player_indexs)  # 時間がかかる処理
        self.select_character.reset()
        self.state = GAME_STATE.STATE_START_FIGHT
        self.system_time = 0
        self.system_counter = 0
        music_type = [music.MUSIC_FIGHTING, music.MUSIC_FIGHTING_2, music.MUSIC_FIGHTING_3][self.title_count % 3]
        volume = 0.5
        if music_type == music.MUSIC_FIGHTING_2:
            volume = 0.3
        elif music_type == music.MUSIC_FIGHTING_3:
            volume = 0.4
        self.music.stop_music()
        self.music.play_music(music_type, -1, volume)
        
    def move_select_chara(self):
        self.select_character.move()
        if self.select_character.is_finish():
            self.state = GAME_STATE.STATE_LOADING
            self.system_time = 0
            self.system_counter = 0
            self.music.stop_music()
        
    def move_finish_fight(self):
        self.move_fighting()
        if self.system_time >= 3.0:
            if self.gauge[0].win_count >= self.MAX_WIN_COUNT or self.gauge[1].win_count >= self.MAX_WIN_COUNT:
                self.state = GAME_STATE.STATE_WINNER
                self.system_time = 0
                self.system_counter = 0
                self.music.stop_music()
                self.music.play_music(music.MUSIC_FINISH_FIGHT, 0, 1.0)
                # カメラ―を設定
                x_from, x_to = 0.0, 0.0
                view_dist = VIEW_DIST * 0.6
                if self.gauge[0].win_count >= self.MAX_WIN_COUNT:
                    x_to = self.player[0].pos[0]
                    x_from = x_to + view_dist
                else:
                    x_to = self.player[1].pos[0]
                    x_from = x_to - view_dist
                view_from = glm.vec3(x_from, VIEW_FROM_Y, 0.0)
                lookat = glm.vec3(x_to, VIEW_LOOKAT_Y, 0.0)
                up = glm.vec3(0, 1, 0)
                self.view = glm.lookAt(view_from, lookat, up)
            else:
                self.state = GAME_STATE.STATE_START_FIGHT
                self.system_time = 0
                self.system_counter = 0
                # 位置のリセット
                for i in range(2):
                    self.player[i].reset()
                # アニメーションのリセット
                self.player[0].prev_anim_index = -1
                self.player[0].next_anim_index = -1
                self.player[0].anim_index = ANIM_ID.ANIM_IDLE
                self.player[1].prev_anim_index = -1
                self.player[1].next_anim_index = -1
                self.player[1].anim_index = ANIM_ID.ANIM_IDLE
                self.player[0].model.reset_animation_weight()
                new_anim = self.player[0].get_animation()
                new_anim.weight = 1.0
                new_anim.time = 0.0
                self.player[1].model.reset_animation_weight()
                new_anim = self.player[1].get_animation()
                new_anim.weight = 1.0
                new_anim.time = 0.0
                # ゲージのリセット
                for i in range(2):
                    self.gauge[i].reset()
        
    def move_start_fight(self):
        # カメラの移動
        p0 = self.player[0].get_fixed_center_pos()
        p1 = self.player[1].get_fixed_center_pos()
        center = (p0 + p1) * 0.5
        unit = p0 - p1
        dist = glm.length(unit)
        unit = glm.normalize(unit)
        view_dist = dist * VIEW_DIST * VIEW_DIST_RATE
        if view_dist < VIEW_DIST: view_dist = VIEW_DIST
        delta_angle_deg = 90 / (model.FPS * 1.0)
        curr_ang_deg = 90.0 - delta_angle_deg * self.system_counter
        curr_ang_deg = max(curr_ang_deg, 0)
        cos_x = glm.cos(glm.radians(curr_ang_deg))
        sin_y = glm.sin(glm.radians(curr_ang_deg))
        camera_from = glm.vec3(center.x, VIEW_FROM_Y + sin_y * view_dist, center.z - unit.x * view_dist * cos_x)
        camera_to = glm.vec3(center.x, VIEW_LOOKAT_Y, center.z)
        camera_up = glm.normalize(glm.vec3(0, 1, -1))
        self.view = glm.lookAt(camera_from, camera_to, camera_up)
        # 移動処理
        self.move_fighting()
        if self.system_time > 3.0:
            self.state = GAME_STATE.STAGE_FIGHTING
        self.system_counter += 1
        # 死亡時のSEのリセット
        for i in range(2):
            self.player[i].falling_down_se = False
        
    def move_fighting(self):
        # 一時停止・コマ送りなど
        #if not self.prev_input and self.player[0].key.button[5]: self.hit_mode = (self.hit_mode+1) % 3
        #if not self.prev_input and self.player[0].key.button[6]: self.cpu_mode =(self.cpu_mode + 1) % 4
        self.player[0].cpu = self.cpu_mode == 2 or self.cpu_mode == 3
        self.player[1].cpu = self.cpu_mode == 1 or self.cpu_mode == 3
        
        # プレイヤーの移動
        for i in range(2):
            self.player[i].move(self.state)
        
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
        
        # 攻撃と防御
        for i in range(2):
            player = self.player[i]
            enemy = self.player[1 - i]
            defense = Defense[enemy.anim_index]
            time = player.get_animation().time
            jn = len(Attack)
            for j in range(jn):
                attack = Attack[j]
                if player.attack_valid[j] and \
                    attack.anim_index == player.anim_index and \
                    attack.from_time <= time and time <= attack.to_time and \
                    self.check_hit(i, attack.hit_index):
                    player.attack_valid[j] = False
                    enemy.next_anim_index = defense.next_anim_index[attack.position]
                    enemy.wait_time = attack.wait_time
                    if Defense[enemy.next_anim_index].attribute & DEFENSE_ATTRIBUTE.DA_DAMAGE:
                        self.gauge[1-i].damage(attack.damage)
                        self.music.play_sound(anim_sound_map[attack.anim_index])
                    break
        
        # 死亡判定
        for i in range(2):
            if self.gauge[i].value <= 0 and self.state == GAME_STATE.STAGE_FIGHTING:
                self.gauge[1-i].win_count += 1
                self.gauge[1-i].win_count_updated = True
                self.round_count += 1
                self.state = GAME_STATE.STATE_FINISH_FIGHT
                self.system_time = 0
                self.system_counter = 0
                # アニメーション切り替え
                self.player[i].prev_anim_index = self.player[i].anim_index
                self.player[i].anim_index = ANIM_ID.ANIM_FALLING_BACK_DEATH
                new_anim = self.player[i].get_animation()
                self.player[i].model.reset_animation_weight()
                new_anim.weight = 1.0
                new_anim.time = 0.0
        
        # 間合いと角度の調整
        if dist < MIN_DIST:
            vpos = unit * (MIN_DIST - dist) * 0.5
            self.player[0].pos += vpos
            self.player[1].pos -= vpos
        
        # カメラ調整
        if self.state != GAME_STATE.STATE_START_FIGHT and self.state != GAME_STATE.STATE_WINNER:
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
            
        # ゲージ
        for i in range(2):
            self.gauge[i].move()
        
    def draw(self):
        if self.state == GAME_STATE.STATE_TITLE:
            self.draw_title()
        elif self.state == GAME_STATE.STATE_SELECT_CHARA:
            self.draw_select_chara()
        elif self.state == GAME_STATE.STATE_LOADING:
            self.draw_loading()
        elif self.state == GAME_STATE.STATE_START_FIGHT:
            self.draw_start_fight()
        elif self.state == GAME_STATE.STAGE_FIGHTING:
            self.draw_fighting()
        elif self.state == GAME_STATE.STATE_FINISH_FIGHT:
            self.draw_finish_fight()
        elif self.state == GAME_STATE.STATE_WINNER:
            self.draw_winner()
        
    def draw_title(self):
        self.title.draw(self.system_time)
        
    def draw_loading(self):
        self.select_character.draw_loading(self.system_time)
        
    def draw_select_chara(self):
        self.select_character.draw(self.system_time)
        
    def draw_winner(self):
        self.draw_fighting()
        if not self.winner_renderer:
            width = 400.0
            height = 150.0
            x = (self.width - width) / 2.0
            y = 400.0
            self.winner_renderer = image_renderer.image_renderer(x, y, width, height, "data/image/Winner.png", self.width, self.height)
        self.winner_renderer.draw()
        
    def draw_finish_fight(self):
        self.draw_fighting()
        text = "K.O."
        if self.renderer.text != text:
            self.renderer.set_text(text)
        img_w, img_h = self.renderer.img.size
        x = (self.width - img_w) / 2.0
        y = (self.height - img_h) / 2.0
        self.renderer.draw_text(x, y)
        
    def draw_start_fight(self):
        self.draw_fighting()
        if self.system_time <= 1.5:
            text = "Round {}".format(self.round_count)
            if self.renderer.text != text:
                self.renderer.set_text(text)
            img_w, img_h = self.renderer.img.size
            x = (self.width - img_w) / 2.0
            y = (self.height - img_h) / 2.0
            self.renderer.draw_text(x, y)
        elif self.system_time <= 3.0:
            text = "Ready"
            if self.renderer.text != text:
                self.renderer.set_text(text)
            img_w, img_h = self.renderer.img.size
            x = (self.width - img_w) / 2.0
            y = (self.height - img_h) / 2.0
            self.renderer.draw_text(x, y)
        
    def draw_fighting(self):
        # 射影行列
        w, h = self.width, self.height
        self.proj = glm.perspective(glm.degrees(1.0), w/h, 1.0, 1000.0)
        
        # 行列の設定
        ball.set_view_matrix(self.view)
        ball.set_projection_matrix(self.proj)
        stage.set_view_matrix(self.view)
        stage.set_projection_matrix(self.proj)
        model.set_eye_pos(self.view_from)
        model.set_view_matrix(self.view)
        model.set_projection_matrix(self.proj)
        
        # ステージの描画
        world = glm.mat4()
        self.stage.draw(world)
        
        # キャラクタの描画
        for i in range(2):
            self.player[i].draw()
        
        # 当たり判定
        if self.hit_mode > 0:
            for i in range(2):
                hit = None
                n = 0
                is_attack = True
                if (self.hit_mode + i) % 2 == 0:
                    is_attack = False
                    hit = HitDefense
                    n = len(HitDefense)
                else:
                    hit = HitAttackR if self.player[i].half_body else HitAttack
                    n = len(HitAttack)
                for j in range(n):
                    r = hit[j].radius * (1.0 / self.player[i].scale)
                    scale = glm.scale(glm.mat4(), glm.vec3(r, r, r))
                    player = self.player[i]
                    node_index = -1
                    if is_attack:
                        node_index = player.hitAttack_nodeIndex[j]
                    else:
                        node_index = player.hitDefence_nodeIndex[j]
                    world = player.model.nodes[node_index].combined_matrix * scale
                    if hit == HitAttack or hit == HitAttackR:
                        if self.check_hit(i, j):
                            self.ball.set_color((1.0, 0.0, 0.0, 0.8))  # (0.2, 0.0, 0.0, 0.8)
                        else:
                            self.ball.set_color((0.0, 1.0, 0.0, 0.6))  # (0.0, 0.5, 0.0, 0.6)
                    else:
                        self.ball.set_color((0.0, 0.0, 1.0, 0.4))
                    self.ball.draw(world)
                    
        # ゲージ
        for i in range(2):
            self.gauge[i].draw(self.state == GAME_STATE.STATE_FINISH_FIGHT, self.system_time)

