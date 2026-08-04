import os
import sys
from sqlalchemy.orm import Session

# Thêm thư mục gốc vào đường dẫn hệ thống để Python có thể import từ 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.models.models import Base, User
from app.core.auth import get_password_hash

# Tạo bảng trong DB nếu chưa có
Base.metadata.create_all(bind=engine)

def create_first_admin():
    db: Session = SessionLocal()
    try:
        # Kiểm tra xem đã có admin nào chưa
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("Tài khoản 'admin' đã tồn tại!")
            return

        # Tạo tài khoản mới với mật khẩu được mã hóa
        hashed_password = get_password_hash("123456")
        new_admin = User(username="admin", hashed_password=hashed_password, is_active=True)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Tạo tài khoản thành công! Username: admin | Password: 123456")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()