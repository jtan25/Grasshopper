import math
import numpy as np
from numpy import linalg as la
from numpy.linalg import inv



class Grasshopper(object):

	#lambda weight balances the probability distribution r and prior rankings 
	#l = .5 and alpha = .25 is the settings for text summarization used on the DUC dataset
	def __init__(self, lambda_weight = .5, alpha = .25, uniform_initial_distribution= False)
	self.lambda_weight = lambda_weight
	self.alpha = alpha
	self.uniform_initial_distribution = uniform_initial_distribution



	def textSummarization(self, matrix, r = None, cosine_threshold = 1.0):
		size_of_matrix = len(matrx[0])
		ranks = []
		if cosine_threshold > 0:
			matrix = applyCosineThreshold(matrix, cosine_threshold, size_of_matrix)
		symmetric_matrix = reflectOverYX(matrix, size_of_matrix)
		
		if r is None:
			r = np.zeros((size_of_matrix,1))
			if uniform_initial_distribution:
				r.fill(1.0/size_of_matrix)
			else:
				for x in range(1,size_of_matrix+1):
					r[x-1] = pow(x, -alpha)

		P = init_markov_chain(symmetric_matrix, size_of_matrix, r, self.lambda_weight)
		stationary_distr = findStationaryDistr(P.T)
		g_index = findArgMaxOfMatrix(stationary_distr)
		ranks.append(g_index)


		while(len(ranks) < size_of_matrix):
			Q = getUnRankedRows(P, g_index)
			size_of_Q = size_of_matrix - len(ranks)
			I = np.identity(size_of_Q)
			N = inv(I-Q)
			one_vec = np.zeros((size_of_Q,1))
			one_vec.fill(1.0)
			v = np.dot(N.T, one_vec) / (size_of_Q)
			g_index = findArgMaxOfMatrix(v)
			P = Q
			#Offset of indices from Q is size_matrix - size of Q
			ranks.append(size_of_matrix - size_of_Q + g_index)
			
		return ranks



		#absorbing states then loop to find next stationary distr
		#rankings = findGrank()

def getUnRankedRows(p, idx):
	Q = np.delete(p,idx,0)
	Q = np.delete(p,idx,1)
	return Q


#P = lambda*normalized(P) + (1-lambda)*1r^t
def init_markov_chain(symmetric_matrix, size_of_matrix, r, lambda_weight):
	normalized_matrix = normalize_by_row(symmetric_matrix)
	normalized_matrix = lambda_weight * normalized_matrix
	one_vec = np.zeros((size_of_matrix,1))
	one_vec.fill(1.0)
	return normalized_matrix + (1 - lambda_weight) * np.outer(one_vec,r)

# π = P^T π
def findStationaryDistr(matrix):
	w, v = la.eig(matrix)
	j_stationary = np.argmin(abs(w-1.0))
	p_stationary = v[:,j_stationary].real
	p_stationary /= p_stationary.sum()
	return p_stationary

#g = argmax of stationary trans
def findArgMaxOfMatrix(matrix):
	idx = np.argmax(matrix)
	return idx

def applyCosineThreshold(matrix, cosine_threshold, size_of_matrix):
	for x in range(0, size_of_matrix):
		for y in range(0, size_of_matrix):
			if matrix[x][y] > cosine_threshold:
				matrix[x][y] = 1
			else:
				matrix[x][y] = 0
	return matrix

def reflectOverYX(matrix, size_of_matrix):
    result = np.zeros((size_of_matrix, size_of_matrix))
    for x in range(0, size_of_matrix):
        for y in range(0,x+1):
            result[x][y] = result[y][x] = matrix[x][y]
    return result

def normalize_by_row(matrix):
    row_sums = matrix.sum(axis=1)
    return (matrix/row_sums[: np.newaxis])

