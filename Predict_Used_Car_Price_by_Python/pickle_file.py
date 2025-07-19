import pickle

pw = '6868'

# 파일로 저장
with open('./Flask/pickle/pw.pkl', 'wb') as f:
    pickle.dump(pw, f)
    
# 파일 불러오기
with open('./Flask/pickle/pw.pkl', 'rb') as f:
    data = pickle.load(f)


host_file = 'ec2-3-87-146-248.compute-1.amazonaws.com'
# 파일로 저장
with open('./Flask/pickle/host.pkl', 'wb') as f:
    pickle.dump(host_file, f)
    
# 파일 불러오기
with open('./Flask/pickle/host.pkl', 'rb') as f:
    host = pickle.load(f)

print(data)
print(host)
