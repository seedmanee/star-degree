import urllib
import re
import lxml.html
import sys
from collections import deque

def titleURL(titleCode):
  return 'http://www.imdb.com/title/' + titleCode + '/fullcredits#cast'

def nameURL(nameCode):
  return 'http://www.imdb.com/name/' + nameCode + '/'

def queryEngName(nameCode):
  url = 'http://www.imdb.com/name/' + nameCode + '/'
  f = lxml.html.parse(url)
  name = f.xpath('//h1[@class="header"]/text()')
  return name[0].strip()

def queryNameCode(name):
  url = 'http://www.imdb.com/find?q=' + urllib.quote_plus(name) + '&s=all'
  try:
    f = urllib.urlopen(url)
    html = f.read()
    f.close()
  
    pat = '/name/(nm\d+)/'
    return re.findall(pat, html)[0]
  except Exception as e:
    print e.args
    print html
    return None

def queryAllCast(titleCode):
  url = 'http://www.imdb.com/title/' + titleCode + '/fullcredits#cast'
  f = lxml.html.parse(url)
  names = f.xpath('//table[@class="cast"]//td[@class="nm"]/a/@href')
  names = map(lambda x: x.split('/')[-2], names)  # /name/nm123456/ -> nm123456
  return names

# only query movie title
def queryAllTitle(nameCode):
  url = 'http://www.imdb.com/name/' + nameCode +'/filmotype'
  f = lxml.html.parse(url)

  links = []
  if len(f.xpath('//h5/a[@name="actress_main"]'))>0:
    links = f.xpath('//h5/a[@name="actress_main"]/../following-sibling::ol/li/a/@href')
  elif len(f.xpath('//h5/a[@name="actor_main"]'))>0:
    links = f.xpath('//h5/a[@name="actor_main"]/../following-sibling::ol/li/a/@href')

  links = filter(lambda x: x[0:7]=='/title/', links)

  if len(links)>0:
    links = map(lambda x: x.split('/')[-2], links)
    return links
  else:
    return None

# count all cast connect degree 1
def fanoutName(nameCode):
  titles = queryAllTitle(nameCode)
  names = []
  if not titles == None:
    for title in titles:
      names.extend( queryAllCast(title))

  return list(set(names))

if __name__ == '__main__':
  if len(sys.argv)>1:
    start_name = sys.argv[1]
    end_name = sys.argv[2]
  else:
    start_name = "jaden smith"
    end_name = "angelina jolie"

  start_node = queryNameCode(start_name)
  end_node = queryNameCode(end_name)

  if ( start_node == None or end_node == None):
    print 'Blocked'
    exit(1)

  print '== from %s (%s) to %s (%s) ==' % (start_node, start_name, end_node, end_name)

  # BFS
  q = deque([start_node])
  dq = deque([1])
  visited = {}

  while len(q) > 0:

    v = q.popleft()
    depth = dq.popleft()

    visited[v] = 1
    fanout = fanoutName(v)

    if end_node in fanout:
      print "fount in depth %d, %s (%s)'s fanout" % (depth, v, queryEngName(v))
      break

    print 'depth %d, %s fanout %d' % (depth, v, len(fanout))

    next_visit = filter( lambda x: ~visited.has_key(x), fanout)

    q.extend(next_visit)
    dq.extend([depth + 1 for i in range(len(next_visit))])
