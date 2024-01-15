# app.py
from flask import Flask, render_template, request, jsonify, make_response
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base 
import services.grpc_gen.grpc_service as ether_grpc

app = Flask(__name__)

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

from models.models import *

Base.metadata.create_all(bind=engine)

@app.route("/")
def home():
    return "Default"

@app.route("/createProposal", methods=['POST'])
def createProposal():
    userId = request.cookies.get("userId")
    if userId == "":
        return {'message':'user unauthorized'}, 401
    user = User.query.filter(User.uid == userId).first()
    if user.isAdmin != True:
        return {'message':'Not access'}, 
    try:
        newProposal = Proposal(
            request.json['header'],
            request.json['description']
        )
    except:
        return '', 400
    session.add(newProposal)
    session.commit()
    serialised = {
        'description':newProposal.description,
        'header':newProposal.header,
        'id': newProposal.pid
    }
    return jsonify(serialised), 201

@app.route("/updateProposal", methods=['POST'])
def updateProposal():
    userId = request.cookies.get("userId")
    if userId == "":
        return {'message':'user unauthorized'}, 401
    user = User.query.filter(User.uid == userId).first()
    if user.isAdmin != True:
        return {'message':'Not access'}, 403
    item = Proposal.query.filter(Proposal.pid == request.json['pid']).first()
    if not item:
        return {'message':'No proposal with this id'}, 400
    try:
        newProposal = Proposal(
            request.json['header'],
            request.json['description']
        )
    except:
        return '', 400
    params = request.json
    for key, value in params.items():
        setattr(item, key, value)
        session.commit()
    session.add(newProposal)
    session.commit()
    serialised = {
        'description':item.description,
        'header':item.header,
        'id': item.pid
    }
    return serialised, 200

@app.route("/deleteProposal", methods=['DELETE'])
def deleteProposal():
    userId = request.cookies.get("userId")
    if userId == "":
        return {'message':'user unauthorized'}, 401
    user = User.query.filter(User.uid == userId).first()
    if user.isAdmin != True:
        return {'message':'Not access'}, 403
    try:
        pid = request.json['pid']
    except:
        return '', 400
    item = Proposal.query.filter(Proposal.pid == pid).first()
    if not item:
        return {'message':'No proposal with this id'}, 400
    session.delete(item)
    session.commit()
    return '', 204

@app.route("/getProposals", methods=['GET'])
def getProposals():
    proposal = Proposal.query.all()
    serialised = []
    for prop in proposal:
        serialised.append({
            'description':prop.description,
            'header':prop.header,
        })
    return jsonify(serialised), 200

@app.route("/register", methods=['POST'])
def registerUser():
    try:
        addr = request.json['addr']
        isAdmin = request.json['isAdmin'] == 'True'
    except:
        return '', 400
    verfiAddress = ether_grpc.VerifyAddress(addr)
    print(verfiAddress)
    if not verfiAddress:
        return {'message':'No valid addres'}, 400
    blockNumber = ether_grpc.GetLatestBlock()
    print(blockNumber)
    newUser = User(
        addr=addr,
        blockNumber=blockNumber,
        isAdmin=isAdmin
    )
    session.add(newUser)
    session.commit()
    item = User.query.filter(User.addr == addr).first()
    res = make_response("Register user")
    res.set_cookie('userId', str(item.uid), max_age=60*60*24*365*2 )
    res.status_code = 200
    return res

@app.route("/createVote", methods=['POST'])
def createVote():
    userId = request.cookies.get("userId")
    if userId == "":
        return {'message':'user unauthorized'}, 401
    user = User.query.filter(User.uid == userId).first()
    userBalance = ether_grpc.GetBalance(user.addr)
    print(userBalance)
    if int(userBalance) <= 0:
        return {'message':'Balance is empty'}, 418
    try:
        vote = request.json['vote']
    except:
        return '', 400
    newVote = Vote(
        vote=vote
    )
    newVote.pid = request.json['pid']
    newVote.blockNumber = user.blockNumber
    newVote.userBalance = userBalance
    session.add(newVote)
    session.commit()
     
    return {'message':'Vote is commit'}, 200


@app.route("/getVotes", methods=['GET'])
def getVotes():
    try:
        proposalId = request.json['pid']
    except:
        return '', 400
    votesFor = Vote.query.filter(db.and_(Vote.pid == proposalId, Vote.vote == True))
    voteFor = 0
    for vote in votesFor:
        voteFor += int(vote.userBalance)
    voteAgainst = 0 
    votesAgainst = Vote.query.filter(db.and_(Vote.pid == proposalId, Vote.vote == False))
    for vote in votesAgainst:
        voteAgainst += int(vote.userBalance)
    proposal = Proposal.query.filter(Proposal.pid == proposalId).first()

    votesRes = {
        'proposal': proposal.header,
        'balancesAgainst':voteAgainst,
        'balancesFor':voteFor,
    }
    return jsonify(votesRes), 200


@app.teardown_appcontext
def shutdown_session(exeption=None):
    session.remove()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)