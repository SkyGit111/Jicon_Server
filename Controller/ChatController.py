from flask import Blueprint, request, redirect, jsonify, url_for
from flask_jwt_extended import jwt_required

from Chat.ChatEntity import Chat
from Chat.ChatService import ChatService
from AIAgent.AgentService import AgentService
from Market.MarketService import MarketService
from User.UserService import UserService

chatcontoller = Blueprint('chat', __name__)


@chatcontoller.route('/agent/user/chat/creation', methods=['POST'])
@jwt_required()
def chat_init():
    data = request.get_json()
    name = data.get('name')
    chat_id = data.get('chat_id')
    agent_id = data.get('agent_id')
    user_id = data.get('user_id')

    if MarketService.getSubStatus(user_id,agent_id)==False:
        return jsonify(message='会话创建失败,未订阅该机器人'), 432

    chat_id = ChatService.createChat(name, agent_id, user_id, chat_id)
    if chat_id:
        return jsonify(message='会话创建成功', chat_id=chat_id),200

    else:
        return jsonify(message='会话创建失败'),431



@chatcontoller.route('/agent/user/chat/<int:chat_id>', methods=['POST'])
@jwt_required()
def chat_detail(chat_id):
    data = request.get_json()
    question = data.get('question')
    ChatService.add_question(chat_id, {"role": "user", "content": question})
    answer = ChatService.chating(chat_id)
    ChatService.add_answer(chat_id, answer)
    return jsonify(answer), 200


@chatcontoller.route('/agent/chat/save/<int:chat_id>', methods=['POST'])
def chat_save(chat_id):
    ChatService.save_HisMess(chat_id)

    return jsonify(message='保存成功', code=200)


@chatcontoller.route('/agent/user/chat/all', methods=['POST'])
@jwt_required()
def allchat():
    user_id = request.get_json().get('user_id')
    chat_dicts = ChatService.showAllChatOfUser(user_id)
    return jsonify(chat_dicts), 200

@chatcontoller.route('/agent/user/chat/<int:chat_id>', methods=['GET'])
@jwt_required()
def showHisMess(chat_id):
    return jsonify(ChatService.showHistoryMess(chat_id)), 200

@chatcontoller.route('/agent/user/chat/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def removeChat(chat_id):
    ChatService.removeChat(chat_id)
    return jsonify(message='关闭成功'), 200

@chatcontoller.route('/agent/user/chat/delete/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def deleteChat(chat_id):
    ChatService.deleteChat(chat_id)
    return jsonify(message='删除成功'), 200