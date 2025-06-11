# ultrasonic_jetson_orinnano_jetpack6.2
jetpack6.2対応のためにJETGPIOを利用

# JETGPIO超音波センサー セットアップガイド

Jetson Orin NanoでJETGPIOライブラリを使用してHC-SR04超音波センサーを制御するための簡潔なセットアップガイドです。

## 🚀 クイックスタート

### 1. JETGPIOライブラリのインストール

```bash
# JETGPIOをダウンロード・インストール
cd ~
git clone https://github.com/Rubberazer/JETGPIO.git
cd JETGPIO
sudo make
sudo make install

# Orin Nanoでは再起動が必要
sudo reboot
```

### 2. 権限設定

```bash
# ユーザーをkmemグループに追加
sudo usermod -a -G kmem $USER

# /dev/memの権限変更
sudo chmod 660 /dev/mem

# 新しいセッションでグループ変更を反映
newgrp kmem

# 確認
groups
ls -la /dev/mem
```

### 3. プロジェクトファイルのダウンロード

```bash
# プロジェクトディレクトリ作成
mkdir -p ~/jetgpio-ultrasonic
cd ~/jetgpio-ultrasonic

# config.pyを既存プロジェクトからコピー
cp /path/to/your/config.py .

# メインプログラムをダウンロード（後述のコードをコピー）
nano ultrasonic_orinano.py
```

## 🔌 ハードウェア接続

### HC-SR04センサーの接続

**⚠️ 重要**: Echo信号は5V出力ですが、Jetsonは3.3V入力です。**必ず電圧分割回路**を使用してください。

```
HC-SR04 Echo(5V) ─── 1kΩ ─┬─── Jetson GPIO(3.3V)
                            │
                            2kΩ
                            │
                           GND
```

### config.pyの設定例

```python
# config.py - センサーピン設定
ULTRASONIC_SENSOR_LIST = ["FrLH","Fr","FrRH","LH","RH"]

ULTRASONIC_ECHO_PINS = {
    "FrLH": 11,  # Pin 11 (GPIO17)
    "Fr": 13,    # Pin 13 (GPIO27) 
    "FrRH": 15,  # Pin 15 (GPIO22)
    "LH": 29,    # Pin 29 (GPIO5)
    "RH": 31     # Pin 31 (GPIO6)
}

ULTRASONIC_TRIG_PINS = {
    "FrLH": 12,  # Pin 12 (GPIO18)
    "Fr": 16,    # Pin 16 (GPIO23)
    "FrRH": 18,  # Pin 18 (GPIO24)
    "LH": 22,    # Pin 22 (GPIO25)
    "RH": 32     # Pin 32 (GPIO12)
}

# その他の設定
CUTOFF_RANGE = 2000
SAMPLING_TIMES = 100
RIGHT_LEFT_RECORD_NUMBER = 3
RECORDS_DIRECTORY_ULTRASONIC_TEST = "records/ultrasonic_test.csv"
```

## 🏃 実行方法

### ステップ1: 基本動作確認
```bash
cd ~/jetgpio-ultrasonic

# GPIO基本テスト
sudo python3 ultrasonic_orinano.py
# メニューから「3. GPIO基本テスト」を選択
```

### ステップ2: 単一センサーテスト
```bash
# 1つのセンサーでテスト（ハードウェア接続後）
sudo python3 ultrasonic_orinano.py  
# メニューから「1. 単一センサーテスト」を選択
```

### ステップ3: 全センサーテスト
```bash
# すべてのセンサーで測定
sudo python3 ultrasonic_orinano.py
# メニューから「2. 全センサーテスト」を選択
```

## 🔧 トラブルシューティング

### エラー: "JETGPIOライブラリが見つかりません"
```bash
# ライブラリの確認
ls -la /usr/lib/libjetgpio.so

# 見つからない場合、再インストール
cd ~/JETGPIO
sudo make clean
sudo make
sudo make install
```

### エラー: "Permission denied"
```bash
# 権限確認
groups | grep kmem
ls -la /dev/mem

# 権限設定の再実行
sudo usermod -a -G kmem $USER
sudo chmod 660 /dev/mem
newgrp kmem
```

### エラー: "Segmentation fault"
```bash
# config.pyのピン設定を確認
# 特定のピンで問題がある場合、設定を変更
```

### 測定値が不安定
- 配線を確認（特にEcho信号の電圧分割）
- VCCに安定した5V電源を供給
- センサー間の距離を離す

## 📋 実行結果例

### 正常動作時の出力例
```
✓ config.pyを読み込みました
設定されたセンサー: ['FrLH', 'Fr', 'FrRH', 'LH', 'RH']
✓ JETGPIO初期化成功
センサー FrLH のピン設定:
  Echo: Pin 11
  Trig: Pin 12
✓ ピン11を入力モードに設定
✓ ピン12を出力モードに設定
✓ センサー FrLH 初期化完了

測定  1: 1250 mm
測定  2: 1248 mm
測定  3: 1252 mm
```

## 🎯 重要なポイント

1. **必ずOrin Nanoで再起動** - JETGPIOインストール後
2. **Echo信号の電圧分割** - 5V→3.3V変換が必須
3. **権限設定** - kmemグループ追加と/dev/mem権限
4. **config.py設定** - 実際の配線と一致させる

---

**対応デバイス**: Jetson Orin Nano/NX, Orin AGX, Jetson Nano, Xavier NX  
**必要なOS**: Ubuntu 22.04 (JetPack 5.x)  
**センサー**: HC-SR04超音波センサー
