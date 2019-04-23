import pandas, statistics, numpy, math, requests, xml.etree.ElementTree
from scipy import stats
ie_data = pandas.read_excel('http://www.econ.yale.edu/~shiller/data/ie_data.xls')
def get_cape(x, date = None):
	if date:
		i = list(ie_data['Unnamed: 0']).index(date)
		return ie_data['Unnamed: 7'][i]/statistics.mean(ie_data['Unnamed: 9'][i - x:i])
	else:
		average_earnings = [statistics.mean(ie_data['Unnamed: 9'][7:x + 7])]
		n = len(ie_data) - 1
		while numpy.isnan(ie_data['Unnamed: 3'][n]): n -= 1
		for i in range(7, n - x + 2): average_earnings += [average_earnings[-1] + (ie_data['Unnamed: 9'][i + x + 2] - ie_data['Unnamed: 9'][i])/x]
		return {ie_data['Unnamed: 0'][i + x + 7]: ie_data['Unnamed: 7'][i + x + 7]/average_earnings[i] for i in range(len(average_earnings) - 1)}
def get_return(y = None):
	if y:
		price = [(ie_data['Unnamed: 1'][i], ie_data['Unnamed: 1'][i + y]) for i in range(7, len(ie_data['Unnamed: 2']) - y - 1)]
		dividend = [statistics.mean(ie_data['Unnamed: 2'][7:y + 7])]
		for i in range(7, len(price) + 7): dividend += [dividend[-1] + (ie_data['Unnamed: 2'][i + y] - ie_data['Unnamed: 2'][i])/y]
		dividend.pop(0)
		while numpy.isnan(dividend[-1]): dividend.pop()
		n = len(dividend)
		price = price[:n]
		return {ie_data['Unnamed: 0'][i + 7]: ((price[i][1] + dividend[i])/price[i][0])**(12/y) - 1 for i in range(n)}
	else:
		a, b, c, d, e, f = numpy.linalg.lstsq([[i**2, i, i*j, j, j**2, 1] for i in gradient_map for j in gradient_map[i]], [gradient_map[i][j] for i in gradient_map for j in gradient_map[i]])[0]
		x, y = map(int, map(round, [-b/(2*a + c), -d/(2*e + c)]))
		w, z = get_pair(x, y)
		m, b = numpy.polyfit(w, [math.log(v + 1) for v in z], 1)
		return math.exp(m*get_cape(x, 2019.01) + b) - 1
def get_pair(x, y):
	cape, ret = get_cape(x), get_return(y)
	date = [k for k in cape if k in ret]
	return [cape[z] for z in date], [math.log(ret[z] + 1) for z in date]
def get_gradient_map(write, cape_range = range(96, 384, 12), return_range = range(108, 168, 12)):
	gradient_map = dict()
	for i in cape_range:
		gradient_map[i] = dict()
		for j in return_range:
			cape, ret = get_cape(i), get_return(j)
			date = [k for k in cape if k in ret]
			gradient_map[i][j] = stats.pearsonr(*get_pair(i, j))[0]
	return gradient_map
def risk_free_rate(): return float(xml.etree.ElementTree.fromstring(requests.get('https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData').content).findall('.//{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_3MONTH')[-1].text)/100
