from flask import Blueprint, request, redirect, jsonify
from flask_jwt_extended import jwt_required

from AIAgent.AgentService import AgentService
from Market.MarketService import MarketService

marketcontroller = Blueprint('Market', __name__)


@marketcontroller.route('/market', methods=['GET'])
def showAll():
    agent_dicts = MarketService.showAll()
    return jsonify(agent_dicts),200

@marketcontroller.route('/market/agentdetail/<int:agent_id>', methods=['GET'])
def showOneAgent(agent_id):
    agent = MarketService.showOneAgent(agent_id)
    return jsonify(agent),200


@marketcontroller.route('/market/user/agent/subscribe',methods=['POST'])
@jwt_required()
def subscirbeAgent():
    data = request.get_json()
    user_id = data.get('user_id')
    agent_id = data.get('agent_id')
    startime = data.get('startime')
    duration = data.get('duration')
    if MarketService.subscirbeAgent(user_id, agent_id, startime, duration):
        return jsonify(message='订阅成功'),200
    else:
        return jsonify(message='订阅失败'),431



@marketcontroller.route('/market/user/subs/<int:user_id>',methods=['GET'])
@jwt_required()
def getSubsByUserId(user_id):
    sublist = MarketService.getSubsByUserId(user_id)
    return jsonify(sublist),200


@marketcontroller.route('/market/user/pay',methods=['POST'])
@jwt_required()
def pay():
    if MarketService.pay():
        return jsonify(message='支付成功'),200
    else:
        return jsonify(message='支付失败'),441



@marketcontroller.route('/start', methods=['POST'])
def startAllAgent():
    agents = AgentService.get_all_agent_db()
    for agent in agents:
        AgentService.add_agent(AgentService.agentdb_To_chatagent(agent))
    return jsonify(message='启动所有机器人成功'),200