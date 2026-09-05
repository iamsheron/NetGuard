from services.os_detector import OSDetector

detector = OSDetector()

result = detector.detect("192.168.1.74")   # Replace with your router IP

print(result)