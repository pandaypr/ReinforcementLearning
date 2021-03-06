import numpy as np

import matplotlib.pyplot as plt

class GridWorld(object):
    def __init__(self, m, n, magicSquares):
        self.grid = np.zeros((m,n))
        self.m = m
        self.n = n
        self.stateSpace = [i for i in range(self.m*self.n)]
        self.stateSpace.remove(self.m*self.n-1)       #state space do not include the terminal State,
                                        #it is included only in the complete state space or StateSpace+
        self.stateSpacePlus = [i for i in range(self.m*self.n)]
        self.actionSpace = {'U': -self.m, 'D': self.m,
                            'L': -1,     'R': 1}
        self.possibleActions = ['U', 'D', 'L', 'R']
        self.magicSquares = magicSquares
        self.P = {}
        self.initP()

    def initP(self):
        for state in self.stateSpace:
            for action in self.possibleActions:
                reward = -1
                state_ = state + self.actionSpace[action]
                if state_ in self.magicSquares.keys():
                    state_ = self.magicSquares[state_]
                if self.offGridMove(state_, state):
                    state_ = state
                if self.isTerminalState(state_):
                    reward = 0
                self.P[(state_, reward, state, action)] = 1

    def isTerminalState(self, state):
        return state in self.stateSpacePlus and state not in self.stateSpace

    def offGridMove(self, newState, oldState):
        if newState not in self.stateSpacePlus:
            return True
        elif oldState % self.m == 0 and newState % self.m == self.m - 1:
            return True
        elif oldState % self.m == self.m-1 and newState % self.m == 0:
            return True
        else:
            return False

def printV(V, grid):
    for idx, row in enumerate(grid.grid):
        for idy, _ in enumerate(row):
            state = grid.m * idx + idy
            print('%.2f' % V[state], end='\t')
        print('\n')
    print('--------------------')

def printPolicy(policy, grid):
    for idx, row in enumerate(grid.grid):
        for idy, _ in enumerate(row):
            state = grid.m * idx + idy
            if not grid.isTerminalState(state):
                if state not in grid.magicSquares.keys():
                    print('%s' % policy[state], end='\t')
                else:
                    print('%s' % '--', end='\t')
            else:
                print('%s' % '--', end='\t')
        print('\n')
    print('--------------------')

def evaluatePolicy(grid, V, policy, GAMMA,THETA):
    converged = False
    i = 0
    while not converged:
        DELTA = 0
        for state in grid.stateSpace:
            i += 1
            oldV = V[state]
            total = 0
            weight = 1/ len(policy[state])
            for action in policy[state]:
                for key in grid.P:
                    (newState, reward, oldState, act) = key
                    if oldState == state and act == action:
                        total += weight*grid.P[key]* (reward + GAMMA * V[newState])
            V[state] = total
            DELTA = max(DELTA, np.abs(oldV - V[state]))
            converged = True if DELTA < THETA else False
    print(i, 'sweeps of state space for evaluationPolicy')
    return V

def improvePolicy(grid, V, policy, GAMMA):    #We try to find the best policy for a given state, t
                                                # aking the action with max value
    stable = True
    newPolicy = {}
    i=0
    for state in grid.stateSpace:
        i +=1
        oldActions = policy[state]
        value=[]
        newAction=[]
        for action in policy[state]:
            weight = 1/len(policy[state])
            for key in grid.P:
                (newState, reward, oldState, act) = key
                if oldState == state and act == action:
                    value.append(np.round(weight * grid.P[key] *(reward + GAMMA * V[newState]),2))
                    newAction.append(action)
        value = np.array(value)
        best = np.where(value == value.max())[0]
        bestActions = [newAction[item] for item in best]
        newPolicy[state] = bestActions

        if oldActions != bestActions:
            stable = False
    print(i, 'sweeps of state space in Policy Improvement')
    return stable, newPolicy

if __name__ == '__main__':
    magicSquares = {18: 54, 63: 14}
    env = GridWorld(9,9,magicSquares)
    #Hyperparameters
    GAMMA = 1.0
    THETA = 1e-6
    V = {}
    for state in env.stateSpacePlus:
        V[state] = 0
    policy = {}
    for state in env.stateSpace:
        policy[state] = env.possibleActions

    stable = False
    while not stable:
        V = evaluatePolicy(env, V, policy, GAMMA,THETA)
        stable, policy = improvePolicy(env, V,policy, GAMMA)

    printV(V, env)
    print('\n----------------------------------------------\n')
    printPolicy(policy, env)
