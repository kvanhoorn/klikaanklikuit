import os,sys
import socket, sqlite3, argparse

UDP_IP = "255.255.255.255"
UDP_PORT = 9760

class Kaku:
    __db = None
    __c = None

    def __init__(self, room, device, to_state):
        self.__initDB()
        self.__setDeviceState(room, device, to_state)

    def __initDB(self):
        conn = sqlite3.connect('kaku.db')
        c = conn.cursor()

        self.__db = conn
        self.__c = c

        sql = '''CREATE TABLE IF NOT EXISTS cmd_hist (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT NOT NULL,
            Input TEXT,
            Teply TEXT)'''
        c.execute(sql)
        conn.commit()

    @staticmethod
    def translateState(i):
        o = None

        if i == 1 or i == 'on' or i == 'aan' or i == 'n' or i == True:
            return "1"
        elif i == 0 or i == 'off' or i == 'uit' or i == 'f' or i == False:
            return "0"
        else:
            return "0"

    @staticmethod
    def getNowString():
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print now_str
        return now_str

    def __setDeviceState(self, room, device, tostate):
        import datetime
        tostate = Kaku.translateState(tostate[0])

        sql = '''INSERT INTO cmd_hist (Date) VALUES (?)'''
        self.__c.execute(sql, (Kaku.getNowString(),))
        self.__db.commit()
        id = self.__c.lastrowid
        
        message = str(id) + ",!R" + str(room) + "D" + str(device) + "F" + tostate
        print message

        sql = '''UPDATE cmd_hist SET Input = ? WHERE ID = ?'''
        self.__c.execute(sql, (message, id))
        self.__db.commit()

        # initialize socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # send udp packet
        sock.sendto(message, 0, (UDP_IP, UDP_PORT))
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn an KAKU device on or off.')
    parser.add_argument('-r', '--room', metavar='room', type=int, help='which room should be used')
    parser.add_argument('-d', '--device', metavar='device', type=int, help='which device should be used')
    parser.add_argument('tostate', metavar='tostate', type=str, nargs=1, help='status device should be')
    args = parser.parse_args()

    Kaku(args.room, args.device, args.tostate)
