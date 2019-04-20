import pandas, statistics, numpy, csv, math
from scipy import stats
ie_data = pandas.read_excel('http://www.econ.yale.edu/~shiller/data/ie_data.xls')
def get_cape(m):
	average_earnings = [statistics.mean(ie_data['Unnamed: 9'][7:m + 7])]
	for i in range(7, len(ie_data) - m - 2): average_earnings += [average_earnings[-1] + (ie_data['Unnamed: 9'][i + m + 2] - ie_data['Unnamed: 9'][i])/m]
	return {ie_data['Unnamed: 0'][i + m + 7]: ie_data['Unnamed: 7'][i + m + 7]/average_earnings[i] for i in range(len(average_earnings) - 1)}
def get_return(n):
	price = [(ie_data['Unnamed: 1'][i], ie_data['Unnamed: 1'][i + n]) for i in range(7, len(ie_data['Unnamed: 2']) - n - 1)]
	dividend = [statistics.mean(ie_data['Unnamed: 2'][7:n + 7])]
	for i in range(7, len(price) + 7): dividend += [dividend[-1] + (ie_data['Unnamed: 2'][i + n] - ie_data['Unnamed: 2'][i])/n]
	dividend.pop(0)
	while numpy.isnan(dividend[-1]): dividend.pop()
	m = len(dividend)
	price = price[:m]
	return {ie_data['Unnamed: 0'][i + 7]: ((price[i][1] + dividend[i])/price[i][0])**(12/n) - 1 for i in range(m)}
def get_gradient_map(write, cape_range = range(96, 384, 12), return_range = range(108, 168, 12)):
	if write:
		wr = csv.writer(open('temp.csv', 'w', newline = ''))
		wr.writerow([None] + list(return_range))
	gradient_map = dict()
	for i in cape_range:
		gradient_map[i] = dict()
		for j in return_range:
			cape, ret = get_cape(i), get_return(j)
			date = [k for k in cape if k in ret]
			gradient_map[i][j] = stats.pearsonr([cape[x] for x in date], [math.log(ret[x] + 1) for x in date])[0]
		if write: wr.writerow([i] + [gradient_map[i][x] for x in sorted(return_range)])
	return gradient_map
