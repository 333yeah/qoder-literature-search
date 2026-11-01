"""配置管理：从环境变量读取 seekdb 连接与应用配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# seekdb 连接配置
SEEKDB_HOST = os.getenv('SEEKDB_HOST', '127.0.0.1')
SEEKDB_PORT = int(os.getenv('SEEKDB_PORT', '2881'))
SEEKDB_USER = os.getenv('SEEKDB_USER', 'root')
SEEKDB_PASSWORD = os.getenv('SEEKDB_PASSWORD', '')
SEEKDB_DATABASE = os.getenv('SEEKDB_DATABASE', 'literature')
SEEKDB_TENANT = os.getenv('SEEKDB_TENANT', '')

# 应用配置
EMBEDDING_DIM = int(os.getenv('EMBEDDING_DIM', '384'))
RRF_K = int(os.getenv('RRF_K', '60'))
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', '8000'))
