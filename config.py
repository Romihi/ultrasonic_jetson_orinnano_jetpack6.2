# config.py
# coding:utf-8
import os

# 使用するセンサー
#ACTIVE_SENSORS = ["ultrasonic", "camera_0", "camera_1", "imu", "lidar", "opticalflow"]
ACTIVE_SENSORS = ["camera_0"]

# モーターへの入力値 （-1~1で設定）
# スロットル
FORWARD_STRAIGHT = 0.2 #ストレートでの値, joy_accel1でボタンマッピング
FORWARD_CORNER = 0.1 #カーブでの値, joy_accel2でボタンマッピング
STOP = 0
REVERSE = -0.3
# ステアリング
LEFT = -1
NEUTRAL = 0 
RIGHT = 1

# 障害物回避の基準距離
DETECTION_RANGE = 300  # 検知開始距離

# 右手法/左手法での目標範囲
TARGET_RANGE = 200  # 右手法/左手法で共有する目標距離
TARGET_RANGE_ADJUSTMENT = 25  # 目標距離近辺で操作変更を実施する基準値（±）

## PIDパラメータ(PDまでを推奨)
K_P = 0.005 #0.005
K_I = 0.0 #0.00001
K_D = 0.0005 #0.0005

# 判断モード選択
PLAN_LIST = [
    "go_straight",
    "right_left_3",
    "right_left_3_records",
    "wall_follow",
    "wall_follow_pid",
    "nn",
    "cnn",
    "resnet18",
    "dual_camera_6ch",
    "dual_camera_cross_attention",
    "vision_transformer",
    "multimodal",
    "multimodal_attention"
]

PLAN = "cnn"
# wall_follow モード関連パラメータ
HAND_SIDE = "left" # "right", "left"

# right_left_3_records モード関連パラメータ
## 過去の操作値記録回数
RIGHT_LEFT_RECORD_NUMBER = 3

# 復帰モード選択
RECOVERY_MODE = "none" #none, back
RECOVERY_STREERING = LEFT # 復帰時のステアリング値
RECOVERY_TIME_DURATION = 1 #復帰処理を行う時間（秒）
RECOVERY_BRAKING = 1 #ブレーキ回数、ブレーキにはReverseを利用
RECOVERY_RANGE = 130  #　復帰時の判定距離

# 出力系
TERMINAL_PRINT = True
# Thonnyのplotterを使う場合
USE_PLOTTER = False

#↑↑↑体験型イベント向けパラメータはここまで↑↑↑～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～
# 車両調整用パラメータ(motor.pyで調整した後値を入れる)
## ステアリングのPWMの値
STEERING_CENTER_PWM = 405 #400~420:newcar, #340~360:oldcar
STEERING_WIDTH_PWM = 100
STEERING_RIGHT_PWM = STEERING_CENTER_PWM - STEERING_WIDTH_PWM
STEERING_LEFT_PWM = STEERING_CENTER_PWM + STEERING_WIDTH_PWM
### !!!ステアリングを壊さないための上限下限の値設定  
STEERING_HI_LIMIT = 520
STEERING_LO_LIMIT = 300


## アクセルのPWM値
## モーターの回転音を聞き、音が変わらないところが最大/最小値とする
THROTTLE_STOPPED_PWM = 380 #めやす：390:newcar, #370~390:oldcar
THROTTLE_FORWARD_PWM = 300
THROTTLE_REVERSE_PWM = 450
THROTTLE_WIDTH_PWM = 100  #motor.pyの確認用

# NNパラメータ
## モデルのパス
MODEL_DIR = "./models"
#MODEL_NAME = "model_nn_20250109_000745_20250108_2339_record"
MODEL_NAME = "model_cnn_20250108_234447_20250108_2339_record"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

## NNモデルのパラメータ
HIDDEN_DIM = 64 #（隠れ層のノード数）
NUM_HIDDEN_LAYERS = 3 #（隠れ層の数）
BATCH_SIZE = 8
EPOCHS = 30

## モデルの種類
MODEL_TYPE = "regression" #regression, categorical
### categoricalのカテゴリ設定、カテゴリ数は揃える↓　
NUM_CATEGORIES = 3
# -100~100の範囲で小さな値→大きな値の順にする（しないとValueError: bins must increase monotonically.）
CATEGORIES_STEERING = [RIGHT, NEUTRAL, LEFT]
CATEGORIES_THROTTLE = [FORWARD_CORNER, FORWARD_STRAIGHT, FORWARD_CORNER] #Strのカテゴリに合わせて設定
# 超音波センサーの距離値をNORMALIZEするスケール
NORMALIZE_RANGE = 2000

# Vision Transformerの設定
VIT_MODEL_NAME = "vit_tiny_patch16_224"  # 一番軽量なViTモデルを指定
MOBILEVIT_MODEL_NAME = 'mobilevit_xxs'  # 'mobilevit_xxs', 'mobilevit_xs', 'mobilevit_s', etc.


"""一旦保留
bins_Str = [-101] # -101は最小値-100を含むため設定、境界の最大値は100
# 分類の境界：binを設定(pd.cutで使う)
for i in range(NUM_CATEGORIES):
    bins_Str.append((CATEGORIES_STEERING[i]+CATEGORIES_STEERING[min(i+1,NUM_CATEGORIES-1)])/2)
bins_Str[-1] = 100
"""
#↑↑↑ルールベース/機械学習講座向けパラメータはここまで↑↑↑～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～

## 超音波センサの最大測定距離 ~4000(mm)
CUTOFF_RANGE = 2000 
## 超音波センサの測定回数、ultrasonic.pyチェック用
SAMPLING_TIMES = 100

# 超音波センサの設定
## 使う超音波センサ位置の指示、計測ループが遅い場合は数を減らす
#ULTRASONIC_SENSOR_LIST = ["FrLH","Fr","FrRH"]
### ５つ使う場合はこちらをコメントアウト外す
ULTRASONIC_SENSOR_LIST = ["FrLH","Fr","FrRH","LH","RH"]
#ULTRASONIC_SENSOR_LIST = ["LH", "FrLH", "Fr", "FrRH","RH"]
### ８つ使う場合ははこちらのコメントアウト外す
#ULTRASONIC_SENSOR_LIST.extend(["RrRH", "Rr", "RrLH"])

# GPIOピン番号:超音波センサの位置の対応とPWMピンのチャンネル
ULTRASONIC_ECHO_PIN_NUMBER=[11,13,15,29,31,33,35,37]
ULTRASONIC_TRIGER_PIN_NUMBER=[12,16,18,22,32,36,38,40]
ULTRASONIC_ECHO_PINS = {name: ULTRASONIC_ECHO_PIN_NUMBER[i] for i, name in enumerate(ULTRASONIC_SENSOR_LIST)}
ULTRASONIC_TRIG_PINS = {name: ULTRASONIC_TRIGER_PIN_NUMBER[i] for i, name in enumerate(ULTRASONIC_SENSOR_LIST)}

CHANNEL_STEERING = 1 
CHANNEL_THROTTLE = 0 

I2C_BUS_NUMBER = 7 # 1 for RPi, 7 for Jetson Orin Nano

# カメラ
CAMERA_MODE = 4          # カメラモード（3=1080p/30fps, 4=720p/60fps など）
#CAMERA_INDEX = 0         # カメラインデックス defaultで0,1を使っていく
CAMERA_FRAMERATE = 60 #DRIVE_LOOP_HZ
CAMERA_VFLIP = True
CAMERA_HFLIP = True

# 画像
IMAGE_W = 160
IMAGE_H = 120
IMAGE_DEPTH = 3         # default RGB=3, make 1 for mono
#IMSHOW = False #　画像を表示するか

# コントローラー（ジョイスティックの設定）
HAVE_JOYSTICK = True #True
JOYSTICK_STEERING_SCALE = -1.0 # left=-1, right=1に調整
JOYSTICK_THROTTLE_SCALE =  1.0 # reverse=-1, forward=1に調整
#CONTROLLER_TYPE = 'F710'            
JOYSTICK_DEVICE_FILE = "/dev/input/js0" 
## ジョイスティックのボタンとスティック割り当て
# F710の操作設定 #割り当て済み
JOYSTICK_A = 0 #ブレーキ
JOYSTICK_B = 1 #アクセル２
JOYSTICK_X = 2 #アクセル１
JOYSTICK_Y = 3 #記録停止開始
JOYSTICK_LB = 4
JOYSTICK_RB = 5
JOYSTICK_BACK = 6
JOYSTICK_S = 7 #自動/手動走行切り替え
JOYSTICK_LOGICOOL = 8
JOYSTICK_LSTICKB = 9
JOYSTICK_RSTICKB = 10
JOYSTICK_AXIS_LEFT = 0 #ステアリング（左右）
JOYSTICK_AXIS_RIGHT = 4 #スロットル（上下）
JOYSTICK_HAT_LR = 0
JOYSTICK_HAT_DU = 1

# ジャイロを使った動的制御モード選択
MODE_DYNAMIC_CONTROL = "counter_steering" #"lateral_g_throttle"

# オプティカルフローセンサー設定値
# 速度(mm/2)を算出するための調整値、路面から30mmの位置にセンサー設置で0.1程度
POSITION_SCALING_FACTOR =  0.1 

# 走行中のデータ確認用WEBアプリ 下記のport番号に出力
## fpvがONの時は画像保存なし
MONITOR = True #True
MONITOR_PORT = 8000

# 走行記録
## 測定データの保存場所
RECORD_FILE_NAME = "record"
RECORDS_DIRECTORY = "records"
RECORDS_DIRECTORY_ULTRASONIC_TEST = "records/ultrasonic_test.csv"
SAVE_FORMAT = "csv" # csv, ndjson 
IMAGES_DIRECTORY = "images"
