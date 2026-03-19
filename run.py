from app import create_app

app = create_app()

if __name__ == '__main__':
    # arranca el servidor web en el puerto 5000
    app.run(host='0.0.0.0', port=5000)