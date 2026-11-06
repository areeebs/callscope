def load_config():
    return {"debug": True}


def connect_db(config):
    return f"db(debug={config['debug']})"


def start():
    config = load_config()
    conn = connect_db(config)
    return handle_request(conn)


def handle_request(conn):
    log(conn)
    return "ok"


def log(msg):
    print(msg)
