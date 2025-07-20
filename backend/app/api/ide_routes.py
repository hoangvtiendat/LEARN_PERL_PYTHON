import requests
import time
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from dotenv import load_dotenv
import os

ide_bp = Blueprint('ide_bp', __name__)

JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com/submissions"

LANGUAGE_IDS = {
    "python": 71,
    "perl": 85
}

@ide_bp.route('/execute', methods=['POST'])
@jwt_required() # Đã bật lại xác thực, bạn cần gửi access_token khi test
def execute_code():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language', 'python').lower()

    if not code:
        return jsonify({"error": "Không có code để thực thi"}), 400

    language_id = LANGUAGE_IDS.get(language)
    if not language_id:
        return jsonify({"error": f"Ngôn ngữ '{language}' không được hỗ trợ"}), 400

    # Lấy key và host từ file config
    # api_key = '94ca38786emshf4f40b7c9c2134ep151650jsn62b86e92bb0c'
    # api_host = 'judge0-ce.p.rapidapi.com'
    api_key = os.getenv('RAPIDAPI_KEY')
    api_host = os.getenv('RAPIDAPI_HOST')

    if not api_host:
        return jsonify({"error": "RAPIDAPI_HOST chưa được cấu hình trong file .env"}), 500
  
    payload = {
        "source_code": code,
        "language_id": language_id,
    }
    
    # Tạo header chứa key để xác thực với RapidAPI
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host,
        "Content-Type": "application/json"
    }

    try:
        # Gửi request có kèm headers để tạo submission
        response = requests.post(JUDGE0_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        submission_token = response.json().get('token')

        if not submission_token:
            return jsonify({"error": "Không thể tạo submission trên Judge0", "details": response.json()}), 500

        # Chờ và lấy kết quả từ Judge0
        result_url = f"{JUDGE0_API_URL}/{submission_token}?base64_encoded=false"
        output = None
        for _ in range(5): # Thử lại tối đa 5 lần
            time.sleep(1) 
            # Request lấy kết quả cũng phải kèm headers
            result_response = requests.get(result_url, headers=headers)
            result_data = result_response.json()
            status_id = result_data.get('status', {}).get('id')

            if status_id is not None and status_id > 2: # 1: In Queue, 2: Processing
                output = {
                    "stdout": result_data.get('stdout'),
                    "stderr": result_data.get('stderr'),
                    "status": result_data.get('status', {}).get('description')
                }
                break

        if output is None:
            return jsonify({"error": "Thực thi code mất quá nhiều thời gian hoặc có lỗi xảy ra"}), 408

        return jsonify(output)

    except requests.exceptions.RequestException as e:
        # Trả về lỗi chi tiết hơn từ API
        error_details = e.response.json() if e.response else str(e)
        return jsonify({"error": "Lỗi khi kết nối đến Judge0", "details": error_details}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500