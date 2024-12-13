from flask import Blueprint, request, jsonify
import pymongo
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import requests

# inference를 스케줄로 call 해도 됨. instant도 만들어.


user_actions_bp = Blueprint('user_actions', __name__)
load_dotenv()
#private Callable Functions Set




# MongoDB Atlas 연결 정보

MONGO_URL = os.getenv('MONGO_URL')

API_URL = "https://dotblossom.today"
# MongoDB 클라이언트 생성
client = pymongo.MongoClient(MONGO_URL)
db = client['user_actions']  # 'user_actions' 데이터베이스 가져오기
collection = db['user_purchases']  # 'user_purchases' 컬렉션 가져오기
not_apply_collection = db['not_apply_yet']  # 'not_apply_yet' 컬렉션 가져오기


# 'service_metadata' 데이터베이스 가져오기 (없으면 생성)
db_metadata = client.get_database('service_metadata')

# 'user_action_metadata' 컬렉션 가져오기 (없으면 생성)
collection_metadata = db_metadata.get_collection('user_action_metadata')


@user_actions_bp.route('/ai-api/user/metadata/<int:userId>', methods=['POST'])
def save_user_metadata(userId):
    try:
        # 요청 본문에서 데이터 가져오기
        data = request.get_json()

        metadata = data['user_metadata']  # 'user_metadata' 키 사용
        # MongoDB에 저장할 데이터
        user_data = {
            'userId': userId,
            'data': metadata  # metadata 변수 사용
        }

        # userId로 document 찾기
        existing_data = collection.find_one({'userId': userId})

        if existing_data:
            # document가 이미 존재하면 'data' 필드 업데이트
            collection.update_one({'userId': userId}, {'$set': {'data': metadata}})  # metadata 변수 사용
            message = "User data updated successfully"
        else:
            # document가 존재하지 않으면 새 document 생성
            collection.insert_one(user_data)
            message = "User data saved successfully"

        return jsonify({'message': message}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_actions_bp.route('/ai-api/user/action/<int:userId>', methods=['POST']) 
def get_user_actions(userId):

    try:
        # 요청 데이터에서 productIds 가져오기
        data = request.get_json()
        productIds = data.get('productIds', [])

        # productIds가 리스트가 아니거나 비어있는 경우 에러 반환
        if not isinstance(productIds, list) or not productIds:
            return jsonify({'message': 'Invalid productIds'}), 400

        # 'user_actions' 데이터베이스 가져오기 (없으면 생성)
        db = client['user_actions']

        # 'user_purchases' 컬렉션 가져오기 (없으면 생성)
        collection = db['user_purchases']

        # userId를 이용하여 document 찾기
        user_data = collection.find_one({'userId': userId})

        if user_data:
            # userId가 이미 존재하는 경우, productIds 업데이트
            collection.update_one(
                {'userId': userId},
                {'$addToSet': {'productIds': {'$each': productIds}}}
            )
            
        else:
            # userId가 없는 경우, 새로운 document 생성
            collection.insert_one({'userId': userId, 'productIds': productIds})
            url = f"{API_URL}/ai-api/invoke/sequential/{userId}"
            requests.post(url)
        
        # productId와 count를 user_action_metadata 컬렉션에 업데이트
        for productId in productIds:
            collection_metadata.update_one(
                {'productId': productId},
                {'$inc': {'count': 1}},
                upsert=True  # document가 없으면 생성
            )

        
        return jsonify({
            "productIds" : productIds,
            "message" : "success to save Ids"
        }), 200


    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
    
    
def merge_user_product_scheduled():  # userId 인자 제거

    try:
        # 'user_purchases' 컬렉션에서 모든 사용자의 userId 가져오기
        user_ids = collection.distinct('userId') 
        not_apply_collection = db.get_collection('not_apply_yet')
        for userId in user_ids:  # 각 사용자에 대해 함수 실행
            # 'not_apply_yet' 컬렉션에서 userId에 해당하는 document 찾기
            not_apply_data = not_apply_collection.find_one({'userId': userId})

            if not_apply_data:
                yet_productIds = not_apply_data.get('yet_productIds', [])

                # 'user_purchases' 컬렉션에서 userId에 해당하는 document 찾기
                user_data = collection.find_one({'userId': userId})

                if user_data:
                    # userId가 이미 존재하는 경우, yet_productIds를 productIds에 추가
                    collection.update_one(
                        {'userId': userId},
                        {'$addToSet': {'productIds': {'$each': yet_productIds}}}
                    )
                else:
                    # userId가 없는 경우, 새로운 document 생성
                    collection.insert_one({'userId': userId, 'productIds': yet_productIds})
                    
                # 'not_apply_yet' 컬렉션에서 yet_productIds 초기화
                not_apply_collection.update_one(
                    {'userId': userId},
                    {'$set': {'yet_productIds': []}}
                )

    except Exception as e:
        print(f"Error merging user product data: {e}")


@user_actions_bp.route('/ai-api/user/action/yet/<int:userId>', methods=['POST'])
def get_user_actions_yet(userId):

    try:
        # 요청 데이터에서 yet_productIds 가져오기
        data = request.get_json()
        yet_productIds = data.get('yet_productIds', [])

        # yet_productIds가 리스트가 아니거나 비어있는 경우 에러 반환
        if not isinstance(yet_productIds, list) or not yet_productIds:
            return jsonify({'message': 'Invalid yet_productIds'}), 400

        # userId를 이용하여 document 찾기
        user_data = not_apply_collection.find_one({'userId': userId})

        if user_data:
            # userId가 이미 존재하는 경우, yet_productIds 업데이트
            not_apply_collection.update_one(
                {'userId': userId},
                {'$addToSet': {'yet_productIds': {'$each': yet_productIds}}}
            )
        else:
            # userId가 없는 경우, 새로운 document 생성
            not_apply_collection.insert_one({'userId': userId, 'yet_productIds': yet_productIds})

        return jsonify({
            "yet_productIds": yet_productIds,
            "message": "success to save yet_productIds"
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_actions_bp.route('/ai-api/user/action/yet/<int:userId>', methods=['GET'])
def get_not_apply_yet(userId):

    try:
        # 'not_apply_yet' 컬렉션에서 userId에 해당하는 document 찾기
        user_data = not_apply_collection.find_one({'userId': userId})

        if user_data:
            yet_productIds = user_data.get('yet_productIds', [])
            return jsonify({
                'userId': userId,
                'yet_productIds': yet_productIds
            }), 200
        else:
            return jsonify({
                'message': 'User data not found',
                'userId': userId
            }), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500


# 스케줄러 생성
scheduler = BackgroundScheduler()

'''
# 애플리케이션 시작 시 스케줄러 초기화 및 작업 추가
@app.before_first_request
def initialize_scheduler():

    if not scheduler.get_job('merge_user_product_job'):
        scheduler.add_job(
            merge_user_product_scheduled, 
            'cron', 
            hour=0, 
            id='merge_user_product_job'  # 작업 ID 설정
        )
        scheduler.start()

'''
# 스케줄러 실행 API 엔드포인트, test용
@user_actions_bp.route('/ai-api/scheduler/run', methods=['POST'])
def run_scheduler():

    try:
        # 스케줄러에 작업 추가 (이미 추가된 작업은 무시)
        if not scheduler.get_job('merge_user_product_job'):
            scheduler.add_job(
                merge_user_product_scheduled, 
                'cron', 
                hour=0, 
                id='merge_user_product_job'  # 작업 ID 설정
            )
            scheduler.start()
            return jsonify({'message': 'Scheduler started'}), 200
        else:
            return jsonify({'message': 'Scheduler is already running'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


#exectute --force
@user_actions_bp.route('/ai-api/scheduler/instant/run', methods=['POST'])
def run_instant_method():
    try:
        # merge_user_product_scheduled() 함수 직접 호출
        merge_user_product_scheduled()  
        return jsonify({'message': 'Function executed successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500