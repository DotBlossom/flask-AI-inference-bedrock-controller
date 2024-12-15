# user revise
import boto3
import json
from botocore.exceptions import ClientError
import requests
from flask import request, jsonify, Blueprint
from apscheduler.schedulers.background import BackgroundScheduler

from inference import update_product_embedding , sequential_invoker

client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"  

flow_controller_bp = Blueprint("flow_controller" , __name__)
'''
scheduler_invoke_prefer = BackgroundScheduler()


def run_prefer_scheduler():
    try:
        # 스케줄러에 작업 추가 (이미 추가된 작업은 무시)
        if not scheduler_invoke_prefer.get_job('auto_prefer_shdlr'):
            scheduler_invoke_prefer.add_job(
                update_product_embedding,
                'cron', 
                hour=3, 
                id='auto_prefer_shdlr'  # 작업 ID 설정
            )
            scheduler_invoke_prefer.start()
            return jsonify({'message': 'Scheduler started'}), 200
        else:
            return jsonify({'message': 'Scheduler is already running'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


'''

@flow_controller_bp.route('/ai-api/bedrock/invoke', methods=['POST'])
def bedrock_invoke():
    try:
        body = request.get_json()
        json_input_clothes = body["product_metadata_to_str"]
        productId = body["product_id"]

    except KeyError:
        return jsonify({'error': 'json_input_clothes or product_id is missing in the request body'}), 400

    # 전체 프롬프트 (줄바꿈 추가)
    user_message = f"""{{json_clothes_metadata_feature_all}} 는 json 형식이며, 옷의 기본적인 정보를 포함하는 전체 feature 셋이야. 
너는 {{json_input_clothes}}의 정보를 이용하여, {{json_clothes_metadata_feature_all}} 내부의 "clothes" 의 전체 feature 값 중에서, 
{{json_input_clothes}}의 특성을 잘 반영하는 feature값을 선택하여 {{json_clothes_metadata_feature_all}} 과 동일한 양식의 json 데이터를 결과로 리턴해줘. 
{{json_clothes_metadata_feature_all}}의 내부 키 중 하나인 "reinforced_feature_value"는  결과 에삽입되어야 하는 값이며, 
{{json_clothes_metadata_feature_all}}의 "clothes"의 feature 값 들 중에 존재하지 않지만, {{json_input_clothes}}에 존재하는 명시적인 feature 특성이 존재한다면, "reinforced_feature_value"에 추가해줘. 


    그리고 답변은 json 데이터의 결과만 리턴해줘. 
    그리고 "category"에 해당하는 값(top, pants, skirt)의 종류에 대응되는 "top.()", "pants.()", "skirt.()" 에 맞는 feature를 선택적으로 채워줘.
    예를들어. "category"가 "02top_01blouse" 이면, top.length.type 과 같은 top.으로 시작하는 feature 값을 골라줘
    "top.()", "pants.()", "skirt.()" 로 시작하는 feature를 제외한 나머지 feature들에는 무조건 1개 이상의 값을 채워줘

{{json_clothes_metadata_feature_all}} : "clothes": {{
                "category": [
                    "01outer_01coat", 
                    "01outer_02jacket", 
                    "01outer_03jumper",
                    "01outer_04cardigan",
                    "02top_01blouse", 
                    "02top_02t-shirt", 
                    "02top_03sweater", 
                    "02top_04shirt", 
                    "02top_05vest", 
                    "03-1onepiece(dress)", 
                    "03-2onepiece(jumpsuite)", 
                    "04bottom_01pants", 
                    "04bottom_02skirt"
                ],
                "season": ["spring&fall", "summer", "winter"],
                    "fiber_composition": ["Cotton", "Hemp", "cellulose fiber Others", "Silk", "Wool", "protein fiber Others", "Viscos rayon", "regenerated fiber Others", "Polyester", "Nylon", "Polyurethane", "synthetic fiber Others"],
                    "elasticity": ["none at all", "none", "contain", "contain little", "contain a lot"],
                    "transparency": ["none at all", "none", "contain", "contain little", "contain a lot"],
                "isfleece": ["fleece_contain", "fleece_none"],
                "color": ["Black", "White", "Gray", "Red", "Orange", "Pink", "Yellow", "Brown", "Green", "Blue", "Purple", "Beige", "Mixed"],
                    "gender": ["male", "female", "both"],
                    "category_specification": ["outer","top","onepiece","bottom"],
                    "top.length_type": ["crop", "nomal", "long", "midi", "short"],
                    "top.sleeve_length_type": ["sleeveless", "short sleeves", "long sleeves"],
                    "top.neck_color_design": ["shirts collar", "bow collar", "sailor collar", "shawl collar", "polo collar", "Peter Pan collar", "tailored collar", "Chinese collar", "band collar", "hood", "round neck", "U-neck", "V-neck", "halter neck", "off shoulder", "one shoulder", "square neck", "turtle neck", "boat neck", "cowl neck", "sweetheart neck", "no neckline", "Others"],
                    "top.sleeve_design": ["basic sleeve", "ribbed sleeve", "shirt sleeve", "puff sleeve", "cape sleeve", "petal sleeve", "Others"]
                    "pant.silhouette": ["skinny", "normal", "wide", "loose", "bell-bottom", "Others"],
                    "skirt.design": ["A-line and bell line", "mermaid line", "Others"]
            }},
"reinforced_feature_value" : {{
                        "category" : [""],
                        "fiber_composition":[""],
                        "color": [""],
                        "category_specification": [""],
                        "specification.metadata":[""]
                }},                                                                      

    }}


{{json_input_clothes}} : {json_input_clothes}
""" 

    conversation = [
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ]

    try:
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                "temperature": 0.9,
                "maxTokens": 2000,
                "topP": 0.974,
            },
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        print(response_text)

        # API Gateway로 결과 전송
        api_gateway_url = "https://dotblossom.today/ai-api/bedrock/result/"
        api_url = f"{api_gateway_url}{productId}"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, data=response_text)

        # API Gateway 응답 확인
        if response.status_code == 200:
            print("API Controller 요청 후 데이터 저장 성공")
        else:
            print(f"API Controller 요청 후 처리 실패: {response.status_code}, {response.text}")

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return jsonify({'error': f"Can't invoke '{model_id}'. Reason: {e}"}), 500

    return jsonify({
        'response_text': response_text
    }), 200
