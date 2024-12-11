from flask import Blueprint, request, jsonify



inference_bp = Blueprint('inference', __name__)

#private Callable Functions Set


@inference_bp.route('/ai-api/inference/result/<int:userId>', methods=['GET']) 
def get_inference_result(userId):
    
    return 'a'

@inference_bp.route('/ai-api/inference/test/<int:userId>', methods=['POST']) 
def get_inference_result_2(userId):
    """
    프론트엔드에서 전송된 body를 JSON 형식으로 반환합니다.
    """
    try:
        data = request.get_json()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inference_bp.route('/ai-api/inference/<int:userId>', methods=['POST']) 
def inference_invoke(userId):
    """
    AI 모델 추론을 수행하고 결과를 반환합니다.
    """
    try:
        data = request.get_json()

        # TODO: 여기에 AI 모델 추론 로직을 추가합니다.
        #       받은 데이터를 사용하여 AI 모델을 실행하고 결과를 생성합니다.
        #       아래는 예시입니다. 실제 AI 모델 로직으로 대체해야 합니다.

        # AI 모델 추론 결과 (예시)
        result = {
            "code": "600",  # 고유한 상품 코드 생성
            "name": data['name'],  # 상품 이름 (받은 데이터에서 가져옴)
            "category": data['category'],  # 상품 카테고리 (받은 데이터에서 가져옴)
            "price": data['price'],  # 상품 가격 (받은 데이터에서 가져옴)
            "thumbnail": "http://example.com/thumbnail.jpg",  # 상품 썸네일 URL (예시)
            "stock": data['stock']  # 상품 재고 (받은 데이터에서 가져옴)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inference_bp.route('/ai-api/embed/product/<int:productId>', methods=['POST']) 
def product_embed_invoke(productId):

    return 'a'


@inference_bp.route('/ai-api/embed/user/<int:userId>', methods=['POST']) 
def user_embed_invoke(userId):

    return 'a'


