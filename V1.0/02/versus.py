import glfw
import glm
import model
from h5_reader import H5Reader
import gl_util

VIEW_FROM_Y = 1.5
VIEW_LOOKAT_Y = 1.0
VIEW_DIST = 4.3

# キャラクタ
class CPlayer:
    def __init__(self, game, window, ID, model_file, model_name, scale):
        self.game = game
        self.model = None
        self.anim_index = 0
        self.next_anim_index = -1
        self.ID = ID
        self.model_file = model_file
        self.model_name = model_name
        self.scale = scale
        self.enemy = None  # CPlayer
        self.pos = glm.vec3([-0.8, 0.8][self.ID], 0.0, 0.0)
        self.yaw = [0.5, 1.5][self.ID] * glm.pi()
        self.import_model()
        
    def import_model(self):
        # メッシュとアニメーション読み込み
        reader = H5Reader(self.model_file)
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
        
    def move(self):
        anim = self.get_animation()
        ticks_per_second = 1.0
        if anim.ticks_per_second != 0.0:
            ticks_per_second = anim.ticks_per_second
        anim.time += model.ANIM_TIME_STEP * ticks_per_second
        if anim.time >= anim.duration:
            anim.time = anim.duration - anim.time
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
        
