from app import load_config, log


def run_job():
    cfg = load_config()
    log("job start")
    return cfg
