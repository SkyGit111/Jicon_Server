from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import wave
import subprocess
from datetime import datetime
import os

AUDIO_CHUNK_DURATION = 10  # 每4秒保存一个文件
FLAC_COMPRESSION_LEVEL = 5  # FLAC压缩级别(0-12)

OUTPUT_FOLDER = "audio_chunks"  # 输出文件夹
# 确保输出目录存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



# 服务端应该预先加载私钥
with open('audiostream/private_key.pem', 'rb') as f:
    PRIVATE_KEY = load_pem_private_key(f.read(), password=None)


def upload_audio(stream, channels, sample_width, sample_rate, user_id, time):
    audio_data = bytearray()
    received_frames = 0
    chunk_counter = 1
    frame_size = channels * sample_width
    target_frames = AUDIO_CHUNK_DURATION * sample_rate

    try:
        # 首先读取加密的AES密钥和IV (RSA加密的AES密钥是256字节 + IV 16字节)
        encrypted_data = stream.read(256 + 16)
        if len(encrypted_data) != 256 + 16:
            return {"status": "error", "message": "Invalid encrypted key size"}

        encrypted_aes_key = encrypted_data[:256]
        iv = encrypted_data[256:]

        # 解密AES密钥
        aes_key = PRIVATE_KEY.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 创建AES解密器
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CFB(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        while True:
            # 读取数据块
            FRAME_SIZE = channels * sample_width
            CHUNK_SIZE = FRAME_SIZE * 170  # 每次读取256帧（1024字节对于16-bit立体声）
            chunk = stream.read(CHUNK_SIZE)  # 与客户端匹配的块大小
            if not chunk:
                break

            decrypted = decryptor.update(chunk)
            audio_data.extend(decrypted)

            # 计算新增的帧数
            new_frames = len(decrypted) // frame_size
            received_frames += new_frames

            if received_frames >= target_frames:
                flac_filename = save_as_flac(audio_data, chunk_counter,
                                             channels, sample_width,
                                             sample_rate, user_id, time)
                audio_data = bytearray()
                received_frames -= target_frames
                chunk_counter += 1

        if len(audio_data) > 0:
            flac_filename = save_as_flac(audio_data, chunk_counter,
                                         channels, sample_width,
                                         sample_rate, user_id, time)

        return {
            "status": "success",
            "chunks_saved": chunk_counter,
            "format": "FLAC"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_as_flac(audio_data, chunk_number, channels, sample_width, sample_rate, user_id, time):
    """将音频数据保存为FLAC文件"""
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_filename = f"{OUTPUT_FOLDER}/temp_{user_id}_{time}_{chunk_number}.wav"

    # 文件名命名方式须按需修改
    flac_filename = f"{OUTPUT_FOLDER}/chunk_{user_id}_{time}_{chunk_number}.flac"

    # 先临时保存为WAV
    with wave.open(wav_filename, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

    # 使用FFmpeg转换为FLAC
    try:
        subprocess.run([
            'ffmpeg',
            '-i', wav_filename,
            '-c:a', 'flac',
            '-compression_level', str(FLAC_COMPRESSION_LEVEL),
            '-y',  # 覆盖已存在文件
            flac_filename
        ], check=True)
    finally:
        # 无论转换是否成功都删除临时WAV文件
        if os.path.exists(wav_filename):
            os.remove(wav_filename)

    print(f"Saved FLAC chunk: {flac_filename}")
    return flac_filename
