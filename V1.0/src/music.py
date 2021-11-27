import pygame

CHANGE_MENU = 0
SELECT_MENU = 1
SELECT_ITEM = 2
FALLING_DOWN = 3
SMALL_PUNCH =4
SMALL_KICK = 5
MIDDLE_KICK = 6

MUSIC_SELECT_CHARA = 0
MUSIC_FINISH_FIGHT = 1
MUSIC_TITLE = 2
MUSIC_FIGHTING = 3
MUSIC_FIGHTING_2 = 4
MUSIC_FIGHTING_3 = 5

class Music:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = [
            pygame.mixer.Sound("data/SE/change_menu.wav"),
            pygame.mixer.Sound("data/SE/select_menu.wav"),
            pygame.mixer.Sound("data/SE/select_item.wav"),
            pygame.mixer.Sound("data/SE/Falling_Down.wav"),
            pygame.mixer.Sound("data/SE/small_punch.wav"),
            pygame.mixer.Sound("data/SE/small_kick.wav"),
            pygame.mixer.Sound("data/SE/middle_kick.wav"),
        ]
        self.musics = [
            "data/Music/Mearas_StageSelect.mp3",
            "data/Music/yattaze1.mp3",
            "data/Music/MusMus-BGM-020.mp3",
            "data/Music/BGM68_Mixdown.mp3",
            "data/Music/MusMus-BGM-045.mp3",
            "data/Music/MusMus-BGM-067.mp3"
        ]
    
    def play_music(self, music_type, loop=-1, volume=0.5):
        pygame.mixer.music.load(self.musics[music_type])
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)  # -1 is loop endless, 0 is no loop
        
    def stop_music(self):
        pygame.mixer.music.stop()
        
    def play_sound(self, sound_type):
        sound = self.sounds[sound_type]
        sound.play()

