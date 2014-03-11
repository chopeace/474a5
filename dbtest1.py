import redis
r = redis.Redis()
r.delete('source')
r.hmset('peace', {'tea':'a','rating':10, 'avg':10})
r.hmset('neha', {'tea':'a','rating':20,'avg':15})
r.hmset('ted', {'tea':'b','rating':30,'avg':30})

keys = r.keys('*')
sum=0
count=0
search_tea = 'a'
for key in keys:
	vals = r.hgetall(key)
	rate = int(r.hmget(key,'rating')[0])
	tea = r.hmget(key,'tea')[0]
	
	if tea == search_tea:
		print 'calculate tea : ', tea, rate
		sum=sum+rate
		count=count+1

print 'previous avg=', sum/count


