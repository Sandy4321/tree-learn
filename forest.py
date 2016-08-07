'''
Created on 07.08.2016

@author: Tobias
'''
import numpy as np
from tree import decision_tree_c45, foggy_decision_tree
from sklearn.datasets.base import load_digits
from sklearn.cross_validation import train_test_split
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.metrics.classification import accuracy_score
import time

class random_forest:
    '''
    standard random forest
    '''
    def __init__(self, n_estimators=10, max_depth=4, bootstrap=True, sample_ratio=1.0, seed=2016):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.bootstrap = bootstrap
        self.sample_ratio = sample_ratio
        self.seed = seed
    
    def fit(self,X,y):
        self._trees = []
        np.random.seed(self.seed)
        for _ in range(self.n_estimators):
            ind = np.random.choice(X.shape[0], int(X.shape[0]*self.sample_ratio), replace=self.bootstrap)
            X_temp = X[ind,:]
            y_temp = y[ind]
            tree = decision_tree_c45(max_depth=self.max_depth).fit(X_temp,y_temp)
            self._trees.append(tree)
        return self    
        
    def predict(self,X):
        predictions = []
        for tree in self._trees:
            y_pred = tree.predict(X)
            predictions.append(y_pred)
        y_out = self.voting(predictions)
        return y_out
    
    def voting(self, predictions):
        def most_freq(x):
            values, counts = np.unique(x,return_counts=True)
            ind=np.argmax(counts)
            return values[ind]
        y_out = [most_freq(x) for x in np.array(predictions).T]
        return np.array(y_out)

class foggy_forest:
    '''
    forest of randomized foggy trees
    '''
    def __init__(self,n_estimators=10, max_depth=4, bootstrap=True, sample_ratio=1.0, var=0.5, seed=2016):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.bootstrap = bootstrap
        self.sample_ratio = sample_ratio
        self.seed = seed
        self.var = var
    
    def fit(self,X,y):
        self._trees = []
        np.random.seed(self.seed)
        for _ in range(self.n_estimators):
            ind = np.random.choice(X.shape[0], int(X.shape[0]*self.sample_ratio), replace=self.bootstrap)
            X_temp = X[ind,:]
            y_temp = y[ind]
            tree = foggy_decision_tree(max_depth=self.max_depth, var=self.var).fit(X_temp,y_temp)
            self._trees.append(tree)
        return self    
        
    def predict(self,X):
        predictions = []
        for tree in self._trees:
            y_pred = tree.predict(X)
            predictions.append(y_pred)
        y_out = self.voting(predictions)
        return y_out
    
    def voting(self, predictions):
        def most_freq(x):
            values, counts = np.unique(x,return_counts=True)
            return values[np.argmax(counts)]
        
        y_out = [most_freq(x) for x in np.array(predictions).T]
        return np.array(y_out)

if __name__ == "__main__":
    digits = load_digits(n_class=3)
    X = digits.data
    y = digits.target
    
    X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=0.9, random_state=2016)
    
    t0 = time.time()
    #forest = random_forest(max_depth=4, n_estimators=20).fit(X_train,y_train)
    forest = foggy_forest(max_depth=4, n_estimators=20, var=3).fit(X_train,y_train)
    y_pred = forest.predict(X_test)
    print("Time taken: %0.3f" %(time.time() - t0))
    print(y_pred)
    
    print("")
    score = accuracy_score(y_test, y_pred)
    print("Score: %0.3f" %score)
    print("")
    
    # printtree(tree._tree,indent='')
    t0 = time.time()
    sklearn_forest = RandomForestClassifier(criterion="entropy", max_depth=4, n_estimators=20, random_state=2016, max_features=None, min_samples_split=1).fit(X_train, y_train)
    y_pred = sklearn_forest.predict(X_test)
    print("Time taken: %0.3f" %(time.time() - t0))
    print(y_pred)
    score = accuracy_score(y_test, y_pred)
    print("Score: %0.3f" %score)
    print("")