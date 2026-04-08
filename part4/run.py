from app import create_app

# Optionally pass a config class name or module path, e.g. 'app.config.DevelopmentConfig'
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
