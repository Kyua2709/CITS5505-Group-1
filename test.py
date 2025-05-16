#!/usr/bin/env python3
import sys
import time
import multiprocessing
import pytest
import tempfile
import socket


def run_test_server():
    from app import create_app
    test_config={
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    }
    app = create_app(test_config)
    app.run(host='localhost', port=5001, debug=False, use_reloader=False)

def run_test(require_server: bool, pytest_args):
    try:
        if require_server:
            print("Starting Flask app in a separate process...")
            p = multiprocessing.Process(target=run_test_server)
            p.start()

            while True:
                print("Waiting for Flask to start...")
                time.sleep(3)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5001))
                sock.close()
                if result == 0:
                    break
    
        return pytest.main(pytest_args)
    finally:
        if require_server:
            # Terminate the Flask process
            print("Stopping Flask application...")
            p.terminate()
            p.join()
            print("Process terminated")

def run_ut():
    return run_test(False, [
            '-xvs',  # -x: exit on first failure, -v: verbose, -s: show output
            'tests/ut'  
        ])

def run_st():
    return run_test(True, [
            '-xvs',  # -x: exit on first failure, -v: verbose, -s: show output
            'tests/st'  
        ])


if __name__ == "__main__":
    if sys.argv[1] == 'ut':
        run_ut()
    if sys.argv[1] == 'st':
        run_st()
