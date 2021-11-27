DB 3D Fighter
V1.0 (2021/11/27)

■概要
PyOpenGLを利用した3Dの格闘ゲームです。

■制作者
PythonMan
GitHub:  https://github.com/PythonMan3
YouTube: https://www.youtube.com/channel/UCKXpN6tEEcDzqXpcvhH0_rw/videos
Twitter: https://twitter.com/MainichiPython

■操作方法
キーボード (ゲームパッドはZ,X,Cの代わりにX,A,B)
  タイトル時:
    Z,X,C,スペースキー: メニュー決定
    上,下キー: メニュー選択
  プレイヤー選択時:
    Z,X,Cキー: キャラ決定
    左,右キー: キャラ選択
  戦闘時:
    Zキー: ガード
    Xキー: パンチ
    Cキー: キック
    下=>右下=>右=>キック: 払い蹴り
    下+キック: ローキック
    右=>右=>パンチ: フック
    左: 後退
    右: 前進

■テスト環境
OS: Windows 10 Pro
メモリ: 16GB
GPU: NVIDIA Quadro M520
言語: Python 3.9.6

■インストール方法および実行方法
手順1: Python 3をインストール
https://www.python.org/downloads/windows/

手順2: 依存する各ライブラリをインストール
(※glfwとPyGLMは指定バージョンをご使用ください。glfwの現時点での最新版2.4.0ではゲームパッド操作が正しく動きませんでした)
glfw==2.1.0
h5py
numpy
Pillow
pygame
PyGLM==1.1.7
PyOpenGL

以下のコマンドでインストール出来ます。
requirements.txt内には、PythonManがテストした時のバージョンが指定されています。
(pipにパスが通っている場合は、pip install -r requirements.txt)

py -m pip install -r requirements.txt

手順3: コマンドプロンプトで実行
コマンドプロンプトを開き、srcフォルダに移動します。
以下のコマンドにより実行します。

py main.py

■免責事項
本プログラムは、使用者の責任においてご利用ください。
万一パソコンなど何らかの損害をこうむった場合、あるいは使用者以外の者に損害を与えた場合など、
プログラムの使用にあたって生じた障害について、制作者(PythonMan)はいっさい責任を負うものではありません。

■利用規約
本プログラムは趣味、勉強目的のご利用を想定しています。
プログラムの販売など有償利用は禁止させて頂きます。
YouTubeなどでのゲーム実況は可能です。

■使用素材
本プログラムで使用した素材はオリジナルの素材のサイトの利用規約に従ってください。

効果音：
[無料効果音で遊ぼう！]
https://taira-komori.jpn.org/attack01.html

[効果音ラボ]
https://soundeffect-lab.info/sound/battle/

ジングル:
[OtoLogic]
https://otologic.jp/free/jing/short1.html

音楽:
[MusMus]
reflectable (MusMus-BGM-067.mp3)
Edge of the galaxy (MusMus-BGM-045.mp3)
https://musmus.main.jp/music_game_03.html
The 4th Dimension (MusMus-BGM-020.mp3)
https://musmus.main.jp/music_game_05.html

[Minstrel's treasure]
BATTLE 2 BREAKS (Mearas_Battle02b.mp3)
Stage Select (Mearas_StageSelect.mp3)
https://takedtm.web.fc2.com/midisozai.html

[BGMusic]
BGM68 (BGM68_Mixdown.mp3)
https://bgmusic.jp/freebgmusic/image/cool/bgm68/

背景：
[Humus]
Yokohama 2
http://www.humus.name/index.php?page=Textures

アニメーション：
[mixamo]
https://www.mixamo.com

3Dモデル：
[Clara.io]
https://clara.io/user/RitamChakraborty
