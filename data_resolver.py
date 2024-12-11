from flask import Blueprint, request, jsonify
import pymongo
from dotenv import load_dotenv
import os

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

    
@data_resolver_bp.route('/ai-api/metadata/product/shorts/<int:productId>', methods=['POST'])
def metadata_resolve(productId):
    try:
        # 요청 데이터에서 JSON 데이터 가져오기
        data = request.get_json()
        shorts_data = data.get('shorts', {})  # 'shorts' 데이터 가져오기

        # productId로 기존 데이터 찾기
        product_metadata = collection_metadata.find_one({'product_id': productId})

        if product_metadata:
            # 'shorts' 필드가 없다면 추가
            if 'shorts' not in product_metadata:
                collection_metadata.update_one(
                    {'product_id': productId},
                    {'$set': {'shorts': shorts_data}}
                )
                return jsonify({
                    'message': 'Shorts data added successfully',
                    'product_id': productId,
                    'shorts': shorts_data
                }), 200
            else:
                # 'shorts' 필드가 이미 있다면 업데이트 (덮어쓰기)
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
            return jsonify({'message': 'Product metadata not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)})