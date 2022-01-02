import glm
import numpy as np

class Trackball:
    def __init__(self):
        self.is_rot = False    # マウスドラッグ中
        self.start_x = None    # 開始マウスX位置
        self.start_y = None    # 開始マウスY位置
        self.start_qtn = None  # 開始クォータニオン
        self.mdl_qtn = None    # 回転クォータニオン
        self.mdl_rot = None    # 回転行列
        self.width = 640       # ウィンドウXサイズ
        self.height = 480      # ウィンドウYサイズ
        self.set_quaternion(glm.quat())
    def set_quaternion(self, qtn):
        self.is_rot = False
        self.mdl_qtn = qtn
        self.mdl_rot = np.array(glm.mat4_cast(self.mdl_qtn))
    def get_quaternion(self):
        return self.mdl_qtn
    def region(self, w, h):
        self.width = w
        self.height = h
    def start(self, x, y):
        self.start_x = x
        self.start_y = y
        self.start_qtn = glm.quat(self.mdl_qtn)
        self.is_rot = True
    def motion(self, x, y):
        if self.is_rot:
            # マウス位置は左上原点
            dx = x - self.start_x
            dy = y - self.start_y
            
            # ドラッグ開始位置からの変位（ラジアン換算)
            # 横方向はウィンドウ幅が一周分、縦方向はウィンドウ高さが一周分
            # 下方向のマウス移動は+X軸回転、右方向のマウス移動は+Y軸回転
            axis = [0.0] * 3
            axis[0] = 2.0 * glm.pi() * dy / float(self.height)
            axis[1] = 2.0 * glm.pi() * dx / float(self.width)
            axis[2] = 0.0
            
            # ドラッグ開始位置からの回転角度、同時に回転軸を正規化
            rot = np.linalg.norm(axis)  # ラジアン
            if rot == 0.0:
                return
            axis = axis / rot
            
            # ドラッグ開始位置からの差分を元に回転クォータニオンを生成
            dqtn = glm.rotate(glm.quat(), rot, glm.vec3(axis))
           
            # 回転クォータニオンを合成
            self.mdl_qtn = dqtn * self.start_qtn
            
            # クォータニオンからマトリックスに変換
            self.mdl_rot = np.array(glm.mat4_cast(self.mdl_qtn))
    def stop(self):
        self.is_rot = False
    def get(self):
        return self.mdl_rot
    def is_rotating(self):
        return self.is_rot