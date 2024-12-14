from flask import Blueprint, request, jsonify
import requests
import os
import pymongo
from dotenv import load_dotenv

inference_bp = Blueprint('inference', __name__)

#private Callable Functions Set

API_URL = "https://dotblossom.today"
#API_URL = "http://localhost:5000"


load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')
# MongoDB 클라이언트 생성
client = pymongo.MongoClient(MONGO_URL)

# 'product_embedding_prev' 데이터베이스 가져오기 (없으면 생성)
prev_db = client.get_database('product_embedding_prev') 

# 'product_data' 컬렉션 가져오기 (없으면 생성)
prev_collection = prev_db.get_collection('product_data')


@inference_bp.route('/ai-api/invoke/product/embed/<int:productId>', methods=['GET']) 
def embed_product_invoker(productId):
    try:
        # API 엔드포인트 URL 생성
        api_url = f"{API_URL}/infer-api/products/{productId}"
        headers = {'Content-Type': 'application/json'}
        response = requests.get(api_url,headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return jsonify({
            'product_id': productId,
            'message': "success to invoke Product Embedding!"
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@inference_bp.route('/ai-api/invoke/user/embed/<int:userId>', methods=['GET'])
def embed_user_invoker(userId):
    try:
        api_url = f"{API_URL}/infer-api/users/{userId}"
        headers = {'Content-Type': 'application/json'}
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return jsonify({
            'user_id': userId,
            'message': "success to invoke User Embedding!"
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@inference_bp.route('/ai-api/invoke/preference/<int:userId>', methods=['POST'])
def preference_invoker(userId):
    try:
        api_url = f"{API_URL}/infer-api/product/preference/{userId}"
        headers = {'Content-Type': 'application/json'}
        response = requests.get(api_url, headers=headers)  # GET 요청으로 변경
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return jsonify({
            'user_id': userId,
            'message': "success to invoke inference and save preference data key"
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500


#new user is buying something -> pref
@inference_bp.route('/ai-api/invoke/sequential/<int:userId>', methods=['POST'])
def sequential_invoker(userId):
    try:
        # 2. embed_user_invoker 호출 (직접 호출)
        response = embed_user_invoker(userId)


        # 3. preference_invoker 호출 (직접 호출)
        response = preference_invoker(userId)


        # 모든 함수가 성공적으로 실행되면 성공 메시지 반환
        return jsonify({
            'user_id': userId,
            'message': "Successfully invoked all functions sequentially."
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    


#product embed Auto propagations
@inference_bp.route('/ai-api/invoke/sequential/product/embed', methods=['POST'])  
def update_product_embedding():  
    try:
        # product_embedding_prev의 product_data 전체 순회
        for product_data in prev_collection.find({'embed': False}):
            if not product_data.get('embed', True):  # embed가 False인 경우
                product_id = product_data.get('product_id') 
                if product_id is not None:
                    # embed_product_invoker 호출 (productId를 이용)
                    api_url = f"{API_URL}/infer-api/products/{product_id}"
                    headers = {'Content-Type': 'application/json'}
                    response = requests.get(api_url, headers=headers)
                    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

                    prev_collection.update_one(
                        {'_id': product_data['_id']}, 
                        {'$set': {'embed': True}}
                    )   

        return jsonify({
            'message': "Successfully updated product embeddings."
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500