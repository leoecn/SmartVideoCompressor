#!/usr/bin/env python3
"""
视频压缩脚本测试工具
用于验证脚本功能是否正常
"""

import os
import sys
import subprocess
from pathlib import Path

def test_ffmpeg_installation():
    """测试FFmpeg是否安装正确"""
    print("测试FFmpeg安装...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, check=True)
        if "ffmpeg version" in result.stdout:
            print("✓ FFmpeg安装正确")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg未安装或未添加到PATH")
        print("请先安装FFmpeg: https://ffmpeg.org/download.html")
        return False

def test_script_syntax():
    """测试脚本语法"""
    print("\n测试脚本语法...")
    script_path = Path(__file__).parent / "video_compressor.py"
    
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", str(script_path)],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 脚本语法正确")
            return True
        else:
            print(f"✗ 脚本语法错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_import():
    """测试模块导入"""
    print("\n测试模块导入...")
    try:
        # 将当前目录添加到Python路径
        sys.path.insert(0, str(Path(__file__).parent))
        
        # 尝试导入模块
        import video_compressor
        print("✓ 模块导入成功")
        
        # 测试类实例化
        compressor = video_compressor.VideoCompressor()
        print("✓ 类实例化成功")
        
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

def test_help():
    """测试帮助文档"""
    print("\n测试帮助文档...")
    script_path = Path(__file__).parent / "video_compressor.py"
    
    try:
        result = subprocess.run([sys.executable, str(script_path), "--help"],
                              capture_output=True, text=True)
        if result.returncode == 0 and "usage:" in result.stdout:
            print("✓ 帮助文档正常")
            return True
        else:
            print("✗ 帮助文档异常")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def create_test_video():
    """创建测试视频（如果不存在）"""
    print("\n创建测试视频...")
    test_video_path = Path(__file__).parent / "test_input.mp4"
    
    if test_video_path.exists():
        print(f"✓ 测试视频已存在: {test_video_path}")
        return str(test_video_path)
    
    # 使用FFmpeg创建简单的测试视频
    try:
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "testsrc=duration=10:size=640x360:rate=30",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-f", "lavfi",
            "-i", "sine=frequency=1000:duration=10",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",  # 覆盖输出
            str(test_video_path)
        ]
        
        print("正在创建测试视频（约10秒）...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and test_video_path.exists():
            file_size = test_video_path.stat().st_size / (1024 * 1024)
            print(f"✓ 测试视频创建成功: {test_video_path} ({file_size:.1f}MB)")
            return str(test_video_path)
        else:
            print(f"✗ 创建测试视频失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ 创建测试视频异常: {e}")
        return None

def run_compression_test(input_video):
    """运行压缩测试"""
    print(f"\n运行压缩测试（输入: {input_video}）...")
    script_path = Path(__file__).parent / "video_compressor.py"
    output_path = Path(__file__).parent / "test_output.mp4"
    
    # 清理之前的输出文件
    if output_path.exists():
        output_path.unlink()
    
    try:
        cmd = [
            sys.executable, str(script_path),
            input_video,
            "--target-size", "5",  # 压缩到5MB
            "--preset", "ultrafast",  # 快速测试
            "--output", str(output_path)
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if output_path.exists():
                input_size = Path(input_video).stat().st_size / (1024 * 1024)
                output_size = output_path.stat().st_size / (1024 * 1024)
                compression_ratio = output_size / input_size * 100
                
                print(f"✓ 压缩测试成功")
                print(f"  输入大小: {input_size:.1f}MB")
                print(f"  输出大小: {output_size:.1f}MB")
                print(f"  压缩率: {compression_ratio:.1f}%")
                
                # 清理测试文件
                output_path.unlink()
                return True
            else:
                print("✗ 输出文件未创建")
                return False
        else:
            print(f"✗ 压缩测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 压缩测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("视频压缩脚本测试工具")
    print("=" * 60)
    
    tests = [
        ("FFmpeg安装", test_ffmpeg_installation),
        ("脚本语法", test_script_syntax),
        ("模块导入", test_import),
        ("帮助文档", test_help),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    # 运行基础测试
    for test_name, test_func in tests:
        if test_func():
            passed_tests += 1
    
    # 如果基础测试通过，运行功能测试
    if passed_tests == total_tests:
        print("\n" + "=" * 60)
        print("运行功能测试...")
        print("=" * 60)
        
        # 创建测试视频
        test_video = create_test_video()
        if test_video:
            if run_compression_test(test_video):
                passed_tests += 1
                total_tests += 1
                
                # 清理测试视频
                test_video_path = Path(test_video)
                if test_video_path.exists():
                    test_video_path.unlink()
                    print(f"✓ 清理测试视频: {test_video_path}")
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n✅ 所有测试通过！脚本可以正常使用。")
        print("\n使用说明:")
        print("1. 基本使用: python video_compressor.py input.mp4")
        print("2. 查看帮助: python video_compressor.py --help")
        print("3. 详细文档: 请阅读README.md")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())