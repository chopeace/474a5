
# Get the good stuff
import redis, json, mimeparse, os, sys
from bottle import route, run, request, response, abort

config = { 'servers': [{ 'host': 'localhost', 'port': 6379 }] }

if (len(sys.argv) > 1):
	config = json.loads(sys.argv[1])

# Connect to a single Redis instance
client = redis.StrictRedis(host=config['servers'][0]['host'], port=config['servers'][0]['port'], db=0)

# Add a route for a user updating their rating of something which can be accessed as:
# curl -XPUT -H'Content-type: application/json' -d'{ "rating": 5, "source": "charles" }' http://localhost/rating/bob
# Response is a JSON object specifying the new rating for the entity:
# { rating: 5 }
@route('/rating/<entity>', method='PUT')
def put_rating(entity):

	# Check to make sure JSON is ok
	type = mimeparse.best_match(['application/json'], request.headers.get('Accept'))
	if not type: return abort(406)

	# Check to make sure the data we're getting is JSON
	if request.headers.get('Content-Type') != 'application/json': return abort(415)

	response.headers.append('Content-Type', type)
	
	# Read in the data
	data = json.load(request.body)
	rating = data.get('rating')
	source = data.get('source')

	# Basic sanity checks on the rating
	if isinstance(rating, int): rating = float(rating)
	if not isinstance(rating, float): return abort(400)

	# Update the rating for the entity
	key = '/rating/'+entity

	#client.set(key, rating)
	
	client.hmset(source, {'tea':entity,'rating':rating })
	
	#r.hmset('neha', {'tea':'a','rating':20,'avg':15})
	#r.hmset('ted', {'tea':'b','rating':30,'avg':30})
	# Return the new rating for the entity
	return {
		"rating": rating
	}


# Add a route for getting the aggregate rating of something which can be accesed as:
# curl -XGET http://localhost/rating/bob
# Response is a JSON object specifying the rating for the entity:
# { rating: 5 }
@route('/rating/<entity>', method='GET')
def get_rating(entity):

	keys = client.keys('*')
	prev_sum=0
	count=0
	search_tea = entity
	for key in keys:
        	if client.type(key) == 'hash':
			#vals = client.hgetall(key)
        		#print float(client.hmget(key,'rating'))
		
			rate = float(client.hmget(key,'rating')[0])
			#print client.type(key),
        		tea = client.hmget(key,'tea')[0]

        		if tea == search_tea:
                	#print 'calculate tea : ', tea, rate
                		prev_sum=prev_sum+rate
                		count=count+1
	
	if count ==0:
		avg_rate = 0
	else:
		avg_rate=prev_sum/count

	return {
		"rating": avg_rate
	}

# Add a route for deleting all the rating information which can be accessed as:
# curl -XDELETE http://localhost/rating/bob
# Response is a JSON object showing the new rating for the entity (always null)
# { rating: null }
@route('/rating/<entity>', method='DELETE')
def delete_rating(entity):
	count = client.delete('/rating/'+entity)
	if count == 0: return abort(404)
	return { "rating": None }

# Fire the engines
if __name__ == '__main__':
	run(host='0.0.0.0', port=os.getenv('PORT', 2500), quiet=True)



