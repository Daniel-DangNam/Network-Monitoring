from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# Khóa bí mật dùng để ký và giải mã Token
SECRET_KEY = "ptit_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token có hiệu lực trong 24 giờ

# Thiết lập thuật toán băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Khai báo cổng nhận tài khoản/mật khẩu
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

def verify_password(plain_password, hashed_password):
    """Kiểm tra mật khẩu người dùng nhập có khớp với mật khẩu đã mã hóa trong DB không"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Băm mật khẩu trước khi lưu vào Database"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Đóng gói thông tin (username) và ký thành chuỗi Token (JWT)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt