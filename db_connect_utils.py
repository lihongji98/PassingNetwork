from mongoengine import connect, disconnect


def db_connect():
    file_path = "/Users/lihongji/mongodb_url.txt"
    with open(file_path, 'r') as file:
        host_address = file.read().strip()
    try:
        connect(db='LaLiga2023', host=host_address)
        print("connected to mongodb database successfully!")
    except RuntimeError:
        print("connection failed!")


def db_disconnect():
    disconnect()
    print("disconnected from mongodb database!")
