from serial import Serial

# public 멤버(클래스 외부에서 편하게 접근 가능): __이름__
# private 멤버(클래스 외부에서 접근 불가능(?), 특별한 부호 붙이면 접근 가능): __이름
class PythonHub: # 클래스(객체의 설계도), 인스턴스(클래스로 만든 실체, 클래스로 만든 변수) 구별
    # Private 멤버: __로 시작하는 변수나 함수
    __defComName = 'COM4'
    __defComBps = 9600
    
    # 생성자(constructor): 이름은 __init__로 고정
    def __init__(self, comName = __defComName, comBps = __defComBps): # comName: Serial 이름, comBps: Serial 속도
        print('생성자 호출됨')
        # 멤버 변수 생성: 변수를 선언하지 않고 self.으로 변수를 추가; self는 클래스(PythonHub)로 만든 인스턴스에 접근하기 위한 키워드
        # Serial 클래스의 인스턴스 생성 -> self.ard에 할당
        self.ard = Serial(comName, comBps) # C++ 경우: Serial ard;
    # 소멸자(destructor): 이름은 __del__으로 고정
    def __del__(self):
        print('소멸자 호출됨')
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
    def talk(self, sCmd):
        return self.writeSerial(sCmd + '\n')
    def listen(self):
        sRead = self.readSerial()
        return sRead.strip()




