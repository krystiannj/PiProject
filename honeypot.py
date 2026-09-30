import psycopg2
from datetime import datetime
import socket

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind(("0.0.0.0", 2222))

server.listen()

print("Honeypot listening on port 2222")

while True:

    client, address = server.accept()
    conn = psycopg2.connect(
        host="10.42.0.246",
        database="monitoring",
        user="postgres",
        password="password"
    )

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO honeypot_logs
        (
            ip_address,
            timestamp
        )
        VALUES (%s, %s)
        """,
        (
            address[0],
            datetime.now()
        )
    )
    conn.commit()
    print(
        f"Connection from {address[0]}"
    )
    cur.close()
    conn.close()
    client.close()