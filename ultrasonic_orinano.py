#!/usr/bin/env python3
# ultrasonic_orinano.py
# Jetson Orin Nano用 JETGPIO超音波センサープログラム

import os
import time
import numpy as np
import ctypes
from ctypes import c_int

# config.pyをインポート
try:
    import config
    print("✓ config.pyを読み込みました")
    print(f"設定されたセンサー: {config.ULTRASONIC_SENSOR_LIST}")
    print(f"最大測定距離: {config.CUTOFF_RANGE} mm")
    print(f"デフォルト測定回数: {config.SAMPLING_TIMES}")
except ImportError:
    print("✗ config.pyが見つかりません。同じディレクトリに配置してください。")
    print("サンプルconfig.pyを作成しますか？ (y/N): ", end="")
    if input().lower() == 'y':
        create_sample_config()
    exit(1)

def create_sample_config():
    """サンプルconfig.pyを作成"""
    config_content = '''# config.py - 超音波センサー設定

# 使用するセンサー
ULTRASONIC_SENSOR_LIST = ["FrLH","Fr","FrRH","LH","RH"]

# エコーピン設定
ULTRASONIC_ECHO_PINS = {
    "FrLH": 11,  # Pin 11 (GPIO17)
    "Fr": 13,    # Pin 13 (GPIO27)
    "FrRH": 15,  # Pin 15 (GPIO22)
    "LH": 29,    # Pin 29 (GPIO5)
    "RH": 31     # Pin 31 (GPIO6)
}

# トリガーピン設定
ULTRASONIC_TRIG_PINS = {
    "FrLH": 12,  # Pin 12 (GPIO18)
    "Fr": 16,    # Pin 16 (GPIO23)
    "FrRH": 18,  # Pin 18 (GPIO24)
    "LH": 22,    # Pin 22 (GPIO25)
    "RH": 32     # Pin 32 (GPIO12)
}

# 測定設定
CUTOFF_RANGE = 2000                    # 最大測定距離 (mm)
SAMPLING_TIMES = 100                   # デフォルト測定回数
RIGHT_LEFT_RECORD_NUMBER = 3           # 履歴記録数
RECORDS_DIRECTORY_ULTRASONIC_TEST = "records/ultrasonic_test.csv"  # 保存先
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    print("✓ サンプルconfig.pyを作成しました")

class JetsonGPIO:
    """Jetson用JETGPIOラッパークラス"""
    
    HIGH = 1
    LOW = 0
    IN = 0
    OUT = 1
    
    def __init__(self):
        self.lib = None
        self.initialized = False
        self.setup_pins = set()
        self._load_and_init()
    
    def _load_and_init(self):
        """JETGPIOライブラリのロードと初期化"""
        try:
            # JETGPIOライブラリをロード
            self.lib = ctypes.CDLL('/usr/lib/libjetgpio.so')
            
            # 関数シグネチャ設定
            self.lib.gpioInitialise.argtypes = []
            self.lib.gpioInitialise.restype = c_int
            self.lib.gpioSetMode.argtypes = [c_int, c_int]
            self.lib.gpioSetMode.restype = c_int
            self.lib.gpioWrite.argtypes = [c_int, c_int]
            self.lib.gpioWrite.restype = c_int
            self.lib.gpioRead.argtypes = [c_int]
            self.lib.gpioRead.restype = c_int
            
            # GPIO初期化
            result = self.lib.gpioInitialise()
            if result > 0:
                self.initialized = True
                print("✓ JETGPIO初期化成功")
            else:
                print(f"✗ JETGPIO初期化失敗: {result}")
                
        except OSError as e:
            print(f"✗ JETGPIOライブラリが見つかりません: {e}")
            print("インストール手順:")
            print("1. cd ~/")
            print("2. git clone https://github.com/Rubberazer/JETGPIO.git")
            print("3. cd JETGPIO")
            print("4. sudo make && sudo make install")
            print("5. sudo reboot")
        except Exception as e:
            print(f"✗ 予期しないエラー: {e}")
    
    def setup(self, pin, mode, initial=None):
        """GPIOピンの設定"""
        if not self.initialized:
            raise RuntimeError("JETGPIO未初期化")
        
        gpio_mode = 1 if mode == self.OUT else 0
        result = self.lib.gpioSetMode(pin, gpio_mode)
        
        if result <= 0:
            raise RuntimeError(f"ピン{pin}設定失敗 (戻り値: {result})")
        
        self.setup_pins.add(pin)
        print(f"✓ ピン{pin}を{'出力' if mode == self.OUT else '入力'}モードに設定")
        
        if mode == self.OUT and initial is not None:
            self.output(pin, initial)
    
    def output(self, pin, value):
        """GPIO出力"""
        if not self.initialized:
            raise RuntimeError("JETGPIO未初期化")
        
        gpio_value = 1 if value else 0
        result = self.lib.gpioWrite(pin, gpio_value)
        
        if result <= 0:
            raise RuntimeError(f"ピン{pin}出力失敗 (戻り値: {result})")
    
    def input(self, pin):
        """GPIO入力"""
        if not self.initialized:
            raise RuntimeError("JETGPIO未初期化")
        
        result = self.lib.gpioRead(pin)
        return self.HIGH if result > 0 else self.LOW
    
    def cleanup(self):
        """GPIOクリーンアップ"""
        if self.initialized and self.lib:
            for pin in self.setup_pins:
                try:
                    self.lib.gpioSetMode(pin, 0)  # 入力モードに戻す
                except:
                    pass
            
            if hasattr(self.lib, 'gpioTerminate'):
                self.lib.gpioTerminate()
            
            self.setup_pins.clear()
            print("✓ GPIO クリーンアップ完了")

class UltrasonicSensor:
    """超音波センサー制御クラス"""
    
    def __init__(self, sensor_name):
        # config.pyの設定確認
        if sensor_name not in config.ULTRASONIC_SENSOR_LIST:
            raise ValueError(f"センサー '{sensor_name}' はconfig.pyで設定されていません")
        
        self.sensor_name = sensor_name
        self.echo_pin = config.ULTRASONIC_ECHO_PINS[sensor_name]
        self.trig_pin = config.ULTRASONIC_TRIG_PINS[sensor_name]
        
        print(f"センサー {sensor_name} のピン設定:")
        print(f"  Echo: Pin {self.echo_pin}")
        print(f"  Trig: Pin {self.trig_pin}")
        
        # GPIO初期化
        self.gpio = JetsonGPIO()
        if not self.gpio.initialized:
            raise RuntimeError("GPIO初期化失敗")
        
        # ピン設定
        try:
            self.gpio.setup(self.echo_pin, self.gpio.IN)
            self.gpio.setup(self.trig_pin, self.gpio.OUT, initial=self.gpio.LOW)
        except Exception as e:
            print(f"✗ ピン設定エラー: {e}")
            print(f"Pin {self.echo_pin} (Echo) または Pin {self.trig_pin} (Trig) に問題があります")
            raise
        
        # 測定パラメータ（config.pyから取得）
        self.sound_speed_mps = 343  # 音速
        self.cutoff = config.CUTOFF_RANGE
        self.cutofftime = self.cutoff * 2 / 1000 / self.sound_speed_mps
        self.trigger_pulse_s = 10e-6  # 10マイクロ秒
        self.wait_s = 0.06  # 測定間隔
        self.records = np.zeros(config.RIGHT_LEFT_RECORD_NUMBER)
        
        print(f"✓ センサー {sensor_name} 初期化完了")
    
    def measure(self):
        """距離測定"""
        try:
            # トリガー信号送信
            self.gpio.output(self.trig_pin, self.gpio.HIGH)
            time.sleep(self.trigger_pulse_s)
            self.gpio.output(self.trig_pin, self.gpio.LOW)
            
            # エコー信号の立ち上がり待機
            start_time = time.perf_counter()
            while self.gpio.input(self.echo_pin) == self.gpio.LOW:
                sig_off = time.perf_counter()
                if sig_off - start_time > 0.02:  # 20msタイムアウト
                    break
            
            # エコー信号の立ち下がり待機
            while self.gpio.input(self.echo_pin) == self.gpio.HIGH:
                sig_on = time.perf_counter()
                if sig_on - sig_off > self.cutofftime:
                    break
            
            # 距離計算 (音速×時間÷2)
            duration = sig_on - sig_off
            distance = int(duration * self.sound_speed_mps / 2 * 1000)  # mm
            distance = min(distance, self.cutoff)
            
            # ノイズフィルタリング
            if distance < 0:
                print(f"@{self.sensor_name}: ノイズ検出、前回値を使用")
                distance = self.records[0] if self.records[0] > 0 else self.cutoff
            
            # 履歴更新
            self.records = np.insert(self.records, 0, distance)
            self.records = np.delete(self.records, -1)
            
            time.sleep(self.wait_s)
            return distance
            
        except Exception as e:
            print(f"✗ 測定エラー({self.sensor_name}): {e}")
            return self.cutoff
    
    def get_data(self):
        """測定データ取得（互換性のため）"""
        return self.measure()
    
    def cleanup(self):
        """センサークリーンアップ"""
        self.gpio.cleanup()
        print(f"センサー {self.sensor_name} クリーンアップ完了")

def display_config_info():
    """設定情報表示"""
    print("\n=== 設定情報 ===")
    print(f"使用センサー: {config.ULTRASONIC_SENSOR_LIST}")
    print(f"最大測定距離: {config.CUTOFF_RANGE} mm")
    print(f"デフォルト測定回数: {config.SAMPLING_TIMES}")
    print(f"データ保存先: {config.RECORDS_DIRECTORY_ULTRASONIC_TEST}")
    
    print("\n=== ピン配置 ===")
    for sensor_name in config.ULTRASONIC_SENSOR_LIST:
        echo_pin = config.ULTRASONIC_ECHO_PINS[sensor_name]
        trig_pin = config.ULTRASONIC_TRIG_PINS[sensor_name]
        print(f"  {sensor_name}: Echo=Pin{echo_pin}, Trig=Pin{trig_pin}")
    
    print("\n⚠️  注意: Echo信号は5V→3.3V電圧分割が必要です")

def test_gpio_basic():
    """GPIO基本動作テスト"""
    print("\n=== GPIO基本テスト ===")
    
    try:
        gpio = JetsonGPIO()
        if gpio.initialized:
            print("✓ JETGPIO動作確認完了")
            
            # 最初のセンサーのトリガーピンで簡単なテスト
            if config.ULTRASONIC_SENSOR_LIST:
                test_pin = config.ULTRASONIC_TRIG_PINS[config.ULTRASONIC_SENSOR_LIST[0]]
                print(f"Pin {test_pin} でI/Oテスト実行...")
                
                gpio.setup(test_pin, gpio.OUT, initial=gpio.LOW)
                
                for i in range(3):
                    gpio.output(test_pin, gpio.HIGH)
                    time.sleep(0.1)
                    gpio.output(test_pin, gpio.LOW)
                    time.sleep(0.1)
                    print(f"  テスト {i+1}/3 完了")
                
                print("✓ I/Oテスト完了")
            
            gpio.cleanup()
            return True
        else:
            print("✗ JETGPIO初期化失敗")
            return False
            
    except Exception as e:
        print(f"✗ GPIOテストエラー: {e}")
        return False

def test_single_sensor():
    """単一センサーテスト"""
    print("\n=== 単一センサーテスト ===")
    
    if not config.ULTRASONIC_SENSOR_LIST:
        print("✗ センサーが設定されていません")
        return False
    
    # 最初のセンサーでテスト
    sensor_name = config.ULTRASONIC_SENSOR_LIST[0]
    print(f"テスト対象: {sensor_name}")
    
    try:
        sensor = UltrasonicSensor(sensor_name)
        
        print(f"\n{sensor_name}センサーで10回測定を実行します...")
        print("測定中... (Ctrl+Cで中断)")
        
        for i in range(10):
            distance = sensor.measure()
            print(f"測定 {i+1:2d}: {distance:4.0f} mm")
            time.sleep(0.5)
        
        print("\n✓ 単一センサーテスト完了")
        sensor.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ 単一センサーテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_sensors():
    """全センサーテスト"""
    print("\n=== 全センサーテスト ===")
    
    sensors = []
    
    try:
        # 全センサー初期化
        print("センサー初期化中...")
        for sensor_name in config.ULTRASONIC_SENSOR_LIST:
            print(f"  {sensor_name} 初期化中...")
            sensor = UltrasonicSensor(sensor_name)
            sensors.append(sensor)
        
        print(f"✓ 初期化完了: {[s.sensor_name for s in sensors]}")
        
        # 測定実行
        num_measurements = min(20, config.SAMPLING_TIMES)
        distance_stack = np.zeros((0, len(sensors) + 1))  # タイムスタンプ + センサー数
        start_time = time.perf_counter()
        
        print(f"\n{num_measurements}回の測定を開始します...")
        print("測定中... (Ctrl+Cで中断)")
        
        for i in range(num_measurements):
            timestamp = time.perf_counter() - start_time
            distances = []
            
            # 各センサーで測定
            for sensor in sensors:
                distance = sensor.measure()
                distances.append(distance)
            
            # データ記録
            distance_stack = np.vstack((distance_stack, [timestamp] + distances))
            
            # 結果表示
            message = f"[{i+1:2d}/{num_measurements}] {timestamp:6.2f}s: " + ", ".join(
                f"{name}:{dist:4.0f}mm" for name, dist in zip(config.ULTRASONIC_SENSOR_LIST, distances)
            )
            print(message)
        
        # 結果保存
        if len(distance_stack) > 0:
            output_file = config.RECORDS_DIRECTORY_ULTRASONIC_TEST
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # CSV保存
            np.savetxt(output_file, 
                       distance_stack,
                       fmt='%.3f', delimiter=",",
                       header="Timestamp," + ",".join(config.ULTRASONIC_SENSOR_LIST), 
                       comments="")
            
            print(f"\n=== 測定結果 ===")
            print(f"測定回数: {len(distance_stack)}")
            print(f"測定時間: {distance_stack[-1, 0]:.2f}秒")
            print(f"データ保存: {output_file}")
            
            # 統計情報
            averages = np.mean(distance_stack[:, 1:], axis=0)
            print("\n各センサーの平均距離:")
            for i, sensor_name in enumerate(config.ULTRASONIC_SENSOR_LIST):
                print(f"  {sensor_name}: {averages[i]:6.1f} mm")
        
        print("\n✓ 全センサーテスト完了")
        return True
        
    except KeyboardInterrupt:
        print("\n測定を中断しました")
        return True
    except Exception as e:
        print(f"\n✗ 全センサーテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # クリーンアップ
        print("\nクリーンアップ中...")
        for sensor in sensors:
            sensor.cleanup()

def main():
    """メイン関数"""
    print("=== Jetson Orin Nano 超音波センサープログラム ===")
    print("JETGPIO版 - HC-SR04超音波センサー制御")
    
    # 設定情報表示
    display_config_info()
    
    print("\n選択してください:")
    print("1. 単一センサーテスト")
    print("2. 全センサーテスト") 
    print("3. GPIO基本テスト")
    print("4. 設定確認のみ")
    print("5. 終了")
    
    try:
        choice = input("\n選択 (1-5): ").strip()
        
        if choice == "1":
            success = test_single_sensor()
        elif choice == "2":
            success = test_all_sensors()
        elif choice == "3":
            success = test_gpio_basic()
        elif choice == "4":
            print("✓ 設定確認完了")
            return
        elif choice == "5":
            print("プログラムを終了します")
            return
        else:
            print("無効な選択です")
            return
        
        if success:
            print("\n🎉 テスト完了！")
            print("問題なく動作した場合、config.pyの設定は正常です。")
        else:
            print("\n❌ テスト失敗")
            print("エラー内容を確認して、必要に応じて設定を見直してください。")
            
    except KeyboardInterrupt:
        print("\nプログラムを中断しました")
    except Exception as e:
        print(f"\nエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
