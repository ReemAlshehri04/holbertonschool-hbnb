from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

# Updated to allow specifying config class from environment variable
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)
