#!/usr/bin/env python3
"""
CSrecomMIND 服务器启动脚本
"""

import os
import sys
import subprocess

def main():
    print("🚀 正在启动CSrecomMIND系统...")
    
    # 检查Python环境
    try:
        import flask
        import flask_cors
        print("✅ Flask环境检查通过")
    except ImportError as e:
        print(f"❌ 缺少必要的Python包: {e}")
        print("请运行: pip install flask flask-cors")
        return
    
    # 启动后端服务
    try:
        print("📡 启动后端API服务...")
        print("🌐 后端服务地址: http://localhost:5000")
        print("📖 API文档:")
        print("  - GET  /api/health - 健康检查")
        print("  - POST /api/student/recommend-questions - 获取推荐题目")
        print("  - POST /api/student/submit-answer - 提交答案")
        print("  - POST /api/student/get-explanation - 获取解析")
        print("  - GET  /api/student/weak-knowledge-points - 获取薄弱知识点")
        print("  - GET  /api/student/progress - 获取学习进展")
        print("\n💡 现在可以在另一个终端启动前端服务:")
        print("   cd prototype-main")
        print("   npm run dev")
        print("\n按 Ctrl+C 停止服务")
        
        # 运行后端服务
        subprocess.run([sys.executable, 'backend_server.py'], cwd=os.path.dirname(__file__))
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()
