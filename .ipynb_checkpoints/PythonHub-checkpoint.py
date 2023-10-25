from serial import Serial

# public 멤버(클래스 외부에서 편하게 접근 가능): __이름__
# private 멤버(클래스 외부에서 접근 불가능(?), 특별한 부호 붙이면 접근 가능): __이름
class PythonHub: # 클래스(객체의 설계도), 인스턴스(클래스로 만든 실체, 클래스로 만든 변수) 구별
    # 생성자(constructor): 이름은 __init__로 고정
    def __init__(self, comName, comBps): # comName: Serial 이름, comBps: Serial 속도
        print('생성자 호출됨')
        self.ard = Serial(comName, comBps)