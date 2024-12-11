from flask import Blueprint, request, jsonify
import pymongo
from dotenv import load_dotenv
import os

result_bp = Blueprint('result', __name__)
default_result_bp = Blueprint('default_result', __name__)

# .env 파일에서 MongoDB 연결 정보 로드
load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')

# MongoDB 클라이언트 생성
client = pymongo.MongoClient(MONGO_URL)
db = client['user_actions']  # 'user_actions' 데이터베이스 가져오기
collection = db['user_purchases']  # 'user_purchases' 컬렉션 가져오기

# 기본 preference 결과 ID (MongoDB에서 값을 가져오지 못할 경우 사용)
default_preference_result_id = [1, 2, 3, 4, 5]


db_metadata = client.get_database('service_metadata')
collection_metadata = db_metadata.get_collection('product_metadata')


collection_user_action_metadata = db_metadata.get_collection('user_action_metadata')
@result_bp.route('/ai-api/preference/<int:userId>', methods=['GET'])
def result_preferences(userId):

    try:
        # MongoDB에서 사용자의 productIds 가져오기
        user_data = collection.find_one({'userId': userId})

        if user_data:
            # productIds를 preference 결과 ID로 사용
            preference_result_id = user_data.get('productIds', [])
            product_metadata_list = []
            for product_id in preference_result_id:
                product_metadata = collection_metadata.find_one({'product_id': product_id})
                if product_metadata:
                    del product_metadata['_id']
                    product_metadata_list.append(product_metadata)

        else:
            # 사용자 데이터가 없는 경우, count가 높은 순으로 3개의 productIds 가져오기
            top_product_ids = collection_user_action_metadata.aggregate([
                {'$sort': {'count': -1}},  # count 필드 기준 내림차순 정렬
                {'$limit': 3},  # 상위 3개 문서 가져오기
                {'$project': {'_id': 0, 'productId': 1}}  # productId 필드만 추출
            ])
            top_product_ids = list(top_product_ids)
            preference_result_id = [doc['productId'] for doc in top_product_ids]

            product_metadata_list = []
            for product_id in preference_result_id:
                product_metadata = collection_metadata.find_one({'product_id': product_id})
                if product_metadata:
                    del product_metadata['_id']
                    product_metadata_list.append({'product_id': product_id,
                                                'product' : product_metadata.get('product', {}),
                                                'shorts' :  product_metadata.get('shorts', {})
                                                })

        return jsonify({
            "user_preference_id": preference_result_id,
            "payload": product_metadata_list,
            "message" : "retrieve user-preference-ids"
        }, 200)

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@default_result_bp.route('/ai-api/preference/default', methods=['GET'])
def default_result_preferences():
    try:
        # count가 높은 순으로 3개의 productIds 가져오기
        top_product_ids = collection_user_action_metadata.aggregate([
            {'$sort': {'count': -1}},  # count 필드 기준 내림차순 정렬
            {'$limit': 3},  # 상위 3개 문서 가져오기
            {'$project': {'_id': 0, 'productId': 1}}  # productId 필드만 추출
        ])
        top_product_ids = list(top_product_ids) 
        preference_result_id = [doc['productId'] for doc in top_product_ids]

        # product_metadata 컬렉션에서 product_id에 맞는 데이터 가져오기
        product_metadata_list = []
        for product_id in preference_result_id:
            product_metadata = collection_metadata.find_one({'product_id': product_id})
            if product_metadata:
                del product_metadata['_id']
                print(product_id)

                product_metadata_list.append({'product_id': product_id,
                                              'product' : product_metadata.get('product', {}),
                                              'shorts' :  product_metadata.get('shorts', {})
                                              }) # product_metadata 필드 값만 추가
                
        return jsonify({
            "default_preference_id": product_metadata_list,

            "message": "retrieve default preference ids"
        }, 200)

    except Exception as e:
        return jsonify({'message': str(e)}), 500