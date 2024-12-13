from flask import Blueprint, request, jsonify
import requests

inference_bp = Blueprint('inference', __name__)

#private Callable Functions Set

API_URL = "https://dotblossom.today"

@inference_bp.route('/ai-api/invoke/product/embed/<int:productId>', methods=['GET']) 
def embed_product_invoker(productId):
    try:
        # API 엔드포인트 URL 생성
        api_url = f"{API_URL}/infer-api/products/{productId}"
        response = requests.get(api_url)

        return jsonify({
            'product_id': productId,
            'message': "success to invoke Product Embedding!"
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@inference_bp.route('/ai-api/invoke/user/embed/<int:userId>', methods=['GET']) 
def embed_user_invoker(userId):
    try:
        api_url = f"{API_URL}/infer-api/users/{userId}"  # API 엔드포인트는 실제 환경에 맞게 수정

        # API 호출
        response = requests.get(api_url)

        # 성공적으로 호출되었는지 확인 (상태 코드 200 확인)
        if response.status_code == 200:
            return jsonify({
                'user_id': userId,
                'message': "success to invoke User Embedding!"
            })
        else:
            return jsonify({'message': str(e)}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

@inference_bp.route('/ai-api/invoke/preference/<int:userId>', methods=['POST']) 
def preference_invoker(userId):
    try:
        api_url = f"{API_URL}/infer-api/product/preference/infer/{userId}"  # API 엔드포인트는 실제 환경에 맞게 수정

        # API 호출
        response = requests.get(api_url)

        # 성공적으로 호출되었는지 확인 (상태 코드 200 확인)
        if response.status_code == 200:
            return jsonify({
                'user_id': userId,
                'message': "success to invoke inference and save preference data key"
            })
        else:
            return jsonify({'message': str(e)}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

@inference_bp.route('/ai-api/invoke/sequential/<int:userId>', methods=['POST'])
def sequential_invoker(userId):
    try:

        # 2. embed_user_invoker 호출 (직접 호출)
        response = embed_user_invoker(userId)
        if response.status_code != 200:
            return response  # 실패 시 바로 반환

        # 3. preference_invoker 호출 (직접 호출)
        response = preference_invoker(userId)
        if response.status_code != 200:
            return response  # 실패 시 바로 반환

        # 모든 함수가 성공적으로 실행되면 성공 메시지 반환
        return jsonify({
            'user_id': userId,
            'message': "Successfully invoked all functions sequentially."
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
