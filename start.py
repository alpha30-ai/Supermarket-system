from app import app

if __name__ == '__main__':
    print("Starting server...")
    app.run(host='127.0.0.1', port=5000, debug=True)
