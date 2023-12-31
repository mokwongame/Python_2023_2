from serial import Serial
import time # time 모듈을 수입: 시간 관련 함수의 집합체
import psycopg2
import statistics as stat
import matplotlib.pyplot as plt
import pandas.io.sql as psql

# public 멤버(클래스 외부에서 편하게 접근 가능): __이름__
# private 멤버(클래스 외부에서 접근 불가능(?), 특별한 부호 붙이면 접근 가능): __이름
class PythonHub: # 클래스(객체의 설계도), 인스턴스(클래스로 만든 실체, 클래스로 만든 변수) 구별
    # Private 멤버: __로 시작하는 변수나 함수
    __defComName = 'COM4'
    __defComBps = 9600
    __defWaitTime = 0.5 # 단위: 초

    # Public 정적 멤버: 항상 위에 정의 -> 위에 정의되어야 밑에서 접근(호출) 가능
    def waitSerial(): # self가 없음 -> 클래스의 정적(static) 멤버: 인스턴스 멤버에 접근하지 않음
        time.sleep(PythonHub.__defWaitTime) # 단위: 초; 클래스 멤버에 접근할 때는 클래스명.(PythonHub.)
    def wait(delaySec):
        time.sleep(delaySec)
            
    # 생성자(constructor): 이름은 __init__로 고정
    def __init__(self, comName = __defComName, comBps = __defComBps): # comName: Serial 이름, comBps: Serial 속도
        #print('생성자 호출됨')
        # 멤버 변수 생성: 변수를 선언하지 않고 self.으로 변수를 추가; self는 클래스(PythonHub)로 만든 인스턴스에 접근하기 위한 키워드
        # Serial 클래스의 인스턴스 생성 -> self.ard에 할당
        self.ard = Serial(comName, comBps) # C++ 경우: Serial ard;
        self.clearSerial() # Serial 입력 버퍼 초기화
        self.clearVoltTuple() # 전압과 측정 시간을 위한 튜플 공간 확보
        self.clearLightTuple()
        self.conn = None # DB의 connection
        self.cur = None # DB의 cursor
    # 소멸자(destructor): 이름은 __del__으로 고정
    def __del__(self):
        #print('소멸자 호출됨')
        if self.ard.isOpen(): # Serial이 열려(open)있는가?
            self.ard.close() # Serial을 닫음(close)
        
    # Serial 메소드(멤버 함수)
    def writeSerial(self, sCmd): # 인스턴스 접근하기 위한 self 추가
        btCmd = sCmd.encode()
        nWrite = self.ard.write(btCmd) # 인스턴스의 멤버인 ard에 접근: self.ard
        self.ard.flush()
        return nWrite
    def readSerial(self):
        nRead = self.ard.in_waiting
        if nRead > 0:
            btRead = self.ard.read(nRead)
            sRead = btRead.decode()
            return sRead
        else: return ''
    def clearSerial(self): # Serial 버퍼를 비우는 메소드
        PythonHub.waitSerial()
        self.readSerial()
    def talk(self, sCmd):
        return self.writeSerial(sCmd + '\n')
    def listen(self):
        PythonHub.waitSerial() # 클래스의 정적 멤버인 waitSerial() 호출
        sRead = self.readSerial()
        return sRead.strip()
    def talkListen(self, sCmd):
        self.talk(sCmd)
        return self.listen()

    # DB 메소드
    def connectDb(self):
        self.conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='2023', port='5432') # DB connection 얻기
        self.cur = self.conn.cursor() # connection의 cursor(커서)
    def closeDb(self):
        self.cur.close()
        self.conn.close()
    def writeDb(self, cmd): # DB에 명령어 cmd 쓰기
        sCmd = str(cmd) # string으로 type casting
        self.cur.execute(sCmd) # cursor에 명령어(SQL) 실행
        self.conn.commit() # connection에 기록하기 -> cursor 명령어를 DB가 실행
    
    # 전압계 메소드
    def getVolt(self):
        try: # 코드 시도(try)
            sVolt = self.talkListen('get volt')
            volt = float(sVolt) # 문자열 sVolt를 float(double)으로 변경
            return volt
        except: # try 부분에서 에러가 발생한 경우 실행되는 코드
            print('Serial error!')
            return -1
    def addVoltToTuple(self):
        volt = self.getVolt()
        measTime = time.time() # 현재 시간 읽기: 에포크 타임(기원후 시간, epoch time)
        if volt >= 0: # 측정 성공
            self.volts += (volt,) # 원소 하나인 튜플은 마지막에 , 추가
            self.voltTimes += (measTime,)
            return True
        else: return False # 측정 실패
    def clearVoltTuple(self):
        self.volts = () # 전압 측정값을 담은 튜플; (): 현재 변수를 tuple로 초기화
        self.voltTimes = () # 전압 측정 시간을 담은 tuple(튜플)
    def printVoltTuple(self):
        for (volt, measTime) in zip(self.volts, self.voltTimes):
            print(f'volt = {volt} @ time = {time.ctime(measTime)}') ## f: formatted string을 의미; {...} 안을 코드로 인식해 실행 -> 그 결과는 문자열로 반환; ctime(): char time -> 현재 에포크 타임을 보기 편한 문자열 시간으로 변경
    def sampleVoltTuple(self, nCount, delay): # delay 주기로 nCount개의 전압 측정값을 샘플링 -> 샘플링 결과는 volts, voltTimes 튜플에 저장
        #for i in range(nCount): # 단순 반복문
        #    print(self.addVoltToTuple())
        #    PythonHub.wait(delay)
        i = 0 # 에러 처리까지 하는 반복문
        while i < nCount:
            bResult = self.addVoltToTuple()
            print(bResult)
            if bResult:
                i += 1 # addVoltToTuple() 성공할 경우(bResult == True)에만 i를 1만큼 증가
                PythonHub.wait(delay)
    def getVoltMean(self): # 전압의 평균
        return stat.mean(self.volts)
    def getVoltVar(self): # 전압의 분산
        return stat.variance(self.volts)
    def getVoltStdev(self): # 전압의 표준 편차
        return stat.stdev(self.volts)
    def plotVoltTuple(self):
        plt.plot(self.voltTimes, self.volts)
        plt.show()
    def countVoltTable(self):
        self.connectDb()
        self.writeDb('SELECT COUNT(*) FROM volt_table')
        nCount = self.cur.fetchone()[0]
        self.closeDb()
        return nCount
    def insertOneVoltTable(self): # 전압 측정값 하나(one)를 DB에 추가
        self.connectDb()
        measTime = time.time()
        volt = self.getVolt()
        if volt >= 0.:
            self.writeDb(f'INSERT INTO volt_table(meas_time, volt) VALUES({measTime}, {volt})')
            self.closeDb()
            return True
        else: return False # 전압 측정 실패 경우
    def clearVoltTable(self): # DB에 저장된 전압 측정값을 삭제
        self.connectDb()
        self.writeDb('TRUNCATE volt_table')
        self.closeDb()
    def saveVoltTupleIntoTable(self): # volts, voltTimes 튜플을 DB에 저장; volts, voltTimes는 clear
        self.connectDb()
        for (volt, measTime) in zip(self.volts, self.voltTimes):
            self.writeDb(f'INSERT INTO volt_table(meas_time, volt) VALUES({measTime}, {volt})')
        self.closeDb()
        self.clearVoltTuple()
    def loadVoltTupleFromTable(self): # DB에서 정보를 가져와서 volts, voltTimes 튜플에 추가
        self.connectDb()
        self.writeDb('SELECT meas_time, volt FROM volt_table')
        result = self.cur.fetchall()
        for record in result:
            self.voltTimes += (record[0],)
            self.volts += (record[1],)
        self.closeDb()
    def writeHtmlVoltTuple(self):
        html = '<table width="100%" border="1"><thead><tr><th>번호</th><th>전압 측정값</th><th>측정 일시</th></tr></thead>'
        i = 1
        for (volt, voltTime) in zip(self.volts, self.voltTimes):
            html += f'<tr><td>{i}</td><td>{volt} V</td><td>{time.ctime(voltTime)}</td></tr>'
            i += 1
        html += '</table>'
        return html
    def describeVoltTable(self):
        self.conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='2023', port='5432')
        df = psql.read_sql('SELECT * FROM volt_table', self.conn)
        self.conn.close()
        ser = df['volt']
        print(f'개수 = {len(df)}')
        print(f'평균 = {ser.mean()}')
        print(f'중앙값 = {ser.median()}')
        print(f'분산 = {ser.var()}')
        print(f'표준편차 = {ser.std()}')

    # 조도계 메소드
    def getLight(self):
        try:
            sLight = self.talkListen('get light')
            return sLight
        except:
            print('Serial error!')
            return ''
    def getLightStep(self):
        try:
            sLightStep = self.talkListen('get lightstep')
            nLightStep = int(sLightStep)
            return nLightStep
        except:
            print('Serial error!')
            return -1
    def addLightToTuple(self):
        light = self.getLight()
        lightStep = self.getLightStep()
        measTime = time.time() # 현재 시간 읽기: 에포크 타임(기원후 시간, epoch time)
        if lightStep >= 0 and len(light) > 0: # 측정 성공
            self.lights += (light,) # 원소 하나인 튜플은 마지막에 , 추가
            self.lightSteps += (lightStep,)
            self.lightTimes += (measTime,)
            return True
        else: return False # 측정 실패
    def clearLightTuple(self):
        self.lights = ()
        self.lightSteps = ()
        self.lightTimes = ()
    def printLightTuple(self):
        for (light, lightStep, measTime) in zip(self.lights, self.lightSteps, self.lightTimes):
            print(f'light = {light}, step = {lightStep} @ time = {time.ctime(measTime)}')
    def sampleLightTuple(self, nCount, delay):
        i = 0 # 에러 처리까지 하는 반복문
        while i < nCount:
            bResult = self.addLightToTuple()
            print(bResult)
            if bResult:
                i += 1
                PythonHub.wait(delay)
    def getLightMean(self): # 평균
        return stat.mean(self.lightSteps)
    def getLightVar(self): # 분산
        return stat.variance(self.lightSteps)
    def getLightStdev(self): # 표준 편차
        return stat.stdev(self.lightSteps)
    def plotLightTuple(self):
        plt.plot(self.lightTimes, self.lightSteps)
        plt.show()
    def countLightTable(self):
        self.connectDb()
        self.writeDb('SELECT COUNT(*) FROM light_table')
        nCount = self.cur.fetchone()[0]
        self.closeDb()
        return nCount
    def clearLightTable(self):
        self.connectDb()
        self.writeDb('TRUNCATE light_table')
        self.closeDb()
    def saveLightTupleIntoTable(self):
        self.connectDb()
        for (light, lightStep, measTime) in zip(self.lights, self.lightSteps, self.lightTimes):
            self.writeDb(f"INSERT INTO light_table(meas_time, light, light_step) VALUES({measTime}, '{light}', {lightStep})")
        self.closeDb()
        self.clearLightTuple()
    def loadLightTupleFromTable(self):
        self.connectDb()
        self.writeDb('SELECT meas_time, light, light_step FROM light_table')
        result = self.cur.fetchall()
        for record in result:
            self.lightTimes += (record[0],)
            self.lights += (record[1],)
            self.lightSteps += (record[2],)
        self.closeDb()
    def describeLightTable(self):
        self.conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='2023', port='5432')
        df = psql.read_sql('SELECT * FROM light_table', self.conn)
        self.conn.close()
        ser = df['light_step']
        print(f'개수 = {len(df)}')
        print(f'평균 = {ser.mean()}')
        print(f'중앙값 = {ser.median()}')
        print(f'분산 = {ser.var()}')
        print(f'표준편차 = {ser.std()}')
        
    # Servo 메소드
    def setServoMove(self, ang): # ang만큼 각도 회전
        try:
            nAng = int(ang) # 변수 ang -> int로 변경(type casting)
            #sAng = str(nAng) # int nAng -> 문자열로 변경
            #self.talk('set servo ' + sAng)
            self.talk(f'set servo {nAng}')
        except:
            print('각도 설정 오류')

    # LED 메소드
    def setLedColor(self, color): # LED를 color로 설정
        try:
            sColor = str(color)
            self.talk('set led ' + sColor)
        except:
            print('LED 설정 오류')

    # 부저 메소드
    def setBuzzerNote(self, note, delay): # 부저 음정을 note로 설정하고 delay만큼 울림
        try:
            sNote = str(note)
            nDelay = int(delay)
            self.talk(f'set buzzer {sNote} {nDelay}')
        except:
            print('부저 설정 오류')