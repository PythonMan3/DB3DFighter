from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import image_renderer
import music

chara_files = [
    "Select_Goku.PNG",
    "Select_Gohan.PNG",
    "Select_Dabra.PNG",
    "Select_Buu.PNG",
    "Select_Android18.PNG",
    "Select_Videl.PNG"]

name_files = [
    "Select_Name_Goku.PNG",
    "Select_Name_Gohan.PNG",
    "Select_Name_Dabra.PNG",
    "Select_Name_Buu.PNG",
    "Select_Name_Android18.PNG",
    "Select_Name_Videl.PNG"]

button_pressed = [False] * 3

class SelectChara:
    def __init__(self, window, screen_width=640, screen_height=480, music=None):
        self.window = window
        self.charas = []
        self.big_chars = []
        self.char_names = []
        self.initial_pressed = True
        # 背景の初期化
        x = 0
        y = 0
        width = screen_width
        height = screen_height
        self.background = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Select_Background.png", screen_width, screen_height)
        # ロード中の初期化
        self.loading = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Select_Loading.png", screen_width, screen_height)
        # キャラの初期化
        x = 15
        y = 440
        width = 120
        height = 120
        for file in chara_files:
            chara = image_renderer.image_renderer(x, y, width, height, "../src/data/image/" + file, screen_width, screen_height)
            self.charas.append(chara)
            x += 130
        x = 75
        y = 102
        width = 250
        height = 250
        for i, file in enumerate(chara_files):
            texture = self.charas[i].get_texture()
            big_char = image_renderer.image_renderer(x, y, width, height, "", screen_width, screen_height, texture)
            self.big_chars.append(big_char)
        # 名前の初期化
        x = 150
        y = 360
        width = 100
        height = 50
        for file in name_files:
            char_name = image_renderer.image_renderer(x, y, width, height, "../src/data/image/" + file, screen_width, screen_height)
            self.char_names.append(char_name)
        # 枠の初期化
        thick = 2
        x = 15 - thick
        y = 440
        width = 120 + thick * 2
        height = 120 + thick * 2
        self.frame1 = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Select_Frame1.png", screen_width, screen_height)
        x =+ 140 + thick * 2
        self.frame2 = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Select_Frame2.png", screen_width, screen_height)
        self.reset()
        self.music = music
        
    def reset(self):
        self.player_1 = 0
        self.player_2 = 5
        self.player_1_done = False
        self.player_2_done = False
        self.initial_pressed = True
        # 枠の移動
        thick = 2
        x = 15 - thick + 130 * self.player_1
        y = 440
        self.frame1.set_pos(x, y)
        x = 15 - thick + 130 * self.player_2
        self.frame2.set_pos(x, y)
        
    def move(self):
        global button_pressed
        ## Button Release
        zxc_released = False
        joystick_button_released = False
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if not state.buttons[glfw.GAMEPAD_BUTTON_X] and \
                not state.buttons[glfw.GAMEPAD_BUTTON_A] and \
                not state.buttons[glfw.GAMEPAD_BUTTON_B]:
                joystick_button_released = True
        else:
            joystick_button_released = True
        keyboard_button_released = (glfw.get_key(self.window, glfw.KEY_Z) == glfw.RELEASE and \
            glfw.get_key(self.window, glfw.KEY_X) == glfw.RELEASE and \
            glfw.get_key(self.window, glfw.KEY_C) == glfw.RELEASE)
        if joystick_button_released and keyboard_button_released:
            zxc_released = True
        # 選択画面に入った時にボタンが押されていたら、離されるまで操作不可にする
        if zxc_released:
            self.initial_pressed = False
        if self.initial_pressed: return
        # キー操作とジョイスティック操作
        ## Right Press
        right_pressed = glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_RIGHT]:
                right_pressed = True
        ## Right Release
        right_released = False
        joystic_right_released = False
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if not state.buttons[glfw.GAMEPAD_BUTTON_DPAD_RIGHT]:
                joystic_right_released = True
        else:
            joystic_right_released = True
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.RELEASE and joystic_right_released:
            right_released = True
        ## Left Press
        left_pressed = glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_LEFT]:
                left_pressed = True
        ## Left Release
        left_released = False
        joystic_left_released = False
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if not state.buttons[glfw.GAMEPAD_BUTTON_DPAD_LEFT]:
                joystic_left_released = True
        else:
            joystic_left_released = True
        if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.RELEASE and joystic_left_released:
            left_released = True
        ## Button Press
        zxc_pressed = (glfw.get_key(self.window, glfw.KEY_Z) == glfw.PRESS or \
            glfw.get_key(self.window, glfw.KEY_X) == glfw.PRESS or \
            glfw.get_key(self.window, glfw.KEY_C) == glfw.PRESS)
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_X] or \
                state.buttons[glfw.GAMEPAD_BUTTON_A] or \
                state.buttons[glfw.GAMEPAD_BUTTON_B]:
                zxc_pressed = True
        # ボタン押下時の処理
        if right_pressed and not button_pressed[0]:
            button_pressed[0] = True
            if not self.player_1_done:
                self.player_1 = (self.player_1 + 1) % 6
            else:
                self.player_2 = (self.player_2 + 1) % 6
            self.music.play_sound(music.CHANGE_MENU)
        elif right_released and button_pressed[0]:
            button_pressed[0] = False
        elif left_pressed and not button_pressed[1]:
            button_pressed[1] = True
            if not self.player_1_done:
                self.player_1 = (self.player_1 - 1) % 6
            else:
                self.player_2 = (self.player_2 - 1) % 6
            self.music.play_sound(music.CHANGE_MENU)
        elif left_released and button_pressed[1]:
            button_pressed[1] = False
        elif zxc_pressed and not button_pressed[2]:
            button_pressed[2] = True
            if not self.player_1_done:
                self.player_1_done = True
            elif not self.player_2_done:
                self.player_2_done = True
            self.music.play_sound(music.SELECT_ITEM)
        elif zxc_released and button_pressed[2]:
            button_pressed[2] = False
        # 枠の移動
        thick = 2
        x = 15 - thick + 130 * self.player_1
        y = 440
        self.frame1.set_pos(x, y)
        x = 15 - thick + 130 * self.player_2
        self.frame2.set_pos(x, y)
        
    def get_player_indexs(self):
        return [self.player_1, self.player_2]
        
    def is_finish(self):
        return self.player_1_done and self.player_2_done
        
    def draw_loading(self, system_time):
        self.loading.draw()
        # 選択キャラの表示
        char1 = self.big_chars[self.player_1]
        x = 75
        y = 102
        char1.set_pos(x, y)
        char1.draw()
        char2 = self.big_chars[self.player_2]
        x = 325 + 140
        y = 102
        char2.set_pos(x, y)
        char2.draw()
        # 選択キャラの名前表示
        char1_name = self.char_names[self.player_1]
        x = 150
        y = 360
        char1_name.set_pos(x, y)
        char1_name.draw()
        char2_name = self.char_names[self.player_2]
        x = 540
        y = 360
        char2_name.set_pos(x, y)
        char2_name.draw()
        
    def draw(self, system_time):
        self.background.draw()
        # 一覧キャラの表示
        for chara in self.charas:
            chara.draw()
        # 選択キャラの表示
        char1 = self.big_chars[self.player_1]
        x = 75
        y = 102
        char1.set_pos(x, y)
        char1.draw()
        char2 = self.big_chars[self.player_2]
        x = 325 + 140
        y = 102
        char2.set_pos(x, y)
        char2.draw()
        # 選択キャラの名前表示
        char1_name = self.char_names[self.player_1]
        x = 150
        y = 360
        char1_name.set_pos(x, y)
        char1_name.draw()
        char2_name = self.char_names[self.player_2]
        x = 540
        y = 360
        char2_name.set_pos(x, y)
        char2_name.draw()
        # 枠の描画
        if not self.player_1_done:
            self.frame1.draw()
        else:
            self.frame2.draw()
