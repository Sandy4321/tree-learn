'''
Created on 06.08.2016

@author: Tobias Sterbak: sterbak-it@outlook.com
'''
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.metrics.classification import accuracy_score
from sklearn.tree.tree import DecisionTreeClassifier
from sklearn.datasets.base import load_digits
import time

from helpers import entropy, divide_set

class decisionnode(object):
    def __init__(self,feature=-1,value=None,results=None,tb=None,fb=None,depth=0):
        self.feature=feature
        self.value=value
        self.results=results
        self.tb=tb
        self.fb=fb
        self.depth=depth

class foggy_decision_tree(object):
    '''
    C4.5 classification tree with normally distributed splits at prediction time
    '''
    def __init__(self, max_depth=4, var=1.0, max_features=None):
        self.max_depth = max_depth
        self._current_depth = 0
        self.var = var
        self.max_features = max_features
    
    def fit(self,X,y):
        if self.max_features == None:
            self.max_features = X.shape[1]
        elif self.max_features == "sqrt":
            self.max_features = int(np.sqrt(X.shape[1]))
        elif self.max_features == "log2":
            self.max_features = int(np.log2(X.shape[1]))

        self._tree = self._build_tree(X,y)
        return self
    
    def predict(self,X):
        y_pred = []
        for i in range(X.shape[0]):
            pred = self._predict_one(X[i], self._tree)
            y_pred.append(pred)
        return np.array(y_pred)
    
    def _predict_one(self, sample, tree):
        if tree.results != None:
            return tree.results
        else:
            v = sample[tree.feature]
            branch = None
            value = np.random.normal(loc=tree.value, scale=self.var)
            if isinstance(v,int) or isinstance(v,float):
                if v >= value: 
                    branch = tree.tb
                else: 
                    branch = tree.fb
            else:
                if v == value: 
                    branch = tree.tb
                else: 
                    branch = tree.fb
            return self._predict_one(sample, branch)
    
    def _build_tree(self,X,y,current_depth=0):
        current_score = entropy(y)
        best_gain = 0.0
        best_criteria = None
        best_sets = None
        best_labels = None
        selected_features = np.random.choice(X.shape[1], self.max_features)
        for feature in selected_features:
            for value in np.unique(X[:,feature])[1:len(np.unique(X[:,feature]))-1]:
                lower_set,lower_set_target, higher_set, higher_set_target = divide_set(X, y, feature, value)
                p = float(lower_set.shape[0])/X.shape[0]
                gain = current_score - p*entropy(lower_set_target) - (1-p)*entropy(higher_set_target)
                if gain > best_gain and lower_set.shape[0] > 0 and higher_set.shape[0] > 0:
                    best_gain = gain
                    best_criteria = (feature,value)
                    best_sets = (lower_set,higher_set)
                    best_labels = (lower_set_target,higher_set_target)
        if best_gain > 0 and current_depth < self.max_depth:
            trueBranch = self._build_tree(best_sets[0], best_labels[0], current_depth=current_depth+1)
            falseBranch = self._build_tree(best_sets[1], best_labels[1], current_depth=current_depth+1)
            return decisionnode(feature=best_criteria[0], value=best_criteria[1], tb=trueBranch, fb=falseBranch, depth=current_depth)
        else:
            values, counts = np.unique(y,return_counts=True)
            ind=np.argmax(counts)
            return decisionnode(results=values[ind])

class simple_tree(object):
    '''
    simple classification tree
    '''
    def __init__(self, max_depth=4, max_features=None):
        self.max_depth = max_depth
        self.max_features = max_features
        
    def fit(self,X,y):
        if self.max_features == None:
            self.max_features = X.shape[1]
        elif self.max_features == "sqrt":
            self.max_features = int(np.sqrt(X.shape[1]))
        elif self.max_features == "log2":
            self.max_features = int(np.log2(X.shape[1]))

        self._tree = self._build_tree(X,y)
        return self
    
    def predict(self,X):
        y_pred = []
        for i in range(X.shape[0]):
            pred = self._predict_one(X[i], self._tree)
            y_pred.append(pred)
        return np.array(y_pred)
    
    def _predict_one(self, sample, tree):
        if tree.results != None:
            return tree.results
        else:
            v = sample[tree.feature]
            branch = None
            if isinstance(v,int) or isinstance(v,float):
                if v >= tree.value: 
                    branch = tree.tb
                else: 
                    branch = tree.fb
            return self._predict_one(sample, branch)
    
    def _build_tree(self,X,y,current_depth=0):
        current_score = entropy(y)
        best_gain = 0.0
        best_criteria = None
        best_sets = None
        best_labels = None
        selected_features = np.random.choice(X.shape[1], self.max_features)
        for feature in selected_features:
            value = (np.max(X[:,feature]) - np.min(X[:,feature]))/2
            lower_set,lower_set_target, higher_set, higher_set_target = divide_set(X, y, feature, value)
            p = float(lower_set.shape[0])/X.shape[0]
            gain = current_score - p*entropy(lower_set_target) - (1-p)*entropy(higher_set_target)
            if gain > best_gain and lower_set.shape[0] > 0 and higher_set.shape[0] > 0:
                best_gain = gain
                best_criteria = (feature,value)
                best_sets = (lower_set,higher_set)
                best_labels = (lower_set_target,higher_set_target)
        if best_gain > 0 and current_depth < self.max_depth:
            trueBranch = self._build_tree(best_sets[0], best_labels[0], current_depth=current_depth+1)
            falseBranch = self._build_tree(best_sets[1], best_labels[1], current_depth=current_depth+1)
            return decisionnode(feature=best_criteria[0], value=best_criteria[1], tb=trueBranch, fb=falseBranch, depth=current_depth)
        else:
            values, counts = np.unique(y,return_counts=True)
            ind=np.argmax(counts)
            return decisionnode(results=values[ind])

class decision_tree_c45(object):
    '''
    C4.5 classification tree
    '''
    def __init__(self, max_depth=4, max_features=None):
        self.max_depth = max_depth
        self.max_features = max_features
        
    def fit(self,X,y):
        if self.max_features == None:
            self.max_features = X.shape[1]
        elif self.max_features == "sqrt":
            self.max_features = int(np.sqrt(X.shape[1]))
        elif self.max_features == "log2":
            self.max_features = int(np.log2(X.shape[1]))
        
        self._possible_labels = list(set(y))
        self._tree = self._build_tree(X,y)
        return self
    
    def predict(self,X):
        y_pred = []
        for i in range(X.shape[0]):
            pred = self._predict_one(X[i], self._tree)
            y_pred.append(pred)
        return np.array(y_pred)
    
    def _predict_one(self, sample, tree):
        if tree.results != None:
            return tree.results
        else:
            v = sample[tree.feature]
            branch = None
            if isinstance(v,int) or isinstance(v,float):
                if v >= tree.value: 
                    branch = tree.tb
                else: 
                    branch = tree.fb
            return self._predict_one(sample, branch)
    
    def _build_tree(self,X,y,current_depth=0):
        current_score = entropy(y)
        best_gain = 0.0
        best_criteria = None
        best_sets = None
        best_labels = None
        selected_features = np.random.choice(X.shape[1], self.max_features)
        for feature in selected_features:
            for value in np.unique(X[:,feature])[1:len(np.unique(X[:,feature]))-1]:
                lower_set,lower_set_target, higher_set, higher_set_target = divide_set(X, y, feature, value)
                p = float(lower_set.shape[0])/X.shape[0]
                gain = current_score - p*entropy(lower_set_target) - (1-p)*entropy(higher_set_target)
                if gain > best_gain and lower_set.shape[0] > 0 and higher_set.shape[0] > 0:
                    best_gain = gain
                    best_criteria = (feature,value)
                    best_sets = (lower_set,higher_set)
                    best_labels = (lower_set_target,higher_set_target)
        if best_gain > 0 and current_depth < self.max_depth:
            trueBranch = self._build_tree(best_sets[0], best_labels[0], current_depth=current_depth+1)
            falseBranch = self._build_tree(best_sets[1], best_labels[1], current_depth=current_depth+1)
            return decisionnode(feature=best_criteria[0], value=best_criteria[1], tb=trueBranch, fb=falseBranch, depth=current_depth)
        else:
            values, counts = np.unique(y,return_counts=True)
            ind=np.argmax(counts)
            return decisionnode(results=values[ind])
    
def printtree(tree, indent='   '):
    if tree.results!=None:
        print(str(tree.results))
    else:
        print(str(tree.depth) +" "+ str(tree.feature)+'>='+str(tree.value)+'? ')
        # Print the branches
        print(indent+'T->', end=" ")
        printtree(tree.tb,indent+'  ')
        print(indent+'F->', end=" ")
        printtree(tree.fb,indent+'  ')

if __name__ == "__main__":
    digits = load_digits(n_class=10)
    X = digits.data
    y = digits.target
    
    X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=0.66, random_state=2016)
    
    t0 = time.time()
    tree = decision_tree_c45(max_depth=10, max_features=2).fit(X_train,y_train)
    #tree = simple_tree(max_depth=10, max_features=20).fit(X_train,y_train)
    #tree = foggy_decision_tree(max_depth=10, var=2, max_features=2).fit(X_train,y_train)
    y_pred = tree.predict(X_test)
    #print(y_pred)
    print("Time taken: %0.3f" %(time.time() - t0))
    
    print("")
    score = accuracy_score(y_test, y_pred)
    print("Score: %0.3f" %score)
    print("")
    
    # printtree(tree._tree,indent='')
    
    t0 = time.time()
    sklearn_tree = DecisionTreeClassifier(max_depth=10, random_state=2016, max_features=2).fit(X_train, y_train)
    y_pred = sklearn_tree.predict(X_test)
    print("Time taken: %0.3f" %(time.time() - t0))
    
    score = accuracy_score(y_test, y_pred)
    print("Score: %0.3f" %score)
    print("")
    