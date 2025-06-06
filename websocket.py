import asyncio
import websockets
import json
import os
import wave
import subprocess
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audio_server.log')
    ]
)
logger = logging.getLogger('AudioStreamServer')

# 配置参数
AUDIO_CHUNK_DURATION = 10  # 每10秒保存一个文件
FLAC_COMPRESSION_LEVEL = 5  # FLAC压缩级别(0-12)
OUTPUT_FOLDER = "audio_chunks"  # 输出文件夹
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8765
PRIVATE_KEY_PATH = "audiostream/private_key.pem"

# 确保输出目录存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 加载私钥
try:
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        PRIVATE_KEY = load_pem_private_key(f.read(), password=None, backend=default_backend())
    logger.info("私钥加载成功")
except Exception as e:
    logger.error(f"私钥加载失败: {str(e)}")
    raise


import aiohttp

async def detect(flac_path, metadata,detect_times):
    """通知外部系统有新FLAC文件保存"""
    try:
        url = "http://localhost:5001/audio/detect"  # 替换为你的检测接口地址
        payload = {
            "user_id": metadata["user_id"],
            "timestamp": metadata["time"],
            "flac_file": os.path.basename(flac_path),
            "detect_times":detect_times
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload)as resp:
                pass  # 不等待结果
        logger.info(f"已发送通知: {payload}")
    except Exception as e:
        logger.warning(f"通知失败: {e}")


def save_as_flac(audio_data, chunk_number, metadata):
    """将音频数据保存为FLAC文件"""
    try:
        user_id = metadata["user_id"]
        time = metadata["time"]
        channels = metadata["channels"]
        sample_width = metadata["sample_width"]
        sample_rate = metadata["sample_rate"]

        # 生成文件名
        wav_filename = f"{OUTPUT_FOLDER}/temp_{user_id}_{time}_{chunk_number}.wav"
        flac_filename = f"{OUTPUT_FOLDER}/chunk_{user_id}_{time}_{chunk_number}.flac"

        # 先临时保存为WAV
        with wave.open(wav_filename, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
            logger.info(f"保存临时WAV文件: {wav_filename}")

        # 使用FFmpeg转换为FLAC
        try:
            logger.info(f"开始转换WAV到FLAC: {wav_filename} -> {flac_filename}")
            subprocess.run([
                'ffmpeg',
                '-i', wav_filename,
                '-c:a', 'flac',
                '-compression_level', str(FLAC_COMPRESSION_LEVEL),
                '-y',  # 覆盖已存在文件
                flac_filename
            ], check=True)
            logger.info(f"保存FLAC文件: {flac_filename}")
            return flac_filename
        except subprocess.CalledProcessError as e:
            logger.error(f"FLAC转换失败: {e}")
            return None
        finally:
            # 无论转换是否成功都删除临时WAV文件
            logger.info(f"删除临时WAV文件: {wav_filename}")
            if os.path.exists(wav_filename):
                os.remove(wav_filename)
    except Exception as e:
        logger.error(f"保存FLAC文件时出错: {str(e)}")
        return None

async def audio_stream_handler(websocket, path):
    """处理WebSocket音频流"""
    client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
    logger.info(f"来自 {client_ip} 的新连接")
    """处理跨域请求的连接处理器"""
    origin = websocket.request_headers.get("Origin", "unknown")

    # 允许的来源列表 - 使用您的服务器IP
    server_ip = "47.96.10.103"  # 替换为您的实际服务器IP
    allowed_origins = [
        f"http://{server_ip}",  # HTTP 访问
        f"https://{server_ip}",  # HTTPS 访问
        "http://localhost",  # 本地开发
        "http://127.0.0.1",  # 本地环回地址
        "client"  # Android应用（替换为您的包名）
    ]

    # 打印连接信息
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 客户端连接 | IP: {client_ip} | Origin: {origin}")

    # 检查Origin是否允许
    if origin not in allowed_origins:
        print(f"⚠️ 拒绝跨域请求: {origin} 不在允许列表中")
        await websocket.close(code=1008, reason="Origin not allowed")
        return

    try:
        # 初始化状态
        metadata = {
            "user_id":1,#
            "time": datetime.now().strftime("%Y%m%d"),  #"20250603221307"
            "channels": 1,
            "sample_width": 2,  # 16-bit
            "sample_rate": 16000 # 默认采样率
        }
        aes_key = None
        iv = None
        decryptor = None
        audio_data = bytearray()
        received_frames = 0
        chunk_counter = 1
        frame_size = None
        target_frames = None

        # 检查必要参数
        required_fields = ["user_id", "time", "channels", "sample_width", "sample_rate"]
        if not all(field in metadata for field in required_fields):
            missing = [f for f in required_fields if f not in metadata]
            logger.error(f"缺少必要元数据字段: {missing}")
            await websocket.close(4001, f"Missing required fields: {missing}")
            return
        # 计算帧大小和目标帧数
        frame_size = metadata["channels"] * metadata["sample_width"]
        target_frames = AUDIO_CHUNK_DURATION * metadata["sample_rate"]


        # 2. 接收初始化数据包 (256字节AES密钥 + 16字节IV)
        logger.info("等待初始化包...")
        init_packet = await websocket.recv()
        if len(init_packet) != 256 + 16:
            logger.error(f"无效的初始化包大小: {len(init_packet)}，应为272")
            await websocket.close(4002, "Invalid init packet size")
            return

        encrypted_aes_key = init_packet[:256]
        iv = init_packet[256:]

        # 解密AES密钥
        try:
            logger.info("开始解密AES密钥...")
            aes_key = PRIVATE_KEY.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            logger.info("AES密钥解密成功")
        except Exception as e:
            logger.error(f"AES密钥解密失败: {str(e)}")
            await websocket.close(4003, "Failed to decrypt AES key")
            return

        # logger.info("AES密钥解密成功")
        # 检查AES密钥和IV的长度

        # 创建AES解密器
        try:
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CFB(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            logger.info("AES解密器初始化成功")
        except Exception as e:
            logger.error(f"创建AES解密器失败: {str(e)}")
            await websocket.close(4004, "Failed to create AES decryptor")
            return

        detect_times = 0
        # 3. 处理音频数据流
        async for message in websocket:
            # 检查EOF信号 (全0xFF)
            if all(b == 0xFF for b in message):
                logger.info("接收到EOF信号")
                break

            # 解密音频数据
            try:
                decrypted = decryptor.update(message)
                audio_data.extend(decrypted)

                # 计算新增的帧数
                new_frames = len(decrypted) // frame_size
                received_frames += new_frames

                # 达到时间阈值时保存文件
                if received_frames >= target_frames:
                    logger.info(f"保存音频块 #{chunk_counter}，大小: {len(audio_data)} 字节")
                    if save_as_flac(audio_data, chunk_counter, metadata):
                        audio_data = bytearray()
                        received_frames -= target_frames
                        chunk_counter += 1
                        detect_times += 1
                        asyncio.create_task(detect(
                            f"{OUTPUT_FOLDER}/chunk_{metadata['user_id']}_{metadata['time']}_{chunk_counter}.flac",
                            metadata,
                            detect_times
                        ))
                    else:
                        logger.warning("保存音频块失败")
            except Exception as e:
                logger.error(f"音频数据处理失败: {str(e)}")
                await websocket.close(4005, "Audio processing error")
                return

        # 4. 连接关闭前保存剩余数据
        if len(audio_data) > 0:
            logger.info(f"保存最后音频块 #{chunk_counter}，大小: {len(audio_data)} 字节")
            save_as_flac(audio_data, chunk_counter, metadata)
            detect_times += 1
            asyncio.create_task(detect(
                f"{OUTPUT_FOLDER}/chunk_{metadata['user_id']}_{metadata['time']}_{chunk_counter}.flac",
                metadata,
                detect_times
            ))
        logger.info(f"音频流处理完成，共保存 {chunk_counter} 个块")
        await websocket.close(1000, "Stream completed")

    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"连接关闭: code={e.code}, reason={e.reason}")
    except Exception as e:
        logger.error(f"处理音频流时出错: {str(e)}")
        try:
            await websocket.close(4006, f"Server error: {str(e)}")
        except:
            pass


async def main():
    """启动WebSocket服务器"""
    # 创建支持跨域的服务器
    server = await websockets.serve(
        audio_stream_handler,
        SERVER_HOST,
        SERVER_PORT,
        max_size=10 * 1024 * 1024,  # 10MB最大消息大小
        ping_interval=20,  # 每20秒发送ping
        ping_timeout=60,  # 等待pong的超时时间
    )

    logger.info(f"WebSocket服务器已启动 ws://{SERVER_HOST}:{SERVER_PORT}/audio/upload_flac")

    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("服务器被用户中断")
    finally:
        logger.info("服务器关闭")


if __name__ == "__main__":
    asyncio.run(main())