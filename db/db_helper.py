import pymysql

DB_CONFIG = dict(
    host="192.168.0.28",
    user="basic",
    password="basic123",
    database="basic",
    charset="utf8"
)

class DB:
    def __init__(self, **config):
        self.config = config

    def connect(self):
        return pymysql.connect(**self.config)
    
    # 테스트
    def test_query(self):
        sql = "SELECT COUNT(*) FROM TB_CARS"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                count = cur.fetchone()
                return count[0]
            
    # 차량 입차 및 출차 로그 INSERT
    def insert_parking_log(self, action):
        sql = "INSERT INTO TB_PARKING_LOG (EVENT_TYPE, EVENT_TIME) VALUES (%s, NOW())"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (action, ))
                count = cur.rowcount
                if count == 1 :
                    conn.commit()
                else :
                    conn.rollback()
        return count == 1

   ######### 여기서부터 시작##########
    # 특정 주차자리의 등록 RFID 조회
    def get_registered_rfid(self, spot_id, rfid_tag):
        sql = "SELECT T2.CAR_ID FROM TB_PARKING_SPOTS T1 LEFT JOIN TB_CARS T2 ON T1.RFID_TAG = T2.RFID_TAG WHERE SPOT_ID=%s AND T1.RFID_TAG = %s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (spot_id, rfid_tag))
                row = cur.fetchone()
                if row:
                    return row[0]
                return None