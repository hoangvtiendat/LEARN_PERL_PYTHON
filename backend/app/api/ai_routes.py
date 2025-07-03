from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
import json 
from ..models.submission import Submission # Import model Submission
from collections import defaultdict # Import defaultdict để nhóm dữ liệu


# Tạo blueprint mới cho các tính năng AI
ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/chatbot', methods=['POST'])
@jwt_required() # Yêu cầu người dùng phải đăng nhập
def chatbot():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "Câu hỏi là bắt buộc"}), 400

    # Lấy API key từ file cấu hình
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({"error": "Gemini API key chưa được cấu hình"}), 500

    try:
        # Cấu hình thư viện Gemini với API key
        genai.configure(api_key=api_key)

        # Định hình vai trò của AI qua system instruction
        system_instruction = "You are a helpful assistant specializing in teaching Perl and Python programming languages."
        
        # Chọn model, ví dụ: gemini-1.5-flash-latest
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction
        )

        # Gửi câu hỏi đến model
        response = model.generate_content(question)

        # Lấy câu trả lời và trả về cho người dùng
        return jsonify({"answer": response.text})

    except Exception as e:
        # Xử lý các lỗi có thể xảy ra khi gọi API
        return jsonify({"error": str(e)}), 500
    

@ai_bp.route('/suggest-fix', methods=['POST'])
@jwt_required()
def suggest_fix():
    data = request.get_json()
    code_snippet = data.get('code')
    language = data.get('language') # 'python' hoặc 'perl'

    if not code_snippet or not language:
        return jsonify({"error": "Cần cung cấp đoạn code và ngôn ngữ lập trình"}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({"error": "Gemini API key chưa được cấu hình"}), 500

    try:
        genai.configure(api_key=api_key)

        # System prompt này sẽ hướng dẫn AI hành động như một chuyên gia review code
        system_instruction = f"""
You are an expert code reviewer for the {language} programming language. 
Your task is to analyze the user's code snippet. 
1. Identify any syntax or logical errors.
2. Provide a corrected version of the code.
3. Explain clearly in Vietnamese: What was the error? Why was it wrong? And why is the corrected version right?
Format your response clearly with the explanation first, followed by the code block.
"""
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction
        )

        # Gửi đoạn code của người dùng đến model
        response = model.generate_content(code_snippet)

        return jsonify({"suggestion": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@ai_bp.route('/generate-questions', methods=['POST'])
@jwt_required()
def generate_questions():
    data = request.get_json()
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'dễ') # Mặc định là 'dễ' nếu không có
    num_questions = data.get('num_questions', 3) # Mặc định là 3 câu

    if not topic:
        return jsonify({"error": "Cần cung cấp chủ đề (topic)"}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({"error": "Gemini API key chưa được cấu hình"}), 500

    try:
        genai.configure(api_key=api_key)

        # System prompt yêu cầu AI trả về ĐÚNG ĐỊNH DẠNG JSON
        system_instruction = """
You are an AI assistant that creates multiple-choice programming questions about Python and Perl.
The user will provide a topic, difficulty, and number of questions.
You MUST return the response as a single, valid JSON object.
The JSON object must have a key named 'questions' which is an array.
Each object in the array must have these exact keys: 'question_text', 'options' (an array of 4 strings), and 'correct_answer' (a string with the correct option letter like 'A', 'B', 'C', or 'D').
"""
        
        # Bật chế độ trả về JSON của Gemini
        generation_config = {"response_mime_type": "application/json"}
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction,
            generation_config=generation_config
        )

        # Prompt cho người dùng
        user_prompt = f"Generate {num_questions} {difficulty} multiple-choice questions about the topic: {topic}"
        
        response = model.generate_content(user_prompt)

        # Vì đã bật chế độ JSON, response.text sẽ là một chuỗi JSON
        # Chúng ta cần parse nó thành một đối tượng Python trước khi trả về
        return jsonify(json.loads(response.text))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

@ai_bp.route('/assessment', methods=['GET'])
@jwt_required()
def assess_competency():
    current_user_id = get_jwt_identity()

    # 1. Truy vấn tất cả bài nộp của người dùng
    submissions = Submission.query.filter_by(student_id=current_user_id, status='graded').all()

    if not submissions:
        return jsonify({
            "assessment": "Chưa có đủ dữ liệu để đánh giá.",
            "recommendation": "Hãy bắt đầu làm các bài tập để hệ thống có thể đánh giá năng lực của bạn."
        })

    # 2. Tổng hợp dữ liệu học tập
    performance_by_topic = defaultdict(lambda: {'scores': [], 'count': 0})

    for sub in submissions:
        if sub.score is not None:
            # Lấy chủ đề từ bài học (lesson) của bài tập (exercise)
            topic_name = sub.exercise.lesson.title 
            performance_by_topic[topic_name]['scores'].append(sub.score)
            performance_by_topic[topic_name]['count'] += 1
    
    # Tạo một chuỗi tóm tắt để gửi cho AI
    summary = "Dưới đây là tóm tắt hiệu suất học tập của sinh viên:\n"
    for topic, data in performance_by_topic.items():
        avg_score = sum(data['scores']) / len(data['scores'])
        summary += f"- Chủ đề: '{topic}', Số bài làm: {data['count']}, Điểm trung bình: {avg_score:.2f}/100.\n"

    # 3. Gọi API Gemini để phân tích
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({"error": "Gemini API key chưa được cấu hình"}), 500

    try:
        genai.configure(api_key=api_key)

        system_instruction = """
You are an AI academic advisor. Based on the student's performance summary, provide a concise, encouraging competency assessment. 
1. Identify their strengths (topics with high scores).
2. Identify their weaknesses (topics with low scores).
3. Based on their weaknesses, you MUST suggest a specific topic they should review next.
Your entire response must be in Vietnamese.
"""
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(summary)
        
        # Tách câu trả lời của AI thành 2 phần để có cấu trúc JSON đẹp hơn
        # (Đây là một cách xử lý đơn giản, có thể cải tiến)
        parts = response.text.split("Gợi ý học tập:")
        assessment_text = parts[0].strip()
        recommendation_text = parts[1].strip() if len(parts) > 1 else "Hãy tiếp tục ôn tập các chủ đề bạn còn yếu."

        return jsonify({
            "assessment": assessment_text,
            "recommendation": recommendation_text,
            "performance_summary": performance_by_topic
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

