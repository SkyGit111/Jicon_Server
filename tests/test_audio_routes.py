# tests/test_audio_routes.py

import os
import shutil
import pytest
import routes.audio_routes as ar

@pytest.fixture(autouse=True)
def mock_audio_deps(monkeypatch):
    """
    Stub out slicing、转写、检测函数，避免执行实际逻辑。
    """
    # 切片解密
    monkeypatch.setattr(ar, "_upload_audio", lambda **kw: None)
    # Whisper 转写
    monkeypatch.setattr(ar, "_convert", lambda filepath, user_id, time, text, length: "transcribed")
    # 伪声检测
    monkeypatch.setattr(ar, "_detect_core", lambda text: [{"label": "fake"}])
    yield


def test_upload_wav_success(auth_client):
    """
    测试完整流程：切片→转写→检测→清理目录。
    """
    data = b"fake audio bytes"
    headers = {
        "Channels": "1",
        "Samplewidth": "2",
        "Samplerate": "16000",
        "Userid": "u1",
        "Time": "t1"
    }
    resp = auth_client.post(
        "/audio/upload_wav",
        data=data,
        headers=headers,
        content_type="application/octet-stream"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    # 核心字段断言
    assert "request_id" in body
    assert body["text"] == "transcribed"
    assert body["detections"] == [{"label": "fake"}]
    # 确保临时目录被清理
    tmp_dir = os.path.join("tmp_audio", body["request_id"])
    assert not os.path.exists(tmp_dir)


@pytest.mark.parametrize("hdrs", [
    # 非法参数：Channels 不能转 int
    ({"Channels": "x", "Samplewidth": "2", "Samplerate": "16000"}),
    # 非法参数：Samplewidth 不能转 int
    ({"Channels": "1", "Samplewidth": "y", "Samplerate": "16000"}),
])
def test_upload_wav_bad_headers(auth_client, hdrs):
    """
    参数格式错误时返回 400。
    """
    resp = auth_client.post(
        "/audio/upload_wav",
        data=b"",
        headers=hdrs,
        content_type="application/octet-stream"
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "音频参数格式错误"


def test_upload_wav_slice_error(auth_client, monkeypatch):
    """
    切片阶段异常应返回 500 并带错误信息。
    """
    def fail_upload(**kw):
        raise RuntimeError("slice fail")
    monkeypatch.setattr(ar, "_upload_audio", fail_upload)
    hdrs = {"Channels":"1","Samplewidth":"2","Samplerate":"16000"}
    resp = auth_client.post("/audio/upload_wav", data=b"data", headers=hdrs)
    assert resp.status_code == 500
    assert "音频切片失败" in resp.get_json()["error"]


def test_upload_wav_transcribe_error(auth_client, monkeypatch):
    """
    转写阶段异常应返回 500 并带错误信息。
    """
    def fail_convert(filepath, user_id, time, text, length):
        raise RuntimeError("trans fail")
    monkeypatch.setattr(ar, "_convert", fail_convert)
    hdrs = {"Channels":"1","Samplewidth":"2","Samplerate":"16000"}
    resp = auth_client.post("/audio/upload_wav", data=b"data", headers=hdrs)
    assert resp.status_code == 500
    assert "音频转写失败" in resp.get_json()["error"]


def test_upload_wav_detect_error(auth_client, monkeypatch):
    """
    检测阶段异常应返回 500 并带错误信息。
    """
    def fail_detect(text):
        raise ValueError("detect fail")
    monkeypatch.setattr(ar, "_detect_core", fail_detect)
    hdrs = {"Channels":"1","Samplewidth":"2","Samplerate":"16000"}
    resp = auth_client.post("/audio/upload_wav", data=b"data", headers=hdrs)
    assert resp.status_code == 500
    assert "伪声检测失败" in resp.get_json()["error"]
