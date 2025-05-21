from dbsearch.db_search import detect
import whisper

if __name__ == '__main__':

    # model = whisper.load_model("tiny")  转文本应该单开模块
    # result = model.transcribe("audio.mp3")
    # print(result["text"])
    detect("您的银行账户存在风险，请立即转账到安全账户：6228...")
