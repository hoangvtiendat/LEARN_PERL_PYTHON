# LEARN_PERL_PYTHON

# back-end
1. how to automation generate database:
    - Create database in mysql 
    - in terminal of backend folder, execute the folllowing commands:
        rm -rf migrations
        flask db init
        flask db migrate -m "<name commit>"
        flask db upgrade

2. how to run backend:
    - cd to backend folder
    - in terminal, execute: flask run

3. env:
    # Flask App Secret Key - Dùng để bảo vệ session và cookies
    # !!! THAY ĐỔI THÀNH MỘT CHUỖI NGẪU NHIÊN VÀ BÍ MẬT CỦA BẠN !!!
    SECRET_KEY=mot-chuoi-bi-mat-rat-dai-va-ngau-nhien-cua-ban
    FLASK_APP=run.py
    FLASK_DEBUG=1

    # Database URL
    DATABASE_URL=mysql+pymysql://root:tiendat2004@127.0.0.1:3306/LEARN_PERL_PYTHON

    # (Tùy chọn) Thêm các API key cho tính năng AI sau này
    # Ví dụ cho OpenAI
    OPENAI_API_KEY=your_openai_api_key_here

    # Email Configuration
    MAIL_SERVER=smtp.googlemail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=hngvtdat010@gmail.com
    MAIL_PASSWORD=

    
    FRONTEND_URL=http://localhost:8080