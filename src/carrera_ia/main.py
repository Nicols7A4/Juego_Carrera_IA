from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def main():
    print("Hola desde carrera_ia! 🏁")

if __name__ == "__main__":
    main()
    
