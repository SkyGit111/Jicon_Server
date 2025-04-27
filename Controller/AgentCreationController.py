from flask import Blueprint, request, redirect, jsonify
from flask_jwt_extended import jwt_required

from AIAgent.AgentService import AgentService
from User.UserService import UserService

agentcreationcontroller = Blueprint('agentCreation', __name__)


@agentcreationcontroller.route('/agent/user/creation', methods=['POST'])
@jwt_required()
def agent_creation():
    data = request.get_json()
    name = data.get('name')
    type = data.get('type')
    LLM_id = data.get('LLM_id')
    chatprompt = data.get('chatprompt')
    description = data.get('description')
    creator_id = data.get('creator_id')

    agent_id =  AgentService.creat_agent(name, type, LLM_id, chatprompt, description,creator_id)
    if agent_id:
        return jsonify(message='创建成功',agent_id=agent_id),200
    else:
        return jsonify(message='创建失败'),411
