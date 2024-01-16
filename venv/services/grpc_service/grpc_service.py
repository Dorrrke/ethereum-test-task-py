import grpc

import services.grpc_gen.ether_pb2
import services.grpc_gen.ether_pb2_grpc

def GetBalance(etherAddr):
    with grpc.insecure_channel("localhost:8080") as channel:
        stub = services.grpc_gen.ether_pb2_grpc.EthereumServiceStub(channel)

        response = stub.GetBalance(services.grpc_gen.ether_pb2.GetBalanceRequest(ethereumAddr=etherAddr))
        print("Greet to server " + response.ethereumBalance)
        return response.ethereumBalance

def GetLatestBlock():
    with grpc.insecure_channel("localhost:8080") as channel:
        stub = services.grpc_gen.ether_pb2_grpc.EthereumServiceStub(channel)

        response = stub.GetLatestBlock(services.grpc_gen.ether_pb2.GetLatestBlockRequest())
        print(response.blockNumber + response.date)
        return response.blockNumber

def VerifyAddress(addres):
    with grpc.insecure_channel("localhost:8080") as channel:
        stub = services.grpc_gen.ether_pb2_grpc.EthereumServiceStub(channel)
        response = stub.VerifyAddress(services.grpc_gen.ether_pb2.VerifyAddressRequest(addr=addres))
        print(response.numberValid)
        return response.numberValid