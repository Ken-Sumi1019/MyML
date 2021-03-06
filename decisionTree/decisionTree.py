import numpy as np
import sys

class DecisionTree(object):
    def __init__(self,maxdepth,minsize):
        self.maxdepth = maxdepth
        self.minsize = max(2,minsize)

    """学習する"""
    def train(self,data,label):
        self.data = np.array(data)
        self.label = np.array(label)
        self.categorys = np.unique(self.label)
        self.tree = {}
        self.makeTree()


    """木を構築する"""
    def makeTree(self):
        allIdx = list(range(len(self.data)))
        self.tree = self.addNode(1,allIdx,self.lossScore(allIdx))

    """頂点を追加する"""
    def addNode(self,depth,indexes,gini):
        node = self.bestThreshold(indexes)

        tree = {"gini" : gini,"feature":node["feature"],"val":node["val"]}
        #sumScore = node["rGini"] + node["lGini"]
        if len(node["right"]) == 0 or len(node["left"]) == 0:
            tree["right"] = self.leafNode(node["right"] + node["left"],gini)
            tree["left"] = self.leafNode(node["right"] + node["left"],gini)
            return tree
        if self.maxdepth <= depth:
            tree["right"] = self.leafNode(node["right"],node["rGini"])
            tree["left"] = self.leafNode(node["left"],node["lGini"])
            return tree
        if len(node["right"]) < self.minsize:
            tree["right"] = self.leafNode(node["right"],node["rGini"])
        else:
            tree["right"] = self.addNode(depth + 1,node["right"],node["rGini"])
        if len(node["left"]) < self.minsize:
            tree["left"] = self.leafNode(node["left"],node["lGini"])
        else:
            tree["left"] = self.addNode(depth + 1,node["left"],node["lGini"])
        return tree

    """葉ノードを作成"""
    def leafNode(self,indexes,gini):
        result = {"gini" : gini}
        result["predictVal"] = self.decisionVal(indexes)
        return result

    """予測値を決定"""
    def decisionVal(self,indexes):
        return 0

    """分類する基準の値を求める"""
    def lossScore(self,index):
        return 0

    """最良の閾値を見つける"""
    def bestThreshold(self,indexs):
        bestScore = 100
        bestRight = [];bestLeft = []
        rscore = 0;lscore = 0
        bestIdx = 0;bestFeature = 0
        for i in range(np.shape(self.data)[1]):
            for j in indexs:
                l,r = self.splitGroup(j,i,indexs)
                lgini = self.lossScore(l) if len(l) != 0 else 10
                rgini = self.lossScore(r) if len(r) != 0 else 10
                p = len(l) + len(r)
                if bestScore > len(l) * lgini / p + len(r) * rgini / p:
                    bestIdx = j;bestFeature = i
                    bestRight = r;bestLeft = l
                    bestScore = len(l) * lgini / p + len(r) * rgini / p
                    rscore = rgini;lscore = lgini

        result = {"val" : self.data[bestIdx][bestFeature],"feature" : bestFeature,
                "right" : bestRight,"left" : bestLeft,
                "rGini" : rscore,"lGini" : lscore}
        return result

    """指定した閾値に合わせてグループを分ける"""
    def splitGroup(self,index,feature,indexs):
        right = [];left = []
        for i in indexs:
            if self.data[i][feature] < self.data[index][feature]:
                left.append(i)
            else:
                right.append(i)
        return left,right

    """木を移動して予測値を探し出す"""
    def DFS_predict(self,data,node):
        if "predictVal" in node:
            return node["predictVal"]
        f = node["feature"];v = node["val"]
        if data[f] < v:
            return self.DFS_predict(data,node["left"])
        else:
            return self.DFS_predict(data,node["right"])

    def predict(self,x):
        ans = [0]*len(x)
        for i in range(len(x)):
            ans[i] = self.DFS_predict(x[i],self.tree)
        return np.array(ans)

class ClassificationTree(DecisionTree):
    """ジニ不純度を計算する"""
    def lossScore(self,index):
        n = len(index)
        return 1.0 - sum(np.array([np.count_nonzero(self.label[index] == c) / n for c in self.categorys])**2)

    """予測値を決定"""
    def decisionVal(self,indexes):
        val,count = np.unique(self.label[indexes],return_counts=True)
        return val[np.argmax(count)]


class RegressionTree(DecisionTree):
    """平均二乗誤差を計算"""
    def lossScore(self,index):
        return sum((self.label[index] - np.mean(self.label[index])) ** 2) / len(index)


    def decisionVal(self,indexes):
        return np.mean(self.label[indexes])