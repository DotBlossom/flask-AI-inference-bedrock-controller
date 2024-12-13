from flask import Blueprint, request, jsonify
import pymongo
from dotenv import load_dotenv
import os
import requests

data_resolver_bp = Blueprint('data_resolver', __name__)

load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')
# MongoDB 클라이언트 생성
client = pymongo.MongoClient(MONGO_URL)

# 'product_embedding_prev' 데이터베이스 가져오기 (없으면 생성)
db = client.get_database('product_embedding_prev') 

# 'product_data' 컬렉션 가져오기 (없으면 생성)
collection = db.get_collection('product_data')


db_metadata = client.get_database('service_metadata')
collection_metadata = db_metadata.get_collection('product_metadata')


# called by APIGATEWAY: bedrock Invokers -- json
@data_resolver_bp.route('/ai-api/bedrock/result/<int:productId>', methods=['POST'])
def data_resolve(productId):
    try:
        # 요청 데이터에서 JSON 데이터 가져오기
        data = request.get_json()

        # productId와 JSON 데이터를 MongoDB에 저장
        collection.insert_one({
            'productId': productId,
            'data': data
        })

        return jsonify({
            'message': 'Product data saved successfully',
            'productId': productId
            }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
# called by APIGATEWAY: bedrock Invokers -- json
@data_resolver_bp.route('/ai-api/bedrock/result/<int:productId>', methods=['GET'])
def data_retrieve(productId):

    try:
        # productId를 이용하여 MongoDB에서 데이터 찾기
        product_data = collection.find_one({'productId': productId})

        if product_data:
            # 'data' 필드의 값을 가져옴
            data = product_data.get('data')
            return jsonify({
                'message': 'Product data retrieved successfully',
                'productId': productId,
                'data': data
            }), 200
        else:
            return jsonify({
                'message': 'Product data not found',
                'productId': productId
            }), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

# called by APIGATEWAY: metadata Invokers -- json
@data_resolver_bp.route('/ai-api/metadata/product/<int:productId>', methods=['GET'])
def metadata_retrieve(productId):
    try:
        # productId를 이용하여 MongoDB에서 데이터 찾기
        product_metadata = collection_metadata.find_one({'product_id': productId})

        if product_metadata:
            # 'data' 필드의 값을 가져옴
            data = product_metadata.get('product')
            return jsonify({
                'message': 'Product metadata retrieved successfully',
                'product_id': productId,  # 'product_id' 필드명으로 반환
                'product': data
            }), 200
        else:
            return jsonify({
                'message': 'Product metadata not found',
                'product_id': productId  # 'product_id' 필드명으로 반환
            }), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
    
    
@data_resolver_bp.route('/ai-api/metadata/product/<int:productId>', methods=['POST'])
def metadata_resolve_get(productId):
    try:
        # 요청 데이터에서 JSON 데이터 가져오기
        data = request.get_json()
        product_data = data.get('product', {})

        # productId로 기존 데이터 찾기
        product_metadata = collection_metadata.find_one({'product_id': productId})

        if product_metadata:
            # 'product' 필드 업데이트 (덮어쓰기)
            collection_metadata.update_one(
                {'product_id': productId},
                {'$set': {'product': product_data}}
            )
            return jsonify({
                'message': 'Product metadata updated successfully',
                'product_id': productId
            }), 200

        else:
            # productId로 데이터를 찾지 못했으므로 새로 생성
            collection_metadata.insert_one({
                'product_id': productId,
                'product': product_data
            })
            return jsonify({
                'message': 'Product metadata saved successfully',
                'product_id': productId
            }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@data_resolver_bp.route('/ai-api/metadata/product/shorts/<int:productId>', methods=['POST'])
def metadata_resolve(productId):
    try:
        # 요청 데이터에서 JSON 데이터 가져오기
        data = request.get_json()
        shorts_data = data.get('shorts', {})  # 'shorts' 데이터 가져오기

        # productId로 기존 데이터 찾기
        product_metadata = collection_metadata.find_one({'product_id': productId})

        if product_metadata:
            # 'shorts' 필드 업데이트 (덮어쓰기)
            collection_metadata.update_one(
                {'product_id': productId},
                {'$set': {'shorts': shorts_data}}
            )
            return jsonify({
                'message': 'Shorts data updated successfully',
                'product_id': productId,
                'shorts': shorts_data
            }), 200

        else:
            # productId로 데이터를 찾지 못했으므로 새로 생성
            collection_metadata.insert_one({
                'product_id': productId,
                'shorts': shorts_data
            })
            return jsonify({
                'message': 'Product metadata created with shorts data',
                'product_id': productId,
                'shorts': shorts_data
            }), 200

    except Exception as e:
        return jsonify({'message': str(e)})
    
    
@data_resolver_bp.route('/ai-api/mongo', methods=['POST'])
def save_product():
    try:
        # 요청 본문에서 데이터 추출
        body = request.get_json()
        product_metadata = body.get("product")
        product_id = body.get("product_id")

        if not product_metadata or not product_id:
            return jsonify({'error': 'Missing product_metadata or product_id'}), 400

        # MongoDB에 데이터 저장
        # ... (MongoDB에 데이터 저장하는 코드 추가)

        # Bedrock 관련 처리 수행
        product_metadata_to_str = "product_name : " + product_metadata["product_name"] + '/' + "product_category : " + product_metadata["product_category"]
        bedrock_body = {
            "product_id": product_id,
            "product_metadata_to_str": product_metadata_to_str
        }
        lambda_endpoint = "https://lambda.dotblossom.today/api/bedrock"
        headers = {'Content-Type': 'application/json'}
        bedrock_response = requests.post(lambda_endpoint, headers=headers, json=bedrock_body, timeout=15)
        bedrock_response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        print("Bedrock invoked successfully.")

        # /ai-api/metadata/product/<int:productId> 엔드포인트로 POST 요청 보내기
        api_ctrl_url = "https://dotblossom.today/ai-api/metadata/product/"
        api_url = f"{api_ctrl_url}{product_id}"
        headers = {'Content-Type': 'application/json'}
        data = {"product": product_metadata}
        response = requests.post(api_url, headers=headers, json=data, timeout=15)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        print("Metadata saved successfully.")

        # 성공 응답 반환
        return jsonify({'message': 'Product has been saved and Bedrock invoked'}), 200

    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500