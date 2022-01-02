import glm
import numpy as np
import sys

def fit_by_view(MV, bound_box, aspect_ratio, scale_ratio=1.0):
    # バウンドボックスのコーナー点をモデルビュー変換して、ビュー座標のXY値の最大最小値を計算
    minX, minY = [sys.float_info.max] * 2
    maxX, maxY = [-sys.float_info.max] * 2
    center, radius = bound_box.get_sphere()
    max_z_pos = -sys.float_info.max
    points = bound_box.get_corner_points()
    for point in points:
        v = glm.vec4(point[0], point[1], point[2], 1.0)
        v2 = MV * v
        minX = min(minX, v2[0])
        minY = min(minY, v2[1])
        maxX = max(maxX, v2[0])
        maxY = max(maxY, v2[1])
        max_z_pos = max(max_z_pos, abs(v2[2]))
    # Y の範囲をフィットさせる
    bottom = minY
    top = maxY
    height = maxY - minY
    new_width = aspect_ratio * height
    left = -new_width / 2.0
    right = new_width / 2.0
    # P
    left *= scale_ratio
    right *= scale_ratio
    bottom *= scale_ratio
    top *= scale_ratio
    near = 0.0
    far = max_z_pos * 2.0
    P = glm.ortho(left, right, bottom, top, near, far)
    P = np.array(P, dtype=np.float32)
    return P

def fit_by_sphere(MV, bound_box, aspect_ratio, scale_ratio=1.0):
    # モデルの中心をモデルビュー座標変換して、半径を使用してビュー座標のY座標の最大最小値を計算
    center, radius = bound_box.get_sphere()
    v = glm.vec4(center[0], center[1], center[2], 1.0)
    v2 = MV * v
    minY = v2[1] - radius
    maxY = v2[1] + radius
    # Y の範囲をフィットさせる
    bottom = minY
    top = maxY
    height = maxY - minY
    new_width = aspect_ratio * height
    left = v2[0] - new_width / 2.0
    right = v2[0] + new_width / 2.0
    # P
    left *= scale_ratio
    right *= scale_ratio
    bottom *= scale_ratio
    top *= scale_ratio
    z_pos = abs(v2[2])
    near = 0.0
    far = z_pos * 2.0
    P = glm.ortho(left, right, bottom, top, near, far)
    P = np.array(P, dtype=np.float32)
    return P
